# Processing queue (ride event pipeline)
# Reported Lyft loop: design a system to process ride lifecycle events.
#
# Example events: ride_requested, driver_assigned, ride_completed
#
# Interview flow:
#   1. Clarify schema (event_id for idempotency, ride_id as partition key).
#   2. Queue + consumer workers (Kafka topic / SQS); at-least-once delivery.
#   3. Retry with backoff; DLQ after max attempts (poison messages).
#   4. Per-ride ordering via partition key; cross-ride eventual consistency.
#   5. Prod stack: Kafka consumer groups, SQS visibility timeout, Redis dedup set.
#
# In-memory reference: O(1) enqueue, O(log n) per consume step for retry scheduling.

from __future__ import annotations

import heapq
import threading
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class EventType(str, Enum):
    """Ride lifecycle events published to the processing queue."""

    RIDE_REQUESTED = "ride_requested"
    DRIVER_ASSIGNED = "driver_assigned"
    RIDE_COMPLETED = "ride_completed"
    RIDE_CANCELLED = "ride_cancelled"


_TERMINAL_STATES = frozenset({EventType.RIDE_COMPLETED, EventType.RIDE_CANCELLED})


class ProcessingError(Exception):
    """Base error raised when an event handler fails."""

    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


@dataclass(frozen=True)
class Event:
    """Immutable unit of work enqueued for async processing."""

    event_id: str
    event_type: EventType
    timestamp_ms: int
    ride_id: str
    rider_id: Optional[str] = None
    driver_id: Optional[str] = None


@dataclass
class RideRecord:
    """Materialized ride state updated by consumers (eventual consistency target)."""

    ride_id: str
    status: EventType
    updated_at_ms: int
    rider_id: Optional[str] = None
    driver_id: Optional[str] = None


@dataclass(order=True)
class _ScheduledItem:
    """Queue entry ordered by scheduled time, then sequence for FIFO tie-break."""

    scheduled_at_ms: int
    sequence: int
    item: _QueueItem = field(compare=False)


@dataclass
class _QueueItem:
    """Internal envelope tracking retry metadata."""

    event: Event
    attempt: int = 0


@dataclass(frozen=True)
class DeadLetter:
    """An event moved to the DLQ after exhausting retries or on permanent failure."""

    event: Event
    attempt: int
    reason: str


@dataclass(frozen=True)
class ConsumeStats:
    """Result of one consumer poll cycle."""

    processed: int
    retried: int
    dead_lettered: int
    skipped_duplicate: int


class ProcessingQueue:
    """
    Thread-safe in-memory ride event queue with retry, DLQ, and idempotency.

    Talk track: partition Kafka topic by ride_id so lifecycle events stay ordered;
    consumer group members each own partitions; Redis SETNX on event_id dedups
    at-least-once retries; failed messages land in SQS DLQ after N attempts.
    """

    def __init__(
        self,
        *,
        max_retries: int = 3,
        base_retry_delay_ms: int = 1_000,
        max_retry_delay_ms: int = 30_000,
    ) -> None:
        self._max_retries = max_retries
        self._base_retry_delay_ms = base_retry_delay_ms
        self._max_retry_delay_ms = max_retry_delay_ms

        self._lock = threading.Lock()
        self._sequence = 0

        # Min-heap of the next eligible event per ride partition.
        self._ready_heap: list[_ScheduledItem] = []

        # Per-ride FIFO buffers preserve ordering within a partition key (ride_id).
        self._per_ride_buffers: dict[str, deque[_QueueItem]] = {}

        # Idempotency store — processed event_id (at-least-once safe handlers).
        self._processed_event_ids: set[str] = set()

        # Materialized ride state (would be Postgres / DynamoDB in production).
        self._rides: dict[str, RideRecord] = {}

        self._dlq: list[DeadLetter] = []

        self._handlers: dict[EventType, Callable[[Event], None]] = {
            EventType.RIDE_REQUESTED: self._handle_ride_requested,
            EventType.DRIVER_ASSIGNED: self._handle_driver_assigned,
            EventType.RIDE_COMPLETED: self._handle_ride_completed,
            EventType.RIDE_CANCELLED: self._handle_ride_cancelled,
        }

    def publish(self, event: Event) -> None:
        """
        Enqueue one event (producer / API path).

        In production this is a Kafka produce or SQS SendMessage; partition key
        is ride_id so all events for one ride land on the same ordered partition.
        """
        with self._lock:
            self._enqueue_unlocked(event, attempt=0, scheduled_at_ms=event.timestamp_ms)

    def publish_batch(self, events: list[Event]) -> None:
        """Enqueue a micro-batch with a single lock acquisition."""
        with self._lock:
            for event in events:
                self._enqueue_unlocked(
                    event, attempt=0, scheduled_at_ms=event.timestamp_ms
                )

    def consume(self, *, now_ms: int, limit: int = 10) -> ConsumeStats:
        """
        Poll and process up to `limit` ready events (consumer worker loop).

        Returns counts for processed, retried, DLQ, and idempotent skips.
        """
        processed = retried = dead_lettered = skipped_duplicate = 0

        with self._lock:
            for _ in range(limit):
                item = self._dequeue_ready_unlocked(now_ms)
                if item is None:
                    break

                event = item.event
                if event.event_id in self._processed_event_ids:
                    self._advance_partition_unlocked(event.ride_id, now_ms)
                    skipped_duplicate += 1
                    continue

                try:
                    self._handlers[event.event_type](event)
                except ProcessingError as exc:
                    if exc.retryable and item.attempt + 1 < self._max_retries:
                        item.attempt += 1
                        delay = self._backoff_ms(item.attempt - 1)
                        self._schedule_head_unlocked(
                            event.ride_id, now_ms + delay
                        )
                        retried += 1
                    else:
                        self._advance_partition_unlocked(event.ride_id, now_ms)
                        self._dlq.append(
                            DeadLetter(
                                event=event,
                                attempt=item.attempt + 1,
                                reason=str(exc),
                            )
                        )
                        dead_lettered += 1
                    continue
                except Exception as exc:  # noqa: BLE001 — surface unknown failures to DLQ
                    self._advance_partition_unlocked(event.ride_id, now_ms)
                    self._dlq.append(
                        DeadLetter(
                            event=event,
                            attempt=item.attempt + 1,
                            reason=f"unexpected: {exc}",
                        )
                    )
                    dead_lettered += 1
                    continue

                self._processed_event_ids.add(event.event_id)
                self._advance_partition_unlocked(event.ride_id, now_ms)
                processed += 1

        return ConsumeStats(
            processed=processed,
            retried=retried,
            dead_lettered=dead_lettered,
            skipped_duplicate=skipped_duplicate,
        )

    def get_ride(self, ride_id: str) -> Optional[RideRecord]:
        """Read materialized ride state (downstream read path)."""
        with self._lock:
            ride = self._rides.get(ride_id)
            if ride is None:
                return None
            return RideRecord(
                ride_id=ride.ride_id,
                status=ride.status,
                updated_at_ms=ride.updated_at_ms,
                rider_id=ride.rider_id,
                driver_id=ride.driver_id,
            )

    def get_dead_letters(self) -> list[DeadLetter]:
        """Inspect poison messages (ops / replay tooling)."""
        with self._lock:
            return list(self._dlq)

    def pending_count(self) -> int:
        """Approximate queue depth for backpressure monitoring."""
        with self._lock:
            buffered = sum(len(q) for q in self._per_ride_buffers.values())
            return buffered + len(self._ready_heap)

    def _enqueue_unlocked(
        self,
        event: Event,
        *,
        attempt: int,
        scheduled_at_ms: int,
    ) -> None:
        """Append to the ride partition; schedule the head only when buffer was empty."""
        buffer = self._per_ride_buffers.setdefault(event.ride_id, deque())
        buffer.append(_QueueItem(event=event, attempt=attempt))
        if len(buffer) == 1:
            self._schedule_head_unlocked(event.ride_id, scheduled_at_ms)

    def _schedule_head_unlocked(self, ride_id: str, scheduled_at_ms: int) -> None:
        """Put the partition head on the ready heap (Kafka: next offset in partition)."""
        buffer = self._per_ride_buffers.get(ride_id)
        if not buffer:
            return

        head = buffer[0]
        ready_at = max(scheduled_at_ms, head.event.timestamp_ms)
        self._sequence += 1
        heapq.heappush(
            self._ready_heap,
            _ScheduledItem(ready_at, self._sequence, head),
        )

    def _dequeue_ready_unlocked(self, now_ms: int) -> Optional[_QueueItem]:
        """Return the earliest eligible partition head without advancing the buffer."""
        while self._ready_heap:
            scheduled = heapq.heappop(self._ready_heap)
            if scheduled.scheduled_at_ms > now_ms:
                heapq.heappush(self._ready_heap, scheduled)
                return None

            ride_id = scheduled.item.event.ride_id
            buffer = self._per_ride_buffers.get(ride_id)
            if not buffer or buffer[0] is not scheduled.item:
                continue

            return buffer[0]

        return None

    def _advance_partition_unlocked(self, ride_id: str, now_ms: int) -> None:
        """Commit the partition head and schedule the next in-order event."""
        buffer = self._per_ride_buffers.get(ride_id)
        if not buffer:
            return

        buffer.popleft()
        if buffer:
            self._schedule_head_unlocked(ride_id, now_ms)
        else:
            self._per_ride_buffers.pop(ride_id, None)

    def _backoff_ms(self, attempt: int) -> int:
        """Exponential backoff capped for retry scheduling."""
        delay = self._base_retry_delay_ms * (2**attempt)
        return min(delay, self._max_retry_delay_ms)

    def _handle_ride_requested(self, event: Event) -> None:
        """Create a ride in requested state; ignore duplicate requests for active rides."""
        ride = self._rides.get(event.ride_id)
        if ride is not None and ride.status not in _TERMINAL_STATES:
            return

        self._rides[event.ride_id] = RideRecord(
            ride_id=event.ride_id,
            status=EventType.RIDE_REQUESTED,
            updated_at_ms=event.timestamp_ms,
            rider_id=event.rider_id,
        )

    def _handle_driver_assigned(self, event: Event) -> None:
        """Transition requested -> assigned; stale/out-of-order events are no-ops."""
        ride = self._rides.get(event.ride_id)
        if ride is None or ride.status in _TERMINAL_STATES:
            return
        if ride.status is not EventType.RIDE_REQUESTED:
            return

        ride.status = EventType.DRIVER_ASSIGNED
        ride.driver_id = event.driver_id
        ride.updated_at_ms = event.timestamp_ms

    def _handle_ride_completed(self, event: Event) -> None:
        """Mark ride completed; idempotent if already terminal."""
        ride = self._rides.get(event.ride_id)
        if ride is None:
            self._rides[event.ride_id] = RideRecord(
                ride_id=event.ride_id,
                status=EventType.RIDE_COMPLETED,
                updated_at_ms=event.timestamp_ms,
            )
            return
        if ride.status in _TERMINAL_STATES:
            return

        ride.status = EventType.RIDE_COMPLETED
        ride.updated_at_ms = event.timestamp_ms

    def _handle_ride_cancelled(self, event: Event) -> None:
        """Mark ride cancelled; safe to apply after terminal states (no-op)."""
        ride = self._rides.get(event.ride_id)
        if ride is None:
            self._rides[event.ride_id] = RideRecord(
                ride_id=event.ride_id,
                status=EventType.RIDE_CANCELLED,
                updated_at_ms=event.timestamp_ms,
            )
            return
        if ride.status in _TERMINAL_STATES:
            return

        ride.status = EventType.RIDE_CANCELLED
        ride.updated_at_ms = event.timestamp_ms


if __name__ == "__main__":
    queue = ProcessingQueue(max_retries=3, base_retry_delay_ms=500)
    base_ts = 1_700_000_000_000

    queue.publish_batch(
        [
            Event("e1", EventType.RIDE_REQUESTED, base_ts, "ride-1", rider_id="r1"),
            Event("e2", EventType.DRIVER_ASSIGNED, base_ts + 1_000, "ride-1", driver_id="d1"),
            Event("e3", EventType.RIDE_REQUESTED, base_ts + 500, "ride-2", rider_id="r2"),
        ]
    )

    stats = queue.consume(now_ms=base_ts + 2_000, limit=10)
    assert stats.processed == 3
    assert stats.skipped_duplicate == 0

    ride1 = queue.get_ride("ride-1")
    assert ride1 is not None
    assert ride1.status is EventType.DRIVER_ASSIGNED
    assert ride1.driver_id == "d1"

    ride2 = queue.get_ride("ride-2")
    assert ride2 is not None
    assert ride2.status is EventType.RIDE_REQUESTED

    queue.publish(
        Event("e4", EventType.RIDE_COMPLETED, base_ts + 120_000, "ride-1")
    )
    stats = queue.consume(now_ms=base_ts + 120_000, limit=10)
    assert stats.processed == 1

    ride1 = queue.get_ride("ride-1")
    assert ride1 is not None
    assert ride1.status is EventType.RIDE_COMPLETED

    # Idempotent retry — duplicate event_id must not re-apply side effects.
    queue.publish(
        Event("e4", EventType.RIDE_COMPLETED, base_ts + 120_000, "ride-1")
    )
    stats = queue.consume(now_ms=base_ts + 120_000, limit=10)
    assert stats.skipped_duplicate == 1
    assert stats.processed == 0

    # Per-ride ordering: completion queued before assignment should no-op assignment.
    queue.publish_batch(
        [
            Event("e5", EventType.RIDE_REQUESTED, base_ts, "ride-3", rider_id="r3"),
            Event("e6", EventType.RIDE_COMPLETED, base_ts + 5_000, "ride-3"),
            Event("e7", EventType.DRIVER_ASSIGNED, base_ts + 2_000, "ride-3", driver_id="d9"),
        ]
    )
    queue.consume(now_ms=base_ts + 10_000, limit=10)
    ride3 = queue.get_ride("ride-3")
    assert ride3 is not None
    assert ride3.status is EventType.RIDE_COMPLETED

    print(
        f"ride-1={queue.get_ride('ride-1')}, "
        f"pending={queue.pending_count()}, dlq={queue.get_dead_letters()}"
    )

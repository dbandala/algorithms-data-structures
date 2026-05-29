# Real-time data processing
# Reported Lyft senior loop: stream of ride lifecycle events -> live analytics.
#
# Interview flow:
#   1. Clarify event schema (event_id for idempotency, type, timestamp, ride_id).
#   2. Single-event ingest vs micro-batches (Kafka consumer poll / Kinesis).
#   3. In-memory aggregations under a lock; prod = Flink/Spark + Redis/ClickHouse.
#   4. Discuss: consumer groups, partition key = ride_id, at-least-once + dedup, DLQ.
#
# In-memory reference: O(1) amortized per event; O(R + S) space for rides R and dedup S.

from __future__ import annotations

import threading
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EventType(str, Enum):
    """Ride lifecycle events emitted to the stream."""

    RIDE_REQUESTED = "ride_requested"
    DRIVER_ASSIGNED = "driver_assigned"
    RIDE_COMPLETED = "ride_completed"
    RIDE_CANCELLED = "ride_cancelled"


_TERMINAL_STATES = frozenset({EventType.RIDE_COMPLETED, EventType.RIDE_CANCELLED})
_ACTIVE_STATES = frozenset({EventType.RIDE_REQUESTED, EventType.DRIVER_ASSIGNED})


@dataclass(frozen=True)
class Event:
    """Single immutable record from the event stream."""

    event_id: str
    event_type: EventType
    timestamp_ms: int
    ride_id: str
    rider_id: Optional[str] = None
    driver_id: Optional[str] = None


@dataclass(frozen=True)
class AnalyticsSnapshot:
    """Point-in-time view of stream analytics (what dashboards would read)."""

    event_counts: dict[str, int]
    active_rides: int
    completed_in_window: int
    avg_completion_time_ms: Optional[float]
    window_seconds: int


@dataclass
class _RideState:
    """Per-ride tracking for lifecycle and latency metrics."""

    status: EventType
    requested_at_ms: Optional[int] = None


class RealTimeProcessing:
    """
    Thread-safe in-memory stream processor for ride lifecycle events.

    Talk track: Kafka topic partitioned by ride_id preserves per-ride ordering;
    consumer group scales horizontally; Redis SET dedups event_id across retries.
    """

    def __init__(self, window_seconds: int = 60) -> None:
        self._window_seconds = window_seconds
        self._lock = threading.Lock()

        # Idempotency: skip duplicate event_id (at-least-once delivery).
        self._seen_event_ids: set[str] = set()

        # Counters exposed to dashboards.
        self._event_counts: defaultdict[str, int] = defaultdict(int)

        # ride_id -> latest non-terminal state for active-ride count.
        self._rides: dict[str, _RideState] = {}

        # (timestamp_ms,) for completed events inside the sliding window.
        self._completed_timestamps: deque[int] = deque()

        # Sum of (completed_at - requested_at) for avg latency in the window.
        self._completion_latency_sum_ms: int = 0
        self._completion_latency_count: int = 0

    def process_event(self, event: Event) -> None:
        """
        Ingest one event and update real-time analytics.

        Duplicate event_id is ignored (idempotent consumer). All mutations run
        under one lock to avoid lost updates from concurrent producers.
        """
        with self._lock:
            self._process_event_unlocked(event)

    def process_event_batch(self, events: list[Event]) -> None:
        """
        Ingest a micro-batch (e.g. Kafka poll) with a single lock acquisition.

        Preserves per-batch order; cross-partition ordering is not guaranteed
        in production — partition by ride_id for lifecycle correctness.
        """
        with self._lock:
            for event in events:
                self._process_event_unlocked(event)

    def get_analytics(self, now_ms: Optional[int] = None) -> AnalyticsSnapshot:
        """
        Return a snapshot of current analytics, trimming the sliding window first.

        In production this would read from Redis/TSDB; here we compute on demand.
        """
        with self._lock:
            if now_ms is not None:
                self._trim_window_unlocked(now_ms)

            avg_ms: Optional[float] = None
            if self._completion_latency_count > 0:
                avg_ms = (
                    self._completion_latency_sum_ms / self._completion_latency_count
                )

            return AnalyticsSnapshot(
                event_counts=dict(self._event_counts),
                active_rides=self._count_active_rides_unlocked(),
                completed_in_window=len(self._completed_timestamps),
                avg_completion_time_ms=avg_ms,
                window_seconds=self._window_seconds,
            )

    def _process_event_unlocked(self, event: Event) -> None:
        """Apply one event; caller must hold self._lock."""
        if event.event_id in self._seen_event_ids:
            return
        self._seen_event_ids.add(event.event_id)

        self._event_counts[event.event_type.value] += 1
        self._trim_window_unlocked(event.timestamp_ms)

        ride = self._rides.get(event.ride_id)

        if event.event_type is EventType.RIDE_REQUESTED:
            if ride is None or ride.status in _TERMINAL_STATES:
                self._rides[event.ride_id] = _RideState(
                    status=EventType.RIDE_REQUESTED,
                    requested_at_ms=event.timestamp_ms,
                )
            return

        if event.event_type is EventType.DRIVER_ASSIGNED:
            if ride is None or ride.status in _TERMINAL_STATES:
                self._rides[event.ride_id] = _RideState(
                    status=EventType.DRIVER_ASSIGNED,
                )
            elif ride.status is EventType.RIDE_REQUESTED:
                ride.status = EventType.DRIVER_ASSIGNED
            return

        if event.event_type is EventType.RIDE_COMPLETED:
            requested_at = ride.requested_at_ms if ride else None
            self._rides.pop(event.ride_id, None)
            self._record_completion_unlocked(event.timestamp_ms, requested_at)
            return

        if event.event_type is EventType.RIDE_CANCELLED:
            self._rides.pop(event.ride_id, None)

    def _record_completion_unlocked(
        self,
        completed_at_ms: int,
        requested_at_ms: Optional[int],
    ) -> None:
        """Track completion in the sliding window and latency aggregates."""
        self._completed_timestamps.append(completed_at_ms)
        if requested_at_ms is not None and completed_at_ms >= requested_at_ms:
            latency = completed_at_ms - requested_at_ms
            self._completion_latency_sum_ms += latency
            self._completion_latency_count += 1

    def _trim_window_unlocked(self, now_ms: int) -> None:
        """Drop completions that fell outside the sliding window."""
        cutoff = now_ms - self._window_seconds * 1000
        while self._completed_timestamps and self._completed_timestamps[0] < cutoff:
            self._completed_timestamps.popleft()
        # Latency avg is approximate in this reference impl; prod would use
        # a time-bucketed structure (Redis ZSET / Flink window operator).

    def _count_active_rides_unlocked(self) -> int:
        """Count rides in requested or assigned state."""
        return sum(1 for ride in self._rides.values() if ride.status in _ACTIVE_STATES)


if __name__ == "__main__":
    processor = RealTimeProcessing(window_seconds=60)

    base_ts = 1_700_000_000_000

    processor.process_event_batch(
        [
            Event("e1", EventType.RIDE_REQUESTED, base_ts, "ride-1", rider_id="r1"),
            Event("e2", EventType.DRIVER_ASSIGNED, base_ts + 1_000, "ride-1", driver_id="d1"),
            Event("e3", EventType.RIDE_REQUESTED, base_ts + 500, "ride-2", rider_id="r2"),
        ]
    )

    snap = processor.get_analytics(now_ms=base_ts + 2_000)
    assert snap.active_rides == 2
    assert snap.event_counts["ride_requested"] == 2
    assert snap.event_counts["driver_assigned"] == 1

    processor.process_event(
        Event("e4", EventType.RIDE_COMPLETED, base_ts + 120_000, "ride-1")
    )

    snap = processor.get_analytics(now_ms=base_ts + 120_000)
    assert snap.active_rides == 1
    assert snap.completed_in_window == 1
    assert snap.avg_completion_time_ms == 120_000.0

    # Idempotent retry — duplicate event_id must not double-count.
    processor.process_event(
        Event("e4", EventType.RIDE_COMPLETED, base_ts + 120_000, "ride-1")
    )
    snap = processor.get_analytics(now_ms=base_ts + 120_000)
    assert snap.event_counts["ride_completed"] == 1

    print(
        f"active={snap.active_rides}, completed_in_window={snap.completed_in_window}, "
        f"avg_completion_ms={snap.avg_completion_time_ms}, counts={snap.event_counts}"
    )

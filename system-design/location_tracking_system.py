# 3. Design Real-Time Location Tracking
#
# "Track millions of moving devices."
#
# Requirements:
# * Drivers update location every few seconds
# * Users see moving cars on maps (live, low-latency)
# * High write throughput; fast reads for map viewport
#
# Interview talk track (senior loop):
#   1. Clarify: who publishes (drivers only vs riders too), staleness SLA, history vs latest-only.
#   2. Write path: ingest API -> validate -> Kafka (partition by device_id) -> geo-index workers + hot store.
#   3. Read path: latest position from Redis; viewport query from geohash/grid index; push via WebSockets.
#   4. Scale: shard geo index by geohash prefix; coalesce updates per cell; TTL stale devices off the map.
#   5. Failure: at-least-once ingest with idempotent upsert; clients interpolate between points.
#
# Architecture (mermaid):
#
# ```mermaid
# flowchart TB
#     subgraph Clients
#         DA[Driver App]
#         RA[Rider App / Map]
#     end
#
#     subgraph Ingest["Hot write path"]
#         LI[Location Ingest API]
#         KQ[(Kafka: device.locations)]
#     end
#
#     subgraph Core["In-memory core (this file)"]
#         LTS[LocationTrackingService]
#         LS[LatestLocationStore]
#         GI[GeohashSpatialIndex]
#         WS[WebSocketGateway]
#         EB{EventBus}
#     end
#
#     subgraph ProdScale["Production scale-out"]
#         REDIS[(Redis GEO + HASH latest)]
#         CASS[(Cassandra / TSDB trail)]
#         WSS[WebSocket cluster by region]
#     end
#
#     DA -->|GPS ~3s| LI
#     LI --> KQ
#     KQ --> LTS
#     LI --> LTS
#     LTS --> LS
#     LTS --> GI
#     LTS --> EB
#     LTS --> WS
#
#     RA -->|subscribe viewport| WS
#     WS -->|push deltas| RA
#     RA -->|GET nearby| LTS
#
#     LS -.-> REDIS
#     GI -.-> REDIS
#     EB -.-> CASS
#     WS -.-> WSS
# ```

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Protocol

# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


class DeviceKind(str, Enum):
    """Type of entity publishing GPS (drivers are the hot path at Lyft)."""

    DRIVER = "driver"
    RIDER = "rider"
    COURIER = "courier"


@dataclass(frozen=True)
class Location:
    """WGS84 point in degrees."""

    lat: float
    lng: float


@dataclass(frozen=True)
class Viewport:
    """
    Map bounding box riders are looking at.

    Production: convert to a set of geohash prefixes at appropriate precision.
    """

    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float

    def center(self) -> Location:
        """Return the geographic center of the viewport."""
        return Location(
            lat=(self.min_lat + self.max_lat) / 2,
            lng=(self.min_lng + self.max_lng) / 2,
        )


@dataclass(frozen=True)
class LocationUpdate:
    """Single GPS sample from a device."""

    device_id: str
    location: Location
    timestamp_ms: int
    heading_deg: Optional[float] = None
    speed_mps: Optional[float] = None
    accuracy_m: Optional[float] = None


@dataclass
class TrackedDevice:
    """Metadata for an entity we track on the map."""

    device_id: str
    kind: DeviceKind = DeviceKind.DRIVER
    is_active: bool = True


@dataclass(frozen=True)
class DeviceSnapshot:
    """Latest known state exposed to map clients."""

    device_id: str
    kind: DeviceKind
    location: Location
    timestamp_ms: int
    heading_deg: Optional[float]
    speed_mps: Optional[float]


# ---------------------------------------------------------------------------
# Events (Kafka topic sketch)
# ---------------------------------------------------------------------------


class EventType(str, Enum):
    """Async topics for analytics, ETA models, and audit."""

    LOCATION_UPDATED = "device.location.updated"
    DEVICE_WENT_STALE = "device.location.stale"
    MAP_SUBSCRIBED = "map.viewport.subscribed"


@dataclass(frozen=True)
class Event:
    """Envelope for pub/sub consumers."""

    event_type: EventType
    payload: dict


EventHandler = Callable[[Event], None]


class EventBus:
    """
    In-process pub/sub stand-in for Kafka.

    Production: partition `device.locations` by device_id hash so per-device
    ordering is preserved; consumers update Redis GEO and push gateways.
    """

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventHandler]] = defaultdict(list)
        self.history: list[Event] = []

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Register a handler for one event type."""
        self._handlers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        """Deliver an event to subscribers (synchronous demo)."""
        self.history.append(event)
        for handler in self._handlers[event.event_type]:
            handler(event)


# ---------------------------------------------------------------------------
# Geohash (spatial sharding + viewport queries)
# ---------------------------------------------------------------------------

_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def encode_geohash(location: Location, precision: int = 7) -> str:
    """
    Encode lat/lng into a geohash string.

    Precision 7 ~ 150 m cell (urban map tiles). Higher precision for matching;
    lower for regional aggregation.
    """
    lat_interval = [-90.0, 90.0]
    lng_interval = [-180.0, 180.0]
    geohash: list[str] = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    even = True

    while len(geohash) < precision:
        if even:
            mid = (lng_interval[0] + lng_interval[1]) / 2
            if location.lng > mid:
                ch |= bits[bit]
                lng_interval[0] = mid
            else:
                lng_interval[1] = mid
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if location.lat > mid:
                ch |= bits[bit]
                lat_interval[0] = mid
            else:
                lat_interval[1] = mid
        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash.append(_BASE32[ch])
            bit = 0
            ch = 0
    return "".join(geohash)


def _geohash_bbox(prefix: str) -> tuple[float, float, float, float]:
    """Return (min_lat, min_lng, max_lat, max_lng) for a geohash prefix."""
    lat_interval = [-90.0, 90.0]
    lng_interval = [-180.0, 180.0]
    even = True
    for char in prefix:
        idx = _BASE32.index(char)
        for mask in [16, 8, 4, 2, 1]:
            if even:
                mid = (lng_interval[0] + lng_interval[1]) / 2
                if idx & mask:
                    lng_interval[0] = mid
                else:
                    lng_interval[1] = mid
            else:
                mid = (lat_interval[0] + lat_interval[1]) / 2
                if idx & mask:
                    lat_interval[0] = mid
                else:
                    lat_interval[1] = mid
            even = not even
    return lat_interval[0], lng_interval[0], lat_interval[1], lng_interval[1]


def _bbox_intersects_viewport(
    cell_min_lat: float,
    cell_min_lng: float,
    cell_max_lat: float,
    cell_max_lng: float,
    viewport: Viewport,
) -> bool:
    """True if a geohash cell bbox overlaps the map viewport."""
    return not (
        cell_max_lat < viewport.min_lat
        or cell_min_lat > viewport.max_lat
        or cell_max_lng < viewport.min_lng
        or cell_min_lng > viewport.max_lng
    )


# ---------------------------------------------------------------------------
# Storage + index
# ---------------------------------------------------------------------------


class LatestLocationStore:
    """
    O(1) latest position per device (Redis HASH stand-in).

    Keys: device_id -> LocationUpdate. Stale entries are purged on read or
    by a background sweeper in production.
    """

    def __init__(self, stale_after_ms: int = 30_000) -> None:
        self._stale_after_ms = stale_after_ms
        self._latest: dict[str, LocationUpdate] = {}

    def upsert(self, update: LocationUpdate) -> None:
        """Keep only the newest sample per device (idempotent replay safe)."""
        current = self._latest.get(update.device_id)
        if current is None or update.timestamp_ms >= current.timestamp_ms:
            self._latest[update.device_id] = update

    def get(self, device_id: str, *, now_ms: Optional[int] = None) -> Optional[LocationUpdate]:
        """Return latest update if still fresh, else None."""
        update = self._latest.get(device_id)
        if update is None:
            return None
        if self._is_stale(update, now_ms=now_ms):
            return None
        return update

    def remove(self, device_id: str) -> None:
        """Drop a device from the hot store."""
        self._latest.pop(device_id, None)

    def all_fresh(self, *, now_ms: Optional[int] = None) -> list[LocationUpdate]:
        """Return every non-stale update (used by sweepers / debug)."""
        return [
            u
            for u in self._latest.values()
            if not self._is_stale(u, now_ms=now_ms)
        ]

    def stale_device_ids(self, *, now_ms: Optional[int] = None) -> list[str]:
        """Devices that exceeded the staleness window."""
        return [
            device_id
            for device_id, update in self._latest.items()
            if self._is_stale(update, now_ms=now_ms)
        ]

    def _is_stale(self, update: LocationUpdate, *, now_ms: Optional[int] = None) -> bool:
        """True if the sample is too old to show on the live map."""
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        return now - update.timestamp_ms > self._stale_after_ms


class SpatialIndex(Protocol):
    """Contract for geo indexes (geohash, grid, Redis GEO, H3)."""

    def upsert(self, device_id: str, location: Location) -> None:
        """Insert or move a device."""

    def remove(self, device_id: str) -> None:
        """Remove a device from the index."""

    def query_viewport(
        self, viewport: Viewport, *, active_device_ids: set[str]
    ) -> list[str]:
        """Return device ids whose last indexed point intersects the viewport."""


class GeohashSpatialIndex:
    """
    Geohash-prefix inverted index for viewport reads.

    Shard key in production: geohash prefix -> Redis GEO key. Writes are
    cheap O(1); reads scan O(cells in viewport) instead of all devices.
    """

    def __init__(self, precision: int = 7) -> None:
        self._precision = precision
        self._prefix_to_devices: dict[str, set[str]] = defaultdict(set)
        self._device_to_prefix: dict[str, str] = {}

    def upsert(self, device_id: str, location: Location) -> None:
        """Move device across geohash cells when it crosses a boundary."""
        new_prefix = encode_geohash(location, self._precision)
        old_prefix = self._device_to_prefix.get(device_id)
        if old_prefix == new_prefix:
            return
        if old_prefix is not None:
            self._prefix_to_devices[old_prefix].discard(device_id)
            if not self._prefix_to_devices[old_prefix]:
                del self._prefix_to_devices[old_prefix]
        self._device_to_prefix[device_id] = new_prefix
        self._prefix_to_devices[new_prefix].add(device_id)

    def remove(self, device_id: str) -> None:
        """Drop a device from the spatial index."""
        prefix = self._device_to_prefix.pop(device_id, None)
        if prefix is None:
            return
        self._prefix_to_devices[prefix].discard(device_id)
        if not self._prefix_to_devices[prefix]:
            del self._prefix_to_devices[prefix]

    def query_viewport(
        self, viewport: Viewport, *, active_device_ids: set[str]
    ) -> list[str]:
        """Collect device ids in geohash cells that overlap the viewport."""
        candidates: set[str] = set()
        for prefix, device_ids in self._prefix_to_devices.items():
            min_lat, min_lng, max_lat, max_lng = _geohash_bbox(prefix)
            if not _bbox_intersects_viewport(
                min_lat, min_lng, max_lat, max_lng, viewport
            ):
                continue
            for device_id in device_ids:
                if device_id in active_device_ids:
                    candidates.add(device_id)
        return list(candidates)


# ---------------------------------------------------------------------------
# WebSocket gateway (map subscriptions)
# ---------------------------------------------------------------------------


@dataclass
class MapSubscription:
    """A rider client watching a map region."""

    subscription_id: str
    subscriber_id: str
    viewport: Viewport


class WebSocketGateway:
    """
    Fan-out location deltas to riders subscribed to a viewport.

    Production: gateway nodes own geohash ranges; clients connect to the node
    covering their viewport; ingest publishes to a pub/sub channel per cell.
    """

    def __init__(self) -> None:
        self._subscriptions: dict[str, MapSubscription] = {}
        self.outbox: list[dict] = []

    def subscribe(
        self, subscriber_id: str, viewport: Viewport, *, subscription_id: Optional[str] = None
    ) -> MapSubscription:
        """Register interest in live updates for a map bounding box."""
        sub = MapSubscription(
            subscription_id=subscription_id or str(uuid.uuid4()),
            subscriber_id=subscriber_id,
            viewport=viewport,
        )
        self._subscriptions[sub.subscription_id] = sub
        return sub

    def unsubscribe(self, subscription_id: str) -> None:
        """Remove a map subscription."""
        self._subscriptions.pop(subscription_id, None)

    def push_location_update(
        self, update: LocationUpdate, device_kind: DeviceKind
    ) -> None:
        """Deliver update to every subscription whose viewport contains the point."""
        point = update.location
        payload = {
            "device_id": update.device_id,
            "kind": device_kind.value,
            "lat": point.lat,
            "lng": point.lng,
            "timestamp_ms": update.timestamp_ms,
            "heading_deg": update.heading_deg,
            "speed_mps": update.speed_mps,
        }
        for sub in self._subscriptions.values():
            if _point_in_viewport(point, sub.viewport):
                self.outbox.append(
                    {
                        "subscription_id": sub.subscription_id,
                        "subscriber_id": sub.subscriber_id,
                        "payload": payload,
                    }
                )


def _point_in_viewport(point: Location, viewport: Viewport) -> bool:
    """True if lat/lng lies inside the viewport bbox."""
    return (
        viewport.min_lat <= point.lat <= viewport.max_lat
        and viewport.min_lng <= point.lng <= viewport.max_lng
    )


# ---------------------------------------------------------------------------
# Location tracking service (orchestrator)
# ---------------------------------------------------------------------------


class LocationTrackingService:
    """
    End-to-end location tracking for Lyft-style live maps.

    Write path: ingest -> latest store + geo index -> events + WebSocket push.
    Read path: viewport query with staleness filter; point lookups by device_id.
    """

    def __init__(
        self,
        *,
        stale_after_ms: int = 30_000,
        geohash_precision: int = 7,
        event_bus: Optional[EventBus] = None,
        websocket_gateway: Optional[WebSocketGateway] = None,
    ) -> None:
        self._devices: dict[str, TrackedDevice] = {}
        self._store = LatestLocationStore(stale_after_ms=stale_after_ms)
        self._index: SpatialIndex = GeohashSpatialIndex(precision=geohash_precision)
        self._events = event_bus or EventBus()
        self._ws = websocket_gateway or WebSocketGateway()
        self._stale_after_ms = stale_after_ms

    @property
    def event_bus(self) -> EventBus:
        """Expose the bus for demo handlers and tests."""
        return self._events

    @property
    def websocket_gateway(self) -> WebSocketGateway:
        """Expose the gateway for inspecting pushed map deltas."""
        return self._ws

    def register_device(self, device: TrackedDevice) -> None:
        """Add a device that will publish GPS updates."""
        self._devices[device.device_id] = device

    def deactivate_device(self, device_id: str) -> None:
        """Mark a device offline and remove it from indexes."""
        device = self._devices.get(device_id)
        if device is not None:
            device.is_active = False
        self._store.remove(device_id)
        self._index.remove(device_id)

    def ingest_location(
        self,
        update: LocationUpdate,
        *,
        now_ms: Optional[int] = None,
    ) -> bool:
        """
        Accept a GPS sample (Location Ingest API / Kafka consumer).

        Returns False if the device is unknown, inactive, or the sample is
        older than what we already have (out-of-order replay).
        """
        device = self._devices.get(update.device_id)
        if device is None or not device.is_active:
            return False

        existing = self._store.get(update.device_id, now_ms=now_ms)
        if existing is not None and update.timestamp_ms < existing.timestamp_ms:
            return False

        self._store.upsert(update)
        self._index.upsert(update.device_id, update.location)

        self._events.publish(
            Event(
                EventType.LOCATION_UPDATED,
                {
                    "device_id": update.device_id,
                    "kind": device.kind.value,
                    "lat": update.location.lat,
                    "lng": update.location.lng,
                    "timestamp_ms": update.timestamp_ms,
                },
            )
        )
        self._ws.push_location_update(update, device.kind)
        return True

    def get_device_location(
        self, device_id: str, *, now_ms: Optional[int] = None
    ) -> Optional[DeviceSnapshot]:
        """Return the latest fresh snapshot for one device."""
        device = self._devices.get(device_id)
        update = self._store.get(device_id, now_ms=now_ms)
        if device is None or update is None:
            return None
        return DeviceSnapshot(
            device_id=device_id,
            kind=device.kind,
            location=update.location,
            timestamp_ms=update.timestamp_ms,
            heading_deg=update.heading_deg,
            speed_mps=update.speed_mps,
        )

    def get_devices_in_viewport(
        self, viewport: Viewport, *, now_ms: Optional[int] = None
    ) -> list[DeviceSnapshot]:
        """
        Read path for the rider map: drivers visible in the current bbox.

        Filters stale GPS and refines geohash candidates to the true viewport.
        """
        active_ids = {
            u.device_id for u in self._store.all_fresh(now_ms=now_ms)
        }
        candidate_ids = self._index.query_viewport(
            viewport, active_device_ids=active_ids
        )
        snapshots: list[DeviceSnapshot] = []
        for device_id in candidate_ids:
            snap = self.get_device_location(device_id, now_ms=now_ms)
            if snap is None:
                continue
            if not _point_in_viewport(snap.location, viewport):
                continue
            snapshots.append(snap)
        snapshots.sort(key=lambda s: s.device_id)
        return snapshots

    def subscribe_map(
        self, subscriber_id: str, viewport: Viewport
    ) -> MapSubscription:
        """Rider opens the map; WebSocket gateway tracks the viewport."""
        sub = self._ws.subscribe(subscriber_id, viewport)
        self._events.publish(
            Event(
                EventType.MAP_SUBSCRIBED,
                {
                    "subscription_id": sub.subscription_id,
                    "subscriber_id": subscriber_id,
                    "viewport": {
                        "min_lat": viewport.min_lat,
                        "max_lat": viewport.max_lat,
                        "min_lng": viewport.min_lng,
                        "max_lng": viewport.max_lng,
                    },
                },
            )
        )
        return sub

    def sweep_stale_devices(self, *, now_ms: Optional[int] = None) -> list[str]:
        """
        Background job: remove devices that stopped heartbeating.

        Production: Redis TTL + Kafka tombstone; map clients remove the marker.
        """
        removed: list[str] = []
        for device_id in self._store.stale_device_ids(now_ms=now_ms):
            self._index.remove(device_id)
            self._store.remove(device_id)
            removed.append(device_id)
            self._events.publish(
                Event(
                    EventType.DEVICE_WENT_STALE,
                    {"device_id": device_id},
                )
            )
        return removed

    def seed_viewport_snapshot(
        self, subscriber_id: str, viewport: Viewport, *, now_ms: Optional[int] = None
    ) -> list[DeviceSnapshot]:
        """
        Initial map load: HTTP returns current positions, then WebSocket deltas.

        Typical flow: GET /map/devices?bbox=... then WS subscribe for updates.
        """
        return self.get_devices_in_viewport(viewport, now_ms=now_ms)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    now = int(time.time() * 1000)
    service = LocationTrackingService(stale_after_ms=30_000)
    pushes: list[dict] = []
    service.event_bus.subscribe(
        EventType.LOCATION_UPDATED,
        lambda e: pushes.append(e.payload),
    )

    sf_viewport = Viewport(37.77, 37.78, -122.42, -122.41)
    service.register_device(TrackedDevice("driver-1", DeviceKind.DRIVER))
    service.register_device(TrackedDevice("driver-2", DeviceKind.DRIVER))

    sub = service.subscribe_map("rider-42", sf_viewport)

    service.ingest_location(
        LocationUpdate("driver-1", Location(37.775, -122.419), now, heading_deg=90.0),
        now_ms=now,
    )
    service.ingest_location(
        LocationUpdate("driver-2", Location(37.776, -122.418), now + 1000),
        now_ms=now + 1000,
    )
    # Driver 1 moves — rider should get a WebSocket delta
    service.ingest_location(
        LocationUpdate("driver-1", Location(37.7755, -122.4185), now + 3000),
        now_ms=now + 3000,
    )

    visible = service.get_devices_in_viewport(sf_viewport, now_ms=now + 3000)
    assert len(visible) == 2
    assert service.websocket_gateway.outbox
    assert any(m["subscriber_id"] == "rider-42" for m in service.websocket_gateway.outbox)

    # Stale driver drops off the map
    service.ingest_location(
        LocationUpdate("driver-2", Location(37.776, -122.418), now + 5000),
        now_ms=now + 40_000,
    )
    stale = service.sweep_stale_devices(now_ms=now + 40_000)
    assert "driver-1" in stale

    print(f"visible drivers: {[s.device_id for s in visible]}")
    print(f"websocket messages: {len(service.websocket_gateway.outbox)}")
    print(f"events: {len(service.event_bus.history)}, pushes: {len(pushes)}")
    print(f"stale removed: {stale}")

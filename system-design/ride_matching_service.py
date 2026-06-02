# 1. Ride Matching Service (Highest Probability)
#
# "Design Uber/Lyft ride matching."
#
# This is almost the canonical Lyft interview.
#
# Requirements:
# * Drivers publish location every few seconds
# * Riders request rides
# * Match nearest driver
# * Handle surge demand
# * Support millions of users
#
# Topics:
# * Geospatial indexing
# * Driver location storage
# * Matching algorithms
# * Event-driven architecture
# * Scalability
#
# Interview talk track (senior loop):
#   1. Clarify: ride types, driver availability, idempotent retries, ETA vs distance.
#   2. Data path: driver app -> location ingest -> geo index; rider -> match API -> assign.
#   3. Geo index: grid partition (here) or Redis GEO / S2 / H3 at scale; shard by geohash.
#   4. Matching: expand rings around rider cell; lock driver (optimistic) to avoid double-assign.
#   5. Surge: supply/demand ratio per region; precomputed multipliers on a timer + event-driven.
#   6. Scale: Kafka for location stream + match queue, regional cells, read replicas for rides DB.
#
# Architecture (mermaid):
#
# ```mermaid
# flowchart TB
#     subgraph Clients
#         DA[Driver App]
#         RA[Rider App]
#     end
#
#     subgraph Ingest["Location ingest (hot write path)"]
#         LI[Location Ingest API]
#         LQ[(Kafka: driver.locations)]
#     end
#
#     subgraph Matching["Match path"]
#         MA[Match API]
#         RMS[RideMatchingService]
#         MQ[(Kafka: ride.requested)]
#     end
#
#     subgraph Core["In-memory core (this file)"]
#         GI[GridGeospatialIndex]
#         SP[SurgePricingService]
#         DL[Driver lock set]
#         IDEM[Idempotency cache]
#         RIDES[(Rides store)]
#     end
#
#     subgraph ProdScale["Production scale-out"]
#         REDIS[(Redis GEO / H3 shards)]
#         LOCK[(Redis SET NX driver locks)]
#         DB[(Rides DB + replicas)]
#     end
#
#     subgraph Events["EventBus → Kafka topics"]
#         EB{EventBus}
#         T1[driver.location.updated]
#         T2[ride.requested]
#         T3[ride.matched]
#         T4[surge.updated]
#     end
#
#     subgraph Consumers["Async consumers"]
#         PN[Push notifications]
#         AN[Analytics / ETA]
#         BL[Billing / surge audit]
#     end
#
#     DA -->|GPS every ~3s| LI
#     LI --> LQ
#     LQ --> GI
#     LI --> GI
#
#     RA -->|POST /rides| MA
#     MA --> RMS
#     MA --> MQ
#     MQ --> RMS
#
#     RMS --> GI
#     RMS --> SP
#     RMS --> DL
#     RMS --> IDEM
#     RMS --> RIDES
#
#     GI -.->|at scale| REDIS
#     DL -.->|at scale| LOCK
#     RIDES -.->|at scale| DB
#
#     RMS --> EB
#     EB --> T1 & T2 & T3 & T4
#     T1 & T2 & T3 & T4 --> PN & AN & BL
#
#     SP -->|supply/demand per cell| T4
# ```
#
# In-memory reference: grid index + event bus. Production replaces index with Redis GEO
# and persists state in DynamoDB/Postgres with idempotent consumers.

from __future__ import annotations

import math
import uuid
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Protocol


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


class DriverStatus(str, Enum):
    """Whether a driver can receive a new match."""

    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


class RideType(str, Enum):
    """Product line requested by the rider."""

    STANDARD = "standard"
    XL = "xl"
    LUX = "lux"


@dataclass(frozen=True)
class Location:
    """A point on the map (WGS84 latitude/longitude in degrees)."""

    lat: float
    lng: float


@dataclass
class Driver:
    """Supply unit tracked in the matching pool."""

    driver_id: str
    location: Location
    status: DriverStatus = DriverStatus.AVAILABLE
    ride_types: frozenset[RideType] = frozenset({RideType.STANDARD})


@dataclass(frozen=True)
class RideRequest:
    """Rider intent to be matched to a driver."""

    rider_id: str
    pickup: Location
    ride_type: RideType = RideType.STANDARD
    request_id: Optional[str] = None


@dataclass(frozen=True)
class MatchResult:
    """Outcome of a successful match."""

    ride_id: str
    driver_id: str
    eta_seconds: int
    surge_multiplier: float
    distance_meters: float


class NoDriversAvailableError(Exception):
    """Raised when no eligible driver exists within the search radius."""


# ---------------------------------------------------------------------------
# Events (event-driven architecture sketch)
# ---------------------------------------------------------------------------


class EventType(str, Enum):
    """Topics you would map to Kafka/SNS in production."""

    DRIVER_LOCATION_UPDATED = "driver.location.updated"
    RIDE_REQUESTED = "ride.requested"
    RIDE_MATCHED = "ride.matched"
    SURGE_UPDATED = "surge.updated"


@dataclass(frozen=True)
class Event:
    """Envelope for async consumers (analytics, ETA, notifications)."""

    event_type: EventType
    payload: dict


EventHandler = Callable[[Event], None]


class EventBus:
    """
    In-process pub/sub stand-in for Kafka/SQS.

    Production: location updates fan out to geo-index workers; match events
    trigger push notifications and billing.
    """

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventHandler]] = defaultdict(list)
        self.history: list[Event] = []

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Register a handler for a single event type."""
        self._handlers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        """Deliver an event to all subscribers synchronously (demo only)."""
        self.history.append(event)
        for handler in self._handlers[event.event_type]:
            handler(event)


# ---------------------------------------------------------------------------
# Geospatial index (grid partition)
# ---------------------------------------------------------------------------


def _haversine_meters(a: Location, b: Location) -> float:
    """Great-circle distance between two lat/lng points in meters."""
    radius_m = 6_371_000.0
    lat1, lon1 = math.radians(a.lat), math.radians(a.lng)
    lat2, lon2 = math.radians(b.lat), math.radians(b.lng)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return 2 * radius_m * math.asin(math.sqrt(h))


class GeospatialIndex(Protocol):
    """Contract for any geo index (grid, geohash, R-tree, Redis GEO)."""

    def upsert_driver(self, driver: Driver) -> None:
        """Insert or move a driver in the index."""

    def remove_driver(self, driver_id: str) -> None:
        """Remove a driver from the index."""

    def get_driver(self, driver_id: str) -> Optional[Driver]:
        """Return a driver by id, or None if not indexed."""

    def nearest_drivers(
        self,
        pickup: Location,
        *,
        ride_type: RideType,
        max_candidates: int = 5,
        max_radius_m: float = 10_000.0,
    ) -> list[tuple[Driver, float]]:
        """Return up to max_candidates drivers within max_radius_m, sorted by distance."""

    def count_available_in_cell(self, location: Location) -> int:
        """Count available drivers near location (surge supply signal)."""


class GridGeospatialIndex:
    """
    Uniform grid over lat/lng for sub-linear nearest-neighbor search.

    Cell size ~500 m (typical urban). Search expands in rings until enough
    candidates or max_radius_m is reached. At millions of drivers, shard cells
    by (cell_x, cell_y) across Redis cluster nodes.
    """

    # ~500 m latitude step; longitude step adjusted by cos(lat) below.
    _CELL_SIZE_M = 500.0
    _METERS_PER_DEG_LAT = 111_320.0

    def __init__(self) -> None:
        self._drivers: dict[str, Driver] = {}
        self._cells: dict[tuple[int, int], set[str]] = defaultdict(set)

    def upsert_driver(self, driver: Driver) -> None:
        """Insert or update a driver's cell membership."""
        existing = self._drivers.get(driver.driver_id)
        if existing is not None:
            old_cell = self._cell_key(existing.location)
            self._cells[old_cell].discard(driver.driver_id)
            if not self._cells[old_cell]:
                del self._cells[old_cell]

        self._drivers[driver.driver_id] = driver
        self._cells[self._cell_key(driver.location)].add(driver.driver_id)

    def remove_driver(self, driver_id: str) -> None:
        """Drop a driver from the index entirely."""
        driver = self._drivers.pop(driver_id, None)
        if driver is None:
            return
        cell = self._cell_key(driver.location)
        self._cells[cell].discard(driver_id)
        if not self._cells[cell]:
            del self._cells[cell]

    def get_driver(self, driver_id: str) -> Optional[Driver]:
        """Return a driver by id, or None if not indexed."""
        return self._drivers.get(driver_id)

    def nearest_drivers(
        self,
        pickup: Location,
        *,
        ride_type: RideType,
        max_candidates: int = 5,
        max_radius_m: float = 10_000.0,
    ) -> list[tuple[Driver, float]]:
        """
        Expand grid rings from pickup until enough eligible drivers are found.

        Filters by availability, ride type, and max_radius_m; returns closest first.
        """
        origin = self._cell_key(pickup)
        ring = 0
        max_rings = int(math.ceil(max_radius_m / self._CELL_SIZE_M)) + 1
        candidates: list[tuple[Driver, float]] = []

        while ring <= max_rings and len(candidates) < max_candidates:
            for cell in self._ring_cells(origin, ring):
                for driver_id in self._cells.get(cell, ()):
                    driver = self._drivers[driver_id]
                    if driver.status != DriverStatus.AVAILABLE:
                        continue
                    if ride_type not in driver.ride_types:
                        continue
                    distance = _haversine_meters(pickup, driver.location)
                    if distance <= max_radius_m:
                        candidates.append((driver, distance))
            ring += 1

        candidates.sort(key=lambda item: item[1])
        return candidates[:max_candidates]

    def count_available_in_cell(self, location: Location) -> int:
        """Count available drivers in the pickup cell (surge supply signal)."""
        cell = self._cell_key(location)
        return sum(
            1
            for driver_id in self._cells.get(cell, ())
            if self._drivers[driver_id].status == DriverStatus.AVAILABLE
        )

    def _cell_key(self, location: Location) -> tuple[int, int]:
        """Map a location to integer grid coordinates."""
        lat_step = self._CELL_SIZE_M / self._METERS_PER_DEG_LAT
        lng_step = lat_step / max(math.cos(math.radians(location.lat)), 1e-6)
        return (int(location.lat / lat_step), int(location.lng / lng_step))

    def _ring_cells(self, origin: tuple[int, int], ring: int) -> list[tuple[int, int]]:
        """Return all cell keys at Manhattan ring distance `ring` from origin."""
        if ring == 0:
            return [origin]
        ox, oy = origin
        cells: list[tuple[int, int]] = []
        for dx in range(-ring, ring + 1):
            for dy in range(-ring, ring + 1):
                if max(abs(dx), abs(dy)) == ring:
                    cells.append((ox + dx, oy + dy))
        return cells


# ---------------------------------------------------------------------------
# Surge pricing
# ---------------------------------------------------------------------------


class SurgePricingService:
    """
    Region-level surge from supply/demand imbalance.

    Production: Flink job aggregates requests + available drivers per H3 cell;
    writes multipliers to a low-latency cache refreshed every 30–60 s.
    """

    _BASE_MULTIPLIER = 1.0
    _MAX_MULTIPLIER = 3.0
    _DEMAND_THRESHOLD = 3  # pending requests in cell before surge kicks in

    def __init__(self, geo_index: GeospatialIndex) -> None:
        self._geo_index = geo_index
        self._pending_demand: dict[tuple[int, int], int] = defaultdict(int)

    def record_demand(self, pickup: Location, cell_key: tuple[int, int]) -> None:
        """Increment pending demand for the pickup cell (call on ride request)."""
        self._pending_demand[cell_key] += 1

    def clear_demand(self, cell_key: tuple[int, int]) -> None:
        """Decrement demand after match or timeout."""
        if self._pending_demand[cell_key] > 0:
            self._pending_demand[cell_key] -= 1

    def multiplier_for(self, pickup: Location, cell_key: tuple[int, int]) -> float:
        """
        Compute surge multiplier from pending demand vs available supply.

        ratio > 1 means more riders than drivers in the cell → higher fare.
        """
        demand = self._pending_demand[cell_key]
        supply = max(1, self._geo_index.count_available_in_cell(pickup))
        if demand <= self._DEMAND_THRESHOLD:
            return self._BASE_MULTIPLIER
        ratio = demand / supply
        surge = self._BASE_MULTIPLIER + (ratio - 1) * 0.5
        return min(self._MAX_MULTIPLIER, round(surge, 2))


# ---------------------------------------------------------------------------
# Ride matching service
# ---------------------------------------------------------------------------


class RideMatchingService:
    """
    Orchestrates driver location ingest, geo-indexed matching, surge, and events.

    Scale-out: partition by geohash prefix; match workers consume ride.requested
    from a queue; driver locks stored in Redis with TTL to prevent double booking.
    """

    _AVG_SPEED_M_S = 11.0  # ~25 mph urban driving

    def __init__(
        self,
        geo_index: Optional[GeospatialIndex] = None,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._geo_index: GeospatialIndex = geo_index or GridGeospatialIndex()
        self._events = event_bus or EventBus()
        self._surge = SurgePricingService(self._geo_index)
        self._rides: dict[str, MatchResult] = {}
        self._idempotency: dict[str, MatchResult] = {}
        self._driver_locks: set[str] = set()

    @property
    def event_bus(self) -> EventBus:
        """Expose the bus for tests and demo subscribers."""
        return self._events

    def register_driver(self, driver: Driver) -> None:
        """Add or replace a driver in the geo index."""
        self._geo_index.upsert_driver(driver)

    def update_driver_location(self, driver_id: str, location: Location) -> None:
        """
        Ingest a periodic location ping (every few seconds from the driver app).

        Hot path at scale: write to Kafka -> geo-index worker upserts Redis GEO.
        """
        driver = self._geo_index.get_driver(driver_id)
        if driver is None:
            raise KeyError(f"unknown driver: {driver_id}")

        updated = Driver(
            driver_id=driver.driver_id,
            location=location,
            status=driver.status,
            ride_types=driver.ride_types,
        )
        self._geo_index.upsert_driver(updated)
        self._events.publish(
            Event(
                EventType.DRIVER_LOCATION_UPDATED,
                {"driver_id": driver_id, "lat": location.lat, "lng": location.lng},
            )
        )

    def set_driver_status(self, driver_id: str, status: DriverStatus) -> None:
        """Mark a driver available, busy, or offline."""
        driver = self._geo_index.get_driver(driver_id)
        if driver is None:
            raise KeyError(f"unknown driver: {driver_id}")
        driver.status = status
        self._geo_index.upsert_driver(driver)

    def match_ride(self, request: RideRequest) -> MatchResult:
        """
        Match a rider to the nearest eligible driver and apply surge pricing.

        Idempotent on request_id. Raises NoDriversAvailableError when no driver
        is found within the search radius.
        """
        if request.request_id:
            cached = self._idempotency.get(request.request_id)
            if cached is not None:
                return cached

        self._events.publish(
            Event(
                EventType.RIDE_REQUESTED,
                {
                    "rider_id": request.rider_id,
                    "lat": request.pickup.lat,
                    "lng": request.pickup.lng,
                    "ride_type": request.ride_type.value,
                },
            )
        )
        cell_key = self._cell_key(request.pickup)
        self._surge.record_demand(request.pickup, cell_key)

        try:
            candidates = self._geo_index.nearest_drivers(
                request.pickup, ride_type=request.ride_type
            )
            driver, distance_m = self._select_driver(candidates)
            if driver is None:
                raise NoDriversAvailableError(
                    f"no drivers for ride_type={request.ride_type.value}"
                )

            surge = self._surge.multiplier_for(request.pickup, cell_key)
            eta_seconds = max(1, int(math.ceil(distance_m / self._AVG_SPEED_M_S)))
            ride_id = str(uuid.uuid4())
            result = MatchResult(
                ride_id=ride_id,
                driver_id=driver.driver_id,
                eta_seconds=eta_seconds,
                surge_multiplier=surge,
                distance_meters=round(distance_m, 1),
            )

            self._lock_driver(driver.driver_id)
            self._rides[ride_id] = result
            if request.request_id:
                self._idempotency[request.request_id] = result

            self._events.publish(
                Event(
                    EventType.RIDE_MATCHED,
                    {
                        "ride_id": ride_id,
                        "driver_id": driver.driver_id,
                        "rider_id": request.rider_id,
                        "surge_multiplier": surge,
                    },
                )
            )
            self._events.publish(
                Event(
                    EventType.SURGE_UPDATED,
                    {"lat": request.pickup.lat, "lng": request.pickup.lng, "multiplier": surge},
                )
            )
            return result
        finally:
            self._surge.clear_demand(cell_key)

    def _cell_key(self, location: Location) -> tuple[int, int]:
        """Delegate to grid index cell math (surge partitioning)."""
        if isinstance(self._geo_index, GridGeospatialIndex):
            return self._geo_index._cell_key(location)
        # Fallback for alternate indexes: bucket by rounded lat/lng.
        return (int(location.lat * 1000), int(location.lng * 1000))

    def get_ride(self, ride_id: str) -> Optional[MatchResult]:
        """Look up a prior match by ride_id."""
        return self._rides.get(ride_id)

    def _select_driver(
        self, candidates: list[tuple[Driver, float]]
    ) -> tuple[Optional[Driver], float]:
        """Pick the closest driver that is not already locked for assignment."""
        for driver, distance in candidates:
            if driver.driver_id not in self._driver_locks:
                return driver, distance
        return None, math.inf

    def _lock_driver(self, driver_id: str) -> None:
        """Reserve a driver (optimistic lock; production uses Redis SET NX EX)."""
        self._driver_locks.add(driver_id)
        self.set_driver_status(driver_id, DriverStatus.BUSY)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    service = RideMatchingService()
    matched_events: list[dict] = []
    service.event_bus.subscribe(
        EventType.RIDE_MATCHED,
        lambda e: matched_events.append(e.payload),
    )

    # Register drivers near downtown SF
    service.register_driver(
        Driver("d1", Location(37.7749, -122.4194), DriverStatus.AVAILABLE)
    )
    service.register_driver(
        Driver("d2", Location(37.7849, -122.4094), DriverStatus.AVAILABLE)
    )
    service.register_driver(
        Driver(
            "d3",
            Location(37.7755, -122.4180),
            DriverStatus.AVAILABLE,
            frozenset({RideType.LUX}),
        )
    )

    # Driver location stream
    service.update_driver_location("d1", Location(37.7750, -122.4190))

    req = RideRequest(
        rider_id="r1",
        pickup=Location(37.7751, -122.4191),
        request_id="idem-ride-1",
    )
    match = service.match_ride(req)
    assert match.driver_id == "d1"
    assert match.surge_multiplier == 1.0
    assert service.match_ride(req).ride_id == match.ride_id  # idempotent

    # Surge: pile up demand with only one standard driver left (d2)
    service.set_driver_status("d2", DriverStatus.OFFLINE)
    service.register_driver(
        Driver("d4", Location(37.7760, -122.4185), DriverStatus.AVAILABLE)
    )
    for i in range(4):
        try:
            service.match_ride(
                RideRequest(f"r-surged-{i}", Location(37.7760, -122.4185))
            )
        except NoDriversAvailableError:
            pass

    print(f"matched driver {match.driver_id}, eta {match.eta_seconds}s, "
          f"surge {match.surge_multiplier}x, distance {match.distance_meters}m")
    print(f"events emitted: {len(service.event_bus.history)}")

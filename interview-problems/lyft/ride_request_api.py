# Ride request API
# Problema: “Diseña una API para solicitar viajes.”
#
# Ejemplo:
#   Input:  RideRequest(rider_id, pickup, ...)
#   Output: RideAssigned(ride_id, driver_id, eta_seconds, status)
#
# Interview flow:
#   1. Clarify contract (pickup required, ride types, idempotency key).
#   2. Model request/response + errors (no drivers, duplicate request).
#   3. Match nearest available driver; mark driver busy.
#   4. Discuss scale: geo index (Redis GEO / S2), async via Kafka/SQS, idempotent consumers.
#
# In-memory reference: O(D) per request over available drivers D.
# Production: shard by geohash, push match work to a queue, persist ride state in DB.

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RideStatus(str, Enum):
    """Lifecycle state returned to the rider after a successful match."""

    ASSIGNED = "assigned"
    NO_DRIVERS = "no_drivers"


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


@dataclass(frozen=True)
class RideRequest:
    """Payload for POST /rides (simplified)."""

    rider_id: str
    pickup: Location
    dropoff: Optional[Location] = None
    ride_type: RideType = RideType.STANDARD
    # Client-generated; retries with the same key return the same assignment.
    request_id: Optional[str] = None


@dataclass(frozen=True)
class RideAssigned:
    """Successful match response."""

    ride_id: str
    driver_id: str
    eta_seconds: int
    status: RideStatus = RideStatus.ASSIGNED


@dataclass
class Driver:
    """Available supply unit in the matching pool."""

    driver_id: str
    location: Location
    ride_types: frozenset[RideType] = frozenset({RideType.STANDARD})
    available: bool = True


class NoDriversAvailableError(Exception):
    """Raised when no driver can serve the request."""


class RideRequestAPI:
    """
    In-memory ride request API: match a rider to the nearest eligible driver.

    Talk track for senior loop: idempotent request_id, driver locking, eventual
    consistency if matching moves async, DLQ on failed assign events.
    """

    # Rough urban driving speed for ETA (m/s) — ~25 mph.
    _AVG_SPEED_M_S = 11.0

    def __init__(self) -> None:
        self._drivers: dict[str, Driver] = {}
        self._rides: dict[str, RideAssigned] = {}
        self._idempotency: dict[str, RideAssigned] = {}

    def register_driver(self, driver: Driver) -> None:
        """Add or replace a driver in the supply pool."""
        self._drivers[driver.driver_id] = driver

    def request_ride(self, ride_request: RideRequest) -> RideAssigned:
        """
        Match ride_request to the nearest available driver that supports ride_type.

        Duplicate request_id returns the prior assignment without re-matching.
        Raises NoDriversAvailableError when no eligible driver exists.
        """
        if ride_request.request_id:
            cached = self._idempotency.get(ride_request.request_id)
            if cached is not None:
                return cached

        driver = self._find_nearest_driver(ride_request)
        if driver is None:
            raise NoDriversAvailableError(
                f"no drivers for ride_type={ride_request.ride_type.value}"
            )

        distance_m = _haversine_meters(ride_request.pickup, driver.location)
        eta_seconds = max(1, int(math.ceil(distance_m / self._AVG_SPEED_M_S)))

        ride_id = str(uuid.uuid4())
        assigned = RideAssigned(
            ride_id=ride_id,
            driver_id=driver.driver_id,
            eta_seconds=eta_seconds,
            status=RideStatus.ASSIGNED,
        )

        driver.available = False
        self._rides[ride_id] = assigned
        if ride_request.request_id:
            self._idempotency[ride_request.request_id] = assigned
        return assigned

    def get_ride(self, ride_id: str) -> Optional[RideAssigned]:
        """Look up an assignment by ride_id (read path after request_ride)."""
        return self._rides.get(ride_id)

    def _find_nearest_driver(self, ride_request: RideRequest) -> Optional[Driver]:
        """Return the closest available driver that supports the requested ride type."""
        best: Optional[Driver] = None
        best_distance = math.inf

        for driver in self._drivers.values():
            if not driver.available:
                continue
            if ride_request.ride_type not in driver.ride_types:
                continue
            distance = _haversine_meters(ride_request.pickup, driver.location)
            if distance < best_distance:
                best_distance = distance
                best = driver

        return best


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


if __name__ == "__main__":
    api = RideRequestAPI()
    api.register_driver(
        Driver("d1", Location(37.7749, -122.4194), frozenset({RideType.STANDARD}))
    )
    api.register_driver(
        Driver("d2", Location(37.7849, -122.4094), frozenset({RideType.STANDARD}))
    )

    req = RideRequest(
        rider_id="r1",
        pickup=Location(37.7750, -122.4190),
        request_id="idem-1",
    )
    assigned = api.request_ride(req)
    assert assigned.driver_id == "d1"  # closer to pickup
    assert assigned.status == RideStatus.ASSIGNED

    # Idempotent retry
    assert api.request_ride(req).ride_id == assigned.ride_id

    print(
        f"ride {assigned.ride_id}: driver {assigned.driver_id}, "
        f"eta {assigned.eta_seconds}s"
    )

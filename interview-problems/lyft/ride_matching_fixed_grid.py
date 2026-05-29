from collections import defaultdict
from math import radians, sin, cos, sqrt, atan2

class FixedGridMatcher:
    """Ride matcher using fixed-size grid buckets in memory."""

    def __init__(self, cell_size_deg: float = 0.01):
        """
        Initialize grid index.
        cell_size_deg: cell size in degree units (approx; good enough for interview).
        """
        self.cell_size_deg = cell_size_deg
        self.grid = defaultdict(dict)  # {(gx, gy): {driver_id: (lat, lng)}}
        self.driver_cell = {}          # {driver_id: (gx, gy)}

    def _cell_of(self, lat: float, lng: float) -> tuple[int, int]:
        """Map lat/lng to a grid cell."""
        return (int(lat / self.cell_size_deg), int(lng / self.cell_size_deg))

    def upsert_driver(self, driver_id: str, lat: float, lng: float) -> None:
        """Insert or move a driver to its new cell."""
        new_cell = self._cell_of(lat, lng)
        old_cell = self.driver_cell.get(driver_id)

        if old_cell is not None and old_cell != new_cell:
            self.grid[old_cell].pop(driver_id, None)

        self.grid[new_cell][driver_id] = (lat, lng)
        self.driver_cell[driver_id] = new_cell

    def remove_driver(self, driver_id: str) -> None:
        """Remove driver from index."""
        old_cell = self.driver_cell.pop(driver_id, None)
        if old_cell is not None:
            self.grid[old_cell].pop(driver_id, None)

    def _dist2(self, a_lat: float, a_lng: float, b_lat: float, b_lng: float) -> float:
        """Squared euclidean distance (interview simplification)."""
        return (a_lat - b_lat) ** 2 + (a_lng - b_lng) ** 2

    def closest_driver(self, rider_lat: float, rider_lng: float, max_ring: int = 6) -> str | None:
        """
        Find nearest driver by expanding neighbor rings around rider cell.
        max_ring controls search expansion if nearby cells are empty.
        """
        cx, cy = self._cell_of(rider_lat, rider_lng)
        best_id, best_d2 = None, float("inf")

        for ring in range(max_ring + 1):
            # Scan square border of this ring
            for x in range(cx - ring, cx + ring + 1):
                for y in range(cy - ring, cy + ring + 1):
                    if ring > 0 and (x not in (cx - ring, cx + ring) and y not in (cy - ring, cy + ring)):
                        continue  # skip inner area, only border
                    for driver_id, (dlat, dlng) in self.grid.get((x, y), {}).items():
                        d2 = self._dist2(rider_lat, rider_lng, dlat, dlng)
                        if d2 < best_d2:
                            best_d2, best_id = d2, driver_id

            # Optional early-stop: if we found candidates in this ring, return.
            if best_id is not None:
                return best_id

        return best_id
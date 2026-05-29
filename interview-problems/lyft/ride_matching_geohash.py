from collections import defaultdict
import geohash2  # pip install geohash2

class GeohashInMemoryMatcher:
    """Ride matcher using in-memory geohash buckets."""

    def __init__(self, precision: int = 7):
        """
        precision controls cell size (higher precision => smaller cells).
        """
        self.precision = precision
        self.buckets = defaultdict(dict)   # {hash: {driver_id: (lat, lng)}}
        self.driver_hash = {}              # {driver_id: hash}

    def _hash(self, lat: float, lng: float) -> str:
        """Encode location to geohash."""
        return geohash2.encode(lat, lng, self.precision)

    def upsert_driver(self, driver_id: str, lat: float, lng: float) -> None:
        """Insert or move driver to new geohash bucket."""
        new_h = self._hash(lat, lng)
        old_h = self.driver_hash.get(driver_id)
        if old_h and old_h != new_h:
            self.buckets[old_h].pop(driver_id, None)
        self.buckets[new_h][driver_id] = (lat, lng)
        self.driver_hash[driver_id] = new_h

    def closest_driver(self, rider_lat: float, rider_lng: float) -> str | None:
        """Search current geohash + neighbors and return nearest driver."""
        center = self._hash(rider_lat, rider_lng)
        neighbors = geohash2.neighbors(center)  # 8 adjacent cells
        candidates_hashes = [center] + neighbors

        best_id, best_d2 = None, float("inf")
        for h in candidates_hashes:
            for driver_id, (dlat, dlng) in self.buckets.get(h, {}).items():
                d2 = (dlat - rider_lat) ** 2 + (dlng - rider_lng) ** 2
                if d2 < best_d2:
                    best_d2, best_id = d2, driver_id

        return best_id









import redis

class RedisGeoMatcher:
    """Ride matcher using Redis native GEO index."""

    def __init__(self, redis_client: redis.Redis, key: str = "drivers:geo"):
        """
        key is the Redis sorted set key used for geo index.
        """
        self.r = redis_client
        self.key = key

    def upsert_driver(self, driver_id: str, lat: float, lng: float) -> None:
        """Insert or update driver coordinates in Redis GEO index."""
        # GEO uses (longitude, latitude)
        self.r.geoadd(self.key, [lng, lat, driver_id])

    def remove_driver(self, driver_id: str) -> None:
        """Remove driver from Redis GEO index."""
        self.r.zrem(self.key, driver_id)

    def closest_driver(self, rider_lat: float, rider_lng: float, radius_km: float = 3.0) -> str | None:
        """
        Query nearest driver within radius.
        Expands radius if needed in production logic.
        """
        # Redis >= 6.2: GEOSEARCH
        res = self.r.geosearch(
            self.key,
            longitude=rider_lng,
            latitude=rider_lat,
            radius=radius_km,
            unit="km",
            sort="ASC",
            count=1
        )
        if not res:
            return None
        return res[0].decode() if isinstance(res[0], bytes) else res[0]
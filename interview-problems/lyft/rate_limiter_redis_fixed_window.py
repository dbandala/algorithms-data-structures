# Rate limiter
# Problema
# “Diseña e implementa un rate limiter para una API de Lyft.”

# Ejemplo:
# * Cada usuario puede hacer:
#     * 100 requests por minuto
# * Si excede el límite:
#     * regresar HTTP 429

# Implementar algo como:
# allow_request(user_id: str) -> bool

# Nivel Senior
# * Complejidad temporal
# * Memory efficiency
# * Race conditions
# * Distributed systems thinking
# * Redis discussion
# * Sliding window vs token bucket
# * Horizontal scaling

import time
import redis
from typing import Optional

class RedisFixedWindowRateLimiter:
    """
    Fixed-window rate limiter distributed using Redis INCR + TTL.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        max_requests: int,
        window_seconds: int,
        prefix: str = "rate_limit",
    ) -> None:
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.prefix = prefix

    def _build_key(self, user_id: str, now: Optional[float] = None) -> str:
        if now is None:
            now = time.time()
        window_index = int(now // self.window_seconds)
        return f"{self.prefix}:{user_id}:{window_index}"

    def allow_request(self, user_id: str) -> bool:
        """
        Distributed fixed-window rate limit:
        - Returns True if request is allowed.
        - Returns False once max_requests is exceeded in current window.
        """
        key = self._build_key(user_id)
        # Atomic increment returns new count
        current = self.redis.incr(key)

        if current == 1:
            # First request in this window, set TTL
            # Small buffer avoids early expiry issues
            self.redis.expire(key, self.window_seconds + 1)

        if current > self.max_requests:
            return False
        return True






RATE_LIMIT_LUA = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])

local current = redis.call("INCR", key)
if current == 1 then
  redis.call("EXPIRE", key, ttl)
end

if current > limit then
  return 0   -- reject
else
  return 1   -- allow
end
"""

class RedisFixedWindowRateLimiterLua:
    """
    Fixed-window limiter con INCR+EXPIRE atómico vía Lua.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        max_requests: int,
        window_seconds: int,
        prefix: str = "rate_limit",
    ) -> None:
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.prefix = prefix
        self._lua = self.redis.register_script(RATE_LIMIT_LUA)

    def _build_key(self, user_id: str, now: Optional[float] = None) -> str:
        if now is None:
            now = time.time()
        window_index = int(now // self.window_seconds)
        return f"{self.prefix}:{user_id}:{window_index}"

    def allow_request(self, user_id: str) -> bool:
        key = self._build_key(user_id)
        result = self._lua(
            keys=[key],
            args=[self.max_requests, self.window_seconds + 1],
        )
        return bool(result)
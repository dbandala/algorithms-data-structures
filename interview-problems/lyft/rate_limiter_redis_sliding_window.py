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

SLIDING_WINDOW_COUNTER_LUA = """
local curr_key = KEYS[1]
local prev_key = KEYS[2]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local elapsed = tonumber(ARGV[3])

local curr = tonumber(redis.call("GET", curr_key) or "0")
local prev = tonumber(redis.call("GET", prev_key) or "0")

local weight_prev = (window - elapsed) / window
local estimated = curr + prev * weight_prev

if estimated >= limit then
  return 0
end

local new_count = redis.call("INCR", curr_key)
if new_count == 1 then
  redis.call("EXPIRE", curr_key, window * 2 + 1)
end

return 1
"""


class RedisSlidingWindowCounterLimiter:
    """
    Distributed sliding window counter rate limiter using Redis.
    Uses current and previous fixed-window counters with weighted blending.
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
        self._lua = self.redis.register_script(SLIDING_WINDOW_COUNTER_LUA)

    def _window_index(self, now: float) -> int:
        """Return the fixed-window bucket index for a timestamp."""
        return int(now // self.window_seconds)

    def _elapsed_in_window(self, now: float) -> float:
        """Return seconds elapsed inside the current fixed window."""
        return now - self._window_index(now) * self.window_seconds

    def _build_keys(self, user_id: str, now: Optional[float] = None) -> tuple[str, str]:
        """Build Redis keys for current and previous window counters."""
        if now is None:
            now = time.time()

        window_index = self._window_index(now)
        curr_key = f"{self.prefix}:{user_id}:{window_index}"
        prev_key = f"{self.prefix}:{user_id}:{window_index - 1}"
        return curr_key, prev_key

    def allow_request(self, user_id: str) -> bool:
        """
        Return True if the request is allowed under the sliding window estimate.
        Return False when the weighted count reaches max_requests.
        """
        now = time.time()
        curr_key, prev_key = self._build_keys(user_id, now)
        elapsed = self._elapsed_in_window(now)

        result = self._lua(
            keys=[curr_key, prev_key],
            args=[self.max_requests, self.window_seconds, elapsed],
        )
        return bool(result)
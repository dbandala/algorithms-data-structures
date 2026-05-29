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

from collections import deque, defaultdict
import time 


# time complexity: O(1) for each request amortized
# because the while loop only runs when the request is outside the time window, and the deque operations are O(1)
# space complexity: O(n) for the requests dictionary
class RateLimiter(object):
    def __init__(self, max_requests: int, time_window: int):
        """
        type max_requests: int
        type time_window: int
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque) # user_id -> deque of timestamps

    def allow_request(self, user_id: str) -> bool:
        """
        Rate limiter per user and time
        type user_id: str
        rtype: bool
        """

        now = time.time()
        user_requests = self.requests[user_id]

        # remove old requests outside the time window
        while user_requests and user_requests[0]<now-self.time_window:
            user_requests.popleft()

        if len(user_requests)>=self.max_requests:
            return False
        
        user_requests.append(now)
        return True


class SlidingWindowCounterLimiter:
    """
    Sliding window counter per user.
    Keeps current and previous fixed-window counters and computes
    a weighted estimate of requests in the last time_window seconds.
    """
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        # user_id -> (window_start, current_count, previous_count)
        self.state = defaultdict(lambda: (0, 0, 0))

    def allow_request(self, user_id: str) -> bool:
        """
        Rate limiter per user and time
        type user_id: str
        rtype: bool
        """
        now = time.time()
        window_start, current_count, previous_count = self.state[user_id]

        # initialize firts window
        if window_start == 0:
            window_start = now - (now%self.time_window) # round down to the nearest time window. eg: if now is 10:01:00, and time_window is 60, then window_start is 10:00:00

        # move window if needed
        # if the elapsed time is greater than the time window, we need to move the window
        elapsed = now - window_start
        if elapsed >= self.time_window:
            steps = int(elapsed//self.time_window) # number of full windows elapsed
            if steps == 1:
                previous_count = current_count
            else:
                # reset previous count to 0
                previous_count = 0
            # reset current count to 0
            # because we are moving the window, we need to reset the current count to 0
            current_count = 0
            # update window start
            window_start = window_start + steps*self.time_window
            elapsed = now - window_start

        # weighted estimate of requests in the last time_window seconds
        # weight_prev is the weight of the previous count in the last time_window seconds
        # formula: estimated = current_count + weight_prev*previous_count
        weight_prev = (self.time_window - elapsed)/self.time_window
        estimated = current_count + weight_prev*previous_count
        if estimated>=self.max_requests:
            return False
        

        # update current count
        current_count += 1
        self.state[user_id] = (window_start, current_count, previous_count)
        return True


class FixedWindowLimiter(object):
    """
    Fixed window limiter per user.
    Keeps a counter of requests within the current discrete time bucket.
    """
    def __init__(self, max_requests: int, time_window: int) -> None:
        """
        type max_requests: int
        type time_window: int
        """
        self.max_requests = max_requests
        self.time_window = time_window
        # user_id -> (bucket_id, count)
        self.requests = defaultdict(lambda: (-1, 0)) # -1 means no bucket has been created yet

    def allow_request(self, user_id: str) -> bool:
        """
        Rate limiter per user and time
        type user_id: str
        rtype: bool
        """
        now = time.time()
        print(f"now: {now}")
        print(f"time_window: {self.time_window}")
        print(f"bucket_id: {int(now//self.time_window)}")
        bucket_id = int(now//self.time_window) # integer division to get the bucket id - this ensures that the bucket id is always an integer. For example, if now is 10:01:00, and time_window is 60, then bucket_id is 10 (10)
        saved_bucket, count = self.requests[user_id]
        # if the bucket is not the same as the saved bucket, we need to reset the count to 0
        if saved_bucket!=bucket_id:
            saved_bucket = bucket_id
            count = 0
        
        if count >= self.max_requests:
            self.requests[user_id] = (saved_bucket, count)
            return False

        count += 1
        self.requests[user_id] = (saved_bucket, count)
        return True



class TokenBucketLimiter(object):
    """
    Token bucket limiter per user.
    Keeps a token bucket of requests within the current time window.
    """
    def __init__(self, capacity: int, refill_rate_per_second: float) -> None:
        """
        type capacity: int
        type refill_rate_per_second: float
        """
        self.capacity = capacity # maximum number of tokens in the bucket (eg: 100 tokens)
        self.refill_rate_per_second = refill_rate_per_second # rate at which tokens are added to the bucket (eg: 10 tokens per second)
        # user_id -> (tokens, last_refill_ts)
        self.buckets = defaultdict(lambda: (float(capacity), time.time()))

    def allow_request(self, user_id: str, cost: float = 1.0) -> bool:
        """
        Returns True if enough tokens are available; otherwise False.
        """
        now = time.time()
        tokens, last_refill = self.buckets[user_id]

        elapsed = max(0.0, now - last_refill)
        tokens = min(self.capacity, tokens + elapsed*self.refill_rate_per_second)

        if tokens < cost:
            self.buckets[user_id] = (tokens, now)
            return False # not enough tokens

        tokens -= cost
        self.buckets[user_id] = (tokens, now)
        return True # enough tokens


limiter = RateLimiter(3, 60)

assert limiter.allow_request("user1") == True
assert limiter.allow_request("user1") == True
assert limiter.allow_request("user1") == True
assert limiter.allow_request("user1") == False
assert limiter.allow_request("user2") == True

import time
from typing import Dict, List, Tuple
from collections import defaultdict
from threading import Lock

from app.core.exceptions import RateLimitError
from app.core.config import settings

class RateLimiter:
    def __init__(self):
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()
        self._global_limit = settings.GLOBAL_RATE_LIMIT
        self._per_user_limit = settings.PER_USER_RATE_LIMIT
        self._window = 60

    def check_limit(self, user_id: int, key: str = None) -> bool:
        if key is None:
            key = str(user_id)

        with self._lock:
            now = time.time()
            user_requests = self._requests[key]
            user_requests = [t for t in user_requests if t > now - self._window]
            self._requests[key] = user_requests

            if len(user_requests) >= self._per_user_limit:
                raise RateLimitError("Per-user rate limit exceeded")

            global_requests = []
            for k, v in self._requests.items():
                global_requests.extend([t for t in v if t > now - self._window])

            if len(global_requests) >= self._global_limit:
                raise RateLimitError("Global rate limit exceeded")

            self._requests[key].append(now)
            return True

    def get_remaining(self, user_id: int, key: str = None) -> int:
        if key is None:
            key = str(user_id)

        with self._lock:
            now = time.time()
            user_requests = [t for t in self._requests[key] if t > now - self._window]
            return max(0, self._per_user_limit - len(user_requests))

    def reset(self, user_id: int, key: str = None):
        if key is None:
            key = str(user_id)

        with self._lock:
            if key in self._requests:
                self._requests[key] = []

    def get_window_reset_time(self, user_id: int, key: str = None) -> float:
        if key is None:
            key = str(user_id)

        with self._lock:
            user_requests = self._requests.get(key, [])
            if not user_requests:
                return time.time()
            oldest = min(user_requests)
            return oldest + self._window

rate_limiter = RateLimiter()
import asyncio
import time
from typing import Dict, Optional
from collections import deque

from app.core.config import settings
from app.analyzers.exceptions import RateLimiterError

class RateLimiter:
    def __init__(self):
        self._global_limit = settings.GLOBAL_RATE_LIMIT
        self._global_window = 60
        self._global_requests = deque()
        self._per_user_limits: Dict[int, deque] = {}
        self._per_user_window = 60

    async def acquire(self, user_id: Optional[int] = None):
        while True:
            if await self._can_make_request(user_id):
                await self._record_request(user_id)
                return
            await asyncio.sleep(1)

    async def _can_make_request(self, user_id: Optional[int] = None) -> bool:
        if not await self._check_global_limit():
            return False
        
        if user_id and not await self._check_user_limit(user_id):
            return False
        
        return True

    async def _check_global_limit(self) -> bool:
        now = time.time()
        while self._global_requests and self._global_requests[0] < now - self._global_window:
            self._global_requests.popleft()
        
        return len(self._global_requests) < self._global_limit

    async def _check_user_limit(self, user_id: int) -> bool:
        if user_id not in self._per_user_limits:
            return True
        
        user_requests = self._per_user_limits[user_id]
        now = time.time()
        
        while user_requests and user_requests[0] < now - self._per_user_window:
            user_requests.popleft()
        
        per_user_limit = settings.PER_USER_RATE_LIMIT
        return len(user_requests) < per_user_limit

    async def _record_request(self, user_id: Optional[int] = None):
        now = time.time()
        
        self._global_requests.append(now)
        
        if user_id:
            if user_id not in self._per_user_limits:
                self._per_user_limits[user_id] = deque()
            self._per_user_limits[user_id].append(now)

    def get_global_count(self) -> int:
        now = time.time()
        while self._global_requests and self._global_requests[0] < now - self._global_window:
            self._global_requests.popleft()
        return len(self._global_requests)

    def get_user_count(self, user_id: int) -> int:
        if user_id not in self._per_user_limits:
            return 0
        
        now = time.time()
        user_requests = self._per_user_limits[user_id]
        while user_requests and user_requests[0] < now - self._per_user_window:
            user_requests.popleft()
        
        return len(user_requests)

    def reset_user(self, user_id: int):
        if user_id in self._per_user_limits:
            del self._per_user_limits[user_id]

    def reset_all(self):
        self._global_requests.clear()
        self._per_user_limits.clear()
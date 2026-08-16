import asyncio
from typing import Callable, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.analyzers.exceptions import RetryManagerError

class RetryManager:
    def __init__(self):
        self.max_attempts = settings.MAX_RETRY_ATTEMPTS
        self.delay_seconds = settings.RETRY_DELAY_SECONDS
        self._attempts = {}
        self._last_attempt = {}

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        attempt = 0
        last_error = None
        
        while attempt < self.max_attempts:
            try:
                result = await func(*args, **kwargs)
                self._record_success(args[0] if args else None)
                return result
            except Exception as e:
                last_error = e
                attempt += 1
                
                if attempt >= self.max_attempts:
                    break
                
                if self._should_retry(e):
                    await self._wait(attempt)
                else:
                    raise
        
        raise RetryManagerError(f"Failed after {self.max_attempts} attempts: {last_error}")

    def _should_retry(self, error: Exception) -> bool:
        error_str = str(error).lower()
        
        retryable_errors = [
            "timeout",
            "connection",
            "rate",
            "429",
            "500",
            "502",
            "503",
            "504",
            "temporary"
        ]
        
        for err in retryable_errors:
            if err in error_str:
                return True
        return False

    async def _wait(self, attempt: int):
        delay = self.delay_seconds * (attempt + 1)
        await asyncio.sleep(delay)

    def _record_success(self, key: Any):
        if key:
            self._attempts[key] = self._attempts.get(key, 0) + 1
            self._last_attempt[key] = datetime.now()

    def get_attempt_count(self, key: Any) -> int:
        return self._attempts.get(key, 0)

    def get_last_attempt(self, key: Any) -> Optional[datetime]:
        return self._last_attempt.get(key)

    def reset(self, key: Any):
        if key in self._attempts:
            del self._attempts[key]
        if key in self._last_attempt:
            del self._last_attempt[key]
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4

from app.core.config import settings
from app.workers.exceptions import QueueError, QueueConnectionError, QueueFullError

class QueueManager:
    def __init__(self):
        self._redis = None
        self._connected = False
        self._queue_name = "whatsapp_scanner_jobs"
        self._max_size = 1000

    async def connect(self):
        try:
            import redis.asyncio as redis
            self._redis = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            await self._redis.ping()
            self._connected = True
        except ImportError:
            raise QueueError("Redis not installed. Install with: pip install redis")
        except Exception as e:
            raise QueueConnectionError(f"Failed to connect to Redis: {e}")

    async def disconnect(self):
        if self._redis and self._connected:
            await self._redis.close()
            self._connected = False

    async def push(self, job_data: Dict[str, Any]) -> str:
        if not self._connected:
            await self.connect()

        try:
            job_id = str(uuid4())
            job_data["job_id"] = job_id
            job_data["created_at"] = datetime.now().isoformat()
            job_data["status"] = "pending"

            await self._redis.lpush(
                self._queue_name,
                json.dumps(job_data)
            )
            return job_id
        except Exception as e:
            raise QueueError(f"Failed to push job: {e}")

    async def pop(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        if not self._connected:
            await self.connect()

        try:
            result = await self._redis.brpop(
                self._queue_name,
                timeout=timeout
            )
            if result:
                _, data = result
                return json.loads(data)
            return None
        except Exception as e:
            raise QueueError(f"Failed to pop job: {e}")

    async def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        if not self._connected:
            await self.connect()

        try:
            key = f"job:{job_id}"
            data = await self._redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None

    async def update_status(self, job_id: str, status: str, **data):
        if not self._connected:
            await self.connect()

        try:
            key = f"job:{job_id}"
            job_data = await self.get_status(job_id)
            if job_data:
                job_data["status"] = status
                job_data.update(data)
                job_data["updated_at"] = datetime.now().isoformat()
                await self._redis.set(key, json.dumps(job_data))
        except Exception:
            pass

    async def get_queue_length(self) -> int:
        if not self._connected:
            await self.connect()

        try:
            return await self._redis.llen(self._queue_name)
        except Exception:
            return 0

    async def clear(self):
        if not self._connected:
            await self.connect()

        try:
            await self._redis.delete(self._queue_name)
        except Exception:
            pass
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.workers import QueueManager

class TestQueueManager:
    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        queue = QueueManager()
        with patch('app.workers.queue.redis.from_url') as mock_redis:
            mock_redis.return_value = AsyncMock()
            await queue.connect()
            assert queue._connected is True
            await queue.disconnect()
            assert queue._connected is False

    @pytest.mark.asyncio
    async def test_push_pop(self):
        queue = QueueManager()
        mock_redis = AsyncMock()
        queue._redis = mock_redis
        queue._connected = True
        
        job_data = {"test": "data"}
        job_id = await queue.push(job_data)
        assert job_id is not None
        assert mock_redis.lpush.called

    @pytest.mark.asyncio
    async def test_get_queue_length(self):
        queue = QueueManager()
        mock_redis = AsyncMock()
        mock_redis.llen.return_value = 5
        queue._redis = mock_redis
        queue._connected = True
        
        length = await queue.get_queue_length()
        assert length == 5
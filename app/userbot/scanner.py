from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime, timedelta
import asyncio

from telethon import TelegramClient
from telethon.tl.types import Message, Channel, Chat, InputPeerChannel
from telethon.errors import FloodWaitError as TelethonFloodWaitError

from app.core.enums import AccessStatus, JobStatus
from app.userbot.exceptions import ScannerError, ScanRateLimitError, ScanTimeoutError, FloodWaitError

class MessageScanner:
    def __init__(self, client: TelegramClient, entity, limit: int = 100000):
        self.client = client
        self.entity = entity
        self.limit = limit
        self._processed = 0
        self._flood_wait_count = 0

    async def scan_messages(
        self,
        offset_date: Optional[datetime] = None,
        offset_id: int = 0,
        max_id: int = 0,
        min_id: int = 0
    ) -> AsyncGenerator[Message, None]:
        try:
            last_date = offset_date
            total_fetched = 0
            batch_size = 100

            while total_fetched < self.limit:
                try:
                    remaining = min(batch_size, self.limit - total_fetched)
                    
                    messages = await self.client.get_messages(
                        self.entity,
                        limit=remaining,
                        offset_date=last_date,
                        offset_id=offset_id,
                        max_id=max_id,
                        min_id=min_id,
                        reverse=False
                    )

                    if not messages:
                        break

                    for msg in messages:
                        if msg:
                            yield msg
                            self._processed += 1
                            total_fetched += 1

                    last_date = messages[-1].date if messages else None
                    offset_id = messages[-1].id if messages else 0

                    if len(messages) < batch_size:
                        break

                except TelethonFloodWaitError as e:
                    self._flood_wait_count += 1
                    if e.seconds > 300:
                        raise FloodWaitError(e.seconds)
                    await asyncio.sleep(e.seconds + 1)
                    continue

                except Exception as e:
                    raise ScannerError(f"Error scanning messages: {e}")

        except Exception as e:
            raise ScannerError(f"Scan failed: {e}")

    async def scan_messages_batch(
        self,
        batch_size: int = 100,
        offset_date: Optional[datetime] = None
    ) -> List[Message]:
        messages = []
        try:
            messages = await self.client.get_messages(
                self.entity,
                limit=batch_size,
                offset_date=offset_date,
                reverse=False
            )
            self._processed += len(messages)
            return messages
        except TelethonFloodWaitError as e:
            raise FloodWaitError(e.seconds)
        except Exception as e:
            raise ScannerError(f"Error fetching messages batch: {e}")

    async def count_messages(self) -> int:
        try:
            if hasattr(self.entity, 'id'):
                total = await self.client.get_messages(self.entity, limit=0, add_offset=0)
                return total.total if hasattr(total, 'total') else 0
            return 0
        except Exception:
            return 0

    def get_processed_count(self) -> int:
        return self._processed

    def get_flood_wait_count(self) -> int:
        return self._flood_wait_count

    async def close(self):
        pass
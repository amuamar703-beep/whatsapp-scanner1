from typing import Optional, Dict, Any
from datetime import datetime
import asyncio

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError as TelethonFloodWaitError,
    SessionExpiredError as TelethonSessionExpiredError,
    AuthKeyError,
    RPCError
)
from telethon.tl.functions.account import UpdateStatusRequest

from app.core.config import settings
from app.userbot.session_manager import SessionManager
from app.userbot.exceptions import (
    UserbotError,
    SessionError,
    SessionExpiredError,
    FloodWaitError
)

class UserbotManager:
    def __init__(self):
        self._session_manager = SessionManager()
        self._clients: Dict[int, TelegramClient] = {}
        self._account_sessions: Dict[int, Dict[str, Any]] = {}

    async def create_client(self, account_id: int, encrypted_session: str) -> TelegramClient:
        try:
            session_data = self._session_manager.get_session_data(encrypted_session)
            session_string = session_data.get("session_string")
            
            if not session_string:
                raise SessionError("No session string found in encrypted data")

            client = TelegramClient(
                StringSession(session_string),
                settings.API_ID,
                settings.API_HASH
            )
            
            self._clients[account_id] = client
            self._account_sessions[account_id] = session_data
            
            await client.connect()
            
            if not await client.is_user_authorized():
                raise SessionExpiredError("Session is not authorized")
            
            return client

        except TelethonSessionExpiredError:
            raise SessionExpiredError("Session expired")
        except AuthKeyError:
            raise SessionExpiredError("Auth key invalid or expired")
        except Exception as e:
            raise SessionError(f"Failed to create client: {e}")

    async def get_client(self, account_id: int, encrypted_session: str = None) -> TelegramClient:
        if account_id in self._clients:
            client = self._clients[account_id]
            try:
                if not client.is_connected():
                    await client.connect()
                if not await client.is_user_authorized():
                    if encrypted_session:
                        return await self.recreate_client(account_id, encrypted_session)
                    raise SessionExpiredError("Session not authorized")
                return client
            except TelethonSessionExpiredError:
                if encrypted_session:
                    return await self.recreate_client(account_id, encrypted_session)
                raise SessionExpiredError("Session expired")
            except Exception:
                if encrypted_session:
                    return await self.recreate_client(account_id, encrypted_session)
                raise

        if encrypted_session:
            return await self.create_client(account_id, encrypted_session)
        
        raise SessionError(f"No client found for account {account_id}")

    async def recreate_client(self, account_id: int, encrypted_session: str) -> TelegramClient:
        await self.disconnect_client(account_id)
        return await self.create_client(account_id, encrypted_session)

    async def disconnect_client(self, account_id: int):
        if account_id in self._clients:
            try:
                await self._clients[account_id].disconnect()
            except Exception:
                pass
            finally:
                del self._clients[account_id]
                if account_id in self._account_sessions:
                    del self._account_sessions[account_id]

    async def disconnect_all(self):
        for account_id in list(self._clients.keys()):
            await self.disconnect_client(account_id)

    async def update_status(self, account_id: int, encrypted_session: str, online: bool = True):
        client = await self.get_client(account_id, encrypted_session)
        try:
            await client(UpdateStatusRequest(offline=not online))
        except Exception as e:
            raise UserbotError(f"Failed to update status: {e}")

    async def handle_flood_wait(self, account_id: int, error: TelethonFloodWaitError) -> int:
        wait_seconds = error.seconds
        if wait_seconds > 300:
            await self.disconnect_client(account_id)
        raise FloodWaitError(wait_seconds)

    def is_client_connected(self, account_id: int) -> bool:
        if account_id not in self._clients:
            return False
        try:
            return self._clients[account_id].is_connected()
        except Exception:
            return False

    def get_phone(self, account_id: int) -> Optional[str]:
        if account_id in self._account_sessions:
            return self._account_sessions[account_id].get("phone")
        return None

    def get_user_id(self, account_id: int) -> Optional[int]:
        if account_id in self._account_sessions:
            return self._account_sessions[account_id].get("user_id")
        return None
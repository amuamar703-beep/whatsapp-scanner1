from typing import Dict, Any, List, Optional
from datetime import datetime

from app.database.database import get_db
from app.database.repositories import (
    TelegramAccountRepository,
    WhatsAppAccountRepository,
    UserRepository
)
from app.core.enums import TelegramAccountStatus
from app.userbot import SessionManager, UserbotManager

class AccountsService:
    def __init__(self):
        self.session_manager = SessionManager()
        self.userbot_manager = UserbotManager()

    async def add_telegram_account(
        self,
        user_id: int,
        phone: str,
        session_string: str,
        telegram_user_id: int
    ) -> Dict[str, Any]:
        async with get_db() as db:
            account_repo = TelegramAccountRepository(db)

            phone_masked = phone[:3] + "****" + phone[-2:] if len(phone) > 5 else phone

            encrypted_session = self.session_manager.pack_session(
                session_string,
                phone,
                telegram_user_id
            )

            existing = account_repo.get_by_telegram_user_id(telegram_user_id)
            if existing:
                return {
                    "success": False,
                    "error": "هذا الحساب موجود بالفعل"
                }

            account = account_repo.create(
                user_id=user_id,
                telegram_user_id=telegram_user_id,
                phone_masked=phone_masked,
                session_encrypted=encrypted_session,
                status=TelegramAccountStatus.ACTIVE,
                is_primary=not account_repo.get_by_user_id(user_id)
            )

            return {
                "success": True,
                "account_id": account.id,
                "phone_masked": phone_masked
            }

    async def get_telegram_accounts(self, user_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            account_repo = TelegramAccountRepository(db)

            accounts = account_repo.get_by_user_id(user_id)

            result = []
            for acc in accounts:
                result.append({
                    "id": acc.id,
                    "telegram_user_id": acc.telegram_user_id,
                    "phone_masked": acc.phone_masked,
                    "status": acc.status.value,
                    "is_primary": acc.is_primary,
                    "last_connected": acc.last_connected
                })

            return {
                "success": True,
                "total": len(result),
                "accounts": result
            }

    async def delete_telegram_account(self, user_id: int, account_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            account_repo = TelegramAccountRepository(db)

            account = account_repo.get(account_id)
            if not account:
                return {
                    "success": False,
                    "error": "الحساب غير موجود"
                }

            if account.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            await self.userbot_manager.disconnect_client(account_id)
            account_repo.delete(account_id)

            return {
                "success": True,
                "message": "تم حذف الحساب بنجاح"
            }

    async def set_primary_telegram_account(self, user_id: int, account_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            account_repo = TelegramAccountRepository(db)

            account = account_repo.get(account_id)
            if not account:
                return {
                    "success": False,
                    "error": "الحساب غير موجود"
                }

            if account.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            account_repo.set_primary(account_id, user_id)

            return {
                "success": True,
                "message": "تم تعيين الحساب كأساسي"
            }

    async def add_whatsapp_account(
        self,
        user_id: int,
        name: str,
        phone: Optional[str] = None,
        direct_url: Optional[str] = None
    ) -> Dict[str, Any]:
        async with get_db() as db:
            account_repo = WhatsAppAccountRepository(db)

            account = account_repo.create(
                user_id=user_id,
                name=name,
                phone=phone,
                direct_url=direct_url,
                enabled=True,
                is_primary=not account_repo.get_by_user_id(user_id)
            )

            return {
                "success": True,
                "account_id": account.id,
                "name": name
            }

    async def get_whatsapp_accounts(self, user_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            account_repo = WhatsAppAccountRepository(db)

            accounts = account_repo.get_by_user_id(user_id)

            result = []
            for acc in accounts:
                result.append({
                    "id": acc.id,
                    "name": acc.name,
                    "phone": acc.phone,
                    "direct_url": acc.direct_url,
                    "enabled": acc.enabled,
                    "is_primary": acc.is_primary
                })

            return {
                "success": True,
                "total": len(result),
                "accounts": result
            }

    async def delete_whatsapp_account(self, user_id: int, account_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            account_repo = WhatsAppAccountRepository(db)

            account = account_repo.get(account_id)
            if not account:
                return {
                    "success": False,
                    "error": "الحساب غير موجود"
                }

            if account.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            account_repo.delete(account_id)

            return {
                "success": True,
                "message": "تم حذف الحساب بنجاح"
            }

    async def toggle_whatsapp_account(self, user_id: int, account_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            account_repo = WhatsAppAccountRepository(db)

            account = account_repo.get(account_id)
            if not account:
                return {
                    "success": False,
                    "error": "الحساب غير موجود"
                }

            if account.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            account_repo.toggle_enabled(account_id)

            return {
                "success": True,
                "enabled": not account.enabled
            }

    async def get_whatsapp_accounts_for_send(self, user_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            account_repo = WhatsAppAccountRepository(db)

            accounts = account_repo.get_enabled_by_user_id(user_id)

            result = []
            for acc in accounts:
                result.append({
                    "id": acc.id,
                    "name": acc.name,
                    "phone": acc.phone,
                    "direct_url": acc.direct_url
                })

            return {
                "success": True,
                "total": len(result),
                "accounts": result
            }
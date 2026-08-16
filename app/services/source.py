from typing import Dict, Any, List, Optional

from app.database.database import get_db
from app.database.repositories import TelegramSourceRepository
from app.core.enums import AccessStatus

class SourceService:
    async def get_sources(self, user_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            source_repo = TelegramSourceRepository(db)

            sources = source_repo.get_by_user_id(user_id)

            result = []
            for src in sources:
                result.append({
                    "id": src.id,
                    "title": src.title,
                    "username": src.username,
                    "type": src.type.value if src.type else None,
                    "access_status": src.access_status.value if src.access_status else None,
                    "last_scanned": src.last_scanned
                })

            return {
                "success": True,
                "total": len(result),
                "sources": result
            }

    async def get_source(self, user_id: int, source_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            source_repo = TelegramSourceRepository(db)

            source = source_repo.get(source_id)
            if not source:
                return {
                    "success": False,
                    "error": "المصدر غير موجود"
                }

            if source.owner_user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            return {
                "success": True,
                "source": {
                    "id": source.id,
                    "title": source.title,
                    "username": source.username,
                    "type": source.type.value if source.type else None,
                    "access_status": source.access_status.value if source.access_status else None,
                    "can_read_messages": source.can_read_messages,
                    "last_scanned": source.last_scanned
                }
            }

    async def delete_source(self, user_id: int, source_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            source_repo = TelegramSourceRepository(db)

            source = source_repo.get(source_id)
            if not source:
                return {
                    "success": False,
                    "error": "المصدر غير موجود"
                }

            if source.owner_user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            source_repo.delete(source_id)

            return {
                "success": True,
                "message": "تم حذف المصدر بنجاح"
            }
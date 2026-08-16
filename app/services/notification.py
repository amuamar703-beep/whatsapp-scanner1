from typing import Dict, Any, Optional
from uuid import UUID

from app.database.database import get_db
from app.database.repositories import JobLogRepository
from app.core.enums import NotificationLevel

class NotificationService:
    async def send_notification(
        self,
        user_id: int,
        job_id: UUID,
        level: NotificationLevel,
        title: str,
        message: str
    ) -> Dict[str, Any]:
        async with get_db() as db:
            job_log_repo = JobLogRepository(db)

            job_log_repo.create_log(
                job_id,
                level,
                title,
                message
            )

            return {
                "success": True,
                "notification_id": job_id
            }

    async def get_notifications(self, user_id: int, limit: int = 50) -> Dict[str, Any]:
        async with get_db() as db:
            job_log_repo = JobLogRepository(db)

            logs = job_log_repo.list(limit=limit)

            result = []
            for log in logs:
                result.append({
                    "id": log.id,
                    "job_id": log.job_id,
                    "level": log.level.value,
                    "event": log.event,
                    "message": log.message,
                    "created_at": log.created_at
                })

            return {
                "success": True,
                "total": len(result),
                "notifications": result
            }

    async def mark_read(self, notification_id: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "تم تحديد الإشعار كمقروء"
        }
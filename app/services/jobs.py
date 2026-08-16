from typing import Dict, Any, List
from uuid import UUID

from app.database.database import get_db
from app.database.repositories import ScanJobRepository, JobLogRepository
from app.core.enums import JobStatus
from app.workers.queue import QueueManager

class JobsService:
    def __init__(self):
        self.queue_manager = QueueManager()

    async def get_user_jobs(self, user_id: int, limit: int = 50) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)

            jobs = scan_job_repo.list(user_id=user_id, limit=limit)

            result = []
            for job in jobs:
                result.append({
                    "id": job.id,
                    "type": job.type.value,
                    "status": job.status.value,
                    "progress": job.progress_percent,
                    "started_at": job.started_at,
                    "finished_at": job.finished_at
                })

            return {
                "success": True,
                "total": len(result),
                "jobs": result
            }

    async def get_job_details(self, user_id: int, job_id: UUID) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)
            job_log_repo = JobLogRepository(db)

            job = scan_job_repo.get(job_id)
            if not job:
                return {
                    "success": False,
                    "error": "المهمة غير موجودة"
                }

            if job.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            logs = job_log_repo.get_by_job_id(job_id)

            return {
                "success": True,
                "job": {
                    "id": job.id,
                    "type": job.type.value,
                    "status": job.status.value,
                    "progress": job.progress_percent,
                    "total_messages": job.total_messages,
                    "processed_messages": job.processed_messages,
                    "total_urls": job.total_urls,
                    "whatsapp_urls": job.whatsapp_urls,
                    "unique_urls": job.unique_urls,
                    "started_at": job.started_at,
                    "finished_at": job.finished_at,
                    "error_code": job.error_code,
                    "error_message": job.error_message
                },
                "logs": [
                    {
                        "level": log.level.value,
                        "event": log.event,
                        "message": log.message,
                        "created_at": log.created_at
                    }
                    for log in logs
                ]
            }

    async def cancel_job(self, user_id: int, job_id: UUID) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)
            job_log_repo = JobLogRepository(db)

            job = scan_job_repo.get(job_id)
            if not job:
                return {
                    "success": False,
                    "error": "المهمة غير موجودة"
                }

            if job.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                return {
                    "success": False,
                    "error": f"لا يمكن إلغاء مهمة بحالة {job.status.value}"
                }

            scan_job_repo.mark_cancelled(job_id)

            job_log_repo.create_log(
                job_id,
                "warning",
                "job_cancelled",
                "Job cancelled by user"
            )

            return {
                "success": True,
                "message": "تم إلغاء المهمة بنجاح"
            }

    async def pause_job(self, user_id: int, job_id: UUID) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)

            job = scan_job_repo.get(job_id)
            if not job:
                return {
                    "success": False,
                    "error": "المهمة غير موجودة"
                }

            if job.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            if job.status != JobStatus.RUNNING:
                return {
                    "success": False,
                    "error": f"لا يمكن إيقاف مهمة بحالة {job.status.value}"
                }

            scan_job_repo.update(job_id, status=JobStatus.PAUSED)

            return {
                "success": True,
                "message": "تم إيقاف المهمة مؤقتاً"
            }

    async def resume_job(self, user_id: int, job_id: UUID) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)

            job = scan_job_repo.get(job_id)
            if not job:
                return {
                    "success": False,
                    "error": "المهمة غير موجودة"
                }

            if job.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            if job.status != JobStatus.PAUSED:
                return {
                    "success": False,
                    "error": f"لا يمكن استئناف مهمة بحالة {job.status.value}"
                }

            scan_job_repo.update(job_id, status=JobStatus.RUNNING)

            return {
                "success": True,
                "message": "تم استئناف المهمة"
            }

    async def get_queue_length(self) -> Dict[str, Any]:
        length = await self.queue_manager.get_queue_length()
        return {
            "success": True,
            "queue_length": length
        }
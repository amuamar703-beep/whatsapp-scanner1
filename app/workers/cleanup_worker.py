import os
import shutil
from datetime import datetime, timedelta
from typing import Optional

from app.workers.base_worker import BaseWorker
from app.workers.queue import QueueManager
from app.workers.exceptions import CleanupWorkerError

from app.database.database import get_db
from app.database.repositories import (
    ExportRepository,
    JobLogRepository,
    ScanJobRepository
)
from app.core.constants import TEMPORARY_EXPORT_EXPIRY_HOURS, LOG_RETENTION_DAYS

class CleanupWorker(BaseWorker):
    def __init__(self, queue_manager: QueueManager):
        super().__init__(queue_manager)
        self.storage_path = "storage/exports"

    async def process_job(self):
        job_data = await self.queue_manager.pop(timeout=5)
        if not job_data:
            return

        try:
            await self.cleanup_exports()
            await self.cleanup_jobs()
            await self.cleanup_logs()
            await self.cleanup_files()

        except Exception as e:
            raise CleanupWorkerError(f"Cleanup failed: {e}")

    async def cleanup_exports(self):
        async with get_db() as db:
            export_repo = ExportRepository(db)
            
            expired = export_repo.cleanup_expired()
            
            if expired > 0:
                for export in expired:
                    try:
                        if os.path.exists(export.file_path):
                            os.remove(export.file_path)
                    except Exception:
                        pass

    async def cleanup_jobs(self):
        async with get_db() as db:
            job_repo = ScanJobRepository(db)
            
            threshold = datetime.now() - timedelta(days=30)
            old_jobs = job_repo.list(created_at=threshold)
            
            for job in old_jobs:
                if job.status in ["completed", "failed", "cancelled"]:
                    job_repo.update(job.id, status="archived")

    async def cleanup_logs(self):
        async with get_db() as db:
            log_repo = JobLogRepository(db)
            
            threshold = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
            old_logs = log_repo.list(created_at=threshold)
            
            for log in old_logs:
                log_repo.delete(log.id)

    async def cleanup_files(self):
        try:
            if not os.path.exists(self.storage_path):
                return

            for file_name in os.listdir(self.storage_path):
                file_path = os.path.join(self.storage_path, file_name)
                if os.path.isfile(file_path):
                    file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_age > timedelta(hours=TEMPORARY_EXPORT_EXPIRY_HOURS):
                        os.remove(file_path)

        except Exception as e:
            raise CleanupWorkerError(f"File cleanup failed: {e}")

    async def handle_error(self, error: Exception):
        pass
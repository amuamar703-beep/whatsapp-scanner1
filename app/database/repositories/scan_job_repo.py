from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository
from app.database.models.scan_job import ScanJob
from app.core.enums import JobStatus, JobType

class ScanJobRepository(BaseRepository[ScanJob]):
    def __init__(self, db: Session):
        super().__init__(ScanJob, db)

    def get_by_user_id(self, user_id: int) -> List[ScanJob]:
        return self.list(user_id=user_id)

    def get_active_by_user_id(self, user_id: int) -> List[ScanJob]:
        return self.list(
            user_id=user_id,
            status=JobStatus.RUNNING
        )

    def get_pending_by_user_id(self, user_id: int) -> List[ScanJob]:
        return self.list(
            user_id=user_id,
            status=JobStatus.PENDING
        )

    def get_running_jobs(self) -> List[ScanJob]:
        return self.list(status=JobStatus.RUNNING)

    def update_progress(self, job_id: UUID, processed_messages: int, total_urls: int = None, whatsapp_urls: int = None) -> Optional[ScanJob]:
        updates = {"processed_messages": processed_messages}
        if total_urls is not None:
            updates["total_urls"] = total_urls
        if whatsapp_urls is not None:
            updates["whatsapp_urls"] = whatsapp_urls
        return self.update(job_id, **updates)

    def mark_completed(self, job_id: UUID, **results) -> Optional[ScanJob]:
        from datetime import datetime
        updates = {"status": JobStatus.COMPLETED, "finished_at": datetime.now()}
        updates.update(results)
        return self.update(job_id, **updates)

    def mark_failed(self, job_id: UUID, error_code: str, error_message: str) -> Optional[ScanJob]:
        from datetime import datetime
        return self.update(
            job_id,
            status=JobStatus.FAILED,
            finished_at=datetime.now(),
            error_code=error_code,
            error_message=error_message
        )

    def mark_cancelled(self, job_id: UUID) -> Optional[ScanJob]:
        from datetime import datetime
        return self.update(
            job_id,
            status=JobStatus.CANCELLED,
            finished_at=datetime.now()
        )
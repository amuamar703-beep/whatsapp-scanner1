from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository
from app.database.models.job_log import JobLog
from app.core.enums import NotificationLevel

class JobLogRepository(BaseRepository[JobLog]):
    def __init__(self, db: Session):
        super().__init__(JobLog, db)

    def get_by_job_id(self, job_id: UUID) -> List[JobLog]:
        return self.list(job_id=job_id)

    def get_by_job_and_level(self, job_id: UUID, level: NotificationLevel) -> List[JobLog]:
        return self.list(job_id=job_id, level=level)

    def create_log(self, job_id: UUID, level: NotificationLevel, event: str, message: str = None) -> JobLog:
        return self.create(
            job_id=job_id,
            level=level,
            event=event,
            message=message
        )
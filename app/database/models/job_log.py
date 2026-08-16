from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base
from app.core.enums import NotificationLevel

class JobLog(Base):
    __tablename__ = "job_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("scan_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    level = Column(Enum(NotificationLevel), nullable=False)
    event = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    job = relationship("ScanJob", back_populates="job_logs")

    def __repr__(self):
        return f"<JobLog(id={self.id}, job_id={self.job_id}, event={self.event})>"
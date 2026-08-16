from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Enum, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.database import Base
from app.core.enums import JobType, JobStatus

class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(BigInteger, ForeignKey("telegram_sources.id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    total_messages = Column(BigInteger, default=0)
    processed_messages = Column(BigInteger, default=0)
    total_urls = Column(BigInteger, default=0)
    whatsapp_urls = Column(BigInteger, default=0)
    unique_urls = Column(BigInteger, default=0)
    progress_percent = Column(Integer, default=0)
    scope = Column(String(50), default="all_messages")
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="scan_jobs")
    source = relationship("TelegramSource", back_populates="scan_jobs")
    job_logs = relationship("JobLog", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScanJob(id={self.id}, type={self.type}, status={self.status})>"
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.core.enums import SourceType, AccessStatus

class TelegramSource(Base):
    __tablename__ = "telegram_sources"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    telegram_chat_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(255), nullable=True, index=True)
    title = Column(String(255), nullable=True)
    type = Column(Enum(SourceType), nullable=True)
    access_status = Column(Enum(AccessStatus), default=AccessStatus.UNKNOWN)
    can_read_messages = Column(Boolean, default=False)
    invite_hash = Column(String(255), nullable=True)
    last_scanned = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner_user = relationship("User", back_populates="telegram_sources")
    scan_jobs = relationship("ScanJob", back_populates="source", cascade="all, delete-orphan")
    link_sources = relationship("LinkSource", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TelegramSource(id={self.id}, title={self.title}, username={self.username})>"
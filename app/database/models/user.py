from sqlalchemy import Column, BigInteger, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.core.enums import UserStatus

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language = Column(String(10), default="ar")
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    telegram_accounts = relationship("TelegramAccount", back_populates="user", cascade="all, delete-orphan")
    telegram_sources = relationship("TelegramSource", back_populates="owner_user", cascade="all, delete-orphan")
    scan_jobs = relationship("ScanJob", back_populates="user", cascade="all, delete-orphan")
    wallet_links = relationship("WalletLink", back_populates="user", cascade="all, delete-orphan")
    whatsapp_accounts = relationship("WhatsAppAccount", back_populates="user", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
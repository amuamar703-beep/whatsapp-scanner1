from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.core.enums import TelegramAccountStatus

class TelegramAccount(Base):
    __tablename__ = "telegram_accounts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    telegram_user_id = Column(BigInteger, nullable=False, index=True)
    phone_masked = Column(String(20), nullable=True)
    session_encrypted = Column(Text, nullable=False)
    status = Column(Enum(TelegramAccountStatus), default=TelegramAccountStatus.ACTIVE)
    is_primary = Column(Boolean, default=False)
    last_connected = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="telegram_accounts")

    __table_args__ = (
        {"indexes": []}
    )

    def __repr__(self):
        return f"<TelegramAccount(id={self.id}, user_id={self.user_id}, telegram_user_id={self.telegram_user_id})>"
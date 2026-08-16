from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base

class WhatsAppAccount(Base):
    __tablename__ = "whatsapp_accounts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    direct_url = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="whatsapp_accounts")

    def __repr__(self):
        return f"<WhatsAppAccount(id={self.id}, user_id={self.user_id}, name={self.name})>"
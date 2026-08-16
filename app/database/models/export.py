from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.database import Base
from app.core.enums import ExportFormat, WalletCategory

class Export(Base):
    __tablename__ = "exports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    format = Column(Enum(ExportFormat), nullable=False)
    category = Column(Enum(WalletCategory), nullable=True)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger, default=0)
    total_links = Column(BigInteger, default=0)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="exports")

    def __repr__(self):
        return f"<Export(id={self.id}, user_id={self.user_id}, format={self.format})>"
from sqlalchemy import Column, BigInteger, String, DateTime, Enum, Integer, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.core.enums import LinkStatus, ConfidenceLevel

class WhatsAppLink(Base):
    __tablename__ = "whatsapp_links"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    normalized_url = Column(Text, unique=True, nullable=False, index=True)
    display_url = Column(Text, nullable=True)
    status = Column(Enum(LinkStatus), default=LinkStatus.DISCOVERED)
    confidence = Column(Enum(ConfidenceLevel), default=ConfidenceLevel.LOW)
    first_seen = Column(DateTime, server_default=func.now())
    last_checked = Column(DateTime, nullable=True)
    check_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    link_sources = relationship("LinkSource", back_populates="link", cascade="all, delete-orphan")
    analysis_runs = relationship("LinkAnalysisRun", back_populates="link", cascade="all, delete-orphan")
    wallet_links = relationship("WalletLink", back_populates="link", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WhatsAppLink(id={self.id}, normalized_url={self.normalized_url[:50]}, status={self.status})>"
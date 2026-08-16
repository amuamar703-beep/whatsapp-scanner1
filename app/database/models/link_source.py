from sqlalchemy import Column, BigInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base

class LinkSource(Base):
    __tablename__ = "link_sources"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    link_id = Column(BigInteger, ForeignKey("whatsapp_links.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(BigInteger, ForeignKey("telegram_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(BigInteger, nullable=True)
    first_seen = Column(DateTime, server_default=func.now())
    last_seen = Column(DateTime, server_default=func.now(), onupdate=func.now())

    link = relationship("WhatsAppLink", back_populates="link_sources")
    source = relationship("TelegramSource", back_populates="link_sources")

    __table_args__ = (
        {"indexes": []}
    )

    def __repr__(self):
        return f"<LinkSource(id={self.id}, link_id={self.link_id}, source_id={self.source_id})>"
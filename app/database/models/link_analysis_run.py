from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.core.enums import LinkStatus, ConfidenceLevel

class LinkAnalysisRun(Base):
    __tablename__ = "link_analysis_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    link_id = Column(BigInteger, ForeignKey("whatsapp_links.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(LinkStatus), nullable=False)
    confidence = Column(Enum(ConfidenceLevel), nullable=True)
    response_data = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    checked_at = Column(DateTime, server_default=func.now())

    link = relationship("WhatsAppLink", back_populates="analysis_runs")

    def __repr__(self):
        return f"<LinkAnalysisRun(id={self.id}, link_id={self.link_id}, status={self.status})>"
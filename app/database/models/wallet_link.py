from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.core.enums import WalletCategory

class WalletLink(Base):
    __tablename__ = "wallet_links"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    link_id = Column(BigInteger, ForeignKey("whatsapp_links.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(Enum(WalletCategory), nullable=False)
    saved_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="wallet_links")
    link = relationship("WhatsAppLink", back_populates="wallet_links")

    __table_args__ = (
        UniqueConstraint('user_id', 'link_id', name='uq_wallet_user_link'),
    )

    def __repr__(self):
        return f"<WalletLink(id={self.id}, user_id={self.user_id}, link_id={self.link_id}, category={self.category})>"
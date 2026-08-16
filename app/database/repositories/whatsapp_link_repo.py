from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.repositories.base import BaseRepository
from app.database.models.whatsapp_link import WhatsAppLink
from app.core.enums import LinkStatus

class WhatsAppLinkRepository(BaseRepository[WhatsAppLink]):
    def __init__(self, db: Session):
        super().__init__(WhatsAppLink, db)

    def get_by_normalized_url(self, normalized_url: str) -> Optional[WhatsAppLink]:
        return self.get_by(normalized_url=normalized_url)

    def get_or_create(self, normalized_url: str, **defaults) -> tuple[WhatsAppLink, bool]:
        link = self.get_by_normalized_url(normalized_url)
        if link:
            return link, False
        
        link_data = {"normalized_url": normalized_url}
        link_data.update(defaults)
        link = self.create(**link_data)
        return link, True

    def get_by_status(self, status: LinkStatus) -> List[WhatsAppLink]:
        return self.list(status=status)

    def get_pending_analysis(self, limit: int = 100) -> List[WhatsAppLink]:
        stmt = select(WhatsAppLink).where(
            WhatsAppLink.status == LinkStatus.DISCOVERED
        ).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def update_status(self, link_id: int, status: LinkStatus, confidence: str = None) -> Optional[WhatsAppLink]:
        updates = {"status": status}
        if confidence:
            updates["confidence"] = confidence
        return self.update(link_id, **updates)

    def increment_check_count(self, link_id: int) -> Optional[WhatsAppLink]:
        link = self.get(link_id)
        if link:
            link.check_count += 1
            self.db.flush()
        return link

    def get_links_by_source_id(self, source_id: int) -> List[WhatsAppLink]:
        stmt = select(WhatsAppLink).join(
            WhatsAppLink.link_sources
        ).where(
            WhatsAppLink.link_sources.any(source_id=source_id)
        )
        return self.db.execute(stmt).scalars().all()
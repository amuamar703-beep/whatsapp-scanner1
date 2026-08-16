from typing import Optional, List
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository
from app.database.models.link_source import LinkSource

class LinkSourceRepository(BaseRepository[LinkSource]):
    def __init__(self, db: Session):
        super().__init__(LinkSource, db)

    def get_by_link_id(self, link_id: int) -> List[LinkSource]:
        return self.list(link_id=link_id)

    def get_by_source_id(self, source_id: int) -> List[LinkSource]:
        return self.list(source_id=source_id)

    def get_by_link_and_source(self, link_id: int, source_id: int) -> Optional[LinkSource]:
        return self.get_by(link_id=link_id, source_id=source_id)

    def get_or_create(self, link_id: int, source_id: int, **defaults) -> tuple[LinkSource, bool]:
        link_source = self.get_by_link_and_source(link_id, source_id)
        if link_source:
            return link_source, False
        
        link_source_data = {"link_id": link_id, "source_id": source_id}
        link_source_data.update(defaults)
        link_source = self.create(**link_source_data)
        return link_source, True

    def update_last_seen(self, link_source_id: int) -> Optional[LinkSource]:
        from datetime import datetime
        return self.update(link_source_id, last_seen=datetime.now())
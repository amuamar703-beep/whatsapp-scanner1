from typing import Optional, List
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository
from app.database.models.telegram_source import TelegramSource
from app.core.enums import AccessStatus

class TelegramSourceRepository(BaseRepository[TelegramSource]):
    def __init__(self, db: Session):
        super().__init__(TelegramSource, db)

    def get_by_user_id(self, user_id: int) -> List[TelegramSource]:
        return self.list(owner_user_id=user_id)

    def get_by_chat_id(self, chat_id: int) -> Optional[TelegramSource]:
        return self.get_by(telegram_chat_id=chat_id)

    def get_by_username(self, username: str) -> Optional[TelegramSource]:
        return self.get_by(username=username)

    def get_by_user_and_chat_id(self, user_id: int, chat_id: int) -> Optional[TelegramSource]:
        return self.get_by(owner_user_id=user_id, telegram_chat_id=chat_id)

    def get_or_create(self, user_id: int, chat_id: int, **defaults) -> tuple[TelegramSource, bool]:
        source = self.get_by_user_and_chat_id(user_id, chat_id)
        if source:
            return source, False
        
        source_data = {"owner_user_id": user_id, "telegram_chat_id": chat_id}
        source_data.update(defaults)
        source = self.create(**source_data)
        return source, True

    def update_access_status(self, source_id: int, status: AccessStatus) -> Optional[TelegramSource]:
        return self.update(source_id, access_status=status)

    def update_last_scanned(self, source_id: int) -> Optional[TelegramSource]:
        from datetime import datetime
        return self.update(source_id, last_scanned=datetime.now())
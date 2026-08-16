from typing import Optional
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository
from app.database.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return self.get_by(telegram_id=telegram_id)

    def get_or_create(self, telegram_id: int, **defaults) -> tuple[User, bool]:
        user = self.get_by_telegram_id(telegram_id)
        if user:
            return user, False
        
        user_data = {"telegram_id": telegram_id}
        user_data.update(defaults)
        user = self.create(**user_data)
        return user, True

    def update_last_seen(self, user_id: int) -> Optional[User]:
        from datetime import datetime
        return self.update(user_id, updated_at=datetime.now())
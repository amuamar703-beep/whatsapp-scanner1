from typing import Optional, List
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository
from app.database.models.telegram_account import TelegramAccount
from app.core.enums import TelegramAccountStatus

class TelegramAccountRepository(BaseRepository[TelegramAccount]):
    def __init__(self, db: Session):
        super().__init__(TelegramAccount, db)

    def get_by_user_id(self, user_id: int) -> List[TelegramAccount]:
        return self.list(user_id=user_id)

    def get_primary_by_user_id(self, user_id: int) -> Optional[TelegramAccount]:
        return self.get_by(user_id=user_id, is_primary=True)

    def get_active_by_user_id(self, user_id: int) -> List[TelegramAccount]:
        return self.list(user_id=user_id, status=TelegramAccountStatus.ACTIVE)

    def get_by_telegram_user_id(self, telegram_user_id: int) -> Optional[TelegramAccount]:
        return self.get_by(telegram_user_id=telegram_user_id)

    def set_primary(self, account_id: int, user_id: int) -> Optional[TelegramAccount]:
        self.db.query(TelegramAccount).filter(
            TelegramAccount.user_id == user_id,
            TelegramAccount.is_primary == True
        ).update({"is_primary": False})
        self.db.flush()
        return self.update(account_id, is_primary=True)

    def update_status(self, account_id: int, status: TelegramAccountStatus) -> Optional[TelegramAccount]:
        return self.update(account_id, status=status)
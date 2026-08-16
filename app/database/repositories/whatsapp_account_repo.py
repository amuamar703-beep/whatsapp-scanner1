from typing import Optional, List
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository
from app.database.models.whatsapp_account import WhatsAppAccount

class WhatsAppAccountRepository(BaseRepository[WhatsAppAccount]):
    def __init__(self, db: Session):
        super().__init__(WhatsAppAccount, db)

    def get_by_user_id(self, user_id: int) -> List[WhatsAppAccount]:
        return self.list(user_id=user_id)

    def get_primary_by_user_id(self, user_id: int) -> Optional[WhatsAppAccount]:
        return self.get_by(user_id=user_id, is_primary=True)

    def get_enabled_by_user_id(self, user_id: int) -> List[WhatsAppAccount]:
        return self.list(user_id=user_id, enabled=True)

    def set_primary(self, account_id: int, user_id: int) -> Optional[WhatsAppAccount]:
        self.db.query(WhatsAppAccount).filter(
            WhatsAppAccount.user_id == user_id,
            WhatsAppAccount.is_primary == True
        ).update({"is_primary": False})
        self.db.flush()
        return self.update(account_id, is_primary=True)

    def toggle_enabled(self, account_id: int) -> Optional[WhatsAppAccount]:
        account = self.get(account_id)
        if account:
            return self.update(account_id, enabled=not account.enabled)
        return None
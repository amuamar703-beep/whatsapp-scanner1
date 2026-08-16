from typing import Optional, List
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository
from app.database.models.wallet_link import WalletLink
from app.core.enums import WalletCategory

class WalletLinkRepository(BaseRepository[WalletLink]):
    def __init__(self, db: Session):
        super().__init__(WalletLink, db)

    def get_by_user_id(self, user_id: int) -> List[WalletLink]:
        return self.list(user_id=user_id)

    def get_by_user_and_category(self, user_id: int, category: WalletCategory) -> List[WalletLink]:
        return self.list(user_id=user_id, category=category)

    def get_by_user_and_link(self, user_id: int, link_id: int) -> Optional[WalletLink]:
        return self.get_by(user_id=user_id, link_id=link_id)

    def get_or_create(self, user_id: int, link_id: int, category: WalletCategory) -> tuple[WalletLink, bool]:
        wallet_link = self.get_by_user_and_link(user_id, link_id)
        if wallet_link:
            return wallet_link, False
        
        wallet_link = self.create(
            user_id=user_id,
            link_id=link_id,
            category=category
        )
        return wallet_link, True

    def delete_by_user_and_link(self, user_id: int, link_id: int) -> bool:
        wallet_link = self.get_by_user_and_link(user_id, link_id)
        if wallet_link:
            self.delete(wallet_link.id)
            return True
        return False

    def count_by_user(self, user_id: int) -> int:
        return self.count(user_id=user_id)

    def count_by_user_and_category(self, user_id: int, category: WalletCategory) -> int:
        return self.count(user_id=user_id, category=category)
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository
from app.database.models.export import Export
from app.core.enums import ExportFormat, WalletCategory

class ExportRepository(BaseRepository[Export]):
    def __init__(self, db: Session):
        super().__init__(Export, db)

    def get_by_user_id(self, user_id: int) -> List[Export]:
        return self.list(user_id=user_id)

    def get_by_user_and_format(self, user_id: int, format: ExportFormat) -> List[Export]:
        return self.list(user_id=user_id, format=format)

    def get_active_exports(self, user_id: int) -> List[Export]:
        now = datetime.now()
        return self.db.query(Export).filter(
            Export.user_id == user_id,
            Export.expires_at > now
        ).all()

    def create_export(self, user_id: int, format: ExportFormat, file_path: str, **data) -> Export:
        export_data = {
            "user_id": user_id,
            "format": format,
            "file_path": file_path
        }
        export_data.update(data)
        return self.create(**export_data)

    def cleanup_expired(self) -> int:
        now = datetime.now()
        expired = self.db.query(Export).filter(Export.expires_at < now).all()
        count = len(expired)
        for exp in expired:
            self.db.delete(exp)
        self.db.flush()
        return count
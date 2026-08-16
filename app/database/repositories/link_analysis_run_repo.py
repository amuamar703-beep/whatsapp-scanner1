from typing import List
from sqlalchemy.orm import Session

from app.database.repositories.base import BaseRepository
from app.database.models.link_analysis_run import LinkAnalysisRun
from app.core.enums import LinkStatus

class LinkAnalysisRunRepository(BaseRepository[LinkAnalysisRun]):
    def __init__(self, db: Session):
        super().__init__(LinkAnalysisRun, db)

    def get_by_link_id(self, link_id: int) -> List[LinkAnalysisRun]:
        return self.list(link_id=link_id)

    def get_latest_by_link_id(self, link_id: int) -> LinkAnalysisRun:
        return self.db.query(LinkAnalysisRun).filter(
            LinkAnalysisRun.link_id == link_id
        ).order_by(
            LinkAnalysisRun.checked_at.desc()
        ).first()

    def create_run(self, link_id: int, status: LinkStatus, **data) -> LinkAnalysisRun:
        run_data = {"link_id": link_id, "status": status}
        run_data.update(data)
        return self.create(**run_data)
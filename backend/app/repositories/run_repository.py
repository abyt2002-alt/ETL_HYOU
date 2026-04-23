from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models import IngestionRun, IngestionRunItem


class RunRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_run(self) -> Optional[IngestionRun]:
        return self.db.query(IngestionRun).order_by(desc(IngestionRun.id)).first()

    def get_run_history(self, limit: int = 50) -> List[IngestionRun]:
        return self.db.query(IngestionRun).order_by(desc(IngestionRun.id)).limit(limit).all()

    def get_run_by_id(self, run_id: int) -> Optional[IngestionRun]:
        return self.db.query(IngestionRun).filter(IngestionRun.id == run_id).first()

    def get_run_items(self, run_id: int) -> List[IngestionRunItem]:
        return self.db.query(IngestionRunItem).filter(IngestionRunItem.run_id == run_id).all()

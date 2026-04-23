from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models import IngestionRun, IngestionRunItem
from app.source_config import SourceConfig, get_all_sources, get_source_config
from app.services.excel_service import ExcelService
from app.services.transform_service import TransformService
from app.repositories.data_repository import DataRepository


class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.sheet_service = ExcelService(excel_path="/app/sample_data.xlsx")
        self.transform_service = TransformService()
        self.data_repository = DataRepository(db)

    def run_all_sources(self, triggered_by: str = "system") -> IngestionRun:
        run = IngestionRun(
            trigger_type="all_sources",
            status="running",
            triggered_by=triggered_by
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        sources = get_all_sources()
        success_count = 0
        failed_count = 0

        for source in sources:
            try:
                self._ingest_source(run.id, source)
                success_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Error ingesting {source.source_name}: {str(e)}")

        run.status = "completed" if failed_count == 0 else "partial"
        run.completed_at = datetime.utcnow()
        run.summary_message = f"Completed: {success_count} succeeded, {failed_count} failed"
        self.db.commit()
        
        return run

    def run_single_source(self, source_name: str, triggered_by: str = "system") -> IngestionRun:
        run = IngestionRun(
            trigger_type="single_source",
            status="running",
            triggered_by=triggered_by
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        try:
            config = get_source_config(source_name)
            self._ingest_source(run.id, config)
            run.status = "completed"
            run.summary_message = f"Successfully ingested {source_name}"
        except Exception as e:
            run.status = "failed"
            run.summary_message = f"Failed to ingest {source_name}: {str(e)}"

        run.completed_at = datetime.utcnow()
        self.db.commit()
        
        return run

    def _ingest_source(self, run_id: int, config: SourceConfig):
        item = IngestionRunItem(
            run_id=run_id,
            source_name=config.source_name,
            sheet_tab_name=config.sheet_tab_name,
            target_table_name=config.target_table_name,
            status="running"
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        try:
            raw_data = self.sheet_service.read_tab(config.sheet_tab_name)
            item.rows_read = len(raw_data)

            valid, message = self.transform_service.validate_columns(raw_data, config)
            if not valid:
                raise ValueError(message)

            df = self.transform_service.transform_data(raw_data, config)
            
            rows_loaded = self.data_repository.bulk_insert(
                config.target_table_name, 
                df, 
                load_mode=config.load_mode
            )
            
            item.rows_loaded = rows_loaded
            item.status = "completed"
            item.completed_at = datetime.utcnow()
        except Exception as e:
            item.status = "failed"
            item.error_message = str(e)
            item.completed_at = datetime.utcnow()
            raise
        finally:
            self.db.commit()

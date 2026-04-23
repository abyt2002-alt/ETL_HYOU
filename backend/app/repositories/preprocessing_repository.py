"""
Repository for preprocessing run tracking operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import PreprocessingRun, PreprocessingRunItem, DataQualityIssue, MappingFile
from datetime import datetime
from typing import List, Optional


class PreprocessingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_run(self, triggered_by: str = "system") -> PreprocessingRun:
        """Create a new preprocessing run."""
        run = PreprocessingRun(
            status="running",
            triggered_by=triggered_by,
            started_at=datetime.utcnow()
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def create_run_item(
        self,
        run_id: int,
        source_name: str,
        input_table: str,
        output_table: str,
        mapping_file_id: Optional[int] = None
    ) -> PreprocessingRunItem:
        """Create a new preprocessing run item."""
        item = PreprocessingRunItem(
            run_id=run_id,
            source_name=source_name,
            input_table=input_table,
            output_table=output_table,
            status="running",
            mapping_file_id=mapping_file_id,
            started_at=datetime.utcnow()
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_run_item(
        self,
        item_id: int,
        status: str,
        rows_read: int = 0,
        rows_output: int = 0,
        exact_duplicates_found: int = 0,
        business_duplicates_found: int = 0,
        mapping_matches: int = 0,
        mapping_unmatched: int = 0,
        unlabeled_count: int = 0,
        issues_found: int = 0,
        error_message: Optional[str] = None
    ):
        """Update preprocessing run item with results."""
        item = self.db.query(PreprocessingRunItem).filter(PreprocessingRunItem.id == item_id).first()
        if item:
            item.status = status
            # Convert numpy types to Python native types
            item.rows_read = int(rows_read) if rows_read is not None else 0
            item.rows_output = int(rows_output) if rows_output is not None else 0
            item.exact_duplicates_found = int(exact_duplicates_found) if exact_duplicates_found is not None else 0
            item.business_duplicates_found = int(business_duplicates_found) if business_duplicates_found is not None else 0
            item.mapping_matches = int(mapping_matches) if mapping_matches is not None else 0
            item.mapping_unmatched = int(mapping_unmatched) if mapping_unmatched is not None else 0
            item.unlabeled_count = int(unlabeled_count) if unlabeled_count is not None else 0
            item.issues_found = int(issues_found) if issues_found is not None else 0
            item.error_message = error_message
            item.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(item)
        return item

    def complete_run(self, run_id: int, status: str, summary_message: Optional[str] = None):
        """Mark preprocessing run as completed."""
        run = self.db.query(PreprocessingRun).filter(PreprocessingRun.id == run_id).first()
        if run:
            run.status = status
            run.summary_message = summary_message
            run.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(run)
        return run

    def get_run(self, run_id: int) -> Optional[PreprocessingRun]:
        """Get preprocessing run by ID."""
        return self.db.query(PreprocessingRun).filter(PreprocessingRun.id == run_id).first()

    def get_run_items(self, run_id: int) -> List[PreprocessingRunItem]:
        """Get all items for a preprocessing run."""
        return self.db.query(PreprocessingRunItem).filter(
            PreprocessingRunItem.run_id == run_id
        ).all()

    def get_latest_run(self) -> Optional[PreprocessingRun]:
        """Get the most recent preprocessing run."""
        return self.db.query(PreprocessingRun).order_by(
            desc(PreprocessingRun.started_at)
        ).first()

    def get_runs(self, limit: int = 50) -> List[PreprocessingRun]:
        """Get recent preprocessing runs."""
        return self.db.query(PreprocessingRun).order_by(
            desc(PreprocessingRun.started_at)
        ).limit(limit).all()

    def log_quality_issue(
        self,
        run_item_id: int,
        source_name: str,
        issue_type: str,
        severity: str,
        row_identifier: Optional[str] = None,
        issue_details: Optional[str] = None
    ):
        """Log a data quality issue."""
        issue = DataQualityIssue(
            run_item_id=run_item_id,
            source_name=source_name,
            issue_type=issue_type,
            severity=severity,
            row_identifier=row_identifier,
            issue_details=issue_details
        )
        self.db.add(issue)
        self.db.commit()

    def get_quality_issues(self, run_item_id: Optional[int] = None, limit: int = 100) -> List[DataQualityIssue]:
        """Get data quality issues, optionally filtered by run item."""
        query = self.db.query(DataQualityIssue)
        if run_item_id:
            query = query.filter(DataQualityIssue.run_item_id == run_item_id)
        return query.order_by(desc(DataQualityIssue.created_at)).limit(limit).all()


class MappingFileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_mapping_file(
        self,
        mapping_name: str,
        source_name: str,
        mapping_type: str,
        file_name: str,
        storage_path: str,
        file_type: str,
        required_columns: str,
        uploaded_by: str = "system",
        notes: Optional[str] = None
    ) -> MappingFile:
        """Create a new mapping file record."""
        mapping_file = MappingFile(
            mapping_name=mapping_name,
            source_name=source_name,
            mapping_type=mapping_type,
            file_name=file_name,
            storage_path=storage_path,
            file_type=file_type,
            required_columns=required_columns,
            is_active=0,
            uploaded_by=uploaded_by,
            notes=notes
        )
        self.db.add(mapping_file)
        self.db.commit()
        self.db.refresh(mapping_file)
        return mapping_file

    def activate_mapping_file(self, mapping_file_id: int, mapping_type: str):
        """Activate a mapping file and deactivate others of the same type."""
        # Deactivate all other mapping files of this type
        self.db.query(MappingFile).filter(
            MappingFile.mapping_type == mapping_type
        ).update({"is_active": 0})
        
        # Activate the selected one
        mapping_file = self.db.query(MappingFile).filter(
            MappingFile.id == mapping_file_id
        ).first()
        if mapping_file:
            mapping_file.is_active = 1
            self.db.commit()
            self.db.refresh(mapping_file)
        return mapping_file

    def get_active_mapping_file(self, mapping_type: str) -> Optional[MappingFile]:
        """Get the active mapping file for a given type."""
        return self.db.query(MappingFile).filter(
            MappingFile.mapping_type == mapping_type,
            MappingFile.is_active == 1
        ).first()

    def get_mapping_file(self, mapping_file_id: int) -> Optional[MappingFile]:
        """Get mapping file by ID."""
        return self.db.query(MappingFile).filter(MappingFile.id == mapping_file_id).first()

    def list_mapping_files(self, mapping_type: Optional[str] = None) -> List[MappingFile]:
        """List all mapping files, optionally filtered by type."""
        query = self.db.query(MappingFile)
        if mapping_type:
            query = query.filter(MappingFile.mapping_type == mapping_type)
        return query.order_by(desc(MappingFile.uploaded_at)).all()

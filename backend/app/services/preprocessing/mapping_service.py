"""
Mapping file management service.
Handles loading, validation, and activation of mapping files.
"""

import pandas as pd
import os
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.repositories.preprocessing_repository import MappingFileRepository


class MappingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MappingFileRepository(db)
        self.storage_base_path = "/app/mapping_files"

    def validate_mapping_file(
        self,
        file_path: str,
        required_columns: List[str]
    ) -> Tuple[bool, Optional[str], Optional[pd.DataFrame]]:
        """
        Validate a mapping file.
        Returns: (is_valid, error_message, preview_df)
        """
        try:
            # Determine file type and read
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return False, "Unsupported file type. Use CSV or Excel.", None

            # Check if file is empty
            if df.empty:
                return False, "File is empty", None

            # Check required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", None

            # Return preview (first 10 rows)
            preview = df.head(10)
            return True, None, preview

        except Exception as e:
            return False, f"Error reading file: {str(e)}", None

    def load_mapping_file(self, mapping_type: str) -> Optional[pd.DataFrame]:
        """Load the active mapping file for a given type."""
        mapping_file = self.repo.get_active_mapping_file(mapping_type)
        if not mapping_file:
            return None

        try:
            file_path = mapping_file.storage_path
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return None

            return df
        except Exception as e:
            print(f"Error loading mapping file: {e}")
            return None

    def save_uploaded_file(
        self,
        file_content: bytes,
        file_name: str,
        mapping_type: str
    ) -> str:
        """Save uploaded file to storage and return path."""
        # Ensure storage directory exists
        os.makedirs(self.storage_base_path, exist_ok=True)

        # Create unique filename
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{mapping_type}_{timestamp}_{file_name}"
        file_path = os.path.join(self.storage_base_path, safe_filename)

        # Write file
        with open(file_path, 'wb') as f:
            f.write(file_content)

        return file_path

    def register_mapping_file(
        self,
        mapping_name: str,
        source_name: str,
        mapping_type: str,
        file_name: str,
        storage_path: str,
        file_type: str,
        required_columns: List[str],
        uploaded_by: str = "system",
        notes: Optional[str] = None
    ):
        """Register a new mapping file in the database."""
        required_columns_str = ",".join(required_columns)
        return self.repo.create_mapping_file(
            mapping_name=mapping_name,
            source_name=source_name,
            mapping_type=mapping_type,
            file_name=file_name,
            storage_path=storage_path,
            file_type=file_type,
            required_columns=required_columns_str,
            uploaded_by=uploaded_by,
            notes=notes
        )

    def activate_mapping_file(self, mapping_file_id: int, mapping_type: str):
        """Activate a mapping file."""
        return self.repo.activate_mapping_file(mapping_file_id, mapping_type)

    def get_active_mapping_file_info(self, mapping_type: str):
        """Get active mapping file information."""
        return self.repo.get_active_mapping_file(mapping_type)

    def list_mapping_files(self, mapping_type: Optional[str] = None):
        """List all mapping files."""
        return self.repo.list_mapping_files(mapping_type)

    def get_mapping_preview(self, mapping_file_id: int, rows: int = 10) -> Optional[Dict]:
        """Get preview of a mapping file."""
        mapping_file = self.repo.get_mapping_file(mapping_file_id)
        if not mapping_file:
            return None

        try:
            file_path = mapping_file.storage_path
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return None

            preview = df.head(rows)
            return {
                "columns": list(preview.columns),
                "rows": preview.to_dict(orient='records'),
                "total_rows": len(df)
            }
        except Exception as e:
            return None

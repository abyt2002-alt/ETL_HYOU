"""
Curated data writer service.
Handles writing processed data to curated tables.
"""

import pandas as pd
from sqlalchemy.orm import Session
from app.repositories.curated_repository import CuratedRepository
from datetime import datetime


class CuratedWriterService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CuratedRepository(db)

    def write_curated_data(
        self,
        df: pd.DataFrame,
        table_name: str,
        truncate_first: bool = True
    ) -> int:
        """
        Write DataFrame to curated table.
        
        Args:
            df: DataFrame to write
            table_name: Target curated table name
            truncate_first: Whether to truncate table before insert
        
        Returns:
            Number of rows written
        """
        if df.empty:
            return 0

        # Add processed_at timestamp
        df['processed_at'] = datetime.utcnow()

        # Convert DataFrame to list of dicts
        records = df.to_dict(orient='records')

        # Truncate if requested
        if truncate_first:
            self.repo.truncate_curated_table(table_name)

        # Bulk insert
        self.repo.bulk_insert_curated(table_name, records)

        return len(records)

    def get_curated_data(self, table_name: str, start_date=None, end_date=None, limit=1000):
        """Get curated data from table."""
        return self.repo.get_curated_data(table_name, start_date, end_date, limit)

    def get_curated_count(self, table_name: str) -> int:
        """Get count of rows in curated table."""
        return self.repo.get_curated_count(table_name)

"""
Repository for curated data operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from datetime import date


class CuratedRepository:
    def __init__(self, db: Session):
        self.db = db

    def truncate_curated_table(self, table_name: str):
        """Truncate a curated table."""
        self.db.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
        self.db.commit()

    def bulk_insert_curated(self, table_name: str, data: List[Dict[str, Any]]):
        """Bulk insert data into curated table."""
        if not data:
            return
        
        # Get column names from first row
        columns = list(data[0].keys())
        columns_str = ", ".join(columns)
        placeholders = ", ".join([f":{col}" for col in columns])
        
        query = text(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})")
        
        self.db.execute(query, data)
        self.db.commit()

    def get_curated_data(
        self,
        table_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get curated data with optional date filtering."""
        query = f"SELECT * FROM {table_name}"
        params = {}
        
        conditions = []
        if start_date:
            conditions.append("day >= :start_date")
            params["start_date"] = start_date
        if end_date:
            conditions.append("day <= :end_date")
            params["end_date"] = end_date
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY day DESC LIMIT :limit"
        params["limit"] = limit
        
        result = self.db.execute(text(query), params)
        
        # Convert to list of dicts
        rows = []
        for row in result:
            row_dict = dict(row._mapping)
            # Convert date objects to strings for JSON serialization
            for key, value in row_dict.items():
                if isinstance(value, date):
                    row_dict[key] = value.isoformat()
            rows.append(row_dict)
        
        return rows

    def get_curated_count(self, table_name: str) -> int:
        """Get count of rows in curated table."""
        result = self.db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar()

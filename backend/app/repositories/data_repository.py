import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any


class DataRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_insert(self, table_name: str, df: pd.DataFrame, load_mode: str = "replace") -> int:
        if load_mode == "replace":
            # Truncate table before loading
            self.db.execute(text(f"TRUNCATE TABLE {table_name}"))
            self.db.commit()
        
        df.to_sql(
            table_name,
            self.db.bind,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )
        return len(df)

    def preview_data(self, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        query = text(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT :limit")
        result = self.db.execute(query, {"limit": limit})
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]

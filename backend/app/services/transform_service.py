import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.source_config import SourceConfig


class TransformService:
    @staticmethod
    def convert_excel_date(excel_date) -> datetime:
        if isinstance(excel_date, (int, float)):
            return datetime(1899, 12, 30) + timedelta(days=excel_date)
        if isinstance(excel_date, str):
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                try:
                    return datetime.strptime(excel_date, fmt)
                except ValueError:
                    continue
        if isinstance(excel_date, datetime):
            return excel_date
        raise ValueError(f"Cannot convert date: {excel_date}")

    @staticmethod
    def validate_columns(data: List[Dict[str, Any]], config: SourceConfig) -> tuple:
        if not data:
            return False, "No data to validate"
        
        actual_columns = set(data[0].keys())
        required_columns = set(config.required_columns)
        allowed_columns = required_columns | set(config.optional_columns)
        
        # Check for missing required columns - this is a hard failure
        missing = required_columns - actual_columns
        if missing:
            return False, f"Missing required columns: {missing}"
        
        # Check for unexpected columns - warn but don't fail unless strict mode
        extra = actual_columns - allowed_columns
        if extra:
            if config.strict_columns:
                return False, f"Unexpected columns found (strict mode): {extra}"
            else:
                # Log warning but allow ingestion to continue
                print(f"WARNING: Unexpected columns will be ignored: {extra}")
        
        return True, "Validation passed"

    @staticmethod
    def transform_data(data: List[Dict[str, Any]], config: SourceConfig) -> pd.DataFrame:
        df = pd.DataFrame(data)
        
        # Filter to only include required and optional columns
        allowed_columns = set(config.required_columns) | set(config.optional_columns)
        df = df[[col for col in df.columns if col in allowed_columns]]
        
        for date_field in config.date_fields:
            if date_field in df.columns:
                df[date_field] = df[date_field].apply(TransformService.convert_excel_date)
        
        for field, field_type in config.field_types.items():
            if field not in df.columns:
                continue
            
            if field_type == "integer":
                df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0).astype(int)
            elif field_type == "numeric":
                df[field] = pd.to_numeric(df[field], errors='coerce')
        
        column_mapping = {col: col.lower().replace(" ", "_").replace(".", "_") for col in df.columns}
        df.rename(columns=column_mapping, inplace=True)
        
        return df

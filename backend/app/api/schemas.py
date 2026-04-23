from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class HealthResponse(BaseModel):
    status: str
    service: str


class SourceConfigResponse(BaseModel):
    source_name: str
    sheet_tab_name: str
    target_table_name: str
    required_columns: List[str]
    optional_columns: List[str]
    field_types: Dict[str, str]
    date_fields: List[str]
    numeric_fields: List[str]
    load_mode: str
    unique_keys: List[str]
    strict_columns: bool


class RunRequest(BaseModel):
    triggered_by: str = "user"


class RunResponse(BaseModel):
    id: int
    trigger_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    triggered_by: str
    summary_message: Optional[str]

    class Config:
        from_attributes = True


class RunItemResponse(BaseModel):
    id: int
    run_id: int
    source_name: str
    sheet_tab_name: str
    target_table_name: str
    status: str
    rows_read: int
    rows_loaded: int
    rows_failed: int
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class RunDetailResponse(BaseModel):
    run: RunResponse
    items: List[RunItemResponse]


class DataPreviewResponse(BaseModel):
    table_name: str
    rows: List[Dict[str, Any]]
    count: int

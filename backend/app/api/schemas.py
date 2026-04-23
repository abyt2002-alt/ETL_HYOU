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


# Preprocessing schemas

class PreprocessingRunRequest(BaseModel):
    triggered_by: str = "user"
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class PreprocessingRunResponse(BaseModel):
    id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    triggered_by: str
    summary_message: Optional[str]

    class Config:
        from_attributes = True


class PreprocessingRunItemResponse(BaseModel):
    id: int
    run_id: int
    source_name: str
    input_table: str
    output_table: str
    status: str
    rows_read: int
    rows_output: int
    exact_duplicates_found: int
    business_duplicates_found: int
    mapping_matches: int
    mapping_unmatched: int
    unlabeled_count: int
    issues_found: int
    mapping_file_id: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class PreprocessingRunDetailResponse(BaseModel):
    run: PreprocessingRunResponse
    items: List[PreprocessingRunItemResponse]


class PreprocessingSourceResponse(BaseModel):
    source_name: str
    raw_table: str
    curated_table: str
    mapping_required: bool
    mapping_type: Optional[str]


class MappingFileResponse(BaseModel):
    id: int
    mapping_name: str
    source_name: str
    mapping_type: str
    file_name: str
    file_type: str
    required_columns: str
    is_active: int
    uploaded_at: datetime
    uploaded_by: str
    notes: Optional[str]

    class Config:
        from_attributes = True


class MappingFileUploadResponse(BaseModel):
    id: int
    message: str
    file_name: str


class DataQualityIssueResponse(BaseModel):
    id: int
    run_item_id: int
    source_name: str
    issue_type: str
    severity: str
    row_identifier: Optional[str]
    issue_details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

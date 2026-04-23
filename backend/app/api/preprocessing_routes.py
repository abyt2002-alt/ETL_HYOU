"""
Preprocessing API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.schemas import (
    PreprocessingRunRequest,
    PreprocessingRunResponse,
    PreprocessingRunDetailResponse,
    PreprocessingRunItemResponse,
    PreprocessingSourceResponse,
    DataPreviewResponse
)
from app.preprocessing_config import list_preprocessing_sources, get_preprocessing_config
from app.services.preprocessing.preprocessing_service import PreprocessingService
from app.services.preprocessing.curated_writer_service import CuratedWriterService
from app.repositories.preprocessing_repository import PreprocessingRepository
from typing import List, Optional
from datetime import date

router = APIRouter()


@router.get("/preprocessing/sources", response_model=List[PreprocessingSourceResponse])
def list_sources(db: Session = Depends(get_db)):
    """List all available preprocessing sources."""
    sources = []
    for source_name in list_preprocessing_sources():
        config = get_preprocessing_config(source_name)
        sources.append(PreprocessingSourceResponse(
            source_name=config.source_name,
            raw_table=config.raw_table_name,
            curated_table=config.curated_table_name,
            mapping_required=config.mapping_required,
            mapping_type=config.mapping_type
        ))
    return sources


@router.post("/preprocessing/run/all", response_model=PreprocessingRunResponse)
def run_all_preprocessing(request: PreprocessingRunRequest, db: Session = Depends(get_db)):
    """Run preprocessing for all sources."""
    service = PreprocessingService(db)
    
    start_date = date.fromisoformat(request.start_date) if request.start_date else None
    end_date = date.fromisoformat(request.end_date) if request.end_date else None
    
    run = service.run_all_sources(
        start_date=start_date,
        end_date=end_date,
        triggered_by=request.triggered_by
    )
    return run


@router.post("/preprocessing/run/{source_name}", response_model=PreprocessingRunItemResponse)
def run_single_preprocessing(
    source_name: str,
    request: PreprocessingRunRequest,
    db: Session = Depends(get_db)
):
    """Run preprocessing for a single source."""
    try:
        get_preprocessing_config(source_name)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Source '{source_name}' not found")
    
    service = PreprocessingService(db)
    
    start_date = date.fromisoformat(request.start_date) if request.start_date else None
    end_date = date.fromisoformat(request.end_date) if request.end_date else None
    
    run_item = service.run_single_source(
        source_name=source_name,
        start_date=start_date,
        end_date=end_date,
        triggered_by=request.triggered_by
    )
    return run_item


@router.get("/preprocessing/runs/latest", response_model=Optional[PreprocessingRunResponse])
def get_latest_run(db: Session = Depends(get_db)):
    """Get the latest preprocessing run."""
    repo = PreprocessingRepository(db)
    run = repo.get_latest_run()
    return run


@router.get("/preprocessing/runs", response_model=List[PreprocessingRunResponse])
def list_runs(limit: int = 50, db: Session = Depends(get_db)):
    """List recent preprocessing runs."""
    repo = PreprocessingRepository(db)
    runs = repo.get_runs(limit=limit)
    return runs


@router.get("/preprocessing/runs/{run_id}", response_model=PreprocessingRunDetailResponse)
def get_run_detail(run_id: int, db: Session = Depends(get_db)):
    """Get preprocessing run details with items."""
    repo = PreprocessingRepository(db)
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    items = repo.get_run_items(run_id)
    return PreprocessingRunDetailResponse(run=run, items=items)


@router.get("/preprocessing/curated/{table_name}", response_model=DataPreviewResponse)
def get_curated_data(
    table_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """Get curated data from a table."""
    # Validate table name
    valid_tables = ["curated_shopify", "curated_ga", "curated_gads", "curated_meta"]
    if table_name not in valid_tables:
        raise HTTPException(status_code=400, detail="Invalid table name")
    
    writer_service = CuratedWriterService(db)
    
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    
    rows = writer_service.get_curated_data(table_name, start, end, limit)
    count = writer_service.get_curated_count(table_name)
    
    return DataPreviewResponse(
        table_name=table_name,
        rows=rows,
        count=count
    )

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.schemas import (
    HealthResponse, SourceConfigResponse, RunResponse, 
    RunDetailResponse, DataPreviewResponse, RunRequest
)
from app.source_config import get_all_sources, get_source_config
from app.services.ingestion_service import IngestionService
from app.repositories.run_repository import RunRepository
from app.repositories.data_repository import DataRepository

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "healthy", "service": "ingestion-platform"}


@router.get("/sources", response_model=List[SourceConfigResponse])
def list_sources():
    sources = get_all_sources()
    return [source.to_dict() for source in sources]


@router.post("/ingest/all", response_model=RunResponse)
def run_all_ingestion(request: RunRequest, db: Session = Depends(get_db)):
    service = IngestionService(db)
    run = service.run_all_sources(triggered_by=request.triggered_by)
    return run


@router.post("/ingest/{source_name}", response_model=RunResponse)
def run_single_ingestion(source_name: str, request: RunRequest, db: Session = Depends(get_db)):
    try:
        get_source_config(source_name)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Source '{source_name}' not found")
    
    service = IngestionService(db)
    run = service.run_single_source(source_name, triggered_by=request.triggered_by)
    return run


@router.get("/runs/latest", response_model=RunDetailResponse)
def get_latest_run(db: Session = Depends(get_db)):
    repo = RunRepository(db)
    run = repo.get_latest_run()
    if not run:
        raise HTTPException(status_code=404, detail="No runs found")
    
    items = repo.get_run_items(run.id)
    return {"run": run, "items": items}


@router.get("/runs", response_model=List[RunResponse])
def get_run_history(limit: int = 50, db: Session = Depends(get_db)):
    repo = RunRepository(db)
    return repo.get_run_history(limit)


@router.get("/runs/{run_id}", response_model=RunDetailResponse)
def get_run_detail(run_id: int, db: Session = Depends(get_db)):
    repo = RunRepository(db)
    run = repo.get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    items = repo.get_run_items(run_id)
    return {"run": run, "items": items}


@router.get("/data/{table_name}", response_model=DataPreviewResponse)
def preview_data(table_name: str, limit: int = 100, db: Session = Depends(get_db)):
    repo = DataRepository(db)
    try:
        data = repo.preview_data(table_name, limit)
        return {"table_name": table_name, "rows": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

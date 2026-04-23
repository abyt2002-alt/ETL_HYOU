from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.schemas import RunResponse, RunRequest
from app.source_config import get_source_config
from app.services.ingestion_service import IngestionService

router = APIRouter()


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

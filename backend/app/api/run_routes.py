from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.schemas import RunResponse, RunDetailResponse
from app.repositories.run_repository import RunRepository

router = APIRouter()


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

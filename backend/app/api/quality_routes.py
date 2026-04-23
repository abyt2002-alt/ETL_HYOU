"""
Data quality API routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.schemas import DataQualityIssueResponse
from app.repositories.preprocessing_repository import PreprocessingRepository
from typing import List, Optional

router = APIRouter()


@router.get("/quality/issues", response_model=List[DataQualityIssueResponse])
def list_quality_issues(
    run_item_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List data quality issues."""
    repo = PreprocessingRepository(db)
    issues = repo.get_quality_issues(run_item_id, limit)
    return issues


@router.get("/quality/issues/run-item/{run_item_id}", response_model=List[DataQualityIssueResponse])
def get_run_item_issues(run_item_id: int, db: Session = Depends(get_db)):
    """Get quality issues for a specific run item."""
    repo = PreprocessingRepository(db)
    issues = repo.get_quality_issues(run_item_id)
    return issues

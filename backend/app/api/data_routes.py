from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.schemas import DataPreviewResponse
from app.repositories.data_repository import DataRepository

router = APIRouter()


@router.get("/data/{table_name}", response_model=DataPreviewResponse)
def preview_data(table_name: str, limit: int = 100, db: Session = Depends(get_db)):
    repo = DataRepository(db)
    try:
        data = repo.preview_data(table_name, limit)
        return {"table_name": table_name, "rows": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

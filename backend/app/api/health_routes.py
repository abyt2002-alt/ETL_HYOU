from fastapi import APIRouter
from app.api.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "healthy", "service": "ingestion-platform"}

from fastapi import APIRouter
from typing import List
from app.api.schemas import SourceConfigResponse
from app.source_config import get_all_sources

router = APIRouter()


@router.get("/sources", response_model=List[SourceConfigResponse])
def list_sources():
    sources = get_all_sources()
    return [source.to_dict() for source in sources]

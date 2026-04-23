"""
Mapping file management API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.schemas import MappingFileResponse, MappingFileUploadResponse
from app.services.preprocessing.mapping_service import MappingService
from typing import List, Optional
import json

router = APIRouter()


@router.get("/mapping-files", response_model=List[MappingFileResponse])
def list_mapping_files(mapping_type: Optional[str] = None, db: Session = Depends(get_db)):
    """List all mapping files."""
    service = MappingService(db)
    files = service.list_mapping_files(mapping_type)
    return files


@router.post("/mapping-files/upload", response_model=MappingFileUploadResponse)
async def upload_mapping_file(
    file: UploadFile = File(...),
    mapping_name: str = Form(...),
    source_name: str = Form(...),
    mapping_type: str = Form(...),
    required_columns: str = Form(...),
    uploaded_by: str = Form("user"),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a new mapping file."""
    service = MappingService(db)
    
    # Parse required columns
    try:
        required_cols = json.loads(required_columns)
    except:
        required_cols = [col.strip() for col in required_columns.split(',')]
    
    # Read file content
    content = await file.read()
    
    # Save file
    file_path = service.save_uploaded_file(content, file.filename, mapping_type)
    
    # Validate file
    is_valid, error_msg, preview = service.validate_mapping_file(file_path, required_cols)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Determine file type
    file_type = "csv" if file.filename.endswith('.csv') else "excel"
    
    # Register in database
    mapping_file = service.register_mapping_file(
        mapping_name=mapping_name,
        source_name=source_name,
        mapping_type=mapping_type,
        file_name=file.filename,
        storage_path=file_path,
        file_type=file_type,
        required_columns=required_cols,
        uploaded_by=uploaded_by,
        notes=notes
    )
    
    return MappingFileUploadResponse(
        id=mapping_file.id,
        message="File uploaded successfully",
        file_name=file.filename
    )


@router.post("/mapping-files/{mapping_file_id}/activate", response_model=MappingFileResponse)
def activate_mapping_file(
    mapping_file_id: int,
    mapping_type: str,
    db: Session = Depends(get_db)
):
    """Activate a mapping file."""
    service = MappingService(db)
    mapping_file = service.activate_mapping_file(mapping_file_id, mapping_type)
    if not mapping_file:
        raise HTTPException(status_code=404, detail="Mapping file not found")
    return mapping_file


@router.get("/mapping-files/{mapping_file_id}/preview")
def preview_mapping_file(mapping_file_id: int, rows: int = 10, db: Session = Depends(get_db)):
    """Preview a mapping file."""
    service = MappingService(db)
    preview = service.get_mapping_preview(mapping_file_id, rows)
    if not preview:
        raise HTTPException(status_code=404, detail="Mapping file not found or cannot be read")
    return preview


@router.get("/mapping-files/active/{mapping_type}", response_model=Optional[MappingFileResponse])
def get_active_mapping_file(mapping_type: str, db: Session = Depends(get_db)):
    """Get the active mapping file for a type."""
    service = MappingService(db)
    mapping_file = service.get_active_mapping_file_info(mapping_type)
    return mapping_file

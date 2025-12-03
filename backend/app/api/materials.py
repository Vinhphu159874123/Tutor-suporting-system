"""
Session Materials API
File upload/download, materials management for sessions
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional
import os
from pathlib import Path

from app.schemas.materials import MaterialResponse
from app.core.dependencies import get_current_user, get_db
from app.models.database import User, SessionMaterial, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = Path("uploads/materials")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'zip', 'rar', '7z', 
    'jpg', 'jpeg', 'png', 'gif',
    'mp4', 'avi', 'mov', 'wmv'
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# SESSION MATERIALS ENDPOINTS
# ============================================================================

@router.post("/sessions/{session_id}/materials", response_model=MaterialResponse)
async def upload_material(
    session_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload learning material for a session
    
    - Validates file type and size
    - Stores file securely
    - Creates database record
    
    Returns: Material metadata
    """
    # Check if session exists
    result = await db.execute(select(Session).where(Session.session_id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content to check size
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{session_id}_{current_user.user_id}_{int(os.urandom(4).hex(), 16)}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        with open(file_path, 'wb') as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create database record
    material = SessionMaterial(
        session_id=session_id,
        uploaded_by=current_user.user_id,
        file_name=file.filename,
        file_url=str(file_path),
        file_type=file.content_type,
        file_size=file_size,
        description=description
    )
    
    db.add(material)
    await db.commit()
    await db.refresh(material)
    
    return MaterialResponse(
        material_id=material.material_id,
        session_id=material.session_id,
        file_name=material.file_name,
        file_url=material.file_url,
        file_type=material.file_type,
        file_size=material.file_size,
        description=material.description,
        uploaded_by=material.uploaded_by,
        uploaded_at=material.uploaded_at
    )


@router.get("/sessions/{session_id}/materials", response_model=List[MaterialResponse])
async def get_session_materials(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all materials for a session
    
    Returns: List of materials sorted by upload date
    """
    # Check if session exists
    result = await db.execute(select(Session).where(Session.session_id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get all materials for this session
    result = await db.execute(
        select(SessionMaterial)
        .where(SessionMaterial.session_id == session_id)
        .order_by(SessionMaterial.uploaded_at.desc())
    )
    materials = result.scalars().all()
    
    return [
        MaterialResponse(
            material_id=m.material_id,
            session_id=m.session_id,
            file_name=m.file_name,
            file_url=m.file_url,
            file_type=m.file_type,
            file_size=m.file_size,
            description=m.description,
            uploaded_by=m.uploaded_by,
            uploaded_at=m.uploaded_at
        )
        for m in materials
    ]


@router.get("/materials/{material_id}/download")
async def download_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download material file
    
    Returns: File stream
    """
    # Get material from database
    result = await db.execute(
        select(SessionMaterial).where(SessionMaterial.material_id == material_id)
    )
    material = result.scalar_one_or_none()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Check if file exists
    file_path = Path(material.file_url)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    # Return file
    return FileResponse(
        path=file_path,
        filename=material.file_name,
        media_type=material.file_type or 'application/octet-stream'
    )


@router.put("/materials/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: int,
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update material metadata (description only)
    
    - Permission check: uploader or admin only
    
    Returns: Updated material
    """
    # Get material from database
    result = await db.execute(
        select(SessionMaterial).where(SessionMaterial.material_id == material_id)
    )
    material = result.scalar_one_or_none()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Check permission
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if material.uploaded_by != current_user.user_id and 'admin' not in user_roles and 'coordinator' not in user_roles:
        raise HTTPException(status_code=403, detail="Not authorized to update this material")
    
    # Update description
    if description is not None:
        material.description = description
    
    await db.commit()
    await db.refresh(material)
    
    return MaterialResponse(
        material_id=material.material_id,
        session_id=material.session_id,
        file_name=material.file_name,
        file_url=material.file_url,
        file_type=material.file_type,
        file_size=material.file_size,
        description=material.description,
        uploaded_by=material.uploaded_by,
        uploaded_at=material.uploaded_at
    )


@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete material and file
    
    - Permission check: uploader, admin, or coordinator only
    - Removes file from storage
    - Removes database record
    
    Returns: Success message
    """
    # Get material from database
    result = await db.execute(
        select(SessionMaterial).where(SessionMaterial.material_id == material_id)
    )
    material = result.scalar_one_or_none()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Check permission (uploader, admin, or coordinator)
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if material.uploaded_by != current_user.user_id and 'admin' not in user_roles and 'coordinator' not in user_roles:
        raise HTTPException(status_code=403, detail="Not authorized to delete this material")
    
    # Delete file from storage
    file_path = Path(material.file_url)
    if file_path.exists():
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: Failed to delete file {file_path}: {e}")
    
    # Delete database record
    await db.delete(material)
    await db.commit()
    
    return {"message": "Material deleted successfully"}
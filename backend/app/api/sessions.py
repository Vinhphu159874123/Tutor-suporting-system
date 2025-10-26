from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.services.session_service import SessionService
from app.core.dependencies import get_session_service

router = APIRouter()

# ============================================================================
# SESSION ENDPOINTS - Migrated to Layered Architecture
# ============================================================================

@router.get("/", response_model=List[SessionResponse])
async def get_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    tutor_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    session_service: SessionService = Depends(get_session_service)
):
    """Get all sessions with filters"""
    return await session_service.get_all_sessions(
        skip=skip, limit=limit,
        tutor_id=tutor_id,
        student_id=student_id,
        status=status
    )

@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    session_data: SessionCreate,
    session_service: SessionService = Depends(get_session_service)
):
    """Create new session - PLACEHOLDER for conflict detection"""
    return await session_service.create_session(session_data)

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    session_service: SessionService = Depends(get_session_service)
):
    """Get session by ID"""
    return await session_service.get_session(session_id)

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    session_service: SessionService = Depends(get_session_service)
):
    """Update session"""
    return await session_service.update_session(session_id, session_data)


# ============================================================================
# PLACEHOLDER ENDPOINTS - Complex features not implemented
# ============================================================================

@router.post("/{session_id}/complete")
async def complete_session(session_id: int):
    """Mark session as completed - PLACEHOLDER"""
    return {"message": "Complete session - Implementation pending"}

@router.post("/{session_id}/materials")
async def upload_materials(session_id: int):
    """Upload learning materials for a session - PLACEHOLDER"""
    return {"message": "Upload materials - Implementation pending"}

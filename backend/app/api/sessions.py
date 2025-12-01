from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException, status
from typing import List, Optional

from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.schemas.session_participant import (
    SessionJoinRequest, 
    SessionParticipantResponse, 
    SessionParticipantUpdate
)
from app.services.session_service import SessionService
from app.core.dependencies import get_session_service, get_current_user
from app.models.database import User

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
    subject_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    session_service: SessionService = Depends(get_session_service)
):
    """Get all sessions with filters"""
    return await session_service.get_all_sessions(
        skip=skip, limit=limit,
        tutor_id=tutor_id,
        student_id=student_id,
        subject_id=subject_id,
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
# SESSION ACTION ENDPOINTS
# ============================================================================

@router.post("/{session_id}/complete")
async def complete_session(
    session_id: int,
    session_service: SessionService = Depends(get_session_service)
):
    """Mark session as completed"""
    return await session_service.complete_session(session_id)


@router.post("/{session_id}/publish")
async def publish_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Publish session (tutor makes it visible for students to join)"""
    return await session_service.publish_session(session_id, current_user.user_id)


@router.post("/{session_id}/materials")
async def upload_materials(
    session_id: int,
    file: Optional[UploadFile] = File(None),
    file_url: Optional[str] = Form(None),
    file_name: Optional[str] = Form(None),
    file_type: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    uploaded_by: int = Form(...),
    session_service: SessionService = Depends(get_session_service)
):
    """Upload learning materials (PDF, images, documents) for a session
    
    Can upload actual file OR provide external URL
    """
    if file:
        # Upload actual file
        return await session_service.upload_material(session_id, file, uploaded_by, description)
    elif file_url and file_name:
        # Just save metadata (external file URL)
        return await session_service.save_material_metadata(
            session_id, file_url, file_name, file_type or "document", uploaded_by, description
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either file upload or file_url + file_name"
        )


# ============================================================================
# SESSION PARTICIPANT ENDPOINTS - Student Join/Leave
# ============================================================================

@router.post("/{session_id}/join", response_model=SessionParticipantResponse)
async def join_session(
    session_id: int,
    join_request: SessionJoinRequest,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Student joins a session (creates pending participant)"""
    return await session_service.join_session(session_id, current_user.user_id, join_request)


@router.post("/{session_id}/participants/{participant_id}/accept")
async def accept_participant(
    session_id: int,
    participant_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Tutor accepts a student join request"""
    return await session_service.update_participant_status(
        session_id, participant_id, "confirmed", current_user.user_id
    )


@router.post("/{session_id}/participants/{participant_id}/reject")
async def reject_participant(
    session_id: int,
    participant_id: int,
    update_data: SessionParticipantUpdate,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Tutor rejects a student join request"""
    return await session_service.update_participant_status(
        session_id, participant_id, "cancelled", current_user.user_id, update_data.notes
    )


@router.delete("/{session_id}/leave")
async def leave_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Student leaves a session"""
    return await session_service.leave_session(session_id, current_user.user_id)


@router.get("/{session_id}/participants", response_model=List[SessionParticipantResponse])
async def get_session_participants(
    session_id: int,
    session_service: SessionService = Depends(get_session_service)
):
    """Get all participants of a session"""
    return await session_service.get_session_participants(session_id)


@router.post("/bulk-save-for-subject")
async def bulk_save_sessions_for_subject(
    subject_id: int,
    sessions_data: List[dict],
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Bulk create/update sessions for a subject
    Used by tutor to save generated weekly sessions
    """
    from app.models.database import Tutor, Session
    from sqlalchemy import select, delete
    from datetime import datetime, time
    
    # Get tutor ID
    tutor_result = await session_service.session_repo.db.execute(
        select(Tutor).where(Tutor.user_id == current_user.user_id)
    )
    tutor = tutor_result.scalar_one_or_none()
    
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor profile not found")
    
    # Delete existing sessions for this subject by this tutor
    await session_service.session_repo.db.execute(
        delete(Session).where(
            Session.subject_id == subject_id,
            Session.tutor_id == tutor.tutor_id
        )
    )
    
    # Create new sessions
    created_sessions = []
    try:
        for session_data in sessions_data:
            try:
                # Parse date and time
                session_date = datetime.fromisoformat(session_data['date']).date()
                time_slots = session_data['time_slots']
                
                # Handle time slots format - could be "HH:MM-HH:MM" or "HH:MM:SS-HH:MM:SS"
                if time_slots and len(time_slots) > 0:
                    time_parts = time_slots[0].split('-')
                    start_time_str = time_parts[0].strip()
                    end_time_str = time_parts[1].strip()
                    
                    # Try parsing with seconds first, then without
                    try:
                        start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
                    except ValueError:
                        start_time = datetime.strptime(start_time_str, "%H:%M").time()
                    
                    try:
                        end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
                    except ValueError:
                        end_time = datetime.strptime(end_time_str, "%H:%M").time()
                else:
                    start_time = datetime.strptime("07:00", "%H:%M").time()
                    end_time = datetime.strptime("09:00", "%H:%M").time()
                
                new_session = Session(
                    tutor_id=tutor.tutor_id,
                    subject_id=subject_id,
                    title=f"Session {session_data['session_number']}",
                    description=session_data.get('description', ''),
                    scheduled_date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                    location_type='online' if session_data.get('location') == 'Online' else 'physical',
                    meeting_link=session_data.get('meeting_link', ''),
                    physical_address=session_data.get('location', '') if session_data.get('location') != 'Online' else None,
                    materials=session_data.get('materials', []),
                    status='draft'
                )
                
                session_service.session_repo.db.add(new_session)
                created_sessions.append(new_session)
                
            except Exception as e:
                print(f"Error creating session {session_data.get('session_number')}: {e}")
                print(f"Session data: {session_data}")
                raise HTTPException(status_code=400, detail=f"Invalid session data: {str(e)}")
        
        await session_service.session_repo.db.commit()
        
    except HTTPException:
        await session_service.session_repo.db.rollback()
        raise
    except Exception as e:
        await session_service.session_repo.db.rollback()
        print(f"Error saving sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save sessions: {str(e)}")
    
    return {
        "message": f"Successfully saved {len(created_sessions)} sessions",
        "sessions_count": len(created_sessions)
    }

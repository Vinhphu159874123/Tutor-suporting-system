"""Sessions API — thin controller, delegates to SessionService"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException, status
from fastapi.responses import Response, RedirectResponse
from typing import List, Optional
import httpx

from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.schemas.session_participant import SessionJoinRequest, SessionParticipantResponse, SessionParticipantUpdate
from app.services.session_service import SessionService
from app.core.dependencies import get_session_service, get_current_user
from app.models.database import User

router = APIRouter()

# ============================================================================
# DASHBOARD & MY SESSIONS
# ============================================================================

@router.get("/my-sessions/dashboard")
async def get_my_sessions_dashboard(
    mode: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    await session_service.ensure_profile(current_user, mode)
    if mode:
        if mode == 'student' and not current_user.student_id:
            raise HTTPException(status_code=403, detail="User is not a student")
        if mode == 'tutor' and not current_user.tutor_id:
            raise HTTPException(status_code=403, detail="User is not a tutor")
    return await session_service.get_dashboard_sessions(current_user, mode)


@router.get("/my-sessions", response_model=List[SessionResponse])
async def get_my_sessions(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    mode: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    await session_service.ensure_profile(current_user, mode)
    active_role = mode or current_user.role
    if active_role == 'student':
        return await session_service.get_all_sessions(
            student_id=current_user.student_id,
            status=status_filter, skip=skip, limit=limit)
    elif active_role == 'tutor':
        tid = await session_service.get_tutor_id_for_user(current_user.user_id)
        if tid:
            return await session_service.get_all_sessions(
                tutor_id=tid, status=status_filter, skip=skip, limit=limit)
    return []


# ============================================================================
# CORE CRUD
# ============================================================================

@router.get("/", response_model=List[SessionResponse])
async def get_sessions(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    subject_id: Optional[int] = None, tutor_id: Optional[int] = None,
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.get_all_sessions(
        skip=skip, limit=limit, status=status_filter,
        subject_id=subject_id, tutor_id=tutor_id)


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.create_session(session_data)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int, session_service: SessionService = Depends(get_session_service),
):
    return await session_service.get_session(session_id)


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int, session_data: SessionUpdate,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.update_session(session_id, session_data)


@router.post("/{session_id}/complete")
async def complete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.complete_session(session_id)


@router.post("/{session_id}/publish")
async def publish_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.publish_session(session_id, current_user.user_id)


# ============================================================================
# MATERIALS
# ============================================================================

@router.post("/{session_id}/materials")
async def upload_materials(
    session_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    if file.filename:
        return await session_service.upload_material(session_id, file, current_user.user_id, description)
    raise HTTPException(status_code=400, detail="No file provided")


@router.get("/materials/bulk")
async def get_bulk_materials(
    session_ids: str = Query(...),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        ids = [int(i.strip()) for i in session_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session IDs format")
    return await session_service.get_bulk_materials(ids)


@router.get("/{session_id}/materials")
async def get_session_materials(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.get_session_materials_list(session_id)


@router.delete("/{session_id}/materials/{material_identifier}")
async def delete_material(
    session_id: int, material_identifier: str,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if not any(r in roles for r in ['tutor', 'admin', 'coordinator']):
        raise HTTPException(status_code=403, detail="Only tutors/coordinators/admins can delete materials")
    return await session_service.delete_material_by_identifier(session_id, material_identifier)


@router.get("/{session_id}/materials/{material_identifier}/download")
async def download_material(
    session_id: int, material_identifier: str,
    inline: bool = Query(False),
    session_service: SessionService = Depends(get_session_service),
):
    mat = await session_service.download_material_by_identifier(session_id, material_identifier)
    if mat.file_url:
        if not inline:
            return RedirectResponse(url=mat.file_url)
        async with httpx.AsyncClient() as client:
            resp = await client.get(mat.file_url)
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="File not found in storage")
            mt = 'application/pdf' if mat.file_name.lower().endswith('.pdf') else resp.headers.get('content-type', 'application/octet-stream')
            return Response(content=resp.content, media_type=mt,
                            headers={"Content-Disposition": f'inline; filename="{mat.file_name}"',
                                     "Content-Length": str(len(resp.content))})
    if mat.file_data:
        mt = 'application/pdf' if mat.file_name.lower().endswith('.pdf') else 'application/octet-stream'
        disp = 'inline' if inline else 'attachment'
        return Response(content=mat.file_data,
                        media_type=mt if inline else 'application/octet-stream',
                        headers={"Content-Disposition": f'{disp}; filename="{mat.file_name}"',
                                 "Content-Length": str(len(mat.file_data))})
    raise HTTPException(status_code=404, detail="File data not found")


# ============================================================================
# PARTICIPANTS
# ============================================================================

@router.post("/{session_id}/join", response_model=SessionParticipantResponse)
async def join_session(
    session_id: int, join_request: SessionJoinRequest,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.join_session(session_id, current_user.user_id, join_request)


@router.post("/{session_id}/participants/{participant_id}/accept")
async def accept_participant(
    session_id: int, participant_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.update_participant_status(session_id, participant_id, "confirmed", current_user.user_id)


@router.post("/{session_id}/participants/{participant_id}/reject")
async def reject_participant(
    session_id: int, participant_id: int, update_data: SessionParticipantUpdate,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.update_participant_status(
        session_id, participant_id, "cancelled", current_user.user_id, update_data.notes)


@router.delete("/{session_id}/leave")
async def leave_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.leave_session(session_id, current_user.user_id)


@router.delete("/remove-student-from-subject")
async def remove_student_from_subject(
    subject_id: int = Query(...), student_id: int = Query(...), tutor_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.remove_student_from_subject(current_user, subject_id, student_id, tutor_id)


@router.get("/{session_id}/participants", response_model=List[SessionParticipantResponse])
async def get_session_participants(
    session_id: int, session_service: SessionService = Depends(get_session_service),
):
    return await session_service.get_session_participants(session_id)


# ============================================================================
# BULK SAVE
# ============================================================================

@router.post("/bulk-save-for-subject")
async def bulk_save_sessions_for_subject(
    subject_id: int, sessions_data: List[dict],
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.bulk_save_sessions(current_user, subject_id, sessions_data)


# ============================================================================
# FEEDBACK
# ============================================================================

@router.post("/{session_id}/feedback")
async def submit_session_feedback(
    session_id: int,
    rating: int = Form(..., ge=1, le=5),
    comment: Optional[str] = Form(None),
    is_anonymous: bool = Form(False),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.submit_feedback(session_id, current_user.user_id, rating, comment, is_anonymous)


@router.get("/{session_id}/feedback")
async def get_session_feedbacks(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    return await session_service.get_feedbacks(session_id, roles, current_user.user_id)


@router.get("/feedback/bulk")
async def get_bulk_feedbacks(
    session_ids: str = Query(...),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        ids = [int(i.strip()) for i in session_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session IDs format")
    roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    return await session_service.get_bulk_feedbacks(ids, roles, current_user.user_id)


@router.get("/subject/{subject_id}/feedbacks")
async def get_subject_feedbacks(
    subject_id: int,
    tutor_id: int = Query(None),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.get_subject_feedbacks(subject_id, current_user, tutor_id)


# ============================================================================
# ATTENDANCE
# ============================================================================

@router.get("/{session_id}/attendance/participants")
async def get_session_participants_for_attendance(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    await session_service.get_session(session_id)
    roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'tutor' not in roles:
        raise HTTPException(status_code=403, detail="Only tutors can view participants")
    return await session_service.get_attendance_participants(session_id)


@router.post("/{session_id}/attendance")
async def mark_attendance(
    session_id: int, attendance_data: List[dict],
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'tutor' not in roles:
        raise HTTPException(status_code=403, detail="Only tutors can mark attendance")
    return await session_service.mark_attendance(session_id, attendance_data)

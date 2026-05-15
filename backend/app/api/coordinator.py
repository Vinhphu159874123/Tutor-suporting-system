"""Coordinator API — thin controller, delegates to CoordinatorService"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Optional
from app.core.dependencies import get_current_user, get_coordinator_service
from app.models.database import User
from app.services.coordinator_service import CoordinatorService
from app.schemas.coordinator import ApprovalRequest

router = APIRouter()

_svc = get_coordinator_service

def _check(user: User):
    roles = user.role if isinstance(user.role, list) else [user.role]
    if 'coordinator' not in roles and 'admin' not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only coordinators can access this endpoint")

# --- Tutor Registration Approval ---
@router.get("/tutor-registrations")
async def get_pending_tutor_registrations(
    status_filter: str = "pending", skip: int = 0, limit: int = 50,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.get_pending_registrations(status_filter, skip, limit)

@router.get("/tutor-registrations/{registration_id}/schedules")
async def get_registration_schedules(
    registration_id: int,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.get_registration_schedules(registration_id)

@router.put("/tutor-registrations/{registration_id}/approve")
async def approve_tutor_registration(
    registration_id: int, approval_data: ApprovalRequest,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.approve_registration(current_user, registration_id, approval_data.schedule_id)

@router.put("/tutor-registrations/{registration_id}/reject")
async def reject_tutor_registration(
    registration_id: int, reason: str,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.reject_registration(current_user, registration_id, reason)

# --- Session Approval ---
@router.get("/sessions/pending")
async def get_pending_sessions(
    skip: int = 0, limit: int = 50,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.get_pending_sessions(skip, limit)

@router.put("/sessions/{session_id}/approve")
async def approve_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.approve_session(session_id)

@router.put("/sessions/{session_id}/reject")
async def reject_session(
    session_id: int, reason: str,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.reject_session(session_id, reason)

# --- Tutor Management ---
@router.get("/tutors")
async def get_all_tutors(
    skip: int = 0, limit: int = 50, search: str = None,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.get_all_tutors(skip, limit, search)

@router.get("/tutors/{tutor_id}/courses")
async def get_tutor_courses(
    tutor_id: int,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.get_tutor_courses(tutor_id)

@router.get("/tutors/{tutor_id}/courses/{subject_id}/details")
async def get_course_details_with_feedbacks(
    tutor_id: int, subject_id: int,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.get_course_details(tutor_id, subject_id)

@router.get("/tutors/{tutor_id}/courses/{subject_id}/export")
async def export_course_report(
    tutor_id: int, subject_id: int, format: str = "csv",
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    details = await svc.get_course_details(tutor_id, subject_id)
    if format == "csv":
        csv_data = svc.export_csv(details)
        fn = f"report_{details['tutor']['staff_code']}_{details['course']['subject_code']}.csv"
        return StreamingResponse(iter([csv_data]), media_type="text/csv",
                                 headers={"Content-Disposition": f"attachment; filename={fn}"})
    return details

@router.post("/tutors/{tutor_id}/update-rating")
async def update_tutor_rating(
    tutor_id: int,
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.update_tutor_rating(tutor_id)

@router.post("/tutors/update-all-ratings")
async def update_all_tutors_ratings(
    current_user: User = Depends(get_current_user),
    svc: CoordinatorService = Depends(_svc),
):
    _check(current_user)
    return await svc.update_all_ratings()

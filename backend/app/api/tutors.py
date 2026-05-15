"""
Tutor Routes — thin controller, delegates to TutorService
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.tutor import TutorCreate, TutorUpdate, TutorResponse, TutorRegistrationCreate, TutorRegistrationResponse
from app.schemas.session import SessionListResponse
from app.services.tutor_service import TutorService
from app.core.dependencies import get_tutor_service, get_current_user
from app.models.database import User

router = APIRouter()

# ============================================================================
# TUTOR ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[TutorResponse])
async def get_tutors(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100),
    subject: Optional[str] = None, min_rating: Optional[float] = Query(None, ge=0, le=5),
    tutor_service: TutorService = Depends(get_tutor_service),
):
    return await tutor_service.get_all_tutors(skip=skip, limit=limit, subject=subject, min_rating=min_rating)


@router.get("/me", response_model=TutorResponse)
async def get_my_tutor_profile(
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    profile = await tutor_service.get_tutor_by_user_id(current_user.user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor profile not found.")
    return profile


@router.post("/register", response_model=TutorResponse)
async def register_tutor(
    tutor_data: TutorCreate,
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    tutor_data.user_id = current_user.user_id
    return await tutor_service.register_tutor(tutor_data)


@router.post("/register-subject", response_model=TutorRegistrationResponse)
async def register_subject(
    registration_data: TutorRegistrationCreate,
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    return await tutor_service.register_subject(current_user.user_id, registration_data)


@router.get("/my-registrations")
async def get_my_registrations(
    status: Optional[str] = Query(None),
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    return await tutor_service.get_my_registrations(current_user.user_id, status)


# ============================================================================
# SPECIFIC ROUTES - Must come BEFORE dynamic routes like /{tutor_id}
# ============================================================================

@router.get("/available-courses")
async def get_available_courses(
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
    skip_cache: bool = False,
):
    return await tutor_service.get_available_courses(current_user.user_id, skip_cache)


@router.post("/courses/{registration_id}/request-join")
async def request_join_course(
    registration_id: int,
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    return await tutor_service.request_join_course(
        current_user.user_id, current_user.full_name, registration_id)


@router.post("/courses/{subject_id}/generate-sessions")
async def generate_sessions_for_course(
    subject_id: int,
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    return await tutor_service.generate_sessions_for_course(current_user.user_id, subject_id)


@router.get("/courses/enrolled-students")
async def get_enrolled_students(
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    return await tutor_service.get_enrolled_students(current_user.user_id)


@router.get("/sessions", response_model=SessionListResponse)
async def get_tutor_sessions(
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100),
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    profile = await tutor_service.get_tutor_by_user_id(current_user.user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor profile not found")
    return await tutor_service.get_tutor_sessions(
        tutor_user_id=current_user.user_id, status=status,
        start_date=start_date, end_date=end_date, skip=skip, limit=limit)


# ============================================================================
# DYNAMIC ROUTES
# ============================================================================

@router.get("/{tutor_id}", response_model=TutorResponse)
async def get_tutor(tutor_id: int, tutor_service: TutorService = Depends(get_tutor_service)):
    return await tutor_service.get_tutor(tutor_id)


@router.get("/{tutor_id}/availability")
async def get_tutor_availability(tutor_id: int, tutor_service: TutorService = Depends(get_tutor_service)):
    return await tutor_service.get_tutor_availability(tutor_id)


@router.put("/{tutor_id}", response_model=TutorResponse)
async def update_tutor(
    tutor_id: int, tutor_data: TutorUpdate,
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    return await tutor_service.update_tutor(tutor_id, tutor_data)


@router.delete("/{tutor_id}")
async def delete_tutor(
    tutor_id: int,
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    await tutor_service.delete_tutor(tutor_id)
    return {"message": "Tutor profile deleted successfully"}


@router.get("/{tutor_id}/reviews")
async def get_tutor_reviews(
    tutor_id: int, skip: int = 0, limit: int = 20,
    tutor_service: TutorService = Depends(get_tutor_service),
):
    return await tutor_service.get_tutor_reviews(tutor_id, skip, min(limit, 100))


@router.post("/check-schedule-conflicts")
async def check_schedule_conflicts(
    registration_ids: list[int],
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user),
):
    return await tutor_service.check_schedule_conflicts(current_user.user_id, registration_ids)

"""
Tutor Routes - Layered Architecture
Routes delegate to TutorService - PLACEHOLDER implementations preserved
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.schemas.tutor import TutorCreate, TutorUpdate, TutorResponse
from app.services.tutor_service import TutorService
from app.core.dependencies import get_tutor_service, get_current_user
from app.models.database import User

router = APIRouter()

# ============================================================================
# TUTOR ENDPOINTS - Layered Architecture (PLACEHOLDER preserved)
# ============================================================================

@router.get("/", response_model=List[TutorResponse])
async def get_tutors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    subject: Optional[str] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    tutor_service: TutorService = Depends(get_tutor_service)
):
    """
    Get all tutors with optional filtering
    
    Filters: subject, min_rating
    """
    return await tutor_service.get_all_tutors(
        skip=skip,
        limit=limit,
        subject=subject,
        min_rating=min_rating
    )


@router.get("/me", response_model=TutorResponse)
async def get_my_tutor_profile(
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's tutor profile
    
    Requires: Valid authentication
    Returns: Tutor profile or 404 if not registered
    """
    profile = await tutor_service.get_tutor_by_user_id(current_user.user_id)
    if not profile:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor profile not found. Please register first."
        )
    return profile


@router.post("/register", response_model=TutorResponse)
async def register_tutor(
    tutor_data: TutorCreate,
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Register as tutor for specific subjects
    
    Request body:
    - user_id: User ID (auto-filled with current_user)
    - subjects: List of subject codes
    - bio: Tutor introduction
    - hourly_rate: Hourly rate in VND
    - experience_years: Years of experience
    
    Returns: Tutor profile
    """
    # Override user_id with current user for security
    tutor_data.user_id = current_user.user_id
    return await tutor_service.register_tutor(tutor_data)


@router.get("/{tutor_id}", response_model=TutorResponse)
async def get_tutor(
    tutor_id: int,
    tutor_service: TutorService = Depends(get_tutor_service)
):
    """Get specific tutor details"""
    return await tutor_service.get_tutor(tutor_id)


@router.put("/{tutor_id}", response_model=TutorResponse)
async def update_tutor(
    tutor_id: int,
    tutor_data: TutorUpdate,
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update tutor profile
    
    Requires: The tutor themselves or admin
    """
    # TODO: Add permission check
    return await tutor_service.update_tutor(tutor_id, tutor_data)


@router.delete("/{tutor_id}")
async def delete_tutor(
    tutor_id: int,
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Delete tutor profile
    
    Requires: Admin only
    """
    # TODO: Add admin permission check
    await tutor_service.delete_tutor(tutor_id)
    return {"message": "Tutor profile deleted successfully"}


# ============================================================================
# PLACEHOLDER ENDPOINTS - Keep original placeholder implementations
# ============================================================================

@router.get("/sessions")
async def get_tutor_sessions():
    """
    Get all sessions for current tutor - PLACEHOLDER
    
    TODO:
    - Filter by status (scheduled, completed, cancelled)
    - Include student info and session details
    - Support date range filtering
    
    Returns: List of tutoring sessions
    """
    return {"message": "Get tutor sessions - Implementation pending"}


@router.post("/availability")
async def set_availability():
    """
    Set or update tutor's available time slots - PLACEHOLDER
    
    TODO:
    - Accept weekly recurring schedule
    - Support one-time availability
    - Prevent conflicts with existing sessions
    - Validate time format
    
    Request body:
    - day_of_week: 0-6 (Monday-Sunday)
    - start_time: HH:MM format
    - end_time: HH:MM format
    - is_recurring: Boolean
    
    Returns: Updated availability schedule
    """
    return {"message": "Set availability - Implementation pending"}


@router.get("/{tutor_id}/reviews")
async def get_tutor_reviews(tutor_id: int):
    """
    Get reviews and ratings for specific tutor - PLACEHOLDER
    
    TODO:
    - Aggregate ratings from completed sessions
    - Include student feedback
    - Calculate average rating
    - Support pagination
    
    Returns: List of reviews with ratings and comments
    """
    return {"message": f"Get reviews for tutor {tutor_id} - Implementation pending"}

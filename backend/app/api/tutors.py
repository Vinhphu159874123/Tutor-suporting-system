"""
Tutor Routes - Layered Architecture
Routes delegate to TutorService - PLACEHOLDER implementations preserved
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime

from app.schemas.tutor import TutorCreate, TutorUpdate, TutorResponse
from app.schemas.session import SessionListResponse
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


# ============================================================================
# SPECIFIC ROUTES - Must come BEFORE dynamic routes like /{tutor_id}
# ============================================================================

@router.get("/sessions", response_model=SessionListResponse)
async def get_tutor_sessions(
    status: Optional[str] = Query(None, description="Filter by status: draft, published, confirmed, etc."),
    start_date: Optional[datetime] = Query(None, description="Filter sessions from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter sessions until this date"),
    skip: int = Query(0, ge=0, description="Skip N records for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Max records to return"),
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all sessions for current tutor - NOW SUPPORTS MULTIPLE STUDENTS
    
    Features:
    - Filter by status (draft, published, confirmed, ongoing, completed, cancelled)
    - Include all students info for each session
    - Support date range filtering
    - Pagination support
    
    Returns: List of tutoring sessions with tutor and students info
    """
    # Get tutor profile to get tutor_user_id
    tutor_profile = await tutor_service.get_tutor_by_user_id(current_user.user_id)
    if not tutor_profile:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Tutor profile not found"
        )
    
    return await tutor_service.get_tutor_sessions(
        tutor_user_id=current_user.user_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )


# ============================================================================
# DYNAMIC ROUTES - Must come AFTER specific routes
# ============================================================================

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

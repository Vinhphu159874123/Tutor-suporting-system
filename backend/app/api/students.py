"""
Student Routes - Layered Architecture
Routes delegate to StudentService
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.schemas.student import (
    StudentCreate,
    StudentUpdate, 
    StudentResponse,
    TutorRequestCreate,
    SessionFeedbackCreate
)
from app.services.student_service import StudentService
from app.core.dependencies import get_student_service, get_current_user
from app.models.database import User

router = APIRouter()

# ============================================================================
# STUDENT ENDPOINTS - Layered Architecture
# ============================================================================

@router.get("/", response_model=List[StudentResponse])
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    year: Optional[int] = Query(None, ge=1, le=5),
    is_active: Optional[bool] = None,
    student_service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all students in the tutoring program
    
    Requires: Admin/Coordinator permissions
    Filters: year (1-5), is_active
    """
    # TODO: Add permission check for admin/coordinator
    return await student_service.get_all_students(
        skip=skip,
        limit=limit,
        year=year,
        is_active=is_active
    )


@router.get("/me", response_model=StudentResponse)
async def get_my_student_profile(
    student_service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's student profile
    
    Requires: Valid authentication
    Returns: Student profile or 404 if not registered
    """
    profile = await student_service.get_student_by_user_id(current_user.user_id)
    if not profile:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please register first."
        )
    return profile


@router.post("/register", response_model=StudentResponse)
async def register_student(
    student_data: StudentCreate,
    student_service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user)
):
    """
    Register as student in tutoring program
    
    Request body:
    - user_id: User ID to register (usually current_user.id)
    - subjects_needed: List of subjects needing help
    - learning_goals: Description of learning goals
    - year: Year of study (1-5)
    - preferred_schedule: Preferred time slots
    
    Returns: Student profile
    """
    # Override user_id with current user for security
    student_data.user_id = current_user.user_id
    return await student_service.register_student(student_data)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    student_service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific student details
    
    Requires: Admin or the student themselves
    """
    # TODO: Add permission check (admin or self)
    return await student_service.get_student(student_id)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    student_service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update student profile
    
    Requires: The student themselves or admin
    """
    # TODO: Add permission check
    return await student_service.update_student(student_id, student_data)


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    student_service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user)
):
    """
    Delete student profile
    
    Requires: Admin only
    """
    # TODO: Add admin permission check
    await student_service.delete_student(student_id)
    return {"message": "Student profile deleted successfully"}


@router.post("/{student_id}/request-tutor")
async def request_tutor(
    student_id: int,
    request_data: TutorRequestCreate,
    student_service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user)
):
    """
    Request a tutor for specific subject
    
    Request body:
    - subject: Subject needing help
    - description: Description of help needed
    - urgency: normal, high, urgent
    
    Returns: Tutor request confirmation
    """
    # TODO: Add permission check (student themselves)
    return await student_service.request_tutor(student_id, request_data)


@router.post("/{student_id}/feedback")
async def submit_feedback(
    student_id: int,
    feedback_data: SessionFeedbackCreate,
    student_service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback after session
    
    Request body:
    - session_id: ID of completed session
    - rating: Rating 1-5
    - comment: Optional comment
    - would_recommend: Boolean
    
    Returns: Feedback confirmation
    """
    # TODO: Add permission check (student themselves)
    return await student_service.submit_feedback(student_id, feedback_data)

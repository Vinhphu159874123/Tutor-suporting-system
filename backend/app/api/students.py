"""
Student Routes - Layered Architecture
Routes delegate to StudentService
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
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


@router.get("/by-user/{user_id}", response_model=StudentResponse)
async def get_student_by_user_id(
    user_id: int,
    student_service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get student details by user_id
    
    Accessible by: Tutors, Coordinators, Admin, or the student themselves
    """
    profile = await student_service.get_student_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    return profile


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
    - tags: Optional tags list
    - is_anonymous: Boolean (default: False)
    
    Returns: Feedback confirmation
    """
    return await student_service.submit_feedback(student_id, feedback_data)


@router.get("/{student_id}/enrolled-courses")
async def get_student_enrolled_courses(
    student_id: int,
    student_service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all courses/subjects the student is enrolled in
    Returns list of subjects with session counts and tutor info
    
    Accessible by: Tutors, Coordinators, Admin, or the student themselves
    """
    from app.models.database import Student, Session, SessionParticipant, Subject, Tutor, User as DBUser
    from sqlalchemy import select, func
    from sqlalchemy.ext.asyncio import AsyncSession
    
    # Get student's user_id
    student_result = await student_service.student_repo.db.execute(
        select(Student).where(Student.student_id == student_id)
    )
    student = student_result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # OPTIMIZATION: Get all data in ONE query with JOIN instead of N queries
    subjects_result = await student_service.student_repo.db.execute(
        select(
            Subject,
            Session.tutor_id,
            func.count(Session.session_id).label('session_count'),
            func.count(SessionParticipant.participant_id).label('enrolled_sessions'),
            DBUser.full_name.label('tutor_name'),
            DBUser.email.label('tutor_email')
        )
        .join(Session, Subject.subject_id == Session.subject_id)
        .join(SessionParticipant, Session.session_id == SessionParticipant.session_id)
        .join(Tutor, Session.tutor_id == Tutor.tutor_id)
        .join(DBUser, Tutor.user_id == DBUser.user_id)
        .where(SessionParticipant.user_id == student.user_id)
        .where(SessionParticipant.role == 'student')
        .group_by(Subject.subject_id, Session.tutor_id, DBUser.full_name, DBUser.email)
    )
    results = subjects_result.all()
    
    courses = []
    for subject, tutor_id, session_count, enrolled_sessions, tutor_name, tutor_email in results:
        courses.append({
            "subject_id": subject.subject_id,
            "subject_code": subject.subject_code,
            "subject_name": subject.subject_name,
            "department": subject.department,
            "credits": subject.credits,
            "total_sessions": session_count,
            "enrolled_sessions": enrolled_sessions,
            "tutor_id": tutor_id,
            "tutor_name": tutor_name,
            "tutor_email": tutor_email
        })
    
    return {
        "student_id": student_id,
        "user_id": student.user_id,
        "courses": courses,
        "total_courses": len(courses)
    }

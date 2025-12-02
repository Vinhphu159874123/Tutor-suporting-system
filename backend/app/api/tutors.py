"""
Tutor Routes - Layered Architecture
Routes delegate to TutorService - PLACEHOLDER implementations preserved
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.tutor import TutorCreate, TutorUpdate, TutorResponse, TutorRegistrationCreate, TutorRegistrationResponse
from app.schemas.session import SessionListResponse
from app.services.tutor_service import TutorService
from app.core.dependencies import get_tutor_service, get_current_user, get_db
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
    Create or update tutor profile (without subject registration)
    
    This creates the general tutor profile with bio, faculty, availability, etc.
    After creating profile, use /register-subject to register for specific subjects.
    
    Request body:
    - bio: Tutor introduction
    - faculty: Faculty name
    - hourly_rate: Hourly rate in VND
    - experience_years: Years of experience
    - availability: Weekly availability slots
    
    Returns: Tutor profile
    """
    # Override user_id with current user for security
    tutor_data.user_id = current_user.user_id
    return await tutor_service.register_tutor(tutor_data)


@router.post("/register-subject", response_model=TutorRegistrationResponse)
async def register_subject(
    registration_data: TutorRegistrationCreate,
    tutor_service: TutorService = Depends(get_tutor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Register for teaching a specific subject
    
    Requires existing tutor profile. Creates a TutorRegistration entry.
    Each registration is for ONE subject and requires coordinator approval.
    
    Request body:
    - subject_id: ID of the subject to teach
    - gpa: Your GPA for this subject (optional)
    - qualifications: Teaching qualifications for this subject (optional)
    - availability: Weekly availability for this subject (optional)
    
    Returns: TutorRegistration with status 'pending'
    """
    return await tutor_service.register_subject(current_user.user_id, registration_data)


@router.get("/my-registrations")
async def get_my_registrations(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all subject registrations for current tutor
    
    Returns list of TutorRegistration with subject info, availability, and schedule details
    """
    from app.models.database import Tutor, TutorRegistration, Subject
    from sqlalchemy import select
    
    # Get tutor record
    tutor_result = await db.execute(
        select(Tutor).where(Tutor.user_id == current_user.user_id)
    )
    tutor = tutor_result.scalar_one_or_none()
    
    if not tutor:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Tutor profile not found"
        )
    
    # Build query
    query = select(TutorRegistration, Subject).join(
        Subject, TutorRegistration.subject_id == Subject.subject_id
    ).where(TutorRegistration.tutor_id == tutor.tutor_id)
    
    if status:
        query = query.where(TutorRegistration.status == status)
    
    result = await db.execute(query)
    registrations = result.all()
    
    return [
        {
            "registration_id": reg.TutorRegistration.registration_id,
            "subject_id": reg.TutorRegistration.subject_id,
            "subject_code": reg.Subject.subject_code,
            "subject_name": reg.Subject.subject_name,
            "status": reg.TutorRegistration.status,
            "gpa": reg.TutorRegistration.gpa,
            "qualifications": reg.TutorRegistration.qualifications,
            "availability": reg.TutorRegistration.availability,
            "total_sessions": reg.TutorRegistration.total_sessions,
            "start_date": reg.TutorRegistration.start_date.isoformat() if reg.TutorRegistration.start_date else None,
            "end_date": reg.TutorRegistration.end_date.isoformat() if reg.TutorRegistration.end_date else None,
            "registered_at": reg.TutorRegistration.registered_at.isoformat() if reg.TutorRegistration.registered_at else None,
            "max_students": reg.TutorRegistration.max_students
        }
        for reg in registrations
    ]


# ============================================================================
# SPECIFIC ROUTES - Must come BEFORE dynamic routes like /{tutor_id}
# ============================================================================

@router.get("/available-courses")
async def get_available_courses(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all approved tutor registrations with available slots for students to browse
    (Public endpoint - no authentication required)
    
    Returns:
    - registration_id: ID of the tutor registration
    - subject details: code, name, department
    - tutor details: name
    - capacity: max_students, current_students, available_slots
    - session info: total_sessions, start_date
    """
    from sqlalchemy import select, func
    from app.models.database import TutorRegistration, Subject, Tutor, Session, SessionParticipant, User
    
    # Get approved registrations with course details
    query = (
        select(
            TutorRegistration.registration_id,
            TutorRegistration.subject_id,
            TutorRegistration.tutor_id,
            TutorRegistration.max_students,
            TutorRegistration.status,
            Subject.subject_code,
            Subject.subject_name,
            Subject.department,
            User.full_name.label("tutor_name"),
        )
        .join(Subject, TutorRegistration.subject_id == Subject.subject_id)
        .join(Tutor, TutorRegistration.tutor_id == Tutor.tutor_id)
        .join(User, Tutor.user_id == User.user_id)
        .where(TutorRegistration.status == "approved")
    )
    
    result = await db.execute(query)
    registrations = result.all()
    
    courses = []
    for reg in registrations:
        # Count sessions for this registration
        session_count_query = select(func.count(Session.session_id)).where(
            Session.subject_id == reg.subject_id,
            Session.tutor_id == reg.tutor_id
        )
        session_count = await db.scalar(session_count_query)
        
        # Get earliest session date
        start_date_query = select(func.min(Session.scheduled_date)).where(
            Session.subject_id == reg.subject_id,
            Session.tutor_id == reg.tutor_id
        )
        start_date = await db.scalar(start_date_query)
        
        # Count current students (participants with role='student' across all sessions)
        # Using DISTINCT to count unique students
        student_count_query = (
            select(func.count(func.distinct(SessionParticipant.user_id)))
            .join(Session, SessionParticipant.session_id == Session.session_id)
            .where(
                Session.subject_id == reg.subject_id,
                Session.tutor_id == reg.tutor_id,
                SessionParticipant.role == "student"
            )
        )
        current_students = await db.scalar(student_count_query) or 0
        
        available_slots = reg.max_students - current_students
        
        # Only include courses with at least 1 session
        if session_count and session_count > 0:
            courses.append({
                "registration_id": reg.registration_id,
                "subject_id": reg.subject_id,
                "subject_code": reg.subject_code,
                "subject_name": reg.subject_name,
                "department": reg.department,
                "tutor_id": reg.tutor_id,
                "tutor_name": reg.tutor_name,
                "total_sessions": session_count,
                "max_students": reg.max_students,
                "current_students": current_students,
                "available_slots": max(0, available_slots),
                "start_date": start_date.isoformat() if start_date else None,
                "status": reg.status
            })
    
    return {"data": courses}


@router.post("/courses/{registration_id}/request-join")
async def request_join_course(
    registration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Student requests to join a course
    
    - Validates registration exists and is approved
    - Checks available slots
    - Adds student to all sessions for the course
    - Sends notification to tutor
    """
    from sqlalchemy import select, and_, func
    from app.models.database import TutorRegistration, Session, SessionParticipant, Tutor, Subject
    from app.events import event_bus, EventTypes
    
    # Get registration details
    reg_query = (
        select(TutorRegistration, Subject.subject_name, Tutor)
        .join(Subject, TutorRegistration.subject_id == Subject.subject_id)
        .join(Tutor, TutorRegistration.tutor_id == Tutor.tutor_id)
        .where(TutorRegistration.registration_id == registration_id)
    )
    reg_result = await db.execute(reg_query)
    reg_data = reg_result.first()
    
    if not reg_data:
        raise HTTPException(status_code=404, detail="Course registration not found")
    
    registration, subject_name, tutor = reg_data
    
    if registration.status != "approved":
        raise HTTPException(status_code=400, detail="Course is not approved yet")
    
    # Count current students
    student_count_query = (
        select(func.count(func.distinct(SessionParticipant.user_id)))
        .join(Session, SessionParticipant.session_id == Session.session_id)
        .where(
            Session.subject_id == registration.subject_id,
            Session.tutor_id == registration.tutor_id,
            SessionParticipant.role == "student"
        )
    )
    current_students = await db.scalar(student_count_query) or 0
    
    if current_students >= registration.max_students:
        raise HTTPException(status_code=400, detail="Course is full")
    
    # Check if student already joined
    check_query = (
        select(SessionParticipant)
        .join(Session, SessionParticipant.session_id == Session.session_id)
        .where(
            Session.subject_id == registration.subject_id,
            Session.tutor_id == registration.tutor_id,
            SessionParticipant.user_id == current_user.user_id,
            SessionParticipant.role == "student"
        )
    )
    existing = await db.scalar(check_query)
    
    if existing:
        raise HTTPException(status_code=400, detail="You have already joined this course")
    
    # Get all sessions for this course
    sessions_query = select(Session).where(
        Session.subject_id == registration.subject_id,
        Session.tutor_id == registration.tutor_id
    )
    sessions_result = await db.execute(sessions_query)
    sessions = sessions_result.scalars().all()
    
    if not sessions:
        raise HTTPException(status_code=400, detail="No sessions available for this course")
    
    # Add student to all sessions
    for session in sessions:
        participant = SessionParticipant(
            session_id=session.session_id,
            user_id=current_user.user_id,
            role="student",
            status="confirmed"
        )
        db.add(participant)
    
    await db.commit()
    
    # Emit event for notification
    await event_bus.emit(EventTypes.STUDENT_ENROLLED_COURSE, {
        'student_id': current_user.user_id,
        'student_name': current_user.full_name,
        'tutor_id': tutor.tutor_id,
        'subject_id': registration.subject_id,
        'subject_name': subject_name,
        'sessions_count': len(sessions)
    })
    
    return {
        "message": f"Successfully joined {subject_name}",
        "sessions_joined": len(sessions)
    }


@router.get("/courses/enrolled-students")
async def get_enrolled_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of students enrolled in tutor's courses
    Returns students grouped by course
    """
    from sqlalchemy import select, func, distinct
    from app.models.database import Tutor, TutorRegistration, Subject, Session, SessionParticipant
    
    # Get tutor_id from current user
    tutor_query = select(Tutor).where(Tutor.user_id == current_user.user_id)
    result = await db.execute(tutor_query)
    tutor = result.scalar_one_or_none()
    
    if not tutor:
        raise HTTPException(status_code=403, detail="Only tutors can access this endpoint")
    
    # Get all approved registrations for this tutor
    reg_query = (
        select(TutorRegistration, Subject)
        .join(Subject, TutorRegistration.subject_id == Subject.subject_id)
        .where(
            TutorRegistration.tutor_id == tutor.tutor_id,
            TutorRegistration.status == "approved"
        )
    )
    reg_result = await db.execute(reg_query)
    registrations = reg_result.all()
    
    courses = []
    
    for registration, subject in registrations:
        # Get all students enrolled in sessions for this course
        students_query = (
            select(
                User.user_id,
                User.full_name,
                User.email,
                func.count(distinct(SessionParticipant.session_id)).label('sessions_count')
            )
            .select_from(SessionParticipant)
            .join(Session, SessionParticipant.session_id == Session.session_id)
            .join(User, SessionParticipant.user_id == User.user_id)
            .where(
                Session.subject_id == registration.subject_id,
                Session.tutor_id == tutor.tutor_id,
                SessionParticipant.role == "student"
            )
            .group_by(User.user_id, User.full_name, User.email)
        )
        
        students_result = await db.execute(students_query)
        students = students_result.all()
        
        if students:  # Only include courses with students
            courses.append({
                "registration_id": registration.registration_id,
                "subject_id": subject.subject_id,
                "subject_code": subject.subject_code,
                "subject_name": subject.subject_name,
                "total_sessions": registration.total_sessions,
                "max_students": registration.max_students,
                "enrolled_count": len(students),
                "students": [
                    {
                        "user_id": s.user_id,
                        "full_name": s.full_name,
                        "email": s.email,
                        "sessions_enrolled": s.sessions_count
                    }
                    for s in students
                ]
            })
    
    return {"data": courses}


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


@router.get("/{tutor_id}/availability")
async def get_tutor_availability(
    tutor_id: int,
    tutor_service: TutorService = Depends(get_tutor_service)
):
    """Get tutor's available time slots"""
    return await tutor_service.get_tutor_availability(tutor_id)


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
# REVIEW ENDPOINTS
# ============================================================================

@router.get("/{tutor_id}/reviews")
async def get_tutor_reviews(
    tutor_id: int,
    skip: int = 0,
    limit: int = 20,
    tutor_service: TutorService = Depends(get_tutor_service)
):
    """
    Get reviews and ratings for specific tutor
    
    Query params:
    - skip: Number of reviews to skip (default: 0)
    - limit: Max number of reviews to return (default: 20, max: 100)
    
    Returns:
    - tutor_id: ID of the tutor
    - statistics: Average rating, total reviews, unique reviewers
    - reviews: List of feedback with ratings and comments
    - pagination: Skip, limit, total count
    """
    if limit > 100:
        limit = 100
    
    return await tutor_service.get_tutor_reviews(tutor_id, skip, limit)


# ============================================================================
# PLACEHOLDER ENDPOINTS
# ============================================================================

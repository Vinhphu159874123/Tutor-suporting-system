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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all approved tutor registrations with available slots for students to browse
    Only shows courses that the current user has NOT joined yet
    
    Returns:
    - registration_id: ID of the tutor registration
    - subject details: code, name, department
    - tutor details: name
    - capacity: max_students, current_students, available_slots
    - session info: total_sessions, start_date
    """
    from sqlalchemy import select, func
    from app.models.database import TutorRegistration, Subject, Tutor, Session, SessionParticipant, User
    
    # Get approved registrations with course details (including total_sessions)
    query = (
        select(
            TutorRegistration.registration_id,
            TutorRegistration.subject_id,
            TutorRegistration.tutor_id,
            TutorRegistration.max_students,
            TutorRegistration.total_sessions,
            TutorRegistration.start_date,
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
    
    # Get all courses the current user has already joined
    joined_courses_query = (
        select(Session.subject_id, Session.tutor_id)
        .join(SessionParticipant, SessionParticipant.session_id == Session.session_id)
        .where(
            SessionParticipant.user_id == current_user.user_id,
            SessionParticipant.role == "student"
        )
        .distinct()
    )
    joined_result = await db.execute(joined_courses_query)
    joined_courses = set((row.subject_id, row.tutor_id) for row in joined_result.all())
    
    # OPTIMIZATION: Get all session stats in ONE query instead of N queries
    from sqlalchemy.orm import aliased
    from app.models.database import SessionFeedback
    
    # Get session counts, start dates, student counts for all registrations at once
    session_stats_query = (
        select(
            Session.subject_id,
            Session.tutor_id,
            func.count(func.distinct(Session.session_id)).label('session_count'),
            func.min(Session.scheduled_date).label('start_date'),
            func.count(func.distinct(SessionParticipant.user_id)).label('student_count')
        )
        .outerjoin(SessionParticipant, 
            (SessionParticipant.session_id == Session.session_id) & 
            (SessionParticipant.role == "student")
        )
        .group_by(Session.subject_id, Session.tutor_id)
    )
    stats_result = await db.execute(session_stats_query)
    session_stats = {
        (row.subject_id, row.tutor_id): {
            'session_count': row.session_count,
            'start_date': row.start_date,
            'student_count': row.student_count or 0
        }
        for row in stats_result.all()
    }
    
    # Get rating stats for all courses in ONE query
    rating_stats_query = (
        select(
            Session.subject_id,
            Session.tutor_id,
            func.avg(SessionFeedback.rating).label('avg_rating'),
            func.count(SessionFeedback.feedback_id).label('feedback_count')
        )
        .join(Session, SessionFeedback.session_id == Session.session_id)
        .group_by(Session.subject_id, Session.tutor_id)
    )
    rating_result = await db.execute(rating_stats_query)
    rating_stats = {
        (row.subject_id, row.tutor_id): {
            'avg_rating': float(row.avg_rating) if row.avg_rating else 0.0,
            'feedback_count': row.feedback_count or 0
        }
        for row in rating_result.all()
    }
    
    courses = []
    for reg in registrations:
        # Skip courses that user has already joined
        if (reg.subject_id, reg.tutor_id) in joined_courses:
            continue
        
        # Get pre-computed stats
        stats = session_stats.get((reg.subject_id, reg.tutor_id))
        ratings = rating_stats.get((reg.subject_id, reg.tutor_id), {'avg_rating': 0.0, 'feedback_count': 0})
        
        if stats and stats['session_count'] > 0:
            # Use actual sessions from database
            total_sessions_display = stats['session_count']
            start_date_display = stats['start_date']
            current_students = stats['student_count']
        else:
            # No sessions saved yet - use planned sessions from registration
            total_sessions_display = reg.total_sessions or 0
            start_date_display = reg.start_date
            current_students = 0
        
        available_slots = reg.max_students - current_students
        
        # Only include courses that have planned sessions
        if total_sessions_display > 0:
            courses.append({
                "registration_id": reg.registration_id,
                "subject_id": reg.subject_id,
                "subject_code": reg.subject_code,
                "subject_name": reg.subject_name,
                "department": reg.department,
                "tutor_id": reg.tutor_id,
                "tutor_name": reg.tutor_name,
                "total_sessions": total_sessions_display,
                "max_students": reg.max_students,
                "current_students": current_students,
                "available_slots": max(0, available_slots),
                "start_date": start_date_display.isoformat() if start_date_display else None,
                "status": reg.status,
                "average_rating": round(ratings['avg_rating'], 1),
                "total_feedbacks": ratings['feedback_count']
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
    import logging
    logger = logging.getLogger(__name__)
    event_data = {
        'student_id': current_user.user_id,
        'student_name': current_user.full_name,
        'tutor_id': tutor.tutor_id,
        'subject_id': registration.subject_id,
        'subject_name': subject_name,
        'sessions_count': len(sessions)
    }
    logger.info(f"🔔 Emitting STUDENT_ENROLLED_COURSE event: {event_data}")
    await event_bus.emit(EventTypes.STUDENT_ENROLLED_COURSE, event_data)
    logger.info(f"✅ Event emitted successfully")
    
    return {
        "message": f"Successfully joined {subject_name}",
        "sessions_joined": len(sessions)
    }


@router.post("/courses/{subject_id}/generate-sessions")
async def generate_sessions_for_course(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate sessions for an approved course based on tutor's registered schedule
    
    This endpoint allows tutors to manually generate sessions after their course is approved.
    Sessions are generated based on:
    - The schedule registered during course registration
    - Total number of sessions specified in registration
    - Start date and max students from registration
    
    Returns:
    - message: Success message
    - generated_count: Number of sessions created
    """
    from sqlalchemy import select, func
    from app.models.database import Tutor, TutorRegistration, SessionSchedule, Session, Subject
    from datetime import datetime, timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Get tutor profile
    tutor_query = select(Tutor).where(Tutor.user_id == current_user.user_id)
    tutor_result = await db.execute(tutor_query)
    tutor = tutor_result.scalar_one_or_none()
    
    if not tutor:
        raise HTTPException(status_code=403, detail="Only tutors can generate sessions")
    
    # Get registration for this subject
    reg_query = select(TutorRegistration).where(
        TutorRegistration.tutor_id == tutor.tutor_id,
        TutorRegistration.subject_id == subject_id
    )
    reg_result = await db.execute(reg_query)
    registration = reg_result.scalar_one_or_none()
    
    if not registration:
        raise HTTPException(status_code=404, detail="Course registration not found")
    
    if registration.status != "approved":
        raise HTTPException(status_code=400, detail="Course must be approved before generating sessions")
    
    # Check if sessions already exist
    existing_sessions_result = await db.execute(
        select(func.count(Session.session_id)).where(
            Session.tutor_id == tutor.tutor_id,
            Session.subject_id == subject_id
        )
    )
    existing_count = existing_sessions_result.scalar() or 0
    
    if existing_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Sessions already exist for this course ({existing_count} sessions). Delete them first if you want to regenerate."
        )
    
    # Get schedule - use selected_schedule_id if available, otherwise first active schedule
    if registration.selected_schedule_id:
        schedule_query = select(SessionSchedule).where(
            SessionSchedule.schedule_id == registration.selected_schedule_id
        )
    else:
        schedule_query = select(SessionSchedule).where(
            SessionSchedule.tutor_id == tutor.tutor_id,
            SessionSchedule.subject_id == subject_id,
            SessionSchedule.is_active == True
        )
    
    schedule_result = await db.execute(schedule_query)
    schedule = schedule_result.scalars().first()  # Get first active schedule instead of expecting only one
    
    if not schedule:
        raise HTTPException(
            status_code=400, 
            detail="No active schedule found. Please set up your schedule first."
        )
    
    # Get subject name
    subject_query = select(Subject).where(Subject.subject_id == subject_id)
    subject_result = await db.execute(subject_query)
    subject = subject_result.scalar_one_or_none()
    subject_name = subject.subject_name if subject else "Unknown Subject"
    
    # Determine start date
    start_date = registration.start_date if registration.start_date else datetime.now().date()
    current_date = start_date
    day_of_week = schedule.day_of_week
    
    # Advance to the first matching day
    while current_date.weekday() != day_of_week:
        current_date += timedelta(days=1)
    
    # Generate sessions
    total_sessions = registration.total_sessions or 10
    max_students = registration.max_students or 5
    
    logger.info(f"Generating {total_sessions} sessions for tutor {tutor.tutor_id}, subject {subject_id}")
    
    for i in range(total_sessions):
        session = Session(
            tutor_id=tutor.tutor_id,
            subject_id=subject_id,
            title=f"{subject_name} - Session {i+1}",
            description=schedule.description or f"Tutoring session for {subject_name}",
            scheduled_date=current_date,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            duration=schedule.duration,
            location_type=schedule.location_type or 'online',
            meeting_link=None,
            physical_address=None,
            max_students=max_students,
            status='draft'
        )
        db.add(session)
        
        # Move to next week (same day)
        current_date += timedelta(weeks=1)
    
    await db.commit()
    
    logger.info(f"✅ Successfully generated {total_sessions} sessions")
    
    return {
        "message": f"Successfully generated {total_sessions} sessions",
        "generated_count": total_sessions,
        "start_date": start_date.isoformat(),
        "schedule": {
            "day_of_week": schedule.day_of_week,
            "start_time": str(schedule.start_time),
            "end_time": str(schedule.end_time)
        }
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

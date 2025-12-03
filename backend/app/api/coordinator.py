"""
Coordinator API Routes
Endpoints for coordinator approval workflows
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import aliased
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
import io
import csv

from app.core.dependencies import get_current_user, get_db
from app.models.database import User, TutorRegistration, Tutor, Subject, Session as SessionModel, Student, Notifications
from app.events import event_bus

router = APIRouter()

# Helper function to check if user has coordinator or admin role
def check_coordinator_permission(user: User):
    """Check if user has coordinator or admin role (supports array)"""
    user_roles = user.role if isinstance(user.role, list) else [user.role]
    if 'coordinator' not in user_roles and 'admin' not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coordinators can access this endpoint"
        )

# ============================================================================
# TUTOR REGISTRATION APPROVAL
# ============================================================================

@router.get("/tutor-registrations")
async def get_pending_tutor_registrations(
    status_filter: str = "pending",
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get tutor registrations for approval
    
    Requires: Coordinator role
    """
    check_coordinator_permission(current_user)
    
    # Query with joins to get tutor and subject info
    query = (
        select(TutorRegistration, Tutor, User, Subject)
        .join(Tutor, TutorRegistration.tutor_id == Tutor.tutor_id)
        .join(User, Tutor.user_id == User.user_id)
        .join(Subject, TutorRegistration.subject_id == Subject.subject_id)
        .where(TutorRegistration.status == status_filter)
        .order_by(TutorRegistration.registered_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    registrations = []
    for reg, tutor, user, subject in rows:
        # Get availability from notification data
        notif_query = (
            select(Notifications)
            .where(
                and_(
                    Notifications.type == "subject_registration",
                    Notifications.data['registration_id'].astext == str(reg.registration_id)
                )
            )
            .order_by(Notifications.created_at.desc())
            .limit(1)
        )
        notif_result = await db.execute(notif_query)
        notification = notif_result.scalar_one_or_none()
        
        availability = None
        if notification and notification.data and 'availability' in notification.data:
            availability = notification.data['availability']
        
        # Get selected schedule info for approved registrations
        selected_schedule = None
        if reg.status == "approved":
            from app.models.database import SessionSchedule, Session
            # Try to find schedule from first session
            session_query = (
                select(Session)
                .where(
                    Session.tutor_id == reg.tutor_id,
                    Session.subject_id == reg.subject_id
                )
                .limit(1)
            )
            session_result = await db.execute(session_query)
            first_session = session_result.scalar_one_or_none()
            
            if first_session:
                # Match schedule by day, time - use .first() instead of .scalar_one_or_none() to handle multiple schedules
                schedule_query = (
                    select(SessionSchedule)
                    .where(
                        SessionSchedule.tutor_id == reg.tutor_id,
                        SessionSchedule.subject_id == reg.subject_id,
                        SessionSchedule.start_time == first_session.start_time,
                        SessionSchedule.end_time == first_session.end_time
                    )
                    .limit(1)
                )
                schedule_result = await db.execute(schedule_query)
                schedule = schedule_result.scalar_one_or_none()
                
                if schedule:
                    day_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
                    selected_schedule = {
                        "schedule_id": schedule.schedule_id,
                        "day_of_week": schedule.day_of_week,
                        "day_name": day_names[schedule.day_of_week],
                        "start_time": str(schedule.start_time),
                        "end_time": str(schedule.end_time),
                        "location_type": schedule.location_type
                    }
        
        registrations.append({
            "registration_id": reg.registration_id,
            "tutor_id": reg.tutor_id,
            "tutor_name": user.full_name,
            "tutor_email": user.email,
            "tutor_bio": tutor.bio,
            "subject_id": reg.subject_id,
            "subject_name": subject.subject_name,
            "subject_code": subject.subject_code,
            "gpa": float(reg.gpa) if reg.gpa else None,
            "qualifications": reg.qualifications,
            "status": reg.status,
            "registered_at": reg.registered_at,
            "responded_at": reg.responded_at,
            "rejection_reason": reg.rejection_reason,
            "availability": availability,
            "total_sessions": reg.total_sessions,
            "start_date": reg.start_date.isoformat() if reg.start_date else None,
            "end_date": reg.end_date.isoformat() if reg.end_date else None,
            "max_students": reg.max_students,
            "selected_schedule": selected_schedule
        })
    
    return registrations


@router.get("/tutor-registrations/{registration_id}/schedules")
async def get_registration_schedules(
    registration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all schedules for a tutor registration
    Returns list of schedules the coordinator can choose from
    """
    check_coordinator_permission(current_user)
    
    # Get the registration
    from app.models.database import SessionSchedule
    
    reg_query = select(TutorRegistration).where(TutorRegistration.registration_id == registration_id)
    reg_result = await db.execute(reg_query)
    registration = reg_result.scalar_one_or_none()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )
    
    # Get all active schedules for this registration
    schedules_query = select(SessionSchedule).where(
        SessionSchedule.tutor_id == registration.tutor_id,
        SessionSchedule.subject_id == registration.subject_id,
        SessionSchedule.is_active == True
    )
    schedules_result = await db.execute(schedules_query)
    schedules = schedules_result.scalars().all()
    
    # Format schedule data
    day_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
    
    return [
        {
            "schedule_id": schedule.schedule_id,
            "day_of_week": schedule.day_of_week,
            "day_name": day_names[schedule.day_of_week],
            "start_time": str(schedule.start_time),
            "end_time": str(schedule.end_time),
            "duration": schedule.duration,
            "location_type": schedule.location_type,
            "description": schedule.description
        }
        for schedule in schedules
    ]


class ApprovalRequest(BaseModel):
    schedule_id: Optional[int] = None

@router.put("/tutor-registrations/{registration_id}/approve")
async def approve_tutor_registration(
    registration_id: int,
    approval_data: ApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a tutor registration
    
    Requires: Coordinator role
    Body: { schedule_id?: number } - Optional schedule to use for session generation
    """
    check_coordinator_permission(current_user)
    
    # Get the registration
    query = select(TutorRegistration).where(TutorRegistration.registration_id == registration_id)
    result = await db.execute(query)
    registration = result.scalar_one_or_none()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )
    
    if registration.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration is already {registration.status}"
        )
    
    # Get coordinator_id from current_user
    from app.models.database import Coordinator
    coord_query = select(Coordinator).where(Coordinator.user_id == current_user.user_id)
    coord_result = await db.execute(coord_query)
    coordinator = coord_result.scalar_one_or_none()
    
    if not coordinator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coordinator profile not found"
        )
    
    # Update registration
    registration.status = 'approved'
    registration.approved_by = coordinator.coordinator_id
    registration.responded_at = datetime.utcnow()
    
    # Save selected schedule if provided
    if approval_data.schedule_id:
        registration.selected_schedule_id = approval_data.schedule_id
    
    await db.commit()
    await db.refresh(registration)
    
    # Get tutor user_id for event emission
    tutor_query = select(Tutor).where(Tutor.tutor_id == registration.tutor_id)
    tutor_result = await db.execute(tutor_query)
    tutor = tutor_result.scalar_one_or_none()
    
    if tutor:
        # Get subject name for event
        subject_query = select(Subject).where(Subject.subject_id == registration.subject_id)
        subject_result = await db.execute(subject_query)
        subject = subject_result.scalar_one_or_none()
        
        subject_name = subject.subject_name if subject else "môn học"
        
        # Emit event for real-time notification (listener will create notification and generate sessions)
        from app.events import EventTypes
        await event_bus.emit(EventTypes.REGISTRATION_APPROVED, {
            'user_id': tutor.user_id,
            'registration_id': registration.registration_id,
            'tutor_id': registration.tutor_id,
            'subject_id': registration.subject_id,
            'subject_name': subject_name,
            'status': 'approved',
            'total_sessions': registration.total_sessions,
            'start_date': registration.start_date.isoformat() if registration.start_date else None,
            'max_students': registration.max_students,
            'schedule_id': approval_data.schedule_id
        })
    
    return {
        "message": "Registration approved successfully",
        "registration_id": registration.registration_id,
        "status": registration.status
    }


@router.put("/tutor-registrations/{registration_id}/reject")
async def reject_tutor_registration(
    registration_id: int,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a tutor registration
    
    Requires: Coordinator role
    """
    check_coordinator_permission(current_user)
    
    # Get the registration
    query = select(TutorRegistration).where(TutorRegistration.registration_id == registration_id)
    result = await db.execute(query)
    registration = result.scalar_one_or_none()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )
    
    if registration.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration is already {registration.status}"
        )
    
    # Get coordinator_id
    from app.models.database import Coordinator
    coord_query = select(Coordinator).where(Coordinator.user_id == current_user.user_id)
    coord_result = await db.execute(coord_query)
    coordinator = coord_result.scalar_one_or_none()
    
    if not coordinator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coordinator profile not found"
        )
    
    # Update registration
    registration.status = 'rejected'
    registration.approved_by = coordinator.coordinator_id
    registration.rejection_reason = reason
    registration.responded_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(registration)
    
    # Get tutor user_id for event emission
    tutor_query = select(Tutor).where(Tutor.tutor_id == registration.tutor_id)
    tutor_result = await db.execute(tutor_query)
    tutor = tutor_result.scalar_one_or_none()
    
    if tutor:
        # Get subject name for event
        subject_query = select(Subject).where(Subject.subject_id == registration.subject_id)
        subject_result = await db.execute(subject_query)
        subject = subject_result.scalar_one_or_none()
        
        subject_name = subject.subject_name if subject else "môn học"
        
        # Emit event for real-time notification (listener will create notification)
        from app.events import EventTypes
        await event_bus.emit(EventTypes.REGISTRATION_REJECTED, {
            'user_id': tutor.user_id,
            'registration_id': registration.registration_id,
            'subject_name': subject_name,
            'reason': reason,
            'status': 'rejected'
        })
    
    return {
        "message": "Registration rejected",
        "registration_id": registration.registration_id,
        "status": registration.status,
        "reason": reason
    }


# ============================================================================
# SESSION APPROVAL
# ============================================================================

@router.get("/sessions/pending")
async def get_pending_sessions(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending sessions for approval
    
    Requires: Coordinator role
    """
    check_coordinator_permission(current_user)
    
    # Query sessions with status 'pending'
    from app.models.database import SessionParticipant
    
    query = (
        select(SessionModel, Tutor, User, Subject)
        .join(Tutor, SessionModel.tutor_id == Tutor.tutor_id)
        .join(User, Tutor.user_id == User.user_id)
        .join(Subject, SessionModel.subject_id == Subject.subject_id)
        .where(SessionModel.status == 'pending')
        .order_by(SessionModel.start_time.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # OPTIMIZATION: Get participant counts for all sessions in ONE query
    session_ids = [session.session_id for session, _, _, _ in rows]
    
    participant_counts_query = (
        select(
            SessionParticipant.session_id,
            func.count(SessionParticipant.participant_id).label('count')
        )
        .where(SessionParticipant.session_id.in_(session_ids))
        .group_by(SessionParticipant.session_id)
    )
    participant_counts_result = await db.execute(participant_counts_query)
    participant_counts = {row.session_id: row.count for row in participant_counts_result.all()}
    
    sessions = []
    for session, tutor, tutor_user, subject in rows:
        sessions.append({
            "session_id": session.session_id,
            "subject_name": subject.subject_name,
            "subject_code": subject.subject_code,
            "tutor_name": tutor_user.full_name,
            "tutor_email": tutor_user.email,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "location": session.location,
            "max_participants": session.max_participants,
            "current_participants": participant_counts.get(session.session_id, 0),
            "status": session.status,
            "created_at": session.created_at
        })
    
    return sessions


@router.put("/sessions/{session_id}/approve")
async def approve_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a pending session
    
    Requires: Coordinator role
    """
    check_coordinator_permission(current_user)
    
    # Get the session
    query = select(SessionModel).where(SessionModel.session_id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is already {session.status}"
        )
    
    # Update session status
    session.status = 'scheduled'
    
    await db.commit()
    await db.refresh(session)
    
    return {
        "message": "Session approved successfully",
        "session_id": session.session_id,
        "status": session.status
    }


@router.put("/sessions/{session_id}/reject")
async def reject_session(
    session_id: int,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a pending session
    
    Requires: Coordinator role
    """
    check_coordinator_permission(current_user)
    
    # Get the session
    query = select(SessionModel).where(SessionModel.session_id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is already {session.status}"
        )
    
    # Update session status
    session.status = 'cancelled'
    # You might want to add a rejection_reason field to Session model
    
    await db.commit()
    await db.refresh(session)
    
    return {
        "message": "Session rejected",
        "session_id": session.session_id,
        "status": session.status,
        "reason": reason
    }


# ============================================================================
# TUTOR MANAGEMENT & REPORTS
# ============================================================================

@router.get("/tutors")
async def get_all_tutors(
    skip: int = 0,
    limit: int = 50,
    search: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tutors with their basic info and statistics
    
    Requires: Coordinator role
    """
    check_coordinator_permission(current_user)
    
    # Query tutors with user info
    query = (
        select(Tutor, User)
        .join(User, Tutor.user_id == User.user_id)
        .order_by(User.full_name)
    )
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            User.full_name.ilike(search_pattern) |
            User.email.ilike(search_pattern) |
            Tutor.staff_code.ilike(search_pattern)
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    tutors_data = result.all()
    
    # OPTIMIZATION: Get all tutor IDs first
    tutor_ids = [tutor.tutor_id for tutor, _ in tutors_data]
    
    # Get session counts for all tutors in ONE query
    sessions_stats_query = (
        select(
            SessionModel.tutor_id,
            func.count(SessionModel.session_id).label('session_count')
        )
        .where(SessionModel.tutor_id.in_(tutor_ids))
        .group_by(SessionModel.tutor_id)
    )
    sessions_stats_result = await db.execute(sessions_stats_query)
    sessions_stats = {row.tutor_id: row.session_count for row in sessions_stats_result.all()}
    
    # Get course counts for all tutors in ONE query
    courses_stats_query = (
        select(
            TutorRegistration.tutor_id,
            func.count(func.distinct(TutorRegistration.subject_id)).label('course_count')
        )
        .where(
            and_(
                TutorRegistration.tutor_id.in_(tutor_ids),
                TutorRegistration.status == 'approved'
            )
        )
        .group_by(TutorRegistration.tutor_id)
    )
    courses_stats_result = await db.execute(courses_stats_query)
    courses_stats = {row.tutor_id: row.course_count for row in courses_stats_result.all()}
    
    tutors_list = []
    for tutor, user in tutors_data:
        tutors_list.append({
            "tutor_id": tutor.tutor_id,
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "staff_code": tutor.staff_code,
            "faculty": tutor.faculty,
            "rating": float(tutor.rating) if tutor.rating else 0.0,
            "total_sessions": sessions_stats.get(tutor.tutor_id, 0),
            "total_courses": courses_stats.get(tutor.tutor_id, 0),
            "is_verified": tutor.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })
    
    return {
        "tutors": tutors_list,
        "total": len(tutors_list),
        "skip": skip,
        "limit": limit
    }


@router.get("/tutors/{tutor_id}/courses")
async def get_tutor_courses(
    tutor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all courses taught by a specific tutor with statistics
    
    Requires: Coordinator role
    """
    check_coordinator_permission(current_user)
    
    # Verify tutor exists
    tutor_query = select(Tutor, User).join(User, Tutor.user_id == User.user_id).where(Tutor.tutor_id == tutor_id)
    tutor_result = await db.execute(tutor_query)
    tutor_data = tutor_result.first()
    
    if not tutor_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found"
        )
    
    tutor, user = tutor_data
    
    # Get courses with statistics
    from app.models.database import SessionParticipant, SessionFeedback
    
    courses_query = (
        select(
            Subject,
            func.count(func.distinct(SessionModel.session_id)).label('total_sessions'),
            func.count(func.distinct(SessionModel.session_id)).filter(
                SessionModel.status == 'completed'
            ).label('completed_sessions'),
            func.avg(SessionFeedback.rating).label('avg_rating')
        )
        .join(SessionModel, Subject.subject_id == SessionModel.subject_id)
        .outerjoin(SessionFeedback, SessionFeedback.session_id == SessionModel.session_id)
        .where(SessionModel.tutor_id == tutor_id)
        .group_by(Subject.subject_id)
    )
    
    result = await db.execute(courses_query)
    courses_data = result.all()
    
    courses_list = []
    for subject, total_sessions, completed_sessions, avg_rating in courses_data:
        # Count unique students
        students_query = select(func.count(func.distinct(SessionParticipant.user_id))).where(
            and_(
                SessionParticipant.session_id.in_(
                    select(SessionModel.session_id).where(
                        and_(
                            SessionModel.subject_id == subject.subject_id,
                            SessionModel.tutor_id == tutor_id
                        )
                    )
                ),
                SessionParticipant.role == 'student'
            )
        )
        student_count = (await db.execute(students_query)).scalar() or 0
        
        courses_list.append({
            "subject_id": subject.subject_id,
            "subject_code": subject.subject_code,
            "subject_name": subject.subject_name,
            "department": subject.department,
            "total_sessions": total_sessions or 0,
            "completed_sessions": completed_sessions or 0,
            "student_count": student_count,
            "average_rating": round(float(avg_rating), 2) if avg_rating else 0.0
        })
    
    return {
        "tutor": {
            "tutor_id": tutor.tutor_id,
            "full_name": user.full_name,
            "email": user.email,
            "staff_code": tutor.staff_code,
            "faculty": tutor.faculty,
            "rating": float(tutor.rating) if tutor.rating else 0.0
        },
        "courses": courses_list,
        "total_courses": len(courses_list)
    }


@router.get("/tutors/{tutor_id}/courses/{subject_id}/details")
async def get_course_details_with_feedbacks(
    tutor_id: int,
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed course information including student feedbacks and progress
    
    Requires: Coordinator role
    """
    check_coordinator_permission(current_user)
    
    from app.models.database import SessionParticipant, SessionFeedback, ProgressTracking
    
    # Get tutor and subject info
    tutor_query = select(Tutor, User).join(User, Tutor.user_id == User.user_id).where(Tutor.tutor_id == tutor_id)
    tutor_result = await db.execute(tutor_query)
    tutor_data = tutor_result.first()
    
    if not tutor_data:
        raise HTTPException(status_code=404, detail="Tutor not found")
    
    tutor, tutor_user = tutor_data
    
    subject_query = select(Subject).where(Subject.subject_id == subject_id)
    subject_result = await db.execute(subject_query)
    subject = subject_result.scalar_one_or_none()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Get all sessions for this course
    sessions_query = (
        select(SessionModel)
        .where(and_(
            SessionModel.tutor_id == tutor_id,
            SessionModel.subject_id == subject_id
        ))
        .order_by(SessionModel.scheduled_date.desc())
    )
    sessions_result = await db.execute(sessions_query)
    sessions = sessions_result.scalars().all()
    
    # Get student participants and their progress
    students_data = {}
    feedbacks_list = []
    
    for session in sessions:
        # Get participants
        participants_query = (
            select(SessionParticipant, User)
            .join(User, SessionParticipant.user_id == User.user_id)
            .where(and_(
                SessionParticipant.session_id == session.session_id,
                SessionParticipant.role == 'student'
            ))
        )
        participants_result = await db.execute(participants_query)
        participants = participants_result.all()
        
        for participant, student_user in participants:
            if student_user.user_id not in students_data:
                # Count sessions this student participated in
                participation_query = select(func.count(SessionParticipant.participant_id)).where(
                    and_(
                        SessionParticipant.user_id == student_user.user_id,
                        SessionParticipant.session_id.in_([s.session_id for s in sessions]),
                        SessionParticipant.role == 'student'
                    )
                )
                attended = (await db.execute(participation_query)).scalar() or 0
                
                students_data[student_user.user_id] = {
                    "user_id": student_user.user_id,
                    "full_name": student_user.full_name,
                    "email": student_user.email,
                    "total_sessions": len(sessions),
                    "attended_sessions": attended,
                    "attendance_rate": round((attended / len(sessions) * 100) if len(sessions) > 0 else 0, 1)
                }
        
        # Get feedbacks for this session
        feedbacks_query = (
            select(SessionFeedback, User)
            .join(User, SessionFeedback.reviewer_id == User.user_id)
            .where(SessionFeedback.session_id == session.session_id)
        )
        feedbacks_result = await db.execute(feedbacks_query)
        feedbacks = feedbacks_result.all()
        
        for feedback, feedback_user in feedbacks:
            feedbacks_list.append({
                "session_id": session.session_id,
                "session_title": session.title,
                "session_date": session.scheduled_date.isoformat() if session.scheduled_date else None,
                "student_name": feedback_user.full_name,
                "student_email": feedback_user.email,
                "rating": feedback.rating,
                "comment": feedback.comment,
                "created_at": feedback.created_at.isoformat() if feedback.created_at else None
            })
    
    # Calculate overall statistics
    total_sessions = len(sessions)
    completed_sessions = sum(1 for s in sessions if s.status == 'completed')
    avg_rating = sum(f["rating"] for f in feedbacks_list) / len(feedbacks_list) if feedbacks_list else 0.0
    
    return {
        "tutor": {
            "tutor_id": tutor.tutor_id,
            "full_name": tutor_user.full_name,
            "email": tutor_user.email,
            "staff_code": tutor.staff_code
        },
        "course": {
            "subject_id": subject.subject_id,
            "subject_code": subject.subject_code,
            "subject_name": subject.subject_name,
            "department": subject.department
        },
        "statistics": {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "total_students": len(students_data),
            "average_rating": round(avg_rating, 2),
            "total_feedbacks": len(feedbacks_list)
        },
        "students": list(students_data.values()),
        "feedbacks": feedbacks_list
    }


@router.get("/tutors/{tutor_id}/courses/{subject_id}/export")
async def export_course_report(
    tutor_id: int,
    subject_id: int,
    format: str = "csv",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export detailed course report as CSV or JSON
    
    Requires: Coordinator role
    Format: csv or json
    """
    check_coordinator_permission(current_user)
    
    # Get the detailed data
    details = await get_course_details_with_feedbacks(tutor_id, subject_id, current_user, db)
    
    if format == "csv":
        # Create CSV report
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header section
        writer.writerow(["COURSE REPORT"])
        writer.writerow([])
        writer.writerow(["Tutor:", details["tutor"]["full_name"]])
        writer.writerow(["Email:", details["tutor"]["email"]])
        writer.writerow(["Staff Code:", details["tutor"]["staff_code"]])
        writer.writerow([])
        writer.writerow(["Course:", details["course"]["subject_name"]])
        writer.writerow(["Code:", details["course"]["subject_code"]])
        writer.writerow(["Department:", details["course"]["department"]])
        writer.writerow([])
        writer.writerow(["Total Sessions:", details["statistics"]["total_sessions"]])
        writer.writerow(["Completed Sessions:", details["statistics"]["completed_sessions"]])
        writer.writerow(["Total Students:", details["statistics"]["total_students"]])
        writer.writerow(["Average Rating:", details["statistics"]["average_rating"]])
        writer.writerow([])
        
        # Students section
        writer.writerow(["STUDENTS ATTENDANCE"])
        writer.writerow(["Student Name", "Email", "Total Sessions", "Attended", "Attendance Rate (%)"   ])
        for student in details["students"]:
            writer.writerow([
                student["full_name"],
                student["email"],
                student["total_sessions"],
                student["attended_sessions"],
                student["attendance_rate"]
            ])
        writer.writerow([])
        
        # Feedbacks section
        writer.writerow(["SESSION FEEDBACKS"])
        writer.writerow(["Session Title", "Date", "Student", "Rating", "Comment"])
        for feedback in details["feedbacks"]:
            writer.writerow([
                feedback["session_title"],
                feedback["session_date"],
                feedback["student_name"],
                feedback["rating"],
                feedback["comment"] or ""
            ])
        
        # Return CSV file
        output.seek(0)
        filename = f"report_{details['tutor']['staff_code']}_{details['course']['subject_code']}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    else:  # JSON format
        return details


@router.post("/tutors/{tutor_id}/update-rating")
async def update_tutor_rating(
    tutor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate and update tutor's overall rating based on all session feedbacks
    
    Requires: Coordinator role
    """
    check_coordinator_permission(current_user)
    
    from app.models.database import SessionFeedback
    
    # Verify tutor exists
    tutor_query = select(Tutor).where(Tutor.tutor_id == tutor_id)
    tutor_result = await db.execute(tutor_query)
    tutor = tutor_result.scalar_one_or_none()
    
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    
    # Get all feedbacks for this tutor's sessions
    feedbacks_query = (
        select(func.avg(SessionFeedback.rating), func.count(SessionFeedback.feedback_id))
        .join(SessionModel, SessionFeedback.session_id == SessionModel.session_id)
        .where(SessionModel.tutor_id == tutor_id)
    )
    
    result = await db.execute(feedbacks_query)
    avg_rating, total_feedbacks = result.first()
    
    # Update tutor rating
    if avg_rating is not None:
        tutor.rating = float(avg_rating)
        await db.commit()
        await db.refresh(tutor)
        
        return {
            "message": "Tutor rating updated successfully",
            "tutor_id": tutor_id,
            "new_rating": round(float(avg_rating), 2),
            "total_feedbacks": total_feedbacks
        }
    else:
        return {
            "message": "No feedbacks found for this tutor",
            "tutor_id": tutor_id,
            "rating": 0.0,
            "total_feedbacks": 0
        }


@router.post("/tutors/update-all-ratings")
async def update_all_tutors_ratings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update ratings for all tutors based on their session feedbacks
    
    Requires: Coordinator role
    """
    check_coordinator_permission(current_user)
    
    from app.models.database import SessionFeedback
    
    # Get all tutors
    tutors_query = select(Tutor)
    tutors_result = await db.execute(tutors_query)
    tutors = tutors_result.scalars().all()
    
    updated_count = 0
    
    for tutor in tutors:
        # Get average rating for this tutor
        feedbacks_query = (
            select(func.avg(SessionFeedback.rating))
            .join(SessionModel, SessionFeedback.session_id == SessionModel.session_id)
            .where(SessionModel.tutor_id == tutor.tutor_id)
        )
        
        result = await db.execute(feedbacks_query)
        avg_rating = result.scalar()
        
        if avg_rating is not None:
            tutor.rating = float(avg_rating)
            updated_count += 1
    
    await db.commit()
    
    return {
        "message": f"Updated ratings for {updated_count} tutors",
        "total_tutors": len(tutors),
        "updated_count": updated_count
    }

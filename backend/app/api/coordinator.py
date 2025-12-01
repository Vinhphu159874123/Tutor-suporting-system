"""
Coordinator API Routes
Endpoints for coordinator approval workflows
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Dict
from datetime import datetime

from app.core.dependencies import get_current_user, get_db
from app.models.database import User, TutorRegistration, Tutor, Subject, Session as SessionModel, Student, Notifications
from app.events import event_bus

router = APIRouter()

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
    if current_user.role not in ['coordinator', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coordinators can access this endpoint"
        )
    
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
            "end_date": reg.end_date.isoformat() if reg.end_date else None
        })
    
    return registrations


@router.put("/tutor-registrations/{registration_id}/approve")
async def approve_tutor_registration(
    registration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a tutor registration
    
    Requires: Coordinator role
    """
    if current_user.role not in ['coordinator', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coordinators can approve registrations"
        )
    
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
    
    await db.commit()
    await db.refresh(registration)
    
    # Get tutor user_id to send notification
    tutor_query = select(Tutor).where(Tutor.tutor_id == registration.tutor_id)
    tutor_result = await db.execute(tutor_query)
    tutor = tutor_result.scalar_one_or_none()
    
    if tutor:
        # Get subject name for notification
        subject_query = select(Subject).where(Subject.subject_id == registration.subject_id)
        subject_result = await db.execute(subject_query)
        subject = subject_result.scalar_one_or_none()
        
        subject_name = subject.subject_name if subject else "môn học"
        
        # Create notification
        notification = Notifications(
            user_id=tutor.user_id,
            type='registration_approved',
            title='Đơn đăng ký môn học được phê duyệt',
            message=f'Chúc mừng! Đơn đăng ký dạy môn {subject_name} của bạn đã được phê duyệt.',
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.add(notification)
        await db.commit()
        
        # Emit event for real-time notification
        await event_bus.emit('registration_approved', {
            'user_id': tutor.user_id,
            'registration_id': registration.registration_id,
            'subject_name': subject_name
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
    if current_user.role not in ['coordinator', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coordinators can reject registrations"
        )
    
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
    
    # Get tutor user_id to send notification
    tutor_query = select(Tutor).where(Tutor.tutor_id == registration.tutor_id)
    tutor_result = await db.execute(tutor_query)
    tutor = tutor_result.scalar_one_or_none()
    
    if tutor:
        # Get subject name for notification
        subject_query = select(Subject).where(Subject.subject_id == registration.subject_id)
        subject_result = await db.execute(subject_query)
        subject = subject_result.scalar_one_or_none()
        
        subject_name = subject.subject_name if subject else "môn học"
        
        # Create notification
        notification = Notifications(
            user_id=tutor.user_id,
            type='registration_rejected',
            title='Đơn đăng ký môn học bị từ chối',
            message=f'Đơn đăng ký dạy môn {subject_name} của bạn đã bị từ chối. Lý do: {reason}',
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.add(notification)
        await db.commit()
        
        # Emit event for real-time notification
        await event_bus.emit('registration_rejected', {
            'user_id': tutor.user_id,
            'registration_id': registration.registration_id,
            'subject_name': subject_name,
            'reason': reason
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
    if current_user.role not in ['coordinator', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coordinators can access this endpoint"
        )
    
    # Query sessions with status 'pending'
    from app.models.database import SessionParticipant
    
    query = (
        select(SessionModel, Tutor, User.label('tutor_user'), Subject)
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
    
    sessions = []
    for session, tutor, tutor_user, subject in rows:
        # Get participant count
        participant_query = select(func.count(SessionParticipant.participant_id)).where(
            SessionParticipant.session_id == session.session_id
        )
        participant_result = await db.execute(participant_query)
        participant_count = participant_result.scalar() or 0
        
        sessions.append({
            "session_id": session.session_id,
            "subject_name": subject.name,
            "subject_code": subject.code,
            "tutor_name": tutor_user.full_name,
            "tutor_email": tutor_user.email,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "location": session.location,
            "max_participants": session.max_participants,
            "current_participants": participant_count,
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
    if current_user.role not in ['coordinator', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coordinators can approve sessions"
        )
    
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
    if current_user.role not in ['coordinator', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coordinators can reject sessions"
        )
    
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

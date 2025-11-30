from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.models.database import User, Session, SessionParticipant, SessionFeedback, Student, Tutor
from app.api.auth import get_current_user

router = APIRouter()

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    program: Optional[str] = None
    faculty: Optional[str] = None
    major: Optional[str] = None

class UserResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    role: str  # Changed from UserRole enum to str
    phone: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    program: Optional[str] = None
    faculty: Optional[str] = None
    major: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile"""
    response_data = {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "phone": current_user.phone,
        "avatar_url": current_user.avatar_url,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "program": None,
        "faculty": None,
        "major": None
    }
    
    # Get student-specific fields if user is a student
    if current_user.role == 'student':
        result = await db.execute(select(Student).where(Student.user_id == current_user.user_id))
        student = result.scalar_one_or_none()
        if student:
            response_data["faculty"] = student.faculty
            response_data["major"] = student.major
            # Get program from preferences
            if student.preferences and 'program' in student.preferences:
                response_data["program"] = student.preferences['program']
    
    return response_data

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    
    # Update user fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    current_user.updated_at = datetime.utcnow()
    
    # Update student profile if user is a student and student-specific fields are provided
    student = None
    if current_user.role == 'student' and (user_update.program or user_update.faculty or user_update.major):
        result = await db.execute(select(Student).where(Student.user_id == current_user.user_id))
        student = result.scalar_one_or_none()
        
        if student:
            if user_update.faculty is not None:
                student.faculty = user_update.faculty
            if user_update.major is not None:
                student.major = user_update.major
            # Store program in preferences if needed
            if user_update.program is not None:
                preferences = student.preferences or {}
                preferences['program'] = user_update.program
                student.preferences = preferences
    
    await db.commit()
    await db.refresh(current_user)
    
    # Build response with student fields
    response_data = {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "phone": current_user.phone,
        "avatar_url": current_user.avatar_url,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "program": None,
        "faculty": None,
        "major": None
    }
    
    # Add student-specific fields if user is a student
    if current_user.role == 'student':
        if not student:
            result = await db.execute(select(Student).where(Student.user_id == current_user.user_id))
            student = result.scalar_one_or_none()
        
        if student:
            response_data["faculty"] = student.faculty
            response_data["major"] = student.major
            if student.preferences and 'program' in student.preferences:
                response_data["program"] = student.preferences['program']
    
    return response_data

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,  # Changed from UserRole to str
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get users list (admin only)"""
    
    # Check permissions
    if current_user.role not in ['admin', 'coordinator']:  # Changed from enum to str
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID"""
    
    # Users can only view their own profile, or admins can view any profile
    if current_user.user_id != user_id and current_user.role not in ['admin', 'coordinator']:  # Changed from enum to str
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (admin only)"""
    
    if current_user.role != 'admin':  # Changed from enum to str
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete - just deactivate
    user.is_active = False
    await db.commit()
    
    return {"message": "User deleted successfully"}

@router.get("/stats/dashboard")
async def get_user_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard statistics for current user"""
    
    stats = {
        "total_sessions": 0,
        "completed_sessions": 0,
        "upcoming_sessions": 0,
        "average_rating": 0.0
    }
    
    try:
        if current_user.role == 'student':
            # Get student record
            student_result = await db.execute(
                select(Student).where(Student.user_id == current_user.user_id)
            )
            student = student_result.scalar_one_or_none()
            
            if student:
                # Count total sessions via SessionParticipant
                total_result = await db.execute(
                    select(func.count(SessionParticipant.participant_id))
                    .where(SessionParticipant.student_id == student.student_id)
                )
                stats["total_sessions"] = total_result.scalar() or 0
                
                # Count completed sessions
                completed_result = await db.execute(
                    select(func.count(SessionParticipant.participant_id))
                    .select_from(SessionParticipant)
                    .join(Session)
                    .where(
                        and_(
                            SessionParticipant.student_id == student.student_id,
                            Session.status == 'completed'
                        )
                    )
                )
                stats["completed_sessions"] = completed_result.scalar() or 0
                
                # Count upcoming sessions (confirmed, ongoing, published)
                upcoming_result = await db.execute(
                    select(func.count(SessionParticipant.participant_id))
                    .select_from(SessionParticipant)
                    .join(Session)
                    .where(
                        and_(
                            SessionParticipant.student_id == student.student_id,
                            Session.status.in_(['confirmed', 'ongoing', 'published'])
                        )
                    )
                )
                stats["upcoming_sessions"] = upcoming_result.scalar() or 0
                
                # Average rating given by this student
                rating_result = await db.execute(
                    select(func.avg(SessionFeedback.rating))
                    .where(SessionFeedback.student_id == student.student_id)
                )
                avg_rating = rating_result.scalar()
                stats["average_rating"] = round(float(avg_rating), 1) if avg_rating else 0.0
        
        elif current_user.role == 'tutor':
            # Get tutor record
            tutor_result = await db.execute(
                select(Tutor).where(Tutor.user_id == current_user.user_id)
            )
            tutor = tutor_result.scalar_one_or_none()
            
            if tutor:
                # Count total sessions
                total_result = await db.execute(
                    select(func.count(Session.session_id))
                    .where(Session.tutor_id == tutor.tutor_id)
                )
                stats["total_sessions"] = total_result.scalar() or 0
                
                # Count completed
                completed_result = await db.execute(
                    select(func.count(Session.session_id))
                    .where(
                        and_(
                            Session.tutor_id == tutor.tutor_id,
                            Session.status == 'completed'
                        )
                    )
                )
                stats["completed_sessions"] = completed_result.scalar() or 0
                
                # Count upcoming
                upcoming_result = await db.execute(
                    select(func.count(Session.session_id))
                    .where(
                        and_(
                            Session.tutor_id == tutor.tutor_id,
                            Session.status.in_(['confirmed', 'ongoing', 'published'])
                        )
                    )
                )
                stats["upcoming_sessions"] = upcoming_result.scalar() or 0
                
                # Average rating received by this tutor
                rating_result = await db.execute(
                    select(func.avg(SessionFeedback.rating))
                    .select_from(SessionFeedback)
                    .join(Session)
                    .where(Session.tutor_id == tutor.tutor_id)
                )
                avg_rating = rating_result.scalar()
                stats["average_rating"] = round(float(avg_rating), 1) if avg_rating else 0.0
        
        return stats
        
    except Exception as e:
        # Return default stats on error
        return stats

@router.get("/stats/coordinator")
async def get_coordinator_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get coordinator dashboard statistics"""
    
    if current_user.role not in ['coordinator', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    stats = {
        "total_sessions": 0,
        "pending_tutors": 0,
        "pending_sessions": 0,
        "average_rating": 0.0
    }
    
    try:
        # Total sessions
        total_result = await db.execute(select(func.count(Session.session_id)))
        stats["total_sessions"] = total_result.scalar() or 0
        
        # Pending tutor registrations
        from app.models.database import TutorRegistration
        pending_tutors_result = await db.execute(
            select(func.count(TutorRegistration.registration_id))
            .where(TutorRegistration.status == 'pending')
        )
        stats["pending_tutors"] = pending_tutors_result.scalar() or 0
        
        # Pending sessions (need approval)
        pending_sessions_result = await db.execute(
            select(func.count(Session.session_id))
            .where(Session.status.in_(['draft', 'published', 'pending_assignment']))
        )
        stats["pending_sessions"] = pending_sessions_result.scalar() or 0
        
        # Average rating
        rating_result = await db.execute(select(func.avg(SessionFeedback.rating)))
        avg_rating = rating_result.scalar()
        stats["average_rating"] = round(float(avg_rating), 1) if avg_rating else 0.0
        
        return stats
        
    except Exception as e:
        return stats
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case, distinct
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.models.database import User, Session, SessionParticipant, SessionFeedback, Student, Tutor, Attendance
from app.api.auth import get_current_user

router = APIRouter()

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    program: Optional[str] = None
    faculty: Optional[str] = None
    major: Optional[str] = None

class UserResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    role: List[str]  # Array of roles
    phone: Optional[str]
    bio: Optional[str] = None
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
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "program": None,
        "faculty": None,
        "major": None
    }
    
    # Get role-specific fields
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    
    if 'student' in user_roles:
        result = await db.execute(select(Student).where(Student.user_id == current_user.user_id))
        student = result.scalar_one_or_none()
        if student:
            response_data["faculty"] = student.faculty
            response_data["major"] = student.major
            # Get program from preferences
            if student.preferences and 'program' in student.preferences:
                response_data["program"] = student.preferences['program']
    
    elif 'tutor' in user_roles:
        result = await db.execute(select(Tutor).where(Tutor.user_id == current_user.user_id))
        tutor = result.scalar_one_or_none()
        if tutor:
            response_data["faculty"] = tutor.faculty
            # Tutor doesn't have major/program, but has faculty
    
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
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    current_user.updated_at = datetime.utcnow()
    
    # Update role-specific profile fields
    student = None
    tutor = None
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    
    if 'student' in user_roles and (user_update.program or user_update.faculty or user_update.major):
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
    
    elif 'tutor' in user_roles and user_update.faculty:
        result = await db.execute(select(Tutor).where(Tutor.user_id == current_user.user_id))
        tutor = result.scalar_one_or_none()
        
        if tutor:
            if user_update.faculty is not None:
                tutor.faculty = user_update.faculty
    
    await db.commit()
    await db.refresh(current_user)
    
    # Build response with student fields
    response_data = {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "phone": current_user.phone,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "program": None,
        "faculty": None,
        "major": None
    }
    
    # Add role-specific fields
    if 'student' in user_roles:
        if not student:
            result = await db.execute(select(Student).where(Student.user_id == current_user.user_id))
            student = result.scalar_one_or_none()
        
        if student:
            response_data["faculty"] = student.faculty
            response_data["major"] = student.major
            if student.preferences and 'program' in student.preferences:
                response_data["program"] = student.preferences['program']
    
    elif 'tutor' in user_roles:
        if not tutor:
            result = await db.execute(select(Tutor).where(Tutor.user_id == current_user.user_id))
            tutor = result.scalar_one_or_none()
        
        if tutor:
            response_data["faculty"] = tutor.faculty
    
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
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'admin' not in user_roles and 'coordinator' not in user_roles:
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
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if current_user.user_id != user_id and 'admin' not in user_roles and 'coordinator' not in user_roles:
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
    
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'admin' not in user_roles:
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
    mode: Optional[str] = None,  # Add mode parameter to allow switching
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard statistics for current user - OPTIMIZED
    
    Args:
        mode: Optional role to get stats for ('student' or 'tutor'). 
              If not provided, uses current_user.role.
              User must have the requested role (student_id or tutor_id must exist).
    """
    
    # Determine which role to fetch stats for
    active_role = mode or current_user.role
    
    # Validate user has the requested role
    if mode:
        if mode == 'student' and not current_user.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a student"
            )
        if mode == 'tutor' and not current_user.tutor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a tutor"
            )
    
    stats = {
        "total_sessions": 0,
        "completed_sessions": 0,
        "upcoming_sessions": 0,
        "average_rating": 0.0
    }
    
    try:
        if active_role == 'student':
            # Get student record
            student_result = await db.execute(
                select(Student).where(Student.user_id == current_user.user_id)
            )
            student = student_result.scalar_one_or_none()
            
            if student:
                from datetime import date
                today = date.today()
                
                # Total sessions from enrolled courses
                total_result = await db.execute(
                    select(func.count(SessionParticipant.participant_id))
                    .where(
                        and_(
                            SessionParticipant.user_id == student.user_id,
                            SessionParticipant.role == 'student'
                        )
                    )
                )
                stats["total_sessions"] = total_result.scalar() or 0
                
                # Completed sessions = sessions with attendance records
                completed_result = await db.execute(
                    select(func.count(distinct(Attendance.session_id)))
                    .where(Attendance.student_id == student.student_id)
                )
                stats["completed_sessions"] = completed_result.scalar() or 0
                
                # Upcoming sessions = sessions from today onwards
                upcoming_result = await db.execute(
                    select(func.count(SessionParticipant.participant_id))
                    .select_from(SessionParticipant)
                    .join(Session, SessionParticipant.session_id == Session.session_id)
                    .where(
                        and_(
                            SessionParticipant.user_id == student.user_id,
                            SessionParticipant.role == 'student',
                            Session.scheduled_date >= today
                        )
                    )
                )
                stats["upcoming_sessions"] = upcoming_result.scalar() or 0
                
                print(f"DEBUG: FINAL - total={stats['total_sessions']}, completed={stats['completed_sessions']}, upcoming={stats['upcoming_sessions']}")
        
        elif active_role == 'tutor':
            # Get tutor record
            tutor_result = await db.execute(
                select(Tutor).where(Tutor.user_id == current_user.user_id)
            )
            tutor = tutor_result.scalar_one_or_none()
            
            if tutor:
                # Single query with CASE aggregation
                result = await db.execute(
                    select(
                        func.count(Session.session_id).label('total'),
                        func.sum(case((Session.status == 'completed', 1), else_=0)).label('completed'),
                        func.sum(case((Session.status.in_(['confirmed', 'ongoing', 'published']), 1), else_=0)).label('upcoming')
                    )
                    .where(Session.tutor_id == tutor.tutor_id)
                )
                row = result.first()
                if row:
                    stats["total_sessions"] = row.total or 0
                    stats["completed_sessions"] = int(row.completed or 0)
                    stats["upcoming_sessions"] = int(row.upcoming or 0)
                
                # Average rating (separate query)
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
    
    # Check if user has coordinator or admin role (support array)
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'coordinator' not in user_roles and 'admin' not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    stats = {
        "total_sessions": 0,
        "active_students": 0,
        "total_tutors": 0,
        "pending_tutors": 0,
        "pending_sessions": 0,
        "completed_sessions": 0,
        "average_rating": 0.0,
        "total_hours": 0,
        "attendance_rate": 0.0
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
        
        # Active students (distinct students with sessions)
        active_students_result = await db.execute(
            select(func.count(distinct(SessionParticipant.user_id)))
            .where(SessionParticipant.role == 'student')
        )
        stats["active_students"] = active_students_result.scalar() or 0
        
        # Total tutors
        total_tutors_result = await db.execute(select(func.count(Tutor.tutor_id)))
        stats["total_tutors"] = total_tutors_result.scalar() or 0
        
        # Completed sessions
        completed_result = await db.execute(
            select(func.count(Session.session_id))
            .where(Session.status == 'completed')
        )
        stats["completed_sessions"] = completed_result.scalar() or 0
        
        # Total hours (estimate 2h per session)
        stats["total_hours"] = stats["total_sessions"] * 2
        
        # Attendance rate
        total_attendance_result = await db.execute(
            select(func.count(Attendance.attendance_id))
        )
        total_attendance = total_attendance_result.scalar() or 0
        
        # Expected attendance = completed sessions * average students per session
        if stats["completed_sessions"] > 0 and stats["active_students"] > 0:
            expected_attendance = stats["completed_sessions"] * (stats["active_students"] / max(stats["total_sessions"], 1))
            stats["attendance_rate"] = round((total_attendance / max(expected_attendance, 1)) * 100, 1) if expected_attendance > 0 else 0.0
        
        return stats
        
    except Exception as e:
        return stats
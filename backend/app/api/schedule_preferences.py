"""
Schedule Preferences API endpoints for students to submit course scheduling preferences
and tutors to view statistics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.database import SchedulePreference, Student, Subject, User
from app.core.dependencies import get_current_user, get_db

router = APIRouter()

# Pydantic models
class TimeSlot(BaseModel):
    """Time slot model"""
    day: str = Field(..., description="Day of week: monday, tuesday, wednesday, thursday, friday, saturday, sunday")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")

class SchedulePreferenceCreate(BaseModel):
    """Create schedule preference request"""
    subject_id: int
    preferred_start_date: date
    total_sessions: int = Field(gt=0, description="Total number of sessions")
    session_duration: int = Field(gt=0, description="Duration of each session in minutes")
    session_format: str = Field(default="both", description="online, offline, or both")
    available_time_slots: List[TimeSlot]
    notes: Optional[str] = None

class SchedulePreferenceUpdate(BaseModel):
    """Update schedule preference request"""
    preferred_start_date: Optional[date] = None
    total_sessions: Optional[int] = Field(None, gt=0)
    session_duration: Optional[int] = Field(None, gt=0)
    session_format: Optional[str] = None
    available_time_slots: Optional[List[TimeSlot]] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class SchedulePreferenceResponse(BaseModel):
    """Schedule preference response"""
    preference_id: int
    student_id: int
    student_name: str
    subject_id: int
    subject_code: str
    subject_name: str
    preferred_start_date: date
    total_sessions: int
    session_duration: int
    session_format: str
    available_time_slots: List[Dict[str, str]]
    notes: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

class PreferenceStatistics(BaseModel):
    """Statistics for a subject's schedule preferences"""
    subject_id: int
    subject_code: str
    subject_name: str
    total_requests: int
    popular_time_slots: List[Dict[str, Any]]
    format_distribution: Dict[str, int]
    average_duration: int
    duration_distribution: Dict[int, int]
    average_sessions: float
    earliest_start_date: Optional[date]
    latest_start_date: Optional[date]


# Student endpoints
@router.post("/", response_model=SchedulePreferenceResponse)
async def create_schedule_preference(
    preference_data: SchedulePreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new schedule preference (Student only)
    """
    if current_user.role != 'student':
        raise HTTPException(status_code=403, detail="Only students can create schedule preferences")
    
    # Get student profile
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.user_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Verify subject exists
    result = await db.execute(
        select(Subject).where(Subject.subject_id == preference_data.subject_id)
    )
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Check for duplicate active preference
    result = await db.execute(
        select(SchedulePreference).where(
            and_(
                SchedulePreference.student_id == student.student_id,
                SchedulePreference.subject_id == preference_data.subject_id,
                SchedulePreference.status == 'pending'
            )
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="You already have a pending preference for this subject. Please update or cancel it first."
        )
    
    # Convert time slots to JSON format
    time_slots_json = [slot.dict() for slot in preference_data.available_time_slots]
    
    # Create preference
    new_preference = SchedulePreference(
        student_id=student.student_id,
        subject_id=preference_data.subject_id,
        preferred_start_date=preference_data.preferred_start_date,
        total_sessions=preference_data.total_sessions,
        session_duration=preference_data.session_duration,
        session_format=preference_data.session_format,
        available_time_slots=time_slots_json,
        notes=preference_data.notes,
        status='pending'
    )
    
    db.add(new_preference)
    await db.commit()
    await db.refresh(new_preference)
    
    return SchedulePreferenceResponse(
        preference_id=new_preference.preference_id,
        student_id=new_preference.student_id,
        student_name=current_user.full_name,
        subject_id=subject.subject_id,
        subject_code=subject.subject_code,
        subject_name=subject.subject_name,
        preferred_start_date=new_preference.preferred_start_date,
        total_sessions=new_preference.total_sessions,
        session_duration=new_preference.session_duration,
        session_format=new_preference.session_format,
        available_time_slots=new_preference.available_time_slots,
        notes=new_preference.notes,
        status=new_preference.status,
        created_at=new_preference.created_at,
        updated_at=new_preference.updated_at
    )


@router.get("/my-preferences", response_model=List[SchedulePreferenceResponse])
async def get_my_preferences(
    status: Optional[str] = Query(None, description="Filter by status: pending, fulfilled, cancelled, expired"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all schedule preferences for current student
    """
    if current_user.role != 'student':
        raise HTTPException(status_code=403, detail="Only students can view their preferences")
    
    # Get student profile
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.user_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Build query
    query = (
        select(SchedulePreference, Subject)
        .join(Subject, SchedulePreference.subject_id == Subject.subject_id)
        .where(SchedulePreference.student_id == student.student_id)
    )
    
    if status:
        query = query.where(SchedulePreference.status == status)
    
    query = query.order_by(SchedulePreference.created_at.desc())
    
    result = await db.execute(query)
    preferences_data = result.all()
    
    return [
        SchedulePreferenceResponse(
            preference_id=pref.preference_id,
            student_id=pref.student_id,
            student_name=current_user.full_name,
            subject_id=subj.subject_id,
            subject_code=subj.subject_code,
            subject_name=subj.subject_name,
            preferred_start_date=pref.preferred_start_date,
            total_sessions=pref.total_sessions,
            session_duration=pref.session_duration,
            session_format=pref.session_format,
            available_time_slots=pref.available_time_slots,
            notes=pref.notes,
            status=pref.status,
            created_at=pref.created_at,
            updated_at=pref.updated_at
        )
        for pref, subj in preferences_data
    ]


@router.put("/{preference_id}", response_model=SchedulePreferenceResponse)
async def update_schedule_preference(
    preference_id: int,
    update_data: SchedulePreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a schedule preference (Student only, own preferences)
    """
    if current_user.role != 'student':
        raise HTTPException(status_code=403, detail="Only students can update preferences")
    
    # Get student profile
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.user_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Get preference
    result = await db.execute(
        select(SchedulePreference, Subject)
        .join(Subject, SchedulePreference.subject_id == Subject.subject_id)
        .where(SchedulePreference.preference_id == preference_id)
    )
    data = result.one_or_none()
    if not data:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    preference, subject = data
    
    # Check ownership
    if preference.student_id != student.student_id:
        raise HTTPException(status_code=403, detail="You can only update your own preferences")
    
    # Update fields
    if update_data.preferred_start_date:
        preference.preferred_start_date = update_data.preferred_start_date
    if update_data.total_sessions:
        preference.total_sessions = update_data.total_sessions
    if update_data.session_duration:
        preference.session_duration = update_data.session_duration
    if update_data.session_format:
        preference.session_format = update_data.session_format
    if update_data.available_time_slots:
        preference.available_time_slots = [slot.dict() for slot in update_data.available_time_slots]
    if update_data.notes is not None:
        preference.notes = update_data.notes
    if update_data.status:
        preference.status = update_data.status
    
    await db.commit()
    await db.refresh(preference)
    
    return SchedulePreferenceResponse(
        preference_id=preference.preference_id,
        student_id=preference.student_id,
        student_name=current_user.full_name,
        subject_id=subject.subject_id,
        subject_code=subject.subject_code,
        subject_name=subject.subject_name,
        preferred_start_date=preference.preferred_start_date,
        total_sessions=preference.total_sessions,
        session_duration=preference.session_duration,
        session_format=preference.session_format,
        available_time_slots=preference.available_time_slots,
        notes=preference.notes,
        status=preference.status,
        created_at=preference.created_at,
        updated_at=preference.updated_at
    )


@router.delete("/{preference_id}")
async def delete_schedule_preference(
    preference_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a schedule preference (Student only, own preferences)
    """
    if current_user.role != 'student':
        raise HTTPException(status_code=403, detail="Only students can delete preferences")
    
    # Get student profile
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.user_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Get preference
    result = await db.execute(
        select(SchedulePreference).where(SchedulePreference.preference_id == preference_id)
    )
    preference = result.scalar_one_or_none()
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    # Check ownership
    if preference.student_id != student.student_id:
        raise HTTPException(status_code=403, detail="You can only delete your own preferences")
    
    await db.delete(preference)
    await db.commit()
    
    return {"message": "Preference deleted successfully"}


# Tutor endpoints
@router.get("/statistics", response_model=List[PreferenceStatistics])
async def get_preferences_statistics(
    subject_id: Optional[int] = Query(None, description="Filter by specific subject"),
    min_requests: int = Query(1, description="Minimum number of requests to include"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics of schedule preferences for tutors to decide which courses to open
    """
    if current_user.role != 'tutor':
        raise HTTPException(status_code=403, detail="Only tutors can view statistics")
    
    # Build base query
    query = (
        select(
            SchedulePreference.subject_id,
            Subject.subject_code,
            Subject.subject_name,
            func.count(SchedulePreference.preference_id).label('total_requests'),
            func.avg(SchedulePreference.session_duration).label('avg_duration'),
            func.avg(SchedulePreference.total_sessions).label('avg_sessions'),
            func.min(SchedulePreference.preferred_start_date).label('earliest_date'),
            func.max(SchedulePreference.preferred_start_date).label('latest_date')
        )
        .join(Subject, SchedulePreference.subject_id == Subject.subject_id)
        .where(SchedulePreference.status == 'pending')
        .group_by(
            SchedulePreference.subject_id,
            Subject.subject_code,
            Subject.subject_name
        )
        .having(func.count(SchedulePreference.preference_id) >= min_requests)
    )
    
    if subject_id:
        query = query.where(SchedulePreference.subject_id == subject_id)
    
    query = query.order_by(func.count(SchedulePreference.preference_id).desc())
    
    result = await db.execute(query)
    stats_data = result.all()
    
    statistics = []
    
    for stat in stats_data:
        # Get format distribution
        format_result = await db.execute(
            select(
                SchedulePreference.session_format,
                func.count(SchedulePreference.preference_id).label('count')
            )
            .where(
                and_(
                    SchedulePreference.subject_id == stat.subject_id,
                    SchedulePreference.status == 'pending'
                )
            )
            .group_by(SchedulePreference.session_format)
        )
        format_dist = {row.session_format: row.count for row in format_result.all()}
        
        # Get duration distribution
        duration_result = await db.execute(
            select(
                SchedulePreference.session_duration,
                func.count(SchedulePreference.preference_id).label('count')
            )
            .where(
                and_(
                    SchedulePreference.subject_id == stat.subject_id,
                    SchedulePreference.status == 'pending'
                )
            )
            .group_by(SchedulePreference.session_duration)
        )
        duration_dist = {row.session_duration: row.count for row in duration_result.all()}
        
        # Get popular time slots
        prefs_result = await db.execute(
            select(SchedulePreference.available_time_slots)
            .where(
                and_(
                    SchedulePreference.subject_id == stat.subject_id,
                    SchedulePreference.status == 'pending'
                )
            )
        )
        
        # Aggregate time slots
        time_slot_counts = {}
        for (slots,) in prefs_result.all():
            for slot in slots:
                key = f"{slot['day']} {slot['start_time']}-{slot['end_time']}"
                time_slot_counts[key] = time_slot_counts.get(key, 0) + 1
        
        # Sort by popularity
        popular_slots = [
            {
                "time_slot": slot,
                "count": count,
                "percentage": round(count / stat.total_requests * 100, 1)
            }
            for slot, count in sorted(time_slot_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        statistics.append(
            PreferenceStatistics(
                subject_id=stat.subject_id,
                subject_code=stat.subject_code,
                subject_name=stat.subject_name,
                total_requests=stat.total_requests,
                popular_time_slots=popular_slots,
                format_distribution=format_dist,
                average_duration=int(stat.avg_duration),
                duration_distribution=duration_dist,
                average_sessions=round(stat.avg_sessions, 1),
                earliest_start_date=stat.earliest_date,
                latest_start_date=stat.latest_date
            )
        )
    
    return statistics


@router.get("/statistics/{subject_id}/details")
async def get_subject_preference_details(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed list of all preferences for a specific subject (Tutor only)
    """
    if current_user.role != 'tutor':
        raise HTTPException(status_code=403, detail="Only tutors can view preference details")
    
    # Get all pending preferences for this subject
    result = await db.execute(
        select(SchedulePreference, Student, User, Subject)
        .join(Student, SchedulePreference.student_id == Student.student_id)
        .join(User, Student.user_id == User.user_id)
        .join(Subject, SchedulePreference.subject_id == Subject.subject_id)
        .where(
            and_(
                SchedulePreference.subject_id == subject_id,
                SchedulePreference.status == 'pending'
            )
        )
        .order_by(SchedulePreference.created_at.desc())
    )
    
    data = result.all()
    
    if not data:
        raise HTTPException(status_code=404, detail="No preferences found for this subject")
    
    return {
        "subject_id": subject_id,
        "subject_code": data[0][3].subject_code,
        "subject_name": data[0][3].subject_name,
        "total_requests": len(data),
        "preferences": [
            {
                "preference_id": pref.preference_id,
                "student_name": user.full_name,
                "student_code": student.student_code,
                "preferred_start_date": pref.preferred_start_date.isoformat(),
                "total_sessions": pref.total_sessions,
                "session_duration": pref.session_duration,
                "session_format": pref.session_format,
                "available_time_slots": pref.available_time_slots,
                "notes": pref.notes,
                "created_at": pref.created_at.isoformat()
            }
            for pref, student, user, _ in data
        ]
    }

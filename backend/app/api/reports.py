"""
Reports API
Analytics and reporting for tutors, students, and administrators
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.database import (
    User, Session, SessionFeedback, ProgressTracking, 
    Subject, Student, Tutor, TutorRegistration
)

router = APIRouter()


@router.get("/statistics")
async def get_system_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get system-wide statistics"""
    
    # Total sessions
    session_result = await db.execute(
        select(func.count(Session.session_id))
    )
    total_sessions = session_result.scalar() or 0
    
    # Completed sessions
    completed_result = await db.execute(
        select(func.count(Session.session_id)).where(
            Session.status == "completed"
        )
    )
    completed_sessions = completed_result.scalar() or 0
    
    # Active students
    students_result = await db.execute(
        select(func.count(Student.student_id))
    )
    active_students = students_result.scalar() or 0
    
    # Average rating
    rating_result = await db.execute(
        select(func.avg(SessionFeedback.rating))
    )
    avg_rating = rating_result.scalar() or 0.0
    
    # Total tutor hours (assuming 1 hour per session for now)
    tutor_hours = completed_sessions
    
    return {
        "completed_sessions": completed_sessions,
        "active_students": active_students,
        "average_satisfaction": round(float(avg_rating), 1) if avg_rating else 0.0,
        "tutor_hours": tutor_hours,
        "total_sessions": total_sessions,
        "completion_rate": round((completed_sessions / total_sessions * 100) if total_sessions > 0 else 0, 1)
    }


@router.get("/courses")
async def get_course_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> list:
    """Get course-level statistics"""
    
    # Get courses with stats
    query = select(
        Subject.subject_id,
        Subject.subject_name,
        Subject.subject_code,
        func.count(Session.session_id).label("total_sessions"),
        func.count(
            Session.session_id
        ).filter(Session.status == "completed").label("completed_sessions"),
        func.avg(ProgressTracking.understanding_level).label("avg_score")
    ).outerjoin(
        Session, Session.subject_id == Subject.subject_id
    ).outerjoin(
        ProgressTracking, ProgressTracking.session_id == Session.session_id
    ).group_by(
        Subject.subject_id, Subject.subject_name, Subject.subject_code
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    courses_list = []
    for row in rows:
        total = row.total_sessions or 0
        completed = row.completed_sessions or 0
        completion = round((completed / total * 100) if total > 0 else 0, 0)
        
        courses_list.append({
            "id": str(row.subject_id),
            "course": row.subject_name,
            "faculty": "CS",  # TODO: Add faculty to Subject model
            "completion": int(completion),
            "averageScore": round(float(row.avg_score or 0), 1),
            "tutorHours": completed,  # Assuming 1h per session
            "activeStudents": 0  # TODO: Count unique students per subject
        })
    
    return courses_list


@router.get("/tutor/{tutor_id}")
async def get_tutor_performance(
    tutor_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get tutor performance report"""
    
    # Build query
    query = select(
        func.count(Session.session_id).label("total_sessions"),
        func.count(Session.session_id).filter(
            Session.status == "completed"
        ).label("completed_sessions"),
        func.avg(SessionFeedback.rating).label("avg_rating")
    ).outerjoin(
        SessionFeedback, SessionFeedback.session_id == Session.session_id
    ).where(
        Session.tutor_id == tutor_id
    )
    
    if start_date:
        query = query.where(Session.start_time >= start_date)
    if end_date:
        query = query.where(Session.start_time <= end_date)
    
    result = await db.execute(query)
    row = result.first()
    
    return {
        "tutor_id": tutor_id,
        "total_sessions": row.total_sessions or 0,
        "completed_sessions": row.completed_sessions or 0,
        "average_rating": round(float(row.avg_rating or 0), 1),
        "completion_rate": round(
            (row.completed_sessions / row.total_sessions * 100) 
            if row.total_sessions and row.total_sessions > 0 else 0, 
            1
        )
    }


@router.get("/student/{student_id}")
async def get_student_progress_report(
    student_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get student progress report"""
    
    # Build query for student sessions
    query = select(
        func.count(Session.session_id).label("total_sessions"),
        func.count(Session.session_id).filter(
            Session.status == "completed"
        ).label("attended_sessions"),
        func.avg(ProgressTracking.understanding_level).label("avg_understanding")
    ).outerjoin(
        ProgressTracking, ProgressTracking.session_id == Session.session_id
    ).where(
        Session.student_id == student_id
    )
    
    if start_date:
        query = query.where(Session.start_time >= start_date)
    if end_date:
        query = query.where(Session.start_time <= end_date)
    
    result = await db.execute(query)
    row = result.first()
    
    return {
        "student_id": student_id,
        "total_sessions": row.total_sessions or 0,
        "attended_sessions": row.attended_sessions or 0,
        "attendance_rate": round(
            (row.attended_sessions / row.total_sessions * 100) 
            if row.total_sessions and row.total_sessions > 0 else 0, 
            1
        ),
        "average_understanding": round(float(row.avg_understanding or 0), 1)
    }
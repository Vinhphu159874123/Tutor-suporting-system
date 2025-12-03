"""
Learning Progress API
Track student learning progress and achievements
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.schemas.progress import (
    ProgressCreate, ProgressUpdate, ProgressResponse, AchievementResponse
)
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.database import User, ProgressTracking, Session, Subject, Student, LearningAchievements

router = APIRouter()


@router.get("/students/{student_id}/progress")
async def get_student_progress(
    student_id: int,
    subject_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """View student learning progress"""
    
    # Build query
    query = select(
        ProgressTracking,
        Session,
        Subject
    ).join(
        Session, ProgressTracking.session_id == Session.session_id
    ).join(
        Subject, ProgressTracking.subject_id == Subject.subject_id
    ).where(
        ProgressTracking.student_id == student_id
    )
    
    if subject_id:
        query = query.where(ProgressTracking.subject_id == subject_id)
    
    if start_date:
        query = query.where(Session.start_time >= start_date)
    
    if end_date:
        query = query.where(Session.start_time <= end_date)
    
    query = query.order_by(Session.start_time.desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    progress_list = []
    for progress, session, subject in rows:
        progress_list.append({
            "courseId": subject.subject_code or f"SUBJ{subject.subject_id}",
            "courseName": subject.subject_name,
            "totalSessions": 1,  # Will aggregate later
            "completedSessions": 1 if session.status == "completed" else 0,
            "averageScore": progress.understanding_level or 0,
            "attendance": 100 if session.status == "completed" else 0,
            "session_date": session.start_time.isoformat() if session.start_time else None,
            "understanding_level": progress.understanding_level,
            "topics_covered": progress.topics_covered or [],
            "strengths": progress.strengths,
            "weaknesses": progress.weaknesses
        })
    
    return progress_list


# TODO: Implement ProgressService and get_progress_service dependency
# The following endpoints are temporarily disabled until ProgressService is implemented

# @router.post("/sessions/{session_id}/progress", response_model=ProgressResponse)
# async def update_session_progress(
#     session_id: int,
#     progress_data: ProgressCreate,
#     progress_service: ProgressService = Depends(get_progress_service),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Update learning progress after session
#     
#     TODO:
#     - Permission check (tutor of the session)
#     - Validate session exists and is completed
#     - Create progress entry
#     - Update student statistics
#     - Trigger achievement checks
#     
#     Returns: Created progress entry
#     """
#     # PLACEHOLDER - Replace with real implementation
#     return {
#         "id": 1,
#         "student_id": progress_data.student_id,
#         "session_id": session_id,
#         "subject_id": progress_data.subject_id,
#         "topics_covered": progress_data.topics_covered,
#         "understanding_level": progress_data.understanding_level,
#         "notes": progress_data.notes,
#         "tutor_feedback": progress_data.tutor_feedback,
#         "created_at": datetime.utcnow()
#     }


# @router.get("/students/{student_id}/achievements", response_model=List[AchievementResponse])
# async def get_student_achievements(
#     student_id: int,
#     progress_service: ProgressService = Depends(get_progress_service),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get student achievements and milestones
#     
#     TODO:
#     - Permission check (student themselves or admin)
#     - Load all achievements
#     - Sort by date earned
#     - Include achievement statistics
#     
#     Returns: List of achievements
#     """
#     # PLACEHOLDER - Replace with real implementation
#     return []


# @router.get("/subjects/{subject_id}/progress", response_model=dict)
# async def get_subject_progress(
#     subject_id: int,
#     student_id: Optional[int] = Query(None),
#     progress_service: ProgressService = Depends(get_progress_service),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get progress statistics by subject
#     
#     TODO:
#     - Calculate average understanding level
#     - Count completed topics
#     - Progress trend over time
#     - Compare with other students (anonymous)
#     
#     Returns: Subject progress statistics
#     """
#     # PLACEHOLDER - Replace with real implementation
#     return {
#         "subject_id": subject_id,
#         "average_understanding": 0,
#         "topics_completed": 0,
#         "total_sessions": 0,
#         "progress_trend": "stable"
#     }


# @router.put("/progress/{progress_id}", response_model=ProgressResponse)
# async def update_progress_entry(
#     progress_id: int,
#     progress_data: ProgressUpdate,
#     progress_service: ProgressService = Depends(get_progress_service),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Update existing progress entry
#     
#     TODO:
#     - Permission check (original tutor or admin)
#     - Validate progress entry exists
#     - Update database record
#     - Recalculate student statistics
#     
#     Returns: Updated progress entry
#     """
#     # PLACEHOLDER - Replace with real implementation
#     raise HTTPException(
#         status_code=status.HTTP_501_NOT_IMPLEMENTED,
#         detail="Update progress entry - Implementation pending"
#     )


@router.get("/courses/{subject_id}/study-progress")
async def get_course_study_progress(
    subject_id: int,
    tutor_id: Optional[int] = Query(None, description="Filter by tutor (for students with multiple tutors)"),
    mode: Optional[str] = Query(None, description="Force mode: student or tutor"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get study progress for a course
    - Tutors: See progress of all enrolled students
    - Students: See their own progress
    """
    from app.models.database import Tutor, SessionParticipant, Attendance
    from datetime import timezone, timedelta
    
    # Determine effective mode
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    effective_mode = mode or ('tutor' if 'tutor' in user_roles else user_roles[0])
    
    # Verify subject exists
    subject_result = await db.execute(
        select(Subject).where(Subject.subject_id == subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if effective_mode == 'tutor' and 'tutor' in user_roles:
        # Get tutor record
        tutor_result = await db.execute(
            select(Tutor).where(Tutor.user_id == current_user.user_id)
        )
        tutor = tutor_result.scalar_one_or_none()
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor profile not found")
        
        # Get all sessions for this subject by this tutor
        sessions_result = await db.execute(
            select(Session)
            .where(and_(
                Session.subject_id == subject_id,
                Session.tutor_id == tutor.tutor_id
            ))
            .order_by(Session.scheduled_date, Session.start_time)
        )
        sessions = sessions_result.scalars().all()
        
        if not sessions:
            return {
                "subject_id": subject_id,
                "subject_name": subject.subject_name,
                "subject_code": subject.subject_code,
                "total_sessions": 0,
                "students": []
            }
        
        session_ids = [s.session_id for s in sessions]
        
        # Get all students enrolled in these sessions
        students_result = await db.execute(
            select(User, Student, SessionParticipant.user_id)
            .join(Student, User.user_id == Student.user_id)
            .join(SessionParticipant, User.user_id == SessionParticipant.user_id)
            .where(and_(
                SessionParticipant.session_id.in_(session_ids),
                SessionParticipant.role == 'student'
            ))
            .distinct()
        )
        
        students_data = []
        for user, student, _ in students_result.all():
            # Get attendance records for this student
            attendance_result = await db.execute(
                select(Attendance)
                .where(and_(
                    Attendance.student_id == student.student_id,
                    Attendance.session_id.in_(session_ids)
                ))
            )
            attendances = attendance_result.scalars().all()
            
            # Calculate statistics
            present_count = sum(1 for a in attendances if a.status == 'present')
            late_count = sum(1 for a in attendances if a.status == 'late')
            absent_count = sum(1 for a in attendances if a.status == 'absent')
            excused_count = sum(1 for a in attendances if a.status == 'excused')
            
            total_sessions = len(sessions)
            completed_sessions = len(attendances)
            attendance_rate = (present_count + late_count) / total_sessions * 100 if total_sessions > 0 else 0
            progress_percentage = completed_sessions / total_sessions * 100 if total_sessions > 0 else 0
            
            students_data.append({
                "student_id": student.student_id,
                "user_id": user.user_id,
                "student_name": user.full_name,
                "student_code": student.student_code,
                "email": user.email,
                "progress": {
                    "total_sessions": total_sessions,
                    "completed_sessions": completed_sessions,
                    "progress_percentage": round(progress_percentage, 1),
                    "attendance": {
                        "present": present_count,
                        "late": late_count,
                        "absent": absent_count,
                        "excused": excused_count,
                        "attendance_rate": round(attendance_rate, 1)
                    }
                }
            })
        
        # Sort by progress percentage (lowest first to highlight who needs attention)
        students_data.sort(key=lambda x: x["progress"]["progress_percentage"])
        
        return {
            "subject_id": subject_id,
            "subject_name": subject.subject_name,
            "subject_code": subject.subject_code,
            "total_sessions": len(sessions),
            "total_students": len(students_data),
            "students": students_data
        }
        
    elif effective_mode == 'student' and 'student' in user_roles:
        # Get student record
        student_result = await db.execute(
            select(Student).where(Student.user_id == current_user.user_id)
        )
        student = student_result.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        
        # Build session query
        session_query = select(Session).where(Session.subject_id == subject_id)
        
        # If tutor_id specified, filter by tutor
        if tutor_id:
            session_query = session_query.where(Session.tutor_id == tutor_id)
        
        # Get sessions where student is participant
        sessions_result = await db.execute(
            session_query
            .join(SessionParticipant, Session.session_id == SessionParticipant.session_id)
            .where(and_(
                SessionParticipant.user_id == current_user.user_id,
                SessionParticipant.role == 'student'
            ))
            .order_by(Session.scheduled_date, Session.start_time)
        )
        sessions = sessions_result.scalars().all()
        
        if not sessions:
            return {
                "subject_id": subject_id,
                "subject_name": subject.subject_name,
                "subject_code": subject.subject_code,
                "student_progress": {
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "progress_percentage": 0,
                    "attendance": {
                        "present": 0,
                        "late": 0,
                        "absent": 0,
                        "excused": 0,
                        "attendance_rate": 0
                    },
                    "sessions": []
                }
            }
        
        session_ids = [s.session_id for s in sessions]
        
        # Get attendance records
        attendance_result = await db.execute(
            select(Attendance)
            .where(and_(
                Attendance.student_id == student.student_id,
                Attendance.session_id.in_(session_ids)
            ))
        )
        attendances = {a.session_id: a for a in attendance_result.scalars().all()}
        
        # Build session details
        vietnam_tz = timezone(timedelta(hours=7))
        now = datetime.now(vietnam_tz)
        
        session_details = []
        for session in sessions:
            attendance = attendances.get(session.session_id)
            
            # Determine session status
            session_datetime = None
            if session.scheduled_date and session.start_time:
                session_datetime = datetime.combine(session.scheduled_date, session.start_time)
                session_datetime = session_datetime.replace(tzinfo=vietnam_tz)
            
            is_past = session_datetime and session_datetime < now if session_datetime else False
            
            session_details.append({
                "session_id": session.session_id,
                "title": session.title,
                "scheduled_date": session.scheduled_date.isoformat() if session.scheduled_date else None,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "status": session.status,
                "is_past": is_past,
                "attendance": {
                    "status": attendance.status if attendance else None,
                    "check_in_time": attendance.check_in_time.isoformat() if attendance and attendance.check_in_time else None,
                    "duration_minutes": attendance.duration_minutes if attendance else None
                } if attendance else None
            })
        
        # Calculate statistics
        present_count = sum(1 for a in attendances.values() if a.status == 'present')
        late_count = sum(1 for a in attendances.values() if a.status == 'late')
        absent_count = sum(1 for a in attendances.values() if a.status == 'absent')
        excused_count = sum(1 for a in attendances.values() if a.status == 'excused')
        
        total_sessions = len(sessions)
        completed_sessions = len(attendances)
        attendance_rate = (present_count + late_count) / total_sessions * 100 if total_sessions > 0 else 0
        progress_percentage = completed_sessions / total_sessions * 100 if total_sessions > 0 else 0
        
        return {
            "subject_id": subject_id,
            "subject_name": subject.subject_name,
            "subject_code": subject.subject_code,
            "student_progress": {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "progress_percentage": round(progress_percentage, 1),
                "attendance": {
                    "present": present_count,
                    "late": late_count,
                    "absent": absent_count,
                    "excused": excused_count,
                    "attendance_rate": round(attendance_rate, 1)
                },
                "sessions": session_details
            }
        }
    else:
        raise HTTPException(status_code=403, detail="Only tutors and students can view progress")
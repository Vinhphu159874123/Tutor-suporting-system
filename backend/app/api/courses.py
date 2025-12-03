"""
Courses API
Integration with HCMUT DataCore for course information
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any, Optional
import httpx

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.database import User, Student, Subject

router = APIRouter()

# HCMUT DataCore service URL
# Use localhost when running backend outside Docker
import os
DATACORE_URL = os.getenv("HCMUT_DATACORE_URL", "http://localhost:3002")


@router.get("/my-courses")
async def get_my_courses(
    mode: Optional[str] = None,  # Add mode parameter
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get courses for current user from database
    Returns subjects the user is enrolled in (student) or teaching (tutor)
    
    Args:
        mode: Optional role to get courses for ('student' or 'tutor').
              If not provided, uses current_user.role.
    """
    
    # Determine which role to fetch courses for
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
    
    courses = []
    
    try:
        if active_role == 'student':
            # Get distinct subjects from sessions student is enrolled in
            # No need to check Student table - enrollment creates SessionParticipant directly
            from app.models.database import Session, SessionParticipant
            
            # Get subjects with session count and tutor_id
            # Group by both subject and tutor since a student enrolls with a specific tutor
            subjects_result = await db.execute(
                select(
                    Subject,
                    Session.tutor_id,
                    func.count(func.distinct(Session.session_id)).label('session_count')
                )
                .join(Session, Subject.subject_id == Session.subject_id)
                .join(SessionParticipant, Session.session_id == SessionParticipant.session_id)
                .where(SessionParticipant.user_id == current_user.user_id)
                .where(SessionParticipant.role == 'student')
                .group_by(Subject.subject_id, Session.tutor_id)
            )
            results = subjects_result.all()
            
            courses = [
                {
                    "subject_id": subject.subject_id,
                    "subject_code": subject.subject_code,
                    "subject_name": subject.subject_name,
                    "department": subject.department,
                    "credits": subject.credits or 4,
                    "session_count": session_count,
                    "tutor_id": tutor_id
                }
                for subject, tutor_id, session_count in results
            ]
        
        elif active_role == 'tutor':
            # Get tutor record
            from app.models.database import Tutor, Session, TutorRegistration
            
            tutor_result = await db.execute(
                select(Tutor).where(Tutor.user_id == current_user.user_id)
            )
            tutor = tutor_result.scalar_one_or_none()
            
            if tutor:
                # Get subjects from sessions (with session counts)
                subjects_with_sessions = await db.execute(
                    select(
                        Subject,
                        func.count(Session.session_id).label('session_count')
                    )
                    .join(Session, Subject.subject_id == Session.subject_id)
                    .where(Session.tutor_id == tutor.tutor_id)
                    .group_by(Subject.subject_id)
                )
                
                session_results = subjects_with_sessions.all()
                
                # Get subjects from pending/approved registrations (with total_sessions)
                registered_subjects = await db.execute(
                    select(Subject, TutorRegistration.status, TutorRegistration.total_sessions, TutorRegistration.subject_id)
                    .join(TutorRegistration, Subject.subject_id == TutorRegistration.subject_id)
                    .where(TutorRegistration.tutor_id == tutor.tutor_id)
                    .where(TutorRegistration.status.in_(['pending', 'approved']))
                )
                
                registration_results = registered_subjects.all()
                
                # Merge both lists
                courses_dict = {}
                
                # Add subjects with sessions
                for subject, session_count in session_results:
                    courses_dict[subject.subject_id] = {
                        "subject_id": subject.subject_id,
                        "subject_code": subject.subject_code,
                        "subject_name": subject.subject_name,
                        "department": subject.department,
                        "credits": subject.credits or 4,
                        "session_count": session_count,
                        "status": "active"
                    }
                
                # Add pending/approved registrations
                # Only show subjects without actual sessions (registration only, no sessions yet)
                for subject, reg_status, total_sessions, subject_id in registration_results:
                    if subject.subject_id not in courses_dict:
                        # Don't show phantom sessions - only count actual sessions from database
                        # If approved but no sessions created yet, show 0
                        courses_dict[subject.subject_id] = {
                            "subject_id": subject.subject_id,
                            "subject_code": subject.subject_code,
                            "subject_name": subject.subject_name,
                            "department": subject.department,
                            "credits": subject.credits or 4,
                            "session_count": 0,  # Always 0 for registrations without actual sessions
                            "status": reg_status
                        }
                
                courses = list(courses_dict.values())
        
        return courses
        
    except Exception as e:
        # Return empty list on error
        return []


@router.get("/courses/{course_code}")
async def get_course_info(
    course_code: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed information about a specific course"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DATACORE_URL}/api/courses/{course_code}",
                timeout=10.0
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Course not found")
            
            response.raise_for_status()
            data = response.json()
            
            return data.get('data', {})
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="DataCore service timeout")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"DataCore service error: {str(e)}")


@router.get("/subjects")
async def get_subjects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all available subjects from database"""
    
    query = select(Subject).order_by(Subject.subject_code)
    result = await db.execute(query)
    subjects = result.scalars().all()
    
    return [
        {
            "subject_id": subject.subject_id,
            "subject_code": subject.subject_code,
            "subject_name": subject.subject_name,
            "department": subject.department,
            "credits": subject.credits,
            "description": subject.description
        }
        for subject in subjects
    ]


@router.get("/subjects/{subject_id}")
async def get_subject_by_id(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get subject details by ID"""
    
    result = await db.execute(
        select(Subject).where(Subject.subject_id == subject_id)
    )
    subject = result.scalar_one_or_none()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Count sessions for this subject
    from app.models.database import Session
    session_count_result = await db.execute(
        select(Session).where(Session.subject_id == subject_id)
    )
    sessions = session_count_result.scalars().all()
    
    return {
        "subject_id": subject.subject_id,
        "subject_code": subject.subject_code,
        "subject_name": subject.subject_name,
        "department": subject.department,
        "credits": subject.credits,
        "description": subject.description,
        "session_count": len(sessions)
    }


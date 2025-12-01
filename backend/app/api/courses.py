"""
Courses API
Integration with HCMUT DataCore for course information
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get courses for current user from database
    Returns subjects the user is enrolled in (student) or teaching (tutor)
    """
    
    courses = []
    
    try:
        if current_user.role == 'student':
            # Get student record
            student_result = await db.execute(
                select(Student).where(Student.user_id == current_user.user_id)
            )
            student = student_result.scalar_one_or_none()
            
            if student:
                # Get distinct subjects from sessions student is enrolled in
                from app.models.database import Session, SessionParticipant
                subjects_result = await db.execute(
                    select(Subject)
                    .join(Session, Subject.subject_id == Session.subject_id)
                    .join(SessionParticipant, Session.session_id == SessionParticipant.session_id)
                    .where(SessionParticipant.user_id == current_user.user_id)
                    .where(SessionParticipant.role == 'student')
                    .distinct()
                )
                subjects = subjects_result.scalars().all()
                
                courses = [
                    {
                        "subject_id": subject.subject_id,
                        "subject_code": subject.subject_code,
                        "subject_name": subject.subject_name,
                        "department": subject.department,
                        "credits": subject.credits or 4
                    }
                    for subject in subjects
                ]
        
        elif current_user.role == 'tutor':
            # Get tutor record
            from app.models.database import Tutor, Session, TutorRegistration
            tutor_result = await db.execute(
                select(Tutor).where(Tutor.user_id == current_user.user_id)
            )
            tutor = tutor_result.scalar_one_or_none()
            
            if tutor:
                # Get subjects from both:
                # 1. Approved registrations (subjects tutor is approved to teach)
                # 2. Active sessions (subjects tutor is currently teaching)
                
                # Get subjects from approved registrations
                registered_subjects_result = await db.execute(
                    select(Subject)
                    .join(TutorRegistration, Subject.subject_id == TutorRegistration.subject_id)
                    .where(
                        TutorRegistration.tutor_id == tutor.tutor_id,
                        TutorRegistration.status == 'approved'
                    )
                    .distinct()
                )
                registered_subjects = registered_subjects_result.scalars().all()
                
                # Get subjects from active sessions
                session_subjects_result = await db.execute(
                    select(Subject)
                    .join(Session, Subject.subject_id == Session.subject_id)
                    .where(Session.tutor_id == tutor.tutor_id)
                    .distinct()
                )
                session_subjects = session_subjects_result.scalars().all()
                
                # Merge both lists (remove duplicates by subject_id)
                subject_dict = {}
                for subject in registered_subjects + session_subjects:
                    if subject.subject_id not in subject_dict:
                        subject_dict[subject.subject_id] = subject
                
                courses = [
                    {
                        "subject_id": subject.subject_id,
                        "subject_code": subject.subject_code,
                        "subject_name": subject.subject_name,
                        "department": subject.department,
                        "credits": subject.credits or 4
                    }
                    for subject in subject_dict.values()
                ]
        
        return courses
        
    except Exception as e:
        print(f"Error fetching courses: {e}")
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


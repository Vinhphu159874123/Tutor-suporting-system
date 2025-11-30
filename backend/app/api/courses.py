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
    Get courses for current user from HCMUT DataCore
    Only available for students
    """
    
    if current_user.role != 'student':
        raise HTTPException(status_code=403, detail="Only students can access courses")
    
    # Get student_code from Student table
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.user_id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    student_code = student.student_code
    
    # Call HCMUT DataCore API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DATACORE_URL}/api/students/{student_code}/courses",
                timeout=10.0
            )
            
            if response.status_code == 404:
                return []
            
            response.raise_for_status()
            data = response.json()
            
            return data.get('data', [])
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="DataCore service timeout")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"DataCore service error: {str(e)}")


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


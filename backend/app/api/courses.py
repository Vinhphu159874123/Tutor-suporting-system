"""Courses API — thin controller, delegates to CoursesService"""
from fastapi import APIRouter, Depends
from typing import Optional
from app.core.dependencies import get_current_user, get_courses_service
from app.models.database import User
from app.services.courses_service import CoursesService

router = APIRouter()

@router.get("/my-courses")
async def get_my_courses(
    mode: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    svc: CoursesService = Depends(get_courses_service),
):
    return await svc.get_my_courses(current_user, mode)

@router.get("/courses/{course_code}")
async def get_course_info(
    course_code: str,
    current_user: User = Depends(get_current_user),
    svc: CoursesService = Depends(get_courses_service),
):
    return await svc.get_course_by_code(course_code)

@router.get("/subjects")
async def get_subjects(
    current_user: User = Depends(get_current_user),
    svc: CoursesService = Depends(get_courses_service),
):
    return await svc.get_all_subjects()

@router.get("/subjects/{subject_id}")
async def get_subject_by_id(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    svc: CoursesService = Depends(get_courses_service),
):
    return await svc.get_subject_by_id(subject_id)

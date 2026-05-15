"""Progress API — thin controller, delegates to ProgressService"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from app.core.dependencies import get_current_user, get_progress_service
from app.models.database import User
from app.services.progress_service import ProgressService

router = APIRouter()

@router.get("/students/{student_id}/progress")
async def get_student_progress(
    student_id: int,
    subject_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    svc: ProgressService = Depends(get_progress_service),
):
    return await svc.get_student_progress(
        student_id, subject_id=subject_id,
        start_date=start_date, end_date=end_date)

@router.get("/courses/{subject_id}/study-progress")
async def get_course_study_progress(
    subject_id: int,
    tutor_id: Optional[int] = Query(None),
    mode: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    svc: ProgressService = Depends(get_progress_service),
):
    return await svc.get_course_study_progress(
        subject_id, current_user, tutor_id=tutor_id, mode=mode)
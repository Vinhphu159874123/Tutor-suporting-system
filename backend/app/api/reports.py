"""Reports API — thin controller, delegates to ReportsService"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from app.core.dependencies import get_current_user, get_reports_service
from app.models.database import User
from app.services.reports_service import ReportsService

router = APIRouter()

@router.get("/statistics")
async def get_system_statistics(
    current_user: User = Depends(get_current_user),
    svc: ReportsService = Depends(get_reports_service),
):
    return await svc.get_system_statistics()

@router.get("/courses")
async def get_course_reports(
    current_user: User = Depends(get_current_user),
    svc: ReportsService = Depends(get_reports_service),
):
    return await svc.get_course_reports()

@router.get("/tutor/{tutor_id}")
async def get_tutor_performance(
    tutor_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    svc: ReportsService = Depends(get_reports_service),
):
    return await svc.get_tutor_performance(tutor_id, start_date, end_date)

@router.get("/student/{student_id}")
async def get_student_progress_report(
    student_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    svc: ReportsService = Depends(get_reports_service),
):
    return await svc.get_student_progress_report(student_id, start_date, end_date)
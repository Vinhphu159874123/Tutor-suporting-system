"""
Report Schemas - Course and Tutor Activity Reports
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal


class CourseReportCreate(BaseModel):
    """Generate course report"""
    subject_id: int
    report_period_start: date
    report_period_end: date


class CourseReportResponse(BaseModel):
    """Course report response"""
    report_id: int
    subject_id: int
    report_period_start: date
    report_period_end: date
    total_sessions: int
    total_students: int
    total_tutors: int
    avg_session_rating: Optional[Decimal]
    completion_rate: Optional[Decimal]
    metrics: Dict[str, Any]
    generated_at: datetime
    
    # Joined data
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    
    class Config:
        from_attributes = True


class TutorActivityReportCreate(BaseModel):
    """Generate tutor activity report"""
    tutor_id: int
    report_period_start: date
    report_period_end: date


class TutorActivityReportResponse(BaseModel):
    """Tutor activity report response"""
    report_id: int
    tutor_id: int
    report_period_start: date
    report_period_end: date
    total_sessions: int
    completed_sessions: int
    avg_rating: Optional[Decimal]
    total_students: int
    total_hours: int
    social_activity_score: Optional[Decimal]
    activity_details: Dict[str, Any]
    generated_at: datetime
    
    # Joined data
    tutor_name: Optional[str] = None
    tutor_email: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReportFilters(BaseModel):
    """Common report filters"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    subject_id: Optional[int] = None
    tutor_id: Optional[int] = None
    student_id: Optional[int] = None
    status: Optional[str] = None


# Deprecated - Keep for backward compatibility
class TutorPerformanceReport(BaseModel):
    """Tutor performance metrics (DEPRECATED - use TutorActivityReportResponse)"""
    tutor_id: int
    tutor_name: str
    total_sessions: int
    completed_sessions: int
    cancelled_sessions: int
    average_rating: float
    total_hours: float
    subjects_taught: list[str]
    period_start: datetime
    period_end: datetime

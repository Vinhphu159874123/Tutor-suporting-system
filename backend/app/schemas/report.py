"""
Reports Schemas - Request/Response DTOs
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class TutorPerformanceReport(BaseModel):
    """Tutor performance metrics"""
    tutor_id: int
    tutor_name: str
    total_sessions: int
    completed_sessions: int
    cancelled_sessions: int
    average_rating: float
    total_hours: float
    subjects_taught: List[str]
    period_start: datetime
    period_end: datetime


class StudentProgressReport(BaseModel):
    """Student progress tracking"""
    student_id: int
    student_name: str
    total_sessions: int
    subjects: List[str]
    average_session_rating: float
    attendance_rate: float
    period_start: datetime
    period_end: datetime


class SystemStatistics(BaseModel):
    """Overall system statistics"""
    total_users: int
    total_tutors: int
    total_students: int
    total_sessions: int
    active_sessions: int
    completion_rate: float
    average_rating: float
    generated_at: datetime


class ReportFilter(BaseModel):
    """Common report filters"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[int] = None
    subject: Optional[str] = None

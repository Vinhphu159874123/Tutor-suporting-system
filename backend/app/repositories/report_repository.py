"""
Report Repository
Database operations for reports/analytics queries
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime
from app.models.database import (
    Session, SessionFeedback, ProgressTracking,
    Subject, Student, Tutor,
)


class ReportRepository:
    """Handle all database operations for Reports module"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_sessions(self) -> int:
        return (await self.db.execute(select(func.count(Session.session_id)))).scalar() or 0

    async def count_completed_sessions(self) -> int:
        return (await self.db.execute(
            select(func.count(Session.session_id)).where(Session.status == "completed")
        )).scalar() or 0

    async def count_students(self) -> int:
        return (await self.db.execute(select(func.count(Student.student_id)))).scalar() or 0

    async def avg_feedback_rating(self) -> Optional[float]:
        return (await self.db.execute(select(func.avg(SessionFeedback.rating)))).scalar()

    async def get_course_report_rows(self) -> list:
        query = select(
            Subject.subject_id, Subject.subject_name, Subject.subject_code,
            func.count(Session.session_id).label("total_sessions"),
            func.count(Session.session_id).filter(Session.status == "completed").label("completed_sessions"),
            func.avg(ProgressTracking.understanding_level).label("avg_score"),
        ).outerjoin(
            Session, Session.subject_id == Subject.subject_id
        ).outerjoin(
            ProgressTracking, ProgressTracking.session_id == Session.session_id
        ).group_by(Subject.subject_id, Subject.subject_name, Subject.subject_code)
        return (await self.db.execute(query)).all()

    async def get_tutor_performance_row(
        self, tutor_id: int, *, start_date=None, end_date=None
    ):
        query = select(
            func.count(Session.session_id).label("total_sessions"),
            func.count(Session.session_id).filter(Session.status == "completed").label("completed_sessions"),
            func.avg(SessionFeedback.rating).label("avg_rating"),
        ).outerjoin(
            SessionFeedback, SessionFeedback.session_id == Session.session_id
        ).where(Session.tutor_id == tutor_id)
        if start_date:
            query = query.where(Session.start_time >= start_date)
        if end_date:
            query = query.where(Session.start_time <= end_date)
        return (await self.db.execute(query)).first()

    async def get_student_progress_row(
        self, student_id: int, *, start_date=None, end_date=None
    ):
        query = select(
            func.count(Session.session_id).label("total_sessions"),
            func.count(Session.session_id).filter(Session.status == "completed").label("attended_sessions"),
            func.avg(ProgressTracking.understanding_level).label("avg_understanding"),
        ).outerjoin(
            ProgressTracking, ProgressTracking.session_id == Session.session_id
        ).where(Session.student_id == student_id)
        if start_date:
            query = query.where(Session.start_time >= start_date)
        if end_date:
            query = query.where(Session.start_time <= end_date)
        return (await self.db.execute(query)).first()

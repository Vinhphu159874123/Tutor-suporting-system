"""
Progress Repository
Database operations for student progress tracking
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from app.models.database import (
    ProgressTracking, Session, Subject, Student, Tutor,
    SessionParticipant, Attendance, User,
)


class ProgressRepository:
    """Handle all database operations for Progress module"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_student_progress(
        self, student_id: int, *,
        subject_id: Optional[int] = None,
        start_date=None, end_date=None,
    ) -> list:
        query = (select(ProgressTracking, Session, Subject)
                 .join(Session, ProgressTracking.session_id == Session.session_id)
                 .join(Subject, ProgressTracking.subject_id == Subject.subject_id)
                 .where(ProgressTracking.student_id == student_id))
        if subject_id:
            query = query.where(ProgressTracking.subject_id == subject_id)
        if start_date:
            query = query.where(Session.start_time >= start_date)
        if end_date:
            query = query.where(Session.start_time <= end_date)
        return (await self.db.execute(query.order_by(Session.start_time.desc()))).all()

    async def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        return (await self.db.execute(
            select(Subject).where(Subject.subject_id == subject_id)
        )).scalar_one_or_none()

    async def get_tutor_by_user_id(self, user_id: int) -> Optional[Tutor]:
        return (await self.db.execute(
            select(Tutor).where(Tutor.user_id == user_id)
        )).scalar_one_or_none()

    async def get_student_by_user_id(self, user_id: int) -> Optional[Student]:
        return (await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )).scalar_one_or_none()

    async def get_sessions_for_tutor_subject(
        self, subject_id: int, tutor_id: int
    ) -> List[Session]:
        return (await self.db.execute(
            select(Session).where(and_(
                Session.subject_id == subject_id,
                Session.tutor_id == tutor_id))
            .order_by(Session.scheduled_date, Session.start_time)
        )).scalars().all()

    async def get_students_in_sessions(self, session_ids: list) -> list:
        return (await self.db.execute(
            select(User, Student, SessionParticipant.user_id)
            .join(Student, User.user_id == Student.user_id)
            .join(SessionParticipant, User.user_id == SessionParticipant.user_id)
            .where(and_(SessionParticipant.session_id.in_(session_ids),
                        SessionParticipant.role == 'student')).distinct()
        )).all()

    async def get_attendance_for_student_sessions(
        self, student_id: int, session_ids: list
    ) -> List[Attendance]:
        return (await self.db.execute(
            select(Attendance).where(and_(
                Attendance.student_id == student_id,
                Attendance.session_id.in_(session_ids)))
        )).scalars().all()

    async def get_student_sessions_for_subject(
        self, subject_id: int, user_id: int, tutor_id: Optional[int] = None
    ) -> List[Session]:
        sq = select(Session).where(Session.subject_id == subject_id)
        if tutor_id:
            sq = sq.where(Session.tutor_id == tutor_id)
        return (await self.db.execute(
            sq.join(SessionParticipant, Session.session_id == SessionParticipant.session_id)
            .where(and_(SessionParticipant.user_id == user_id,
                        SessionParticipant.role == 'student'))
            .order_by(Session.scheduled_date, Session.start_time)
        )).scalars().all()

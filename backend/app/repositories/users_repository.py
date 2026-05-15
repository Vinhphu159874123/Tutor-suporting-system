"""
Users Repository
Database operations for user profile, search, dashboard
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case, distinct, or_
from typing import List, Optional
from datetime import date
from app.models.database import (
    User, Session, SessionParticipant, SessionFeedback,
    Student, Tutor, Attendance, TutorRegistration,
)


class UsersRepository:
    """Handle all database operations for Users module"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(self, query: str, limit: int = 10) -> List[User]:
        search_filter = or_(
            User.full_name.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%"),
        )
        result = await self.db.execute(
            select(User).where(and_(search_filter, User.is_active == True)).limit(limit)
        )
        return result.scalars().all()

    async def get_student_by_user_id(self, user_id: int) -> Optional[Student]:
        return (await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )).scalar_one_or_none()

    async def get_tutor_by_user_id(self, user_id: int) -> Optional[Tutor]:
        return (await self.db.execute(
            select(Tutor).where(Tutor.user_id == user_id)
        )).scalar_one_or_none()

    async def get_all(self, *, skip: int = 0, limit: int = 100,
                      role: Optional[str] = None) -> List[User]:
        query = select(User)
        if role:
            query = query.where(User.role == role)
        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_student(self, student: Student) -> Student:
        self.db.add(student)
        await self.db.commit()
        return student

    async def create_tutor(self, tutor: Tutor) -> Tutor:
        self.db.add(tutor)
        await self.db.commit()
        return tutor

    async def refresh(self, obj) -> None:
        await self.db.refresh(obj)

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    # --- Stats queries ---
    async def count_total_sessions(self) -> int:
        return (await self.db.execute(select(func.count(Session.session_id)))).scalar() or 0

    async def count_pending_registrations(self) -> int:
        return (await self.db.execute(
            select(func.count(TutorRegistration.registration_id))
            .where(TutorRegistration.status == 'pending')
        )).scalar() or 0

    async def count_pending_sessions(self) -> int:
        return (await self.db.execute(
            select(func.count(Session.session_id))
            .where(Session.status.in_(['draft', 'published', 'pending_assignment']))
        )).scalar() or 0

    async def avg_feedback_rating(self) -> Optional[float]:
        return (await self.db.execute(select(func.avg(SessionFeedback.rating)))).scalar()

    async def count_active_students(self) -> int:
        return (await self.db.execute(
            select(func.count(distinct(SessionParticipant.user_id)))
            .where(SessionParticipant.role == 'student')
        )).scalar() or 0

    async def count_tutors(self) -> int:
        return (await self.db.execute(select(func.count(Tutor.tutor_id)))).scalar() or 0

    async def count_completed_sessions(self) -> int:
        return (await self.db.execute(
            select(func.count(Session.session_id)).where(Session.status == 'completed')
        )).scalar() or 0

    async def count_attendance(self) -> int:
        return (await self.db.execute(select(func.count(Attendance.attendance_id)))).scalar() or 0

    async def get_student_session_count(self, user_id: int) -> int:
        return (await self.db.execute(
            select(func.count(SessionParticipant.participant_id))
            .where(and_(SessionParticipant.user_id == user_id, SessionParticipant.role == 'student'))
        )).scalar() or 0

    async def get_student_attendance_count(self, student_id: int) -> int:
        return (await self.db.execute(
            select(func.count(distinct(Attendance.session_id)))
            .where(Attendance.student_id == student_id)
        )).scalar() or 0

    async def get_student_upcoming_count(self, user_id: int, today: date) -> int:
        return (await self.db.execute(
            select(func.count(SessionParticipant.participant_id))
            .select_from(SessionParticipant)
            .join(Session, SessionParticipant.session_id == Session.session_id)
            .where(and_(SessionParticipant.user_id == user_id,
                        SessionParticipant.role == 'student',
                        Session.scheduled_date >= today))
        )).scalar() or 0

    async def get_tutor_session_stats(self, tutor_id: int):
        return (await self.db.execute(
            select(func.count(Session.session_id).label('total'),
                   func.sum(case((Session.status == 'completed', 1), else_=0)).label('completed'),
                   func.sum(case((Session.status.in_(['confirmed', 'ongoing', 'published']), 1), else_=0)).label('upcoming'))
            .where(Session.tutor_id == tutor_id)
        )).first()

    async def get_tutor_avg_rating(self, tutor_id: int) -> Optional[float]:
        return (await self.db.execute(
            select(func.avg(SessionFeedback.rating))
            .select_from(SessionFeedback).join(Session)
            .where(Session.tutor_id == tutor_id)
        )).scalar()

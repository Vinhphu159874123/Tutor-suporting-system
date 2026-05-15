"""
Course Repository
Database operations for Subject (course) model
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Tuple, Any
from app.models.database import (
    Subject, Session, SessionParticipant, Tutor, TutorRegistration,
)


class CourseRepository:
    """Handle all database operations for Subject/Course model"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_code(self, course_code: str) -> Optional[Subject]:
        result = await self.db.execute(
            select(Subject).where(Subject.subject_code == course_code)
        )
        return result.scalar_one_or_none()

    async def get_all_ordered(self) -> List[Subject]:
        result = await self.db.execute(
            select(Subject).order_by(Subject.subject_code)
        )
        return result.scalars().all()

    async def get_by_id(self, subject_id: int) -> Optional[Subject]:
        result = await self.db.execute(
            select(Subject).where(Subject.subject_id == subject_id)
        )
        return result.scalar_one_or_none()

    async def count_sessions_by_subject(self, subject_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Session.session_id)).where(Session.subject_id == subject_id)
        )
        return result.scalar() or 0

    async def get_student_courses(self, user_id: int) -> list:
        r = await self.db.execute(
            select(Subject, Session.tutor_id,
                   func.count(func.distinct(Session.session_id)).label('sc'))
            .join(Session, Subject.subject_id == Session.subject_id)
            .join(SessionParticipant, Session.session_id == SessionParticipant.session_id)
            .where(SessionParticipant.user_id == user_id, SessionParticipant.role == 'student')
            .group_by(Subject.subject_id, Session.tutor_id))
        return r.all()

    async def get_tutor_by_user_id(self, user_id: int) -> Optional[Tutor]:
        result = await self.db.execute(select(Tutor).where(Tutor.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_tutor_session_courses(self, tutor_id: int) -> list:
        return (await self.db.execute(
            select(Subject, func.count(Session.session_id).label('sc'))
            .join(Session, Subject.subject_id == Session.subject_id)
            .where(Session.tutor_id == tutor_id).group_by(Subject.subject_id)
        )).all()

    async def get_tutor_registered_courses(self, tutor_id: int) -> list:
        return (await self.db.execute(
            select(Subject, TutorRegistration.status)
            .join(TutorRegistration, Subject.subject_id == TutorRegistration.subject_id)
            .where(TutorRegistration.tutor_id == tutor_id,
                   TutorRegistration.status.in_(['pending', 'approved']))
        )).all()

"""
Schedule Preference Repository
Database operations for SchedulePreference model
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from app.models.database import SchedulePreference, Student, Subject, User


class SchedulePreferenceRepository:
    """Handle all database operations for SchedulePreference module"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_student_by_user_id(self, user_id: int) -> Optional[Student]:
        return (await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )).scalar_one_or_none()

    async def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        return (await self.db.execute(
            select(Subject).where(Subject.subject_id == subject_id)
        )).scalar_one_or_none()

    async def get_pending_for_student_subject(self, student_id: int, subject_id: int) -> Optional[SchedulePreference]:
        return (await self.db.execute(
            select(SchedulePreference).where(and_(
                SchedulePreference.student_id == student_id,
                SchedulePreference.subject_id == subject_id,
                SchedulePreference.status == 'pending'))
        )).scalar_one_or_none()

    async def create(self, pref: SchedulePreference) -> SchedulePreference:
        self.db.add(pref)
        await self.db.commit()
        await self.db.refresh(pref)
        return pref

    async def get_by_student(self, student_id: int, status_filter: Optional[str] = None) -> list:
        query = (select(SchedulePreference, Subject)
                 .join(Subject, SchedulePreference.subject_id == Subject.subject_id)
                 .where(SchedulePreference.student_id == student_id))
        if status_filter:
            query = query.where(SchedulePreference.status == status_filter)
        return (await self.db.execute(query.order_by(SchedulePreference.created_at.desc()))).all()

    async def get_with_subject(self, preference_id: int):
        return (await self.db.execute(
            select(SchedulePreference, Subject)
            .join(Subject, SchedulePreference.subject_id == Subject.subject_id)
            .where(SchedulePreference.preference_id == preference_id)
        )).one_or_none()

    async def get_by_id(self, preference_id: int) -> Optional[SchedulePreference]:
        return (await self.db.execute(
            select(SchedulePreference).where(SchedulePreference.preference_id == preference_id)
        )).scalar_one_or_none()

    async def delete(self, pref: SchedulePreference) -> None:
        await self.db.delete(pref)
        await self.db.commit()

    async def get_statistics_rows(self, subject_id: Optional[int], min_requests: int) -> list:
        query = (select(
            SchedulePreference.subject_id,
            Subject.subject_code, Subject.subject_name,
            func.count(SchedulePreference.preference_id).label('total_requests'),
            func.avg(SchedulePreference.session_duration).label('avg_duration'),
            func.avg(SchedulePreference.total_sessions).label('avg_sessions'),
            func.min(SchedulePreference.preferred_start_date).label('earliest_date'),
            func.max(SchedulePreference.preferred_start_date).label('latest_date'))
            .join(Subject, SchedulePreference.subject_id == Subject.subject_id)
            .where(SchedulePreference.status == 'pending')
            .group_by(SchedulePreference.subject_id, Subject.subject_code, Subject.subject_name)
            .having(func.count(SchedulePreference.preference_id) >= min_requests))
        if subject_id:
            query = query.where(SchedulePreference.subject_id == subject_id)
        return (await self.db.execute(
            query.order_by(func.count(SchedulePreference.preference_id).desc())
        )).all()

    async def get_format_distribution(self, subject_id: int) -> dict:
        rows = (await self.db.execute(
            select(SchedulePreference.session_format,
                   func.count(SchedulePreference.preference_id).label('count'))
            .where(and_(SchedulePreference.subject_id == subject_id,
                        SchedulePreference.status == 'pending'))
            .group_by(SchedulePreference.session_format)
        )).all()
        return {r.session_format: r.count for r in rows}

    async def get_duration_distribution(self, subject_id: int) -> dict:
        rows = (await self.db.execute(
            select(SchedulePreference.session_duration,
                   func.count(SchedulePreference.preference_id).label('count'))
            .where(and_(SchedulePreference.subject_id == subject_id,
                        SchedulePreference.status == 'pending'))
            .group_by(SchedulePreference.session_duration)
        )).all()
        return {r.session_duration: r.count for r in rows}

    async def get_time_slots(self, subject_id: int) -> list:
        return (await self.db.execute(
            select(SchedulePreference.available_time_slots)
            .where(and_(SchedulePreference.subject_id == subject_id,
                        SchedulePreference.status == 'pending'))
        )).all()

    async def get_subject_details(self, subject_id: int) -> list:
        return (await self.db.execute(
            select(SchedulePreference, Student, User, Subject)
            .join(Student, SchedulePreference.student_id == Student.student_id)
            .join(User, Student.user_id == User.user_id)
            .join(Subject, SchedulePreference.subject_id == Subject.subject_id)
            .where(and_(SchedulePreference.subject_id == subject_id,
                        SchedulePreference.status == 'pending'))
            .order_by(SchedulePreference.created_at.desc())
        )).all()

    # --- Transaction helpers ---
    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def refresh(self, obj) -> None:
        await self.db.refresh(obj)

"""
Tutor Repository - Database Access Layer
Pure database operations, no business logic
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_, text, distinct
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models.database import (
    Tutor, TutorRegistration, TutorAvailability,
    Subject, User, Session as SessionModel,
    SessionParticipant, SessionSchedule, SessionFeedback,
)


class TutorRepository:
    """Handle database operations for Tutor model"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Transaction helpers ──────────────────────────────────────────────
    async def commit(self):
        await self.db.commit()

    async def rollback(self):
        await self.db.rollback()

    async def refresh(self, obj, attrs=None):
        if attrs:
            await self.db.refresh(obj, attrs)
        else:
            await self.db.refresh(obj)

    def add(self, obj):
        self.db.add(obj)

    # ── Core CRUD ────────────────────────────────────────────────────────

    async def get_by_id(self, tutor_id: int) -> Optional[Tutor]:
        result = await self.db.execute(select(Tutor).where(Tutor.tutor_id == tutor_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Optional[Tutor]:
        result = await self.db.execute(select(Tutor).where(Tutor.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100,
                      subject: Optional[str] = None,
                      min_rating: Optional[float] = None) -> List[Tutor]:
        query = select(Tutor)
        if min_rating is not None:
            query = query.where(Tutor.rating >= min_rating)
        query = query.offset(skip).limit(limit)
        return (await self.db.execute(query)).scalars().all()

    async def create(self, tutor_data: dict) -> Tutor:
        tutor = Tutor(**tutor_data)
        self.db.add(tutor)
        await self.db.commit()
        await self.db.refresh(tutor)
        return tutor

    async def update(self, tutor_id: int, tutor_data: dict) -> Optional[Tutor]:
        tutor = await self.get_by_id(tutor_id)
        if not tutor:
            return None
        for key, value in tutor_data.items():
            setattr(tutor, key, value)
        await self.db.commit()
        await self.db.refresh(tutor)
        return tutor

    async def delete(self, tutor_id: int) -> bool:
        tutor = await self.get_by_id(tutor_id)
        if not tutor:
            return False
        await self.db.delete(tutor)
        await self.db.commit()
        return True

    async def exists_by_user_id(self, user_id: int) -> bool:
        result = await self.db.execute(select(Tutor.tutor_id).where(Tutor.user_id == user_id))
        return result.scalar_one_or_none() is not None

    # ── User lookups ─────────────────────────────────────────────────────

    async def get_users_by_ids(self, user_ids: list) -> list:
        return (await self.db.execute(
            select(User).where(User.user_id.in_(user_ids))
        )).scalars().all()

    async def get_user_by_id(self, user_id: int):
        return (await self.db.execute(
            select(User).where(User.user_id == user_id)
        )).scalar_one_or_none()

    # ── Availability ─────────────────────────────────────────────────────

    async def get_availability(self, tutor_id: int) -> list:
        result = await self.db.execute(
            select(TutorAvailability)
            .where(TutorAvailability.tutor_id == tutor_id)
            .order_by(TutorAvailability.day_of_week, TutorAvailability.start_time))
        return result.scalars().all()

    async def delete_availability(self, tutor_id: int):
        await self.db.execute(
            delete(TutorAvailability).where(TutorAvailability.tutor_id == tutor_id))

    # ── Registration ─────────────────────────────────────────────────────

    async def get_subject(self, subject_id: int):
        return (await self.db.execute(
            select(Subject).where(Subject.subject_id == subject_id)
        )).scalar_one_or_none()

    async def get_registration(self, tutor_id: int, subject_id: int, statuses: list = None):
        q = select(TutorRegistration).where(
            TutorRegistration.tutor_id == tutor_id,
            TutorRegistration.subject_id == subject_id)
        if statuses:
            q = q.where(TutorRegistration.status.in_(statuses))
        return (await self.db.execute(q)).scalar_one_or_none()

    async def get_registration_by_id(self, registration_id: int):
        """Get registration with subject name and tutor"""
        result = (await self.db.execute(
            select(TutorRegistration, Subject.subject_name, Tutor)
            .join(Subject, TutorRegistration.subject_id == Subject.subject_id)
            .join(Tutor, TutorRegistration.tutor_id == Tutor.tutor_id)
            .where(TutorRegistration.registration_id == registration_id)
        )).first()
        return result

    async def get_registrations_with_subjects(self, tutor_id: int, status_filter: Optional[str] = None):
        q = (select(TutorRegistration, Subject)
             .join(Subject, TutorRegistration.subject_id == Subject.subject_id)
             .where(TutorRegistration.tutor_id == tutor_id))
        if status_filter:
            q = q.where(TutorRegistration.status == status_filter)
        return (await self.db.execute(q)).all()

    async def get_approved_registrations(self, tutor_id: int, exclude_subject_id: int = None):
        conditions = [
            TutorRegistration.tutor_id == tutor_id,
            TutorRegistration.status == 'approved'
        ]
        if exclude_subject_id:
            conditions.append(TutorRegistration.subject_id != exclude_subject_id)
        q = (select(TutorRegistration, Subject)
             .join(Subject, TutorRegistration.subject_id == Subject.subject_id)
             .where(and_(*conditions)))
        return (await self.db.execute(q)).all()

    async def get_approved_registrations_with_subjects(self, tutor_id: int):
        return (await self.db.execute(
            select(TutorRegistration, Subject)
            .join(Subject, TutorRegistration.subject_id == Subject.subject_id)
            .where(TutorRegistration.tutor_id == tutor_id,
                   TutorRegistration.status == 'approved')
        )).all()

    # ── Session Schedule ─────────────────────────────────────────────────

    async def get_session_schedules(self, tutor_id: int, subject_id: int):
        return (await self.db.execute(
            select(SessionSchedule).where(
                SessionSchedule.tutor_id == tutor_id,
                SessionSchedule.subject_id == subject_id)
        )).scalars().all()

    async def delete_session_schedules(self, tutor_id: int, subject_id: int):
        await self.db.execute(
            delete(SessionSchedule).where(
                SessionSchedule.tutor_id == tutor_id,
                SessionSchedule.subject_id == subject_id))

    async def get_active_schedule(self, tutor_id: int, subject_id: int,
                                   schedule_id: int = None):
        if schedule_id:
            q = select(SessionSchedule).where(SessionSchedule.schedule_id == schedule_id)
        else:
            q = select(SessionSchedule).where(
                SessionSchedule.tutor_id == tutor_id,
                SessionSchedule.subject_id == subject_id,
                SessionSchedule.is_active == True)
        return (await self.db.execute(q)).scalars().first()

    # ── Sessions ─────────────────────────────────────────────────────────

    async def get_sessions_for_tutor_subject(self, tutor_id: int, subject_id: int,
                                              date_from=None, date_to=None,
                                              statuses: list = None):
        q = select(SessionModel).where(
            SessionModel.tutor_id == tutor_id,
            SessionModel.subject_id == subject_id)
        if date_from:
            q = q.where(SessionModel.scheduled_date >= date_from)
        if date_to:
            q = q.where(SessionModel.scheduled_date <= date_to)
        if statuses:
            q = q.where(SessionModel.status.in_(statuses))
        if date_from:
            q = q.where(SessionModel.scheduled_date.isnot(None))
        return (await self.db.execute(q)).scalars().all()

    async def count_sessions(self, tutor_id: int, subject_id: int):
        return (await self.db.execute(
            select(func.count(SessionModel.session_id)).where(
                SessionModel.tutor_id == tutor_id,
                SessionModel.subject_id == subject_id)
        )).scalar() or 0

    # ── Course browsing (raw SQL) ────────────────────────────────────────

    async def get_available_courses_raw(self):
        query = text("""
            WITH
            session_stats AS (
                SELECT s.subject_id, s.tutor_id,
                    COUNT(DISTINCT s.session_id) as session_count,
                    MIN(s.scheduled_date) as start_date,
                    COUNT(DISTINCT CASE WHEN sp.role = 'student' THEN sp.user_id END) as student_count
                FROM tutor_system.session s
                LEFT JOIN tutor_system."SessionParticipant" sp ON sp.session_id = s.session_id
                GROUP BY s.subject_id, s.tutor_id
            ),
            rating_stats AS (
                SELECT s.subject_id, s.tutor_id,
                    AVG(sf.rating) as avg_rating, COUNT(sf.feedback_id) as feedback_count
                FROM tutor_system.sessionfeedback sf
                JOIN tutor_system.session s ON sf.session_id = s.session_id
                GROUP BY s.subject_id, s.tutor_id
            )
            SELECT tr.registration_id, tr.subject_id, tr.tutor_id, tr.max_students,
                tr.total_sessions, tr.start_date, tr.status,
                sub.subject_code, sub.subject_name, sub.department,
                u.full_name as tutor_name,
                COALESCE(ss.session_count, 0) as actual_session_count,
                ss.start_date as actual_start_date,
                COALESCE(ss.student_count, 0) as current_students,
                COALESCE(rs.avg_rating, 0.0) as avg_rating,
                COALESCE(rs.feedback_count, 0) as feedback_count
            FROM tutor_system.tutorregistration tr
            JOIN tutor_system.subject sub ON tr.subject_id = sub.subject_id
            JOIN tutor_system.tutor t ON tr.tutor_id = t.tutor_id
            JOIN tutor_system."User" u ON t.user_id = u.user_id
            LEFT JOIN session_stats ss ON ss.subject_id = tr.subject_id AND ss.tutor_id = tr.tutor_id
            LEFT JOIN rating_stats rs ON rs.subject_id = tr.subject_id AND rs.tutor_id = tr.tutor_id
            WHERE tr.status = 'approved'
        """)
        return (await self.db.execute(query)).fetchall()

    async def get_user_joined_courses(self, user_id: int):
        return (await self.db.execute(
            text("""SELECT DISTINCT s.subject_id, s.tutor_id
                    FROM tutor_system.session s
                    JOIN tutor_system."SessionParticipant" sp ON sp.session_id = s.session_id
                    WHERE sp.user_id = :user_id AND sp.role = 'student'"""),
            {"user_id": user_id}
        )).fetchall()

    # ── Course join ──────────────────────────────────────────────────────

    async def count_enrolled_students(self, subject_id: int, tutor_id: int):
        return (await self.db.scalar(
            select(func.count(func.distinct(SessionParticipant.user_id)))
            .join(SessionModel, SessionParticipant.session_id == SessionModel.session_id)
            .where(SessionModel.subject_id == subject_id,
                   SessionModel.tutor_id == tutor_id,
                   SessionParticipant.role == "student")
        )) or 0

    async def is_student_enrolled(self, subject_id: int, tutor_id: int, user_id: int):
        return await self.db.scalar(
            select(SessionParticipant)
            .join(SessionModel, SessionParticipant.session_id == SessionModel.session_id)
            .where(SessionModel.subject_id == subject_id,
                   SessionModel.tutor_id == tutor_id,
                   SessionParticipant.user_id == user_id,
                   SessionParticipant.role == "student"))

    async def get_course_sessions(self, subject_id: int, tutor_id: int):
        return (await self.db.execute(
            select(SessionModel).where(
                SessionModel.subject_id == subject_id,
                SessionModel.tutor_id == tutor_id)
        )).scalars().all()

    # ── Enrolled students ────────────────────────────────────────────────

    async def get_enrolled_students_for_courses(self, tutor_id: int, subject_id: int):
        return (await self.db.execute(
            select(User.user_id, User.full_name, User.email,
                   func.count(distinct(SessionParticipant.session_id)).label('sc'))
            .select_from(SessionParticipant)
            .join(SessionModel, SessionParticipant.session_id == SessionModel.session_id)
            .join(User, SessionParticipant.user_id == User.user_id)
            .where(SessionModel.subject_id == subject_id,
                   SessionModel.tutor_id == tutor_id,
                   SessionParticipant.role == "student")
            .group_by(User.user_id, User.full_name, User.email)
        )).all()

    # ── Schedule conflict check ──────────────────────────────────────────

    async def get_student_sessions(self, user_id: int):
        return (await self.db.execute(
            select(SessionModel)
            .join(SessionParticipant, SessionParticipant.session_id == SessionModel.session_id)
            .where(SessionParticipant.user_id == user_id,
                   SessionParticipant.role == 'student',
                   SessionModel.scheduled_date.isnot(None))
        )).scalars().all()

    async def get_course_sessions_by_registration(self, reg_id: int):
        return (await self.db.execute(
            text("""SELECT DISTINCT s.scheduled_date, s.start_time, s.end_time
                    FROM tutor_system.session s
                    JOIN tutor_system.tutorregistration tr
                         ON tr.subject_id = s.subject_id AND tr.tutor_id = s.tutor_id
                    WHERE tr.registration_id = :reg_id AND s.scheduled_date IS NOT NULL"""),
            {"reg_id": reg_id}
        )).fetchall()

    # ── Batch user/registration lookups ──────────────────────────────────

    async def get_approved_registrations_for_tutors(self, tutor_ids: list):
        return (await self.db.execute(
            select(TutorRegistration, Subject)
            .join(Subject, TutorRegistration.subject_id == Subject.subject_id)
            .where(and_(
                TutorRegistration.tutor_id.in_(tutor_ids),
                TutorRegistration.status == 'approved'))
        )).all()

    async def execute_raw(self, stmt, params=None):
        if params:
            return await self.db.execute(stmt, params)
        return await self.db.execute(stmt)

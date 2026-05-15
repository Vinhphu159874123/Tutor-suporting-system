"""
Session Repository - Database Access Layer
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete, text, desc, asc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date

from app.models.database import (
    Session as SessionModel,
    SessionParticipant,
    SessionMaterial,
    SessionFeedback,
    SessionSchedule,
    Tutor,
    Student,
    User,
    Subject,
    Attendance,
    Notifications,
    TutorRegistration,
)


class SessionRepository:
    """Handle database operations for Session model"""

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

    async def flush(self):
        await self.db.flush()

    # ── Core CRUD ────────────────────────────────────────────────────────

    async def get_by_id(self, session_id: int) -> Optional[SessionModel]:
        """Get session by ID with eager loading"""
        result = await self.db.execute(
            select(SessionModel)
            .options(
                selectinload(SessionModel.tutor).selectinload(Tutor.user),
                selectinload(SessionModel.participants).selectinload(SessionParticipant.user),
                selectinload(SessionModel.subject)
            )
            .where(SessionModel.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100,
        tutor_id: Optional[int] = None, student_id: Optional[int] = None,
        subject_id: Optional[int] = None, status: Optional[str] = None
    ) -> List[SessionModel]:
        """Get all sessions with filters and optimized eager loading"""
        query = select(SessionModel)
        if tutor_id:
            query = query.where(SessionModel.tutor_id == tutor_id)
        if subject_id:
            query = query.where(SessionModel.subject_id == subject_id)
        if status:
            query = query.where(SessionModel.status == status)
        if student_id:
            query = (query.join(SessionParticipant, SessionModel.session_id == SessionParticipant.session_id)
                     .where(and_(SessionParticipant.user_id == student_id, SessionParticipant.role == 'student'))
                     .distinct())
        query = query.options(
            selectinload(SessionModel.tutor).selectinload(Tutor.user),
            selectinload(SessionModel.subject)
        ).offset(skip).limit(limit)
        return (await self.db.execute(query)).scalars().all()

    async def create(self, session_data: dict) -> SessionModel:
        session = SessionModel(**session_data)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session, ['tutor', 'participants'])
        if session.tutor:
            await self.db.refresh(session.tutor, ['user'])
        return session

    async def update(self, session_id: int, session_data: dict) -> Optional[SessionModel]:
        session = await self.get_by_id(session_id)
        if not session:
            return None
        for key, value in session_data.items():
            setattr(session, key, value)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def delete(self, session_id: int) -> bool:
        session = await self.get_by_id(session_id)
        if not session:
            return False
        await self.db.delete(session)
        await self.db.commit()
        return True

    # ── Tutor sessions ───────────────────────────────────────────────────

    async def get_sessions_by_tutor(
        self, tutor_user_id: int, status: Optional[str] = None,
        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
        skip: int = 0, limit: int = 100
    ) -> Tuple[List[SessionModel], int]:
        conditions = [SessionParticipant.user_id == tutor_user_id, SessionParticipant.role == 'tutor']
        if status:
            conditions.append(SessionModel.status == status)
        if start_date:
            conditions.append(SessionModel.scheduled_date >= start_date)
        if end_date:
            conditions.append(SessionModel.scheduled_date <= end_date)
        count_stmt = (select(func.count(SessionModel.session_id.distinct()))
                      .join(SessionParticipant, SessionModel.session_id == SessionParticipant.session_id)
                      .where(and_(*conditions)))
        total = (await self.db.execute(count_stmt)).scalar() or 0
        stmt = (select(SessionModel)
                .join(SessionParticipant, SessionModel.session_id == SessionParticipant.session_id)
                .where(and_(*conditions))
                .options(
                    selectinload(SessionModel.participants).selectinload(SessionParticipant.user),
                    selectinload(SessionModel.tutor).selectinload(Tutor.user),
                    selectinload(SessionModel.subject))
                .order_by(SessionModel.scheduled_date.desc())
                .offset(skip).limit(limit).distinct())
        sessions = (await self.db.execute(stmt)).scalars().all()
        return list(sessions), int(total)

    async def get_sessions_by_tutor_date(self, tutor_id: int, dt: date, statuses: List[str]) -> List[SessionModel]:
        query = select(SessionModel).where(
            SessionModel.tutor_id == tutor_id,
            SessionModel.scheduled_date == dt,
            SessionModel.status.in_(statuses))
        return (await self.db.execute(query)).scalars().all()

    # ── Participant operations ───────────────────────────────────────────

    async def get_participant(self, session_id: int, user_id: int, role: Optional[str] = None):
        q = select(SessionParticipant).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == user_id)
        if role:
            q = q.where(SessionParticipant.role == role)
        return (await self.db.execute(q)).scalar_one_or_none()

    async def get_confirmed_student_count(self, session_id: int) -> int:
        result = await self.db.execute(
            select(SessionParticipant).where(and_(
                SessionParticipant.session_id == session_id,
                SessionParticipant.role == 'student',
                SessionParticipant.status == 'confirmed')))
        return len(result.scalars().all())

    async def get_participant_by_id(self, participant_id: int):
        return (await self.db.execute(
            select(SessionParticipant).where(SessionParticipant.participant_id == participant_id)
        )).scalar_one_or_none()

    async def get_session_participants(self, session_id: int):
        result = await self.db.execute(
            select(SessionParticipant)
            .options(selectinload(SessionParticipant.user))
            .where(SessionParticipant.session_id == session_id))
        return result.scalars().all()

    async def delete_participant(self, participant):
        await self.db.delete(participant)
        await self.db.commit()

    # ── Material operations ──────────────────────────────────────────────

    async def add_material(self, material: SessionMaterial):
        self.db.add(material)
        await self.db.commit()
        await self.db.refresh(material)
        return material

    async def get_materials_by_session(self, session_id: int):
        return (await self.db.execute(
            select(SessionMaterial).where(SessionMaterial.session_id == session_id)
        )).scalars().all()

    async def get_materials_by_session_ids(self, session_ids: list):
        return (await self.db.execute(
            select(SessionMaterial).where(SessionMaterial.session_id.in_(session_ids))
        )).scalars().all()

    async def get_material_by_id(self, material_id: int, session_id: int):
        return (await self.db.execute(
            select(SessionMaterial).where(
                SessionMaterial.material_id == material_id,
                SessionMaterial.session_id == session_id)
        )).scalar_one_or_none()

    async def get_material_by_name(self, file_name: str, session_id: int):
        return (await self.db.execute(
            select(SessionMaterial).where(
                SessionMaterial.file_name == file_name,
                SessionMaterial.session_id == session_id)
            .order_by(SessionMaterial.uploaded_at.desc())
        )).scalars().first()

    async def delete_material(self, material):
        await self.db.delete(material)
        await self.db.commit()

    # ── Tutor / Student lookup ───────────────────────────────────────────

    async def get_tutor_id_for_user(self, user_id: int) -> Optional[int]:
        return (await self.db.execute(
            select(Tutor.tutor_id).where(Tutor.user_id == user_id)
        )).scalar_one_or_none()

    async def ensure_student_profile(self, user):
        from app.models.database import Student as StudentModel
        if not user.student_id:
            s = StudentModel(user_id=user.user_id, student_code=f"ST{user.user_id:06d}",
                             faculty="Unknown", major="Unknown", preferences={})
            self.db.add(s)
            await self.db.commit()
            await self.db.refresh(s)
            await self.db.refresh(user)

    async def ensure_tutor_profile(self, user):
        from app.models.database import Tutor as TutorModel
        if not user.tutor_id:
            t = TutorModel(user_id=user.user_id, bio=user.bio or "No bio provided",
                           rating=0.0, total_sessions=0)
            self.db.add(t)
            await self.db.commit()
            await self.db.refresh(t)
            await self.db.refresh(user)

    # ── Dashboard queries ────────────────────────────────────────────────

    async def get_dashboard_recent_student(self, user_id: int, limit: int = 3):
        q = (select(SessionModel)
             .options(selectinload(SessionModel.tutor).selectinload(Tutor.user))
             .join(SessionParticipant, SessionModel.session_id == SessionParticipant.session_id)
             .where(SessionParticipant.user_id == user_id, SessionParticipant.role == 'student',
                    SessionModel.status == 'completed')
             .order_by(desc(SessionModel.scheduled_date)).limit(limit))
        return (await self.db.execute(q)).scalars().all()

    async def get_dashboard_upcoming_student(self, user_id: int, today, limit: int = 3):
        q = (select(SessionModel)
             .options(selectinload(SessionModel.tutor).selectinload(Tutor.user))
             .join(SessionParticipant, SessionModel.session_id == SessionParticipant.session_id)
             .where(SessionParticipant.user_id == user_id, SessionParticipant.role == 'student',
                    SessionModel.scheduled_date >= today)
             .order_by(asc(SessionModel.scheduled_date)).limit(limit))
        return (await self.db.execute(q)).scalars().all()

    async def get_dashboard_recent_tutor(self, tutor_id: int, limit: int = 3):
        q = (select(SessionModel)
             .options(selectinload(SessionModel.tutor).selectinload(Tutor.user))
             .where(SessionModel.tutor_id == tutor_id, SessionModel.status == 'completed')
             .order_by(desc(SessionModel.scheduled_date)).limit(limit))
        return (await self.db.execute(q)).scalars().all()

    async def get_dashboard_upcoming_tutor(self, tutor_id: int, today, limit: int = 3):
        q = (select(SessionModel)
             .options(selectinload(SessionModel.tutor).selectinload(Tutor.user))
             .where(SessionModel.tutor_id == tutor_id, SessionModel.scheduled_date >= today,
                    SessionModel.status.in_(['confirmed', 'ongoing', 'published']))
             .order_by(asc(SessionModel.scheduled_date)).limit(limit))
        return (await self.db.execute(q)).scalars().all()

    # ── Feedback operations ──────────────────────────────────────────────

    async def get_feedback(self, session_id: int, reviewer_id: int):
        return (await self.db.execute(
            select(SessionFeedback).where(
                SessionFeedback.session_id == session_id,
                SessionFeedback.reviewer_id == reviewer_id)
        )).scalar_one_or_none()

    async def get_feedbacks_by_session(self, session_id: int, user_roles=None, user_id=None):
        q = select(SessionFeedback).where(SessionFeedback.session_id == session_id)
        if user_roles and 'student' in user_roles:
            q = q.where(SessionFeedback.reviewer_id == user_id)
        return (await self.db.execute(q)).scalars().all()

    async def get_feedbacks_by_session_ids(self, session_ids: list, user_roles=None, user_id=None):
        q = select(SessionFeedback).where(SessionFeedback.session_id.in_(session_ids))
        if user_roles and 'student' in user_roles:
            q = q.where(SessionFeedback.reviewer_id == user_id)
        return (await self.db.execute(q)).scalars().all()

    async def get_subject_feedbacks(self, subject_id: int, tutor_id: Optional[int] = None):
        from app.models.database import User as DBUser
        q = (select(SessionFeedback, SessionModel, DBUser)
             .join(SessionModel, SessionFeedback.session_id == SessionModel.session_id)
             .outerjoin(DBUser, SessionFeedback.reviewer_id == DBUser.user_id)
             .where(SessionModel.subject_id == subject_id))
        if tutor_id:
            q = q.where(SessionModel.tutor_id == tutor_id)
        return (await self.db.execute(q.order_by(SessionFeedback.created_at.desc()))).all()

    # ── Attendance ───────────────────────────────────────────────────────

    async def get_attendance_data(self, session_id: int):
        return (await self.db.execute(
            select(SessionParticipant, User, Student, Attendance)
            .join(User, SessionParticipant.user_id == User.user_id)
            .join(Student, User.user_id == Student.user_id)
            .outerjoin(Attendance, and_(
                Attendance.session_id == session_id,
                Attendance.student_id == Student.student_id))
            .where(SessionParticipant.session_id == session_id,
                   SessionParticipant.role == 'student')
        )).all()

    async def get_student_by_user_id(self, user_id: int):
        return (await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )).scalar_one_or_none()

    async def get_attendance(self, session_id: int, student_id: int):
        return (await self.db.execute(
            select(Attendance).where(
                Attendance.session_id == session_id,
                Attendance.student_id == student_id)
        )).scalar_one_or_none()

    # ── Bulk session / course operations ─────────────────────────────────

    async def get_tutor_by_user_id(self, user_id: int):
        return (await self.db.execute(
            select(Tutor).where(Tutor.user_id == user_id)
        )).scalar_one_or_none()

    async def get_session_by_tutor_and_id(self, session_id: int, tutor_id: int):
        return (await self.db.execute(
            select(SessionModel).where(
                SessionModel.session_id == session_id,
                SessionModel.tutor_id == tutor_id)
        )).scalar_one_or_none()

    async def get_session_by_tutor_subject_date(self, tutor_id, subject_id, sdate, st, et):
        return (await self.db.execute(
            select(SessionModel).where(
                SessionModel.tutor_id == tutor_id,
                SessionModel.subject_id == subject_id,
                SessionModel.scheduled_date == sdate,
                SessionModel.start_time == st,
                SessionModel.end_time == et)
        )).scalar_one_or_none()

    async def get_session_ids_for_subject_tutor(self, subject_id: int, tutor_id: int):
        rows = (await self.db.execute(
            select(SessionModel.session_id).where(
                SessionModel.subject_id == subject_id,
                SessionModel.tutor_id == tutor_id)
        )).fetchall()
        return [r[0] for r in rows]

    async def delete_participants_bulk(self, session_ids: list, user_id: int):
        res = await self.db.execute(
            delete(SessionParticipant).where(
                SessionParticipant.session_id.in_(session_ids),
                SessionParticipant.user_id == user_id,
                SessionParticipant.role == 'student'))
        return res.rowcount

    async def get_user_by_id(self, user_id: int):
        return (await self.db.execute(
            select(User).where(User.user_id == user_id)
        )).scalar_one_or_none()

    async def get_subject_by_id(self, subject_id: int):
        return (await self.db.execute(
            select(Subject).where(Subject.subject_id == subject_id)
        )).scalar_one_or_none()

    async def execute_raw(self, stmt, params=None):
        """Execute raw SQL / text queries"""
        if params:
            return await self.db.execute(stmt, params)
        return await self.db.execute(stmt)
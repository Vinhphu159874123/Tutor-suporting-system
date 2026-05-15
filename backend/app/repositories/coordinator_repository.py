"""
Coordinator Repository
Database operations for coordinator module
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, List
from app.models.database import (
    User, TutorRegistration, Tutor, Subject, Coordinator,
    Session as SessionModel, SessionParticipant, SessionFeedback,
    Notifications, SessionSchedule,
)


class CoordinatorRepository:
    """Handle all database operations for Coordinator module"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Registration queries ---
    async def get_registrations_with_details(self, status_filter: str, skip: int, limit: int) -> list:
        return (await self.db.execute(
            select(TutorRegistration, Tutor, User, Subject)
            .join(Tutor, TutorRegistration.tutor_id == Tutor.tutor_id)
            .join(User, Tutor.user_id == User.user_id)
            .join(Subject, TutorRegistration.subject_id == Subject.subject_id)
            .where(TutorRegistration.status == status_filter)
            .order_by(TutorRegistration.registered_at.desc())
            .offset(skip).limit(limit)
        )).all()

    async def get_registration_notification(self, registration_id: int) -> Optional[Notifications]:
        return (await self.db.execute(
            select(Notifications)
            .where(and_(Notifications.type == "subject_registration",
                        Notifications.data['registration_id'].astext == str(registration_id)))
            .order_by(Notifications.created_at.desc()).limit(1)
        )).scalar_one_or_none()

    async def get_first_session_for_reg(self, tutor_id: int, subject_id: int) -> Optional[SessionModel]:
        return (await self.db.execute(
            select(SessionModel).where(
                SessionModel.tutor_id == tutor_id,
                SessionModel.subject_id == subject_id).limit(1)
        )).scalar_one_or_none()

    async def get_schedule_for_session(self, tutor_id: int, subject_id: int,
                                        start_time, end_time) -> Optional[SessionSchedule]:
        return (await self.db.execute(
            select(SessionSchedule).where(
                SessionSchedule.tutor_id == tutor_id,
                SessionSchedule.subject_id == subject_id,
                SessionSchedule.start_time == start_time,
                SessionSchedule.end_time == end_time).limit(1)
        )).scalar_one_or_none()

    async def get_registration_by_id(self, registration_id: int) -> Optional[TutorRegistration]:
        return (await self.db.execute(
            select(TutorRegistration).where(TutorRegistration.registration_id == registration_id)
        )).scalar_one_or_none()

    async def get_schedules_for_registration(self, tutor_id: int, subject_id: int) -> list:
        return (await self.db.execute(
            select(SessionSchedule).where(
                SessionSchedule.tutor_id == tutor_id,
                SessionSchedule.subject_id == subject_id,
                SessionSchedule.is_active == True)
        )).scalars().all()

    async def get_coordinator_by_user_id(self, user_id: int) -> Optional[Coordinator]:
        return (await self.db.execute(
            select(Coordinator).where(Coordinator.user_id == user_id)
        )).scalar_one_or_none()

    async def get_tutor_by_id(self, tutor_id: int) -> Optional[Tutor]:
        return (await self.db.execute(
            select(Tutor).where(Tutor.tutor_id == tutor_id)
        )).scalar_one_or_none()

    async def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        return (await self.db.execute(
            select(Subject).where(Subject.subject_id == subject_id)
        )).scalar_one_or_none()

    # --- Session queries ---
    async def get_pending_sessions(self, skip: int, limit: int) -> list:
        return (await self.db.execute(
            select(SessionModel, Tutor, User, Subject)
            .join(Tutor, SessionModel.tutor_id == Tutor.tutor_id)
            .join(User, Tutor.user_id == User.user_id)
            .join(Subject, SessionModel.subject_id == Subject.subject_id)
            .where(SessionModel.status == 'pending')
            .order_by(SessionModel.start_time.desc())
            .offset(skip).limit(limit)
        )).all()

    async def get_participant_counts(self, session_ids: list) -> dict:
        rows = (await self.db.execute(
            select(SessionParticipant.session_id,
                   func.count(SessionParticipant.participant_id).label('count'))
            .where(SessionParticipant.session_id.in_(session_ids))
            .group_by(SessionParticipant.session_id)
        )).all()
        return {r.session_id: r.count for r in rows}

    async def get_session_by_id(self, session_id: int) -> Optional[SessionModel]:
        return (await self.db.execute(
            select(SessionModel).where(SessionModel.session_id == session_id)
        )).scalar_one_or_none()

    # --- Tutor management queries ---
    async def get_tutors_with_users(self, skip: int, limit: int, search: Optional[str]) -> list:
        q = select(Tutor, User).join(User, Tutor.user_id == User.user_id).order_by(User.full_name)
        if search:
            pat = f"%{search}%"
            q = q.where(User.full_name.ilike(pat) | User.email.ilike(pat) | Tutor.staff_code.ilike(pat))
        return (await self.db.execute(q.offset(skip).limit(limit))).all()

    async def get_session_counts_for_tutors(self, tutor_ids: list) -> dict:
        rows = (await self.db.execute(
            select(SessionModel.tutor_id, func.count(SessionModel.session_id).label('session_count'))
            .where(SessionModel.tutor_id.in_(tutor_ids)).group_by(SessionModel.tutor_id)
        )).all()
        return {r.tutor_id: r.session_count for r in rows}

    async def get_course_counts_for_tutors(self, tutor_ids: list) -> dict:
        rows = (await self.db.execute(
            select(TutorRegistration.tutor_id,
                   func.count(func.distinct(TutorRegistration.subject_id)).label('course_count'))
            .where(and_(TutorRegistration.tutor_id.in_(tutor_ids), TutorRegistration.status == 'approved'))
            .group_by(TutorRegistration.tutor_id)
        )).all()
        return {r.tutor_id: r.course_count for r in rows}

    async def get_tutor_with_user(self, tutor_id: int):
        return (await self.db.execute(
            select(Tutor, User).join(User, Tutor.user_id == User.user_id)
            .where(Tutor.tutor_id == tutor_id)
        )).first()

    async def get_tutor_course_stats(self, tutor_id: int) -> list:
        return (await self.db.execute(
            select(Subject,
                   func.count(func.distinct(SessionModel.session_id)).label('ts'),
                   func.count(func.distinct(SessionModel.session_id)).filter(
                       SessionModel.status == 'completed').label('cs'),
                   func.avg(SessionFeedback.rating).label('ar'))
            .join(SessionModel, Subject.subject_id == SessionModel.subject_id)
            .outerjoin(SessionFeedback, SessionFeedback.session_id == SessionModel.session_id)
            .where(SessionModel.tutor_id == tutor_id)
            .group_by(Subject.subject_id)
        )).all()

    async def get_student_counts_for_subjects(self, tutor_id: int, subject_ids: list) -> dict:
        rows = (await self.db.execute(
            select(SessionModel.subject_id,
                   func.count(func.distinct(SessionParticipant.user_id)).label('student_count'))
            .join(SessionParticipant, SessionParticipant.session_id == SessionModel.session_id)
            .where(and_(SessionModel.tutor_id == tutor_id, SessionModel.subject_id.in_(subject_ids),
                        SessionParticipant.role == 'student'))
            .group_by(SessionModel.subject_id)
        )).all()
        return {r.subject_id: r.student_count for r in rows}

    async def get_sessions_for_tutor_subject(self, tutor_id: int, subject_id: int) -> list:
        return (await self.db.execute(
            select(SessionModel).where(and_(
                SessionModel.tutor_id == tutor_id, SessionModel.subject_id == subject_id))
            .order_by(SessionModel.scheduled_date.desc())
        )).scalars().all()

    async def get_participants_for_sessions(self, session_ids: list) -> list:
        return (await self.db.execute(
            select(SessionParticipant, User)
            .join(User, SessionParticipant.user_id == User.user_id)
            .where(and_(SessionParticipant.session_id.in_(session_ids),
                        SessionParticipant.role == 'student'))
        )).all()

    async def get_feedbacks_for_sessions(self, session_ids: list) -> list:
        return (await self.db.execute(
            select(SessionFeedback, User, SessionModel)
            .join(User, SessionFeedback.reviewer_id == User.user_id)
            .join(SessionModel, SessionFeedback.session_id == SessionModel.session_id)
            .where(SessionFeedback.session_id.in_(session_ids))
        )).all()

    async def get_tutor_avg_rating(self, tutor_id: int):
        return (await self.db.execute(
            select(func.avg(SessionFeedback.rating), func.count(SessionFeedback.feedback_id))
            .join(SessionModel, SessionFeedback.session_id == SessionModel.session_id)
            .where(SessionModel.tutor_id == tutor_id)
        )).first()

    async def get_all_tutors(self) -> list:
        return (await self.db.execute(select(Tutor))).scalars().all()

    async def get_tutor_avg_rating_scalar(self, tutor_id: int) -> Optional[float]:
        return (await self.db.execute(
            select(func.avg(SessionFeedback.rating))
            .join(SessionModel, SessionFeedback.session_id == SessionModel.session_id)
            .where(SessionModel.tutor_id == tutor_id)
        )).scalar()

    # --- Transaction helpers ---
    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def refresh(self, obj) -> None:
        await self.db.refresh(obj)

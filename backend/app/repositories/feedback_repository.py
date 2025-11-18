from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from typing import List, Optional, Dict
from app.models.database import SessionFeedback, Session, User, Tutor


class FeedbackRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_feedback(self, feedback_data: dict) -> SessionFeedback:
        """Create new session feedback"""
        feedback = SessionFeedback(**feedback_data)
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def get_feedbacks_by_tutor(
        self, 
        tutor_id: int, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[SessionFeedback]:
        """Get all feedbacks for a specific tutor from completed sessions"""
        query = (
            select(SessionFeedback)
            .join(Session, SessionFeedback.session_id == Session.session_id)
            .join(User, SessionFeedback.reviewer_id == User.user_id)
            .where(
                and_(
                    Session.tutor_id == tutor_id,
                    Session.status == 'completed',
                    SessionFeedback.is_public == True
                )
            )
            .options(joinedload(SessionFeedback.reviewer))
            .order_by(SessionFeedback.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().unique().all()

    async def get_tutor_rating_stats(self, tutor_id: int) -> Dict:
        """Get aggregated rating statistics for a tutor"""
        query = (
            select(
                func.avg(SessionFeedback.rating).label('average_rating'),
                func.count(SessionFeedback.feedback_id).label('total_reviews'),
                func.count(func.distinct(SessionFeedback.reviewer_id)).label('unique_reviewers')
            )
            .join(Session, SessionFeedback.session_id == Session.session_id)
            .where(
                and_(
                    Session.tutor_id == tutor_id,
                    Session.status == 'completed',
                    SessionFeedback.is_public == True
                )
            )
        )
        result = await self.db.execute(query)
        stats = result.first()
        
        return {
            'average_rating': float(stats.average_rating) if stats.average_rating else 0.0,
            'total_reviews': stats.total_reviews or 0,
            'unique_reviewers': stats.unique_reviewers or 0
        }

    async def update_tutor_rating(self, tutor_id: int) -> None:
        """Update tutor's aggregated rating"""
        stats = await self.get_tutor_rating_stats(tutor_id)
        
        query = select(Tutor).where(Tutor.tutor_id == tutor_id)
        result = await self.db.execute(query)
        tutor = result.scalar_one_or_none()
        
        if tutor:
            tutor.rating = round(stats['average_rating'], 2)
            await self.db.commit()

    async def get_feedback_by_session_and_reviewer(
        self, 
        session_id: int, 
        reviewer_id: int
    ) -> Optional[SessionFeedback]:
        """Check if feedback already exists for this session and reviewer"""
        query = select(SessionFeedback).where(
            and_(
                SessionFeedback.session_id == session_id,
                SessionFeedback.reviewer_id == reviewer_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

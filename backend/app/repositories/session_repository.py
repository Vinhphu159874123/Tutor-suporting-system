"""
Session Repository - Database Access Layer
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models.database import (
    Session as SessionModel,
    SessionParticipant,
    Tutor,
    User
)
from datetime import datetime
from typing import Tuple

class SessionRepository:
    """Handle database operations for Session model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, session_id: int) -> Optional[SessionModel]:
        """Get session by ID"""
        result = await self.db.execute(
            select(SessionModel).where(SessionModel.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        tutor_id: Optional[int] = None,
        student_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[SessionModel]:
        """Get all sessions with filters"""
        query = select(SessionModel)
        
        if tutor_id:
            query = query.where(SessionModel.tutor_id == tutor_id)
        if student_id:
            query = query.where(SessionModel.student_id == student_id)
        if status:
            query = query.where(SessionModel.status == status)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, session_data: dict) -> SessionModel:
        """Create new session"""
        session = SessionModel(**session_data)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def update(self, session_id: int, session_data: dict) -> Optional[SessionModel]:
        """Update session"""
        session = await self.get_by_id(session_id)
        if not session:
            return None
        
        for key, value in session_data.items():
            setattr(session, key, value)
        
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def delete(self, session_id: int) -> bool:
        """Delete session"""
        session = await self.get_by_id(session_id)
        if not session:
            return False
        
        await self.db.delete(session)
        await self.db.commit()
        return True

    async def get_sessions_by_tutor(
        self,
        tutor_user_id: int,  # Changed from tutor_id to tutor_user_id
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[SessionModel], int]:
        """
        Get sessions where user is tutor - using SessionParticipant
        
        Args:
            tutor_user_id: User ID of the tutor (not tutor table ID)
            status: Filter by session status
            start_date/end_date: Date range filters
            skip/limit: Pagination
            
        Returns:
            Tuple of (sessions list, total count)
        """
        # Build WHERE conditions
        conditions = []
        
        # Join condition: find sessions where user is tutor
        conditions.append(SessionParticipant.user_id == tutor_user_id)
        conditions.append(SessionParticipant.role == 'tutor')
        
        if status:
            conditions.append(SessionModel.status == status)
        if start_date:
            conditions.append(SessionModel.scheduled_date >= start_date)
        if end_date:
            conditions.append(SessionModel.scheduled_date <= end_date)
        
        # Count query
        count_stmt = (
            select(func.count(SessionModel.session_id.distinct()))
            .join(SessionParticipant, SessionModel.session_id == SessionParticipant.session_id)
            .where(and_(*conditions))
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Main query with eager loading
        stmt = (
            select(SessionModel)
            .join(SessionParticipant, SessionModel.session_id == SessionParticipant.session_id)
            .where(and_(*conditions))
            .options(
                # Eager load participants with their user data
                selectinload(SessionModel.participants).selectinload(SessionParticipant.user),
                # Load tutor info
                selectinload(SessionModel.tutor).selectinload(Tutor.user),
                # Load subject
                selectinload(SessionModel.subject)
            )
            .order_by(SessionModel.scheduled_date.desc())
            .offset(skip)
            .limit(limit)
            .distinct()
        )
        
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        
        return list(sessions), int(total)
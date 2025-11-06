"""
Session Repository - Database Access Layer
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.database import Session as SessionModel


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

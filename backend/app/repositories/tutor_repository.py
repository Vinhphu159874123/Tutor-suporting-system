"""
Tutor Repository - Database Access Layer
Pure database operations, no business logic
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.database import Tutor


class TutorRepository:
    """Handle database operations for Tutor model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, tutor_id: int) -> Optional[Tutor]:
        """Get tutor by ID"""
        result = await self.db.execute(
            select(Tutor).where(Tutor.id == tutor_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> Optional[Tutor]:
        """Get tutor by user ID"""
        result = await self.db.execute(
            select(Tutor).where(Tutor.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        subject: Optional[str] = None,
        is_available: Optional[bool] = None,
        min_rating: Optional[float] = None
    ) -> List[Tutor]:
        """Get all tutors with optional filters"""
        query = select(Tutor)
        
        # TODO: Filter by subject (needs ARRAY contains in PostgreSQL)
        # if subject:
        #     query = query.where(Tutor.subjects.contains([subject]))
        
        if is_available is not None:
            query = query.where(Tutor.is_available == is_available)
        
        if min_rating is not None:
            query = query.where(Tutor.rating >= min_rating)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, tutor_data: dict) -> Tutor:
        """Create new tutor"""
        tutor = Tutor(**tutor_data)
        self.db.add(tutor)
        await self.db.commit()
        await self.db.refresh(tutor)
        return tutor
    
    async def update(self, tutor_id: int, tutor_data: dict) -> Optional[Tutor]:
        """Update tutor"""
        tutor = await self.get_by_id(tutor_id)
        if not tutor:
            return None
        
        for key, value in tutor_data.items():
            setattr(tutor, key, value)
        
        await self.db.commit()
        await self.db.refresh(tutor)
        return tutor
    
    async def delete(self, tutor_id: int) -> bool:
        """Delete tutor"""
        tutor = await self.get_by_id(tutor_id)
        if not tutor:
            return False
        
        await self.db.delete(tutor)
        await self.db.commit()
        return True
    
    async def exists_by_user_id(self, user_id: int) -> bool:
        """Check if user already has tutor profile"""
        result = await self.db.execute(
            select(Tutor.id).where(Tutor.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None

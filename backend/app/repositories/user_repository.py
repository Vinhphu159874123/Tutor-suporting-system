"""
User Repository
Database operations for User model
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
from app.models.database import User

class UserRepository:
    """Handle all database operations for User model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        role: Optional[str] = None
    ) -> List[User]:
        """Get all users with optional filtering"""
        query = select(User)
        
        if role:
            query = query.where(User.role == role)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, user_data: dict) -> User:
        """Create new user"""
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**user_data)
        )
        await self.db.commit()
        return await self.get_by_id(user_id)
    
    async def delete(self, user_id: int) -> bool:
        """Delete user (soft delete by setting is_active=False)"""
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        user = await self.get_by_email(email)
        return user is not None

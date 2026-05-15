"""
Admin Repository
Database operations for admin/statistics queries
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, any_
from sqlalchemy.orm import joinedload
from typing import List, Optional
from app.models.database import User, Session as SessionModel, SessionFeedback


class AdminRepository:
    """Handle all database operations for Admin module"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_users(
        self, *, skip: int = 0, limit: int = 100,
        include_inactive: bool = False, role: Optional[str] = None
    ) -> List[User]:
        query = select(User).options(joinedload(User.student))
        if not include_inactive:
            query = query.where(User.is_active == True)
        if role:
            query = query.where(role == any_(User.role))
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def count_users(self) -> int:
        return (await self.db.execute(select(func.count(User.user_id)))).scalar() or 0

    async def count_students(self) -> int:
        return (await self.db.execute(
            select(func.count(User.user_id)).where('student' == any_(User.role))
        )).scalar() or 0

    async def count_tutors(self) -> int:
        return (await self.db.execute(
            select(func.count(User.user_id)).where('tutor' == any_(User.role))
        )).scalar() or 0

    async def count_sessions(self) -> int:
        return (await self.db.execute(
            select(func.count(SessionModel.session_id))
        )).scalar() or 0

    async def avg_rating(self) -> Optional[float]:
        return (await self.db.execute(
            select(func.avg(SessionFeedback.rating))
        )).scalar()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

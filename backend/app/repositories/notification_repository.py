"""
Notification Repository
Database operations for Notifications model
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from typing import List, Optional
from app.models.database import Notifications


class NotificationRepository:
    """Handle all database operations for Notifications model"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(
        self, user_id: int, *, is_read: Optional[bool] = None,
        limit: int = 50, offset: int = 0
    ) -> List[Notifications]:
        query = select(Notifications).where(Notifications.user_id == user_id)
        if is_read is not None:
            query = query.where(Notifications.is_read == is_read)
        query = query.order_by(Notifications.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_unread_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Notifications.notification_id)).where(
                and_(Notifications.user_id == user_id, Notifications.is_read == False)
            )
        )
        return result.scalar() or 0

    async def get_by_id_and_user(self, notification_id: int, user_id: int) -> Optional[Notifications]:
        result = await self.db.execute(
            select(Notifications).where(
                and_(Notifications.notification_id == notification_id,
                     Notifications.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def mark_as_read(self, notification: Notifications) -> None:
        notification.is_read = True
        await self.db.commit()

    async def mark_all_as_read(self, user_id: int) -> int:
        """Bulk update using UPDATE query instead of loading all into memory"""
        result = await self.db.execute(
            update(Notifications)
            .where(and_(Notifications.user_id == user_id, Notifications.is_read == False))
            .values(is_read=True)
        )
        await self.db.commit()
        return result.rowcount

    async def create(
        self, *, user_id: int, type: str, title: str, message: str,
        data: dict = None, related_entity_type: str = None,
        related_entity_id: int = None, is_read: bool = False,
        created_at=None
    ) -> Notifications:
        """Create a single notification"""
        notification = Notifications(
            user_id=user_id, type=type, title=title, message=message,
            data=data, related_entity_type=related_entity_type,
            related_entity_id=related_entity_id, is_read=is_read,
        )
        if created_at:
            notification.created_at = created_at
        self.db.add(notification)
        return notification

    async def bulk_create(self, notifications: list[dict]) -> None:
        """Bulk insert notifications — 1 SQL query instead of N"""
        from sqlalchemy import insert
        if notifications:
            await self.db.execute(insert(Notifications), notifications)

    async def commit(self):
        await self.db.commit()

    async def delete_read(self, user_id: int) -> int:
        notifications = await self.get_by_user(user_id, is_read=True, limit=10000)
        count = len(notifications)
        for n in notifications:
            await self.db.delete(n)
        await self.db.commit()
        return count

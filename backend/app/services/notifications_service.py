"""
Notifications Service
Business logic for user notifications
"""
from typing import List, Optional
from fastapi import HTTPException

from app.repositories.notification_repository import NotificationRepository


class NotificationsService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def get_notifications(
        self, user_id: int, *, is_read: Optional[bool] = None,
        limit: int = 50, offset: int = 0
    ) -> List[dict]:
        from app.core.cache import get_or_load

        cache_key = f"notifications:{user_id}:{is_read}:{limit}:{offset}"

        async def _load():
            notifications = await self.repo.get_by_user(
                user_id, is_read=is_read, limit=limit, offset=offset
            )
            return [
                {
                    "notification_id": n.notification_id,
                    "type": n.type,
                    "title": n.title,
                    "message": n.message,
                    "data": n.data,
                    "is_read": n.is_read,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                    "link": None,
                }
                for n in notifications
            ]

        return await get_or_load(cache_key, _load, ttl=10)

    async def get_unread_count(self, user_id: int) -> int:
        return await self.repo.get_unread_count(user_id)

    async def mark_as_read(self, notification_id: int, user_id: int) -> dict:
        notification = await self.repo.get_by_id_and_user(notification_id, user_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        try:
            await self.repo.mark_as_read(notification)
        except Exception:
            await self.repo.rollback()
            raise
        return {"message": "Marked as read"}

    async def mark_all_as_read(self, user_id: int) -> dict:
        try:
            count = await self.repo.mark_all_as_read(user_id)
        except Exception:
            await self.repo.rollback()
            raise
        return {"message": f"Marked {count} notifications as read"}

    async def delete_read(self, user_id: int) -> dict:
        try:
            count = await self.repo.delete_read(user_id)
        except Exception:
            await self.repo.rollback()
            raise
        return {"message": f"Deleted {count} read notifications"}

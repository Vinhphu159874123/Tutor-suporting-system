"""
Notifications API
User notifications and real-time alerts
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from app.schemas.notifications import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationStats
)
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.database import User, Notifications
from sqlalchemy import func

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_notifications(
    is_read: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user notifications"""
    
    query = select(Notifications).where(Notifications.user_id == current_user.user_id)
    
    if is_read is not None:
        query = query.where(Notifications.is_read == is_read)
    
    query = query.order_by(Notifications.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return [
        {
            "notification_id": n.notification_id,
            "type": n.type,
            "title": n.title,
            "message": n.message,
            "data": n.data,  # Add data field
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "link": None  # Can be enhanced based on type
        }
        for n in notifications
    ]


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications"""
    
    from sqlalchemy import func
    result = await db.execute(
        select(func.count(Notifications.notification_id))
        .where(and_(
            Notifications.user_id == current_user.user_id,
            Notifications.is_read == False
        ))
    )
    count = result.scalar() or 0
    return {"unread_count": count}


@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read"""
    
    # Get notification
    result = await db.execute(
        select(Notifications).where(
            and_(
                Notifications.notification_id == notification_id,
                Notifications.user_id == current_user.user_id
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Update
    notification.is_read = True
    await db.commit()
    
    return {"message": "Marked as read"}


@router.put("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read"""
    
    # Update all unread notifications
    result = await db.execute(
        select(Notifications).where(
            and_(
                Notifications.user_id == current_user.user_id,
                Notifications.is_read == False
            )
        )
    )
    notifications = result.scalars().all()
    
    for notification in notifications:
        notification.is_read = True
    
    await db.commit()
    
    return {"message": f"Marked {len(notifications)} notifications as read"}


@router.delete("/delete-read")
async def delete_read_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete all read notifications"""
    
    # Get all read notifications
    result = await db.execute(
        select(Notifications).where(
            and_(
                Notifications.user_id == current_user.user_id,
                Notifications.is_read == True
            )
        )
    )
    notifications = result.scalars().all()
    
    count = len(notifications)
    
    # Delete them
    for notification in notifications:
        await db.delete(notification)
    
    await db.commit()
    
    return {"message": f"Deleted {count} read notifications"}

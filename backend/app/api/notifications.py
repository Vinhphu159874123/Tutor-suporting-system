"""Notifications API — thin controller, delegates to NotificationsService"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from app.core.dependencies import get_current_user, get_notifications_service
from app.models.database import User
from app.services.notifications_service import NotificationsService

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_notifications(
    is_read: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    svc: NotificationsService = Depends(get_notifications_service),
):
    return await svc.get_notifications(current_user.user_id, is_read=is_read,
                                       limit=limit, offset=offset)

@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    svc: NotificationsService = Depends(get_notifications_service),
):
    count = await svc.get_unread_count(current_user.user_id)
    return {"unread_count": count}

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    svc: NotificationsService = Depends(get_notifications_service),
):
    return await svc.mark_as_read(notification_id, current_user.user_id)

@router.put("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    svc: NotificationsService = Depends(get_notifications_service),
):
    return await svc.mark_all_as_read(current_user.user_id)

@router.delete("/delete-read")
async def delete_read_notifications(
    current_user: User = Depends(get_current_user),
    svc: NotificationsService = Depends(get_notifications_service),
):
    return await svc.delete_read(current_user.user_id)

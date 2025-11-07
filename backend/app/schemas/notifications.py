"""
Notifications Schemas - PLACEHOLDER
Pydantic models for notifications API
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class NotificationBase(BaseModel):
    """Base notification schema"""
    type: str = Field(..., max_length=100)
    title: str = Field(..., max_length=255)
    message: str = Field(..., max_length=1000)
    related_entity_type: Optional[str] = Field(None, max_length=100)
    related_entity_id: Optional[int] = None
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class NotificationCreate(NotificationBase):
    """Schema for creating notification"""
    user_id: int = Field(..., gt=0)


class NotificationUpdate(BaseModel):
    """Schema for updating notification"""
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response"""
    notification_id: int
    user_id: int
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationStats(BaseModel):
    """Notification statistics"""
    total_count: int
    unread_count: int
    read_count: int
    by_type: Dict[str, int]

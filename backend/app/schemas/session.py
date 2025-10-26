"""
Session Schemas - Request/Response DTOs
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enum"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SessionBase(BaseModel):
    """Base session fields"""
    tutor_id: int
    student_id: int
    subject: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    notes: Optional[str] = None


class SessionCreate(SessionBase):
    """Data for creating session"""
    pass


class SessionUpdate(BaseModel):
    """Data for updating session"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[SessionStatus] = None


class SessionResponse(SessionBase):
    """Session response DTO"""
    id: int
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    
    # Joined data
    tutor_name: Optional[str] = None
    student_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SessionMaterialCreate(BaseModel):
    """Upload session material"""
    session_id: int
    file_url: str
    file_type: str
    description: Optional[str] = None

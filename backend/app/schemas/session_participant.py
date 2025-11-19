"""
Session Participant Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SessionParticipantBase(BaseModel):
    """Base participant schema"""
    notes: Optional[str] = None


class SessionJoinRequest(SessionParticipantBase):
    """Student request to join a session"""
    pass


class SessionParticipantResponse(BaseModel):
    """Participant response"""
    participant_id: int
    session_id: int
    user_id: int
    role: str  # 'tutor' or 'student'
    status: str  # 'confirmed', 'pending', 'cancelled'
    joined_at: datetime
    notes: Optional[str] = None
    
    # User info
    email: str
    full_name: str
    
    class Config:
        from_attributes = True


class SessionParticipantUpdate(BaseModel):
    """Update participant status (accept/reject)"""
    status: str = Field(..., pattern="^(confirmed|cancelled)$")
    notes: Optional[str] = None

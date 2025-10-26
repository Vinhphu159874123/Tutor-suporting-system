"""
Student Schemas - Request/Response DTOs
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StudentBase(BaseModel):
    """Base student fields"""
    subjects_needed: List[str] = Field(..., min_length=1, description="Subjects needing help")
    learning_goals: Optional[str] = Field(None, description="Description of learning goals")
    year: Optional[int] = Field(None, ge=1, le=5, description="Year of study (1-5)")
    preferred_schedule: Optional[str] = Field(None, description="Preferred time slots")


class StudentCreate(StudentBase):
    """Data for creating student profile"""
    user_id: int


class StudentUpdate(BaseModel):
    """Data for updating student profile"""
    subjects_needed: Optional[List[str]] = Field(None, min_length=1)
    learning_goals: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=5)
    preferred_schedule: Optional[str] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    """Student response DTO"""
    id: int
    user_id: int
    is_active: bool
    total_sessions: int
    created_at: datetime
    updated_at: datetime
    
    # User data (joined)
    full_name: Optional[str] = None
    email: Optional[str] = None
    faculty: Optional[str] = None
    major: Optional[str] = None
    
    class Config:
        from_attributes = True


class TutorRequestCreate(BaseModel):
    """Request for a tutor"""
    subject: str = Field(..., description="Subject needing help")
    description: Optional[str] = Field(None, description="Description of help needed")
    urgency: Optional[str] = Field("normal", description="normal, high, urgent")


class SessionFeedbackCreate(BaseModel):
    """Feedback after session"""
    session_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    comment: Optional[str] = None
    would_recommend: bool = True

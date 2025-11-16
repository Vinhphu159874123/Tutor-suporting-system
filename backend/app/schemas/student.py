"""
Student Schemas - Request/Response DTOs
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class StudentBase(BaseModel):
    """Base student fields"""
    student_code: str = Field(..., description="Student code (MSSV)")
    faculty: Optional[str] = Field(None, description="Faculty name")
    major: Optional[str] = Field(None, description="Major/Program")
    year: Optional[int] = Field(None, ge=1, le=5, description="Year of study (1-5)")
    preferences: Optional[Dict[str, Any]] = Field(default={}, description="Student preferences (JSON)")


class StudentCreate(StudentBase):
    """Data for creating student profile"""
    user_id: int


class StudentUpdate(BaseModel):
    """Data for updating student profile"""
    faculty: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=5)
    preferences: Optional[Dict[str, Any]] = None


class StudentResponse(StudentBase):
    """Student response DTO"""
    student_id: int
    user_id: int
    
    # User data (joined)
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class StudentRegistrationCreate(BaseModel):
    """Request to register for a subject"""
    subject_id: int
    learning_goals: Optional[str] = Field(None, description="Learning objectives")
    urgency: str = Field("medium", description="high, medium, low")


class StudentRegistrationResponse(BaseModel):
    """Student registration response"""
    registration_id: int
    student_id: int
    subject_id: int
    learning_goals: Optional[str]
    urgency: str
    status: str  # pending, approved, rejected
    approved_by: Optional[int]
    rejection_reason: Optional[str]
    registered_at: datetime
    responded_at: Optional[datetime]
    
    # Joined data
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    
    class Config:
        from_attributes = True


class SessionFeedbackCreate(BaseModel):
    """Feedback after session"""
    session_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    comment: Optional[str] = None
    tags: Optional[list[str]] = Field(default=[], description="Feedback tags")
    is_anonymous: bool = False


class TutorRequestCreate(BaseModel):
    """Request to create a tutor request"""
    subject_id: int = Field(..., description="Subject ID to request tutor for")
    description: Optional[str] = Field(None, description="Request description")
    urgency: str = Field("medium", description="high, medium, low")
    preferred_schedule: Optional[str] = Field(None, description="Preferred schedule")

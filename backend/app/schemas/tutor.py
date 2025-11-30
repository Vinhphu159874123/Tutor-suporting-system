"""
Tutor Schemas - Request/Response DTOs
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class TutorBase(BaseModel):
    """Base tutor fields"""
    staff_code: Optional[str] = None
    faculty: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[Decimal] = Field(default=0, ge=0, description="Hourly rate in VND")
    teaching_experience: Optional[Dict[str, Any]] = Field(default={}, description="Teaching experience (JSON)")


class TutorCreate(TutorBase):
    """Data for creating tutor profile"""
    user_id: Optional[int] = None  # Will be auto-filled from current_user in endpoint
    experience_years: Optional[int] = Field(default=0, ge=0, description="Years of teaching experience")
    availability: Optional[Dict[str, list[str]]] = Field(default={}, description="Weekly availability slots")


class TutorUpdate(BaseModel):
    """Data for updating tutor profile"""
    staff_code: Optional[str] = None
    faculty: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    teaching_experience: Optional[Dict[str, Any]] = None


class TutorResponse(TutorBase):
    """Tutor response DTO"""
    tutor_id: int
    user_id: int
    rating: Decimal
    total_sessions: int
    is_verified: bool
    verified_at: Optional[datetime]
    
    # User data (joined)
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class TutorRegistrationCreate(BaseModel):
    """Request to register for teaching a subject"""
    subject_id: int = Field(..., description="Subject ID to register for teaching")
    gpa: Optional[Decimal] = Field(None, ge=0, le=4.0, description="GPA for this subject (0-4.0)")
    qualifications: Optional[str] = Field(None, description="Teaching qualifications and experience for this subject")
    availability: Optional[Dict[str, list[str]]] = Field(default={}, description="Weekly availability slots for this subject")


class TutorRegistrationResponse(BaseModel):
    """Tutor registration response"""
    registration_id: int
    tutor_id: int
    subject_id: int
    gpa: Optional[Decimal]
    qualifications: Optional[str]
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


class AvailabilitySlot(BaseModel):
    """Tutor availability slot"""
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: str = Field(..., description="Start time (HH:MM)")
    end_time: str = Field(..., description="End time (HH:MM)")
    is_available: bool = Field(default=True, description="Whether slot is available")

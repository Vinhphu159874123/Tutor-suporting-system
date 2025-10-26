"""
Tutor Schemas - Request/Response DTOs
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class TutorBase(BaseModel):
    """Base tutor fields"""
    bio: Optional[str] = None
    hourly_rate: Optional[Decimal] = Field(None, gt=0, description="Hourly rate in VND")
    subjects: Optional[List[str]] = Field(default_factory=list, description="Teaching subjects")
    experience_years: Optional[int] = Field(None, ge=0, description="Years of experience")
    is_available: Optional[bool] = True


class TutorCreate(TutorBase):
    """Data for creating tutor profile"""
    user_id: int
    bio: str
    hourly_rate: Decimal = Field(..., gt=0)
    subjects: List[str] = Field(..., min_length=1)


class TutorUpdate(BaseModel):
    """Data for updating tutor profile"""
    bio: Optional[str] = None
    hourly_rate: Optional[Decimal] = Field(None, gt=0)
    subjects: Optional[List[str]] = Field(None, min_length=1)
    experience_years: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None


class TutorResponse(TutorBase):
    """Tutor response DTO"""
    id: int
    user_id: int
    rating: Decimal
    total_sessions: int
    created_at: datetime
    updated_at: datetime
    
    # User data (joined)
    full_name: Optional[str] = None
    email: Optional[str] = None
    faculty: Optional[str] = None
    
    class Config:
        from_attributes = True


class AvailabilitySlot(BaseModel):
    """Tutor availability time slot"""
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: str = Field(..., description="HH:MM format")
    end_time: str = Field(..., description="HH:MM format")

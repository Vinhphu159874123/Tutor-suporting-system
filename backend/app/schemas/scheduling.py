"""
Scheduling Schemas - Request/Response DTOs
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time


class AvailabilityBase(BaseModel):
    """Base availability fields"""
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time


class AvailabilityCreate(AvailabilityBase):
    """Data for creating availability slot"""
    pass


class AvailabilityUpdate(BaseModel):
    """Data for updating availability"""
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_active: Optional[bool] = None


class AvailabilityResponse(AvailabilityBase):
    """Availability response DTO"""
    id: int
    tutor_id: int
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class TimeSlotRequest(BaseModel):
    """Request for available time slots"""
    tutor_id: int
    date: datetime
    duration_minutes: int = Field(60, ge=30, le=240)


class TimeSlotResponse(BaseModel):
    """Available time slot"""
    start_time: datetime
    end_time: datetime
    is_available: bool

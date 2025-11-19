"""
Scheduling Schemas - Request/Response DTOs
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date, time


class AvailabilityCreate(BaseModel):
    """Schema for creating availability slot"""
    is_recurring: bool = Field(..., description="True for weekly recurring, False for one-time")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="0-6 for Mon-Sun (required if is_recurring=True)")
    specific_date: Optional[date] = Field(None, description="Specific date (required if is_recurring=False)")
    start_time: time = Field(..., description="Start time")
    end_time: time = Field(..., description="End time")
    is_available: bool = Field(True, description="Whether the slot is available")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")

    
    @validator('day_of_week')
    def validate_recurring_day(cls, v, values):
        if values.get('is_recurring') and v is None:
            raise ValueError('day_of_week is required for recurring availability')
        if not values.get('is_recurring') and v is not None:
            raise ValueError('day_of_week should not be set for one-time availability')
        return v
    
    @validator('specific_date')
    def validate_onetime_date(cls, v, values):
        if not values.get('is_recurring') and v is None:
            raise ValueError('specific_date is required for one-time availability')
        if values.get('is_recurring') and v is not None:
            raise ValueError('specific_date should not be set for recurring availability')
        return v


class AvailabilityUpdate(BaseModel):
    """Schema for updating availability slot"""
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class AvailabilityResponse(BaseModel):
    """Schema for availability response"""
    availability_id: int
    tutor_id: int
    is_recurring: bool
    day_of_week: Optional[int]
    specific_date: Optional[date]
    start_time: time
    end_time: time
    is_available: bool
    notes: Optional[str]
    
    class Config:
        from_attributes = True



class TimeSlotRequest(BaseModel):
    """Request for available time slots"""
    tutor_id: int
    date: datetime
    duration_minutes: int = Field(60, ge=30, le=240)


class TimeSlotResponse(BaseModel):
    """Available time slot"""
    date: str  # ISO date string
    start_time: str  # Time in HH:MM:SS format
    end_time: str  # Time in HH:MM:SS format

class ScheduleSessionRequest(BaseModel):
    """Request to schedule a session"""
    tutor_id: int = Field(..., gt=0)
    scheduled_date: date
    start_time: time
    end_time: time
    subject_id: int = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=500)


class RescheduleRequest(BaseModel):
    """Request to reschedule a session"""
    scheduled_date: date
    start_time: time
    end_time: time
    reason: Optional[str] = Field(None, max_length=500)

"""
Schedule Preference Schemas — Request/Response DTOs
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class TimeSlot(BaseModel):
    day: str
    start_time: str
    end_time: str


class SchedulePreferenceCreate(BaseModel):
    subject_id: int
    preferred_start_date: date
    total_sessions: int = Field(gt=0)
    session_duration: int = Field(gt=0)
    session_format: str = Field(default="both")
    available_time_slots: List[TimeSlot]
    notes: Optional[str] = None


class SchedulePreferenceUpdate(BaseModel):
    preferred_start_date: Optional[date] = None
    total_sessions: Optional[int] = Field(None, gt=0)
    session_duration: Optional[int] = Field(None, gt=0)
    session_format: Optional[str] = None
    available_time_slots: Optional[List[TimeSlot]] = None
    notes: Optional[str] = None
    status: Optional[str] = None

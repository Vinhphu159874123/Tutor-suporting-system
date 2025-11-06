"""
Coordinator Schemas - Request/Response DTOs
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class CoordinatorBase(BaseModel):
    """Base coordinator fields"""
    department: Optional[str] = None
    assigned_subjects: Optional[list[str]] = Field(default=[], description="Assigned subject IDs")


class CoordinatorCreate(CoordinatorBase):
    """Data for creating coordinator profile"""
    user_id: int


class CoordinatorUpdate(BaseModel):
    """Data for updating coordinator profile"""
    department: Optional[str] = None
    assigned_subjects: Optional[list[str]] = None


class CoordinatorResponse(CoordinatorBase):
    """Coordinator response DTO"""
    coordinator_id: int
    user_id: int
    workload: int
    
    # User data (joined)
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True


class RegistrationReview(BaseModel):
    """Review registration request"""
    registration_id: int
    status: str  # approved, rejected
    coordinator_notes: Optional[str] = None
    rejection_reason: Optional[str] = None

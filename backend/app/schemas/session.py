"""
Session Schemas - Request/Response DTOs
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enum"""
    DRAFT = "draft"
    PUBLISHED = "published"
    PENDING_ASSIGNMENT = "pending_assignment"
    CONFIRMED = "confirmed"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LocationType(str, Enum):
    """Location type enum"""
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"


class ParticipantRole(str, Enum):
    """Participant role enum"""
    TUTOR = "tutor"
    STUDENT = "student"


class ParticipantStatus(str, Enum):
    """Participant status enum"""
    CONFIRMED = "confirmed"
    PENDING = "pending"
    CANCELLED = "cancelled"


# Participant Info Schemas
class ParticipantInfo(BaseModel):
    """Basic participant information"""
    user_id: int
    email: str
    full_name: str
    role: ParticipantRole
    status: ParticipantStatus
    joined_at: datetime
    
    class Config:
        from_attributes = True


class StudentInfo(BaseModel):
    """Student participant info"""
    user_id: int
    student_id: int
    email: str
    full_name: str
    status: ParticipantStatus
    
    class Config:
        from_attributes = True


class TutorInfo(BaseModel):
    """Tutor participant info"""
    user_id: int
    tutor_id: int
    email: str
    full_name: str
    specialization: Optional[str] = None
    
    class Config:
        from_attributes = True


class SessionBase(BaseModel):
    """Base session fields"""
    title: str
    description: Optional[str] = None
    subject_id: int
    scheduled_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration: int = Field(default=1, ge=1, le=4, description="Duration in hours (1-4)")
    location_type: LocationType = LocationType.ONLINE
    meeting_link: Optional[str] = None
    physical_address: Optional[str] = None
    max_students: int = Field(default=1, ge=1, description="Max students per session")


class SessionCreate(SessionBase):
    """Data for creating session - now supports multiple students"""
    tutor_id: int
    student_ids: list[int] = Field(default=[], description="List of student IDs to add to session")
    coordinator_id: Optional[int] = None


class SessionUpdate(BaseModel):
    """Data for updating session"""
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration: Optional[int] = Field(None, ge=1, le=4)
    location_type: Optional[LocationType] = None
    meeting_link: Optional[str] = None
    physical_address: Optional[str] = None
    status: Optional[SessionStatus] = None
    session_notes: Optional[str] = None


class SessionResponse(SessionBase):
    """Session response DTO - with multiple students support"""
    session_id: int
    tutor_id: int
    coordinator_id: Optional[int]
    status: SessionStatus
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    session_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # NEW: Multiple students instead of single student
    tutor: Optional[TutorInfo] = None
    students: list[StudentInfo] = Field(default=[], description="List of students in this session")
    
    # Subject info
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    
    class Config:
        from_attributes = True

class SessionListResponse(BaseModel):
    """Schema for paginated session list"""
    total: int
    sessions: list[SessionResponse]
    skip: int
    limit: int

class SessionMaterialCreate(BaseModel):
    """Upload session material"""
    session_id: int
    file_name: str
    file_url: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    description: Optional[str] = None


class SessionMaterialResponse(BaseModel):
    """Session material response"""
    material_id: int
    session_id: int
    uploaded_by: int
    file_name: str
    file_url: str
    file_type: Optional[str]
    file_size: Optional[int]
    description: Optional[str]
    uploaded_at: datetime
    
    # Joined data
    uploader_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SessionFeedbackCreate(BaseModel):
    """Create session feedback"""
    session_id: int
    reviewer_type: str  # student, tutor
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    comment: Optional[str] = None
    tags: Optional[list[str]] = Field(default=[], description="Feedback tags")
    is_anonymous: bool = False


class SessionFeedbackResponse(BaseModel):
    """Session feedback response"""
    feedback_id: int
    session_id: int
    reviewer_id: int
    reviewer_type: str
    rating: int
    comment: Optional[str]
    tags: Optional[list[str]]
    is_public: bool
    is_anonymous: bool
    created_at: datetime
    
    # Joined data
    reviewer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SessionResponseCreate(BaseModel):
    """Respond to session invitation"""
    session_id: int
    responder_type: str  # tutor, student
    action: str  # accept, decline, request_new_time
    reason: Optional[str] = None
    proposed_new_time: Optional[datetime] = None


class AttendanceCreate(BaseModel):
    """Record attendance"""
    session_id: int
    student_id: int
    status: str  # present, late, absent, excused
    notes: Optional[str] = None


class AttendanceResponse(BaseModel):
    """Attendance response"""
    attendance_id: int
    session_id: int
    student_id: int
    status: str
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    duration_minutes: Optional[int]
    notes: Optional[str]
    
    # Joined data
    student_name: Optional[str] = None
    
    class Config:
        from_attributes = True

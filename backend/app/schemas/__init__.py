"""Schemas package"""
from app.schemas.auth import (
    Token,
    TokenData,
    UserCreate,
    UserResponse,
    UserLogin,
    UserUpdate
)
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    TutorRequestCreate,
    SessionFeedbackCreate
)
from app.schemas.tutor import (
    TutorCreate,
    TutorUpdate,
    TutorResponse,
    AvailabilitySlot
)
from app.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionMaterialCreate
)
from app.schemas.scheduling import (
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityResponse,
    TimeSlotRequest,
    TimeSlotResponse
)
from app.schemas.report import (
    TutorPerformanceReport,
    StudentProgressReport,
    SystemStatistics,
    ReportFilters
)
from app.schemas.admin import (
    UserManagement,
    SystemConfig,
    ApprovalWorkflow
)

__all__ = [
    "Token",
    "TokenData", 
    "UserCreate",
    "UserResponse",
    "UserLogin",
    "UserUpdate",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "TutorRequestCreate",
    "SessionFeedbackCreate",
    "TutorCreate",
    "TutorUpdate",
    "TutorResponse",
    "AvailabilitySlot"
]

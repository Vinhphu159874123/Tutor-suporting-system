"""Schemas package"""
from app.schemas.auth import (
    Token,
    TokenData,
    UserCreate,
    UserResponse,
    UserLogin,
    UserUpdate,
    ChangePasswordRequest,
)
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserProfileUpdate,
    UserProfileResponse,
)
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    TutorRequestCreate,
    SessionFeedbackCreate,
)
from app.schemas.tutor import (
    TutorCreate,
    TutorUpdate,
    TutorResponse,
    AvailabilitySlot,
)
from app.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionMaterialCreate,
)
from app.schemas.scheduling import (
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityResponse,
    TimeSlotRequest,
    TimeSlotResponse,
)
from app.schemas.report import (
    TutorPerformanceReport,
    StudentProgressReport,
    SystemStatistics,
    ReportFilters,
)
from app.schemas.admin import (
    UserManagement,
    SystemConfig,
    ApprovalWorkflow,
)
from app.schemas.coordinator import (
    CoordinatorCreate,
    CoordinatorUpdate,
    CoordinatorResponse,
    RegistrationReview,
    ApprovalRequest,
)
from app.schemas.forum import (
    PostCreate,
    PostUpdate,
    PostResponse,
    CommentCreate,
    CommentResponse,
    CreatePostRequest,
    CreateReplyRequest,
)
from app.schemas.study_group import (
    CreateStudyGroupRequest,
    CreateActivityRequest,
    AddMemberRequest,
    SendMessageRequest,
)
from app.schemas.schedule_preference import (
    TimeSlot,
    SchedulePreferenceCreate,
    SchedulePreferenceUpdate,
)

__all__ = [
    # Auth
    "Token", "TokenData", "UserCreate", "UserResponse", "UserLogin",
    "UserUpdate", "ChangePasswordRequest",
    # User
    "UserProfileUpdate", "UserProfileResponse",
    # Student
    "StudentCreate", "StudentUpdate", "StudentResponse",
    "TutorRequestCreate", "SessionFeedbackCreate",
    # Tutor
    "TutorCreate", "TutorUpdate", "TutorResponse", "AvailabilitySlot",
    # Session
    "SessionCreate", "SessionUpdate", "SessionResponse", "SessionMaterialCreate",
    # Scheduling
    "AvailabilityCreate", "AvailabilityUpdate", "AvailabilityResponse",
    "TimeSlotRequest", "TimeSlotResponse",
    # Report
    "TutorPerformanceReport", "StudentProgressReport",
    "SystemStatistics", "ReportFilters",
    # Admin
    "UserManagement", "SystemConfig", "ApprovalWorkflow",
    # Coordinator
    "CoordinatorCreate", "CoordinatorUpdate", "CoordinatorResponse",
    "RegistrationReview", "ApprovalRequest",
    # Forum
    "PostCreate", "PostUpdate", "PostResponse",
    "CommentCreate", "CommentResponse",
    "CreatePostRequest", "CreateReplyRequest",
    # Study Group
    "CreateStudyGroupRequest", "CreateActivityRequest",
    "AddMemberRequest", "SendMessageRequest",
    # Schedule Preference
    "TimeSlot", "SchedulePreferenceCreate", "SchedulePreferenceUpdate",
]

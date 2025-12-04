from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float, Numeric, Date, Time, BigInteger, CheckConstraint, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import enum
from datetime import datetime

Base = declarative_base()

class UserRole(enum.Enum):
    STUDENT = "student"
    TUTOR = "tutor"
    COORDINATOR = "coordinator"
    ADMIN = "admin"

class SessionStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PENDING_ASSIGNMENT = "pending_assignment"
    CONFIRMED = "confirmed"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RegistrationStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AttendanceStatus(enum.Enum):
    PRESENT = "present"
    LATE = "late"
    ABSENT = "absent"
    EXCUSED = "excused"

class LocationType(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"

class MemberRole(enum.Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"
    OWNER = "owner"

class MemberStatus(enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    BANNED = "banned"

class ReviewerType(enum.Enum):
    STUDENT = "student"
    TUTOR = "tutor"

class ResponderType(enum.Enum):
    TUTOR = "tutor"
    STUDENT = "student"

class ResponseAction(enum.Enum):
    ACCEPT = "accept"
    DECLINE = "decline"
    REQUEST_NEW_TIME = "request_new_time"

class ResourceSource(enum.Enum):
    HCMUT_LIBRARY = "hcmut_library"
    YOUTUBE = "youtube"
    OTHER = "other"

class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SessionResponseStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELLED = "cancelled"

class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"

class AchievementType(str, Enum):
    MILESTONE = "milestone"
    STREAK = "streak"
    EXCELLENCE = "excellence"
    PARTICIPATION = "participation"
    IMPROVEMENT = "improvement"

class AchievementStatus(str, Enum):
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    EARNED = "earned"

class NotificationType(str, Enum):
    SESSION_REMINDER = "session_reminder"
    SESSION_CANCELLED = "session_cancelled"
    SESSION_UPDATED = "session_updated"
    NEW_MESSAGE = "new_message"
    ACHIEVEMENT_EARNED = "achievement_earned"
    REPORT_AVAILABLE = "report_available"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    STUDENT_ENROLLED = "student_enrolled"  # Student enrolled in course

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class ResourceType(str, Enum):
    BOOK = "book"
    ARTICLE = "article"
    VIDEO = "video"
    WEBSITE = "website"
    DOCUMENT = "document"
    OTHER = "other"

class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"

class User(Base):
    __tablename__ = "User"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    role = Column(ARRAY(String), nullable=False, server_default="{student}")  # Array: student, tutor, coordinator, admin
    avatar_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="user", uselist=False)
    tutor = relationship("Tutor", back_populates="user", uselist=False)
    coordinator = relationship("Coordinator", back_populates="user", uselist=False)
    created_forums = relationship("Forum", foreign_keys="Forum.creator_id", back_populates="creator")
    forum_memberships = relationship("ForumMember", back_populates="user")
    forum_posts = relationship("ForumPost", back_populates="author")
    study_group_created = relationship("StudyGroup", foreign_keys="StudyGroup.creator_id", back_populates="creator")
    study_group_memberships = relationship("StudyGroupMember", back_populates="user")
    uploaded_materials = relationship("SessionMaterial", back_populates="uploader")
    session_feedbacks = relationship("SessionFeedback", back_populates="reviewer")
    session_responses = relationship("SessionResponse", back_populates="user")
    reports_generated = relationship("OverallAcademicReport", back_populates="generator")
    notifications = relationship("Notifications", back_populates="user")

class Student(Base):
    __tablename__ = "student"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    student_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), unique=True, nullable=False)
    student_code = Column(String, nullable=False, unique=True)
    faculty = Column(String, nullable=True)
    major = Column(String, nullable=True)
    year = Column(Integer, CheckConstraint('year >= 1 AND year <= 5'), nullable=True)
    preferences = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="student")
    sessions = relationship("Session", back_populates="student")
    registrations = relationship("StudentRegistration", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")
    progress_trackings = relationship("ProgressTracking", back_populates="student")
    achievements = relationship("LearningAchievements", back_populates="student")
    schedule_preferences = relationship("SchedulePreference", back_populates="student")

class Tutor(Base):
    __tablename__ = "tutor"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    tutor_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), unique=True, nullable=False)
    staff_code = Column(String, nullable=True)
    faculty = Column(String, nullable=True)
    hourly_rate = Column(Numeric, default=0)
    bio = Column(Text, nullable=True)
    rating = Column(Numeric, CheckConstraint('rating >= 0 AND rating <= 5'), default=0)
    total_sessions = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    teaching_experience = Column(JSONB, default={})
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tutor")
    sessions = relationship("Session", back_populates="tutor")
    registrations = relationship("TutorRegistration", back_populates="tutor")
    activity_reports = relationship("TutorActivityReport", back_populates="tutor")
    matching_logs = relationship("MatchingLog", back_populates="selected_tutor")
    schedules = relationship("SessionSchedule", back_populates="tutor")
    availabilities = relationship("TutorAvailability", back_populates="tutor")

class Coordinator(Base):
    __tablename__ = "coordinator"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    coordinator_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), unique=True, nullable=False)
    department = Column(String, nullable=True)
    assigned_subjects = Column(JSONB, default=[])
    workload = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="coordinator")
    approved_student_regs = relationship("StudentRegistration", back_populates="approved_by_coordinator")
    approved_tutor_regs = relationship("TutorRegistration", back_populates="approved_by_coordinator")
    coordinated_sessions = relationship("Session", back_populates="coordinator")
    matching_logs = relationship("MatchingLog", back_populates="coordinator")

class Subject(Base):
    __tablename__ = "subject"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    subject_id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String, nullable=False, unique=True)
    subject_name = Column(String, nullable=False)
    department = Column(String, nullable=True)
    credits = Column(Integer, default=3)
    description = Column(Text, nullable=True)
    prerequisites = Column(JSONB, default=[])
    
    # Relationships
    sessions = relationship("Session", back_populates="subject")
    student_registrations = relationship("StudentRegistration", back_populates="subject")
    tutor_registrations = relationship("TutorRegistration", back_populates="subject")
    forums = relationship("Forum", back_populates="subject")
    study_groups = relationship("StudyGroup", back_populates="subject")
    course_reports = relationship("CourseReport", back_populates="subject")
    progress_trackings = relationship("ProgressTracking", back_populates="subject")
    schedules = relationship("SessionSchedule", back_populates="subject")
    schedule_preferences = relationship("SchedulePreference", back_populates="subject")

class SessionParticipant(Base):
    """Session participant - link between session and users (tutor/students)"""
    __tablename__ = "SessionParticipant"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    participant_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('tutor_system.session.session_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('tutor_system.User.user_id'), nullable=False)
    role = Column(String, nullable=False)  # 'tutor' or 'student'
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default='confirmed')  # confirmed, pending, cancelled
    notes = Column(Text, nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="participants")
    user = relationship("User")

class Session(Base):
    __tablename__ = "session"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    session_id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutor_system.tutor.tutor_id"), nullable=False)
    student_id = Column(Integer, ForeignKey("tutor_system.student.student_id"), nullable=True)  # DEPRECATED - use SessionParticipant
    subject_id = Column(Integer, ForeignKey("tutor_system.subject.subject_id"), nullable=False)
    coordinator_id = Column(Integer, ForeignKey("tutor_system.coordinator.coordinator_id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    scheduled_date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    duration = Column(Integer, CheckConstraint('duration >= 1 AND duration <= 4'), default=1)
    
    location_type = Column(String, default='online')  # online, offline, hybrid
    meeting_link = Column(Text, nullable=True)
    physical_address = Column(Text, nullable=True)
    
    status = Column(String, default='draft')  # draft, published, pending_assignment, confirmed, ongoing, completed, cancelled
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    
    session_notes = Column(Text, nullable=True)
    max_students = Column(Integer, default=1)
    materials = Column(JSONB, nullable=True, default=list)  # List of material file names
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tutor = relationship("Tutor", back_populates="sessions")
    student = relationship("Student", back_populates="sessions")  # DEPRECATED - use participants
    subject = relationship("Subject", back_populates="sessions")
    coordinator = relationship("Coordinator", back_populates="coordinated_sessions")
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")
    session_materials = relationship("SessionMaterial", back_populates="session", cascade="all, delete-orphan")
    feedbacks = relationship("SessionFeedback", back_populates="session")
    responses = relationship("SessionResponse", back_populates="session")
    attendance_records = relationship("Attendance", back_populates="session")
    external_resources = relationship("ExternalResource", back_populates="session")
    matching_logs = relationship("MatchingLog", back_populates="session")
    progress_tracking = relationship("ProgressTracking", back_populates="session", uselist=False)

class StudentRegistration(Base):
    __tablename__ = "studentregistration"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    registration_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("tutor_system.student.student_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("tutor_system.subject.subject_id"), nullable=False)
    learning_goals = Column(Text, nullable=True)
    urgency = Column(String, default='medium')  # high, medium, low
    status = Column(String, default='pending')  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey("tutor_system.coordinator.coordinator_id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="registrations")
    subject = relationship("Subject", back_populates="student_registrations")
    approved_by_coordinator = relationship("Coordinator", back_populates="approved_student_regs")

class TutorRegistration(Base):
    __tablename__ = "tutorregistration"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    registration_id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutor_system.tutor.tutor_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("tutor_system.subject.subject_id"), nullable=False)
    gpa = Column(Numeric, CheckConstraint('gpa >= 0 AND gpa <= 4.0'), nullable=True)
    qualifications = Column(Text, nullable=True)
    status = Column(String, default='pending')  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey("tutor_system.coordinator.coordinator_id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    # Course schedule fields
    total_sessions = Column(Integer, default=10, nullable=False)  # Số buổi học (mặc định 10)
    start_date = Column(Date, nullable=True)  # Ngày bắt đầu dạy
    end_date = Column(Date, nullable=True)  # Ngày kết thúc dự kiến
    availability = Column(JSONB, nullable=True)  # Lịch rảnh theo tuần (JSONB format)
    max_students = Column(Integer, default=25, nullable=False)  # Số sinh viên tối đa mỗi buổi (1-35)
    selected_schedule_id = Column(Integer, ForeignKey("tutor_system.session_schedule.schedule_id"), nullable=True)  # Schedule coordinator chọn
    
    # Relationships
    tutor = relationship("Tutor", back_populates="registrations")
    subject = relationship("Subject", back_populates="tutor_registrations")
    approved_by_coordinator = relationship("Coordinator", back_populates="approved_tutor_regs")

class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    attendance_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tutor_system.session.session_id"), nullable=False)
    student_id = Column(Integer, ForeignKey("tutor_system.student.student_id"), nullable=False)
    status = Column(String, default='present')  # present, late, absent, excused
    check_in_time = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")

class SessionMaterial(Base):
    __tablename__ = "sessionmaterial"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    material_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tutor_system.session.session_id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(Text, nullable=True)  # External URL (optional if file_data exists)
    file_data = Column(LargeBinary, nullable=True)  # Store actual file in database (BYTEA)
    file_type = Column(String, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    description = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="session_materials")
    uploader = relationship("User", back_populates="uploaded_materials")

class SessionFeedback(Base):
    __tablename__ = "sessionfeedback"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    feedback_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tutor_system.session.session_id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    reviewer_type = Column(String, nullable=False)  # student, tutor
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    comment = Column(Text, nullable=True)
    tags = Column(JSONB, default=[])
    is_public = Column(Boolean, default=True)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="feedbacks")
    reviewer = relationship("User", back_populates="session_feedbacks")

class SessionResponse(Base):
    __tablename__ = "sessionresponse"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    response_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tutor_system.session.session_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    responder_type = Column(String, nullable=False)  # tutor, student
    action = Column(String, nullable=False)  # accept, decline, request_new_time
    reason = Column(Text, nullable=True)
    proposed_new_time = Column(DateTime(timezone=True), nullable=True)
    is_final = Column(Boolean, default=False)
    responded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="responses")
    user = relationship("User", back_populates="session_responses")

class ExternalResource(Base):
    __tablename__ = "externalresource"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    resource_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tutor_system.session.session_id"), nullable=False)
    resource_name = Column(String, nullable=False)
    library_resource_id = Column(String, nullable=True)
    external_url = Column(Text, nullable=True)
    source = Column(String, nullable=True)  # hcmut_library, youtube, other
    description = Column(Text, nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="external_resources")

class MatchingLog(Base):
    __tablename__ = "matchinglog"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    log_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tutor_system.session.session_id"), nullable=False)
    student_id = Column(Integer, ForeignKey("tutor_system.student.student_id"), nullable=False)
    coordinator_id = Column(Integer, ForeignKey("tutor_system.coordinator.coordinator_id"), nullable=True)
    ai_provider = Column(String, nullable=True)
    ai_model = Column(String, nullable=True)
    request_data = Column(JSONB, nullable=True)
    ai_response = Column(JSONB, nullable=True)
    candidates = Column(JSONB, default=[])
    selected_tutor_id = Column(Integer, ForeignKey("tutor_system.tutor.tutor_id"), nullable=True)
    match_score = Column(Numeric, CheckConstraint('match_score >= 0 AND match_score <= 100'), nullable=True)
    matching_criteria = Column(Text, nullable=True)
    processing_time_ms = Column(Numeric, nullable=True)
    matched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="matching_logs")
    student = relationship("Student")
    coordinator = relationship("Coordinator", back_populates="matching_logs")
    selected_tutor = relationship("Tutor", back_populates="matching_logs")

class Forum(Base):
    __tablename__ = "forum"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    forum_id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("tutor_system.subject.subject_id"), nullable=True)
    forum_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String, nullable=True)
    is_public = Column(Boolean, default=True)
    require_approval = Column(Boolean, default=False)
    member_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_forums")
    subject = relationship("Subject", back_populates="forums")
    members = relationship("ForumMember", back_populates="forum")
    posts = relationship("ForumPost", back_populates="forum")

class ForumMember(Base):
    __tablename__ = "forummember"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    member_id = Column(Integer, primary_key=True, index=True)
    forum_id = Column(Integer, ForeignKey("tutor_system.forum.forum_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    role = Column(String, default='member')  # admin, moderator, member
    status = Column(String, default='active')  # active, pending, banned
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    forum = relationship("Forum", back_populates="members")
    user = relationship("User", back_populates="forum_memberships")

class ForumPost(Base):
    __tablename__ = "forumpost"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    post_id = Column(Integer, primary_key=True, index=True)
    forum_id = Column(Integer, ForeignKey("tutor_system.forum.forum_id"), nullable=False)
    author_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    parent_post_id = Column(Integer, ForeignKey("tutor_system.forumpost.post_id"), nullable=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    attachments = Column(JSONB, default=[])
    is_pinned = Column(Boolean, default=False)
    upvote_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    forum = relationship("Forum", back_populates="posts")
    author = relationship("User", back_populates="forum_posts")
    parent_post = relationship("ForumPost", remote_side=[post_id], foreign_keys=[parent_post_id])

class StudyGroup(Base):
    __tablename__ = "studygroup"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    group_id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("tutor_system.subject.subject_id"), nullable=True)
    group_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String, nullable=True)
    is_public = Column(Boolean, default=True)
    require_approval = Column(Boolean, default=False)
    member_count = Column(Integer, default=0)
    max_members = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], back_populates="study_group_created")
    subject = relationship("Subject", back_populates="study_groups")
    members = relationship("StudyGroupMember", back_populates="group")
    posts = relationship("StudyGroupPost", back_populates="group")

class StudyGroupMember(Base):
    __tablename__ = "studygroupmember"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    member_id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("tutor_system.studygroup.group_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    role = Column(String, default='member')  # owner, member
    status = Column(String, default='active')  # active, pending
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    group = relationship("StudyGroup", back_populates="members")
    user = relationship("User", back_populates="study_group_memberships")

class StudyGroupPost(Base):
    __tablename__ = "studygrouppost"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    post_id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("tutor_system.studygroup.group_id"), nullable=False)
    author_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    parent_post_id = Column(Integer, ForeignKey("tutor_system.studygrouppost.post_id"), nullable=True)
    content = Column(Text, nullable=False)
    attachments = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    group = relationship("StudyGroup", back_populates="posts")
    author = relationship("User")
    parent_post = relationship("StudyGroupPost", remote_side=[post_id], foreign_keys=[parent_post_id])

class StudyGroupMaterial(Base):
    __tablename__ = "studygroupmaterial"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    material_id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("tutor_system.studygroup.group_id"), nullable=False)
    uploader_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    file_path = Column(String)
    file_url = Column(String)
    file_type = Column(String)  # pdf, doc, video, link
    file_size = Column(Integer)
    file_data = Column(LargeBinary)  # Store file binary data in database
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    group = relationship("StudyGroup")
    uploader = relationship("User")

class StudyGroupActivity(Base):
    __tablename__ = "studygroupactivity"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    activity_id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("tutor_system.studygroup.group_id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    activity_type = Column(String, nullable=False)  # meeting, assignment, discussion
    title = Column(String, nullable=False)
    description = Column(Text)
    scheduled_date = Column(Date)
    scheduled_time = Column(Time)
    location = Column(String)
    meeting_link = Column(String)
    status = Column(String, default='upcoming')  # upcoming, active, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    group = relationship("StudyGroup")
    creator = relationship("User")

class CourseReport(Base):
    __tablename__ = "coursereport"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    report_id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("tutor_system.subject.subject_id"), nullable=False)
    report_period_start = Column(Date, nullable=False)
    report_period_end = Column(Date, nullable=False)
    total_sessions = Column(Integer, default=0)
    total_students = Column(Integer, default=0)
    total_tutors = Column(Integer, default=0)
    avg_session_rating = Column(Numeric, nullable=True)
    completion_rate = Column(Numeric, nullable=True)
    metrics = Column(JSONB, default={})
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subject = relationship("Subject", back_populates="course_reports")

class TutorActivityReport(Base):
    __tablename__ = "tutoractivityreport"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    report_id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutor_system.tutor.tutor_id"), nullable=False)
    report_period_start = Column(Date, nullable=False)
    report_period_end = Column(Date, nullable=False)
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    avg_rating = Column(Numeric, nullable=True)
    total_students = Column(Integer, default=0)
    total_hours = Column(Integer, default=0)
    social_activity_score = Column(Numeric, nullable=True)
    activity_details = Column(JSONB, default={})
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tutor = relationship("Tutor", back_populates="activity_reports")

class ProgressTracking(Base):
    __tablename__ = "progress_tracking"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    progress_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tutor_system.session.session_id"), nullable=False, unique=True)
    student_id = Column(Integer, ForeignKey("tutor_system.student.student_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("tutor_system.subject.subject_id"), nullable=False)
    topics_covered = Column(ARRAY(Text))  # text[] in PostgreSQL
    understanding_level = Column(Integer, CheckConstraint('understanding_level >= 1 AND understanding_level <= 5'))
    strengths = Column(Text)
    weaknesses = Column(Text)
    notes = Column(Text)
    tutor_feedback = Column(Text)
    homework_assigned = Column(Text)
    homework_completed = Column(Boolean, default=False)
    homework_grade = Column(Integer, CheckConstraint('homework_grade >= 0 AND homework_grade <= 100'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="progress_tracking")
    student = relationship("Student", back_populates="progress_trackings")
    subject = relationship("Subject", back_populates="progress_trackings")

class LearningAchievements(Base):
    __tablename__ = "learning_achievements"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    achievement_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("tutor_system.student.student_id"), nullable=False)
    achievement_type = Column(String, nullable=False)  # first_session, sessions_10, sessions_50, etc.
    title = Column(String, nullable=False)
    description = Column(Text)
    icon_url = Column(Text)
    achievement_metadata = Column(JSONB, default={})
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="achievements")

class Notifications(Base):
    __tablename__ = "notifications"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("tutor_system.User.user_id"), nullable=False)
    type = Column(String, nullable=False)  # session_created, session_updated, etc.
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    related_entity_type = Column(String)
    related_entity_id = Column(Integer)
    data = Column(JSONB, default={})
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class LibraryResourcesCache(Base):
    __tablename__ = "library_resources_cache"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    cache_id = Column(Integer, primary_key=True, index=True)
    library_resource_id = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    authors = Column(JSONB, default=[])  # Array in PostgreSQL
    publisher = Column(String)
    published_year = Column(Integer)
    isbn = Column(String)
    resource_type = Column(String)  # book, journal, thesis, paper, video, other
    subject_category = Column(String)
    description = Column(Text)
    thumbnail_url = Column(Text)
    is_available = Column(Boolean, default=True)
    location = Column(String)
    call_number = Column(String)
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    access_count = Column(Integer, default=0)

class SessionSchedule(Base):
    __tablename__ = "session_schedule"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    schedule_id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutor_system.tutor.tutor_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("tutor_system.subject.subject_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String)  # daily, weekly, biweekly, monthly
    day_of_week = Column(Integer, CheckConstraint('day_of_week >= 0 AND day_of_week <= 6'))
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration = Column(Integer, CheckConstraint('duration >= 1 AND duration <= 4'))
    location_type = Column(String, default="online")
    meeting_link = Column(Text)
    physical_address = Column(Text)
    max_students = Column(Integer, default=1)
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tutor = relationship("Tutor", back_populates="schedules")
    subject = relationship("Subject", back_populates="schedules")

class OverallAcademicReport(Base):
    __tablename__ = "overall_academic_report"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    report_id = Column(Integer, primary_key=True, index=True)
    report_period_start = Column(Date, nullable=False)
    report_period_end = Column(Date, nullable=False)
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    cancelled_sessions = Column(Integer, default=0)
    total_students = Column(Integer, default=0)
    active_students = Column(Integer, default=0)
    total_tutors = Column(Integer, default=0)
    active_tutors = Column(Integer, default=0)
    verified_tutors = Column(Integer, default=0)
    total_subjects = Column(Integer, default=0)
    avg_session_rating = Column(Numeric)
    avg_tutor_rating = Column(Numeric)
    completion_rate = Column(Numeric)
    total_forums = Column(Integer, default=0)
    total_forum_posts = Column(Integer, default=0)
    total_study_groups = Column(Integer, default=0)
    subject_breakdown = Column(JSONB, default={})
    faculty_breakdown = Column(JSONB, default={})
    session_type_breakdown = Column(JSONB, default={})
    generated_by = Column(Integer, ForeignKey("tutor_system.User.user_id"))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    generator = relationship("User")


class PreferenceStatus(str, Enum):
    PENDING = "pending"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class SessionFormat(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BOTH = "both"

class SchedulePreference(Base):
    """Student schedule preferences for course requests"""
    __tablename__ = "SchedulePreference"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    preference_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("tutor_system.student.student_id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("tutor_system.subject.subject_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Scheduling details
    preferred_start_date = Column(Date, nullable=False)
    total_sessions = Column(Integer, nullable=False)
    session_duration = Column(Integer, nullable=False)  # in minutes
    session_format = Column(String(20), nullable=False, default='both')
    
    # Available time slots (JSON array)
    # Format: [{"day": "monday", "start_time": "08:00", "end_time": "10:00"}, ...]
    available_time_slots = Column(JSONB, nullable=False)
    
    # Additional info
    notes = Column(Text)
    status = Column(String(20), nullable=False, default='pending')
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    student = relationship("Student", back_populates="schedule_preferences")
    subject = relationship("Subject", back_populates="schedule_preferences")

class TutorAvailability(Base):
    """Tutor availability schedule"""
    __tablename__ = "tutor_availability"
    __table_args__ = {
        'schema': 'tutor_system',
        'extend_existing': True
    }
    
    availability_id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutor_system.tutor.tutor_id"), nullable=False, index=True)
    
    # Recurring vs One-time
    is_recurring = Column(Boolean, nullable=False, default=True)
    day_of_week = Column(Integer)  # 0-6 for Mon-Sun (for recurring)
    specific_date = Column(Date)   # For one-time availability
    
    # Time slots
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Availability status
    is_available = Column(Boolean, nullable=False, default=True)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tutor = relationship("Tutor", back_populates="availabilities")



        
        
    
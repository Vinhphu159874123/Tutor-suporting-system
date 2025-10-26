from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

Base = declarative_base()

class UserRole(enum.Enum):
    STUDENT = "student"
    TUTOR = "tutor"
    COORDINATOR = "coordinator"
    DEPARTMENT_CHAIR = "department_chair"
    ACADEMIC_AFFAIR = "academic_affair"
    ADMIN = "admin"

class SessionStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class RegistrationStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), unique=True, index=True, nullable=True)  # MSSV
    staff_id = Column(String(20), unique=True, index=True, nullable=True)    # MSCB
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for SSO users
    role = Column(String(50), nullable=False)  # Stored as string: 'admin', 'student', 'tutor', etc.
    faculty = Column(String(100), nullable=True)
    major = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # SSO Integration
    sso_id = Column(String(100), unique=True, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    tutor_profile = relationship("Tutor", back_populates="user", uselist=False)
    student_profile = relationship("Student", back_populates="user", uselist=False)

class Tutor(Base):
    __tablename__ = "tutors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    bio = Column(Text, nullable=True)
    subjects = Column(Text, nullable=True)  # JSON array - teaching subjects
    expertise_areas = Column(Text, nullable=True)  # JSON string - deprecated, use subjects
    available_hours = Column(Text, nullable=True)  # JSON string - availability schedule
    hourly_rate = Column(Float, nullable=True)
    experience_years = Column(Integer, default=0)  # Years of teaching experience
    rating = Column(Float, default=0.0)
    total_sessions = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)  # Currently available for tutoring
    is_approved = Column(Boolean, default=False)
    approval_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tutor_profile")
    sessions = relationship("Session", back_populates="tutor")
    registrations = relationship("TutorRegistration", back_populates="tutor")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    year = Column(Integer, nullable=True)  # Năm học (1-5)
    gpa = Column(Float, nullable=True)
    learning_goals = Column(Text, nullable=True)
    subjects_needed = Column(Text, nullable=True)  # JSON string - subjects needing help
    preferred_subjects = Column(Text, nullable=True)  # JSON string - deprecated, use subjects_needed
    preferred_schedule = Column(Text, nullable=True)  # Preferred time slots
    study_schedule = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)  # Active student status
    total_sessions = Column(Integer, default=0)  # Total completed sessions
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    sessions = relationship("Session", back_populates="student")
    registrations = relationship("StudentRegistration", back_populates="student")

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)  # Mã môn học
    name = Column(String(200), nullable=False)
    faculty = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutors.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    location = Column(String(200), nullable=True)
    is_online = Column(Boolean, default=False)
    meeting_url = Column(String(500), nullable=True)
    
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED)
    
    # Session content
    materials = Column(Text, nullable=True)  # JSON string
    notes = Column(Text, nullable=True)
    homework = Column(Text, nullable=True)
    
    # Feedback and evaluation
    tutor_feedback = Column(Text, nullable=True)
    student_feedback = Column(Text, nullable=True)
    tutor_rating = Column(Float, nullable=True)
    student_rating = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    tutor = relationship("Tutor", back_populates="sessions")
    student = relationship("Student", back_populates="sessions")
    subject = relationship("Subject")

class TutorRegistration(Base):
    __tablename__ = "tutor_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutors.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    qualification = Column(Text, nullable=True)  # Bằng cấp, chứng chỉ
    experience = Column(Text, nullable=True)
    status = Column(Enum(RegistrationStatus), default=RegistrationStatus.PENDING)
    
    coordinator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    coordinator_notes = Column(Text, nullable=True)
    
    submitted_at = Column(DateTime, default=func.now())
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    tutor = relationship("Tutor", back_populates="registrations")
    subject = relationship("Subject")
    coordinator = relationship("User")

class StudentRegistration(Base):
    __tablename__ = "student_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    reason = Column(Text, nullable=True)  # Lý do đăng ký
    current_grade = Column(String(5), nullable=True)
    target_grade = Column(String(5), nullable=True)
    
    status = Column(Enum(RegistrationStatus), default=RegistrationStatus.PENDING)
    
    coordinator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    coordinator_notes = Column(Text, nullable=True)
    
    submitted_at = Column(DateTime, default=func.now())
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="registrations")
    subject = relationship("Subject")
    coordinator = relationship("User")

class Forum(Base):
    __tablename__ = "forums"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    creator = relationship("User")
    subject = relationship("Subject")

class ForumPost(Base):
    __tablename__ = "forum_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    forum_id = Column(Integer, ForeignKey("forums.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=True)  # For replies
    
    likes = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    forum = relationship("Forum")
    author = relationship("User")
    parent = relationship("ForumPost", remote_side=[id])

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)  # course, academic, tutor_activity
    generated_by = Column(Integer, ForeignKey("users.id"))
    generated_at = Column(DateTime, default=func.now())
    
    # Report data (JSON)
    data = Column(Text, nullable=True)
    
    # Filters used
    filters = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    generator = relationship("User")
"""
User Schemas
Pydantic models for user-related operations
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user fields"""
    email: EmailStr
    full_name: str
    role: str  # student, tutor, coordinator, admin
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    """User registration"""
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    """User profile response"""
    user_id: int
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """User profile update"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserInDB(UserBase):
    """User in database with password hash"""
    user_id: int
    hashed_password: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update (API router)"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    program: Optional[str] = None
    faculty: Optional[str] = None
    major: Optional[str] = None


class UserProfileResponse(BaseModel):
    """User profile response with multi-role support (API router)"""
    user_id: int
    email: str
    full_name: str
    role: list[str]
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    program: Optional[str] = None
    faculty: Optional[str] = None
    major: Optional[str] = None

    class Config:
        from_attributes = True

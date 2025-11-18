"""
Authentication Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ============================================================================
# AUTH REQUEST/RESPONSE SCHEMAS
# ============================================================================

class Token(BaseModel):
    """JWT Token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """JWT Token payload data"""
    email: Optional[str] = None

class UserBase(BaseModel):
    """Base user fields"""
    email: EmailStr
    full_name: str
    faculty: Optional[str] = None
    major: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    """User creation schema"""
    password: str
    role: str  # 'student', 'tutor', 'admin', etc.

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to map user_id to id"""
        if hasattr(obj, 'user_id'):
            obj.id = obj.user_id
        return super().model_validate(obj)

class UserLogin(BaseModel):
    """Login credentials"""
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """User profile update"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

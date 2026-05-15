"""
Authentication Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
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
    role: List[str] = ['student']  # Array of roles: 'student', 'tutor', 'admin', etc.
    student_code: Optional[str] = None  # Student code (e.g., 2152001)
    year: Optional[int] = None  # Year of study (1-5)

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    role: List[str]  # Array of roles user has
    is_active: bool
    is_verified: bool
    created_at: datetime
    tutor_id: Optional[int] = None
    student_id: Optional[int] = None
    available_roles: List[str] = []

    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to map user_id to id and populate available_roles"""
        if hasattr(obj, 'user_id'):
            obj.id = obj.user_id
        
        # available_roles is now same as role array (user can have multiple roles)
        if hasattr(obj, 'role') and obj.role:
            obj.available_roles = obj.role if isinstance(obj.role, list) else [obj.role]
        else:
            obj.available_roles = []
        
        return super().model_validate(obj)

class UserLogin(BaseModel):
    """Login credentials"""
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """User profile update"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str

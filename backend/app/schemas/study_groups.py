"""
Study Groups Schemas - PLACEHOLDER
Pydantic models for study groups API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ============================================================================
# STUDY GROUPS SCHEMAS - PLACEHOLDER IMPLEMENTATIONS
# ============================================================================

class StudyGroupBase(BaseModel):
    """Base study group schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    subject_id: int = Field(..., gt=0)

class StudyGroupCreate(StudyGroupBase):
    """Schema for creating study group"""
    max_members: Optional[int] = Field(10, ge=2, le=50)

class StudyGroupUpdate(BaseModel):
    """Schema for updating study group"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    max_members: Optional[int] = Field(None, ge=2, le=50)
    is_active: Optional[bool] = None

class StudyGroupResponse(StudyGroupBase):
    """Schema for study group response"""
    id: int
    creator_id: int
    max_members: int
    current_member_count: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudyGroupMemberResponse(BaseModel):
    """Schema for group member response"""
    id: int
    group_id: int
    user_id: int
    user_name: str
    role: str = Field(..., regex="^(admin|moderator|member)$")
    joined_at: datetime
    
    class Config:
        from_attributes = True

class JoinGroupRequest(BaseModel):
    """Schema for joining group request"""
    message: Optional[str] = Field(None, max_length=500)

class GroupListResponse(BaseModel):
    """Schema for groups list response"""
    groups: List[StudyGroupResponse]
    total_count: int

# TODO: Add more schemas as needed
# - GroupActivityResponse
# - GroupSearchRequest
# - GroupInviteRequest
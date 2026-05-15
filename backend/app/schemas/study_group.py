"""
Study Group Schemas — Request/Response DTOs
"""
from pydantic import BaseModel
from typing import Optional


class CreateStudyGroupRequest(BaseModel):
    group_name: str
    subject_id: int
    description: Optional[str] = None
    topic: Optional[str] = None
    max_members: int = 10
    is_public: bool = True
    require_approval: bool = False


class CreateActivityRequest(BaseModel):
    activity_type: str
    title: str
    description: Optional[str] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None


class AddMemberRequest(BaseModel):
    user_id: int


class SendMessageRequest(BaseModel):
    message_text: str

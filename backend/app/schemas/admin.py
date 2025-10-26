"""
Admin Schemas - Request/Response DTOs
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserManagement(BaseModel):
    """User management data"""
    user_id: int
    action: str  # 'activate', 'deactivate', 'delete', 'change_role'
    role: Optional[str] = None
    reason: Optional[str] = None


class SystemConfig(BaseModel):
    """System configuration"""
    config_key: str
    config_value: str
    description: Optional[str] = None


class ApprovalWorkflow(BaseModel):
    """Approval workflow data"""
    request_id: int
    request_type: str  # 'tutor_registration', 'session_appeal', etc.
    action: str  # 'approve', 'reject'
    notes: Optional[str] = None

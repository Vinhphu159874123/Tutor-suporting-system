"""
Materials Schemas - PLACEHOLDER
Pydantic models for session materials API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ============================================================================
# MATERIALS SCHEMAS - PLACEHOLDER IMPLEMENTATIONS
# ============================================================================

class MaterialBase(BaseModel):
    """Base material schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

class MaterialCreate(MaterialBase):
    """Schema for creating material (without file)"""
    session_id: int = Field(..., gt=0)

class MaterialUpload(BaseModel):
    """Schema for file upload metadata"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

class MaterialUpdate(BaseModel):
    """Schema for updating material metadata"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

class MaterialResponse(MaterialBase):
    """Schema for material response"""
    id: int
    session_id: int
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MaterialListResponse(BaseModel):
    """Schema for materials list response"""
    materials: list[MaterialResponse]
    total_count: int
    session_id: int

class MaterialDownloadResponse(BaseModel):
    """Schema for download response"""
    download_url: str
    filename: str
    expires_at: datetime

# TODO: Add more schemas as needed
# - MaterialSearchRequest
# - MaterialStatsResponse
# - MaterialPermissionCheck
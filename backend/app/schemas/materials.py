"""
Materials Schemas
Pydantic models for session materials API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ============================================================================
# MATERIALS SCHEMAS
# ============================================================================

class MaterialResponse(BaseModel):
    """Schema for material response"""
    material_id: int
    session_id: int
    file_name: str
    file_url: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    description: Optional[str] = None
    uploaded_by: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
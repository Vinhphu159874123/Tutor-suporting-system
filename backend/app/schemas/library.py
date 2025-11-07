"""
Library Resources Schemas - PLACEHOLDER
Pydantic models for library resources cache API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LibraryResourceBase(BaseModel):
    """Base library resource schema"""
    library_resource_id: str = Field(..., max_length=255)
    title: str = Field(..., max_length=500)
    authors: List[str] = Field(default_factory=list)
    publisher: Optional[str] = Field(None, max_length=255)
    published_year: Optional[int] = None
    isbn: Optional[str] = Field(None, max_length=50)
    resource_type: Optional[str] = Field(None, max_length=50)
    subject_category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_available: bool = True
    location: Optional[str] = Field(None, max_length=255)
    call_number: Optional[str] = Field(None, max_length=100)


class LibraryResourceCreate(LibraryResourceBase):
    """Schema for creating library resource"""
    pass


class LibraryResourceUpdate(BaseModel):
    """Schema for updating library resource"""
    is_available: Optional[bool] = None
    location: Optional[str] = None
    description: Optional[str] = None


class LibraryResourceResponse(LibraryResourceBase):
    """Schema for library resource response"""
    cache_id: int
    cached_at: datetime
    last_accessed: datetime
    access_count: int
    
    class Config:
        from_attributes = True


class LibrarySearchQuery(BaseModel):
    """Schema for library search"""
    query: str = Field(..., min_length=1, max_length=255)
    resource_type: Optional[str] = None
    subject_category: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

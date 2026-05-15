"""
Forum Schemas - Request/Response DTOs
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PostBase(BaseModel):
    """Base post fields"""
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)
    subject: Optional[str] = None
    tags: List[str] = []


class PostCreate(PostBase):
    """Data for creating post"""
    pass


class PostUpdate(BaseModel):
    """Data for updating post"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    tags: Optional[List[str]] = None


class PostResponse(PostBase):
    """Post response DTO"""
    id: int
    author_id: int
    author_name: Optional[str] = None
    views: int = 0
    votes: int = 0
    comments_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    """Data for creating comment"""
    post_id: int
    content: str = Field(..., min_length=1)
    parent_id: Optional[int] = None


class CommentResponse(BaseModel):
    """Comment response DTO"""
    id: int
    post_id: int
    author_id: int
    author_name: Optional[str] = None
    content: str
    votes: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreatePostRequest(BaseModel):
    """Create forum post request"""
    title: str
    content: str
    category: Optional[str] = "other"
    forum_id: Optional[int] = 1
    is_pinned: Optional[bool] = False


class CreateReplyRequest(BaseModel):
    """Create reply to a post"""
    content: str
    parent_post_id: int

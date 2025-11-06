"""
Matching Schemas - AI-powered tutor-student matching
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class MatchingRequest(BaseModel):
    """Request AI matching for tutor"""
    session_id: int
    student_id: int
    matching_criteria: Optional[str] = Field(None, description="Custom matching criteria")
    ai_provider: Optional[str] = Field("openai", description="AI provider (openai, anthropic, etc.)")
    ai_model: Optional[str] = Field("gpt-4", description="AI model to use")


class TutorCandidate(BaseModel):
    """Tutor candidate from AI matching"""
    tutor_id: int
    tutor_name: str
    faculty: Optional[str]
    rating: Decimal
    total_sessions: int
    match_score: Decimal = Field(..., ge=0, le=100, description="Match score (0-100)")
    match_reasons: list[str] = Field(default=[], description="Reasons for match")


class MatchingResponse(BaseModel):
    """AI matching result"""
    log_id: int
    session_id: int
    student_id: int
    ai_provider: str
    ai_model: str
    candidates: list[TutorCandidate]
    selected_tutor_id: Optional[int]
    match_score: Optional[Decimal]
    processing_time_ms: Optional[Decimal]
    matched_at: datetime
    
    class Config:
        from_attributes = True


class SelectTutorRequest(BaseModel):
    """Select tutor from candidates"""
    log_id: int
    selected_tutor_id: int

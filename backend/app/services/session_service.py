"""
Session Service - Business Logic Layer
Now with event emission for async side effects
"""
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.repositories.session_repository import SessionRepository
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.events import event_bus, EventTypes


class SessionService:
    """Business logic for session operations - PLACEHOLDER"""
    
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo
    
    async def get_session(self, session_id: int) -> SessionResponse:
        """Get session by ID"""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        return SessionResponse.model_validate(session)
    
    async def get_all_sessions(
        self,
        skip: int = 0,
        limit: int = 100,
        tutor_id: Optional[int] = None,
        student_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[SessionResponse]:
        """Get all sessions with filters"""
        sessions = await self.session_repo.get_all(
            skip=skip, limit=limit,
            tutor_id=tutor_id,
            student_id=student_id,
            status=status
        )
        return [SessionResponse.model_validate(s) for s in sessions]
    
    async def create_session(self, session_data: SessionCreate) -> SessionResponse:
        """Create new session - Emits event for notifications"""
        # TODO: Implement time conflict detection
        # TODO: Verify tutor availability
        
        data = session_data.model_dump()
        data['status'] = 'pending'
        session = await self.session_repo.create(data)
        
        # Emit event for async processing (notifications, etc.)
        await event_bus.emit(EventTypes.SESSION_CREATED, {
            "session_id": session.id,
            "tutor_id": session.tutor_id,
            "student_id": session.student_id,
            "subject": session.subject,
            "start_time": session.start_time.isoformat()
        })
        
        return SessionResponse.model_validate(session)
    
    async def update_session(
        self,
        session_id: int,
        session_data: SessionUpdate
    ) -> SessionResponse:
        """Update session"""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        update_data = session_data.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        updated = await self.session_repo.update(session_id, update_data)
        return SessionResponse.model_validate(updated)
    
    async def complete_session(self, session_id: int) -> dict:
        """Mark session as completed - Emits event for feedback request"""
        # TODO: Implement completion logic
        
        # Emit event for async processing
        await event_bus.emit(EventTypes.SESSION_COMPLETED, {
            "session_id": session_id
        })
        
        return {"message": "Complete session - Not implemented"}
    
    async def upload_material(self, session_id: int, material_data: dict) -> dict:
        """Upload session material - PLACEHOLDER"""
        # TODO: Implement material upload
        return {"message": "Upload material - Not implemented"}

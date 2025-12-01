"""
Session Service - Business Logic Layer
Now with event emission for async side effects
"""
from fastapi import HTTPException, status, UploadFile
from typing import List, Optional
from datetime import datetime

from app.repositories.session_repository import SessionRepository
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.schemas.session_participant import SessionJoinRequest, SessionParticipantResponse
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
        return self._to_response(session)
    
    def _to_response(self, session) -> SessionResponse:
        """Convert session model to response DTO"""
        from datetime import datetime, time as time_type
        
        # Combine scheduled_date with start_time and end_time for better frontend display
        start_datetime = None
        end_datetime = None
        
        if session.scheduled_date and session.start_time:
            if isinstance(session.start_time, time_type):
                start_datetime = datetime.combine(session.scheduled_date, session.start_time)
            else:
                start_datetime = session.start_time
                
        if session.scheduled_date and session.end_time:
            if isinstance(session.end_time, time_type):
                end_datetime = datetime.combine(session.scheduled_date, session.end_time)
            else:
                end_datetime = session.end_time
        
        # Build dict manually to avoid validation errors
        data = {
            'session_id': session.session_id,
            'tutor_id': session.tutor_id,
            'coordinator_id': session.coordinator_id,
            'title': session.title,
            'description': session.description,
            'subject_id': session.subject_id,
            'scheduled_date': session.scheduled_date,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'duration': session.duration,
            'location_type': session.location_type or 'online',
            'meeting_link': session.meeting_link,
            'physical_address': session.physical_address,
            'max_students': session.max_students,
            'status': session.status,
            'actual_start': session.actual_start or start_datetime,  # Use combined datetime if actual_start is None
            'actual_end': session.actual_end or end_datetime,  # Use combined datetime if actual_end is None
            'session_notes': session.session_notes,
            'materials': [],  # Don't access materials relationship
            'created_at': session.created_at,
            'updated_at': session.updated_at,
            'students': [],
            'tutor': None
        }
        
        # Add tutor info from relationship
        try:
            if session.tutor and session.tutor.user:
                data['tutor'] = {
                    'user_id': session.tutor.user.user_id,
                    'tutor_id': session.tutor.tutor_id,
                    'email': session.tutor.user.email,
                    'full_name': session.tutor.user.full_name,
                    'specialization': session.tutor.bio
                }
        except:
            pass
        
        # Add student info from participants
        students = []
        try:
            for participant in session.participants:
                if participant.role == 'student' and participant.user:
                    # Need to get student record from user
                    # For now, just use participant data
                    students.append({
                        'user_id': participant.user.user_id,
                        'student_id': 0,  # TODO: Get from user.student relationship
                        'email': participant.user.email,
                        'full_name': participant.user.full_name,
                        'status': participant.status
                    })
            data['students'] = students
        except:
            pass
        
        return SessionResponse(**data)
    
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
        # Convert each session - relationships already eager loaded
        result = []
        for s in sessions:
            result.append(self._to_response(s))
        return result
    
    async def create_session(self, session_data: SessionCreate) -> SessionResponse:
        """Create new session - Emits event for notifications"""
        # TODO: Implement time conflict detection
        # TODO: Verify tutor availability
        
        data = session_data.model_dump()
        # Use status from request, or default to 'draft' if not provided
        if 'status' not in data or data['status'] is None:
            data['status'] = 'draft'
        
        # Remove student_ids - handle separately if needed
        student_ids = data.pop('student_ids', [])
        coordinator_id = data.pop('coordinator_id', None)
        
        session = await self.session_repo.create(data)
        
        # Emit event for async processing (notifications, etc.)
        await event_bus.emit(EventTypes.SESSION_CREATED, {
            "session_id": session.session_id,
            "tutor_id": session.tutor_id
        })
        
        return self._to_response(session)
    
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
        return self._to_response(updated)
    
    async def complete_session(self, session_id: int) -> dict:
        """Mark session as completed - Emits event for feedback request"""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Validate status transition (confirmed or ongoing can be completed)
        if session.status not in ['confirmed', 'ongoing']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete session with status '{session.status}'"
            )
        
        # Update to completed
        update_data = {
            'status': 'completed',
            'updated_at': datetime.utcnow()
        }
        
        await self.session_repo.update(session_id, update_data)
        
        # Emit event for async processing (feedback notifications)
        await event_bus.emit(EventTypes.SESSION_COMPLETED, {
            "session_id": session_id,
            "tutor_id": session.tutor_id,
            "student_id": session.student_id
        })
        
        return {
            "message": "Session marked as completed",
            "session_id": session_id,
            "status": "completed"
        }
    
    async def publish_session(self, session_id: int, tutor_user_id: int) -> dict:
        """Publish session - makes it visible for students to join"""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Verify tutor
        if session.tutor.user_id != tutor_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the session tutor can publish it"
            )
        
        # Check status - can only publish draft sessions
        if session.status != 'draft':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot publish session with status '{session.status}'. Must be draft."
            )
        
        # Update to published
        await self.session_repo.update(session_id, {
            'status': 'published',
            'updated_at': datetime.utcnow()
        })
        
        return {
            "message": "Session published successfully",
            "session_id": session_id,
            "status": "published"
        }
    
    async def upload_material(
        self, 
        session_id: int, 
        file: UploadFile,
        uploaded_by: int,
        description: Optional[str] = None
    ) -> dict:
        """Upload session material - Supports PDF, images, text, Word, Excel files"""
        from fastapi import UploadFile
        import os
        import shutil
        from pathlib import Path
        
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Validate file type
        allowed_types = {
            'application/pdf': 'pdf',
            'image/jpeg': 'image',
            'image/png': 'image',
            'image/gif': 'image',
            'text/plain': 'text',
            'application/msword': 'document',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document',
            'application/vnd.ms-excel': 'spreadsheet',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'spreadsheet'
        }
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not supported. Allowed: PDF, images (JPEG/PNG/GIF), text, Word, Excel"
            )
        
        # Create upload directory
        upload_dir = Path("uploads/session_materials")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"session_{session_id}_{datetime.utcnow().timestamp()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file to disk
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(file_path)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Create SessionMaterial record
        from app.models.database import SessionMaterial
        
        material = SessionMaterial(
            session_id=session_id,
            uploaded_by=uploaded_by,
            file_name=file.filename,
            file_url=str(file_path),  # In production: replace with S3/Azure Blob URL
            file_type=allowed_types[file.content_type],
            file_size=file_size,
            description=description,
            uploaded_at=datetime.utcnow()
        )
        
        self.session_repo.db.add(material)
        await self.session_repo.db.commit()
        await self.session_repo.db.refresh(material)
        
        return {
            "message": "Material uploaded successfully",
            "material_id": material.material_id,
            "session_id": session_id,
            "file_name": file.filename,
            "file_type": material.file_type,
            "file_size": file_size
        }
    
    async def save_material_metadata(
        self,
        session_id: int,
        file_url: str,
        file_name: str,
        file_type: str,
        uploaded_by: int,
        description: Optional[str] = None
    ) -> dict:
        """Save material metadata without uploading file (for external URLs)"""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Create SessionMaterial record with external URL
        from app.models.database import SessionMaterial
        
        material = SessionMaterial(
            session_id=session_id,
            uploaded_by=uploaded_by,
            file_name=file_name,
            file_url=file_url,
            file_type=file_type,
            file_size=None,  # Unknown for external URLs
            description=description,
            uploaded_at=datetime.utcnow()
        )
        
        self.session_repo.db.add(material)
        await self.session_repo.db.commit()
        await self.session_repo.db.refresh(material)
        
        return {
            "message": "Material metadata saved successfully",
            "material_id": material.material_id,
            "session_id": session_id,
            "file_name": file_name,
            "file_type": file_type,
            "file_url": file_url
        }
    
    # ============================================================================
    # SESSION PARTICIPANT MANAGEMENT
    # ============================================================================
    
    async def join_session(
        self, 
        session_id: int, 
        user_id: int,
        join_request: SessionJoinRequest
    ) -> SessionParticipantResponse:
        """Student joins a session - creates pending participant"""
        from app.models.database import SessionParticipant
        from sqlalchemy import select, and_
        
        # Get session
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Check session status - only published or pending_assignment sessions can be joined
        if session.status not in ['published', 'pending_assignment']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot join session with status '{session.status}'. Session must be published."
            )
        
        # Check if already participant
        result = await self.session_repo.db.execute(
            select(SessionParticipant).where(
                and_(
                    SessionParticipant.session_id == session_id,
                    SessionParticipant.user_id == user_id
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a participant in this session"
            )
        
        # Check max students
        result = await self.session_repo.db.execute(
            select(SessionParticipant).where(
                and_(
                    SessionParticipant.session_id == session_id,
                    SessionParticipant.role == 'student',
                    SessionParticipant.status == 'confirmed'
                )
            )
        )
        confirmed_students = len(result.scalars().all())
        if confirmed_students >= session.max_students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Session is full ({session.max_students} students max)"
            )
        
        # Create participant (pending by default)
        participant = SessionParticipant(
            session_id=session_id,
            user_id=user_id,
            role='student',
            status='pending',
            notes=join_request.notes,
            joined_at=datetime.utcnow()
        )
        
        self.session_repo.db.add(participant)
        await self.session_repo.db.commit()
        await self.session_repo.db.refresh(participant, ['user'])
        
        # Emit event for tutor notification
        await event_bus.emit(EventTypes.SESSION_COMPLETED, {  # TODO: Create SESSION_JOIN_REQUEST event
            "session_id": session_id,
            "student_user_id": user_id,
            "tutor_id": session.tutor_id
        })
        
        return SessionParticipantResponse(
            participant_id=participant.participant_id,
            session_id=participant.session_id,
            user_id=participant.user_id,
            role=participant.role,
            status=participant.status,
            joined_at=participant.joined_at,
            notes=participant.notes,
            email=participant.user.email,
            full_name=participant.user.full_name
        )
    
    async def update_participant_status(
        self,
        session_id: int,
        participant_id: int,
        new_status: str,
        tutor_user_id: int,
        notes: Optional[str] = None
    ) -> dict:
        """Tutor accepts/rejects a student join request"""
        from app.models.database import SessionParticipant
        from sqlalchemy import select
        
        # Get session and verify tutor
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Verify current user is the tutor
        if session.tutor.user_id != tutor_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the session tutor can accept/reject participants"
            )
        
        # Get participant
        result = await self.session_repo.db.execute(
            select(SessionParticipant).where(
                SessionParticipant.participant_id == participant_id
            )
        )
        participant = result.scalar_one_or_none()
        
        if not participant or participant.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participant not found in this session"
            )
        
        # Update status
        participant.status = new_status
        if notes:
            participant.notes = notes
        
        await self.session_repo.db.commit()
        
        return {
            "message": f"Participant {new_status}",
            "participant_id": participant_id,
            "status": new_status
        }
    
    async def leave_session(self, session_id: int, user_id: int) -> dict:
        """Student leaves a session"""
        from app.models.database import SessionParticipant
        from sqlalchemy import select, and_
        
        # Get participant
        result = await self.session_repo.db.execute(
            select(SessionParticipant).where(
                and_(
                    SessionParticipant.session_id == session_id,
                    SessionParticipant.user_id == user_id,
                    SessionParticipant.role == 'student'
                )
            )
        )
        participant = result.scalar_one_or_none()
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You are not a participant in this session"
            )
        
        # Delete participant
        await self.session_repo.db.delete(participant)
        await self.session_repo.db.commit()
        
        return {
            "message": "Successfully left the session",
            "session_id": session_id
        }
    
    async def get_session_participants(self, session_id: int) -> List[SessionParticipantResponse]:
        """Get all participants of a session"""
        from app.models.database import SessionParticipant
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.session_repo.db.execute(
            select(SessionParticipant)
            .options(selectinload(SessionParticipant.user))
            .where(SessionParticipant.session_id == session_id)
        )
        participants = result.scalars().all()
        
        return [
            SessionParticipantResponse(
                participant_id=p.participant_id,
                session_id=p.session_id,
                user_id=p.user_id,
                role=p.role,
                status=p.status,
                joined_at=p.joined_at,
                notes=p.notes,
                email=p.user.email,
                full_name=p.user.full_name
            )
            for p in participants
        ]


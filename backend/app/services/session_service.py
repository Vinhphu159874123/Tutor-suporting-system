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
from app.core.locks import distributed_lock, LockAcquisitionError


class SessionService:
    """Business logic for session operations"""
    
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo
    
    # ── Authorization helpers ────────────────────────────────────────────
    @staticmethod
    def _get_roles(user) -> list:
        """Get user roles as list"""
        return user.role if isinstance(user.role, list) else [user.role]
    
    def _is_privileged(self, user) -> bool:
        """Check if user is admin or coordinator"""
        roles = self._get_roles(user)
        return any(r in roles for r in ['admin', 'coordinator'])
    
    async def _assert_session_owner_or_privileged(self, session, user):
        """
        Verify that user is the tutor who owns this session, or is admin/coordinator.
        Raises 403 if not authorized.
        """
        if self._is_privileged(user):
            return
        # Check if user is the tutor who owns this session
        tutor_id = await self.get_tutor_id_for_user(user.user_id)
        if tutor_id and session.tutor_id == tutor_id:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này trên buổi học này"
        )
    
    async def _is_session_participant(self, session_id: int, user_id: int) -> bool:
        """Check if user is a participant of this session"""
        participants = await self.session_repo.get_session_participants(session_id)
        return any(p.user_id == user_id for p in participants)
    
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
        
        # Get materials from SessionMaterial table (uploaded files)
        material_files = []
        try:
            if hasattr(session, 'session_materials') and session.session_materials:
                material_files = [mat.file_name for mat in session.session_materials]
        except:
            pass
        
        # Merge with old JSONB materials (fallback for legacy data)
        jsonb_materials = session.materials or []
        all_materials = list(set(material_files + jsonb_materials))  # Deduplicate
        
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
            'materials': all_materials,  # Merged materials from SessionMaterial table + JSONB
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
        
        # Add subject info from relationship
        try:
            if session.subject:
                data['subject_name'] = session.subject.subject_name
                data['subject_code'] = session.subject.subject_code
        except:
            pass
        
        return SessionResponse(**data)
    
    async def get_all_sessions(
        self,
        skip: int = 0,
        limit: int = 100,
        tutor_id: Optional[int] = None,
        student_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[SessionResponse]:
        """Get all sessions with filters (cached for 15s)"""
        from app.core.cache import get_or_load

        cache_key = f"sessions:list:{skip}:{limit}:{tutor_id}:{student_id}:{subject_id}:{status}"

        async def _load():
            sessions = await self.session_repo.get_all(
                skip=skip, limit=limit,
                tutor_id=tutor_id,
                student_id=student_id,
                subject_id=subject_id,
                status=status
            )
            return [self._to_response(s).dict() for s in sessions]

        data = await get_or_load(cache_key, _load, ttl=15)
        return [SessionResponse(**d) for d in data]
    
    async def create_session(self, session_data: SessionCreate, current_user=None) -> SessionResponse:
        """Create new session - Emits event for notifications"""
        # Authorization: only tutor or privileged users can create sessions
        if current_user:
            roles = self._get_roles(current_user)
            if not any(r in roles for r in ['tutor', 'admin', 'coordinator']):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Chỉ tutor hoặc coordinator mới có thể tạo buổi học"
                )
        
        data = session_data.model_dump()
        # Use status from request, or default to 'draft' if not provided
        if 'status' not in data or data['status'] is None:
            data['status'] = 'draft'
        
        # Pop student_ids — not a column on Session table, handle separately
        student_ids = data.pop('student_ids', [])
        # coordinator_id IS a column on Session table — keep it in data
        
        session = await self.session_repo.create(data)
        
        # Add students as participants if provided
        if student_ids:
            from app.models.database import SessionParticipant
            for uid in student_ids:
                self.session_repo.add(SessionParticipant(
                    session_id=session.session_id,
                    user_id=uid,
                    role='student',
                    status='confirmed'
                ))
            await self.session_repo.commit()
        
        # Emit event for async processing (notifications, etc.)
        await event_bus.emit(EventTypes.SESSION_CREATED, {
            "session_id": session.session_id,
            "tutor_id": session.tutor_id
        })
        
        return self._to_response(session)
    
    async def update_session(
        self,
        session_id: int,
        session_data: SessionUpdate,
        current_user=None
    ) -> SessionResponse:
        """Update session — only owner tutor or privileged users"""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Authorization check
        if current_user:
            await self._assert_session_owner_or_privileged(session, current_user)
        
        update_data = session_data.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        updated = await self.session_repo.update(session_id, update_data)
        return self._to_response(updated)
    
    async def complete_session(self, session_id: int, current_user=None) -> dict:
        """Mark session as completed — only owner tutor or privileged users"""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Authorization check
        if current_user:
            await self._assert_session_owner_or_privileged(session, current_user)
        
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
        """Upload session material - Store file in Supabase Storage"""
        from fastapi import UploadFile
        from app.models.database import SessionMaterial
        from app.core.supabase_storage import get_storage_client
        
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
        
        # Check file size BEFORE reading entire file into memory (prevent DoS)
        MAX_SIZE = 50 * 1024 * 1024  # 50MB
        CHUNK_SIZE = 64 * 1024       # 64KB chunks
        
        chunks = []
        total_size = 0
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size is 50MB"
                )
            chunks.append(chunk)
        
        file_data = b''.join(chunks)
        file_size = total_size
        
        # Upload to Supabase Storage
        try:
            storage_client = get_storage_client()
            file_url = await storage_client.upload_file(
                file_data=file_data,
                filename=file.filename,
                session_id=session_id,
                content_type=file.content_type
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to storage: {str(e)}"
            )
        
        # Create SessionMaterial record with file URL (no binary data)
        material = SessionMaterial(
            session_id=session_id,
            uploaded_by=uploaded_by,
            file_name=file.filename,
            file_url=file_url,  # Supabase Storage URL
            file_data=None,  # No longer store binary in database
            file_type=allowed_types[file.content_type],
            file_size=file_size,
            description=description,
            uploaded_at=datetime.utcnow()
        )
        
        await self.session_repo.add_material(material)
        
        return {
            "message": "Material uploaded successfully to Supabase Storage",
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
            file_url=file_url.replace('\\', '/'),  # Normalize path separators
            file_type=file_type,
            file_size=0,  # External file, size unknown
            description=description,
            uploaded_at=datetime.utcnow()
        )
        
        await self.session_repo.add_material(material)
        
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
        """
        Student joins a session - creates pending participant.

        Race condition protection:
            Dùng Redis distributed lock trên key "session:<id>:enroll" để đảm bảo
            chỉ 1 request được check + insert participant cùng lúc.
            Nếu 2 student cùng join slot cuối, request thứ 2 sẽ thấy session full
            sau khi acquire lock và nhận HTTP 400.
        """
        from app.models.database import SessionParticipant
        from sqlalchemy import select, and_
        
        # Get session — đọc trước lock để giảm thời gian giữ lock
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
        
        try:
            # ─── CRITICAL SECTION ───────────────────────────────────────────
            # Lock theo session_id: chỉ 1 request enroll vào session này cùng lúc
            async with distributed_lock(
                resource=f"session:{session_id}:enroll",
                ttl_ms=5_000,      # 5s — đủ cho check + insert + commit
                timeout_s=3.0,     # chờ tối đa 3s trước khi báo lỗi
            ):
                # Kiểm tra lại session sau khi giữ lock (state có thể đã thay đổi)
                session = await self.session_repo.get_by_id(session_id)

                # Check if already participant
                existing = await self.session_repo.get_participant(session_id, user_id)
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="You are already a participant in this session"
                    )
                
                # Check max students — đọc lại count sau khi lock để tránh TOCTOU
                confirmed_students = await self.session_repo.get_confirmed_student_count(session_id)
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
                
                self.session_repo.add(participant)
                await self.session_repo.commit()
                await self.session_repo.refresh(participant, ['user'])
            # ─── END CRITICAL SECTION ────────────────────────────────────────

        except LockAcquisitionError as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e)
            )
        
        # Emit event for tutor notification (ngoài lock — không cần bảo vệ)
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
        """
        Tutor accepts/rejects a student join request.

        Race condition protection:
            Khi tutor accept participant vào session, cần kiểm tra lại max_students
            vì có thể có nhiều pending participant và tutor đang accept đồng thời
            từ nhiều tab/request. Lock đảm bảo chỉ 1 accept được xử lý cùng lúc.
        """
        from app.models.database import SessionParticipant
        from sqlalchemy import select, and_
        
        # Get session and verify tutor — trước lock để fail-fast
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
        
        try:
            # ─── CRITICAL SECTION ───────────────────────────────────────────
            # Lock khi accept để tránh over-accept vượt max_students
            # (reject không cần lock vì không tăng count)
            lock_resource = f"session:{session_id}:enroll"  # dùng cùng key với join_session
            async with distributed_lock(resource=lock_resource, ttl_ms=5_000, timeout_s=3.0):
                # Get participant
                participant = await self.session_repo.get_participant_by_id(participant_id)
                
                if not participant or participant.session_id != session_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Participant not found in this session"
                    )
                
                # Nếu accept, kiểm tra lại capacity trước khi confirm
                if new_status == 'confirmed':
                    confirmed_count = await self.session_repo.get_confirmed_student_count(session_id)
                    if confirmed_count >= session.max_students:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Cannot confirm: session already at max capacity ({session.max_students} students)"
                        )
                
                # Update status
                participant.status = new_status
                if notes:
                    participant.notes = notes
                
                await self.session_repo.commit()
            # ─── END CRITICAL SECTION ────────────────────────────────────────

        except LockAcquisitionError as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e)
            )
        
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
        participant = await self.session_repo.get_participant(session_id, user_id, role='student')
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You are not a participant in this session"
            )
        
        # Delete participant
        await self.session_repo.delete_participant(participant)
        
        return {
            "message": "Successfully left the session",
            "session_id": session_id
        }
    
    async def get_session_participants(self, session_id: int, current_user=None) -> List[SessionParticipantResponse]:
        """Get all participants of a session — only related users"""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Authorization: only session owner, participants, or privileged users
        if current_user:
            if not self._is_privileged(current_user):
                tutor_id = await self.get_tutor_id_for_user(current_user.user_id)
                is_owner = tutor_id and session.tutor_id == tutor_id
                is_participant = await self._is_session_participant(session_id, current_user.user_id)
                if not is_owner and not is_participant:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Bạn không có quyền xem danh sách thành viên của buổi học này"
                    )
        
        participants = await self.session_repo.get_session_participants(session_id)
        
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

    # ==================================================================
    # Phase 2: Methods extracted from sessions controller
    # ==================================================================

    async def get_tutor_id_for_user(self, user_id: int) -> Optional[int]:
        """Get tutor_id for a given user_id"""
        return await self.session_repo.get_tutor_id_for_user(user_id)

    async def ensure_profile(self, user, mode: Optional[str] = None):
        """Auto-create Student/Tutor profile if missing"""
        roles = user.role if isinstance(user.role, list) else [user.role]
        if mode == 'student' or 'student' in roles:
            await self.session_repo.ensure_student_profile(user)
        if mode == 'tutor' or 'tutor' in roles:
            await self.session_repo.ensure_tutor_profile(user)

    async def get_dashboard_sessions(self, user, mode: Optional[str] = None) -> dict:
        """OPTIMIZED + CACHED: Recent and upcoming sessions for dashboard"""
        from datetime import date
        from app.core.cache import get_or_load

        active_role = mode or user.role

        async def _load():
            today = date.today()

            def to_dict(s):
                return {"session_id": s.session_id, "tutor_id": s.tutor_id,
                        "subject_id": s.subject_id, "title": s.title, "description": s.description,
                        "scheduled_date": s.scheduled_date.isoformat() if s.scheduled_date else None,
                        "start_time": str(s.start_time) if s.start_time else None,
                        "end_time": str(s.end_time) if s.end_time else None,
                        "duration": s.duration, "location_type": s.location_type,
                        "meeting_link": s.meeting_link, "physical_address": s.physical_address,
                        "status": s.status, "max_students": s.max_students,
                        "tutor": {"tutor_id": s.tutor.tutor_id, "user_id": s.tutor.user_id,
                                  "email": s.tutor.user.email if s.tutor and s.tutor.user else None,
                                  "full_name": s.tutor.user.full_name if s.tutor and s.tutor.user else None} if s.tutor else None}

            if active_role == 'student':
                recent = await self.session_repo.get_dashboard_recent_student(user.user_id)
                upcoming = await self.session_repo.get_dashboard_upcoming_student(user.user_id, today)
            elif active_role == 'tutor':
                tid = await self.session_repo.get_tutor_id_for_user(user.user_id)
                if not tid:
                    return {"recent": [], "upcoming": []}
                recent = await self.session_repo.get_dashboard_recent_tutor(tid)
                upcoming = await self.session_repo.get_dashboard_upcoming_tutor(tid, today)
            else:
                return {"recent": [], "upcoming": []}

            return {"recent": [to_dict(s) for s in recent],
                    "upcoming": [to_dict(s) for s in upcoming]}

        cache_key = f"sessions:dashboard:{user.user_id}:{active_role}"
        return await get_or_load(cache_key, _load, ttl=10)

    async def get_bulk_materials(self, session_ids: list) -> dict:
        from app.core.cache import get_or_load

        async def _load():
            mats = await self.session_repo.get_materials_by_session_ids(session_ids)
            m_map: dict = {}
            for m in mats:
                m_map.setdefault(m.session_id, []).append({
                    "material_id": m.material_id, "file_name": m.file_name,
                    "file_type": m.file_type, "file_size": m.file_size,
                    "description": m.description, "uploaded_at": m.uploaded_at,
                    "uploaded_by": m.uploaded_by})
            return {sid: m_map.get(sid, []) for sid in session_ids}

        cache_key = f"materials:bulk:{','.join(map(str, sorted(session_ids)))}"
        return await get_or_load(cache_key, _load, ttl=30)

    async def get_session_materials_list(self, session_id: int) -> dict:
        mats = await self.session_repo.get_materials_by_session(session_id)
        return {"data": [{"material_id": m.material_id, "file_name": m.file_name,
                          "file_type": m.file_type, "file_size": m.file_size,
                          "description": m.description, "uploaded_at": m.uploaded_at,
                          "uploaded_by": m.uploaded_by} for m in mats]}

    async def delete_material_by_identifier(self, session_id: int, identifier: str) -> dict:
        from pathlib import Path
        import os
        try:
            mid = int(identifier)
            mat = await self.session_repo.get_material_by_id(mid, session_id)
        except ValueError:
            mat = await self.session_repo.get_material_by_name(identifier, session_id)
        if not mat:
            raise HTTPException(status_code=404, detail=f"Material '{identifier}' not found")
        if mat.file_url:
            fp = Path(mat.file_url.replace('\\', '/'))
            if fp.exists():
                try: os.remove(fp)
                except: pass
        await self.session_repo.delete_material(mat)
        return {"message": "Material deleted successfully", "file_name": mat.file_name}

    async def download_material_by_identifier(self, session_id: int, identifier: str, current_user=None):
        """Download material — only participants, session owner, or privileged users"""
        # Authorization check
        if current_user:
            session = await self.session_repo.get_by_id(session_id)
            if session and not self._is_privileged(current_user):
                tutor_id = await self.get_tutor_id_for_user(current_user.user_id)
                is_owner = tutor_id and session.tutor_id == tutor_id
                is_participant = await self._is_session_participant(session_id, current_user.user_id)
                if not is_owner and not is_participant:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Bạn không có quyền tải tài liệu của buổi học này"
                    )
        
        try:
            mid = int(identifier)
            mat = await self.session_repo.get_material_by_id(mid, session_id)
        except ValueError:
            mat = await self.session_repo.get_material_by_name(identifier, session_id)
        if not mat:
            raise HTTPException(status_code=404, detail=f"Material '{identifier}' not found")
        return mat

    async def remove_student_from_subject(self, current_user, subject_id: int,
                                           student_id: int, tutor_id: int) -> dict:
        from app.models.database import Notifications
        from datetime import datetime, timezone, timedelta
        tutor = await self.session_repo.get_tutor_by_user_id(current_user.user_id)
        if not tutor or tutor.tutor_id != tutor_id:
            raise HTTPException(status_code=403, detail="Only the tutor can remove students")
        sids = await self.session_repo.get_session_ids_for_subject_tutor(subject_id, tutor_id)
        if not sids:
            raise HTTPException(status_code=404, detail="No sessions found")
        student = await self.session_repo.get_user_by_id(student_id)
        subject = await self.session_repo.get_subject_by_id(subject_id)
        cnt = await self.session_repo.delete_participants_bulk(sids, student_id)
        await self.session_repo.commit()
        if cnt > 0 and student and subject:
            vn = timezone(timedelta(hours=7))
            self.session_repo.add(Notifications(user_id=student_id, type="removed_from_course",
                                 title="Bạn đã bị xóa khỏi khóa học",
                                 message=f"Giáo viên đã xóa bạn khỏi khóa học {subject.subject_name} ({subject.subject_code}). Bạn đã bị xóa khỏi {cnt} phiên học.",
                                 related_entity_type="subject", related_entity_id=subject_id,
                                 is_read=False, created_at=datetime.now(vn)))
            await self.session_repo.commit()
        return {"message": f"Student removed from {cnt} sessions", "sessions_affected": cnt,
                "student_id": student_id, "subject_id": subject_id}

    async def bulk_save_sessions(self, user, subject_id: int, sessions_data: list) -> dict:
        from app.models.database import Session as SM
        tutor = await self.session_repo.get_tutor_by_user_id(user.user_id)
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor profile not found")
        created, updated = [], []
        try:
            for sd in sessions_data:
                try:
                    sdate = datetime.fromisoformat(sd['date']).date()
                    ts = sd['time_slots']
                    if ts and len(ts) > 0:
                        parts = ts[0].split('-')
                        try: st = datetime.strptime(parts[0].strip(), "%H:%M:%S").time()
                        except: st = datetime.strptime(parts[0].strip(), "%H:%M").time()
                        try: et = datetime.strptime(parts[1].strip(), "%H:%M:%S").time()
                        except: et = datetime.strptime(parts[1].strip(), "%H:%M").time()
                    else:
                        st = datetime.strptime("07:00", "%H:%M").time()
                        et = datetime.strptime("09:00", "%H:%M").time()
                    sid = sd.get('session_id')
                    if sid:
                        ex = await self.session_repo.get_session_by_tutor_and_id(sid, tutor.tutor_id)
                        if ex:
                            ex.description = sd.get('description', ''); ex.scheduled_date = sdate
                            ex.start_time = st; ex.end_time = et
                            ex.location_type = 'online' if sd.get('location') == 'Online' else 'physical'
                            ex.meeting_link = sd.get('meeting_link', '')
                            ex.physical_address = sd.get('location', '') if sd.get('location') != 'Online' else None
                            ex.materials = sd.get('materials', []); ex.updated_at = datetime.utcnow()
                            updated.append(ex); continue
                        sid = None
                    if not sid:
                        dup = await self.session_repo.get_session_by_tutor_subject_date(
                            tutor.tutor_id, subject_id, sdate, st, et)
                        if dup:
                            dup.description = sd.get('description', '')
                            dup.location_type = 'online' if sd.get('location') == 'Online' else 'physical'
                            dup.meeting_link = sd.get('meeting_link', '')
                            dup.physical_address = sd.get('location', '') if sd.get('location') != 'Online' else None
                            dup.materials = sd.get('materials', []); dup.updated_at = datetime.utcnow()
                            updated.append(dup)
                        else:
                            ns = SM(tutor_id=tutor.tutor_id, subject_id=subject_id,
                                    title=f"Session {sd['session_number']}",
                                    description=sd.get('description', ''), scheduled_date=sdate,
                                    start_time=st, end_time=et,
                                    location_type='online' if sd.get('location') == 'Online' else 'physical',
                                    meeting_link=sd.get('meeting_link', ''),
                                    physical_address=sd.get('location', '') if sd.get('location') != 'Online' else None,
                                    materials=sd.get('materials', []), status='draft')
                            self.session_repo.add(ns); created.append(ns)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid session data: {e}")
            await self.session_repo.commit()
            return {"message": "Sessions saved successfully", "created_count": len(created), "updated_count": len(updated)}
        except HTTPException:
            await self.session_repo.rollback(); raise
        except Exception as e:
            await self.session_repo.rollback(); raise HTTPException(status_code=500, detail=f"Failed to save sessions: {e}")

    async def submit_feedback(self, session_id: int, user_id: int, rating: int,
                               comment: Optional[str] = None, is_anonymous: bool = False) -> dict:
        from app.models.database import SessionFeedback
        await self.get_session(session_id)
        p = await self.session_repo.get_participant(session_id, user_id, role='student')
        if not p:
            raise HTTPException(status_code=403, detail="You are not enrolled in this session")
        ex = await self.session_repo.get_feedback(session_id, user_id)
        if ex:
            ex.rating = rating; ex.comment = comment; ex.is_anonymous = is_anonymous
            await self.session_repo.commit(); return {"message": "Feedback updated successfully"}
        self.session_repo.add(SessionFeedback(session_id=session_id, reviewer_id=user_id, reviewer_type='student',
                               rating=rating, comment=comment, is_anonymous=is_anonymous, is_public=True))
        await self.session_repo.commit(); return {"message": "Feedback submitted successfully"}

    async def get_feedbacks(self, session_id: int, user_roles: list, user_id: int) -> list:
        fbs = await self.session_repo.get_feedbacks_by_session(session_id, user_roles, user_id)
        return [{"feedback_id": f.feedback_id, "rating": f.rating, "comment": f.comment,
                 "is_anonymous": f.is_anonymous,
                 "reviewer_id": None if f.is_anonymous else f.reviewer_id,
                 "created_at": f.created_at.isoformat() if f.created_at else None} for f in fbs]

    async def get_bulk_feedbacks(self, session_ids: list, user_roles: list, user_id: int) -> dict:
        from app.core.cache import get_or_load

        async def _load():
            fbs = await self.session_repo.get_feedbacks_by_session_ids(session_ids, user_roles, user_id)
            m: dict = {}
            for f in fbs:
                m.setdefault(f.session_id, []).append({
                    "feedback_id": f.feedback_id, "session_id": f.session_id, "rating": f.rating,
                    "comment": f.comment, "is_anonymous": f.is_anonymous,
                    "reviewer_id": None if f.is_anonymous else f.reviewer_id,
                    "created_at": f.created_at.isoformat() if f.created_at else None})
            return m

        sfx = f":{user_id}" if 'student' in user_roles else ""
        ck = f"feedbacks:bulk:{','.join(map(str, sorted(session_ids)))}{sfx}"
        return await get_or_load(ck, _load, ttl=30)

    async def get_subject_feedbacks(self, subject_id: int, user, tutor_id_param: Optional[int]) -> dict:
        roles = user.role if isinstance(user.role, list) else [user.role]
        tid = tutor_id_param
        if 'tutor' in roles and not tid:
            t = await self.session_repo.get_tutor_by_user_id(user.user_id)
            if t: tid = t.tutor_id
        data = await self.session_repo.get_subject_feedbacks(subject_id, tid)
        if not data:
            return {"average_rating": 0, "total_feedbacks": 0, "rating_distribution": {1:0,2:0,3:0,4:0,5:0}, "feedbacks": []}
        ratings = [f.rating for f, _, _ in data]
        dist = {1:0,2:0,3:0,4:0,5:0}
        for r in ratings: dist[r] += 1
        fl = []
        for f, s, u in data:
            item = {"feedback_id": f.feedback_id, "session_id": f.session_id,
                    "session_date": s.scheduled_date.isoformat() if s.scheduled_date else None,
                    "rating": f.rating, "comment": f.comment, "is_anonymous": f.is_anonymous,
                    "created_at": f.created_at.isoformat() if f.created_at else None}
            item["reviewer_name"] = u.full_name if not f.is_anonymous and u else "Ẩn danh"
            item["reviewer_email"] = u.email if not f.is_anonymous and u else None
            fl.append(item)
        return {"average_rating": round(sum(ratings)/len(ratings), 2), "total_feedbacks": len(ratings),
                "rating_distribution": dist, "feedbacks": fl}

    async def get_attendance_participants(self, session_id: int) -> list:
        data = await self.session_repo.get_attendance_data(session_id)
        return [{"user_id": u.user_id, "full_name": u.full_name, "email": u.email,
                 "status": p.status, "attended": p.attended,
                 "attendance_status": a.status if a else None,
                 "joined_at": p.joined_at.isoformat() if p.joined_at else None}
                for p, u, s, a in data]

    async def mark_attendance(self, session_id: int, attendance_data: list) -> dict:
        from app.models.database import Attendance
        from datetime import datetime, timezone, timedelta
        await self.get_session(session_id)
        vn = timezone(timedelta(hours=7)); now = datetime.now(vn)
        updated = 0
        for rec in attendance_data:
            uid = rec.get('user_id')
            st = 'present' if rec.get('is_present') else ('late' if rec.get('is_late') else ('excused' if rec.get('is_excused') else 'absent'))
            p = await self.session_repo.get_participant(session_id, uid, role='student')
            if not p: continue
            stu = await self.session_repo.get_student_by_user_id(uid)
            if not stu: continue
            ex = await self.session_repo.get_attendance(session_id, stu.student_id)
            if ex:
                ex.status = st; ex.check_in_time = now
            else:
                self.session_repo.add(Attendance(session_id=session_id, student_id=stu.student_id, status=st,
                                  check_in_time=now if st in ['present', 'late'] else None))
            p.attended = st in ['present', 'late']; updated += 1
        await self.session_repo.commit()
        return {"message": f"Attendance marked for {updated} students", "updated_count": updated, "skipped_count": 0}



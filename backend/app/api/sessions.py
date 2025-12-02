from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from typing import List, Optional
import os
from pathlib import Path
from sqlalchemy import and_

from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.schemas.session_participant import (
    SessionJoinRequest, 
    SessionParticipantResponse, 
    SessionParticipantUpdate
)
from app.services.session_service import SessionService
from app.core.dependencies import get_session_service, get_current_user
from app.models.database import User

router = APIRouter()

# ============================================================================
# SESSION ENDPOINTS - Migrated to Layered Architecture
# ============================================================================

@router.get("/", response_model=List[SessionResponse])
async def get_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    tutor_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    session_service: SessionService = Depends(get_session_service)
):
    """Get all sessions with filters"""
    return await session_service.get_all_sessions(
        skip=skip, limit=limit,
        tutor_id=tutor_id,
        student_id=student_id,
        subject_id=subject_id,
        status=status
    )

@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    session_data: SessionCreate,
    session_service: SessionService = Depends(get_session_service)
):
    """Create new session - PLACEHOLDER for conflict detection"""
    return await session_service.create_session(session_data)

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    session_service: SessionService = Depends(get_session_service)
):
    """Get session by ID"""
    return await session_service.get_session(session_id)

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    session_service: SessionService = Depends(get_session_service)
):
    """Update session"""
    return await session_service.update_session(session_id, session_data)


# ============================================================================
# SESSION ACTION ENDPOINTS
# ============================================================================

@router.post("/{session_id}/complete")
async def complete_session(
    session_id: int,
    session_service: SessionService = Depends(get_session_service)
):
    """Mark session as completed"""
    return await session_service.complete_session(session_id)


@router.post("/{session_id}/publish")
async def publish_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Publish session (tutor makes it visible for students to join)"""
    return await session_service.publish_session(session_id, current_user.user_id)


@router.post("/{session_id}/materials")
async def upload_materials(
    session_id: int,
    file: Optional[UploadFile] = File(None),
    file_url: Optional[str] = Form(None),
    file_name: Optional[str] = Form(None),
    file_type: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    uploaded_by: int = Form(...),
    session_service: SessionService = Depends(get_session_service)
):
    """Upload learning materials (PDF, images, documents) for a session
    
    Can upload actual file OR provide external URL
    """
    if file:
        # Upload actual file
        return await session_service.upload_material(session_id, file, uploaded_by, description)
    elif file_url and file_name:
        # Just save metadata (external file URL)
        return await session_service.save_material_metadata(
            session_id, file_url, file_name, file_type or "document", uploaded_by, description
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either file upload or file_url + file_name"
        )


@router.get("/{session_id}/materials")
async def get_session_materials(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Get all materials for a session"""
    from app.models.database import SessionMaterial
    from sqlalchemy import select
    
    result = await session_service.session_repo.db.execute(
        select(SessionMaterial).where(SessionMaterial.session_id == session_id)
    )
    materials = result.scalars().all()
    
    return {
        "data": [
            {
                "material_id": m.material_id,
                "file_name": m.file_name,
                "file_type": m.file_type,
                "file_size": m.file_size,
                "description": m.description,
                "uploaded_at": m.uploaded_at,
                "uploaded_by": m.uploaded_by
            }
            for m in materials
        ]
    }


@router.delete("/{session_id}/materials/{material_identifier}")
async def delete_material(
    session_id: int,
    material_identifier: str,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Delete a session material - accepts material_id (int) or filename (str)"""
    from app.models.database import SessionMaterial
    from sqlalchemy import select
    import os
    
    # Only tutors can delete materials
    if current_user.role != 'tutor':
        raise HTTPException(status_code=403, detail="Only tutors can delete materials")
    
    # Try to parse as integer first (material_id)
    try:
        material_id = int(material_identifier)
        result = await session_service.session_repo.db.execute(
            select(SessionMaterial).where(
                SessionMaterial.material_id == material_id,
                SessionMaterial.session_id == session_id
            )
        )
        material = result.scalar_one_or_none()
    except ValueError:
        # If not an integer, search by filename
        result = await session_service.session_repo.db.execute(
            select(SessionMaterial).where(
                SessionMaterial.file_name == material_identifier,
                SessionMaterial.session_id == session_id
            )
        )
        material = result.scalar_one_or_none()
    
    if not material:
        # Fallback: Try to find and delete file in uploads directory (for old materials)
        upload_dir = Path("uploads/session_materials")
        deleted = False
        
        if upload_dir.exists():
            matching_files = list(upload_dir.glob(f"session_{session_id}_*"))
            
            for file_path in matching_files:
                if material_identifier in file_path.name or file_path.name.endswith(material_identifier):
                    try:
                        os.remove(file_path)
                        deleted = True
                        return {
                            "message": "Material deleted from filesystem (no database record)",
                            "file_name": material_identifier
                        }
                    except Exception as e:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Could not delete file: {str(e)}"
                        )
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Material '{material_identifier}' not found in database or filesystem. Upload dir exists: {upload_dir.exists()}"
            )
    
    # Delete file from disk
    file_path = Path(material.file_url)
    if file_path.exists():
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {file_path}: {e}")
    
    # Delete from database
    await session_service.session_repo.db.delete(material)
    await session_service.session_repo.db.commit()
    
    return {"message": "Material deleted successfully", "file_name": material.file_name}


@router.get("/{session_id}/materials/{material_identifier}/download")
async def download_material(
    session_id: int,
    material_identifier: str,
    inline: bool = Query(False, description="Display inline in browser instead of download"),
    session_service: SessionService = Depends(get_session_service)
    # Remove auth requirement for direct browser access
):
    """Download or preview a session material file - accepts material_id (int) or filename (str) - PUBLIC"""
    from app.models.database import SessionMaterial
    from sqlalchemy import select
    
    # Try to parse as integer first (material_id)
    try:
        material_id = int(material_identifier)
        result = await session_service.session_repo.db.execute(
            select(SessionMaterial).where(
                SessionMaterial.material_id == material_id,
                SessionMaterial.session_id == session_id
            )
        )
        material = result.scalar_one_or_none()
    except ValueError:
        # If not an integer, search by filename within this session
        result = await session_service.session_repo.db.execute(
            select(SessionMaterial).where(
                SessionMaterial.session_id == session_id,
                SessionMaterial.file_name == material_identifier
            ).order_by(SessionMaterial.uploaded_at.desc())  # Get latest if multiple
        )
        material = result.scalars().first()  # Get first result instead of scalar_one_or_none
    
    if not material:
        # Fallback: Try to find file in uploads directory (for old materials)
        upload_dir = Path("uploads/session_materials")
        
        # Try to find file with pattern session_{session_id}_*{filename}
        if upload_dir.exists():
            matching_files = list(upload_dir.glob(f"session_{session_id}_*"))
            for file_path in matching_files:
                if material_identifier in file_path.name or file_path.name.endswith(material_identifier):
                    return FileResponse(
                        path=str(file_path),
                        filename=material_identifier,
                        media_type='application/octet-stream'
                    )
        
        raise HTTPException(status_code=404, detail=f"Material '{material_identifier}' not found in database or uploads folder")
    
    # Check if file exists
    file_path = Path(material.file_url)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    # Determine media type and content disposition
    if inline:
        # For inline display (preview in browser)
        media_type = 'application/pdf' if material.file_name.lower().endswith('.pdf') else 'application/octet-stream'
        from fastapi.responses import FileResponse
        response = FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=material.file_name
        )
        # Set Content-Disposition to inline for browser preview
        response.headers["Content-Disposition"] = f'inline; filename="{material.file_name}"'
        return response
    else:
        # For download
        return FileResponse(
            path=str(file_path),
            filename=material.file_name,
            media_type='application/octet-stream'
        )


# ============================================================================
# SESSION PARTICIPANT ENDPOINTS - Student Join/Leave
# ============================================================================

@router.post("/{session_id}/join", response_model=SessionParticipantResponse)
async def join_session(
    session_id: int,
    join_request: SessionJoinRequest,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Student joins a session (creates pending participant)"""
    return await session_service.join_session(session_id, current_user.user_id, join_request)


@router.post("/{session_id}/participants/{participant_id}/accept")
async def accept_participant(
    session_id: int,
    participant_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Tutor accepts a student join request"""
    return await session_service.update_participant_status(
        session_id, participant_id, "confirmed", current_user.user_id
    )


@router.post("/{session_id}/participants/{participant_id}/reject")
async def reject_participant(
    session_id: int,
    participant_id: int,
    update_data: SessionParticipantUpdate,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Tutor rejects a student join request"""
    return await session_service.update_participant_status(
        session_id, participant_id, "cancelled", current_user.user_id, update_data.notes
    )


@router.delete("/{session_id}/leave")
async def leave_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Student leaves a session"""
    return await session_service.leave_session(session_id, current_user.user_id)


@router.delete("/remove-student-from-subject")
async def remove_student_from_subject(
    subject_id: int = Query(..., description="Subject ID"),
    student_id: int = Query(..., description="Student user ID to remove"),
    tutor_id: int = Query(..., description="Tutor user ID"),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Tutor removes a student from all sessions of a specific subject"""
    # Verify current user is a tutor and owns this course
    from app.models.database import Session, SessionParticipant, TutorRegistration
    from sqlalchemy import select, delete
    
    # Check if current user is the tutor who registered this subject
    tutor_reg_result = await session_service.session_repo.db.execute(
        select(TutorRegistration).where(
            TutorRegistration.subject_id == subject_id,
            TutorRegistration.tutor_id == tutor_id
        )
    )
    tutor_registration = tutor_reg_result.scalar_one_or_none()
    
    if not tutor_registration:
        raise HTTPException(
            status_code=404,
            detail="Tutor registration not found for this subject"
        )
    
    # Verify the tutor_id belongs to current user
    from app.models.database import Tutor
    tutor_result = await session_service.session_repo.db.execute(
        select(Tutor).where(Tutor.tutor_id == tutor_id)
    )
    tutor = tutor_result.scalar_one_or_none()
    
    if not tutor or tutor.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the tutor can remove students from their sessions"
        )
    
    # Get all sessions for this subject and tutor
    
    # Get session IDs
    sessions_result = await session_service.session_repo.db.execute(
        select(Session.session_id).where(
            Session.subject_id == subject_id,
            Session.tutor_id == tutor_id
        )
    )
    session_ids = [row[0] for row in sessions_result.fetchall()]
    
    if not session_ids:
        raise HTTPException(
            status_code=404,
            detail="No sessions found for this tutor and subject"
        )
    
    # Get student info and subject info before deletion
    from app.models.database import User, Subject
    student_result = await session_service.session_repo.db.execute(
        select(User).where(User.user_id == student_id)
    )
    student = student_result.scalar_one_or_none()
    
    subject_result = await session_service.session_repo.db.execute(
        select(Subject).where(Subject.subject_id == subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    
    # Delete all participant records for this student in these sessions
    delete_stmt = delete(SessionParticipant).where(
        SessionParticipant.session_id.in_(session_ids),
        SessionParticipant.user_id == student_id,
        SessionParticipant.role == 'student'
    )
    
    result = await session_service.session_repo.db.execute(delete_stmt)
    await session_service.session_repo.db.commit()
    
    removed_count = result.rowcount
    
    # Send notification to student if they were removed
    if removed_count > 0 and student and subject:
        from app.models.database import Notifications
        from datetime import datetime, timezone, timedelta
        
        # Convert to Vietnam timezone (UTC+7)
        vietnam_tz = timezone(timedelta(hours=7))
        vietnam_time = datetime.now(vietnam_tz)
        
        notification = Notifications(
            user_id=student_id,
            type="removed_from_course",
            title="Bạn đã bị xóa khỏi khóa học",
            message=f"Giáo viên đã xóa bạn khỏi khóa học {subject.subject_name} ({subject.subject_code}). Bạn đã bị xóa khỏi {removed_count} phiên học.",
            related_entity_type="subject",
            related_entity_id=subject_id,
            is_read=False,
            created_at=vietnam_time
        )
        
        session_service.session_repo.db.add(notification)
        await session_service.session_repo.db.commit()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"✅ Notification sent to student {student_id} for removal from course {subject_id}")
    
    return {
        "message": f"Student removed from {removed_count} sessions",
        "sessions_affected": removed_count,
        "student_id": student_id,
        "subject_id": subject_id
    }


@router.get("/{session_id}/participants", response_model=List[SessionParticipantResponse])
async def get_session_participants(
    session_id: int,
    session_service: SessionService = Depends(get_session_service)
):
    """Get all participants of a session"""
    return await session_service.get_session_participants(session_id)


@router.post("/bulk-save-for-subject")
async def bulk_save_sessions_for_subject(
    subject_id: int,
    sessions_data: List[dict],
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Bulk create/update sessions for a subject
    Used by tutor to save generated weekly sessions
    """
    from app.models.database import Tutor, Session
    from sqlalchemy import select, delete
    from datetime import datetime, time
    
    # Get tutor ID
    tutor_result = await session_service.session_repo.db.execute(
        select(Tutor).where(Tutor.user_id == current_user.user_id)
    )
    tutor = tutor_result.scalar_one_or_none()
    
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor profile not found")
    
    # Process each session - UPDATE if has session_id, CREATE if not
    created_sessions = []
    updated_sessions = []
    
    try:
        for session_data in sessions_data:
            try:
                # Parse date and time
                session_date = datetime.fromisoformat(session_data['date']).date()
                time_slots = session_data['time_slots']
                
                # Handle time slots format - could be "HH:MM-HH:MM" or "HH:MM:SS-HH:MM:SS"
                if time_slots and len(time_slots) > 0:
                    time_parts = time_slots[0].split('-')
                    start_time_str = time_parts[0].strip()
                    end_time_str = time_parts[1].strip()
                    
                    # Try parsing with seconds first, then without
                    try:
                        start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
                    except ValueError:
                        start_time = datetime.strptime(start_time_str, "%H:%M").time()
                    
                    try:
                        end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
                    except ValueError:
                        end_time = datetime.strptime(end_time_str, "%H:%M").time()
                else:
                    start_time = datetime.strptime("07:00", "%H:%M").time()
                    end_time = datetime.strptime("09:00", "%H:%M").time()
                
                # Check if this is an update (has session_id) or create (no session_id)
                session_id = session_data.get('session_id')
                
                if session_id:
                    # UPDATE existing session
                    result = await session_service.session_repo.db.execute(
                        select(Session).where(
                            Session.session_id == session_id,
                            Session.tutor_id == tutor.tutor_id  # Security check
                        )
                    )
                    existing_session = result.scalar_one_or_none()
                    
                    if existing_session:
                        existing_session.description = session_data.get('description', '')
                        existing_session.scheduled_date = session_date
                        existing_session.start_time = start_time
                        existing_session.end_time = end_time
                        existing_session.location_type = 'online' if session_data.get('location') == 'Online' else 'physical'
                        existing_session.meeting_link = session_data.get('meeting_link', '')
                        existing_session.physical_address = session_data.get('location', '') if session_data.get('location') != 'Online' else None
                        existing_session.materials = session_data.get('materials', [])
                        existing_session.updated_at = datetime.utcnow()
                        updated_sessions.append(existing_session)
                    else:
                        # Session ID provided but not found - create new
                        session_id = None
                
                if not session_id:
                    # Check if session already exists for this date/time/subject/tutor
                    check_result = await session_service.session_repo.db.execute(
                        select(Session).where(
                            Session.tutor_id == tutor.tutor_id,
                            Session.subject_id == subject_id,
                            Session.scheduled_date == session_date,
                            Session.start_time == start_time,
                            Session.end_time == end_time
                        )
                    )
                    existing_duplicate = check_result.scalar_one_or_none()
                    
                    if existing_duplicate:
                        # Update existing session instead of creating duplicate
                        existing_duplicate.description = session_data.get('description', '')
                        existing_duplicate.location_type = 'online' if session_data.get('location') == 'Online' else 'physical'
                        existing_duplicate.meeting_link = session_data.get('meeting_link', '')
                        existing_duplicate.physical_address = session_data.get('location', '') if session_data.get('location') != 'Online' else None
                        existing_duplicate.materials = session_data.get('materials', [])
                        existing_duplicate.updated_at = datetime.utcnow()
                        updated_sessions.append(existing_duplicate)
                    else:
                        # CREATE new session
                        new_session = Session(
                            tutor_id=tutor.tutor_id,
                            subject_id=subject_id,
                            title=f"Session {session_data['session_number']}",
                            description=session_data.get('description', ''),
                            scheduled_date=session_date,
                            start_time=start_time,
                            end_time=end_time,
                            location_type='online' if session_data.get('location') == 'Online' else 'physical',
                            meeting_link=session_data.get('meeting_link', ''),
                            physical_address=session_data.get('location', '') if session_data.get('location') != 'Online' else None,
                            materials=session_data.get('materials', []),
                            status='draft'
                        )
                        
                        session_service.session_repo.db.add(new_session)
                        created_sessions.append(new_session)
                
            except Exception as e:
                print(f"Error processing session {session_data.get('session_number')}: {e}")
                print(f"Session data: {session_data}")
                raise HTTPException(status_code=400, detail=f"Invalid session data: {str(e)}")
        
        await session_service.session_repo.db.commit()
        
        return {
            "message": "Sessions saved successfully", 
            "created_count": len(created_sessions),
            "updated_count": len(updated_sessions)
        }
        
    except HTTPException:
        await session_service.session_repo.db.rollback()
        raise
    except Exception as e:
        await session_service.session_repo.db.rollback()
        print(f"Error saving sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save sessions: {str(e)}")


# ============================================================================
# SESSION FEEDBACK ENDPOINTS
# ============================================================================

@router.post("/{session_id}/feedback")
async def submit_session_feedback(
    session_id: int,
    rating: int = Form(..., ge=1, le=5),
    comment: Optional[str] = Form(None),
    is_anonymous: bool = Form(False),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Student submits feedback for a session
    - rating: 1-5 stars
    - comment: optional text feedback
    - is_anonymous: whether to hide student identity
    """
    from app.models.database import SessionFeedback, SessionParticipant
    from sqlalchemy import select
    
    # Verify session exists
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify student is enrolled in this session
    participant_result = await session_service.session_repo.db.execute(
        select(SessionParticipant).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == current_user.user_id,
            SessionParticipant.role == 'student'
        )
    )
    participant = participant_result.scalar_one_or_none()
    
    if not participant:
        raise HTTPException(status_code=403, detail="You are not enrolled in this session")
    
    # Check if feedback already exists
    existing_feedback = await session_service.session_repo.db.execute(
        select(SessionFeedback).where(
            SessionFeedback.session_id == session_id,
            SessionFeedback.reviewer_id == current_user.user_id
        )
    )
    existing = existing_feedback.scalar_one_or_none()
    
    if existing:
        # Update existing feedback
        existing.rating = rating
        existing.comment = comment
        existing.is_anonymous = is_anonymous
        await session_service.session_repo.db.commit()
        return {"message": "Feedback updated successfully"}
    
    # Create new feedback
    feedback = SessionFeedback(
        session_id=session_id,
        reviewer_id=current_user.user_id,
        reviewer_type='student',
        rating=rating,
        comment=comment,
        is_anonymous=is_anonymous,
        is_public=True
    )
    
    session_service.session_repo.db.add(feedback)
    await session_service.session_repo.db.commit()
    
    return {"message": "Feedback submitted successfully"}


@router.get("/{session_id}/feedback")
async def get_session_feedbacks(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Get all feedback for a session (tutor can see all, student sees their own)"""
    from app.models.database import SessionFeedback
    from sqlalchemy import select
    
    query = select(SessionFeedback).where(SessionFeedback.session_id == session_id)
    
    # Students can only see their own feedback
    if current_user.role == 'student':
        query = query.where(SessionFeedback.reviewer_id == current_user.user_id)
    
    result = await session_service.session_repo.db.execute(query)
    feedbacks = result.scalars().all()
    
    return [
        {
            "feedback_id": f.feedback_id,
            "rating": f.rating,
            "comment": f.comment,
            "is_anonymous": f.is_anonymous,
            "reviewer_id": None if f.is_anonymous else f.reviewer_id,
            "created_at": f.created_at.isoformat() if f.created_at else None
        }
        for f in feedbacks
    ]


@router.get("/feedback/bulk")
async def get_bulk_feedbacks(
    session_ids: str = Query(..., description="Comma-separated session IDs"),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Get feedbacks for multiple sessions in one call - OPTIMIZED"""
    from app.models.database import SessionFeedback
    from sqlalchemy import select
    
    # Parse comma-separated IDs
    try:
        ids = [int(id.strip()) for id in session_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session IDs format")
    
    # Single query for all sessions
    query = select(SessionFeedback).where(SessionFeedback.session_id.in_(ids))
    
    # Students can only see their own feedback
    if current_user.role == 'student':
        query = query.where(SessionFeedback.reviewer_id == current_user.user_id)
    
    result = await session_service.session_repo.db.execute(query)
    feedbacks = result.scalars().all()
    
    # Group by session_id
    feedback_map = {}
    for f in feedbacks:
        if f.session_id not in feedback_map:
            feedback_map[f.session_id] = []
        feedback_map[f.session_id].append({
            "feedback_id": f.feedback_id,
            "session_id": f.session_id,
            "rating": f.rating,
            "comment": f.comment,
            "is_anonymous": f.is_anonymous,
            "reviewer_id": None if f.is_anonymous else f.reviewer_id,
            "created_at": f.created_at.isoformat() if f.created_at else None
        })
    
    return feedback_map


@router.get("/subject/{subject_id}/feedbacks")
async def get_subject_feedbacks(
    subject_id: int,
    tutor_id: int = Query(None, description="Optional tutor_id to filter feedbacks for specific tutor"),
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Get all feedbacks for a subject's sessions
    Returns: average rating, total feedbacks, and individual feedback details
    
    Accessible by: Everyone (students can view to decide which course to join)
    Optional tutor_id filter to get feedbacks for specific tutor's sessions only
    """
    from app.models.database import SessionFeedback, Session as DBSession, Tutor, User as DBUser
    from sqlalchemy import select, func
    
    # If called by tutor without tutor_id specified, use their own tutor_id
    if current_user.role == 'tutor' and not tutor_id:
        tutor_result = await session_service.session_repo.db.execute(
            select(Tutor).where(Tutor.user_id == current_user.user_id)
        )
        tutor = tutor_result.scalar_one_or_none()
        if tutor:
            tutor_id = tutor.tutor_id
    
    # Build query to get feedbacks
    query = (
        select(SessionFeedback, DBSession, DBUser)
        .join(DBSession, SessionFeedback.session_id == DBSession.session_id)
        .outerjoin(DBUser, SessionFeedback.reviewer_id == DBUser.user_id)
        .where(DBSession.subject_id == subject_id)
    )
    
    # Filter by tutor_id if specified
    if tutor_id:
        query = query.where(DBSession.tutor_id == tutor_id)
    
    # Execute query
    feedbacks_result = await session_service.session_repo.db.execute(
        query.order_by(SessionFeedback.created_at.desc())
    )
    feedbacks_data = feedbacks_result.all()
    
    # If no feedbacks found, return empty result
    if not feedbacks_data:
        return {
            "average_rating": 0,
            "total_feedbacks": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "feedbacks": []
        }
    
    # Calculate statistics
    ratings = [f[0].rating for f in feedbacks_data]
    total_feedbacks = len(ratings)
    average_rating = sum(ratings) / total_feedbacks if total_feedbacks > 0 else 0
    
    # Rating distribution
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating in ratings:
        rating_distribution[rating] += 1
    
    # Format feedback details
    feedbacks_list = []
    for feedback, session, user in feedbacks_data:
        feedback_item = {
            "feedback_id": feedback.feedback_id,
            "session_id": feedback.session_id,
            "session_date": session.scheduled_date.isoformat() if session.scheduled_date else None,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "is_anonymous": feedback.is_anonymous,
            "created_at": feedback.created_at.isoformat() if feedback.created_at else None
        }
        
        # Only show reviewer info if NOT anonymous
        if not feedback.is_anonymous and user:
            feedback_item["reviewer_name"] = user.full_name
            feedback_item["reviewer_email"] = user.email
        else:
            feedback_item["reviewer_name"] = "Ẩn danh"
            feedback_item["reviewer_email"] = None
        
        feedbacks_list.append(feedback_item)
    
    return {
        "average_rating": round(average_rating, 2),
        "total_feedbacks": total_feedbacks,
        "rating_distribution": rating_distribution,
        "feedbacks": feedbacks_list
    }


# ============================================================================
# ATTENDANCE ENDPOINTS
# ============================================================================

@router.get("/{session_id}/participants")
async def get_session_participants(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Get list of students enrolled in a session (for attendance)"""
    from app.models.database import SessionParticipant, User as DBUser, Student, Attendance
    from sqlalchemy import select
    from sqlalchemy.orm import outerjoin
    
    # Verify session exists and user is the tutor
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Only tutors can view participants
    if current_user.role != 'tutor':
        raise HTTPException(status_code=403, detail="Only tutors can view participants")
    
    # Get all student participants with their attendance status
    result = await session_service.session_repo.db.execute(
        select(SessionParticipant, DBUser, Student, Attendance)
        .join(DBUser, SessionParticipant.user_id == DBUser.user_id)
        .join(Student, DBUser.user_id == Student.user_id)
        .outerjoin(Attendance, and_(
            Attendance.session_id == session_id,
            Attendance.student_id == Student.student_id
        ))
        .where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.role == 'student'
        )
    )
    participants_data = result.all()
    
    # Debug log
    for participant, user, student, attendance in participants_data:
        print(f"🔍 User: {user.full_name}, Student ID: {student.student_id}, Attendance: {attendance}, Status: {attendance.status if attendance else 'NO RECORD'}")
    
    return [
        {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "status": participant.status,
            "attended": participant.attended,
            "attendance_status": attendance.status if attendance else None,  # 'present' or 'absent'
            "joined_at": participant.joined_at.isoformat() if participant.joined_at else None
        }
        for participant, user, student, attendance in participants_data
    ]


@router.post("/{session_id}/attendance")
async def mark_attendance(
    session_id: int,
    attendance_data: List[dict],  # [{"user_id": int, "is_present": bool, "is_late": bool, "is_excused": bool}, ...]
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Tutor marks attendance for students in a session"""
    from app.models.database import SessionParticipant, Student, Attendance
    from sqlalchemy import select
    from datetime import datetime, timezone, timedelta
    
    # Verify session exists and user is the tutor
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if current_user.role != 'tutor':
        raise HTTPException(status_code=403, detail="Only tutors can mark attendance")
    
    vietnam_tz = timezone(timedelta(hours=7))
    now = datetime.now(vietnam_tz)
    
    # Update attendance for each student
    updated_count = 0
    skipped_count = 0
    
    for record in attendance_data:
        user_id = record.get('user_id')
        is_present = record.get('is_present', False)
        is_late = record.get('is_late', False)
        is_excused = record.get('is_excused', False)
        
        # Determine status
        if is_present:
            status = 'present'
        elif is_late:
            status = 'late'
        elif is_excused:
            status = 'excused'
        else:
            status = 'absent'
        
        # Get participant
        result = await session_service.session_repo.db.execute(
            select(SessionParticipant).where(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id,
                SessionParticipant.role == 'student'
            )
        )
        participant = result.scalar_one_or_none()
        
        if not participant:
            continue
        
        # Get student_id from user_id
        student_result = await session_service.session_repo.db.execute(
            select(Student).where(Student.user_id == user_id)
        )
        student = student_result.scalar_one_or_none()
        
        if not student:
            continue
        
        # Check if attendance already exists
        existing_attendance = await session_service.session_repo.db.execute(
            select(Attendance).where(
                Attendance.session_id == session_id,
                Attendance.student_id == student.student_id
            )
        )
        existing = existing_attendance.scalar_one_or_none()
        
        if existing:
            # Update existing attendance
            existing.status = status
            existing.check_in_time = now
            updated_count += 1
        else:
            # Create new attendance record
            attendance = Attendance(
                session_id=session_id,
                student_id=student.student_id,
                status=status,
                check_in_time=now if status in ['present', 'late'] else None,
                check_out_time=None,
                duration_minutes=None,
                notes=None
            )
            
            session_service.session_repo.db.add(attendance)
            updated_count += 1
        
        # Also update participant status (attended = present or late)
        participant.attended = (status in ['present', 'late'])
    
    await session_service.session_repo.db.commit()
    
    message = f"Attendance marked for {updated_count} students"
    if skipped_count > 0:
        message += f". {skipped_count} students already marked (skipped)"
    
    return {
        "message": message,
        "updated_count": updated_count,
        "skipped_count": skipped_count
    }

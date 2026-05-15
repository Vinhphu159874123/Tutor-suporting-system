from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from datetime import datetime

from app.schemas.scheduling import (
    AvailabilityCreate, AvailabilityResponse, AvailabilityUpdate,
    TimeSlotRequest, TimeSlotResponse,
    ScheduleSessionRequest, RescheduleRequest
)
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.services.scheduling_service import SchedulingService
from app.services.session_service import SessionService
from app.core.dependencies import get_scheduling_service, get_session_service, get_current_user, get_tutor_repository
from app.models.database import User
from app.repositories.tutor_repository import TutorRepository

router = APIRouter()

# ============================================================================
# AVAILABILITY ENDPOINTS - IMPLEMENTED
# ============================================================================

@router.get("/availability/{tutor_id}", response_model=Dict)
async def get_tutor_availability(
    tutor_id: int,
    scheduling_service: SchedulingService = Depends(get_scheduling_service)
):
    """
    Get tutor availability schedule
    
    Returns:
    - recurring: Weekly schedule grouped by day (0=Monday, 6=Sunday)
    - one_time: Specific date availability slots
    """
    return await scheduling_service.get_tutor_availability(tutor_id)


@router.post("/availability/{tutor_id}", response_model=dict)
async def set_availability(
    tutor_id: int,
    availability_data: AvailabilityCreate,
    scheduling_service: SchedulingService = Depends(get_scheduling_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create new availability slot for tutor
    
    For recurring: Set day_of_week (0-6), leave specific_date null
    For one-time: Set specific_date, leave day_of_week null
    """
    # TODO: Verify current_user is the tutor or admin
    try:
        return await scheduling_service.set_availability(tutor_id, availability_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/availability/{availability_id}", response_model=dict)
async def update_availability(
    availability_id: int,
    availability_data: AvailabilityUpdate,
    scheduling_service: SchedulingService = Depends(get_scheduling_service),
    current_user: User = Depends(get_current_user)
):
    """Update an existing availability slot"""
    update_dict = availability_data.model_dump(exclude_unset=True)
    result = await scheduling_service.update_availability(availability_id, update_dict)
    if not result:
        raise HTTPException(status_code=404, detail="Availability slot not found")
    return result


@router.delete("/availability/{availability_id}")
async def delete_availability(
    availability_id: int,
    scheduling_service: SchedulingService = Depends(get_scheduling_service),
    current_user: User = Depends(get_current_user)
):
    """Delete an availability slot"""
    success = await scheduling_service.delete_availability(availability_id)
    if not success:
        raise HTTPException(status_code=404, detail="Availability slot not found")
    return {"message": "Availability slot deleted successfully"}


@router.post("/find-slots", response_model=List[TimeSlotResponse])
async def find_available_slots(
    slot_request: TimeSlotRequest,
    scheduling_service: SchedulingService = Depends(get_scheduling_service)
):
    """Find available time slots for tutor on specific date"""
    return await scheduling_service.find_available_slots(
        slot_request.tutor_id,
        slot_request.date,
        slot_request.duration_minutes
    )


# ============================================================================
# SESSION SCHEDULING ENDPOINTS - IMPLEMENTED
# ============================================================================

@router.post("/sessions", response_model=SessionResponse)
async def schedule_session(
    request: ScheduleSessionRequest,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    scheduling_service: SchedulingService = Depends(get_scheduling_service)
):
    """Schedule a new tutoring session"""
    
    # 1. Calculate duration
    duration_minutes = int((datetime.combine(request.scheduled_date, request.end_time) - 
                          datetime.combine(request.scheduled_date, request.start_time)).seconds / 60)
    
    # 2. Check if tutor is available at requested time
    available_slots = await scheduling_service.find_available_slots(
        tutor_id=request.tutor_id,
        date=datetime.combine(request.scheduled_date, request.start_time),
        duration_minutes=duration_minutes
    )
    
    # Check if requested slot is available
    requested_start = request.start_time.strftime("%H:%M:%S")
    requested_end = request.end_time.strftime("%H:%M:%S")
    
    slot_available = any(
        slot["start_time"] == requested_start and 
        slot["end_time"] == requested_end
        for slot in available_slots
    )
    
    if not slot_available:
        raise HTTPException(
            status_code=400, 
            detail="Requested time slot is not available"
        )
    
    # 3. Create session
    session_data = SessionCreate(
        title=f"Tutoring Session - {request.scheduled_date}",
        tutor_id=request.tutor_id,
        student_ids=[current_user.user_id],  # Current user as student
        scheduled_date=request.scheduled_date,
        start_time=request.start_time,
        end_time=request.end_time,
        subject_id=request.subject_id,
        notes=request.notes
    )
    
    return await session_service.create_session(session_data)


@router.put("/sessions/{session_id}/reschedule", response_model=SessionResponse)
async def reschedule_session(
    session_id: int,
    request: RescheduleRequest,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    scheduling_service: SchedulingService = Depends(get_scheduling_service),
    tutor_repo: TutorRepository = Depends(get_tutor_repository)
):
    """Reschedule an existing session"""
    
    # 1. Get current session
    session = await session_service.get_session(session_id)
    
    # 2. Check permissions (tutor or coordinator)
    is_authorized = False
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    
    # Check if user is the session tutor
    if 'tutor' in user_roles:
        tutor = await tutor_repo.get_by_user_id(current_user.user_id)
        if tutor and tutor.tutor_id == session.tutor_id:
            is_authorized = True
    
    # Check if user is coordinator/admin
    if 'coordinator' in user_roles or 'admin' in user_roles:
        is_authorized = True
    
    if not is_authorized:
        raise HTTPException(status_code=403, detail="Not authorized to reschedule this session")
    
    # 3. Check session status (only confirmed/published sessions can be rescheduled)
    if session.status not in ["confirmed", "published"]:
        raise HTTPException(
            status_code=400, 
            detail="Can only reschedule confirmed or published sessions"
        )
    
    # 4. Calculate duration
    duration_minutes = int((datetime.combine(request.scheduled_date, request.end_time) - 
                          datetime.combine(request.scheduled_date, request.start_time)).seconds / 60)
    
    # 5. Check if new time is available
    available_slots = await scheduling_service.find_available_slots(
        tutor_id=session.tutor_id,
        date=datetime.combine(request.scheduled_date, request.start_time),
        duration_minutes=duration_minutes
    )
    
    requested_slot = {
        "start_time": request.start_time.strftime("%H:%M:%S"),
        "end_time": request.end_time.strftime("%H:%M:%S")
    }
    
    slot_available = any(
        slot["start_time"] == requested_slot["start_time"] and 
        slot["end_time"] == requested_slot["end_time"]
        for slot in available_slots
    )
    
    if not slot_available:
        raise HTTPException(
            status_code=400, 
            detail="New time slot is not available"
        )
    
    # 6. Update session
    update_data = SessionUpdate(
        scheduled_date=request.scheduled_date,
        start_time=request.start_time,
        end_time=request.end_time,
        notes=f"Rescheduled: {request.reason}" if request.reason else "Rescheduled"
    )
    
    return await session_service.update_session(session_id, update_data)


@router.delete("/sessions/{session_id}")
async def cancel_session(
    session_id: int,
    reason: str = None,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    tutor_repo: TutorRepository = Depends(get_tutor_repository)
):
    """Cancel a scheduled session"""
    
    # 1. Get session
    session = await session_service.get_session(session_id)
    
    # 2. Check permissions (tutor or coordinator)
    is_authorized = False
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    
    # Check if user is the session tutor
    if 'tutor' in user_roles:
        tutor = await tutor_repo.get_by_user_id(current_user.user_id)
        if tutor and tutor.tutor_id == session.tutor_id:
            is_authorized = True
    
    # Check if user is coordinator/admin
    if 'coordinator' in user_roles or 'admin' in user_roles:
        is_authorized = True
    
    if not is_authorized:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this session")
    
    # 3. Check if can cancel (not completed or ongoing)
    if session.status in ["completed", "ongoing"]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot cancel completed or ongoing sessions"
        )
    
    # 4. Update status to cancelled
    update_data = SessionUpdate(
        status="cancelled",
        notes=f"Cancelled by {current_user.full_name}: {reason}" if reason else f"Cancelled by {current_user.full_name}"
    )
    
    await session_service.update_session(session_id, update_data)
    
    return {"message": "Session cancelled successfully", "session_id": session_id}

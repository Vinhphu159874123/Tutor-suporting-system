from fastapi import APIRouter, Depends
from typing import List

from app.schemas.scheduling import (
    AvailabilityCreate, AvailabilityResponse, TimeSlotRequest, TimeSlotResponse
)
from app.services.scheduling_service import SchedulingService
from app.core.dependencies import get_scheduling_service

router = APIRouter()

# ============================================================================
# SCHEDULING ENDPOINTS - All PLACEHOLDER (no availability table yet)
# ============================================================================

@router.get("/availability/{tutor_id}", response_model=List[AvailabilityResponse])
async def get_tutor_availability(
    tutor_id: int,
    scheduling_service: SchedulingService = Depends(get_scheduling_service)
):
    """Get tutor availability - PLACEHOLDER (no table yet)"""
    return await scheduling_service.get_tutor_availability(tutor_id)

@router.post("/availability", response_model=dict)
async def set_availability(
    availability_data: AvailabilityCreate,
    scheduling_service: SchedulingService = Depends(get_scheduling_service)
):
    """Set tutor availability - PLACEHOLDER (no table yet)"""
    # Service will return placeholder response
    return await scheduling_service.set_availability(0, availability_data.model_dump())

@router.post("/find-slots", response_model=List[TimeSlotResponse])
async def find_available_slots(
    slot_request: TimeSlotRequest,
    scheduling_service: SchedulingService = Depends(get_scheduling_service)
):
    """Find available time slots - PLACEHOLDER (no table yet)"""
    return await scheduling_service.find_available_slots(
        slot_request.tutor_id,
        slot_request.date,
        slot_request.duration_minutes
    )


# ============================================================================
# LEGACY PLACEHOLDER ENDPOINTS
# ============================================================================

@router.post("/sessions")
async def schedule_session():
    """Schedule a new tutoring session - PLACEHOLDER"""
    return {"message": "Schedule session - Implementation pending"}

@router.put("/sessions/{session_id}/reschedule")
async def reschedule_session(session_id: int):
    """Reschedule an existing session - PLACEHOLDER"""
    return {"message": "Reschedule session - Implementation pending"}

@router.delete("/sessions/{session_id}")
async def cancel_session(session_id: int):
    """Cancel a scheduled session - PLACEHOLDER"""
    return {"message": "Cancel session - Implementation pending"}

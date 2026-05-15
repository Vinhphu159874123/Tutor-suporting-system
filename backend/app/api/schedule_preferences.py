"""Schedule Preferences API — thin controller"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from app.models.database import User
from app.core.dependencies import get_current_user, get_schedule_preferences_service
from app.services.schedule_preferences_service import SchedulePreferencesService
from app.schemas.schedule_preference import (
    TimeSlot, SchedulePreferenceCreate, SchedulePreferenceUpdate,
)

router = APIRouter()

# --- DI ---
_svc = get_schedule_preferences_service

def _check_student(user: User, mode: Optional[str] = None):
    roles = user.role if isinstance(user.role, list) else [user.role]
    eff = mode or ('student' if 'student' in roles else roles[0])
    if eff != 'student' and 'student' not in roles:
        raise HTTPException(status_code=403, detail="Only students can use this endpoint")

def _check_tutor(user: User, mode: Optional[str] = None):
    roles = user.role if isinstance(user.role, list) else [user.role]
    eff = mode or ('tutor' if 'tutor' in roles else roles[0])
    if eff != 'tutor' and 'tutor' not in roles:
        raise HTTPException(status_code=403, detail="Only tutors can use this endpoint")

# --- Student endpoints ---
@router.post("/")
async def create_schedule_preference(
    data: SchedulePreferenceCreate,
    mode: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    svc: SchedulePreferencesService = Depends(_svc),
):
    _check_student(current_user, mode)
    payload = data.model_dump()
    payload['available_time_slots'] = [s.model_dump() for s in data.available_time_slots]
    return await svc.create_preference(current_user, payload)

@router.get("/my-preferences")
async def get_my_preferences(
    status: Optional[str] = Query(None),
    mode: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    svc: SchedulePreferencesService = Depends(_svc),
):
    _check_student(current_user, mode)
    return await svc.get_my_preferences(current_user, status)

@router.put("/{preference_id}")
async def update_schedule_preference(
    preference_id: int,
    update_data: SchedulePreferenceUpdate,
    current_user: User = Depends(get_current_user),
    svc: SchedulePreferencesService = Depends(_svc),
):
    _check_student(current_user)
    payload = update_data.model_dump(exclude_none=True)
    if update_data.available_time_slots is not None:
        payload['available_time_slots'] = [s.model_dump() for s in update_data.available_time_slots]
    return await svc.update_preference(current_user, preference_id, payload)

@router.delete("/{preference_id}")
async def delete_schedule_preference(
    preference_id: int,
    current_user: User = Depends(get_current_user),
    svc: SchedulePreferencesService = Depends(_svc),
):
    _check_student(current_user)
    return await svc.delete_preference(current_user, preference_id)

# --- Tutor endpoints ---
@router.get("/statistics")
async def get_preferences_statistics(
    subject_id: Optional[int] = Query(None),
    min_requests: int = Query(1),
    mode: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    svc: SchedulePreferencesService = Depends(_svc),
):
    _check_tutor(current_user, mode)
    return await svc.get_statistics(subject_id=subject_id, min_requests=min_requests)

@router.get("/statistics/{subject_id}/details")
async def get_subject_preference_details(
    subject_id: int,
    mode: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    svc: SchedulePreferencesService = Depends(_svc),
):
    _check_tutor(current_user, mode)
    return await svc.get_subject_details(subject_id)

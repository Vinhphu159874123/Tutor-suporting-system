"""
Scheduling Service - Business Logic Layer
Business logic for scheduling operations
"""
from typing import List, Optional
from datetime import datetime

from app.repositories.scheduling_repository import SchedulingRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.scheduling import AvailabilityCreate
from datetime import time, timedelta
class SchedulingService:
    """Business logic for scheduling operations"""
    
    def __init__(self, scheduling_repo: SchedulingRepository, session_repo: SessionRepository):
        self.scheduling_repo = scheduling_repo
        self.session_repo = session_repo
    
    async def get_tutor_availability(self, tutor_id: int) -> List[dict]:
        """Get tutor's availability schedule"""
        availability = await self.scheduling_repo.get_tutor_availability(tutor_id)
        recurring = {i: [] for i in range(7)}  # 0-6 for Mon-Sun
        one_time = []

        for slot in availability:
            slot_data = {
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
                "is_available": slot.is_available,
                "notes": slot.notes
            }
            if slot.is_recurring:
                recurring[slot.day_of_week].append(slot_data)
            else:
                one_time.append({
                    "specific_date": slot.specific_date.isoformat(),
                    **slot_data
                })
        return {"recurring": recurring, "one_time": one_time}

    
    
    async def set_availability(
        self, 
        tutor_id: int, 
        availability_data: AvailabilityCreate
    ) -> dict:
        """
        Create new availability slot
        
        Validates:
        - end_time > start_time
        - For recurring: day_of_week in 0-6
        - For one-time: specific_date provided
        """
        # Validate time range
        if availability_data.end_time <= availability_data.start_time:
            raise ValueError("end_time must be after start_time")
        
        # Validate recurring vs one-time
        if availability_data.is_recurring:
            if availability_data.day_of_week is None or not (0 <= availability_data.day_of_week <= 6):
                raise ValueError("Recurring availability requires valid day_of_week (0-6)")
            if availability_data.specific_date is not None:
                raise ValueError("Recurring availability cannot have specific_date")
        else:
            if availability_data.specific_date is None:
                raise ValueError("One-time availability requires specific_date")
            if availability_data.day_of_week is not None:
                raise ValueError("One-time availability cannot have day_of_week")
        
        # Create availability
        availability = await self.scheduling_repo.create_availability(
            tutor_id=tutor_id,
            is_recurring=availability_data.is_recurring,
            start_time=availability_data.start_time,
            end_time=availability_data.end_time,
            day_of_week=availability_data.day_of_week,
            specific_date=availability_data.specific_date,
            is_available=availability_data.is_available,
            notes=availability_data.notes
        )
        
        return {
            "availability_id": availability.availability_id,
            "tutor_id": availability.tutor_id,
            "is_recurring": availability.is_recurring,
            "day_of_week": availability.day_of_week,
            "specific_date": availability.specific_date.isoformat() if availability.specific_date else None,
            "start_time": availability.start_time.isoformat(),
            "end_time": availability.end_time.isoformat(),
            "is_available": availability.is_available,
            "notes": availability.notes,
            "created_at": availability.created_at.isoformat()
        }
    
    async def update_availability(
        self,
        availability_id: int,
        update_data: dict
    ) -> dict:
        """Update an existing availability slot"""
        availability = await self.scheduling_repo.get_by_id(availability_id)
        if not availability:
            return None
        
        updated = await self.scheduling_repo.update_availability(
            availability_id, **update_data
        )
        
        return {
            "availability_id": updated.availability_id,
            "tutor_id": updated.tutor_id,
            "is_recurring": updated.is_recurring,
            "day_of_week": updated.day_of_week,
            "specific_date": updated.specific_date.isoformat() if updated.specific_date else None,
            "start_time": updated.start_time.isoformat(),
            "end_time": updated.end_time.isoformat(),
            "is_available": updated.is_available,
            "notes": updated.notes,
            "created_at": updated.created_at.isoformat()
        }
    
    async def delete_availability(self, availability_id: int) -> bool:
        """Delete an availability slot"""
        return await self.scheduling_repo.delete_availability(availability_id)
    
    async def find_available_slots(
        self,
        tutor_id: int,
        date: datetime,
        duration_minutes: int
    ) -> List[dict]:
        """Find available time slots for a specific date"""
        day_of_week = date.weekday()  # 0=Monday, 6=Sunday
        target_date = date.date() if isinstance(date, datetime) else date
        
        # Get availability for this date
        available_ranges = []
        
        # 1. Get recurring availability for this day of week
        recurring = await self.scheduling_repo.get_recurring_by_day(tutor_id, day_of_week)
        for avail in recurring:
            if avail.is_available:
                available_ranges.append({
                    'start': datetime.combine(target_date, avail.start_time),
                    'end': datetime.combine(target_date, avail.end_time)
                })
        
        # 2. Get one-time availability for this specific date
        one_time = await self.scheduling_repo.get_one_time_by_date(tutor_id, target_date)
        for avail in one_time:
            if avail.is_available:
                available_ranges.append({
                    'start': datetime.combine(target_date, avail.start_time),
                    'end': datetime.combine(target_date, avail.end_time)
                })
        
        if not available_ranges:
            return []
        
        # 3. Get booked sessions for this date
        booked_ranges = []
        sessions = await self.session_repo.get_sessions_by_tutor_date(
            tutor_id, 
            target_date,
            statuses=['confirmed', 'ongoing']
        )
        
        for session in sessions:
            booked_ranges.append({
                'start': datetime.combine(session.scheduled_date, session.start_time),
                'end': datetime.combine(session.scheduled_date, session.end_time)
            })
        
        # 4. Calculate free time ranges
        free_ranges = self._calculate_free_ranges(available_ranges, booked_ranges)
        
        # 5. Split into duration-based slots
        slots = []
        for free_range in free_ranges:
            range_slots = self._split_into_duration_slots(
                free_range['start'],
                free_range['end'],
                duration_minutes
            )
            slots.extend(range_slots)
        
        return slots
    
    def _calculate_free_ranges(self, available_ranges: List[dict], booked_ranges: List[dict]) -> List[dict]:
        """Calculate free time ranges from available minus booked"""
        free_ranges = []
        
        for avail in available_ranges:
            avail_start = avail['start']
            avail_end = avail['end']
            
            # Find overlapping bookings
            overlapping = [
                booked for booked in booked_ranges
                if not (booked['end'] <= avail_start or booked['start'] >= avail_end)
            ]
            
            if not overlapping:
                # No overlap, entire range is free
                free_ranges.append({'start': avail_start, 'end': avail_end})
            else:
                # Calculate free segments between bookings
                current_start = avail_start
                
                for booked in sorted(overlapping, key=lambda x: x['start']):
                    booked_start = max(current_start, booked['start'])
                    booked_end = min(avail_end, booked['end'])
                    
                    if current_start < booked_start:
                        free_ranges.append({
                            'start': current_start,
                            'end': booked_start
                        })
                    
                    current_start = max(current_start, booked_end)
                
                # Add remaining segment
                if current_start < avail_end:
                    free_ranges.append({
                        'start': current_start,
                        'end': avail_end
                    })
        
        return free_ranges
            
    def _split_into_duration_slots(self, start: datetime, end: datetime, duration_minutes: int) -> List[dict]:
        """Split a time range into slots of specified duration"""
        slots = []
        duration = timedelta(minutes=duration_minutes)
        current = start
        
        while current + duration <= end:
            slot_end = current + duration
            slots.append({
                'start_time': current.time().isoformat(),
                'end_time': slot_end.time().isoformat(),
                'date': current.date().isoformat()
            })
            current = slot_end
        
        return slots
   
    

    async def check_conflict(
        self,
        tutor_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """Check if time slot has conflict"""
        # TODO: Check against existing sessions
        # TODO: Check against availability schedule
        return False

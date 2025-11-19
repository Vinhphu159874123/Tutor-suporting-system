"""
Scheduling Repository - Database Access Layer
PLACEHOLDER - No availability table in current schema
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select
from datetime import time, date
from app.models.database import TutorAvailability  # Assuming this model will be created in the future


class SchedulingRepository:
    """Handle database operations for scheduling - PLACEHOLDER"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_tutor_availability(self, tutor_id: int) -> List[dict]:
        """Get tutor's availability slots - PLACEHOLDER"""
        result = await self.db.execute(
            select(TutorAvailability)
            .where(TutorAvailability.tutor_id == tutor_id)
            .order_by(
                TutorAvailability.is_recurring.desc(),
                TutorAvailability.day_of_week,
                TutorAvailability.specific_date,
                TutorAvailability.start_time
            )
        )
        availability_records = result.scalars().all()
        return availability_records
    
    
    async def create_availability(self,  is_recurring: bool,
        tutor_id: int,
        start_time: time,
        end_time: time,
        day_of_week: Optional[int] = None,
        specific_date: Optional[date] = None,
        is_available: bool = True,
        notes: Optional[str] = None) -> dict:

        
        availability = TutorAvailability(
            tutor_id=tutor_id,
            is_recurring=is_recurring,
            day_of_week=day_of_week,
            specific_date=specific_date,
            start_time=start_time,
            end_time=end_time,
            is_available=is_available,
            notes=notes
        )
        self.db.add(availability)
        await self.db.commit()
        await self.db.refresh(availability)
        return availability
    

    async def get_by_id(self, availability_id: int) -> Optional[TutorAvailability]:
        """Get availability slot by ID"""
        result = await self.db.execute(
            select(TutorAvailability)
            .where(TutorAvailability.availability_id == availability_id)
        )
        return result.scalar_one_or_none()
    
    async def update_availability(
        self, 
        availability_id: int, 
        **kwargs
    ) -> Optional[TutorAvailability]:
        """Update availability slot"""

        availability = await self.get_by_id(availability_id)
        if not availability:
            return None
        
        for key, value in kwargs.items():
            if hasattr(availability, key) and value is not None:
                setattr(availability, key, value)
        
        await self.db.commit()
        await self.db.refresh(availability)
        return availability
    
    async def delete_availability(self, availability_id: int) -> bool:
        """Delete availability slot"""
        availability = await self.get_by_id(availability_id)
        if not availability:
            return False
        
        await self.db.delete(availability)
        await self.db.commit()
        return True
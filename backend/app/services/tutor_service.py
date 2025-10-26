"""
Tutor Service - Business Logic Layer
Handle tutor-related business logic and orchestration
Now with event emission for async side effects
"""
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.repositories.tutor_repository import TutorRepository
from app.repositories.user_repository import UserRepository
from app.schemas.tutor import TutorCreate, TutorUpdate, TutorResponse
from app.events import event_bus, EventTypes


class TutorService:
    """Business logic for tutor operations - Placeholder implementations"""
    
    def __init__(
        self, 
        tutor_repo: TutorRepository,
        user_repo: UserRepository
    ):
        self.tutor_repo = tutor_repo
        self.user_repo = user_repo
    
    async def get_tutor(self, tutor_id: int) -> TutorResponse:
        """Get tutor by ID with user data"""
        tutor = await self.tutor_repo.get_by_id(tutor_id)
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found"
            )
        
        # Get user data
        user = await self.user_repo.get_by_id(tutor.user_id)
        
        # Combine data
        response = TutorResponse.model_validate(tutor)
        if user:
            response.full_name = user.full_name
            response.email = user.email
            response.faculty = user.faculty
        
        return response
    
    async def get_tutor_by_user_id(self, user_id: int) -> Optional[TutorResponse]:
        """Get tutor by user ID"""
        tutor = await self.tutor_repo.get_by_user_id(user_id)
        if not tutor:
            return None
        
        return await self.get_tutor(tutor.id)
    
    async def get_all_tutors(
        self,
        skip: int = 0,
        limit: int = 100,
        subject: Optional[str] = None,
        is_available: Optional[bool] = None,
        min_rating: Optional[float] = None
    ) -> List[TutorResponse]:
        """Get all tutors with filters - PLACEHOLDER"""
        tutors = await self.tutor_repo.get_all(
            skip=skip,
            limit=limit,
            subject=subject,
            is_available=is_available,
            min_rating=min_rating
        )
        
        # Convert to response DTOs with user data
        responses = []
        for tutor in tutors:
            user = await self.user_repo.get_by_id(tutor.user_id)
            response = TutorResponse.model_validate(tutor)
            if user:
                response.full_name = user.full_name
                response.email = user.email
                response.faculty = user.faculty
            responses.append(response)
        
        return responses
    
    async def register_tutor(self, tutor_data: TutorCreate) -> TutorResponse:
        """Register new tutor profile"""
        # Validate user exists
        user = await self.user_repo.get_by_id(tutor_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user already has tutor profile
        existing = await self.tutor_repo.get_by_user_id(tutor_data.user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has tutor profile"
            )
        
        # Validate user role (optional)
        if user.role not in ['tutor', 'admin']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must have tutor role"
            )
        
        # Create tutor profile
        tutor_dict = tutor_data.model_dump()
        tutor_dict['is_available'] = True
        tutor_dict['total_sessions'] = 0
        tutor_dict['rating'] = 0.0
        
        tutor = await self.tutor_repo.create(tutor_dict)
        
        # Emit event for approval workflow, welcome email
        await event_bus.emit(EventTypes.TUTOR_REGISTERED, {
            "tutor_id": tutor.id,
            "user_id": tutor.user_id,
            "email": user.email,
            "full_name": user.full_name,
            "subjects": tutor.subjects
        })
        
        return await self.get_tutor(tutor.id)
    
    async def update_tutor(
        self, 
        tutor_id: int, 
        tutor_data: TutorUpdate
    ) -> TutorResponse:
        """Update tutor profile"""
        tutor = await self.tutor_repo.get_by_id(tutor_id)
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found"
            )
        
        # Update tutor
        update_data = tutor_data.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        updated = await self.tutor_repo.update(tutor_id, update_data)
        
        return await self.get_tutor(updated.id)
    
    async def delete_tutor(self, tutor_id: int) -> bool:
        """Delete tutor profile"""
        result = await self.tutor_repo.delete(tutor_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found"
            )
        return True
    
    # PLACEHOLDER methods - implement when needed
    
    async def set_availability(self, tutor_id: int, availability_data: dict) -> dict:
        """Set tutor availability - PLACEHOLDER"""
        # TODO: Implement availability management
        return {"message": "Set availability - Not implemented yet"}
    
    async def get_tutor_schedule(self, tutor_id: int, date_range: dict) -> dict:
        """Get tutor schedule - PLACEHOLDER"""
        # TODO: Implement schedule retrieval
        return {"message": "Get schedule - Not implemented yet"}

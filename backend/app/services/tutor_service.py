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
from app.repositories.student_repository import StudentRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.tutor import TutorCreate, TutorUpdate, TutorResponse
from app.events import event_bus, EventTypes
from app.schemas.session import SessionListResponse
from app.repositories.session_repository import SessionRepository
from app.models.database import Session as SessionModel
from app.models.database import Student as StudentModel
from app.schemas.session import SessionResponse
class TutorService:
    """Business logic for tutor operations - Placeholder implementations"""
    
    def __init__(
        self, 
        tutor_repo: TutorRepository,
        user_repo: UserRepository,
        session_repo: SessionRepository,
        student_repo: StudentRepository,
        feedback_repo: FeedbackRepository
    ):
        self.tutor_repo = tutor_repo
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.student_repo = student_repo
        self.feedback_repo = feedback_repo 

    
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
            response.phone = user.phone
            response.avatar_url = user.avatar_url
        
        return response
    
    async def get_tutor_by_user_id(self, user_id: int) -> Optional[TutorResponse]:
        """Get tutor by user ID"""
        tutor = await self.tutor_repo.get_by_user_id(user_id)
        if not tutor:
            return None
        
        return await self.get_tutor(tutor.tutor_id)
    
    async def get_all_tutors(
        self,
        skip: int = 0,
        limit: int = 100,
        subject: Optional[str] = None,
        min_rating: Optional[float] = None
    ) -> List[TutorResponse]:
        """Get all tutors with filters - PLACEHOLDER"""
        tutors = await self.tutor_repo.get_all(
            skip=skip,
            limit=limit,
            subject=subject,
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
                response.phone = user.phone
                response.avatar_url = user.avatar_url
            responses.append(response)
        
        return responses
    
    async def get_tutor_availability(self, tutor_id: int) -> dict:
        """Get tutor's available time slots from database"""
        from sqlalchemy import select, and_
        from app.models.database import TutorAvailability
        from datetime import datetime, timedelta
        
        # Get tutor
        tutor = await self.tutor_repo.get_by_id(tutor_id)
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found"
            )
        
        # Query availability from database
        query = select(TutorAvailability).where(
            TutorAvailability.tutor_id == tutor_id
        ).order_by(TutorAvailability.day_of_week, TutorAvailability.start_time)
        
        result = await self.tutor_repo.db.execute(query)
        availabilities = result.scalars().all()
        
        # Group by day
        days_map = {
            0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4", 
            3: "Thứ 5", 4: "Thứ 6", 5: "Thứ 7", 6: "Chủ nhật"
        }
        
        grouped = {}
        for avail in availabilities:
            day_name = days_map.get(avail.day_of_week, f"Day {avail.day_of_week}")
            if day_name not in grouped:
                grouped[day_name] = []
            
            # Format time slot
            start_str = avail.start_time.strftime("%H:%M") if hasattr(avail.start_time, 'strftime') else str(avail.start_time)[:5]
            end_str = avail.end_time.strftime("%H:%M") if hasattr(avail.end_time, 'strftime') else str(avail.end_time)[:5]
            slot = f"{start_str} - {end_str}"
            grouped[day_name].append(slot)
        
        # Convert to array format
        availability_list = [
            {"day": day, "slots": slots}
            for day, slots in grouped.items()
        ]
        
        return {"availability": availability_list}
    
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
        tutor_dict['total_sessions'] = 0
        tutor_dict['rating'] = 0.0
        
        tutor = await self.tutor_repo.create(tutor_dict)
        
        # Emit event for approval workflow, welcome email
        await event_bus.emit(EventTypes.TUTOR_REGISTERED, {
            "tutor_id": tutor.tutor_id,
            "user_id": tutor.user_id,
            "email": user.email,
            "full_name": user.full_name
        })
        
        return await self.get_tutor(tutor.tutor_id)
    
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
        
        return await self.get_tutor(updated.tutor_id)
    
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

    async def get_tutor_sessions(
        self,
        tutor_user_id: int,  # Changed: User ID instead of tutor table ID
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> SessionListResponse:
        """
        Get tutor's sessions with multiple students support
        
        Args:
            tutor_user_id: User ID of the tutor (not tutor table ID)
            status: Filter by session status
            start_date/end_date: Date range
            skip/limit: Pagination
        
        Returns:
            SessionListResponse with sessions containing multiple students
        """
        # Validate status parameter
        valid_statuses = ["draft", "published", "pending_assignment", "confirmed", "ongoing", "completed", "cancelled"]
        if status and status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Get sessions from repository
        sessions, total = await self.session_repo.get_sessions_by_tutor(
            tutor_user_id=tutor_user_id,
            status=status,
            start_date=start_date,  
            end_date=end_date,
            skip=skip,
            limit=limit
        )

        # Build response DTOs with multiple students
        session_responses = []
        for session in sessions:
            # Build tutor info
            tutor_info = None
            if session.tutor and session.tutor.user:
                from app.schemas.session import TutorInfo
                tutor_info = TutorInfo(
                    user_id=session.tutor.user_id,
                    tutor_id=session.tutor.tutor_id,
                    email=session.tutor.user.email,
                    full_name=session.tutor.user.full_name,
                    specialization=session.tutor.bio or session.tutor.faculty  # Use bio or faculty as specialization
                )
            
            # Build students list from participants
            students = []
            if session.participants:
                from app.schemas.session import StudentInfo, ParticipantStatus
                for participant in session.participants:
                    # Only include student participants
                    if participant.role == 'student' and participant.user:
                        # Get student record using repository
                        student_record = await self.student_repo.get_by_user_id(participant.user_id)
                        student_id = student_record.student_id if student_record else 0
                        
                        students.append(StudentInfo(
                            user_id=participant.user.user_id,
                            student_id=student_id,
                            email=participant.user.email,
                            full_name=participant.user.full_name,
                            status=ParticipantStatus(participant.status)
                        ))
            
            # Build session response
            session_responses.append(
                SessionResponse(
                    session_id=session.session_id,
                    tutor_id=session.tutor_id,
                    coordinator_id=session.coordinator_id,
                    title=session.title,
                    description=session.description,
                    subject_id=session.subject_id,
                    scheduled_date=session.scheduled_date,
                    start_time=session.start_time,
                    end_time=session.end_time,
                    duration=session.duration,
                    location_type=session.location_type,
                    meeting_link=session.meeting_link,
                    physical_address=session.physical_address,
                    max_students=session.max_students,
                    status=session.status,
                    actual_start=session.actual_start,
                    actual_end=session.actual_end,
                    session_notes=session.session_notes,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    tutor=tutor_info,
                    students=students,
                    subject_name=session.subject.subject_name if session.subject else None,
                    subject_code=session.subject.subject_code if session.subject else None
                )
            )
        
        return SessionListResponse(
            total=total,
            sessions=session_responses,
            skip=skip,
            limit=limit
        )

    
    async def set_availability(self, tutor_id: int, availability_data: dict) -> dict:
        """Set tutor availability - PLACEHOLDER"""
        # TODO: Implement availability management
        return {"message": "Set availability - Not implemented yet"}
    
    async def get_tutor_schedule(self, tutor_id: int, date_range: dict) -> dict:
        """Get tutor schedule - PLACEHOLDER"""
        # TODO: Implement schedule retrieval
        return {"message": "Get schedule - Not implemented yet"}
    
    async def get_tutor_reviews(self, tutor_id: int, skip: int = 0, limit: int = 20) -> dict:
        """Get reviews and ratings for a tutor"""
        # Verify tutor exists
        tutor = await self.tutor_repo.get_by_id(tutor_id)
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found"
            )
        
        # Get rating statistics
        stats = await self.feedback_repo.get_tutor_rating_stats(tutor_id)
        
        # Get feedbacks with pagination
        feedbacks = await self.feedback_repo.get_feedbacks_by_tutor(tutor_id, skip, limit)
        
        # Format response
        reviews = []
        for feedback in feedbacks:
            review = {
                "feedback_id": feedback.feedback_id,
                "session_id": feedback.session_id,
                "rating": feedback.rating,
                "comment": feedback.comment,
                "tags": feedback.tags,
                "created_at": feedback.created_at.isoformat(),
                "is_anonymous": feedback.is_anonymous
            }
            
            # Add reviewer name if not anonymous
            if not feedback.is_anonymous and feedback.reviewer:
                review["reviewer_name"] = feedback.reviewer.full_name
            else:
                review["reviewer_name"] = "Anonymous"
            
            reviews.append(review)
        
        return {
            "tutor_id": tutor_id,
            "statistics": {
                "average_rating": stats['average_rating'],
                "total_reviews": stats['total_reviews'],
                "unique_reviewers": stats['unique_reviewers']
            },
            "reviews": reviews,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": stats['total_reviews']
            }
        }


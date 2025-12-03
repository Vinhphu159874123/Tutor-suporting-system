"""
Student Service - Business Logic Layer
Handle student-related business logic and orchestration
Now with event emission for async side effects
"""
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.repositories.student_repository import StudentRepository
from app.repositories.user_repository import UserRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.student import (
    StudentCreate, 
    StudentUpdate, 
    StudentResponse,
    TutorRequestCreate,
    SessionFeedbackCreate
)
from app.events import event_bus, EventTypes


class StudentService:
    """Business logic for student operations"""
    
    def __init__(
        self, 
        student_repo: StudentRepository,
        user_repo: UserRepository,
        feedback_repo: FeedbackRepository
    ):
        self.student_repo = student_repo
        self.user_repo = user_repo
        self.feedback_repo = feedback_repo
    
    async def get_student(self, student_id: int) -> StudentResponse:
        """Get student by ID with user data"""
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Get user data
        user = await self.user_repo.get_by_id(student.user_id)
        
        # Combine data
        response = StudentResponse.model_validate(student)
        if user:
            response.full_name = user.full_name
            response.email = user.email
            response.phone = user.phone
            response.avatar_url = user.avatar_url
        
        return response
    
    async def get_student_by_user_id(self, user_id: int) -> Optional[StudentResponse]:
        """Get student by user ID"""
        student = await self.student_repo.get_by_user_id(user_id)
        if not student:
            return None
        
        return await self.get_student(student.student_id)
    
    async def get_all_students(
        self,
        skip: int = 0,
        limit: int = 100,
        year: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[StudentResponse]:
        """Get all students with filters"""
        students = await self.student_repo.get_all(
            skip=skip,
            limit=limit,
            year=year,
            is_active=is_active
        )
        
        # Convert to response DTOs with user data
        responses = []
        for student in students:
            user = await self.user_repo.get_by_id(student.user_id)
            response = StudentResponse.model_validate(student)
            if user:
                response.full_name = user.full_name
                response.email = user.email
                response.phone = user.phone
                response.avatar_url = user.avatar_url
            responses.append(response)
        
        return responses
    
    async def register_student(self, student_data: StudentCreate) -> StudentResponse:
        """Register new student profile"""
        # Validate user exists
        user = await self.user_repo.get_by_id(student_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user already has student profile
        existing = await self.student_repo.get_by_user_id(student_data.user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has student profile"
            )
        
        # Validate user role (optional - should be student)
        user_roles = user.role if isinstance(user.role, list) else [user.role]
        if 'student' not in user_roles and 'admin' not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must have student role"
            )
        
        # Create student profile
        student_dict = student_data.model_dump()
        student_dict['is_active'] = True
        student_dict['total_sessions'] = 0
        
        student = await self.student_repo.create(student_dict)
        
        # Emit event for welcome email, notifications
        await event_bus.emit(EventTypes.STUDENT_REGISTERED, {
            "student_id": student.student_id,
            "user_id": student.user_id,
            "email": user.email,
            "full_name": user.full_name
        })
        
        return await self.get_student(student.student_id)
    
    async def update_student(
        self, 
        student_id: int, 
        student_data: StudentUpdate
    ) -> StudentResponse:
        """Update student profile"""
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Update student
        update_data = student_data.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        updated = await self.student_repo.update(student_id, update_data)
        
        return await self.get_student(updated.student_id)
    
    async def delete_student(self, student_id: int) -> bool:
        """Delete student profile"""
        result = await self.student_repo.delete(student_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        return True
    
    async def request_tutor(
        self, 
        student_id: int, 
        request_data: TutorRequestCreate
    ) -> dict:
        """Request a tutor for specific subject"""
        # Verify student exists
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # TODO: Implement tutor request creation
        # - Create tutor request record
        # - Notify available tutors
        # - Use AI matching if configured
        
        return {
            "message": "Tutor request created",
            "student_id": student_id,
            "subject": request_data.subject,
            "status": "pending"
        }
    
    async def submit_feedback(
        self, 
        student_id: int,
        feedback_data: SessionFeedbackCreate
    ) -> dict:
        """Submit feedback after session"""
        from app.repositories.session_repository import SessionRepository
        from app.core.database import get_db
        
        # Verify student exists
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Get session to verify ownership and status
        session_repo = SessionRepository(self.student_repo.db)
        session = await session_repo.get_by_id(feedback_data.session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Verify session is completed
        if session.status != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only submit feedback for completed sessions"
            )
        
        # Check if feedback already exists
        existing = await self.feedback_repo.get_feedback_by_session_and_reviewer(
            feedback_data.session_id,
            student.user_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback already submitted for this session"
            )
        
        # Create feedback
        feedback_dict = {
            'session_id': feedback_data.session_id,
            'reviewer_id': student.user_id,
            'reviewer_type': 'student',
            'rating': feedback_data.rating,
            'comment': feedback_data.comment,
            'tags': feedback_data.tags or [],
            'is_public': True,
            'is_anonymous': feedback_data.is_anonymous,
            'created_at': datetime.utcnow()
        }
        
        feedback = await self.feedback_repo.create_feedback(feedback_dict)
        
        # Update tutor's aggregated rating
        await self.feedback_repo.update_tutor_rating(session.tutor_id)
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": feedback.feedback_id,
            "session_id": feedback.session_id,
            "rating": feedback.rating
        }


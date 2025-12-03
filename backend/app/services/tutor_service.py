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
from app.schemas.tutor import TutorCreate, TutorUpdate, TutorResponse, TutorRegistrationCreate, TutorRegistrationResponse
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
        """Get all tutors with filters - Optimized with JOINs"""
        from sqlalchemy import select, and_
        from sqlalchemy.orm import selectinload
        from app.models.database import TutorRegistration, Subject, User, Tutor
        
        # Get tutors first
        tutors = await self.tutor_repo.get_all(
            skip=skip,
            limit=limit,
            subject=subject,
            min_rating=min_rating
        )
        
        if not tutors:
            return []
        
        # Get tutor IDs and user IDs
        tutor_ids = [t.tutor_id for t in tutors]
        user_ids = [t.user_id for t in tutors]
        
        # Batch fetch users
        users_query = select(User).where(User.user_id.in_(user_ids))
        users_result = await self.tutor_repo.db.execute(users_query)
        users = users_result.scalars().all()
        user_map = {u.user_id: u for u in users}
        
        # Batch fetch tutor registrations with subjects using JOIN
        registrations_query = select(
            TutorRegistration, Subject
        ).join(
            Subject, TutorRegistration.subject_id == Subject.subject_id
        ).where(
            and_(
                TutorRegistration.tutor_id.in_(tutor_ids),
                TutorRegistration.status == 'approved'
            )
        )
        registrations_result = await self.tutor_repo.db.execute(registrations_query)
        registrations = registrations_result.all()
        
        # Group subjects by tutor_id
        tutor_subjects_map = {}
        for reg, subject in registrations:
            if reg.tutor_id not in tutor_subjects_map:
                tutor_subjects_map[reg.tutor_id] = []
            tutor_subjects_map[reg.tutor_id].append(subject.subject_name)
        
        # Build responses
        responses = []
        for tutor in tutors:
            response = TutorResponse.model_validate(tutor)
            
            # Add user data
            user = user_map.get(tutor.user_id)
            if user:
                response.full_name = user.full_name
                response.email = user.email
                response.phone = user.phone
                response.avatar_url = user.avatar_url
            
            # Add subjects
            response.subjects = tutor_subjects_map.get(tutor.tutor_id, [])
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
        """
        Register or update tutor profile (without subject registration)
        This creates the general tutor profile. Use register_subject() to register for specific subjects.
        """
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
            # Update existing profile instead of creating new one
            tutor_dict = tutor_data.model_dump(exclude_unset=True)
            availability_data = tutor_dict.pop('availability', None)
            experience_years = tutor_dict.pop('experience_years', None)
            
            # Update teaching_experience if experience_years provided
            if experience_years is not None:
                if 'teaching_experience' not in tutor_dict:
                    tutor_dict['teaching_experience'] = existing.teaching_experience or {}
                tutor_dict['teaching_experience']['years'] = experience_years
            
            tutor_dict['updated_at'] = datetime.utcnow()
            tutor = await self.tutor_repo.update(existing.tutor_id, tutor_dict)
            
            # Update availability if provided
            if availability_data:
                await self._save_tutor_availability(tutor.tutor_id, availability_data)
            
            return await self.get_tutor(tutor.tutor_id)
        
        # Add 'tutor' role to user if not already present
        user_roles = user.role if isinstance(user.role, list) else [user.role]
        if 'tutor' not in user_roles:
            user_roles.append('tutor')
            await self.user_repo.update(user.user_id, {"role": user_roles})
        
        # Create new tutor profile
        tutor_dict = tutor_data.model_dump()
        tutor_dict['total_sessions'] = 0
        tutor_dict['rating'] = 0.0
        
        # Set default hourly_rate if not provided
        if 'hourly_rate' not in tutor_dict or tutor_dict['hourly_rate'] is None:
            tutor_dict['hourly_rate'] = 0
        
        # Extract availability to handle separately
        availability_data = tutor_dict.pop('availability', {})
        experience_years = tutor_dict.pop('experience_years', 0)
        
        # Store experience_years in teaching_experience JSON field
        if 'teaching_experience' not in tutor_dict:
            tutor_dict['teaching_experience'] = {}
        tutor_dict['teaching_experience']['years'] = experience_years
        
        tutor = await self.tutor_repo.create(tutor_dict)
        
        # Save availability to TutorAvailability table
        if availability_data:
            await self._save_tutor_availability(tutor.tutor_id, availability_data)
        
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
    
    async def _save_tutor_availability(self, tutor_id: int, availability: dict):
        """Save tutor availability to database"""
        from app.models.database import TutorAvailability
        from datetime import time
        
        # Map day names to numbers
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        # Delete existing availability for this tutor
        from sqlalchemy import delete
        await self.tutor_repo.db.execute(
            delete(TutorAvailability).where(TutorAvailability.tutor_id == tutor_id)
        )
        
        # Insert new availability
        for day_name, time_slots in availability.items():
            day_num = day_map.get(day_name.lower())
            if day_num is None:
                continue
                
            for time_slot in time_slots:
                # Parse time slot (format: "07:00-09:00" or "7:00 - 9:00")
                time_slot = time_slot.replace(' ', '')
                if '-' in time_slot:
                    start_str, end_str = time_slot.split('-')
                    start_hour, start_min = map(int, start_str.split(':'))
                    end_hour, end_min = map(int, end_str.split(':'))
                    
                    avail = TutorAvailability(
                        tutor_id=tutor_id,
                        day_of_week=day_num,
                        start_time=time(start_hour, start_min),
                        end_time=time(end_hour, end_min),
                        is_recurring=True
                    )
                    self.tutor_repo.db.add(avail)
        
        await self.tutor_repo.db.commit()

    async def _save_session_schedule(self, tutor_id: int, subject_id: int, availability: dict, subject_name: str):
        """Save session schedule for specific subject"""
        from app.models.database import SessionSchedule
        from datetime import time, date
        from sqlalchemy import delete
        
        # Map day names to numbers
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        # Delete existing schedules for this tutor + subject
        await self.tutor_repo.db.execute(
            delete(SessionSchedule).where(
                SessionSchedule.tutor_id == tutor_id,
                SessionSchedule.subject_id == subject_id
            )
        )
        
        # Insert new schedules
        for day_name, time_slots in availability.items():
            day_num = day_map.get(day_name.lower())
            if day_num is None:
                continue
                
            for time_slot in time_slots:
                # Parse time slot (format: "07:00-09:00" or "7:00 - 9:00")
                time_slot = time_slot.replace(' ', '')
                if '-' in time_slot:
                    start_str, end_str = time_slot.split('-')
                    start_hour, start_min = map(int, start_str.split(':'))
                    end_hour, end_min = map(int, end_str.split(':'))
                    
                    # Calculate duration in hours
                    duration_hours = (end_hour * 60 + end_min - start_hour * 60 - start_min) // 60
                    if duration_hours < 1:
                        duration_hours = 1
                    
                    schedule = SessionSchedule(
                        tutor_id=tutor_id,
                        subject_id=subject_id,
                        title=f"Tutoring Session - {subject_name}",
                        description=f"Weekly tutoring session for {subject_name}",
                        is_recurring=True,
                        recurrence_pattern='weekly',
                        day_of_week=day_num,
                        start_time=time(start_hour, start_min),
                        end_time=time(end_hour, end_min),
                        duration=duration_hours,
                        location_type='online',
                        max_students=5,
                        valid_from=date.today(),
                        valid_until=None,  # No end date
                        is_active=True
                    )
                    self.tutor_repo.db.add(schedule)
        
        await self.tutor_repo.db.commit()
    
    async def register_subject(
        self, 
        user_id: int, 
        registration_data: TutorRegistrationCreate
    ) -> TutorRegistrationResponse:
        """
        Register tutor for teaching a specific subject
        Creates TutorRegistration entry for one subject
        """
        from app.models.database import TutorRegistration, Subject
        from sqlalchemy import select
        
        # Get tutor profile - must exist first
        tutor = await self.tutor_repo.get_by_user_id(user_id)
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor profile not found. Please create your tutor profile first."
            )
        
        # Validate subject exists
        subject_query = select(Subject).where(Subject.subject_id == registration_data.subject_id)
        subject_result = await self.tutor_repo.db.execute(subject_query)
        subject = subject_result.scalar_one_or_none()
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {registration_data.subject_id} not found"
            )
        
        # Check if already registered for this subject
        existing_query = select(TutorRegistration).where(
            TutorRegistration.tutor_id == tutor.tutor_id,
            TutorRegistration.subject_id == registration_data.subject_id
        )
        existing_result = await self.tutor_repo.db.execute(existing_query)
        existing_reg = existing_result.scalar_one_or_none()
        
        if existing_reg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You have already registered for {subject.subject_name} ({subject.subject_code})"
            )
        
        # Create registration
        new_registration = TutorRegistration(
            tutor_id=tutor.tutor_id,
            subject_id=registration_data.subject_id,
            gpa=registration_data.gpa,
            qualifications=registration_data.qualifications,
            status='pending',
            total_sessions=registration_data.total_sessions,
            start_date=registration_data.start_date,
            availability=registration_data.availability,  # Save availability to registration
            max_students=registration_data.max_students
        )
        
        self.tutor_repo.db.add(new_registration)
        await self.tutor_repo.db.commit()
        await self.tutor_repo.db.refresh(new_registration)
        
        # Save availability for this subject if provided
        availability_data = registration_data.availability
        if availability_data:
            # Save to TutorAvailability (general availability)
            await self._save_tutor_availability(tutor.tutor_id, availability_data)
            # Save to SessionSchedule (schedule for this specific subject)
            await self._save_session_schedule(tutor.tutor_id, registration_data.subject_id, availability_data, subject.subject_name)
        
        # Get user info for event
        user = await self.user_repo.get_by_id(user_id)
        
        # Emit event for notification to coordinators
        await event_bus.emit(EventTypes.TUTOR_SUBJECT_REGISTERED, {
            "registration_id": new_registration.registration_id,
            "tutor_id": tutor.tutor_id,
            "user_id": user_id,
            "subject_id": registration_data.subject_id,
            "subject_name": subject.subject_name,
            "subject_code": subject.subject_code,
            "full_name": user.full_name if user else "Unknown",
            "email": user.email if user else "",
            "bio": tutor.bio,
            "gpa": float(registration_data.gpa) if registration_data.gpa else None,
            "qualifications": registration_data.qualifications,
            "availability": availability_data if availability_data else {},
            "total_sessions": new_registration.total_sessions,
            "start_date": new_registration.start_date.isoformat() if new_registration.start_date else None,
            "end_date": new_registration.end_date.isoformat() if new_registration.end_date else None,
            "max_students": new_registration.max_students
        })
        
        # Build response
        response = TutorRegistrationResponse(
            registration_id=new_registration.registration_id,
            tutor_id=new_registration.tutor_id,
            subject_id=new_registration.subject_id,
            gpa=new_registration.gpa,
            qualifications=new_registration.qualifications,
            status=new_registration.status,
            approved_by=new_registration.approved_by,
            rejection_reason=new_registration.rejection_reason,
            registered_at=new_registration.registered_at,
            responded_at=new_registration.responded_at,
            total_sessions=new_registration.total_sessions,
            start_date=new_registration.start_date,
            end_date=new_registration.end_date,
            subject_name=subject.subject_name,
            subject_code=subject.subject_code
        )
        
        return response
    
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


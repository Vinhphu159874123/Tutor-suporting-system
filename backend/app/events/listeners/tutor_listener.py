"""
Tutor Event Listener
Handle tutor-related events
"""
import logging
from typing import Dict, Any
from sqlalchemy import select, func

from app.events.base_listener import BaseListener
from app.events import event_bus, EventTypes
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class TutorRegistrationListener(BaseListener):
    """Handle tutor registration events"""
    
    async def handle(self, data: Dict[str, Any]):
        """
        Create notification for admin when tutor registers
        
        Expected data:
            - tutor_id: int
            - user_id: int
            - email: str
            - full_name: str
        """
        try:
            logger.info(f"New tutor registration: {data.get('full_name')} (ID: {data.get('tutor_id')})")
            
            # Get all admin users
            from app.models.database import User, Notifications
            
            async with AsyncSessionLocal() as db:
                # Find all admins and coordinators
                result = await db.execute(
                    select(User).where(User.role.in_(['admin', 'coordinator']))
                )
                admins_and_coordinators = result.scalars().all()
                
                # Create notification for each admin/coordinator
                for admin in admins_and_coordinators:
                    notification = Notifications(
                        user_id=admin.user_id,
                        type="tutor_registration",
                        title="Đơn đăng ký Tutor mới",
                        message=f"{data.get('full_name')} đã đăng ký làm Tutor. Vui lòng xem xét và phê duyệt.",
                        data={
                            "tutor_id": data.get('tutor_id'),
                            "user_id": data.get('user_id'),
                            "status": "pending"
                        },
                        is_read=False
                    )
                    db.add(notification)
                
                await db.commit()
                logger.info(f"Created notifications for {len(admins_and_coordinators)} admin(s)/coordinator(s)")
                
        except Exception as e:
            logger.error(f"Error creating tutor registration notification: {e}")


class TutorSubjectRegistrationListener(BaseListener):
    """Handle tutor subject registration events"""
    
    async def handle(self, data: Dict[str, Any]):
        """
        Create notification for coordinators when tutor registers for a subject
        
        Expected data:
            - registration_id: int
            - tutor_id: int
            - user_id: int
            - subject_id: int
            - subject_name: str
            - subject_code: str
            - full_name: str
            - email: str
            - gpa: float (optional)
            - qualifications: str (optional)
        """
        try:
            subject_name = data.get('subject_name')
            subject_code = data.get('subject_code')
            full_name = data.get('full_name')
            logger.info(f"New subject registration: {full_name} for {subject_code} - {subject_name}")
            
            from app.models.database import User, Notifications
            from sqlalchemy import any_
            
            async with AsyncSessionLocal() as db:
                # Find all coordinators
                result = await db.execute(
                    select(User).where('coordinator' == any_(User.role))
                )
                coordinators = result.scalars().all()
                
                # Create notification for each coordinator
                message = f"{full_name} đã đăng ký dạy môn {subject_code} - {subject_name}."
                if data.get('gpa'):
                    message += f" GPA: {data.get('gpa')}"
                if data.get('max_students'):
                    message += f" | Tối đa {data.get('max_students')} sinh viên/buổi"
                
                for coordinator in coordinators:
                    notification = Notifications(
                        user_id=coordinator.user_id,
                        type="subject_registration",
                        title="Đơn đăng ký dạy môn mới",
                        message=message,
                        data={
                            "registration_id": data.get('registration_id'),
                            "tutor_id": data.get('tutor_id'),
                            "user_id": data.get('user_id'),
                            "subject_id": data.get('subject_id'),
                            "subject_code": subject_code,
                            "subject_name": subject_name,
                            "status": "pending",
                            "bio": data.get('bio'),
                            "gpa": data.get('gpa'),
                            "qualifications": data.get('qualifications'),
                            "availability": data.get('availability', {}),
                            "total_sessions": data.get('total_sessions', 10),
                            "start_date": data.get('start_date'),
                            "end_date": data.get('end_date'),
                            "max_students": data.get('max_students', 25)
                        },
                        is_read=False
                    )
                    db.add(notification)
                
                await db.commit()
                logger.info(f"Created subject registration notifications for {len(coordinators)} coordinator(s)")
                
                # Also notify the tutor about submission
                tutor_message = f"Đơn đăng ký dạy môn {subject_code} - {subject_name} của bạn đã được gửi và đang chờ phê duyệt."
                if data.get('gpa'):
                    tutor_message += f" GPA: {data.get('gpa')}"
                if data.get('max_students'):
                    tutor_message += f" | Tối đa {data.get('max_students')} sinh viên/buổi"
                
                tutor_notification = Notifications(
                    user_id=data.get('user_id'),
                    type="subject_registration_submitted",
                    title="Đơn đăng ký đã được gửi",
                    message=tutor_message,
                    data={
                        "registration_id": data.get('registration_id'),
                        "subject_code": subject_code,
                        "subject_name": subject_name,
                        "status": "pending",
                        "bio": data.get('bio'),
                        "gpa": data.get('gpa'),
                        "qualifications": data.get('qualifications'),
                        "availability": data.get('availability', {}),
                        "total_sessions": data.get('total_sessions', 10),
                        "start_date": data.get('start_date'),
                        "end_date": data.get('end_date'),
                        "max_students": data.get('max_students', 25)
                    },
                    is_read=False
                )
                db.add(tutor_notification)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error creating subject registration notification: {e}")


class TutorApprovalListener(BaseListener):
    """Handle tutor registration approval/rejection events"""
    
    async def handle(self, data: Dict[str, Any]):
        """
        Create notification for tutor when their registration is approved/rejected
        AND auto-generate sessions from schedule
        
        Expected data:
            - user_id: int
            - registration_id: int
            - tutor_id: int
            - subject_id: int
            - subject_name: str
            - status: str ('approved' or 'rejected')
            - reason: str (optional, for rejection)
            - total_sessions: int (optional, default 10)
            - start_date: str (ISO format)
            - schedule_id: int (optional, specific schedule to use)
        """
        try:
            user_id = data.get('user_id')
            subject_name = data.get('subject_name', 'môn học')
            status = data.get('status', 'approved')
            
            logger.info(f"Registration {status}: user_id={user_id}, subject={subject_name}")
            
            from app.models.database import Notifications
            
            async with AsyncSessionLocal() as db:
                if status == 'approved':
                    notification = Notifications(
                        user_id=user_id,
                        type='registration_approved',
                        title='Đơn đăng ký môn học được phê duyệt',
                        message=f'Chúc mừng! Đơn đăng ký dạy môn {subject_name} của bạn đã được phê duyệt.',
                        data={
                            "registration_id": data.get('registration_id'),
                            "subject_name": subject_name,
                            "status": "approved"
                        },
                        is_read=False
                    )
                    db.add(notification)
                    await db.commit()
                    
                    # NOTE: Sessions are NO LONGER auto-generated on approval
                    # Tutor must manually generate sessions from CourseDetail page
                    logger.info(f"✅ Registration approved. Tutor can now generate sessions manually from course detail page.")
                    
                else:  # rejected
                    reason = data.get('reason', 'Không đáp ứng yêu cầu')
                    notification = Notifications(
                        user_id=user_id,
                        type='registration_rejected',
                        title='Đơn đăng ký môn học bị từ chối',
                        message=f'Đơn đăng ký dạy môn {subject_name} của bạn đã bị từ chối. Lý do: {reason}',
                        data={
                            "registration_id": data.get('registration_id'),
                            "subject_name": subject_name,
                            "status": "rejected",
                            "reason": reason
                        },
                        is_read=False
                    )
                    db.add(notification)
                    await db.commit()
                
                logger.info(f"Created {status} notification for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error creating approval/rejection notification: {e}")
    
    async def _generate_sessions_from_schedule(
        self,
        db,
        tutor_id: int,
        subject_id: int,
        total_sessions: int,
        start_date_str: str,
        max_students: int = 5,
        schedule_id: int = None
    ):
        """Generate Session records from SessionSchedule"""
        try:
            from app.models.database import SessionSchedule, Session, Subject
            from datetime import datetime, timedelta
            
            # Get the schedule (specific one if schedule_id provided, otherwise first active)
            if schedule_id:
                schedule_result = await db.execute(
                    select(SessionSchedule).where(
                        SessionSchedule.schedule_id == schedule_id,
                        SessionSchedule.tutor_id == tutor_id,
                        SessionSchedule.subject_id == subject_id,
                        SessionSchedule.is_active == True
                    )
                )
            else:
                schedule_result = await db.execute(
                    select(SessionSchedule).where(
                        SessionSchedule.tutor_id == tutor_id,
                        SessionSchedule.subject_id == subject_id,
                        SessionSchedule.is_active == True
                    )
                )
            schedule = schedule_result.scalar_one_or_none()
            
            if not schedule:
                logger.warning(f"No active schedule found for tutor {tutor_id}, subject {subject_id}")
                return
            
            # Get subject name
            subject_result = await db.execute(
                select(Subject).where(Subject.subject_id == subject_id)
            )
            subject = subject_result.scalar_one_or_none()
            subject_name = subject.subject_name if subject else "Unknown Subject"
            
            # Parse start date
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str).date()
            else:
                start_date = datetime.now().date()
            
            # Check if sessions already exist to prevent duplicates
            existing_sessions_result = await db.execute(
                select(func.count(Session.session_id)).where(
                    Session.tutor_id == tutor_id,
                    Session.subject_id == subject_id
                )
            )
            existing_count = existing_sessions_result.scalar() or 0
            
            if existing_count > 0:
                logger.warning(f"⚠️  Sessions already exist for tutor {tutor_id}, subject {subject_id} ({existing_count} sessions). Skipping generation.")
                return
            
            # Find first occurrence of the scheduled day
            current_date = start_date
            day_of_week = schedule.day_of_week
            
            # Advance to the first matching day
            while current_date.weekday() != day_of_week:
                current_date += timedelta(days=1)
            
            # Generate sessions
            logger.info(f"Generating {total_sessions} sessions starting from {current_date}")
            
            for i in range(total_sessions):
                session = Session(
                    tutor_id=tutor_id,
                    subject_id=subject_id,
                    title=f"{subject_name} - Session {i+1}",
                    description=schedule.description or f"Tutoring session for {subject_name}",
                    scheduled_date=current_date,
                    start_time=schedule.start_time,
                    end_time=schedule.end_time,
                    duration=schedule.duration,
                    location_type=schedule.location_type or 'online',
                    meeting_link=None,
                    physical_address=None,
                    max_students=max_students,
                    status='draft'
                )
                db.add(session)
                
                # Move to next week (same day)
                current_date += timedelta(weeks=1)
            
            await db.commit()
            logger.info(f"✅ Successfully generated {total_sessions} sessions for tutor {tutor_id}, subject {subject_id}")
            
        except Exception as e:
            logger.error(f"Error generating sessions from schedule: {e}")
            await db.rollback()


def register_tutor_listeners():
    """Register all tutor-related event listeners"""
    event_bus.register(EventTypes.TUTOR_REGISTERED, TutorRegistrationListener().execute)
    event_bus.register(EventTypes.TUTOR_SUBJECT_REGISTERED, TutorSubjectRegistrationListener().execute)
    event_bus.register(EventTypes.REGISTRATION_APPROVED, TutorApprovalListener().execute)
    event_bus.register(EventTypes.REGISTRATION_REJECTED, TutorApprovalListener().execute)
    logger.info("✅ Tutor event listeners registered")

"""
Tutor Event Listener
Handle tutor-related events
"""
import logging
from typing import Dict, Any
from sqlalchemy import select

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
            
            async with AsyncSessionLocal() as db:
                # Find all coordinators
                result = await db.execute(
                    select(User).where(User.role == 'coordinator')
                )
                coordinators = result.scalars().all()
                
                # Create notification for each coordinator
                message = f"{full_name} đã đăng ký dạy môn {subject_code} - {subject_name}."
                if data.get('gpa'):
                    message += f" GPA: {data.get('gpa')}"
                
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
                            "end_date": data.get('end_date')
                        },
                        is_read=False
                    )
                    db.add(notification)
                
                await db.commit()
                logger.info(f"Created subject registration notifications for {len(coordinators)} coordinator(s)")
                
                # Also notify the tutor about submission
                tutor_notification = Notifications(
                    user_id=data.get('user_id'),
                    type="subject_registration_submitted",
                    title="Đơn đăng ký đã được gửi",
                    message=f"Đơn đăng ký dạy môn {subject_code} - {subject_name} của bạn đã được gửi và đang chờ phê duyệt.",
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
                        "end_date": data.get('end_date')
                    },
                    is_read=False
                )
                db.add(tutor_notification)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error creating subject registration notification: {e}")


def register_tutor_listeners():
    """Register all tutor-related event listeners"""
    event_bus.register(EventTypes.TUTOR_REGISTERED, TutorRegistrationListener())
    event_bus.register(EventTypes.TUTOR_SUBJECT_REGISTERED, TutorSubjectRegistrationListener())
    logger.info("✅ Tutor event listeners registered")

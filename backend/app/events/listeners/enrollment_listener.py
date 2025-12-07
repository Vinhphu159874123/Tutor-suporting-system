"""
Student Enrollment Event Listeners
Handle course enrollment events with notifications
"""
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.base_listener import BaseListener
from app.events.event_bus import event_bus
from app.events.event_types import EventTypes
from app.core.database import get_db
from app.models.database import Notifications, User, Tutor, Subject
from app.websocket import manager
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class StudentEnrollmentListener(BaseListener):
    """
    Handle student enrollment events - sends notification to tutor
    """
    
    async def handle(self, data: Dict[str, Any]):
        """
        Process student enrollment event
        
        Expected data:
            - student_id: int (user_id)
            - student_name: str
            - tutor_id: int
            - subject_id: int
            - subject_name: str
            - sessions_count: int
        """
        logger.info(f"🎯 StudentEnrollmentListener.handle() called with data: {data}")
        
        student_id = data.get('student_id')
        student_name = data.get('student_name')
        tutor_id = data.get('tutor_id')
        subject_id = data.get('subject_id')
        subject_name = data.get('subject_name')
        sessions_count = data.get('sessions_count', 0)
        
        if not all([student_id, tutor_id, subject_id, subject_name]):
            logger.error(f"❌ Missing required data for enrollment event: {data}")
            return
            
        logger.info(f"📝 Processing enrollment: Student {student_id} enrolled in {subject_name}")
        
        try:
            # Create a new database session
            from app.core.database import AsyncSessionLocal
            from sqlalchemy import select
            
            async with AsyncSessionLocal() as db:
                # Get tutor user_id
                tutor_query = select(Tutor).where(Tutor.tutor_id == tutor_id)
                result = await db.execute(tutor_query)
                tutor = result.scalar_one_or_none()
                
                if not tutor:
                    logger.error(f"Tutor not found: {tutor_id}")
                    return
                
                # Create notification for tutor
                # Convert to Vietnam timezone (UTC+7)
                vietnam_tz = timezone(timedelta(hours=7))
                vietnam_time = datetime.now(vietnam_tz)
                
                notification = Notifications(
                    user_id=tutor.user_id,
                    type="student_enrolled",
                    title="Sinh viên mới đăng ký khóa học",
                    message=f"{student_name} đã đăng ký tham gia khóa học {subject_name} ({sessions_count} buổi học)",
                    related_entity_type="subject",
                    related_entity_id=subject_id,
                    is_read=False,
                    created_at=vietnam_time
                )
                
                db.add(notification)
                await db.commit()
                
                logger.info(f"✅ Notification sent to tutor {tutor.user_id} for enrollment of student {student_id}")
                
                # Send real-time notification via WebSocket if user is online
                try:
                    await manager.notify_user(
                        user_id=tutor.user_id,
                        notification_type="student_enrolled",
                        data={
                            "title": "Sinh viên mới đăng ký khóa học",
                            "message": f"{student_name} đã đăng ký tham gia khóa học {subject_name} ({sessions_count} buổi học)",
                            "student_id": student_id,
                            "student_name": student_name,
                            "subject_id": subject_id,
                            "subject_name": subject_name,
                            "sessions_count": sessions_count,
                            "timestamp": vietnam_time.isoformat()
                        }
                    )
                    logger.info(f"✅ Real-time WebSocket notification sent to tutor {tutor.user_id}")
                except Exception as ws_error:
                    logger.warning(f"⚠️ Failed to send WebSocket notification (user may be offline): {ws_error}")
            
        except Exception as e:
            logger.error(f"❌ Error handling enrollment event: {str(e)}", exc_info=True)


def register_enrollment_listeners():
    """Register all enrollment-related event listeners"""
    event_bus.register(
        EventTypes.STUDENT_ENROLLED_COURSE,
        StudentEnrollmentListener().execute
    )
    print(f"✅ Enrollment listener registered for event: {EventTypes.STUDENT_ENROLLED_COURSE}")
    logger.info(f"Enrollment event listeners registered for: {EventTypes.STUDENT_ENROLLED_COURSE}")

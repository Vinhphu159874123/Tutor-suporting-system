"""
Session Event Listeners
Handle session-related events with notifications
"""
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.base_listener import BaseListener
from app.events.event_bus import event_bus
from app.events.event_types import EventTypes
from app.core.database import get_db
from app.models.database import Notifications, User, Session as SessionModel, Tutor
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionCreatedListener(BaseListener):
    """
    Handle session creation events - sends notification to tutor
    """
    
    async def handle(self, data: Dict[str, Any]):
        """
        Process session created event
        
        Expected data:
            - session_id: int
            - tutor_id: int
        """
        session_id = data.get('session_id')
        tutor_id = data.get('tutor_id')
        
        if not session_id or not tutor_id:
            logger.error(f"Missing required data for session created event: {data}")
            return
            
        logger.info(f"Processing session created: {session_id}")
        
        try:
            # Get database session
            db = None
            async for db_session in get_db():
                db = db_session
                break
            
            if not db:
                logger.error("Failed to get database session")
                return
            
            # Get tutor user_id
            from sqlalchemy import select
            tutor_query = select(Tutor).where(Tutor.tutor_id == tutor_id)
            result = await db.execute(tutor_query)
            tutor = result.scalar_one_or_none()
            
            if not tutor:
                logger.error(f"Tutor not found: {tutor_id}")
                return
            
            # Get session details
            session_query = select(SessionModel).where(SessionModel.session_id == session_id)
            session_result = await db.execute(session_query)
            session = session_result.scalar_one_or_none()
            
            if not session:
                logger.error(f"Session not found: {session_id}")
                return
            
            # Create notification for tutor
            notification = Notifications(
                user_id=tutor.user_id,
                type="session_booked",
                title="Lịch học mới",
                message=f"Bạn có lịch học mới: {session.title}",
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.add(notification)
            await db.commit()
            
            logger.info(f"Notification sent to tutor {tutor.user_id} for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error creating session notification: {e}")
            # Don't raise - notification is non-critical


class SessionCompletedListener(BaseListener):
    """
    Handle session completion events
    PLACEHOLDER - Implement when needed
    """
    
    async def handle(self, data: Dict[str, Any]):
        """Process session completed event"""
        logger.info(f"[PLACEHOLDER] Session completed: {data.get('session_id')}")
        
        # TODO: Send feedback request to student
        # TODO: Update tutor statistics (total sessions, hours)
        # TODO: Update student statistics


class SessionCancelledListener(BaseListener):
    """
    Handle session cancellation events
    PLACEHOLDER - Implement when needed
    """
    
    async def handle(self, data: Dict[str, Any]):
        """Process session cancelled event"""
        logger.info(f"[PLACEHOLDER] Session cancelled: {data.get('session_id')}")
        
        # TODO: Notify both parties
        # TODO: Free up time slot
        # TODO: Update cancellation statistics
        # TODO: Apply cancellation policy if needed


# Register listeners with event bus
def register_session_listeners():
    """Register all session event listeners"""
    
    session_created = SessionCreatedListener()
    event_bus.register(
        EventTypes.SESSION_CREATED,
        session_created.execute
    )
    
    session_completed = SessionCompletedListener()
    event_bus.register(
        EventTypes.SESSION_COMPLETED,
        session_completed.execute
    )
    
    session_cancelled = SessionCancelledListener()
    event_bus.register(
        EventTypes.SESSION_CANCELLED,
        session_cancelled.execute
    )
    
    logger.info("Session event listeners registered")

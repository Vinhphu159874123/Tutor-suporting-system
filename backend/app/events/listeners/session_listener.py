"""
Session Event Listeners
Handle session-related events with notifications
"""
import logging
from typing import Dict, Any

from app.events.base_listener import BaseListener
from app.events.event_bus import event_bus
from app.events.event_types import EventTypes
from app.core.database import AsyncSessionLocal
from app.websocket import manager

logger = logging.getLogger(__name__)


class SessionCreatedListener(BaseListener):
    """
    Handle session creation events — notify tutor about new session.
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
            from sqlalchemy import select, insert
            from app.models.database import Notifications, Tutor, Session as SessionModel
            from datetime import datetime
            
            async with AsyncSessionLocal() as db:
                # Get tutor user_id
                tutor_result = await db.execute(
                    select(Tutor.user_id).where(Tutor.tutor_id == tutor_id)
                )
                tutor_user_id = tutor_result.scalar_one_or_none()
                
                if not tutor_user_id:
                    logger.error(f"Tutor not found: {tutor_id}")
                    return
                
                # Get session title
                session_result = await db.execute(
                    select(SessionModel.title).where(SessionModel.session_id == session_id)
                )
                session_title = session_result.scalar_one_or_none() or "Untitled"
                
                # Insert notification
                message = f"Bạn có lịch học mới: {session_title}"
                await db.execute(
                    insert(Notifications),
                    [{
                        "user_id": tutor_user_id,
                        "type": "session_booked",
                        "title": "Lịch học mới",
                        "message": message,
                        "is_read": False,
                    }]
                )
                await db.commit()
                
                # WebSocket push if online
                if manager.is_online(tutor_user_id):
                    try:
                        await manager.notify_user(
                            user_id=tutor_user_id,
                            notification_type="session_booked",
                            data={"title": "Lịch học mới", "message": message, "session_id": session_id}
                        )
                    except Exception as ws_err:
                        logger.warning(f"WebSocket push failed: {ws_err}")
                
                logger.info(f"Notification sent to tutor user_id={tutor_user_id} for session {session_id}")
                
        except Exception as e:
            logger.error(f"Error in SessionCreatedListener: {e}", exc_info=True)


# Register listeners with event bus
def register_session_listeners():
    """Register all session event listeners"""
    
    session_created = SessionCreatedListener()
    event_bus.register(
        EventTypes.SESSION_CREATED,
        session_created.execute
    )
    
    logger.info("Session event listeners registered")

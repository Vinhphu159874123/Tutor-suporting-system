"""
Notification Listener
Handle notification sending via WebSocket
"""
import logging
from typing import Dict, Any, List

from app.events.base_listener import BaseListener
from app.websocket import manager

logger = logging.getLogger(__name__)


class NotificationListener(BaseListener):
    """
    Handle notification sending via WebSocket
    """
    
    async def handle(self, data: Dict[str, Any]):
        """
        Send notification to users
        
        Expected data:
            - user_id: int or List[int]
            - title: str
            - message: str
            - type: str (info, warning, success, error)
            - link: str (optional)
        """
        user_ids = data.get('user_id')
        title = data.get('title', '')
        message = data.get('message', '')
        notification_type = data.get('type', 'info')
        link = data.get('link')
        
        logger.info(f"Sending notification: {title} to user(s): {user_ids}")
        
        # Convert single user_id to list
        if isinstance(user_ids, int):
            user_ids = [user_ids]
        
        # Prepare notification data
        notification_data = {
            "title": title,
            "message": message,
            "type": notification_type,
            "timestamp": data.get('timestamp')
        }
        
        if link:
            notification_data["link"] = link
        
        # Send to each user via WebSocket
        for user_id in user_ids:
            try:
                await manager.notify_user(
                    user_id=user_id,
                    notification_type=notification_type,
                    data=notification_data
                )
                logger.info(f"✅ WebSocket notification sent to user {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to send WebSocket notification to user {user_id}: {e}")
        
        # TODO: Store notification in database if needed
        # TODO: Send via mobile push notification if user offline


class EmailListener(BaseListener):
    """
    Handle email sending
    PLACEHOLDER - Implement when needed
    """
    
    async def handle(self, data: Dict[str, Any]):
        """
        Send email to users
        
        Expected data:
            - to: str or List[str]
            - subject: str
            - body: str or html
            - template: str (optional)
            - attachments: List (optional)
        """
        logger.info(f"[PLACEHOLDER] Sending email: {data.get('subject')}")
        
        # TODO: Implement email sending (SMTP)
        # TODO: Use email templates
        # TODO: Queue emails for batch sending
        # TODO: Handle email delivery status
        # TODO: Retry on failure

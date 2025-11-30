"""
Notification Listener - PLACEHOLDER
Handle notification sending
"""
import logging
from typing import Dict, Any

from app.events.base_listener import BaseListener

logger = logging.getLogger(__name__)


class NotificationListener(BaseListener):
    """
    Handle notification sending
    PLACEHOLDER - Implement when needed
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
        logger.info(f"[PLACEHOLDER] Sending notification: {data.get('title')}")
        
        # For now, just log it
        # TODO: Implement push notification
        # TODO: Store notification in database
        # TODO: Send via WebSocket if user online
        # TODO: Send via mobile push notification


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

"""
WebSocket Connection Manager
Handles WebSocket connections, message routing, and broadcasting
"""
import logging
from typing import Dict, List, Optional
from fastapi import WebSocket
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time communication
    
    Features:
    - User-based connection management
    - Personal messages to specific users
    - Group broadcasting
    - Connection tracking and cleanup
    """
    
    def __init__(self):
        # user_id → list of websocket connections (support multiple tabs/devices)
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Track connection metadata
        self.connection_info: Dict[int, Dict] = {}
    
    async def connect(self, user_id: int, websocket: WebSocket, metadata: Optional[Dict] = None):
        """
        Accept and register a new WebSocket connection
        
        Args:
            user_id: User ID
            websocket: WebSocket instance
            metadata: Optional connection metadata (device info, etc.)
        """
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
            self.connection_info[user_id] = {
                'connected_at': datetime.now(timezone.utc),
                'connection_count': 0,
                'metadata': metadata or {}
            }
        
        self.active_connections[user_id].append(websocket)
        self.connection_info[user_id]['connection_count'] = len(self.active_connections[user_id])
        
        logger.info(f"✅ User {user_id} connected via WebSocket. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, user_id: int, websocket: WebSocket):
        """
        Remove a WebSocket connection
        
        Args:
            user_id: User ID
            websocket: WebSocket instance to remove
        """
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                
                # Clean up if no more connections
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    del self.connection_info[user_id]
                    logger.info(f"🔌 User {user_id} fully disconnected (no active connections)")
                else:
                    self.connection_info[user_id]['connection_count'] = len(self.active_connections[user_id])
                    logger.info(f"🔌 User {user_id} connection closed. Remaining: {len(self.active_connections[user_id])}")
            except ValueError:
                logger.warning(f"⚠️ Tried to disconnect non-existent connection for user {user_id}")
    
    def is_online(self, user_id: int) -> bool:
        """Check if a user has any active connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_online_users(self) -> List[int]:
        """Get list of all online user IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self, user_id: int) -> int:
        """Get number of active connections for a user"""
        return len(self.active_connections.get(user_id, []))
    
    async def send_personal_message(self, user_id: int, message: dict, exclude_connection: Optional[WebSocket] = None):
        """
        Send a message to all connections of a specific user
        
        Args:
            user_id: Target user ID
            message: Message dictionary to send as JSON
            exclude_connection: Optional connection to exclude (e.g., sender's own connection)
        """
        if user_id not in self.active_connections:
            logger.debug(f"📭 User {user_id} is offline, message not delivered via WebSocket")
            return
        
        # Add server timestamp
        message['_server_timestamp'] = datetime.now(timezone(timedelta(hours=7))).isoformat()
        
        dead_connections = []
        for connection in self.active_connections[user_id]:
            if connection == exclude_connection:
                continue
            
            try:
                await connection.send_json(message)
                logger.debug(f"📤 Sent message to user {user_id}: {message.get('type', 'unknown')}")
            except Exception as e:
                logger.error(f"❌ Failed to send message to user {user_id}: {str(e)}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(user_id, connection)
    
    async def broadcast_to_group(self, user_ids: List[int], message: dict, exclude_user_id: Optional[int] = None):
        """
        Broadcast a message to multiple users
        
        Args:
            user_ids: List of user IDs to send to
            message: Message dictionary to send as JSON
            exclude_user_id: Optional user ID to exclude from broadcast (e.g., message sender)
        """
        logger.info(f"📢 Broadcasting to {len(user_ids)} users (excluding {exclude_user_id})")
        
        for user_id in user_ids:
            if user_id == exclude_user_id:
                continue
            await self.send_personal_message(user_id, message)
    
    async def send_to_study_group(self, group_id: int, message: dict, exclude_user_id: Optional[int] = None):
        """
        Send message to all online members of a study group
        This is a helper that will be called from the API
        
        Args:
            group_id: Study group ID
            message: Message to broadcast
            exclude_user_id: User to exclude (typically the sender)
        """
        # This will be populated by the API endpoint with actual member user_ids
        message['group_id'] = group_id
        logger.info(f"📢 Sending to study group {group_id}")
    
    async def notify_user(self, user_id: int, notification_type: str, data: dict):
        """
        Send a notification to a user
        
        Args:
            user_id: Target user ID
            notification_type: Type of notification (e.g., 'new_message', 'session_update')
            data: Notification data
        """
        message = {
            'type': 'notification',
            'notification_type': notification_type,
            'data': data,
            'timestamp': datetime.now(timezone(timedelta(hours=7))).isoformat()
        }
        await self.send_personal_message(user_id, message)
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            'total_online_users': len(self.active_connections),
            'total_connections': sum(len(conns) for conns in self.active_connections.values()),
            'online_user_ids': self.get_online_users()
        }


# Global singleton instance
manager = ConnectionManager()

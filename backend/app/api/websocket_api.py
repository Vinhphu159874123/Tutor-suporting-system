"""
WebSocket API Endpoints
Real-time communication via WebSocket
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.database import User, StudyGroupMember, StudyGroupMessage
from app.websocket.manager import manager
from datetime import datetime, timezone, timedelta

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_current_user_from_token(token: str, db: AsyncSession) -> Optional[User]:
    """
    Validate token and return user (for WebSocket authentication)
    """
    try:
        from jose import jwt, JWTError
        from app.core.config import settings
        
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        email: str = payload.get("sub")
        if email is None:
            logger.error("No email in token payload")
            return None
        
        # Get user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user is None or not user.is_active:
            logger.error(f"User not found or inactive: {email}")
            return None
        
        return user
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Main WebSocket endpoint for real-time communication
    
    Authentication: Via token query parameter
    URL: ws://localhost:8000/ws?token=<jwt_token>
    
    Message Types:
    - ping: Keep-alive ping
    - chat_message: Send chat message to study group
    - typing: Typing indicator
    """
    # Authenticate user
    user = await get_current_user_from_token(token, db)
    if not user:
        logger.warning("❌ WebSocket authentication failed")
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    user_id = user.user_id
    
    # Connect user
    await manager.connect(user_id, websocket, metadata={
        'user_name': user.full_name,
        'email': user.email
    })
    
    # Send welcome message
    await websocket.send_json({
        'type': 'connected',
        'message': 'WebSocket connection established',
        'user_id': user_id,
        'user_name': user.full_name
    })
    
    # Broadcast user online status to their groups
    await broadcast_online_status(user_id, True, db)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            message_type = data.get('type')
            logger.info(f"📨 Received from user {user_id}: {message_type}")
            
            # Handle different message types
            if message_type == 'ping':
                # Respond to keep-alive ping
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': datetime.now(timezone(timedelta(hours=7))).isoformat()
                })
            
            elif message_type == 'chat_message':
                # Handle chat message
                await handle_chat_message(data, user, db, websocket)
            
            elif message_type == 'typing':
                # Handle typing indicator
                await handle_typing_indicator(data, user, db)
            
            else:
                logger.warning(f"⚠️ Unknown message type: {message_type}")
                await websocket.send_json({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                })
    
    except WebSocketDisconnect:
        logger.info(f"🔌 User {user_id} disconnected")
        manager.disconnect(user_id, websocket)
        # Broadcast user offline status if fully disconnected
        if not manager.is_online(user_id):
            await broadcast_online_status(user_id, False, db)
    except Exception as e:
        logger.error(f"❌ WebSocket error for user {user_id}: {str(e)}", exc_info=True)
        manager.disconnect(user_id, websocket)
        # Broadcast user offline status if fully disconnected
        if not manager.is_online(user_id):
            await broadcast_online_status(user_id, False, db)


async def broadcast_online_status(user_id: int, is_online: bool, db: AsyncSession):
    """
    Broadcast user's online status to all their study groups
    """
    try:
        # Get all groups the user is in
        groups_result = await db.execute(
            select(StudyGroupMember.group_id).where(
                StudyGroupMember.user_id == user_id,
                StudyGroupMember.status == 'active'
            )
        )
        group_ids = [row[0] for row in groups_result.all()]
        
        # For each group, broadcast to all members
        for group_id in group_ids:
            members_result = await db.execute(
                select(StudyGroupMember.user_id).where(
                    StudyGroupMember.group_id == group_id,
                    StudyGroupMember.status == 'active'
                )
            )
            member_user_ids = [row[0] for row in members_result.all()]
            
            # Broadcast online status update
            status_message = {
                'type': 'user_status',
                'data': {
                    'user_id': user_id,
                    'group_id': group_id,
                    'is_online': is_online
                }
            }
            
            await manager.broadcast_to_group(member_user_ids, status_message)
    except Exception as e:
        logger.error(f"Error broadcasting online status: {e}")


async def handle_chat_message(data: dict, user: User, db: AsyncSession, websocket: WebSocket):
    """
    Handle incoming chat message
    Save to database and broadcast to group members
    """
    # Extract data from nested structure
    message_data = data.get('data', {})
    group_id = message_data.get('group_id')
    message_text = message_data.get('message_text', '').strip()
    
    if not group_id or not message_text:
        await websocket.send_json({
            'type': 'error',
            'message': 'Missing group_id or message_text'
        })
        return
    
    # Check if user is a member of the group
    member_check = await db.execute(
        select(StudyGroupMember).where(
            StudyGroupMember.group_id == group_id,
            StudyGroupMember.user_id == user.user_id,
            StudyGroupMember.status == 'active'
        )
    )
    
    if not member_check.scalar_one_or_none():
        await websocket.send_json({
            'type': 'error',
            'message': 'You are not a member of this group'
        })
        return
    
    # Save message to database
    vietnam_tz = timezone(timedelta(hours=7))
    message = StudyGroupMessage(
        group_id=group_id,
        user_id=user.user_id,
        message_text=message_text,
        created_at=datetime.now(vietnam_tz)
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    # Get all group members
    members_result = await db.execute(
        select(StudyGroupMember.user_id).where(
            StudyGroupMember.group_id == group_id,
            StudyGroupMember.status == 'active'
        )
    )
    member_user_ids = [row[0] for row in members_result.all()]
    
    # Broadcast to all group members (including sender for confirmation)
    broadcast_message = {
        'type': 'new_message',
        'data': {
            'message_id': message.message_id,
            'group_id': message.group_id,
            'user_id': message.user_id,
            'user_name': user.full_name,
            'message_text': message.message_text,
            'created_at': message.created_at.isoformat(),
            'is_deleted': message.is_deleted
        }
    }
    
    await manager.broadcast_to_group(member_user_ids, broadcast_message)
    
    logger.info(f"✅ Message {message.message_id} broadcasted to group {group_id}")


async def handle_typing_indicator(data: dict, user: User, db: AsyncSession):
    """
    Handle typing indicator
    Broadcast to group members that user is typing
    """
    # Extract data from nested structure
    message_data = data.get('data', {})
    group_id = message_data.get('group_id')
    is_typing = message_data.get('is_typing', True)
    
    if not group_id:
        return
    
    # Check membership
    member_check = await db.execute(
        select(StudyGroupMember).where(
            StudyGroupMember.group_id == group_id,
            StudyGroupMember.user_id == user.user_id,
            StudyGroupMember.status == 'active'
        )
    )
    
    if not member_check.scalar_one_or_none():
        return
    
    # Get all group members
    members_result = await db.execute(
        select(StudyGroupMember.user_id).where(
            StudyGroupMember.group_id == group_id,
            StudyGroupMember.status == 'active'
        )
    )
    member_user_ids = [row[0] for row in members_result.all()]
    
    # Broadcast typing indicator (exclude sender)
    await manager.broadcast_to_group(
        member_user_ids,
        {
            'type': 'user_typing',
            'data': {
                'group_id': group_id,
                'user_id': user.user_id,
                'user_name': user.full_name,
                'is_typing': is_typing
            }
        },
        exclude_user_id=user.user_id
    )


@router.get("/ws/stats")
async def get_websocket_stats(current_user: User = Depends(get_current_user)):
    """
    Get WebSocket connection statistics (admin only)
    """
    return manager.get_stats()


@router.get("/ws/status/{user_id}")
async def check_user_online_status(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Check if a specific user is online
    """
    return {
        'user_id': user_id,
        'is_online': manager.is_online(user_id),
        'connection_count': manager.get_connection_count(user_id)
    }


@router.get("/ws/group/{group_id}/online")
async def get_group_online_users(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of online users in a study group
    """
    # Get all group members
    members_result = await db.execute(
        select(StudyGroupMember).where(
            StudyGroupMember.group_id == group_id,
            StudyGroupMember.status == 'active'
        )
    )
    members = members_result.scalars().all()
    
    # Check which members are online
    online_users = []
    for member in members:
        if manager.is_online(member.user_id):
            # Get user info
            user_result = await db.execute(
                select(User).where(User.user_id == member.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                online_users.append({
                    'user_id': user.user_id,
                    'full_name': user.full_name,
                    'is_online': True
                })
    
    return {
        'group_id': group_id,
        'online_count': len(online_users),
        'online_users': online_users
    }

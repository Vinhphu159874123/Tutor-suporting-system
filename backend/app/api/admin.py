from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List

from app.schemas.admin import UserManagement, SystemConfig, ApprovalWorkflow
from app.services.admin_service import AdminService
from app.core.dependencies import get_admin_service, get_current_user
from app.core.database import get_db
from app.models.database import User, Session as SessionModel

router = APIRouter()

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.get("/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users - admin only"""
    if current_user.role not in ['admin', 'coordinator']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [
        {
            "user_id": u.user_id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "created_at": u.created_at
        }
        for u in users
    ]

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """Get system statistics - admin only"""
    if current_user.role not in ['admin', 'coordinator']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Count users by role
    total_users = await db.execute(select(func.count(User.user_id)))
    students = await db.execute(select(func.count(User.user_id)).where(User.role == 'student'))
    tutors = await db.execute(select(func.count(User.user_id)).where(User.role == 'tutor'))
    
    # Count sessions
    total_sessions = await db.execute(select(func.count(SessionModel.session_id)))
    
    # Average rating
    from app.models.database import SessionFeedback
    avg_rating_result = await db.execute(select(func.avg(SessionFeedback.rating)))
    avg_rating = avg_rating_result.scalar()
    
    return {
        "total_users": total_users.scalar() or 0,
        "total_students": students.scalar() or 0,
        "total_tutors": tutors.scalar() or 0,
        "total_sessions": total_sessions.scalar() or 0,
        "average_rating": round(float(avg_rating), 1) if avg_rating else 0.0
    }

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Update user role - PLACEHOLDER"""
    return {"message": "Update user role - Implementation pending"}

@router.get("/registrations")
async def get_pending_registrations():
    """Get pending registrations - PLACEHOLDER"""
    return {"message": "Get pending registrations - Implementation pending"}

@router.put("/registrations/{registration_id}/approve")
async def approve_registration(registration_id: int):
    """Approve a pending registration - PLACEHOLDER"""
    return {"message": "Approve registration - Implementation pending"}

@router.get("/config")
async def get_system_config():
    """Get system configuration - PLACEHOLDER"""
    return {"message": "Get system config - Implementation pending"}

@router.put("/config")
async def update_system_config():
    """Update system configuration - PLACEHOLDER"""
    return {"message": "Update system config - Implementation pending"}

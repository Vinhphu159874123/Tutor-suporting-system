from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, any_
from sqlalchemy.orm import joinedload
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
    include_inactive: bool = False,  # Add parameter to show inactive users
    role: str = None,  # Filter by role
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users - admin only"""
    # Check if user has admin/coordinator role
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'admin' not in user_roles and 'coordinator' not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Filter active users by default
    query = select(User).options(joinedload(User.student))
    if not include_inactive:
        query = query.where(User.is_active == True)
    
    # Filter by role if provided (use ANY for PostgreSQL array)
    if role:
        query = query.where(role == any_(User.role))
    
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.unique().scalars().all()
    
    user_list = []
    for u in users:
        user_data = {
            "user_id": u.user_id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "created_at": u.created_at,
            "phone": u.phone,
            "faculty": None,
            "major": None,
            "student_code": None
        }
        
        # Get student info if user has student relationship (already loaded)
        if u.student:
            user_data["student_code"] = u.student.student_code
            user_data["faculty"] = u.student.faculty
            user_data["major"] = u.student.major
        
        user_list.append(user_data)
    
    return user_list

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """Get system statistics - admin only"""
    # Check if user has admin/coordinator role
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'admin' not in user_roles and 'coordinator' not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Count users by role
    total_users = await db.execute(select(func.count(User.user_id)))
    # Use ANY operator for PostgreSQL array
    students = await db.execute(select(func.count(User.user_id)).where('student' == any_(User.role)))
    tutors = await db.execute(select(func.count(User.user_id)).where('tutor' == any_(User.role)))
    
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

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user - admin only"""
    # Check if user has admin role (support array)
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'admin' not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Find user
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete - just deactivate
    user.is_active = False
    await db.commit()
    
    return {"message": "User deleted successfully"}

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user - admin only"""
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'admin' not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Find user
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update allowed fields
    if 'full_name' in user_data:
        user.full_name = user_data['full_name']
    if 'phone' in user_data:
        user.phone = user_data['phone']
    if 'role' in user_data:
        user.role = user_data['role']
    if 'is_active' in user_data:
        user.is_active = user_data['is_active']
    
    await db.commit()
    
    return {"message": "User updated successfully"}

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

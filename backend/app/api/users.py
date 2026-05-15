"""Users API — thin controller, delegates to UsersService"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.dependencies import get_current_user, get_users_service
from app.models.database import User
from app.services.users_service import UsersService
from app.schemas.user import UserProfileUpdate as UserUpdate, UserProfileResponse as UserResponse

router = APIRouter()

# --- DI helper ---
_svc = get_users_service

# --- Routes ---
@router.get("/search")
async def search_users(
    query: str, limit: int = 10,
    current_user: User = Depends(get_current_user),
    svc: UsersService = Depends(_svc),
):
    return await svc.search_users(query, limit)

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    svc: UsersService = Depends(_svc),
):
    return await svc.get_profile(current_user)

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    svc: UsersService = Depends(_svc),
):
    return await svc.update_profile(current_user, user_update.model_dump())

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0, limit: int = 100, role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    svc: UsersService = Depends(_svc),
):
    roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'admin' not in roles and 'coordinator' not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await svc.get_users_list(skip=skip, limit=limit, role=role)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    svc: UsersService = Depends(_svc),
):
    roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if current_user.user_id != user_id and 'admin' not in roles and 'coordinator' not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await svc.get_user_by_id(user_id)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    svc: UsersService = Depends(_svc),
):
    roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'admin' not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await svc.soft_delete_user(user_id)

@router.get("/stats/dashboard")
async def get_user_dashboard_stats(
    mode: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    svc: UsersService = Depends(_svc),
):
    return await svc.get_dashboard_stats(current_user, mode)

@router.get("/stats/coordinator")
async def get_coordinator_dashboard_stats(
    current_user: User = Depends(get_current_user),
    svc: UsersService = Depends(_svc),
):
    roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    if 'coordinator' not in roles and 'admin' not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await svc.get_coordinator_stats()

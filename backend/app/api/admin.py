"""Admin API — thin controller, delegates to AdminService"""
from fastapi import APIRouter, Depends
from typing import Optional
from app.core.dependencies import get_current_user, get_admin_service
from app.models.database import User
from app.services.admin_service import AdminService

router = APIRouter()

@router.get("/users")
async def get_all_users(
    skip: int = 0, limit: int = 100,
    include_inactive: bool = False, role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    svc: AdminService = Depends(get_admin_service),
):
    svc.check_admin_or_coordinator(current_user)
    return await svc.get_all_users(skip=skip, limit=limit,
                                   include_inactive=include_inactive, role=role)

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_user),
    svc: AdminService = Depends(get_admin_service),
):
    svc.check_admin_or_coordinator(current_user)
    return await svc.get_stats()

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    svc: AdminService = Depends(get_admin_service),
):
    svc.check_admin_only(current_user)
    return await svc.soft_delete_user(user_id)

@router.put("/users/{user_id}")
async def update_user(
    user_id: int, user_data: dict,
    current_user: User = Depends(get_current_user),
    svc: AdminService = Depends(get_admin_service),
):
    svc.check_admin_only(current_user)
    return await svc.update_user(user_id, user_data)

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int, role_data: dict,
    current_user: User = Depends(get_current_user),
    svc: AdminService = Depends(get_admin_service),
):
    svc.check_admin_only(current_user)
    return await svc.update_user_role(user_id, role_data.get('role'))

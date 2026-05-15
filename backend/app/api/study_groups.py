"""Study Groups API — thin controller, delegates to StudyGroupsService"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from app.core.dependencies import get_current_user, get_study_groups_service
from app.models.database import User
from app.services.study_groups_service import StudyGroupsService
from app.schemas.study_group import (
    CreateStudyGroupRequest, CreateActivityRequest,
    AddMemberRequest, SendMessageRequest,
)

router = APIRouter()

_svc = get_study_groups_service

# --- Group CRUD ---
@router.get("/")
async def get_study_groups(
    skip: int = Query(0, ge=0), limit: int = Query(100, le=100),
    subject_id: Optional[int] = Query(None), is_public: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.get_groups(current_user.user_id, skip=skip, limit=limit,
                                subject_id=subject_id, is_public=is_public)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_study_group(
    data: CreateStudyGroupRequest,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.create_group(current_user, data.model_dump())

@router.get("/{group_id}")
async def get_study_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.get_group(group_id, current_user.user_id)

# --- Membership ---
@router.post("/{group_id}/members")
async def add_member_to_group(
    group_id: int, request: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.add_member(group_id, current_user, request.user_id)

@router.post("/{group_id}/join")
async def join_study_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.join_group(group_id, current_user)

@router.post("/{group_id}/leave")
async def leave_study_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.leave_group(group_id, current_user)

# --- Activities ---
@router.post("/{group_id}/activities", status_code=status.HTTP_201_CREATED)
async def create_activity(
    group_id: int, data: CreateActivityRequest,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.create_activity(group_id, current_user, data.model_dump())

# --- Materials ---
@router.post("/{group_id}/materials", status_code=status.HTTP_201_CREATED)
async def create_material(
    group_id: int,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
    file: Optional[UploadFile] = File(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file_url: Optional[str] = Form(None),
    file_type: Optional[str] = Form(None),
):
    return await svc.create_material(group_id, current_user, file=file,
                                      title=title, description=description,
                                      file_url=file_url, file_type=file_type)

@router.get("/{group_id}/materials/{material_id}")
async def download_material(
    group_id: int, material_id: int,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    m = await svc.download_material(group_id, material_id)
    return Response(content=m.file_data,
                    media_type=m.file_type or "application/octet-stream",
                    headers={"Content-Disposition": f'inline; filename="{m.title}"'})

@router.put("/{group_id}/materials/{material_id}")
async def update_material(
    group_id: int, material_id: int,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
):
    return await svc.update_material(group_id, material_id, title=title, description=description)

@router.delete("/{group_id}/materials/{material_id}")
async def delete_material(
    group_id: int, material_id: int,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.delete_material(group_id, material_id, current_user)

@router.get("/{group_id}/materials")
async def get_materials(
    group_id: int,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.get_materials(group_id)

# --- Chat ---
@router.post("/{group_id}/messages")
async def send_message(
    group_id: int, request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.send_message(group_id, current_user, request.message_text)

@router.get("/{group_id}/messages")
async def get_messages(
    group_id: int,
    limit: int = Query(50, le=100), before_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.get_messages(group_id, current_user.user_id, limit=limit, before_id=before_id)

@router.delete("/{group_id}/messages/{message_id}")
async def delete_message(
    group_id: int, message_id: int,
    current_user: User = Depends(get_current_user),
    svc: StudyGroupsService = Depends(_svc),
):
    return await svc.delete_message(group_id, message_id, current_user)

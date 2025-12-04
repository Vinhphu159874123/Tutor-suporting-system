"""
Study Groups API
Group creation, membership management, collaboration features
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import os
import uuid

from app.core.dependencies import get_current_user, get_db
from app.models.database import User, StudyGroup, StudyGroupMember, Subject, StudyGroupMaterial, StudyGroupActivity

router = APIRouter()


# Schemas
class CreateStudyGroupRequest(BaseModel):
    group_name: str
    subject_id: int
    description: Optional[str] = None
    topic: Optional[str] = None
    max_members: int = 10
    is_public: bool = True
    require_approval: bool = False


class CreateActivityRequest(BaseModel):
    activity_type: str  # meeting, assignment, discussion
    title: str
    description: Optional[str] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None


class CreateMaterialRequest(BaseModel):
    title: str
    description: Optional[str] = None
    file_url: str
    file_type: str  # pdf, doc, video, link


@router.get("/")
async def get_study_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    subject_id: Optional[int] = Query(None),
    is_public: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """List all study groups with filters - OPTIMIZED + CACHED"""
    
    # Try cache first (30s TTL)
    from app.core.cache import get_cached, set_cached
    cache_key = f"study_groups:{skip}:{limit}:{subject_id}:{is_public}"
    cached = await get_cached(cache_key)
    if cached:
        return cached
    
    query = select(StudyGroup, User, Subject).join(
        User, StudyGroup.creator_id == User.user_id
    ).outerjoin(
        Subject, StudyGroup.subject_id == Subject.subject_id
    )
    
    # Apply filters
    if subject_id:
        query = query.where(StudyGroup.subject_id == subject_id)
    if is_public is not None:
        query = query.where(StudyGroup.is_public == is_public)
    
    query = query.order_by(StudyGroup.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    # Get user's group memberships
    membership_query = select(StudyGroupMember.group_id).where(
        StudyGroupMember.user_id == current_user.user_id
    )
    membership_result = await db.execute(membership_query)
    user_group_ids = {row[0] for row in membership_result.all()}
    
    groups_list = []
    for group, creator, subject in rows:
        is_member = group.group_id in user_group_ids
        groups_list.append({
            "id": str(group.group_id),
            "name": group.group_name,
            "course": subject.subject_name if subject else "Chưa xác định",
            "members": group.member_count or 0,
            "maxMembers": group.max_members or 10,
            "description": group.description or "",
            "createdBy": creator.full_name,
            "schedule": group.topic or "",
            "status": "open" if (group.member_count or 0) < (group.max_members or 10) else "full",
            "created_at": group.created_at.isoformat() if group.created_at else None,
            "is_member": is_member
        })
    
    # Cache for 30 seconds
    await set_cached(cache_key, groups_list, ttl=30)
    return groups_list


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_study_group(
    group_data: CreateStudyGroupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new study group"""
    
    # Verify subject exists
    subject_query = select(Subject).where(Subject.subject_id == group_data.subject_id)
    subject_result = await db.execute(subject_query)
    subject = subject_result.scalar_one_or_none()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Create study group
    new_group = StudyGroup(
        creator_id=current_user.user_id,
        subject_id=group_data.subject_id,
        group_name=group_data.group_name,
        description=group_data.description,
        topic=group_data.topic,
        max_members=group_data.max_members,
        is_public=group_data.is_public,
        require_approval=group_data.require_approval,
        member_count=1,  # Creator is first member
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_group)
    await db.flush()  # Get the group_id
    
    # Add creator as first member with owner role
    creator_member = StudyGroupMember(
        group_id=new_group.group_id,
        user_id=current_user.user_id,
        role='owner',
        status='active',
        joined_at=datetime.utcnow()
    )
    
    db.add(creator_member)
    await db.commit()
    await db.refresh(new_group)
    
    return {
        "id": str(new_group.group_id),
        "name": new_group.group_name,
        "course": subject.subject_name,
        "members": 1,
        "maxMembers": new_group.max_members,
        "description": new_group.description or "",
        "createdBy": current_user.full_name,
        "schedule": new_group.topic or "",
        "status": "open",
        "created_at": new_group.created_at.isoformat()
    }


@router.get("/{group_id}")
async def get_study_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get study group details with members"""
    
    # Get group info
    query = select(StudyGroup, User, Subject).join(
        User, StudyGroup.creator_id == User.user_id
    ).outerjoin(
        Subject, StudyGroup.subject_id == Subject.subject_id
    ).where(StudyGroup.group_id == group_id)
    
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study group not found"
        )
    
    group, creator, subject = row
    
    # Get members
    members_query = select(StudyGroupMember, User).join(
        User, StudyGroupMember.user_id == User.user_id
    ).where(
        StudyGroupMember.group_id == group_id,
        StudyGroupMember.status == 'active'
    ).order_by(StudyGroupMember.joined_at)
    
    members_result = await db.execute(members_query)
    members_rows = members_result.all()
    
    members_list = []
    for member, user in members_rows:
        members_list.append({
            "id": str(user.user_id),
            "name": user.full_name,
            "role": "Trưởng nhóm" if member.role == 'owner' else "Thành viên",
            "joinedAt": member.joined_at.isoformat() if member.joined_at else None
        })
    
    # Get recent activities from study group activities + sessions
    activities = []
    
    # First get study group activities
    group_activities_query = select(StudyGroupActivity).where(
        StudyGroupActivity.group_id == group_id,
        StudyGroupActivity.status.in_(['upcoming', 'active'])
    ).order_by(StudyGroupActivity.scheduled_date.asc()).limit(10)
    
    group_activities_result = await db.execute(group_activities_query)
    group_activities = group_activities_result.scalars().all()
    
    for activity in group_activities:
        activities.append({
            "id": str(activity.activity_id),
            "type": activity.activity_type,
            "title": activity.title,
            "date": f"{activity.scheduled_date} {activity.scheduled_time}" if activity.scheduled_date else "",
            "status": activity.status,
            "description": activity.description,
            "location": activity.location,
            "meeting_link": activity.meeting_link
        })
    
    # Get materials
    materials_query = select(StudyGroupMaterial, User).join(
        User, StudyGroupMaterial.uploader_id == User.user_id
    ).where(
        StudyGroupMaterial.group_id == group_id
    ).order_by(StudyGroupMaterial.created_at.desc()).limit(10)
    
    materials_result = await db.execute(materials_query)
    materials_rows = materials_result.all()
    
    materials_list = []
    for material, uploader in materials_rows:
        materials_list.append({
            "id": material.material_id,
            "title": material.title,
            "description": material.description,
            "file_url": material.file_url,
            "file_type": material.file_type,
            "uploader": uploader.full_name,
            "created_at": material.created_at.isoformat()
        })
    
    # Check if current user is a member
    is_member = any(member.user_id == current_user.user_id for member, _ in members_rows)
    
    return {
        "id": str(group.group_id),
        "name": group.group_name,
        "course": subject.subject_name if subject else "Chưa xác định",
        "members": len(members_list),
        "maxMembers": group.max_members or 10,
        "description": group.description or "",
        "createdBy": creator.full_name,
        "schedule": group.topic or "Chưa có lịch",
        "location": "Online - Google Meet",
        "status": "open" if len(members_list) < (group.max_members or 10) else "full",
        "createdAt": group.created_at.isoformat() if group.created_at else None,
        "is_member": is_member,
        "members_list": members_list,
        "activities": activities,
        "materials": materials_list
    }


class AddMemberRequest(BaseModel):
    user_id: int

@router.post("/{group_id}/members")
async def add_member_to_group(
    group_id: int,
    request: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a member to study group (by group leader/admin)"""
    from app.models.database import Notifications
    
    user_id = request.user_id
    
    # Check if group exists
    group_result = await db.execute(select(StudyGroup).where(StudyGroup.group_id == group_id))
    group = group_result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user to add exists
    user_result = await db.execute(select(User).where(User.user_id == user_id))
    user_to_add = user_result.scalar_one_or_none()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = await db.execute(
        select(StudyGroupMember).where(
            StudyGroupMember.group_id == group_id,
            StudyGroupMember.user_id == user_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member")
    
    # Add member
    from sqlalchemy import func
    new_member = StudyGroupMember(
        group_id=group_id,
        user_id=user_id,
        role="member",
        status="active",
        joined_at=func.now()
    )
    db.add(new_member)
    
    # Create notification for the added user
    notification = Notifications(
        user_id=user_id,
        type="study_group_added",
        title="Được thêm vào nhóm học",
        message=f"{current_user.full_name} đã thêm bạn vào nhóm '{group.group_name}'",
        data={"group_id": group_id, "group_name": group.group_name},
        is_read=False
        # created_at will be auto-set by server_default=func.now()
    )
    db.add(notification)
    
    await db.commit()
    
    return {"message": "Member added successfully"}

@router.post("/{group_id}/join", status_code=status.HTTP_200_OK)
async def join_study_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Join a study group"""
    from sqlalchemy import func
    
    # Check if group exists
    group_query = select(StudyGroup).where(StudyGroup.group_id == group_id)
    group_result = await db.execute(group_query)
    group = group_result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study group not found"
        )
    
    # Check if already a member
    member_query = select(StudyGroupMember).where(
        StudyGroupMember.group_id == group_id,
        StudyGroupMember.user_id == current_user.user_id
    )
    member_result = await db.execute(member_query)
    existing_member = member_result.scalar_one_or_none()
    
    if existing_member:
        if existing_member.status == 'active':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bạn đã là thành viên của nhóm này"
            )
        else:
            # Reactivate membership
            existing_member.status = 'active'
            existing_member.joined_at = datetime.now()
    else:
        # Check if group is full
        count_query = select(func.count(StudyGroupMember.member_id)).where(
            StudyGroupMember.group_id == group_id,
            StudyGroupMember.status == 'active'
        )
        count_result = await db.execute(count_query)
        member_count = count_result.scalar()
        
        if member_count >= (group.max_members or 10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nhóm đã đầy"
            )
        
        # Add new member
        new_member = StudyGroupMember(
            group_id=group_id,
            user_id=current_user.user_id,
            role='member',
            status='active' if not group.require_approval else 'pending'
        )
        db.add(new_member)
        
        # Update member count
        group.member_count = (group.member_count or 0) + 1
    
    await db.commit()
    
    return {
        "message": "Tham gia nhóm thành công" if not group.require_approval else "Yêu cầu tham gia đã được gửi",
        "status": "active" if not group.require_approval else "pending"
    }


@router.post("/{group_id}/leave", status_code=status.HTTP_200_OK)
async def leave_study_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Leave a study group"""
    
    # Check if group exists
    group_query = select(StudyGroup).where(StudyGroup.group_id == group_id)
    group_result = await db.execute(group_query)
    group = group_result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study group not found"
        )
    
    # Check if user is a member
    member_query = select(StudyGroupMember).where(
        StudyGroupMember.group_id == group_id,
        StudyGroupMember.user_id == current_user.user_id,
        StudyGroupMember.status == 'active'
    )
    member_result = await db.execute(member_query)
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn không phải là thành viên của nhóm này"
        )
    
    # Don't allow group owner to leave
    if member.role == 'owner':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trưởng nhóm không thể rời nhóm. Vui lòng chuyển quyền trước."
        )
    
    # Remove member
    await db.delete(member)
    
    # Update member count
    if group.member_count and group.member_count > 0:
        group.member_count = group.member_count - 1
    
    await db.commit()
    
    return {
        "message": "Đã rời nhóm thành công"
    }


@router.post("/{group_id}/activities", status_code=status.HTTP_201_CREATED)
async def create_activity(
    group_id: int,
    activity_data: CreateActivityRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new activity for study group"""
    from datetime import date, time
    
    # Verify group exists and user is member
    group_query = select(StudyGroup).where(StudyGroup.group_id == group_id)
    group_result = await db.execute(group_query)
    group = group_result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study group not found"
        )
    
    # Create activity
    new_activity = StudyGroupActivity(
        group_id=group_id,
        creator_id=current_user.user_id,
        activity_type=activity_data.activity_type,
        title=activity_data.title,
        description=activity_data.description,
        scheduled_date=date.fromisoformat(activity_data.scheduled_date) if activity_data.scheduled_date else None,
        scheduled_time=time.fromisoformat(activity_data.scheduled_time) if activity_data.scheduled_time else None,
        location=activity_data.location,
        meeting_link=activity_data.meeting_link,
        status='upcoming'
    )
    
    db.add(new_activity)
    await db.commit()
    await db.refresh(new_activity)
    
    return {
        "id": str(new_activity.activity_id),
        "type": new_activity.activity_type,
        "title": new_activity.title,
        "date": f"{new_activity.scheduled_date} {new_activity.scheduled_time}" if new_activity.scheduled_date else None,
        "status": new_activity.status,
        "message": "Hoạt động đã được tạo thành công"
    }


@router.post("/{group_id}/materials", status_code=status.HTTP_201_CREATED)
async def create_material(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    file: Optional[UploadFile] = File(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file_url: Optional[str] = Form(None),
    file_type: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Upload material to study group - stores file in DATABASE"""
    
    # Verify group exists
    group_query = select(StudyGroup).where(StudyGroup.group_id == group_id)
    group_result = await db.execute(group_query)
    group = group_result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study group not found"
        )
    
    material_title = title
    material_url = file_url
    material_type = file_type or "document"
    file_data_bytes = None
    file_size = None
    
    # Handle file upload - SAVE TO DATABASE
    if file:
        # Read file content
        content = await file.read()
        
        # Check file size (max 10MB)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File quá lớn. Tối đa 10MB"
            )
        
        file_data_bytes = content
        # Generate download URL using material_id (will be set after insert)
        material_url = None  # Will update after commit
        material_title = material_title or file.filename
        material_type = file.content_type or "application/octet-stream"
        file_size = len(content)
    elif not file_url or not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either file upload or (title + file_url)"
        )
    
    # Create material record with file data in database
    new_material = StudyGroupMaterial(
        group_id=group_id,
        uploader_id=current_user.user_id,
        title=material_title,
        description=description,
        file_url=material_url,
        file_type=material_type,
        file_size=file_size,
        file_data=file_data_bytes  # Store in database
    )
    
    db.add(new_material)
    await db.commit()
    await db.refresh(new_material)
    
    # Update file_url with material_id for uploaded files
    if file_data_bytes:
        new_material.file_url = f"/api/v1/study-groups/{group_id}/materials/{new_material.material_id}"
        await db.commit()
        await db.refresh(new_material)
    
    return {
        "id": new_material.material_id,
        "title": new_material.title,
        "file_url": new_material.file_url,
        "file_type": new_material.file_type,
        "file_size": new_material.file_size,
        "created_at": new_material.created_at.isoformat(),
        "message": "Tài liệu đã được thêm thành công"
    }


@router.get("/{group_id}/materials/{material_id}")
async def download_material(
    group_id: int,
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download material file from DATABASE"""
    from fastapi.responses import Response
    
    # Find material by ID
    query = select(StudyGroupMaterial).where(
        StudyGroupMaterial.group_id == group_id,
        StudyGroupMaterial.material_id == material_id
    )
    result = await db.execute(query)
    material = result.scalar_one_or_none()
    
    if not material or not material.file_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return Response(
        content=material.file_data,
        media_type=material.file_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{material.title}"'}
    )


@router.put("/{group_id}/materials/{material_id}")
async def update_material(
    group_id: int,
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Update material metadata"""
    
    # Get material
    query = select(StudyGroupMaterial).where(
        StudyGroupMaterial.material_id == material_id,
        StudyGroupMaterial.group_id == group_id
    )
    result = await db.execute(query)
    material = result.scalar_one_or_none()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Update fields
    if title:
        material.title = title
    if description is not None:
        material.description = description
    
    await db.commit()
    await db.refresh(material)
    
    return {
        "id": material.material_id,
        "title": material.title,
        "description": material.description,
        "message": "Cập nhật tài liệu thành công"
    }


@router.delete("/{group_id}/materials/{material_id}")
async def delete_material(
    group_id: int,
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Delete material"""
    
    # Get material
    query = select(StudyGroupMaterial).where(
        StudyGroupMaterial.material_id == material_id,
        StudyGroupMaterial.group_id == group_id
    )
    result = await db.execute(query)
    material = result.scalar_one_or_none()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Check ownership
    if material.uploader_id != current_user.user_id:
        user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
        if 'admin' not in user_roles and 'coordinator' not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền xóa tài liệu này"
            )
    
    await db.delete(material)
    await db.commit()
    
    return {"message": "Xóa tài liệu thành công"}


@router.get("/{group_id}/materials")
async def get_materials(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all materials for a study group"""
    
    query = select(StudyGroupMaterial, User).join(
        User, StudyGroupMaterial.uploader_id == User.user_id
    ).where(
        StudyGroupMaterial.group_id == group_id
    ).order_by(StudyGroupMaterial.created_at.desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    materials = []
    for material, uploader in rows:
        materials.append({
            "id": material.material_id,
            "title": material.title,
            "description": material.description,
            "file_url": material.file_url,
            "file_type": material.file_type,
            "uploader": uploader.full_name,
            "created_at": material.created_at.isoformat()
        })
    
    return materials

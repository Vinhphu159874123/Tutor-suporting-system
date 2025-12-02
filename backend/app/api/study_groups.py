"""
Study Groups API
Group creation, membership management, collaboration features
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.core.dependencies import get_current_user, get_db
from app.models.database import User, StudyGroup, StudyGroupMember, Subject

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


@router.get("/")
async def get_study_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    subject_id: Optional[int] = Query(None),
    is_public: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """List all study groups with filters"""
    
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
    
    groups_list = []
    for group, creator, subject in rows:
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
            "created_at": group.created_at.isoformat() if group.created_at else None
        })
    
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
        "members_list": members_list,
        "activities": []
    }

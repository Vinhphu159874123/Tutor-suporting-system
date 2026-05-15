"""
Study Group Repository
Database operations for StudyGroup, membership, materials, chat
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.models.database import (
    User, StudyGroup, StudyGroupMember, Subject,
    StudyGroupMaterial, StudyGroupActivity, StudyGroupMessage, Notifications,
)


class StudyGroupRepository:
    """Handle all database operations for StudyGroup module"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_groups_with_details(self, *, skip: int, limit: int,
                                       subject_id: Optional[int], is_public: Optional[bool]) -> list:
        q = (select(StudyGroup, User, Subject)
             .join(User, StudyGroup.creator_id == User.user_id)
             .outerjoin(Subject, StudyGroup.subject_id == Subject.subject_id))
        if subject_id:
            q = q.where(StudyGroup.subject_id == subject_id)
        if is_public is not None:
            q = q.where(StudyGroup.is_public == is_public)
        q = q.order_by(StudyGroup.created_at.desc()).offset(skip).limit(limit)
        return (await self.db.execute(q)).all()

    async def get_user_group_ids(self, user_id: int) -> set:
        rows = (await self.db.execute(
            select(StudyGroupMember.group_id).where(StudyGroupMember.user_id == user_id)
        )).all()
        return {r[0] for r in rows}

    async def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        return (await self.db.execute(
            select(Subject).where(Subject.subject_id == subject_id)
        )).scalar_one_or_none()

    async def create_group(self, group: StudyGroup) -> StudyGroup:
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def create_member(self, member: StudyGroupMember) -> StudyGroupMember:
        self.db.add(member)
        await self.db.commit()
        return member

    async def get_group_by_id(self, group_id: int) -> Optional[StudyGroup]:
        return (await self.db.execute(
            select(StudyGroup).where(StudyGroup.group_id == group_id)
        )).scalar_one_or_none()

    async def get_group_with_details(self, group_id: int):
        return (await self.db.execute(
            select(StudyGroup, User, Subject)
            .join(User, StudyGroup.creator_id == User.user_id)
            .outerjoin(Subject, StudyGroup.subject_id == Subject.subject_id)
            .where(StudyGroup.group_id == group_id)
        )).first()

    async def get_group_members(self, group_id: int) -> list:
        return (await self.db.execute(
            select(StudyGroupMember, User)
            .join(User, StudyGroupMember.user_id == User.user_id)
            .where(StudyGroupMember.group_id == group_id)
            .order_by(StudyGroupMember.joined_at)
        )).all()

    async def get_member(self, group_id: int, user_id: int) -> Optional[StudyGroupMember]:
        return (await self.db.execute(
            select(StudyGroupMember).where(
                StudyGroupMember.group_id == group_id,
                StudyGroupMember.user_id == user_id)
        )).scalar_one_or_none()

    async def create_notification(self, notification: Notifications) -> None:
        self.db.add(notification)

    async def create_activity(self, activity: StudyGroupActivity) -> StudyGroupActivity:
        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def create_material(self, material: StudyGroupMaterial) -> StudyGroupMaterial:
        self.db.add(material)
        await self.db.commit()
        await self.db.refresh(material)
        return material

    async def get_material_by_id(self, material_id: int) -> Optional[StudyGroupMaterial]:
        return (await self.db.execute(
            select(StudyGroupMaterial).where(StudyGroupMaterial.material_id == material_id)
        )).scalar_one_or_none()

    async def get_materials_by_group(self, group_id: int) -> list:
        return (await self.db.execute(
            select(StudyGroupMaterial, User)
            .join(User, StudyGroupMaterial.uploaded_by == User.user_id)
            .where(StudyGroupMaterial.group_id == group_id)
            .order_by(StudyGroupMaterial.uploaded_at.desc())
        )).all()

    async def delete_material(self, material: StudyGroupMaterial) -> None:
        await self.db.delete(material)
        await self.db.commit()

    async def get_messages(self, group_id: int, limit: int, before_id: Optional[int]) -> list:
        q = (select(StudyGroupMessage, User)
             .join(User, StudyGroupMessage.user_id == User.user_id)
             .where(StudyGroupMessage.group_id == group_id))
        if before_id:
            q = q.where(StudyGroupMessage.message_id < before_id)
        return (await self.db.execute(
            q.order_by(StudyGroupMessage.sent_at.desc()).limit(limit)
        )).all()

    async def create_message(self, message: StudyGroupMessage) -> StudyGroupMessage:
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_message_by_id(self, message_id: int) -> Optional[StudyGroupMessage]:
        return (await self.db.execute(
            select(StudyGroupMessage).where(StudyGroupMessage.message_id == message_id)
        )).scalar_one_or_none()

    async def delete_message(self, message: StudyGroupMessage) -> None:
        await self.db.delete(message)
        await self.db.commit()

    # --- Transaction helpers ---
    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def refresh(self, obj) -> None:
        await self.db.refresh(obj)

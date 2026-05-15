"""
Study Groups Service — group creation, membership, materials, chat
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time, timezone, timedelta
from fastapi import HTTPException, status, UploadFile
from app.core.locks import distributed_lock, LockAcquisitionError
from app.models.database import (
    User, StudyGroup, StudyGroupMember, StudyGroupActivity,
    StudyGroupMaterial, StudyGroupMessage, Notifications,
)
from app.repositories.study_group_repository import StudyGroupRepository
from app.core.cache import get_or_load


class StudyGroupsService:
    def __init__(self, repo: StudyGroupRepository):
        self.repo = repo

    async def get_groups(self, user_id: int, *, skip: int = 0, limit: int = 100,
                          subject_id: Optional[int] = None,
                          is_public: Optional[bool] = None) -> list:
        async def _load():
            rows = await self.repo.get_groups_with_details(
                skip=skip, limit=limit, subject_id=subject_id, is_public=is_public)
            my_ids = await self.repo.get_user_group_ids(user_id)
            return [
                {"id": str(g.group_id), "name": g.group_name,
                 "course": s.subject_name if s else "Chưa xác định",
                 "members": g.member_count or 0, "maxMembers": g.max_members or 10,
                 "description": g.description or "", "createdBy": u.full_name,
                 "schedule": g.topic or "",
                 "status": "open" if (g.member_count or 0) < (g.max_members or 10) else "full",
                 "created_at": g.created_at.isoformat() if g.created_at else None,
                 "is_member": g.group_id in my_ids}
                for g, u, s in rows]
        return await get_or_load(f"study_groups:{skip}:{limit}:{subject_id}:{is_public}", _load, ttl=30)

    async def create_group(self, user: User, data: dict) -> dict:
        subject = await self.repo.get_subject_by_id(data['subject_id'])
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        g = StudyGroup(creator_id=user.user_id, subject_id=data['subject_id'],
                       group_name=data['group_name'], description=data.get('description'),
                       topic=data.get('topic'), max_members=data.get('max_members', 10),
                       is_public=data.get('is_public', True),
                       require_approval=data.get('require_approval', False),
                       member_count=1, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        g = await self.repo.create_group(g)
        await self.repo.create_member(StudyGroupMember(
            group_id=g.group_id, user_id=user.user_id, role='owner',
            status='active', joined_at=datetime.utcnow()))
        return {"id": str(g.group_id), "name": g.group_name, "course": subject.subject_name,
                "members": 1, "maxMembers": g.max_members, "description": g.description or "",
                "createdBy": user.full_name, "schedule": g.topic or "", "status": "open",
                "created_at": g.created_at.isoformat()}

    async def get_group(self, group_id: int, user_id: int) -> dict:
        row = await self.repo.get_group_with_details(group_id)
        if not row:
            raise HTTPException(status_code=404, detail="Study group not found")
        group, creator, subject = row
        members_rows = await self.repo.get_group_members(group_id)
        members = [{"id": str(u.user_id), "user_id": u.user_id, "name": u.full_name,
                     "email": u.email,
                     "role": "Trưởng nhóm" if m.role == 'owner' else "Thành viên",
                     "joinedAt": m.joined_at.isoformat() if m.joined_at else None}
                    for m, u in members_rows]
        return {"id": str(group.group_id), "name": group.group_name,
                "course": subject.subject_name if subject else "Chưa xác định",
                "members": len(members), "maxMembers": group.max_members or 10,
                "description": group.description or "", "createdBy": creator.full_name,
                "schedule": group.topic or "Chưa có lịch", "location": "Online - Google Meet",
                "status": "open" if len(members) < (group.max_members or 10) else "full",
                "createdAt": group.created_at.isoformat() if group.created_at else None,
                "is_member": any(m.user_id == user_id for m, _ in members_rows),
                "members_list": members, "activities": [], "materials": []}

    async def join_group(self, group_id: int, user: User) -> dict:
        group = await self.repo.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Study group not found")
        try:
            async with distributed_lock(resource=f"study-group:{group_id}:join", ttl_ms=5_000, timeout_s=3.0):
                ex = await self.repo.get_member(group_id, user.user_id)
                if ex:
                    if ex.status == 'active':
                        raise HTTPException(status_code=400, detail="Bạn đã là thành viên")
                    ex.status = 'active'; ex.joined_at = datetime.now()
                else:
                    members_rows = await self.repo.get_group_members(group_id)
                    if len(members_rows) >= (group.max_members or 10):
                        raise HTTPException(status_code=400, detail="Nhóm đã đầy")
                    await self.repo.create_member(StudyGroupMember(
                        group_id=group_id, user_id=user.user_id, role='member',
                        status='active' if not group.require_approval else 'pending'))
                    group.member_count = (group.member_count or 0) + 1
                await self.repo.commit()
        except LockAcquisitionError:
            raise HTTPException(status_code=429, detail="Hệ thống đang xử lý, vui lòng thử lại")
        except HTTPException:
            raise
        except Exception:
            await self.repo.rollback(); raise
        return {"message": "Tham gia nhóm thành công" if not group.require_approval else "Yêu cầu đã gửi",
                "status": "active" if not group.require_approval else "pending"}

    async def leave_group(self, group_id: int, user: User) -> dict:
        group = await self.repo.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Study group not found")
        member = await self.repo.get_member(group_id, user.user_id)
        if not member or member.status != 'active':
            raise HTTPException(status_code=400, detail="Bạn không phải thành viên")
        if member.role == 'owner':
            raise HTTPException(status_code=400, detail="Trưởng nhóm không thể rời nhóm.")
        try:
            await self.repo.delete_message(member)
            if group.member_count and group.member_count > 0:
                group.member_count -= 1
            await self.repo.commit()
        except Exception:
            await self.repo.rollback(); raise
        return {"message": "Đã rời nhóm thành công"}

    async def add_member(self, group_id: int, adder: User, user_id: int) -> dict:
        group = await self.repo.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        existing = await self.repo.get_member(group_id, user_id)
        if existing:
            raise HTTPException(status_code=400, detail="User is already a member")
        await self.repo.create_member(StudyGroupMember(
            group_id=group_id, user_id=user_id, role="member",
            status="active", joined_at=datetime.utcnow()))
        await self.repo.create_notification(Notifications(
            user_id=user_id, type="study_group_added", title="Được thêm vào nhóm",
            message=f"{adder.full_name} đã thêm bạn vào nhóm '{group.group_name}'",
            data={"group_id": group_id, "group_name": group.group_name}, is_read=False))
        await self.repo.commit()
        return {"message": "Member added successfully"}

    async def create_activity(self, group_id: int, user: User, data: dict) -> dict:
        group = await self.repo.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Study group not found")
        a = StudyGroupActivity(
            group_id=group_id, creator_id=user.user_id,
            activity_type=data['activity_type'], title=data['title'],
            description=data.get('description'),
            scheduled_date=date.fromisoformat(data['scheduled_date']) if data.get('scheduled_date') else None,
            scheduled_time=time.fromisoformat(data['scheduled_time']) if data.get('scheduled_time') else None,
            location=data.get('location'), meeting_link=data.get('meeting_link'), status='upcoming')
        a = await self.repo.create_activity(a)
        return {"id": str(a.activity_id), "type": a.activity_type, "title": a.title,
                "date": f"{a.scheduled_date} {a.scheduled_time}" if a.scheduled_date else None,
                "status": a.status, "message": "Hoạt động đã được tạo thành công"}

    async def create_material(self, group_id: int, user: User, *,
                               file: Optional[UploadFile] = None, title: Optional[str] = None,
                               description: Optional[str] = None, file_url: Optional[str] = None,
                               file_type: Optional[str] = None) -> dict:
        group = await self.repo.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Study group not found")
        mt, mu, mtype, fd, fs = title, file_url, file_type or "document", None, None
        if file:
            content = await file.read()
            if len(content) > 10*1024*1024:
                raise HTTPException(status_code=413, detail="File quá lớn. Tối đa 10MB")
            fd, mu, mt, mtype, fs = content, None, mt or file.filename, file.content_type or "application/octet-stream", len(content)
        elif not file_url or not title:
            raise HTTPException(status_code=400, detail="Must provide file or (title + file_url)")
        m = StudyGroupMaterial(group_id=group_id, uploader_id=user.user_id, title=mt,
                               description=description, file_url=mu, file_type=mtype, file_size=fs, file_data=fd)
        m = await self.repo.create_material(m)
        if fd:
            m.file_url = f"/api/v1/study-groups/{group_id}/materials/{m.material_id}"
            await self.repo.commit(); await self.repo.refresh(m)
        return {"id": m.material_id, "title": m.title, "file_url": m.file_url, "file_type": m.file_type,
                "file_size": m.file_size, "created_at": m.created_at.isoformat(), "message": "Tài liệu đã thêm"}

    async def download_material(self, group_id: int, material_id: int):
        m = await self.repo.get_material_by_id(material_id)
        if not m or m.group_id != group_id or not m.file_data:
            raise HTTPException(status_code=404, detail="File not found")
        return m

    async def update_material(self, group_id: int, material_id: int, *, title=None, description=None) -> dict:
        m = await self.repo.get_material_by_id(material_id)
        if not m or m.group_id != group_id:
            raise HTTPException(status_code=404, detail="Material not found")
        if title: m.title = title
        if description is not None: m.description = description
        await self.repo.commit()
        return {"id": m.material_id, "title": m.title, "description": m.description, "message": "Cập nhật thành công"}

    async def delete_material(self, group_id: int, material_id: int, user: User) -> dict:
        m = await self.repo.get_material_by_id(material_id)
        if not m or m.group_id != group_id:
            raise HTTPException(status_code=404, detail="Material not found")
        if m.uploader_id != user.user_id:
            roles = user.role if isinstance(user.role, list) else [user.role]
            if 'admin' not in roles and 'coordinator' not in roles:
                raise HTTPException(status_code=403, detail="Không có quyền xóa")
        await self.repo.delete_material(m)
        return {"message": "Xóa tài liệu thành công"}

    async def get_materials(self, group_id: int) -> list:
        rows = await self.repo.get_materials_by_group(group_id)
        return [{"id": m.material_id, "title": m.title, "description": m.description,
                 "file_url": m.file_url, "file_type": m.file_type,
                 "uploader": u.full_name, "created_at": m.created_at.isoformat()} for m, u in rows]

    async def send_message(self, group_id: int, user: User, text: str) -> dict:
        member = await self.repo.get_member(group_id, user.user_id)
        if not member or member.status != 'active':
            raise HTTPException(status_code=403, detail="You are not a member")
        vn = timezone(timedelta(hours=7))
        msg = StudyGroupMessage(group_id=group_id, user_id=user.user_id,
                                message_text=text.strip(), created_at=datetime.now(vn))
        msg = await self.repo.create_message(msg)
        return {"message_id": msg.message_id, "group_id": msg.group_id, "user_id": msg.user_id,
                "user_name": user.full_name, "message_text": msg.message_text,
                "created_at": msg.created_at.isoformat(), "is_deleted": msg.is_deleted}

    async def get_messages(self, group_id: int, user_id: int, *, limit: int = 50, before_id=None) -> list:
        member = await self.repo.get_member(group_id, user_id)
        if not member or member.status != 'active':
            raise HTTPException(status_code=403, detail="You are not a member")
        rows = await self.repo.get_messages(group_id, limit, before_id)
        return list(reversed([{"message_id": m.message_id, "group_id": m.group_id,
                "user_id": m.user_id, "user_name": u.full_name, "message_text": m.message_text,
                "created_at": m.created_at.isoformat(), "is_deleted": m.is_deleted} for m, u in rows]))

    async def delete_message(self, group_id: int, message_id: int, user: User) -> dict:
        msg = await self.repo.get_message_by_id(message_id)
        if not msg or msg.group_id != group_id:
            raise HTTPException(status_code=404, detail="Message not found")
        if msg.user_id != user.user_id:
            group = await self.repo.get_group_by_id(group_id)
            if not group or group.creator_id != user.user_id:
                raise HTTPException(status_code=403, detail="Can only delete your own messages")
        msg.is_deleted = True
        await self.repo.commit()
        return {"message": "Message deleted successfully"}
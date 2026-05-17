"""
Admin Service
Business logic for user management and system statistics
"""
from typing import Dict, List, Optional
from fastapi import HTTPException, status

from app.models.database import User
from app.repositories.admin_repository import AdminRepository
from app.core.cache import get_or_load


class AdminService:
    def __init__(self, repo: AdminRepository):
        self.repo = repo

    # ------------------------------------------------------------------
    # Permission helpers
    # ------------------------------------------------------------------
    @staticmethod
    def check_admin_or_coordinator(user: User):
        roles = user.role if isinstance(user.role, list) else [user.role]
        if 'admin' not in roles and 'coordinator' not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    @staticmethod
    def check_admin_only(user: User):
        roles = user.role if isinstance(user.role, list) else [user.role]
        if 'admin' not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # ------------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------------
    async def get_all_users(
        self, *, skip: int = 0, limit: int = 100,
        include_inactive: bool = False, role: Optional[str] = None
    ) -> List[dict]:
        users = await self.repo.get_all_users(
            skip=skip, limit=limit, include_inactive=include_inactive, role=role
        )
        user_list = []
        for u in users:
            user_data = {
                "user_id": u.user_id, "email": u.email,
                "full_name": u.full_name, "role": u.role,
                "is_active": u.is_active, "is_verified": u.is_verified,
                "created_at": u.created_at, "phone": u.phone,
                "faculty": None, "major": None, "student_code": None,
            }
            if u.student:
                user_data["student_code"] = u.student.student_code
                user_data["faculty"] = u.student.faculty
                user_data["major"] = u.student.major
            user_list.append(user_data)
        return user_list

    async def get_stats(self) -> Dict:
        async def _load():
            total_users = await self.repo.count_users()
            total_students = await self.repo.count_students()
            total_tutors = await self.repo.count_tutors()
            total_sessions = await self.repo.count_sessions()
            avg_rating = await self.repo.avg_rating()
            return {
                "total_users": total_users,
                "total_students": total_students,
                "total_tutors": total_tutors,
                "total_sessions": total_sessions,
                "average_rating": round(float(avg_rating), 1) if avg_rating else 0.0,
            }
        return await get_or_load("admin:stats", _load, ttl=30)

    async def soft_delete_user(self, user_id: int) -> dict:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.is_active = False
        try:
            await self.repo.commit()
        except Exception:
            await self.repo.rollback()
            raise
        return {"message": "User deleted successfully"}

    async def update_user(self, user_id: int, user_data: dict) -> dict:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if 'full_name' in user_data:
            user.full_name = user_data['full_name']
        if 'phone' in user_data:
            user.phone = user_data['phone']
        if 'role' in user_data:
            user.role = user_data['role']
        if 'is_active' in user_data:
            user.is_active = user_data['is_active']
        try:
            await self.repo.commit()
        except Exception:
            await self.repo.rollback()
            raise
        return {"message": "User updated successfully"}

    async def update_user_role(self, user_id: int, new_role) -> dict:
        from app.models.database import Student, Tutor, Coordinator
        
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.role = new_role if isinstance(new_role, list) else [new_role]
        
        roles = user.role
        
        # Auto-create Coordinator profile if needed
        if 'coordinator' in roles and not user.coordinator:
            self.repo.add(Coordinator(user_id=user_id, department='General'))
        
        # Auto-create Tutor profile if needed
        if 'tutor' in roles and not user.tutor:
            self.repo.add(Tutor(
                user_id=user_id,
                staff_code=f'GV{user_id:06d}',
                faculty='General'
            ))
        
        # Auto-create Student profile if needed
        if 'student' in roles and not user.student:
            self.repo.add(Student(
                user_id=user_id,
                student_code=f'SV{user_id:06d}',
                faculty='General'
            ))
        
        try:
            await self.repo.commit()
        except Exception:
            await self.repo.rollback()
            raise
        return {"message": "User role updated successfully", "user_id": user_id, "role": user.role}

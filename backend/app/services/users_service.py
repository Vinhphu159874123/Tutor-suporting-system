"""
Users Service — user profile, search, dashboard stats
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from fastapi import HTTPException, status

from app.models.database import User, Student, Tutor
from app.repositories.users_repository import UsersRepository
from app.core.cache import get_or_load


class UsersService:
    def __init__(self, repo: UsersRepository):
        self.repo = repo

    async def search_users(self, query: str, limit: int = 10) -> List[dict]:
        users = await self.repo.search(query, limit)
        return [
            {"user_id": u.user_id, "email": u.email, "full_name": u.full_name,
             "avatar_url": u.avatar_url,
             "role": u.role if isinstance(u.role, list) else [u.role]}
            for u in users
        ]

    async def get_profile(self, user: User) -> dict:
        data = {
            "user_id": user.user_id, "email": user.email,
            "full_name": user.full_name, "role": user.role,
            "phone": user.phone, "bio": user.bio,
            "avatar_url": user.avatar_url, "is_active": user.is_active,
            "is_verified": user.is_verified, "created_at": user.created_at,
            "program": None, "faculty": None, "major": None,
        }
        roles = user.role if isinstance(user.role, list) else [user.role]
        if 'student' in roles:
            s = await self.repo.get_student_by_user_id(user.user_id)
            if s:
                data["faculty"] = s.faculty
                data["major"] = s.major
                if s.preferences and 'program' in s.preferences:
                    data["program"] = s.preferences['program']
        elif 'tutor' in roles:
            t = await self.repo.get_tutor_by_user_id(user.user_id)
            if t:
                data["faculty"] = t.faculty
        return data

    async def update_profile(self, user: User, update_data: dict) -> dict:
        if update_data.get('full_name') is not None:
            user.full_name = update_data['full_name']
        if update_data.get('phone') is not None:
            user.phone = update_data['phone']
        if update_data.get('bio') is not None:
            user.bio = update_data['bio']
        if update_data.get('avatar_url') is not None:
            user.avatar_url = update_data['avatar_url']
        user.updated_at = datetime.utcnow()

        roles = user.role if isinstance(user.role, list) else [user.role]
        if 'student' in roles and any(update_data.get(k) for k in ('program', 'faculty', 'major')):
            s = await self.repo.get_student_by_user_id(user.user_id)
            if s:
                if update_data.get('faculty') is not None:
                    s.faculty = update_data['faculty']
                if update_data.get('major') is not None:
                    s.major = update_data['major']
                if update_data.get('program') is not None:
                    prefs = s.preferences or {}
                    prefs['program'] = update_data['program']
                    s.preferences = prefs
        elif 'tutor' in roles and update_data.get('faculty'):
            t = await self.repo.get_tutor_by_user_id(user.user_id)
            if t and update_data.get('faculty') is not None:
                t.faculty = update_data['faculty']

        try:
            await self.repo.commit()
            await self.repo.refresh(user)
        except Exception:
            await self.repo.rollback()
            raise
        return await self.get_profile(user)

    async def get_users_list(self, *, skip: int = 0, limit: int = 100,
                              role: Optional[str] = None) -> list:
        return await self.repo.get_all(skip=skip, limit=limit, role=role)

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def soft_delete_user(self, user_id: int) -> dict:
        user = await self.get_user_by_id(user_id)
        user.is_active = False
        try:
            await self.repo.commit()
        except Exception:
            await self.repo.rollback()
            raise
        return {"message": "User deleted successfully"}

    async def get_dashboard_stats(self, user: User, mode: Optional[str] = None) -> Dict[str, Any]:
        active_role = mode or user.role
        roles = user.role if isinstance(user.role, list) else [user.role]

        # Auto-create profiles if needed
        await self._ensure_profiles(user, roles)

        if mode:
            if mode == 'student' and not user.student_id:
                raise HTTPException(status_code=403, detail="User is not a student")
            if mode == 'tutor' and not user.tutor_id:
                raise HTTPException(status_code=403, detail="User is not a tutor")

        async def _load():
            stats = {"total_sessions": 0, "completed_sessions": 0,
                     "upcoming_sessions": 0, "average_rating": 0.0}
            try:
                if active_role == 'student':
                    stats = await self._student_stats(user)
                elif active_role == 'tutor':
                    stats = await self._tutor_stats(user)
            except Exception:
                pass
            return stats

        cache_key = f"dashboard:stats:{user.user_id}:{active_role}"
        return await get_or_load(cache_key, _load, ttl=15)

    async def get_coordinator_stats(self) -> Dict[str, Any]:
        stats = {"total_sessions": 0, "active_students": 0, "total_tutors": 0,
                 "pending_tutors": 0, "pending_sessions": 0,
                 "completed_sessions": 0, "average_rating": 0.0,
                 "total_hours": 0, "attendance_rate": 0.0}
        try:
            stats["total_sessions"] = await self.repo.count_total_sessions()
            stats["pending_tutors"] = await self.repo.count_pending_registrations()
            stats["pending_sessions"] = await self.repo.count_pending_sessions()
            avg = await self.repo.avg_feedback_rating()
            stats["average_rating"] = round(float(avg), 1) if avg else 0.0
            stats["active_students"] = await self.repo.count_active_students()
            stats["total_tutors"] = await self.repo.count_tutors()
            stats["completed_sessions"] = await self.repo.count_completed_sessions()
            stats["total_hours"] = stats["total_sessions"] * 2
            total_att = await self.repo.count_attendance()
            if stats["completed_sessions"] > 0 and stats["active_students"] > 0:
                expected = stats["completed_sessions"] * (stats["active_students"] / max(stats["total_sessions"], 1))
                stats["attendance_rate"] = round((total_att / max(expected, 1)) * 100, 1) if expected > 0 else 0.0
        except Exception:
            pass
        return stats

    # ---- private ----
    async def _ensure_profiles(self, user: User, roles: list):
        if 'student' in roles and not user.student_id:
            s = Student(user_id=user.user_id, student_code=f"ST{user.user_id:06d}",
                        faculty="Unknown", major="Unknown", preferences={})
            try:
                await self.repo.create_student(s)
            except Exception:
                await self.repo.rollback()
                raise
            await self.repo.refresh(user)
        if 'tutor' in roles and not user.tutor_id:
            t = Tutor(user_id=user.user_id, faculty="Unknown",
                      bio=user.bio or "No bio provided", rating=0.0, total_sessions=0)
            try:
                await self.repo.create_tutor(t)
            except Exception:
                await self.repo.rollback()
                raise
            await self.repo.refresh(user)

    async def _student_stats(self, user: User) -> dict:
        s = await self.repo.get_student_by_user_id(user.user_id)
        if not s:
            return {"total_sessions": 0, "completed_sessions": 0, "upcoming_sessions": 0, "average_rating": 0.0}
        today = date.today()
        total = await self.repo.get_student_session_count(s.user_id)
        completed = await self.repo.get_student_attendance_count(s.student_id)
        upcoming = await self.repo.get_student_upcoming_count(s.user_id, today)
        return {"total_sessions": total, "completed_sessions": completed,
                "upcoming_sessions": upcoming, "average_rating": 0.0}

    async def _tutor_stats(self, user: User) -> dict:
        t = await self.repo.get_tutor_by_user_id(user.user_id)
        if not t:
            return {"total_sessions": 0, "completed_sessions": 0, "upcoming_sessions": 0, "average_rating": 0.0}
        row = await self.repo.get_tutor_session_stats(t.tutor_id)
        avg = await self.repo.get_tutor_avg_rating(t.tutor_id)
        return {"total_sessions": row.total or 0, "completed_sessions": int(row.completed or 0),
                "upcoming_sessions": int(row.upcoming or 0),
                "average_rating": round(float(avg), 1) if avg else 0.0}

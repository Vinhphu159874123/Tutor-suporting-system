"""
Courses Service — business logic for course / subject management
"""
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.models.database import User
from app.repositories.course_repository import CourseRepository
from app.core.cache import get_or_load


class CoursesService:
    def __init__(self, repo: CourseRepository):
        self.repo = repo

    async def get_my_courses(self, user: User, mode: Optional[str] = None) -> List[Dict[str, Any]]:
        active_role = mode or user.role
        if mode == 'student' and not user.student_id:
            raise HTTPException(status_code=403, detail="User is not a student")
        if mode == 'tutor' and not user.tutor_id:
            raise HTTPException(status_code=403, detail="User is not a tutor")
        try:
            if active_role == 'student':
                return await self._student_courses(user.user_id)
            elif active_role == 'tutor':
                return await self._tutor_courses(user.user_id)
        except Exception:
            pass
        return []

    async def get_course_by_code(self, course_code: str) -> Dict[str, Any]:
        subject = await self.repo.get_by_code(course_code)
        if not subject:
            raise HTTPException(status_code=404, detail="Course not found")
        return {"code": subject.subject_code, "name": subject.subject_name,
                "credits": subject.credits or 4, "department": subject.department,
                "subject_id": subject.subject_id}

    async def get_all_subjects(self) -> List[Dict[str, Any]]:
        async def _load():
            subjects = await self.repo.get_all_ordered()
            return [
                {"subject_id": s.subject_id, "subject_code": s.subject_code,
                 "subject_name": s.subject_name, "department": s.department,
                 "credits": s.credits, "description": s.description}
                for s in subjects
            ]
        return await get_or_load("subjects:all", _load, ttl=120)

    async def get_subject_by_id(self, subject_id: int) -> Dict[str, Any]:
        subject = await self.repo.get_by_id(subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        cnt = await self.repo.count_sessions_by_subject(subject_id)
        return {"subject_id": subject.subject_id, "subject_code": subject.subject_code,
                "subject_name": subject.subject_name, "department": subject.department,
                "credits": subject.credits, "description": subject.description,
                "session_count": cnt}

    # ---- private ----
    async def _student_courses(self, user_id: int) -> List[dict]:
        rows = await self.repo.get_student_courses(user_id)
        return [{"subject_id": s.subject_id, "subject_code": s.subject_code,
                 "subject_name": s.subject_name, "department": s.department,
                 "credits": s.credits or 4, "session_count": sc, "tutor_id": tid}
                for s, tid, sc in rows]

    async def _tutor_courses(self, user_id: int) -> List[dict]:
        tutor = await self.repo.get_tutor_by_user_id(user_id)
        if not tutor:
            return []
        sess_rows = await self.repo.get_tutor_session_courses(tutor.tutor_id)
        reg_rows = await self.repo.get_tutor_registered_courses(tutor.tutor_id)
        d: Dict[int, dict] = {}
        for s, sc in sess_rows:
            d[s.subject_id] = {"subject_id": s.subject_id, "subject_code": s.subject_code,
                               "subject_name": s.subject_name, "department": s.department,
                               "credits": s.credits or 4, "session_count": sc, "status": "active"}
        for s, st in reg_rows:
            if s.subject_id not in d:
                d[s.subject_id] = {"subject_id": s.subject_id, "subject_code": s.subject_code,
                                   "subject_name": s.subject_name, "department": s.department,
                                   "credits": s.credits or 4, "session_count": 0, "status": st}
        return list(d.values())

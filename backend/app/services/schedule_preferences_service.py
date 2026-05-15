"""
Schedule Preferences Service — student scheduling preference management
"""
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.models.database import SchedulePreference, User
from app.repositories.schedule_preference_repository import SchedulePreferenceRepository


class SchedulePreferencesService:
    def __init__(self, repo: SchedulePreferenceRepository):
        self.repo = repo

    async def _get_student(self, user_id: int):
        s = await self.repo.get_student_by_user_id(user_id)
        if not s:
            raise HTTPException(status_code=404, detail="Student profile not found")
        return s

    async def _get_subject(self, subject_id: int):
        s = await self.repo.get_subject_by_id(subject_id)
        if not s:
            raise HTTPException(status_code=404, detail="Subject not found")
        return s

    async def create_preference(self, user: User, data: dict) -> dict:
        student = await self._get_student(user.user_id)
        subject = await self._get_subject(data['subject_id'])
        dup = await self.repo.get_pending_for_student_subject(student.student_id, data['subject_id'])
        if dup:
            raise HTTPException(status_code=400, detail="You already have a pending preference for this subject.")
        pref = SchedulePreference(
            student_id=student.student_id, subject_id=data['subject_id'],
            preferred_start_date=data['preferred_start_date'],
            total_sessions=data['total_sessions'], session_duration=data['session_duration'],
            session_format=data.get('session_format', 'both'),
            available_time_slots=data['available_time_slots'],
            notes=data.get('notes'), status='pending')
        try:
            pref = await self.repo.create(pref)
        except Exception:
            await self.repo.rollback()
            raise
        return self._to_response(pref, subject, user.full_name)

    async def get_my_preferences(self, user: User, status_filter: Optional[str] = None) -> List[dict]:
        student = await self._get_student(user.user_id)
        rows = await self.repo.get_by_student(student.student_id, status_filter)
        return [self._to_response(p, s, user.full_name) for p, s in rows]

    async def update_preference(self, user: User, preference_id: int, update: dict) -> dict:
        student = await self._get_student(user.user_id)
        row = await self.repo.get_with_subject(preference_id)
        if not row:
            raise HTTPException(status_code=404, detail="Preference not found")
        pref, subject = row
        if pref.student_id != student.student_id:
            raise HTTPException(status_code=403, detail="You can only update your own preferences")
        for field in ('preferred_start_date', 'total_sessions', 'session_duration',
                      'session_format', 'notes', 'status'):
            if update.get(field) is not None:
                setattr(pref, field, update[field])
        if update.get('available_time_slots') is not None:
            pref.available_time_slots = update['available_time_slots']
        try:
            await self.repo.commit()
            await self.repo.refresh(pref)
        except Exception:
            await self.repo.rollback()
            raise
        return self._to_response(pref, subject, user.full_name)

    async def delete_preference(self, user: User, preference_id: int) -> dict:
        student = await self._get_student(user.user_id)
        pref = await self.repo.get_by_id(preference_id)
        if not pref:
            raise HTTPException(status_code=404, detail="Preference not found")
        if pref.student_id != student.student_id:
            raise HTTPException(status_code=403, detail="You can only delete your own preferences")
        try:
            await self.repo.delete(pref)
        except Exception:
            await self.repo.rollback()
            raise
        return {"message": "Preference deleted successfully"}

    async def get_statistics(self, *, subject_id: Optional[int] = None,
                              min_requests: int = 1) -> List[dict]:
        stats_data = await self.repo.get_statistics_rows(subject_id, min_requests)
        result_list = []
        for st in stats_data:
            fmt = await self.repo.get_format_distribution(st.subject_id)
            dur = await self.repo.get_duration_distribution(st.subject_id)
            slots_rows = await self.repo.get_time_slots(st.subject_id)
            tc: Dict[str, int] = {}
            for (slots,) in slots_rows:
                for s in slots:
                    k = f"{s['day']} {s['start_time']}-{s['end_time']}"
                    tc[k] = tc.get(k, 0) + 1
            popular = [{"time_slot": k, "count": v,
                        "percentage": round(v / st.total_requests * 100, 1)}
                       for k, v in sorted(tc.items(), key=lambda x: x[1], reverse=True)[:10]]
            result_list.append({
                "subject_id": st.subject_id, "subject_code": st.subject_code,
                "subject_name": st.subject_name, "total_requests": st.total_requests,
                "popular_time_slots": popular, "format_distribution": fmt,
                "average_duration": int(st.avg_duration), "duration_distribution": dur,
                "average_sessions": round(st.avg_sessions, 1),
                "earliest_start_date": st.earliest_date, "latest_start_date": st.latest_date})
        return result_list

    async def get_subject_details(self, subject_id: int) -> dict:
        data = await self.repo.get_subject_details(subject_id)
        if not data:
            raise HTTPException(status_code=404, detail="No preferences found for this subject")
        return {
            "subject_id": subject_id,
            "subject_code": data[0][3].subject_code,
            "subject_name": data[0][3].subject_name,
            "total_requests": len(data),
            "preferences": [
                {"preference_id": p.preference_id, "student_name": u.full_name,
                 "student_code": s.student_code,
                 "preferred_start_date": p.preferred_start_date.isoformat(),
                 "total_sessions": p.total_sessions, "session_duration": p.session_duration,
                 "session_format": p.session_format, "available_time_slots": p.available_time_slots,
                 "notes": p.notes, "created_at": p.created_at.isoformat()}
                for p, s, u, _ in data]}

    @staticmethod
    def _to_response(pref, subject, student_name: str) -> dict:
        return {
            "preference_id": pref.preference_id, "student_id": pref.student_id,
            "student_name": student_name, "subject_id": subject.subject_id,
            "subject_code": subject.subject_code, "subject_name": subject.subject_name,
            "preferred_start_date": pref.preferred_start_date,
            "total_sessions": pref.total_sessions, "session_duration": pref.session_duration,
            "session_format": pref.session_format,
            "available_time_slots": pref.available_time_slots,
            "notes": pref.notes, "status": pref.status,
            "created_at": pref.created_at, "updated_at": pref.updated_at}

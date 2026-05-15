"""
Progress Service — student learning progress tracking
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from app.models.database import User
from app.repositories.progress_repository import ProgressRepository


class ProgressService:
    def __init__(self, repo: ProgressRepository):
        self.repo = repo

    async def get_student_progress(
        self, student_id: int, *,
        subject_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        rows = await self.repo.get_student_progress(
            student_id, subject_id=subject_id,
            start_date=start_date, end_date=end_date,
        )
        return [
            {"courseId": sub.subject_code or f"SUBJ{sub.subject_id}",
             "courseName": sub.subject_name, "totalSessions": 1,
             "completedSessions": 1 if ses.status == "completed" else 0,
             "averageScore": prog.understanding_level or 0,
             "attendance": 100 if ses.status == "completed" else 0,
             "session_date": ses.start_time.isoformat() if ses.start_time else None,
             "understanding_level": prog.understanding_level,
             "topics_covered": prog.topics_covered or [],
             "strengths": prog.strengths, "weaknesses": prog.weaknesses}
            for prog, ses, sub in rows
        ]

    async def get_course_study_progress(
        self, subject_id: int, user: User, *,
        tutor_id: Optional[int] = None, mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        user_roles = user.role if isinstance(user.role, list) else [user.role]
        effective_mode = mode or ('tutor' if 'tutor' in user_roles else user_roles[0])

        subject = await self.repo.get_subject_by_id(subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")

        if effective_mode == 'tutor' and 'tutor' in user_roles:
            return await self._tutor_view(subject, user)
        elif effective_mode == 'student' and 'student' in user_roles:
            return await self._student_view(subject, user, tutor_id)
        raise HTTPException(status_code=403, detail="Only tutors and students can view progress")

    # ---- private ----
    async def _tutor_view(self, subject, user: User) -> dict:
        tutor = await self.repo.get_tutor_by_user_id(user.user_id)
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor profile not found")
        sessions = await self.repo.get_sessions_for_tutor_subject(subject.subject_id, tutor.tutor_id)
        if not sessions:
            return {"subject_id": subject.subject_id, "subject_name": subject.subject_name,
                    "subject_code": subject.subject_code, "total_sessions": 0, "students": []}
        sids = [s.session_id for s in sessions]
        students_result = await self.repo.get_students_in_sessions(sids)
        students_data = []
        for u, stu, _ in students_result:
            att = await self.repo.get_attendance_for_student_sessions(stu.student_id, sids)
            pc = sum(1 for a in att if a.status == 'present')
            lc = sum(1 for a in att if a.status == 'late')
            ac = sum(1 for a in att if a.status == 'absent')
            ec = sum(1 for a in att if a.status == 'excused')
            ts = len(sessions); cs = len(att)
            ar = (pc + lc) / ts * 100 if ts else 0
            pp = cs / ts * 100 if ts else 0
            students_data.append({
                "student_id": stu.student_id, "user_id": u.user_id,
                "student_name": u.full_name, "student_code": stu.student_code,
                "email": u.email,
                "progress": {"total_sessions": ts, "completed_sessions": cs,
                             "progress_percentage": round(pp, 1),
                             "attendance": {"present": pc, "late": lc, "absent": ac,
                                            "excused": ec, "attendance_rate": round(ar, 1)}}})
        students_data.sort(key=lambda x: x["progress"]["progress_percentage"])
        return {"subject_id": subject.subject_id, "subject_name": subject.subject_name,
                "subject_code": subject.subject_code, "total_sessions": len(sessions),
                "total_students": len(students_data), "students": students_data}

    async def _student_view(self, subject, user: User, tutor_id: Optional[int]) -> dict:
        student = await self.repo.get_student_by_user_id(user.user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        sessions = await self.repo.get_student_sessions_for_subject(
            subject.subject_id, user.user_id, tutor_id
        )
        empty = {"subject_id": subject.subject_id, "subject_name": subject.subject_name,
                 "subject_code": subject.subject_code,
                 "student_progress": {"total_sessions": 0, "completed_sessions": 0,
                                      "progress_percentage": 0,
                                      "attendance": {"present": 0, "late": 0, "absent": 0,
                                                     "excused": 0, "attendance_rate": 0},
                                      "sessions": []}}
        if not sessions:
            return empty
        sids = [s.session_id for s in sessions]
        att_list = await self.repo.get_attendance_for_student_sessions(student.student_id, sids)
        att_map = {a.session_id: a for a in att_list}
        vtz = timezone(timedelta(hours=7))
        now = datetime.now(vtz)
        details = []
        for s in sessions:
            a = att_map.get(s.session_id)
            sdt = None
            if s.scheduled_date and s.start_time:
                sdt = datetime.combine(s.scheduled_date, s.start_time).replace(tzinfo=vtz)
            details.append({
                "session_id": s.session_id, "title": s.title,
                "scheduled_date": s.scheduled_date.isoformat() if s.scheduled_date else None,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "status": s.status, "is_past": bool(sdt and sdt < now),
                "attendance": {"status": a.status,
                               "check_in_time": a.check_in_time.isoformat() if a and a.check_in_time else None,
                               "duration_minutes": a.duration_minutes if a else None} if a else None})
        pc = sum(1 for a in att_map.values() if a.status == 'present')
        lc = sum(1 for a in att_map.values() if a.status == 'late')
        ac_ = sum(1 for a in att_map.values() if a.status == 'absent')
        ec = sum(1 for a in att_map.values() if a.status == 'excused')
        ts = len(sessions); cs = len(att_map)
        return {"subject_id": subject.subject_id, "subject_name": subject.subject_name,
                "subject_code": subject.subject_code,
                "student_progress": {"total_sessions": ts, "completed_sessions": cs,
                                     "progress_percentage": round(cs / ts * 100, 1) if ts else 0,
                                     "attendance": {"present": pc, "late": lc, "absent": ac_,
                                                    "excused": ec,
                                                    "attendance_rate": round((pc + lc) / ts * 100, 1) if ts else 0},
                                     "sessions": details}}

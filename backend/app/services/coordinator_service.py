"""
Coordinator Service — tutor registration approval, session approval, tutor management
"""
from typing import Optional, List, Dict
from datetime import datetime
from fastapi import HTTPException, status
import io, csv

from app.models.database import User
from app.events import event_bus, EventTypes
from app.core.locks import distributed_lock, LockAcquisitionError
from app.repositories.coordinator_repository import CoordinatorRepository


class CoordinatorService:
    def __init__(self, repo: CoordinatorRepository):
        self.repo = repo

    async def get_pending_registrations(self, status_filter: str, skip: int, limit: int) -> list:
        rows = await self.repo.get_registrations_with_details(status_filter, skip, limit)
        result = []
        for reg, tutor, user, subject in rows:
            notif = await self.repo.get_registration_notification(reg.registration_id)
            availability = notif.data.get('availability') if notif and notif.data else None
            selected_schedule = None
            if reg.status == "approved":
                first_session = await self.repo.get_first_session_for_reg(reg.tutor_id, reg.subject_id)
                if first_session:
                    sched = await self.repo.get_schedule_for_session(
                        reg.tutor_id, reg.subject_id, first_session.start_time, first_session.end_time)
                    if sched:
                        day_names = ["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6","Thứ 7","Chủ nhật"]
                        selected_schedule = {
                            "schedule_id": sched.schedule_id, "day_of_week": sched.day_of_week,
                            "day_name": day_names[sched.day_of_week],
                            "start_time": str(sched.start_time), "end_time": str(sched.end_time),
                            "location_type": sched.location_type}
            result.append({
                "registration_id": reg.registration_id, "tutor_id": reg.tutor_id,
                "tutor_name": user.full_name, "tutor_email": user.email, "tutor_bio": tutor.bio,
                "subject_id": reg.subject_id, "subject_name": subject.subject_name,
                "subject_code": subject.subject_code,
                "gpa": float(reg.gpa) if reg.gpa else None,
                "qualifications": reg.qualifications, "status": reg.status,
                "registered_at": reg.registered_at, "responded_at": reg.responded_at,
                "rejection_reason": reg.rejection_reason, "availability": availability,
                "total_sessions": reg.total_sessions,
                "start_date": reg.start_date.isoformat() if reg.start_date else None,
                "end_date": reg.end_date.isoformat() if reg.end_date else None,
                "max_students": reg.max_students, "selected_schedule": selected_schedule})
        return result

    async def get_registration_schedules(self, registration_id: int) -> list:
        reg = await self.repo.get_registration_by_id(registration_id)
        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")
        schedules = await self.repo.get_schedules_for_registration(reg.tutor_id, reg.subject_id)
        day_names = ["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6","Thứ 7","Chủ nhật"]
        return [{"schedule_id": s.schedule_id, "day_of_week": s.day_of_week,
                 "day_name": day_names[s.day_of_week],
                 "start_time": str(s.start_time), "end_time": str(s.end_time),
                 "duration": s.duration, "location_type": s.location_type,
                 "description": s.description} for s in schedules]

    async def approve_registration(self, user: User, registration_id: int,
                                    schedule_id: Optional[int] = None) -> dict:
        try:
            async with distributed_lock(resource=f"registration:{registration_id}:approve",
                                         ttl_ms=5_000, timeout_s=3.0):
                reg = await self.repo.get_registration_by_id(registration_id)
                if not reg:
                    raise HTTPException(status_code=404, detail="Registration not found")
                if reg.status != 'pending':
                    raise HTTPException(status_code=400, detail=f"Registration is already {reg.status}")
                coord = await self.repo.get_coordinator_by_user_id(user.user_id)
                if not coord:
                    raise HTTPException(status_code=400, detail="Coordinator profile not found")
                reg.status = 'approved'
                reg.approved_by = coord.coordinator_id
                reg.responded_at = datetime.utcnow()
                if schedule_id:
                    reg.selected_schedule_id = schedule_id
                await self.repo.commit()
                await self.repo.refresh(reg)
        except LockAcquisitionError:
            raise HTTPException(status_code=429, detail="Request đang được xử lý")
        except HTTPException:
            raise
        except Exception:
            await self.repo.rollback(); raise
        tutor = await self.repo.get_tutor_by_id(reg.tutor_id)
        if tutor:
            subject = await self.repo.get_subject_by_id(reg.subject_id)
            await event_bus.emit(EventTypes.REGISTRATION_APPROVED, {
                'user_id': tutor.user_id, 'registration_id': reg.registration_id,
                'tutor_id': reg.tutor_id, 'subject_id': reg.subject_id,
                'subject_name': subject.subject_name if subject else "môn học",
                'status': 'approved', 'total_sessions': reg.total_sessions,
                'start_date': reg.start_date.isoformat() if reg.start_date else None,
                'max_students': reg.max_students, 'schedule_id': schedule_id})
        return {"message": "Registration approved successfully",
                "registration_id": reg.registration_id, "status": reg.status}

    async def reject_registration(self, user: User, registration_id: int, reason: str) -> dict:
        try:
            reg = await self.repo.get_registration_by_id(registration_id)
            if not reg:
                raise HTTPException(status_code=404, detail="Registration not found")
            if reg.status != 'pending':
                raise HTTPException(status_code=400, detail=f"Registration is already {reg.status}")
            coord = await self.repo.get_coordinator_by_user_id(user.user_id)
            if not coord:
                raise HTTPException(status_code=400, detail="Coordinator profile not found")
            reg.status = 'rejected'
            reg.approved_by = coord.coordinator_id
            reg.rejection_reason = reason
            reg.responded_at = datetime.utcnow()
            await self.repo.commit()
        except HTTPException:
            raise
        except Exception:
            await self.repo.rollback(); raise
        tutor = await self.repo.get_tutor_by_id(reg.tutor_id)
        if tutor:
            subject = await self.repo.get_subject_by_id(reg.subject_id)
            await event_bus.emit(EventTypes.REGISTRATION_REJECTED, {
                'user_id': tutor.user_id, 'registration_id': reg.registration_id,
                'subject_name': subject.subject_name if subject else "môn học",
                'reason': reason, 'status': 'rejected'})
        return {"message": "Registration rejected", "registration_id": reg.registration_id,
                "status": reg.status, "reason": reason}

    async def get_pending_sessions(self, skip: int, limit: int) -> list:
        rows = await self.repo.get_pending_sessions(skip, limit)
        ids = [s.session_id for s, _, _, _ in rows]
        counts = await self.repo.get_participant_counts(ids)
        return [{"session_id": s.session_id, "subject_name": sub.subject_name,
                 "subject_code": sub.subject_code, "tutor_name": u.full_name,
                 "tutor_email": u.email, "start_time": s.start_time, "end_time": s.end_time,
                 "location": s.location, "max_participants": s.max_participants,
                 "current_participants": counts.get(s.session_id, 0),
                 "status": s.status, "created_at": s.created_at}
                for s, t, u, sub in rows]

    async def approve_session(self, session_id: int) -> dict:
        try:
            s = await self.repo.get_session_by_id(session_id)
            if not s:
                raise HTTPException(status_code=404, detail="Session not found")
            if s.status != 'pending':
                raise HTTPException(status_code=400, detail=f"Session is already {s.status}")
            s.status = 'scheduled'
            await self.repo.commit()
        except HTTPException:
            raise
        except Exception:
            await self.repo.rollback(); raise
        return {"message": "Session approved", "session_id": s.session_id, "status": s.status}

    async def reject_session(self, session_id: int, reason: str) -> dict:
        try:
            s = await self.repo.get_session_by_id(session_id)
            if not s:
                raise HTTPException(status_code=404, detail="Session not found")
            if s.status != 'pending':
                raise HTTPException(status_code=400, detail=f"Session is already {s.status}")
            s.status = 'cancelled'
            await self.repo.commit()
        except HTTPException:
            raise
        except Exception:
            await self.repo.rollback(); raise
        return {"message": "Session rejected", "session_id": s.session_id, "status": s.status, "reason": reason}

    async def get_all_tutors(self, skip: int, limit: int, search: Optional[str]) -> dict:
        data = await self.repo.get_tutors_with_users(skip, limit, search)
        ids = [t.tutor_id for t, _ in data]
        sess_stats = await self.repo.get_session_counts_for_tutors(ids)
        course_stats = await self.repo.get_course_counts_for_tutors(ids)
        return {
            "tutors": [{"tutor_id": t.tutor_id, "user_id": u.user_id, "full_name": u.full_name,
                         "email": u.email, "staff_code": t.staff_code, "faculty": t.faculty,
                         "rating": float(t.rating) if t.rating else 0.0,
                         "total_sessions": sess_stats.get(t.tutor_id, 0),
                         "total_courses": course_stats.get(t.tutor_id, 0),
                         "is_verified": t.is_verified,
                         "created_at": u.created_at.isoformat() if u.created_at else None}
                        for t, u in data],
            "total": len(data), "skip": skip, "limit": limit}

    async def get_tutor_courses(self, tutor_id: int) -> dict:
        td = await self.repo.get_tutor_with_user(tutor_id)
        if not td:
            raise HTTPException(status_code=404, detail="Tutor not found")
        tutor, user = td
        cd = await self.repo.get_tutor_course_stats(tutor_id)
        sids = [s.subject_id for s, _, _, _ in cd]
        sc = await self.repo.get_student_counts_for_subjects(tutor_id, sids)
        return {"tutor": {"tutor_id": tutor.tutor_id, "full_name": user.full_name,
                          "email": user.email, "staff_code": tutor.staff_code,
                          "faculty": tutor.faculty,
                          "rating": float(tutor.rating) if tutor.rating else 0.0},
                "courses": [{"subject_id": s.subject_id, "subject_code": s.subject_code,
                             "subject_name": s.subject_name, "department": s.department,
                             "total_sessions": ts or 0, "completed_sessions": cs or 0,
                             "student_count": sc.get(s.subject_id, 0),
                             "average_rating": round(float(ar), 2) if ar else 0.0}
                            for s, ts, cs, ar in cd],
                "total_courses": len(cd)}

    async def get_course_details(self, tutor_id: int, subject_id: int) -> dict:
        td = await self.repo.get_tutor_with_user(tutor_id)
        if not td:
            raise HTTPException(status_code=404, detail="Tutor not found")
        tutor, tutor_user = td
        subject = await self.repo.get_subject_by_id(subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        sessions = await self.repo.get_sessions_for_tutor_subject(tutor_id, subject_id)
        sids = [s.session_id for s in sessions]
        parts = await self.repo.get_participants_for_sessions(sids)
        students_data: Dict = {}
        for p, su in parts:
            if su.user_id not in students_data:
                students_data[su.user_id] = {"user_id": su.user_id, "full_name": su.full_name,
                                             "email": su.email, "total_sessions": len(sessions),
                                             "attended_sessions": 0, "attendance_rate": 0}
            students_data[su.user_id]["attended_sessions"] += 1
        for sd in students_data.values():
            sd["attendance_rate"] = round(sd["attended_sessions"]/sd["total_sessions"]*100, 1) if sd["total_sessions"] > 0 else 0
        fbs = await self.repo.get_feedbacks_for_sessions(sids)
        fb_list = [{"session_id": sm.session_id, "session_title": sm.title,
                     "session_date": sm.scheduled_date.isoformat() if sm.scheduled_date else None,
                     "student_name": u.full_name, "student_email": u.email,
                     "rating": f.rating, "comment": f.comment,
                     "created_at": f.created_at.isoformat() if f.created_at else None}
                    for f, u, sm in fbs]
        avg_r = sum(f["rating"] for f in fb_list)/len(fb_list) if fb_list else 0.0
        return {"tutor": {"tutor_id": tutor.tutor_id, "full_name": tutor_user.full_name,
                           "email": tutor_user.email, "staff_code": tutor.staff_code},
                "course": {"subject_id": subject.subject_id, "subject_code": subject.subject_code,
                           "subject_name": subject.subject_name, "department": subject.department},
                "statistics": {"total_sessions": len(sessions),
                               "completed_sessions": sum(1 for s in sessions if s.status == 'completed'),
                               "total_students": len(students_data),
                               "average_rating": round(avg_r, 2), "total_feedbacks": len(fb_list)},
                "students": list(students_data.values()), "feedbacks": fb_list}

    def export_csv(self, details: dict) -> str:
        output = io.StringIO()
        w = csv.writer(output)
        w.writerow(["COURSE REPORT"]); w.writerow([])
        w.writerow(["Tutor:", details["tutor"]["full_name"]])
        w.writerow(["Email:", details["tutor"]["email"]])
        w.writerow(["Staff Code:", details["tutor"]["staff_code"]]); w.writerow([])
        w.writerow(["Course:", details["course"]["subject_name"]])
        w.writerow(["Code:", details["course"]["subject_code"]])
        w.writerow(["Department:", details["course"]["department"]]); w.writerow([])
        w.writerow(["Total Sessions:", details["statistics"]["total_sessions"]])
        w.writerow(["Completed:", details["statistics"]["completed_sessions"]])
        w.writerow(["Students:", details["statistics"]["total_students"]])
        w.writerow(["Avg Rating:", details["statistics"]["average_rating"]]); w.writerow([])
        w.writerow(["STUDENTS ATTENDANCE"])
        w.writerow(["Name", "Email", "Total", "Attended", "Rate (%)"])
        for s in details["students"]:
            w.writerow([s["full_name"], s["email"], s["total_sessions"], s["attended_sessions"], s["attendance_rate"]])
        w.writerow([]); w.writerow(["SESSION FEEDBACKS"])
        w.writerow(["Session", "Date", "Student", "Rating", "Comment"])
        for f in details["feedbacks"]:
            w.writerow([f["session_title"], f["session_date"], f["student_name"], f["rating"], f["comment"] or ""])
        output.seek(0)
        return output.getvalue()

    async def update_tutor_rating(self, tutor_id: int) -> dict:
        tutor = await self.repo.get_tutor_by_id(tutor_id)
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor not found")
        avg, cnt = await self.repo.get_tutor_avg_rating(tutor_id)
        if avg is not None:
            tutor.rating = float(avg)
            await self.repo.commit()
            return {"message": "Rating updated", "tutor_id": tutor_id,
                    "new_rating": round(float(avg), 2), "total_feedbacks": cnt}
        return {"message": "No feedbacks", "tutor_id": tutor_id, "rating": 0.0, "total_feedbacks": 0}

    async def update_all_ratings(self) -> dict:
        tutors = await self.repo.get_all_tutors()
        updated = 0
        for t in tutors:
            avg = await self.repo.get_tutor_avg_rating_scalar(t.tutor_id)
            if avg is not None:
                t.rating = float(avg)
                updated += 1
        await self.repo.commit()
        return {"message": f"Updated ratings for {updated} tutors",
                "total_tutors": len(tutors), "updated_count": updated}

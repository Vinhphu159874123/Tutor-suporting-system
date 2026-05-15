"""
Reports Service
Business logic for analytics and reporting
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.repositories.report_repository import ReportRepository
from app.core.cache import get_or_load


class ReportsService:
    def __init__(self, repo: ReportRepository):
        self.repo = repo

    async def get_system_statistics(self) -> Dict[str, Any]:
        async def _load():
            total_sessions = await self.repo.count_sessions()
            completed_sessions = await self.repo.count_completed_sessions()
            active_students = await self.repo.count_students()
            avg_rating = await self.repo.avg_feedback_rating()
            tutor_hours = completed_sessions
            return {
                "completed_sessions": completed_sessions,
                "active_students": active_students,
                "average_satisfaction": round(float(avg_rating), 1) if avg_rating else 0.0,
                "tutor_hours": tutor_hours,
                "total_sessions": total_sessions,
                "completion_rate": round((completed_sessions / total_sessions * 100) if total_sessions > 0 else 0, 1),
            }
        return await get_or_load("reports:statistics", _load, ttl=60)

    async def get_course_reports(self) -> List[dict]:
        rows = await self.repo.get_course_report_rows()
        courses_list = []
        for row in rows:
            total = row.total_sessions or 0
            completed = row.completed_sessions or 0
            completion = round((completed / total * 100) if total > 0 else 0, 0)
            courses_list.append({
                "id": str(row.subject_id),
                "course": row.subject_name,
                "faculty": "CS",
                "completion": int(completion),
                "averageScore": round(float(row.avg_score or 0), 1),
                "tutorHours": completed,
                "activeStudents": 0,
            })
        return courses_list

    async def get_tutor_performance(
        self, tutor_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        row = await self.repo.get_tutor_performance_row(
            tutor_id, start_date=start_date, end_date=end_date
        )
        return {
            "tutor_id": tutor_id,
            "total_sessions": row.total_sessions or 0,
            "completed_sessions": row.completed_sessions or 0,
            "average_rating": round(float(row.avg_rating or 0), 1),
            "completion_rate": round(
                (row.completed_sessions / row.total_sessions * 100)
                if row.total_sessions and row.total_sessions > 0 else 0, 1
            ),
        }

    async def get_student_progress_report(
        self, student_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        row = await self.repo.get_student_progress_row(
            student_id, start_date=start_date, end_date=end_date
        )
        return {
            "student_id": student_id,
            "total_sessions": row.total_sessions or 0,
            "attended_sessions": row.attended_sessions or 0,
            "attendance_rate": round(
                (row.attended_sessions / row.total_sessions * 100)
                if row.total_sessions and row.total_sessions > 0 else 0, 1
            ),
            "average_understanding": round(float(row.avg_understanding or 0), 1),
        }

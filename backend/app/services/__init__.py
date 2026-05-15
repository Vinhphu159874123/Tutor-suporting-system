"""
Services package — business logic layer
Each service encapsulates DB queries and business rules.
Controllers should only call service methods, never access the DB directly.
"""
from app.services.auth_service import AuthService
from app.services.student_service import StudentService
from app.services.tutor_service import TutorService
from app.services.session_service import SessionService
from app.services.scheduling_service import SchedulingService
from app.services.study_groups_service import StudyGroupsService
from app.services.admin_service import AdminService
from app.services.reports_service import ReportsService
from app.services.notifications_service import NotificationsService
from app.services.courses_service import CoursesService
from app.services.forum_service import ForumService
from app.services.progress_service import ProgressService
from app.services.users_service import UsersService
from app.services.schedule_preferences_service import SchedulePreferencesService
from app.services.coordinator_service import CoordinatorService

__all__ = [
    "AuthService",
    "StudentService",
    "TutorService",
    "SessionService",
    "SchedulingService",
    "StudyGroupsService",
    "AdminService",
    "ReportsService",
    "NotificationsService",
    "CoursesService",
    "ForumService",
    "ProgressService",
    "UsersService",
    "SchedulePreferencesService",
    "CoordinatorService",
]
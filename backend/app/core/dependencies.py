"""
Dependency Injection
Provide instances of services and repositories
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status

from app.core.database import get_db
from app.core.config import settings

# --- Existing Repositories ---
from app.repositories.user_repository import UserRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.tutor_repository import TutorRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.scheduling_repository import SchedulingRepository
from app.repositories.feedback_repository import FeedbackRepository

# --- New Repositories ---
from app.repositories.notification_repository import NotificationRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.forum_repository import ForumRepository
from app.repositories.admin_repository import AdminRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.users_repository import UsersRepository
from app.repositories.coordinator_repository import CoordinatorRepository
from app.repositories.study_group_repository import StudyGroupRepository
from app.repositories.schedule_preference_repository import SchedulePreferenceRepository

# --- Services ---
from app.services.auth_service import AuthService
from app.services.student_service import StudentService
from app.services.tutor_service import TutorService
from app.services.session_service import SessionService
from app.services.scheduling_service import SchedulingService
from app.services.admin_service import AdminService
from app.services.reports_service import ReportsService
from app.services.notifications_service import NotificationsService
from app.services.courses_service import CoursesService
from app.services.forum_service import ForumService
from app.services.progress_service import ProgressService
from app.services.users_service import UsersService
from app.services.coordinator_service import CoordinatorService
from app.services.study_groups_service import StudyGroupsService
from app.services.schedule_preferences_service import SchedulePreferencesService

from app.schemas.auth import TokenData

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ============================================================================
# REPOSITORY DEPENDENCIES
# ============================================================================

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Get User Repository instance"""
    return UserRepository(db)

def get_student_repository(db: AsyncSession = Depends(get_db)) -> StudentRepository:
    """Get Student Repository instance"""
    return StudentRepository(db)

def get_tutor_repository(db: AsyncSession = Depends(get_db)) -> TutorRepository:
    """Get Tutor Repository instance"""
    return TutorRepository(db)

def get_session_repository(db: AsyncSession = Depends(get_db)) -> SessionRepository:
    """Get Session Repository instance"""
    return SessionRepository(db)

def get_scheduling_repository(db: AsyncSession = Depends(get_db)) -> SchedulingRepository:
    """Get Scheduling Repository instance"""
    return SchedulingRepository(db)

def get_feedback_repository(db: AsyncSession = Depends(get_db)) -> FeedbackRepository:
    """Get Feedback Repository instance"""
    return FeedbackRepository(db)

def get_notification_repository(db: AsyncSession = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)

def get_course_repository(db: AsyncSession = Depends(get_db)) -> CourseRepository:
    return CourseRepository(db)

def get_forum_repository(db: AsyncSession = Depends(get_db)) -> ForumRepository:
    return ForumRepository(db)

def get_admin_repository(db: AsyncSession = Depends(get_db)) -> AdminRepository:
    return AdminRepository(db)

def get_report_repository(db: AsyncSession = Depends(get_db)) -> ReportRepository:
    return ReportRepository(db)

def get_progress_repository(db: AsyncSession = Depends(get_db)) -> ProgressRepository:
    return ProgressRepository(db)

def get_users_repository(db: AsyncSession = Depends(get_db)) -> UsersRepository:
    return UsersRepository(db)

def get_coordinator_repository(db: AsyncSession = Depends(get_db)) -> CoordinatorRepository:
    return CoordinatorRepository(db)

def get_study_group_repository(db: AsyncSession = Depends(get_db)) -> StudyGroupRepository:
    return StudyGroupRepository(db)

def get_schedule_preference_repository(db: AsyncSession = Depends(get_db)) -> SchedulePreferenceRepository:
    return SchedulePreferenceRepository(db)

# ============================================================================
# SERVICE DEPENDENCIES
# ============================================================================

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """Get Auth Service instance"""
    return AuthService(user_repo)

def get_student_service(
    student_repo: StudentRepository = Depends(get_student_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
) -> StudentService:
    """Get Student Service instance"""
    return StudentService(student_repo, user_repo, feedback_repo)

def get_tutor_service(
    tutor_repo: TutorRepository = Depends(get_tutor_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository),
    student_repo: StudentRepository = Depends(get_student_repository),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
) -> TutorService:
    """Get Tutor Service instance with all required repositories"""
    return TutorService(tutor_repo, user_repo, session_repo, student_repo, feedback_repo)

def get_session_service(
    session_repo: SessionRepository = Depends(get_session_repository)
) -> SessionService:
    """Get Session Service instance"""
    return SessionService(session_repo)

def get_scheduling_service(
    scheduling_repo: SchedulingRepository = Depends(get_scheduling_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
) -> SchedulingService:
    """Get Scheduling Service instance"""
    return SchedulingService(scheduling_repo, session_repo)

def get_admin_service(
    repo: AdminRepository = Depends(get_admin_repository)
) -> AdminService:
    return AdminService(repo)

def get_reports_service(
    repo: ReportRepository = Depends(get_report_repository)
) -> ReportsService:
    return ReportsService(repo)

def get_notifications_service(
    repo: NotificationRepository = Depends(get_notification_repository)
) -> NotificationsService:
    return NotificationsService(repo)

def get_courses_service(
    repo: CourseRepository = Depends(get_course_repository)
) -> CoursesService:
    return CoursesService(repo)

def get_forum_service(
    repo: ForumRepository = Depends(get_forum_repository)
) -> ForumService:
    return ForumService(repo)

def get_progress_service(
    repo: ProgressRepository = Depends(get_progress_repository)
) -> ProgressService:
    return ProgressService(repo)

def get_users_service(
    repo: UsersRepository = Depends(get_users_repository)
) -> UsersService:
    return UsersService(repo)

def get_coordinator_service(
    repo: CoordinatorRepository = Depends(get_coordinator_repository)
) -> CoordinatorService:
    return CoordinatorService(repo)

def get_study_groups_service(
    repo: StudyGroupRepository = Depends(get_study_group_repository)
) -> StudyGroupsService:
    return StudyGroupsService(repo)

def get_schedule_preferences_service(
    repo: SchedulePreferenceRepository = Depends(get_schedule_preference_repository)
) -> SchedulePreferencesService:
    return SchedulePreferencesService(repo)

# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Get current authenticated user from JWT token
    Used as dependency in protected routes
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await user_repo.get_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    
    # Load student_id or tutor_id from relationships
    if hasattr(user, 'student') and user.student:
        user.student_id = user.student.student_id
    else:
        user.student_id = None
        
    if hasattr(user, 'tutor') and user.tutor:
        user.tutor_id = user.tutor.tutor_id
    else:
        user.tutor_id = None
    
    return user

async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Get current authenticated user from JWT token (optional - returns None if not authenticated)
    Used for endpoints that can work with or without authentication
    """
    if not token:
        return None
        
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
    except JWTError:
        return None
    
    user = await user_repo.get_by_email(token_data.email)
    if user is None:
        return None
    
    # Load student_id or tutor_id from relationships
    if hasattr(user, 'student') and user.student:
        user.student_id = user.student.student_id
    else:
        user.student_id = None
        
    if hasattr(user, 'tutor') and user.tutor:
        user.tutor_id = user.tutor.tutor_id
    else:
        user.tutor_id = None
    
    return user

async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """Get current active user (not suspended)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Inactive user"
        )
    return current_user

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
from app.repositories.user_repository import UserRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.tutor_repository import TutorRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.scheduling_repository import SchedulingRepository
from app.repositories.reports_repository import ReportsRepository
from app.repositories.admin_repository import AdminRepository
from app.repositories.forum_repository import ForumRepository
from app.services.auth_service import AuthService
from app.services.student_service import StudentService
from app.services.tutor_service import TutorService
from app.services.session_service import SessionService
from app.services.scheduling_service import SchedulingService
from app.services.reports_service import ReportsService
from app.services.admin_service import AdminService
from app.services.forum_service import ForumService
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

def get_reports_repository(db: AsyncSession = Depends(get_db)) -> ReportsRepository:
    """Get Reports Repository instance"""
    return ReportsRepository(db)

def get_admin_repository(db: AsyncSession = Depends(get_db)) -> AdminRepository:
    """Get Admin Repository instance"""
    return AdminRepository(db)

def get_forum_repository(db: AsyncSession = Depends(get_db)) -> ForumRepository:
    """Get Forum Repository instance"""
    return ForumRepository(db)

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
    user_repo: UserRepository = Depends(get_user_repository)
) -> StudentService:
    """Get Student Service instance"""
    return StudentService(student_repo, user_repo)

def get_tutor_service(
    tutor_repo: TutorRepository = Depends(get_tutor_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> TutorService:
    """Get Tutor Service instance"""
    return TutorService(tutor_repo, user_repo)

def get_session_service(
    session_repo: SessionRepository = Depends(get_session_repository)
) -> SessionService:
    """Get Session Service instance"""
    return SessionService(session_repo)

def get_scheduling_service(
    scheduling_repo: SchedulingRepository = Depends(get_scheduling_repository)
) -> SchedulingService:
    """Get Scheduling Service instance"""
    return SchedulingService(scheduling_repo)

def get_reports_service(
    reports_repo: ReportsRepository = Depends(get_reports_repository)
) -> ReportsService:
    """Get Reports Service instance"""
    return ReportsService(reports_repo)

def get_admin_service(
    admin_repo: AdminRepository = Depends(get_admin_repository)
) -> AdminService:
    """Get Admin Service instance"""
    return AdminService(admin_repo)

def get_forum_service(
    forum_repo: ForumRepository = Depends(get_forum_repository)
) -> ForumService:
    """Get Forum Service instance"""
    return ForumService(forum_repo)

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

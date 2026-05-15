"""
Authentication Routes - Layered Architecture
Routes only handle HTTP layer, business logic in AuthService
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import Token, UserCreate, UserResponse, ChangePasswordRequest
from app.services.auth_service import AuthService
from app.services.hcmut_sso import HCMUTSSOService
from app.core.dependencies import get_auth_service, get_current_user
from app.models.database import User

router = APIRouter()

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with email/password using local database + JWT
    
    Flow:
    1. Authenticate against local database
    2. Verify password hash with bcrypt
    3. Return JWT access token
    
    Note: Auto-appends @hcmut.edu.vn if username doesn't contain @
    """
    # Auto-append @hcmut.edu.vn if not present
    username = form_data.username
    if '@' not in username:
        username = f"{username}@hcmut.edu.vn"
    
    # OPTIMIZATION: Use local authentication only (SSO disabled)
    # SSO was causing 2s delay on every login due to timeout
    token = await auth_service.login(username, form_data.password)
    return token


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register new user (without password for SSO)
    
    Note: This creates unverified account, needs admin approval
    """
    user = await auth_service.register(user_data)
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user profile
    
    Requires: Valid JWT token in Authorization header
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout():
    """
    Logout user (client-side token removal)
    
    Note: JWT tokens are stateless, client must discard token
    """
    return {"message": "Successfully logged out"}


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh JWT access token
    
    Requires: Valid (possibly expiring soon) JWT token
    Returns: New JWT token with extended expiration
    """
    new_token = auth_service.create_access_token({"sub": current_user.email})
    return Token(access_token=new_token, token_type="bearer")


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Change user password
    
    Requires: Valid JWT token and correct current password
    """
    return await auth_service.change_password(
        current_user.user_id,
        request.current_password,
        request.new_password
    )
"""
Authentication Service
Business logic for authentication operations
"""
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from typing import Optional

from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate, UserResponse, Token
from app.core.config import settings

class AuthService:
    """Handle authentication business logic"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash using bcrypt
        """
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash password using bcrypt
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    async def authenticate_user(self, email: str, password: str):
        """Authenticate user with email and password"""
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user has hashed password (not SSO-only user)
        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please login through HCMUT SSO",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
    
    async def login(self, email: str, password: str) -> Token:
        """Login user and return JWT token"""
        # Auto-append @hcmut.edu.vn if not present
        if '@' not in email:
            email = f"{email}@hcmut.edu.vn"
        
        user = await self.authenticate_user(email, password)
        
        # Update last login
        await self.user_repo.update(user.user_id, {"updated_at": datetime.utcnow()})
        
        # Create access token
        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = self.create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    async def login_with_sso(self, sso_user: dict) -> Token:
        """Login or create user from HCMUT SSO data"""
        # Check if user exists
        user = await self.user_repo.get_by_email(sso_user["email"])
        
        if not user:
            # Create new user from SSO data
            user_data = {
                "email": sso_user["email"],
                "full_name": sso_user["full_name"],
                "role": "student",  # Default role
                "faculty": sso_user.get("faculty"),
                "major": sso_user.get("major"),
                "sso_id": sso_user["id"],
                "is_verified": True,
                "is_active": True
            }
            user = await self.user_repo.create(user_data)
        
        # Update last login
        await self.user_repo.update(user.user_id, {"updated_at": datetime.utcnow()})
        
        # Create access token
        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = self.create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    async def register(self, user_data: UserCreate) -> UserResponse:
        """Register new user"""
        # Check if user already exists
        if await self.user_repo.exists_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user with hashed password
        user_dict = user_data.model_dump()
        
        # Remove fields that belong to Student/Tutor tables, not User table
        faculty = user_dict.pop('faculty', None)
        major = user_dict.pop('major', None)
        
        # Hash the password
        password = user_dict.pop('password')
        user_dict['hashed_password'] = self.get_password_hash(password)
        
        user_dict['is_verified'] = False
        user_dict['is_active'] = True
        
        user = await self.user_repo.create(user_dict)
        
        # TODO: Create Student or Tutor record with faculty/major based on role
        # This should be implemented when we have Student/Tutor repositories
        
        return UserResponse.model_validate(user)
    
    async def get_user_by_email(self, email: str):
        """Get user by email for dependency injection"""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

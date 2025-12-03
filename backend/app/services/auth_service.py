"""
Authentication Service
Business logic for authentication operations
"""
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from typing import Optional
from sqlalchemy import select

from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate, UserResponse, Token
from app.core.config import settings
from app.models.database import Student

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
        """Login or create user from HCMUT SSO data, auto-create Student profile"""
        # Check if user exists
        user = await self.user_repo.get_by_email(sso_user["email"])
        
        if not user:
            # Create new user from SSO data
            user_data = {
                "email": sso_user["email"],
                "full_name": sso_user["full_name"],
                "role": ["student"],  # Default role as array
                "faculty": sso_user.get("faculty"),
                "major": sso_user.get("major"),
                "sso_id": sso_user["id"],
                "is_verified": True,
                "is_active": True
            }
            user = await self.user_repo.create(user_data)
            
            # Auto-create Student profile for SSO users
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                new_student = Student(
                    user_id=user.user_id,
                    student_code=f'SV{user.user_id:06d}',
                    faculty=sso_user.get("faculty") or 'Computer Science',
                    major=sso_user.get("major") or 'Computer Science',
                    year=1
                )
                db.add(new_student)
                await db.commit()
                print(f"✅ Auto-created student profile for SSO user {user.email}")
        else:
            # Check if existing user has student profile
            if 'student' in user.role:  # Check if student in role array
                from app.core.database import AsyncSessionLocal
                async with AsyncSessionLocal() as db:
                    result = await db.execute(
                        select(Student).where(Student.user_id == user.user_id)
                    )
                    existing_student = result.scalar_one_or_none()
                    
                    if not existing_student:
                        # Create missing student profile
                        new_student = Student(
                            user_id=user.user_id,
                            student_code=f'SV{user.user_id:06d}',
                            faculty=sso_user.get("faculty") or 'Computer Science',
                            major=sso_user.get("major") or 'Computer Science',
                            year=1
                        )
                        db.add(new_student)
                        await db.commit()
                        print(f"✅ Created missing student profile for existing user {user.email}")
        
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
        """Register new user and auto-create Student profile if role is student"""
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
        student_code = user_dict.pop('student_code', None)
        year = user_dict.pop('year', None)
        role = user_dict.get('role', 'student')
        
        # Hash the password
        password = user_dict.pop('password')
        user_dict['hashed_password'] = self.get_password_hash(password)
        
        user_dict['is_verified'] = False
        user_dict['is_active'] = True
        
        user = await self.user_repo.create(user_dict)
        
        # Auto-create Student profile for student role
        if 'student' in (role if isinstance(role, list) else [role]):  # Support both array and string
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                # Check if student profile already exists
                result = await db.execute(
                    select(Student).where(Student.user_id == user.user_id)
                )
                existing_student = result.scalar_one_or_none()
                
                if not existing_student:
                    # Validate student_code uniqueness if provided
                    final_student_code = student_code or f'SV{user.user_id:06d}'
                    
                    if student_code:
                        # Check if student_code already exists
                        code_check = await db.execute(
                            select(Student).where(Student.student_code == student_code)
                        )
                        if code_check.scalar_one_or_none():
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Mã số sinh viên {student_code} đã tồn tại!"
                            )
                    
                    # Create student profile with user-provided or auto-generated data
                    new_student = Student(
                        user_id=user.user_id,
                        student_code=final_student_code,
                        faculty=faculty or 'Computer Science',
                        major=major or 'Computer Science',
                        year=int(year) if year else 1
                    )
                    db.add(new_student)
                    await db.commit()
                    print(f"✅ Auto-created student profile for user {user.email} with code {new_student.student_code}")
        
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
    
    async def change_password(self, user_id: int, current_password: str, new_password: str):
        """Change user password"""
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user has local password (not SSO-only)
        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change password for SSO-only accounts"
            )
        
        # Verify current password
        if not self.verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Hash new password and update
        new_hashed_password = self.get_password_hash(new_password)
        await self.user_repo.update(user_id, {"hashed_password": new_hashed_password})
        
        return {"message": "Password changed successfully"}

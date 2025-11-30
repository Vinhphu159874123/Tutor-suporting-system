"""
Script to create demo users for testing
"""
import asyncio
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.database import User
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_demo_users():
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if users already exist
        from sqlalchemy import select
        result = await session.execute(select(User).filter(User.email == "student@hcmut.edu.vn"))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("Demo users already exist!")
            return
        
        # Create demo users
        hashed_password = pwd_context.hash("password123")
        
        demo_users = [
            User(
                email="student@hcmut.edu.vn",
                full_name="Nguyễn Văn A",
                hashed_password=hashed_password,
                role="student",
                faculty="Khoa Khoa học và Kỹ thuật Máy tính",
                major="Khoa học Máy tính",
                phone="0123456789",
                is_active=True,
                is_verified=True,
                student_id="2112345"
            ),
            User(
                email="tutor@hcmut.edu.vn",
                full_name="Trần Thị B",
                hashed_password=hashed_password,
                role="tutor",
                faculty="Khoa Khoa học và Kỹ thuật Máy tính",
                major="Khoa học Máy tính",
                phone="0987654321",
                is_active=True,
                is_verified=True,
                student_id="2012345"
            ),
            User(
                email="admin@hcmut.edu.vn",
                full_name="Quản Trị Viên",
                hashed_password=hashed_password,
                role="admin",
                is_active=True,
                is_verified=True,
                staff_id="GV001"
            ),
        ]
        
        for user in demo_users:
            session.add(user)
        
        await session.commit()
        print("✅ Demo users created successfully!")
        print("\nDemo accounts:")
        print("1. Student: student@hcmut.edu.vn / password123")
        print("2. Tutor: tutor@hcmut.edu.vn / password123")
        print("3. Admin: admin@hcmut.edu.vn / password123")

if __name__ == "__main__":
    asyncio.run(create_demo_users())

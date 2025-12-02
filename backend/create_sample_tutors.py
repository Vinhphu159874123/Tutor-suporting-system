"""
Create sample tutors and their availability
Run: python -m backend.create_sample_tutors
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.database import User, Tutor, TutorAvailability
from app.core.config import settings
from datetime import time

async def create_sample_tutors():
    """Create sample tutors with availability"""
    
    # Get database URL from settings
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # Create async engine
    engine = create_async_engine(database_url, echo=True)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Sample tutors data
        tutors_data = [
            {
                "email": "tutor1@hcmut.edu.vn",
                "full_name": "Nguyễn Văn Hòa",
                "faculty": "Computer Science",
                "subjects": ["CO2013 - Database Systems", "CO1027 - Data Structures and Algorithms"],
                "hourly_rate": 150000,
                "bio": "Giảng viên CSE, chuyên Data Structures",
                "experience_years": 5,
                "availability": [
                    (1, time(14, 0), time(16, 0)),  # Thứ 3, 14:00-16:00
                    (1, time(18, 0), time(20, 0)),  # Thứ 3, 18:00-20:00
                    (3, time(14, 0), time(16, 0)),  # Thứ 5, 14:00-16:00
                ]
            },
            {
                "email": "tutor2@hcmut.edu.vn",
                "full_name": "Trần Thị Mai",
                "faculty": "Mathematics",
                "subjects": ["MATH101 - Toán Cao Cấp 1", "MT1003 - Calculus 1"],
                "hourly_rate": 120000,
                "bio": "Giáo viên Toán, 3 năm kinh nghiệm",
                "experience_years": 3,
                "availability": [
                    (0, time(8, 0), time(10, 0)),   # Thứ 2, 8:00-10:00
                    (2, time(14, 0), time(16, 0)),  # Thứ 4, 14:00-16:00
                    (4, time(16, 0), time(18, 0)),  # Thứ 6, 16:00-18:00
                ]
            },
            {
                "email": "tutor3@hcmut.edu.vn",
                "full_name": "Lê Minh Tuấn",
                "faculty": "Electrical Engineering",
                "subjects": ["EE2003 - Circuit Analysis", "PH1003 - Physics 1"],
                "hourly_rate": 180000,
                "bio": "Kỹ sư Điện, chuyên môn mạch điện",
                "experience_years": 7,
                "availability": [
                    (1, time(9, 0), time(11, 0)),   # Thứ 3, 9:00-11:00
                    (3, time(13, 0), time(15, 0)),  # Thứ 5, 13:00-15:00
                    (5, time(10, 0), time(12, 0)),  # Thứ 7, 10:00-12:00
                ]
            },
        ]
        
        for tutor_data in tutors_data:
            # Check if user exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == tutor_data["email"])
            )
            user = result.scalar_one_or_none()
            
            if not user:
                # Create user (use simple hash for demo)
                import hashlib
                hashed_pw = hashlib.sha256("password123".encode()).hexdigest()
                
                user = User(
                    email=tutor_data["email"],
                    hashed_password=hashed_pw,
                    full_name=tutor_data["full_name"],
                    role="tutor",
                    is_active=True,
                    is_verified=True
                )
                session.add(user)
                await session.flush()
                print(f"✅ Created user: {user.full_name}")
            
            # Check if tutor profile exists
            result = await session.execute(
                select(Tutor).where(Tutor.user_id == user.user_id)
            )
            tutor = result.scalar_one_or_none()
            
            if not tutor:
                # Create tutor profile
                tutor = Tutor(
                    user_id=user.user_id,
                    faculty=tutor_data["faculty"],
                    hourly_rate=tutor_data["hourly_rate"],
                    bio=tutor_data["bio"],
                    teaching_experience={"years": tutor_data["experience_years"]},
                    rating=4.5,
                    total_sessions=0,
                    is_verified=True
                )
                session.add(tutor)
                await session.flush()
                print(f"✅ Created tutor profile: {user.full_name}")
                
                # Note: subjects stored in teaching_experience JSON
                # In real app, might use TutorRegistration table
                
                # Create availability
                for day, start_time, end_time in tutor_data["availability"]:
                    availability = TutorAvailability(
                        tutor_id=tutor.tutor_id,
                        day_of_week=day,
                        start_time=start_time,
                        end_time=end_time
                    )
                    session.add(availability)
                
                print(f"✅ Created {len(tutor_data['availability'])} availability slots")
            else:
                print(f"⚠️  Tutor already exists: {user.full_name}")
        
        await session.commit()
        print("\n🎉 Sample tutors created successfully!")
        print("\nLogin credentials:")
        print("Email: tutor1@hcmut.edu.vn | Password: password123")
        print("Email: tutor2@hcmut.edu.vn | Password: password123")
        print("Email: tutor3@hcmut.edu.vn | Password: password123")

if __name__ == "__main__":
    asyncio.run(create_sample_tutors())

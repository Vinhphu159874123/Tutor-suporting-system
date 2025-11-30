"""
Create Student profile for student@hcmut.edu.vn test user
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import get_db
from app.models.database import User, Student


async def create_student_profile():
    """Create Student profile for test user"""
    async for db in get_db():
        try:
            # Get student user
            result = await db.execute(
                select(User).where(User.email == "student@hcmut.edu.vn")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ User student@hcmut.edu.vn not found!")
                return
            
            print(f"✓ Found user: {user.full_name} (ID: {user.user_id})")
            
            # Check if student profile already exists
            result = await db.execute(
                select(Student).where(Student.user_id == user.user_id)
            )
            existing_student = result.scalar_one_or_none()
            
            if existing_student:
                print(f"✓ Student profile already exists: {existing_student.student_code}")
                return
            
            # Create student profile
            student = Student(
                user_id=user.user_id,
                student_code="2210001",  # Matches mock DATACORE data
                faculty="Computer Science",
                major="Software Engineering",
                year=3,
                preferences={}
            )
            
            db.add(student)
            await db.commit()
            
            print(f"✅ Created student profile: {student.student_code}")
            print(f"   Faculty: {student.faculty}")
            print(f"   Major: {student.major}")
            print(f"   Year: {student.year}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
        finally:
            break


if __name__ == "__main__":
    asyncio.run(create_student_profile())

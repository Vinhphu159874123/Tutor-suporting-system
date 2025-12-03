"""
Create student profile for nhan.nguyenpercy account
Run with: python3 create_student_for_nhan.py
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.database import User, Student

async def create_student_profile():
    """Create student profile for nhan.nguyenpercy"""
    async with AsyncSessionLocal() as db:
        try:
            print("\n" + "="*80)
            print("CREATING STUDENT PROFILE FOR nhan.nguyenpercy")
            print("="*80 + "\n")
            
            # Find user by username
            username = "nhan.nguyenpercy"
            user_query = select(User).where(User.username == username)
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                print(f"❌ User '{username}' not found!")
                print(f"Please make sure this account exists in the database")
                return
            
            print(f"✓ Found user: {user.full_name} ({user.email})")
            print(f"  User ID: {user.user_id}")
            print(f"  Role: {user.role}")
            
            # Check if student profile already exists
            student_query = select(Student).where(Student.user_id == user.user_id)
            student_result = await db.execute(student_query)
            existing_student = student_result.scalar_one_or_none()
            
            if existing_student:
                print(f"\n✓ Student profile already exists!")
                print(f"  Student ID: {existing_student.student_id}")
                print(f"  Student Code: {existing_student.student_code}")
                print(f"  Major: {existing_student.major}")
                return
            
            # Create student profile
            new_student = Student(
                user_id=user.user_id,
                student_code=f"SV{user.user_id:06d}",  # Generate student code
                major="Computer Science",  # Default major
                year_of_study=2,  # Default year
                gpa=3.5  # Default GPA
            )
            
            db.add(new_student)
            await db.commit()
            await db.refresh(new_student)
            
            print(f"\n✅ Successfully created student profile!")
            print(f"  Student ID: {new_student.student_id}")
            print(f"  Student Code: {new_student.student_code}")
            print(f"  Major: {new_student.major}")
            print(f"  Year: {new_student.year_of_study}")
            print(f"  GPA: {new_student.gpa}")
            
            print("\n" + "="*80)
            print("✅ DONE! You can now use schedule preferences feature")
            print("="*80 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await db.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_student_profile())

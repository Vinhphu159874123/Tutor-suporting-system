"""
Script to create test accounts for testing
Creates 4 accounts: student113, tutor113, coordinator113, admin113
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from app.core.database import get_db
from app.models.database import User, Student, Tutor
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TEST_ACCOUNTS = [
    {
        "email": "student113@hcmut.edu.vn",
        "password": "TestPass123!",
        "full_name": "Test Student 113",
        "role": ["student"],
        "student_id": "2211113"
    },
    {
        "email": "tutor113@hcmut.edu.vn",
        "password": "TestPass123!",
        "full_name": "Test Tutor 113",
        "role": ["tutor"],
        "student_id": "2011113"
    },
    {
        "email": "coordinator113@hcmut.edu.vn",
        "password": "TestPass123!",
        "full_name": "Test Coordinator 113",
        "role": ["coordinator"],
        "student_id": "1911113"
    },
    {
        "email": "admin113@hcmut.edu.vn",
        "password": "TestPass123!",
        "full_name": "Test Admin 113",
        "role": ["admin"],
        "student_id": "1811113"
    }
]

async def create_test_accounts():
    print("\n" + "="*80)
    print("CREATING TEST ACCOUNTS")
    print("="*80 + "\n")
    
    async for db in get_db():
        for account in TEST_ACCOUNTS:
            print(f"Creating {account['email']}...")
            
            # Check if user exists
            existing_user = await db.execute(
                select(User).where(User.email == account["email"])
            )
            existing_user = existing_user.scalar_one_or_none()
            
            if existing_user:
                print(f"  ⚠️  User already exists, updating...")
                # Update password and roles
                existing_user.hashed_password = pwd_context.hash(account["password"])
                existing_user.role = account["role"]
                existing_user.full_name = account["full_name"]
                user = existing_user
            else:
                # Create new user
                user = User(
                    email=account["email"],
                    hashed_password=pwd_context.hash(account["password"]),
                    full_name=account["full_name"],
                    role=account["role"],
                    student_id=account["student_id"],
                    is_active=True
                )
                db.add(user)
                await db.flush()
                print(f"  ✅ Created user")
            
            # Create student/tutor profile if needed
            if "student" in account["role"]:
                existing_student = await db.execute(
                    select(Student).where(Student.user_id == user.user_id)
                )
                if not existing_student.scalar_one_or_none():
                    student = Student(
                        user_id=user.user_id,
                        subjects_interested=["Mathematics", "Physics"],
                        learning_goals="Testing purposes"
                    )
                    db.add(student)
                    print(f"  ✅ Created student profile")
            
            if "tutor" in account["role"]:
                existing_tutor = await db.execute(
                    select(Tutor).where(Tutor.user_id == user.user_id)
                )
                if not existing_tutor.scalar_one_or_none():
                    tutor = Tutor(
                        user_id=user.user_id,
                        subjects_expertise=["Mathematics", "Physics"],
                        availability="Monday-Friday 9AM-5PM",
                        rating=4.5,
                        total_hours=10
                    )
                    db.add(tutor)
                    print(f"  ✅ Created tutor profile")
            
            await db.commit()
            print(f"✅ {account['email']} ready!\n")
    
    print("\n" + "="*80)
    print("TEST ACCOUNTS CREATED SUCCESSFULLY")
    print("="*80)
    print("\nCredentials:")
    for account in TEST_ACCOUNTS:
        print(f"  Email: {account['email']}")
        print(f"  Password: {account['password']}")
        print(f"  Role: {', '.join(account['role'])}")
        print()

if __name__ == "__main__":
    asyncio.run(create_test_accounts())

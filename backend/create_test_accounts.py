"""
Create test accounts for all roles
Run with: python3 create_test_accounts.py
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
from app.models.database import User, Student, Tutor, Coordinator
import bcrypt

async def create_test_accounts():
    """Create 4 test accounts for different roles"""
    async with AsyncSessionLocal() as db:
        try:
            print("\n" + "="*80)
            print("CREATING TEST ACCOUNTS FOR ALL ROLES")
            print("="*80 + "\n")
            
            # Hash password function
            def hash_password(password: str) -> str:
                password_bytes = password.encode('utf-8')
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password_bytes, salt)
                return hashed.decode('utf-8')
            
            accounts_created = []
            
            # ========================================================================
            # 1. ADMIN ACCOUNT
            # ========================================================================
            admin_email = "admin@hcmut.edu.vn"
            admin_query = select(User).where(User.email == admin_email)
            admin_result = await db.execute(admin_query)
            admin_user = admin_result.scalar_one_or_none()
            
            if not admin_user:
                admin_user = User(
                    email=admin_email,
                    hashed_password=hash_password("admin123"),
                    full_name="Admin Nguyễn",
                    role="admin",
                    phone="0901234567",
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                await db.flush()
                accounts_created.append({
                    "role": "admin",
                    "email": admin_email,
                    "password": "admin123",
                    "name": admin_user.full_name
                })
                print(f"✅ Created ADMIN account: {admin_email}")
            else:
                print(f"⚠️  ADMIN account already exists: {admin_email}")
            
            # ========================================================================
            # 2. COORDINATOR ACCOUNT
            # ========================================================================
            coord_email = "coordinator@hcmut.edu.vn"
            coord_query = select(User).where(User.email == coord_email)
            coord_result = await db.execute(coord_query)
            coord_user = coord_result.scalar_one_or_none()
            
            if not coord_user:
                coord_user = User(
                    email=coord_email,
                    hashed_password=hash_password("coord123"),
                    full_name="Coordinator Trần",
                    role="coordinator",
                    phone="0901234568",
                    is_active=True,
                    is_verified=True
                )
                db.add(coord_user)
                await db.flush()
                
                # Create Coordinator profile
                coordinator_profile = Coordinator(
                    user_id=coord_user.user_id,
                    department="Khoa Khoa học và Kỹ thuật Máy tính",
                    assigned_subjects=[],
                    workload=0
                )
                db.add(coordinator_profile)
                
                accounts_created.append({
                    "role": "coordinator",
                    "email": coord_email,
                    "password": "coord123",
                    "name": coord_user.full_name
                })
                print(f"✅ Created COORDINATOR account: {coord_email}")
            else:
                print(f"⚠️  COORDINATOR account already exists: {coord_email}")
            
            # ========================================================================
            # 3. TUTOR ACCOUNT
            # ========================================================================
            tutor_email = "tutor@hcmut.edu.vn"
            tutor_query = select(User).where(User.email == tutor_email)
            tutor_result = await db.execute(tutor_query)
            tutor_user = tutor_result.scalar_one_or_none()
            
            if not tutor_user:
                tutor_user = User(
                    email=tutor_email,
                    hashed_password=hash_password("tutor123"),
                    full_name="Tutor Lê",
                    role="tutor",
                    phone="0901234569",
                    is_active=True,
                    is_verified=True
                )
                db.add(tutor_user)
                await db.flush()
                
                # Create Tutor profile
                tutor_profile = Tutor(
                    user_id=tutor_user.user_id,
                    staff_code="TC2024001",
                    faculty="Khoa Khoa học và Kỹ thuật Máy tính",
                    bio="Tutor chuyên môn Toán & Lập trình",
                    hourly_rate=150000,
                    rating=4.7,
                    total_sessions=15,
                    is_verified=True
                )
                db.add(tutor_profile)
                
                accounts_created.append({
                    "role": "tutor",
                    "email": tutor_email,
                    "password": "tutor123",
                    "name": tutor_user.full_name
                })
                print(f"✅ Created TUTOR account: {tutor_email}")
            else:
                print(f"⚠️  TUTOR account already exists: {tutor_email}")
            
            # ========================================================================
            # 4. STUDENT ACCOUNT
            # ========================================================================
            student_email = "student@hcmut.edu.vn"
            student_query = select(User).where(User.email == student_email)
            student_result = await db.execute(student_query)
            student_user = student_result.scalar_one_or_none()
            
            if not student_user:
                student_user = User(
                    email=student_email,
                    hashed_password=hash_password("student123"),
                    full_name="Student Phạm",
                    role="student",
                    phone="0901234570",
                    is_active=True,
                    is_verified=True
                )
                db.add(student_user)
                await db.flush()
                
                # Create Student profile
                student_profile = Student(
                    user_id=student_user.user_id,
                    student_code="2052001",
                    year_of_study=2,
                    gpa=3.5
                )
                db.add(student_profile)
                
                accounts_created.append({
                    "role": "student",
                    "email": student_email,
                    "password": "student123",
                    "name": student_user.full_name
                })
                print(f"✅ Created STUDENT account: {student_email}")
            else:
                print(f"⚠️  STUDENT account already exists: {student_email}")
            
            # Commit all changes
            await db.commit()
            
            # ========================================================================
            # SUMMARY
            # ========================================================================
            print("\n" + "="*80)
            print("TEST ACCOUNTS SUMMARY")
            print("="*80 + "\n")
            
            if accounts_created:
                print("🎉 New accounts created:\n")
                for acc in accounts_created:
                    print(f"┌─ {acc['role'].upper()} ─────────────────────────────")
                    print(f"│  Name:     {acc['name']}")
                    print(f"│  Email:    {acc['email']}")
                    print(f"│  Password: {acc['password']}")
                    print(f"└────────────────────────────────────────────\n")
            else:
                print("ℹ️  All accounts already exist. No new accounts created.\n")
            
            print("\n📋 ALL TEST ACCOUNTS (including existing):\n")
            print("┌─ ADMIN ─────────────────────────────────")
            print("│  Username: admin")
            print("│  Email:    admin@hcmut.edu.vn")
            print("│  Password: admin123")
            print("└────────────────────────────────────────────\n")
            
            print("┌─ COORDINATOR ───────────────────────────")
            print("│  Username: coordinator")
            print("│  Email:    coordinator@hcmut.edu.vn")
            print("│  Password: coord123")
            print("└────────────────────────────────────────────\n")
            
            print("┌─ TUTOR ─────────────────────────────────")
            print("│  Username: tutor")
            print("│  Email:    tutor@hcmut.edu.vn")
            print("│  Password: tutor123")
            print("└────────────────────────────────────────────\n")
            
            print("┌─ STUDENT ───────────────────────────────")
            print("│  Username: student")
            print("│  Email:    student@hcmut.edu.vn")
            print("│  Password: student123")
            print("└────────────────────────────────────────────\n")
            
            print("\n💡 TIP: Bạn có thể login chỉ với username (không cần @hcmut.edu.vn)")
            print("   Ví dụ: username='admin', password='admin123'\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(create_test_accounts())

"""
Create Admin Account
Run this script to create an admin user in the database
"""
import asyncio
import bcrypt
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.database import User

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

async def create_admin():
    """Create admin user"""
    
    admin_data = {
        "email": "admin@hcmut.edu.vn",
        "full_name": "Admin User",
        "hashed_password": get_password_hash("admin123"),  # Change this password
        "role": "admin",
        "is_active": True,
        "is_verified": True,
        "phone": "0123456789",
        "faculty": "Khoa KH-KT Máy Tính",
        "major": "Quản trị hệ thống"
    }
    
    async with AsyncSessionLocal() as db:
        # Check if admin already exists
        result = await db.execute(
            select(User).where(User.email == admin_data["email"])
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"❌ Admin user already exists: {admin_data['email']}")
            print(f"   User ID: {existing_user.user_id}")
            print(f"   Role: {existing_user.role}")
            return
        
        # Create new admin user
        admin_user = User(**admin_data)
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: admin123")
        print(f"   User ID: {admin_user.user_id}")
        print(f"   Role: {admin_user.role}")
        print(f"\n⚠️  Please change the password after first login!")

if __name__ == "__main__":
    print("Creating admin account...")
    asyncio.run(create_admin())

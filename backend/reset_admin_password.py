"""
Reset Admin Password
Run this script to reset admin password
"""
import asyncio
import bcrypt
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.database import User

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

async def reset_admin_password():
    """Reset admin password to 'admin123'"""
    
    admin_email = "admin@hcmut.edu.vn"
    new_password = "admin123"
    
    async with AsyncSessionLocal() as db:
        # Find admin user
        result = await db.execute(
            select(User).where(User.email == admin_email)
        )
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            print(f"❌ Admin user not found: {admin_email}")
            return
        
        # Update password
        new_hash = get_password_hash(new_password)
        admin_user.hashed_password = new_hash
        await db.commit()
        
        print(f"✅ Password reset successfully!")
        print(f"   Email: {admin_email}")
        print(f"   New Password: {new_password}")
        print(f"   User ID: {admin_user.user_id}")
        print(f"   Role: {admin_user.role}")
        print(f"\n🔐 You can now login with these credentials")

if __name__ == "__main__":
    print("Resetting admin password...")
    asyncio.run(reset_admin_password())

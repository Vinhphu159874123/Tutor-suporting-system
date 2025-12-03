import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import get_db_session
from app.models.database import SessionMaterial, Session
from sqlalchemy import select

async def test_materials():
    """Test materials upload logic"""
    async with get_db_session() as db:
        # Check if we have any sessions
        result = await db.execute(select(Session).limit(5))
        sessions = result.scalars().all()
        
        print(f"\n📊 Found {len(sessions)} sessions")
        for session in sessions:
            print(f"   - Session {session.session_id}: {session.title or 'Untitled'}")
        
        # Check existing materials
        result = await db.execute(select(SessionMaterial))
        materials = result.scalars().all()
        
        print(f"\n📁 Found {len(materials)} materials in database")
        for material in materials:
            print(f"   - {material.file_name} ({material.file_size} bytes) - Session {material.session_id}")

if __name__ == "__main__":
    asyncio.run(test_materials())

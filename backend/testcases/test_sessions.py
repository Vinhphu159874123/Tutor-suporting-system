"""
Test Session Endpoints
Run: python test_sessions.py
"""
import asyncio
import sys
from datetime import datetime, timedelta, time, date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.repositories.session_repository import SessionRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.tutor_repository import TutorRepository
from app.repositories.admin_repository import AdminRepository
from app.services.session_service import SessionService
from app.schemas.session import SessionCreate, SessionUpdate


async def test_sessions():
    """Test session service methods"""
    print("🧪 Testing Session Service...")
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Initialize repositories
        session_repo = SessionRepository(db)
        student_repo = StudentRepository(db)
        tutor_repo = TutorRepository(db)
        
        # Initialize service
        session_service = SessionService(session_repo)
        
        print("\n1️⃣ Test: Get all sessions")
        try:
            sessions = await session_service.get_all_sessions(skip=0, limit=5)
            print(f"   ✅ Found {len(sessions)} sessions")
            if sessions:
                print(f"   📄 First session: ID={sessions[0].session_id}, Status={sessions[0].status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n2️⃣ Test: Get sessions by tutor")
        try:
            # Get first tutor
            tutors = await tutor_repo.get_all(skip=0, limit=1)
            if tutors:
                tutor_id = tutors[0].tutor_id
                sessions = await session_service.get_all_sessions(tutor_id=tutor_id, limit=5)
                print(f"   ✅ Found {len(sessions)} sessions for tutor {tutor_id}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n3️⃣ Test: Create new session")
        try:
            # Get first student, tutor and subject
            students = await student_repo.get_all(skip=0, limit=1)
            tutors = await tutor_repo.get_all(skip=0, limit=1)
            admin_repo = AdminRepository(db)
            
            # Get first subject
            from sqlalchemy import select
            from app.models.database import Subject
            result = await db.execute(select(Subject).limit(1))
            subject = result.scalar_one_or_none()
            
            if students and tutors and subject:
                session_data = SessionCreate(
                    tutor_id=tutors[0].tutor_id,
                    title="Test Session - Python Testing",
                    description="Test session created by test script",
                    subject_id=subject.subject_id,
                    scheduled_date=date.today() + timedelta(days=1),
                    start_time=time(10, 0),
                    end_time=time(11, 0),
                    duration=1,
                    location_type="online",
                    meeting_link="https://meet.google.com/test",
                    max_students=5,
                    student_ids=[students[0].student_id]
                )
                
                new_session = await session_service.create_session(session_data)
                print(f"   ✅ Created session ID={new_session.session_id}, Status={new_session.status}")
                
                # Store for later tests
                test_session_id = new_session.session_id
                
                print("\n4️⃣ Test: Get session by ID")
                try:
                    session = await session_service.get_session(test_session_id)
                    print(f"   ✅ Retrieved session ID={session.session_id}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                print("\n5️⃣ Test: Update session")
                try:
                    update_data = SessionUpdate(
                        description="Updated by test script",
                        meeting_link="https://meet.google.com/updated"
                    )
                    updated = await session_service.update_session(test_session_id, update_data)
                    print(f"   ✅ Updated session ID={updated.session_id}")
                    print(f"   📝 New description: {updated.description}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                print("\n6️⃣ Test: Complete session (should fail - wrong status)")
                try:
                    result = await session_service.complete_session(test_session_id)
                    print(f"   ⚠️  Unexpected success: {result}")
                except Exception as e:
                    print(f"   ✅ Expected error (status=draft): {str(e)[:100]}")
                
                print("\n7️⃣ Test: Update status to ongoing")
                try:
                    update_data = SessionUpdate(status="ongoing")
                    await session_service.update_session(test_session_id, update_data)
                    print(f"   ✅ Changed status to ongoing")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                print("\n8️⃣ Test: Complete session (should succeed)")
                try:
                    result = await session_service.complete_session(test_session_id)
                    print(f"   ✅ Session completed: {result['message']}")
                    print(f"   📊 Status: {result['status']}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                print("\n9️⃣ Test: Upload material")
                try:
                    material_data = {
                        "title": "Test Material",
                        "file_url": "https://example.com/material.pdf",
                        "type": "pdf",
                        "uploaded_by": tutors[0].user_id  # Add user_id
                    }
                    result = await session_service.upload_material(test_session_id, material_data)
                    print(f"   ✅ Material uploaded: {result['message']}")
                    if 'material_id' in result:
                        print(f"   📁 Material ID: {result['material_id']}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                print("\n🔟 Test: Verify material was saved")
                try:
                    # Query SessionMaterial directly instead of loading relationship
                    from app.models.database import SessionMaterial
                    result = await db.execute(
                        select(SessionMaterial).where(SessionMaterial.session_id == test_session_id)
                    )
                    materials = result.scalars().all()
                    if materials:
                        print(f"   ✅ Found {len(materials)} materials")
                        print(f"   📄 Material: {materials[0].file_name}")
                    else:
                        print(f"   ⚠️  No materials found")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                print("\n🗑️  Cleanup: Delete test session")
                try:
                    await session_repo.delete(test_session_id)
                    print(f"   ✅ Deleted session ID={test_session_id}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
            else:
                print("   ⚠️  No students or tutors found in database")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    await engine.dispose()
    print("\n✅ All tests completed!\n")


if __name__ == "__main__":
    asyncio.run(test_sessions())

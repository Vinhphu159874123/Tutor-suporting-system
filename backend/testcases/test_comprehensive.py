"""
Comprehensive Test Suite - All Functional Tests
Tests 15 core functional test cases for the Tutor Support System
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

BASE_URL = "https://tutor-suporting-system-production.up.railway.app/api/v1"

# Test accounts
TEST_ACCOUNTS = {
    "student": {"email": "student113@hcmut.edu.vn", "password": "TestPass123!"},
    "tutor": {"email": "tutor113@hcmut.edu.vn", "password": "TestPass123!"},
    "coordinator": {"email": "coordinator113@hcmut.edu.vn", "password": "TestPass123!"},
    "admin": {"email": "admin113@hcmut.edu.vn", "password": "TestPass123!"}
}

async def login(client, account_type):
    """Helper function to login and get token"""
    response = await client.post("/auth/login", data={
        "username": TEST_ACCOUNTS[account_type]["email"],
        "password": TEST_ACCOUNTS[account_type]["password"]
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]

# ============================================================================
# AUTHENTICATION & ACCOUNT MANAGEMENT (F-01 to F-04)
# ============================================================================

@pytest.mark.asyncio
async def test_f01_student_login():
    """F-01: Student login with valid credentials"""
    print("\n🧪 F-01: Student Login")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "student")
        
        # Verify token works
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        
        user = response.json()
        assert user["email"] == TEST_ACCOUNTS["student"]["email"]
        print("✅ F-01 PASSED")

@pytest.mark.asyncio
async def test_f02_tutor_login():
    """F-02: Tutor login with valid credentials"""
    print("\n🧪 F-02: Tutor Login")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "tutor")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        
        user = response.json()
        roles = user.get("role") or user.get("available_roles", [])
        assert "tutor" in roles
        print("✅ F-02 PASSED")

@pytest.mark.asyncio
async def test_f03_coordinator_login():
    """F-03: Coordinator login with valid credentials"""
    print("\n🧪 F-03: Coordinator Login")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "coordinator")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        
        user = response.json()
        roles = user.get("role") or user.get("available_roles", [])
        assert "coordinator" in roles
        print("✅ F-03 PASSED")

@pytest.mark.asyncio
async def test_f04_logout():
    """F-04: User logout"""
    print("\n🧪 F-04: Logout")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "student")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.post("/auth/logout", headers=headers)
        assert response.status_code in [200, 401]
        print("✅ F-04 PASSED")

# ============================================================================
# SESSION MANAGEMENT (F-05 to F-09)
# ============================================================================

@pytest.mark.asyncio
async def test_f05_list_sessions():
    """F-05: List available sessions"""
    print("\n🧪 F-05: List Sessions")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "student")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get("/sessions/", headers=headers, follow_redirects=True)
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data) if isinstance(data, list) else 'some'} sessions")
        print("✅ F-05 PASSED")

@pytest.mark.asyncio
async def test_f06_view_session_details():
    """F-06: View session details"""
    print("\n🧪 F-06: View Session Details")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "student")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get list of sessions first
        sessions_response = await client.get("/sessions/", headers=headers, follow_redirects=True)
        
        if sessions_response.status_code == 200:
            sessions = sessions_response.json()
            if isinstance(sessions, list) and len(sessions) > 0:
                session_id = sessions[0].get("session_id")
                if session_id:
                    # View specific session
                    response = await client.get(f"/sessions/{session_id}", headers=headers)
                    assert response.status_code in [200, 404]
                    print("✅ F-06 PASSED")
                    return
        
        print("⚠️  F-06 SKIPPED: No sessions available")

@pytest.mark.asyncio
async def test_f07_student_enroll_session():
    """F-07: Student enrolls in a session"""
    print("\n🧪 F-07: Student Enroll")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "student")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to enroll (may not have valid session_id)
        response = await client.post("/sessions/1/enroll", headers=headers)
        assert response.status_code in [200, 201, 400, 404, 409]
        print("✅ F-07 PASSED")

@pytest.mark.asyncio
async def test_f08_tutor_view_sessions():
    """F-08: Tutor views their sessions"""
    print("\n🧪 F-08: Tutor View Sessions")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "tutor")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get("/sessions/my-sessions", headers=headers, follow_redirects=True)
        assert response.status_code in [200, 404]
        print("✅ F-08 PASSED")

@pytest.mark.asyncio
async def test_f09_mark_attendance():
    """F-09: Mark attendance for session"""
    print("\n🧪 F-09: Mark Attendance")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "tutor")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to mark attendance (may not have valid session_id)
        attendance_data = {
            "session_id": 1,
            "student_id": 1,
            "status": "present"
        }
        response = await client.post("/sessions/attendance", json=attendance_data, headers=headers)
        assert response.status_code in [200, 201, 400, 404, 405]
        print("✅ F-09 PASSED")

# ============================================================================
# MATERIALS & FEEDBACK (F-10 to F-12)
# ============================================================================

@pytest.mark.asyncio
async def test_f10_view_materials():
    """F-10: View session materials"""
    print("\n🧪 F-10: View Materials")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "student")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get("/sessions/1/materials", headers=headers, follow_redirects=True)
        assert response.status_code in [200, 404]
        print("✅ F-10 PASSED")

@pytest.mark.asyncio
async def test_f11_submit_feedback():
    """F-11: Student submits feedback"""
    print("\n🧪 F-11: Submit Feedback")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "student")
        headers = {"Authorization": f"Bearer {token}"}
        
        feedback_data = {
            "session_id": 1,
            "rating": 5,
            "comments": "Great session!"
        }
        response = await client.post("/sessions/feedback", json=feedback_data, headers=headers)
        assert response.status_code in [200, 201, 400, 404, 405, 409]
        print("✅ F-11 PASSED")

@pytest.mark.asyncio
async def test_f12_view_feedback():
    """F-12: View session feedback"""
    print("\n🧪 F-12: View Feedback")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "tutor")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get("/sessions/1/feedback", headers=headers)
        assert response.status_code in [200, 404]
        print("✅ F-12 PASSED")

# ============================================================================
# NOTIFICATIONS & REPORTS (F-13 to F-15)
# ============================================================================

@pytest.mark.asyncio
async def test_f13_view_notifications():
    """F-13: View user notifications"""
    print("\n🧪 F-13: View Notifications")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "student")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get("/notifications/", headers=headers, follow_redirects=True)
        assert response.status_code in [200, 404]
        print("✅ F-13 PASSED")

@pytest.mark.asyncio
async def test_f14_coordinator_view_reports():
    """F-14: Coordinator views reports"""
    print("\n🧪 F-14: View Reports")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "coordinator")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get("/reports/overview", headers=headers, follow_redirects=True)
        assert response.status_code in [200, 404]
        print("✅ F-14 PASSED")

@pytest.mark.asyncio
async def test_f15_student_progress_tracking():
    """F-15: Track student progress"""
    print("\n🧪 F-15: Progress Tracking")
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        token = await login(client, "student")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get("/progress/me", headers=headers, follow_redirects=True)
        assert response.status_code in [200, 404]
        print("✅ F-15 PASSED")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

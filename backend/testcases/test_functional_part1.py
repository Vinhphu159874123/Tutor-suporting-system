"""
Functional Test Cases - Part 1 (F-01 to F-10)
Testing Account Management, Registration, and Scheduling modules
"""
import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, date, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

# Test configuration
BASE_URL = "https://tutor-suporting-system-production.up.railway.app/api/v1"
FRONTEND_URL = "https://tutor-suporting-system.vercel.app"

# Test credentials
TEST_STUDENT = {
    "email": "student113@hcmut.edu.vn",
    "password": "TestPass123!"
}
TEST_TUTOR = {
    "email": "tutor113@hcmut.edu.vn", 
    "password": "TestPass123!"
}
TEST_COORDINATOR = {
    "email": "coordinator113@hcmut.edu.vn",
    "password": "TestPass123!"
}

class TestFunctionalPart1:
    """Functional test cases F-01 to F-10"""
    
    @pytest.mark.asyncio
    async def test_f01_login_with_sso(self):
        """
        F-01: Account Management (Login)
        Test user login with HCMUT_SSO authentication
        """
        print("\n🧪 Testing F-01: Login with HCMUT_SSO")
        
        async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            # Test student login
            response = await client.post("/auth/login", data={"username": TEST_STUDENT["email"], "password": TEST_STUDENT["password"]}, headers={"Content-Type": "application/x-www-form-urlencoded"})
            assert response.status_code == 200, f"Login failed: {response.text}"
            
            data = response.json()
            token = data.get("access_token") or data.get("token")
            assert token is not None, "No token returned"
            
            # Verify user can access protected route
            headers = {"Authorization": f"Bearer {token}"}
            me_response = await client.get("/auth/me", headers=headers)
            assert me_response.status_code == 200, f"Auth verification failed: {me_response.text}"
            
            user_data = me_response.json()
            # API returns 'email' and 'role' fields, not 'user_id'
            assert "email" in user_data or "user_id" in user_data
            assert "role" in user_data or "available_roles" in user_data
            
            print(f"✅ F-01 PASSED: User logged in with email {user_data.get('email')}")

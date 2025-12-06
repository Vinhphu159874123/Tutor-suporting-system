"""
Functional Test Cases - Part 3 (F-21 to F-25)
Testing Session Management, Reports, Admin, and Forum modules
"""
import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, date, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "https://tutor-suporting-system-production.up.railway.app/api/v1"

TEST_STUDENT = {"email": "student.test@hcmut.edu.vn", "password": "test123456"}
TEST_TUTOR = {"email": "tutor.test@hcmut.edu.vn", "password": "test123456"}
TEST_COORDINATOR = {"email": "coordinator.test@hcmut.edu.vn", "password": "test123456"}
TEST_ADMIN = {"email": "admin.test@hcmut.edu.vn", "password": "test123456"}


class TestFunctionalPart3:
    """Functional test cases F-21 to F-25"""
    
@pytest.fixture
    async def student_token(self, client):
        response = await client.post("/auth/login", data={"username": TEST_STUDENT["email"], "password": TEST_STUDENT["password"]}, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")
    

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

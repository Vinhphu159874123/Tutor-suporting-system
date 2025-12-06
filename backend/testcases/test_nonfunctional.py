"""
Non-Functional Test Cases (NF-01 to NF-10)
Testing Performance, Security, Scalability, Load, and Database Integrity
"""
import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, date, timedelta
import time
import statistics
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "https://tutor-suporting-system-production.up.railway.app/api/v1"

TEST_STUDENT = {"email": "student.test@hcmut.edu.vn", "password": "test123456"}
TEST_TUTOR = {"email": "tutor.test@hcmut.edu.vn", "password": "test123456"}
TEST_COORDINATOR = {"email": "coordinator.test@hcmut.edu.vn", "password": "test123456"}


class TestNonFunctional:
    """Non-functional test cases NF-01 to NF-10"""
    
@pytest.fixture
    async def student_token(self, client):
        response = await client.post("/auth/login", data={"username": TEST_STUDENT["email"], "password": TEST_STUDENT["password"]}, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")
    

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])

import httpx
import asyncio
from typing import Optional, Dict, Any
from app.core.config import settings

class HCMUTSSOService:
    """Service for HCMUT SSO integration"""
    
    def __init__(self):
        self.sso_url = settings.HCMUT_SSO_URL
        
    async def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with HCMUT SSO"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.sso_url}/auth/login",
                    json={"username": username, "password": password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "id": data.get("id"),
                        "email": data.get("email"),
                        "full_name": data.get("full_name"),
                        "faculty": data.get("faculty"),
                        "major": data.get("major"),
                        "student_id": data.get("student_id"),
                        "staff_id": data.get("staff_id"),
                        "role": data.get("role", "student")
                    }
                return None
        except Exception as e:
            print(f"SSO authentication error: {e}")
            return None
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate SSO token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.sso_url}/auth/validate",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"SSO token validation error: {e}")
            return None
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from SSO"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.sso_url}/users/{user_id}")
                
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"SSO user info error: {e}")
            return None
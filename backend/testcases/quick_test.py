"""Quick test to verify API connectivity and credentials"""
import asyncio
import httpx
import sys

BASE_URL = "https://tutor-suporting-system-production.up.railway.app/api/v1"

# Test with actual credentials from your system
TEST_CREDENTIALS = [
    {"email": "student113@hcmut.edu.vn", "password": "TestPass123!"},
    {"email": "tutor113@hcmut.edu.vn", "password": "TestPass123!"},
    {"email": "coordinator113@hcmut.edu.vn", "password": "TestPass123!"},
    {"email": "admin113@hcmut.edu.vn", "password": "TestPass123!"},
]

async def test_connection():
    print("Testing API connection...")
    print(f"Base URL: {BASE_URL}")
    print()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Health check or base endpoint
        try:
            response = await client.get(f"{BASE_URL.replace('/api/v1', '')}/")
            print(f"✅ Server reachable: {response.status_code}")
        except Exception as e:
            print(f"❌ Server unreachable: {e}")
            return False
        
        # Test 2: Try login with different credentials
        print("\nTesting login credentials...")
        for i, creds in enumerate(TEST_CREDENTIALS, 1):
            try:
                # Use form data format (OAuth2PasswordRequestForm)
                form_data = {
                    "username": creds["email"],
                    "password": creds["password"]
                }
                response = await client.post(
                    f"{BASE_URL}/auth/login", 
                    data=form_data,  # Use data= for form, not json=
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("access_token") or data.get("token")
                    print(f"✅ Credentials {i} work: {creds['email']}")
                    print(f"   Token: {token[:50]}...")
                    
                    # Test /auth/me
                    headers = {"Authorization": f"Bearer {token}"}
                    me_response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
                    if me_response.status_code == 200:
                        user = me_response.json()
                        print(f"   User: {user.get('email')} | Role: {user.get('role')}")
                        return True
                else:
                    print(f"❌ Credentials {i} failed: {creds['email']} - {response.status_code}")
            except Exception as e:
                print(f"❌ Error testing credentials {i}: {e}")
        
        print("\n⚠️  No valid credentials found. Please update TEST_CREDENTIALS in quick_test.py")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)

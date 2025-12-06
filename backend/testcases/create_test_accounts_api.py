"""
Create test accounts via API
Creates 4 accounts: student113, tutor113, coordinator113, admin113
"""
import asyncio
import httpx

BASE_URL = "https://tutor-suporting-system-production.up.railway.app/api/v1"

TEST_ACCOUNTS = [
    {
        "email": "student113@hcmut.edu.vn",
        "password": "TestPass123!",
        "full_name": "Test Student 113",
        "student_id": "2211113",
        "role": ["student"]
    },
    {
        "email": "tutor113@hcmut.edu.vn",
        "password": "TestPass123!",
        "full_name": "Test Tutor 113",
        "student_id": "2011113",
        "role": ["tutor"]
    },
    {
        "email": "coordinator113@hcmut.edu.vn",
        "password": "TestPass123!",
        "full_name": "Test Coordinator 113",
        "student_id": "1911113",
        "role": ["coordinator"]
    },
    {
        "email": "admin113@hcmut.edu.vn",
        "password": "TestPass123!",
        "full_name": "Test Admin 113",
        "student_id": "1811113",
        "role": ["admin"]
    }
]

async def create_accounts():
    print("\n" + "="*80)
    print("CREATING TEST ACCOUNTS VIA API")
    print("="*80 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for account in TEST_ACCOUNTS:
            print(f"Creating {account['email']}...")
            
            try:
                # Try to register
                response = await client.post(
                    f"{BASE_URL}/auth/register",
                    json={
                        "email": account["email"],
                        "password": account["password"],
                        "full_name": account["full_name"],
                        "student_id": account["student_id"],
                        "role": account["role"]
                    }
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    print(f"  ✅ Created: {account['email']}")
                elif response.status_code == 400:
                    # Already exists, try to login
                    print(f"  ℹ️  Account exists, testing login...")
                    login_response = await client.post(
                        f"{BASE_URL}/auth/login",
                        data={
                            "username": account["email"],
                            "password": account["password"]
                        },
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                    
                    if login_response.status_code == 200:
                        print(f"  ✅ Login successful: {account['email']}")
                    else:
                        print(f"  ⚠️  Login failed: {login_response.status_code}")
                        print(f"     Response: {login_response.text}")
                else:
                    print(f"  ❌ Error: {response.status_code}")
                    print(f"     Response: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Exception: {e}")
            
            print()
    
    print("\n" + "="*80)
    print("ACCOUNT CREATION COMPLETE")
    print("="*80)
    print("\nTest Credentials:")
    print("-" * 80)
    for account in TEST_ACCOUNTS:
        print(f"Email: {account['email']}")
        print(f"Password: {account['password']}")
        print(f"Role: {', '.join(account['role'])}")
        print()

if __name__ == "__main__":
    asyncio.run(create_accounts())

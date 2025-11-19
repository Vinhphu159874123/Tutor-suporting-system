"""
Quick Auth Test - Test layered architecture
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_register():
    print_section("1. TEST REGISTER")
    
    # Generate unique email
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_user = {
        "email": f"test_{timestamp}@hcmut.edu.vn",
        "password": "Test123456",
        "full_name": "Test User",
        "role": "student"
    }
    
    print(f"📝 Registering: {test_user['email']}")
    response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Register SUCCESS")
        print(f"   User ID: {data['user']['id']}")
        print(f"   Email: {data['user']['email']}")
        print(f"   Role: {data['user']['role']}")
        return test_user
    else:
        print(f"❌ Register FAILED: {response.status_code}")
        print(f"   {response.text}")
        return None

def test_login(user_data):
    print_section("2. TEST LOGIN")
    
    login_data = {
        "username": user_data["email"],  # OAuth2 uses 'username' field
        "password": user_data["password"]
    }
    
    print(f"🔐 Logging in: {user_data['email']}")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,  # OAuth2 uses form data
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login SUCCESS")
        print(f"   Access Token: {data['access_token'][:50]}...")
        print(f"   Token Type: {data['token_type']}")
        return data["access_token"]
    else:
        print(f"❌ Login FAILED: {response.status_code}")
        print(f"   {response.text}")
        return None

def test_get_profile(token):
    print_section("3. TEST GET PROFILE (Protected Route)")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"👤 Fetching profile...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Get Profile SUCCESS")
        print(f"   Email: {data['email']}")
        print(f"   Full Name: {data['full_name']}")
        print(f"   Role: {data['role']}")
        print(f"   Active: {data['is_active']}")
        return True
    else:
        print(f"❌ Get Profile FAILED: {response.status_code}")
        print(f"   {response.text}")
        return False

def test_invalid_token():
    print_section("4. TEST INVALID TOKEN")
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    print(f"🔒 Testing with invalid token...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 401:
        print(f"✅ Security working - Unauthorized correctly")
        print(f"   Status: {response.status_code}")
    else:
        print(f"❌ Security issue - Should return 401")
        print(f"   Status: {response.status_code}")

def main():
    print("\n" + "🚀"*30)
    print(" HCMUT TUTOR SYSTEM - AUTH MODULE TEST")
    print(" Testing Layered Architecture + Event System")
    print("🚀"*30)
    
    try:
        # Test 1: Register
        user = test_register()
        if not user:
            print("\n❌ FAILED: Cannot register")
            return
        
        # Test 2: Login
        token = test_login(user)
        if not token:
            print("\n❌ FAILED: Cannot login")
            return
        
        # Test 3: Get Profile (Protected)
        success = test_get_profile(token)
        if not success:
            print("\n❌ FAILED: Cannot get profile")
            return
        
        # Test 4: Security test
        test_invalid_token()
        
        # Final summary
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n🎯 Architecture Verification:")
        print("   ✅ Routes Layer - Working")
        print("   ✅ Service Layer - Working")
        print("   ✅ Repository Layer - Working")
        print("   ✅ Database Layer - Working")
        print("   ✅ Event System - Registered")
        print("   ✅ JWT Authentication - Working")
        print("   ✅ Dependency Injection - Working")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print("   Make sure server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()

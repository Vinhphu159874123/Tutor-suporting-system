"""
Sequential API Testing Script
Tests all endpoints one by one with detailed output
"""
import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def print_header(test_num, title):
    """Print test header"""
    print("\n" + "="*80)
    print(f"📍 Test {test_num}: {title}")
    print("="*80)

def test_get(endpoint, description):
    """Test GET endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        req = urllib.request.Request(url, method='GET')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"✅ {description}")
            print(f"Status: {response.status}")
            print(f"Response ({type(data).__name__}):")
            
            if isinstance(data, dict):
                print(json.dumps(data, indent=2, ensure_ascii=False))
            elif isinstance(data, list):
                print(f"  📊 Total items: {len(data)}")
                if len(data) > 0:
                    print(f"  📝 First item:")
                    print("  " + json.dumps(data[0], indent=4, ensure_ascii=False).replace("\n", "\n  "))
                if len(data) > 1:
                    print(f"  ... and {len(data)-1} more items")
            else:
                print(data)
            
            return data
    except urllib.error.HTTPError as e:
        print(f"❌ {description}")
        print(f"Status: {e.code}")
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(e.read().decode('utf-8'))
        return None
    except Exception as e:
        print(f"❌ {description} - Error: {str(e)}")
        return None

def test_post(endpoint, data, description):
    """Test POST endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            print(f"✅ {description}")
            print(f"Status: {response.status}")
            print(f"Response:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            return response_data
    except urllib.error.HTTPError as e:
        print(f"❌ {description}")
        print(f"Status: {e.code}")
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(e.read().decode('utf-8'))
        return None
    except Exception as e:
        print(f"❌ {description} - Error: {str(e)}")
        return None

def main():
    print("🚀 HCMUT Tutor Support System - Sequential API Testing")
    print("⏰ Started at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Test 1: Health Check
    print_header(1, "Health Check")
    test_get("/health", "GET /health")
    
    # Test 2: Root Endpoint
    print_header(2, "Root Endpoint")
    test_get("/", "GET /")
    
    # Test 3: Get All Users
    print_header(3, "Get All Users")
    users = test_get("/api/v1/users", "GET /api/v1/users")
    
    # Test 4: Get User by ID (if users exist)
    if users and len(users) > 0:
        print_header(4, "Get User by ID")
        user_id = users[0].get('id')
        test_get(f"/api/v1/users/{user_id}", f"GET /api/v1/users/{user_id}")
    
    # Test 5: Get All Subjects
    print_header(5, "Get All Subjects")
    subjects = test_get("/api/v1/subjects", "GET /api/v1/subjects")
    
    # Test 6: Get All Tutors
    print_header(6, "Get All Tutors")
    tutors = test_get("/api/v1/tutors", "GET /api/v1/tutors")
    
    # Test 7: Get All Students
    print_header(7, "Get All Students")
    students = test_get("/api/v1/students", "GET /api/v1/students")
    
    # Test 8: Get All Sessions
    print_header(8, "Get All Sessions")
    sessions = test_get("/api/v1/sessions", "GET /api/v1/sessions")
    
    # Test 9: Get All Forums
    print_header(9, "Get All Forums")
    forums = test_get("/api/v1/forum/forums", "GET /api/v1/forum/forums")
    
    # Test 10: Login Test
    print_header(10, "Login Test (Admin)")
    login_data = {
        "username": "admin@hcmut.edu.vn",
        "password": "admin123"
    }
    test_post("/api/v1/auth/login", login_data, "POST /api/v1/auth/login")
    
    # Summary
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED!")
    print("⏰ Finished at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)
    print("\n📊 Summary:")
    print(f"  - Users: {len(users) if users else 0}")
    print(f"  - Subjects: {len(subjects) if subjects else 0}")
    print(f"  - Tutors: {len(tutors) if tutors else 0}")
    print(f"  - Students: {len(students) if students else 0}")
    print(f"  - Sessions: {len(sessions) if sessions else 0}")
    print(f"  - Forums: {len(forums) if forums else 0}")

if __name__ == "__main__":
    main()

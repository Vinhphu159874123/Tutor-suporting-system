"""
Test Suite for Scheduling Endpoints
Test all availability and session scheduling functionality
"""
import requests
import json
from datetime import datetime, date, time, timedelta

# API Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test accounts
TUTOR_CREDENTIALS = {
    "username": "nhanteacher",
    "password": "Password123!"
}

STUDENT_CREDENTIALS = {
    "username": "gfmg",
    "password": "Password123!"
}

# Global tokens
tutor_token = None
student_token = None
tutor_id = None
student_id = None

def print_test_header(test_name):
    """Print test header"""
    print("\n" + "="*80)
    print(f"🧪 TEST: {test_name}")
    print("="*80)

def print_result(success, message, response=None):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    if response:
        print(f"📊 Status: {response.status_code}")
        try:
            print(f"📦 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"📦 Response: {response.text}")
    print()

def login(credentials, role):
    """Login and get token"""
    print_test_header(f"Login as {role}")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": credentials["username"],
            "password": credentials["password"]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user_id = data.get("user", {}).get("user_id")
        print_result(True, f"Login successful as {role}", response)
        return token, user_id
    else:
        print_result(False, f"Login failed as {role}", response)
        return None, None

def test_01_login():
    """Test 1: Login as tutor and student"""
    global tutor_token, student_token, tutor_id, student_id
    
    tutor_token, tutor_id = login(TUTOR_CREDENTIALS, "TUTOR")
    student_token, student_id = login(STUDENT_CREDENTIALS, "STUDENT")
    
    assert tutor_token is not None, "Tutor login failed"
    assert student_token is not None, "Student login failed"

def test_02_create_recurring_availability():
    """Test 2: Create recurring availability (Monday 9-11 AM)"""
    print_test_header("Create Recurring Availability")
    
    # Get tutor_id from profile
    response = requests.get(
        f"{BASE_URL}/users/profile",
        headers={"Authorization": f"Bearer {tutor_token}"}
    )
    
    if response.status_code != 200:
        print_result(False, "Failed to get tutor profile", response)
        return
    
    profile = response.json()
    tutor_id_from_profile = profile.get("tutor", {}).get("tutor_id")
    
    if not tutor_id_from_profile:
        print_result(False, "Tutor ID not found in profile", response)
        return
    
    # Create recurring availability
    tomorrow = date.today() + timedelta(days=1)
    day_of_week = tomorrow.weekday()  # 0=Monday, 6=Sunday
    
    payload = {
        "is_recurring": True,
        "day_of_week": day_of_week,
        "specific_date": None,
        "start_time": "09:00:00",
        "end_time": "11:00:00",
        "is_available": True,
        "notes": "Morning teaching slot"
    }
    
    response = requests.post(
        f"{BASE_URL}/scheduling/availability/{tutor_id_from_profile}",
        headers={"Authorization": f"Bearer {tutor_token}"},
        json=payload
    )
    
    if response.status_code == 200:
        print_result(True, "Recurring availability created successfully", response)
    else:
        print_result(False, "Failed to create recurring availability", response)

def test_03_create_onetime_availability():
    """Test 3: Create one-time availability (specific date 14-16)"""
    print_test_header("Create One-Time Availability")
    
    # Get tutor_id
    response = requests.get(
        f"{BASE_URL}/users/profile",
        headers={"Authorization": f"Bearer {tutor_token}"}
    )
    tutor_id_from_profile = response.json().get("tutor", {}).get("tutor_id")
    
    # Create one-time availability for tomorrow
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    payload = {
        "is_recurring": False,
        "day_of_week": None,
        "specific_date": tomorrow,
        "start_time": "14:00:00",
        "end_time": "16:00:00",
        "is_available": True,
        "notes": "Extra afternoon slot"
    }
    
    response = requests.post(
        f"{BASE_URL}/scheduling/availability/{tutor_id_from_profile}",
        headers={"Authorization": f"Bearer {tutor_token}"},
        json=payload
    )
    
    if response.status_code == 200:
        print_result(True, "One-time availability created successfully", response)
    else:
        print_result(False, "Failed to create one-time availability", response)

def test_04_get_tutor_availability():
    """Test 4: Get tutor availability schedule"""
    print_test_header("Get Tutor Availability")
    
    # Get tutor_id
    response = requests.get(
        f"{BASE_URL}/users/profile",
        headers={"Authorization": f"Bearer {tutor_token}"}
    )
    tutor_id_from_profile = response.json().get("tutor", {}).get("tutor_id")
    
    response = requests.get(
        f"{BASE_URL}/scheduling/availability/{tutor_id_from_profile}",
        headers={"Authorization": f"Bearer {tutor_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Retrieved availability: {len(data.get('recurring', {}))} recurring days, {len(data.get('one_time', []))} one-time slots", response)
    else:
        print_result(False, "Failed to get availability", response)

def test_05_find_available_slots():
    """Test 5: Find available time slots"""
    print_test_header("Find Available Time Slots")
    
    # Get tutor_id
    response = requests.get(
        f"{BASE_URL}/users/profile",
        headers={"Authorization": f"Bearer {tutor_token}"}
    )
    tutor_id_from_profile = response.json().get("tutor", {}).get("tutor_id")
    
    # Find slots for tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
    
    payload = {
        "tutor_id": tutor_id_from_profile,
        "date": tomorrow,
        "duration_minutes": 60
    }
    
    response = requests.post(
        f"{BASE_URL}/scheduling/find-slots",
        headers={"Authorization": f"Bearer {student_token}"},
        json=payload
    )
    
    if response.status_code == 200:
        slots = response.json()
        print_result(True, f"Found {len(slots)} available slots", response)
    else:
        print_result(False, "Failed to find available slots", response)

def test_06_schedule_session():
    """Test 6: Schedule a new session"""
    print_test_header("Schedule New Session")
    
    # Get tutor_id and subject_id
    response = requests.get(
        f"{BASE_URL}/users/profile",
        headers={"Authorization": f"Bearer {tutor_token}"}
    )
    tutor_id_from_profile = response.json().get("tutor", {}).get("tutor_id")
    
    # Get a valid subject (assuming subject_id 37-46 exist)
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    payload = {
        "tutor_id": tutor_id_from_profile,
        "scheduled_date": tomorrow,
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "subject_id": 37,  # Use valid subject ID
        "notes": "Test session"
    }
    
    response = requests.post(
        f"{BASE_URL}/scheduling/sessions",
        headers={"Authorization": f"Bearer {student_token}"},
        json=payload
    )
    
    if response.status_code == 200:
        session_data = response.json()
        global scheduled_session_id
        scheduled_session_id = session_data.get("session_id")
        print_result(True, f"Session scheduled successfully (ID: {scheduled_session_id})", response)
        return scheduled_session_id
    else:
        print_result(False, "Failed to schedule session", response)
        return None

def test_07_reschedule_session():
    """Test 7: Reschedule existing session"""
    print_test_header("Reschedule Session")
    
    # First schedule a session
    session_id = test_06_schedule_session()
    if not session_id:
        print_result(False, "Cannot test reschedule without scheduled session")
        return
    
    # Reschedule to different time
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    payload = {
        "scheduled_date": tomorrow,
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "reason": "Time conflict"
    }
    
    response = requests.put(
        f"{BASE_URL}/scheduling/sessions/{session_id}/reschedule",
        headers={"Authorization": f"Bearer {tutor_token}"},
        json=payload
    )
    
    if response.status_code == 200:
        print_result(True, "Session rescheduled successfully", response)
    else:
        print_result(False, "Failed to reschedule session", response)

def test_08_cancel_session():
    """Test 8: Cancel scheduled session"""
    print_test_header("Cancel Session")
    
    # Schedule a session first
    session_id = test_06_schedule_session()
    if not session_id:
        print_result(False, "Cannot test cancel without scheduled session")
        return
    
    response = requests.delete(
        f"{BASE_URL}/scheduling/sessions/{session_id}?reason=Student request",
        headers={"Authorization": f"Bearer {tutor_token}"}
    )
    
    if response.status_code == 200:
        print_result(True, "Session cancelled successfully", response)
    else:
        print_result(False, "Failed to cancel session", response)

def test_09_validation_errors():
    """Test 9: Test validation errors"""
    print_test_header("Validation Error Tests")
    
    # Get tutor_id
    response = requests.get(
        f"{BASE_URL}/users/profile",
        headers={"Authorization": f"Bearer {tutor_token}"}
    )
    tutor_id_from_profile = response.json().get("tutor", {}).get("tutor_id")
    
    # Test 1: Recurring without day_of_week
    print("📝 Test: Recurring without day_of_week")
    payload = {
        "is_recurring": True,
        "day_of_week": None,  # Missing!
        "specific_date": None,
        "start_time": "09:00:00",
        "end_time": "11:00:00"
    }
    
    response = requests.post(
        f"{BASE_URL}/scheduling/availability/{tutor_id_from_profile}",
        headers={"Authorization": f"Bearer {tutor_token}"},
        json=payload
    )
    
    if response.status_code == 422 or response.status_code == 400:
        print_result(True, "Correctly rejected recurring without day_of_week", response)
    else:
        print_result(False, "Should reject recurring without day_of_week", response)
    
    # Test 2: One-time without specific_date
    print("📝 Test: One-time without specific_date")
    payload = {
        "is_recurring": False,
        "day_of_week": None,
        "specific_date": None,  # Missing!
        "start_time": "09:00:00",
        "end_time": "11:00:00"
    }
    
    response = requests.post(
        f"{BASE_URL}/scheduling/availability/{tutor_id_from_profile}",
        headers={"Authorization": f"Bearer {tutor_token}"},
        json=payload
    )
    
    if response.status_code == 422 or response.status_code == 400:
        print_result(True, "Correctly rejected one-time without specific_date", response)
    else:
        print_result(False, "Should reject one-time without specific_date", response)

def run_all_tests():
    """Run all tests in sequence"""
    print("\n🚀 Starting Scheduling API Test Suite")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API URL: {BASE_URL}")
    
    tests = [
        ("Login", test_01_login),
        ("Create Recurring Availability", test_02_create_recurring_availability),
        ("Create One-Time Availability", test_03_create_onetime_availability),
        ("Get Tutor Availability", test_04_get_tutor_availability),
        ("Find Available Slots", test_05_find_available_slots),
        ("Schedule Session", test_06_schedule_session),
        ("Reschedule Session", test_07_reschedule_session),
        ("Cancel Session", test_08_cancel_session),
        ("Validation Errors", test_09_validation_errors),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print_result(False, f"Test '{test_name}' failed with exception: {str(e)}")
            failed += 1
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print(f"📈 Success Rate: {(passed/len(tests)*100):.1f}%")
    print("="*80)

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {str(e)}")

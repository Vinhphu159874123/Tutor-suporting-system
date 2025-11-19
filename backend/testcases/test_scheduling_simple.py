"""
Test Scheduling API - Simple Version
Just paste your tokens and run!

HOW TO GET TOKENS:
1. Login via Postman: POST http://localhost:8000/api/v1/auth/login
   - Tutor: username=nhanteacher, password=Password123!
   - Student: username=gfmg, password=Password123!
2. Copy access_token from response
3. Paste below
"""
import requests
import json
from datetime import datetime, date, timedelta

# ============================================================================
# PASTE YOUR TOKENS HERE (Get from Postman login)
# ============================================================================

BASE_URL = "http://localhost:8000/api/v1"

TUTOR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuaGFudGVhY2hlckBoY211dC5lZHUudm4iLCJleHAiOjE3NjM1NDYyMDR9.18XbO3vC73OOWxI79NvuWN6sg5HpIpJayGKIjorLqsQ"
STUDENT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnZm1nQGhjbXV0LmVkdS52biIsImV4cCI6MTc2MzU0NjI1MH0.Ap1AcBTHVUmjX6X6Pyy8QrTErTZteEhRE9LttMI3kVU"  
TUTOR_ID = 27  # Change if needed

# ============================================================================

def test_create_availability():
    """Test: Create availability"""
    print("\n🧪 Test 1: Create Availability (Tomorrow 9-11 AM)")
    print("="*70)
    
    tomorrow = date.today() + timedelta(days=1)
    
    payload = {
        "is_recurring": False,
        "day_of_week": None,
        "specific_date": tomorrow.isoformat(),
        "start_time": "09:00:00",
        "end_time": "11:00:00",
        "is_available": True,
        "notes": "Test slot"
    }
    
    response = requests.post(
        f"{BASE_URL}/scheduling/availability/{TUTOR_ID}",
        headers={"Authorization": f"Bearer {TUTOR_TOKEN}"},
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, default=str)[:300]}")
    return response.status_code == 200

def test_get_availability():
    """Test: Get availability"""
    print("\n🧪 Test 2: Get Tutor Availability")
    print("="*70)
    
    response = requests.get(
        f"{BASE_URL}/scheduling/availability/{TUTOR_ID}",
        headers={"Authorization": f"Bearer {TUTOR_TOKEN}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Recurring slots: {len(data.get('recurring', {}))}")
        print(f"One-time slots: {len(data.get('one_time', []))}")
    else:
        print(f"Response: {response.text[:300]}")
    return response.status_code == 200

def test_find_slots():
    """Test: Find available slots"""
    print("\n🧪 Test 3: Find Available Slots")
    print("="*70)
    
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    payload = {
        "tutor_id": TUTOR_ID,
        "date": tomorrow,
        "duration_minutes": 60
    }
    
    response = requests.post(
        f"{BASE_URL}/scheduling/find-slots",
        headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        slots = response.json()
        print(f"Found {len(slots)} slots")
        for slot in slots[:3]:  # Show first 3
            print(f"  - {slot['start_time']} to {slot['end_time']}")
    else:
        print(f"Response: {response.text[:300]}")
    return response.status_code == 200

def test_schedule_session():
    """Test: Schedule session"""
    print("\n🧪 Test 4: Schedule Session")
    print("="*70)
    
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    payload = {
        "tutor_id": TUTOR_ID,
        "scheduled_date": tomorrow,
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "subject_id": 37,
        "notes": "Test session"
    }
    
    response = requests.post(
        f"{BASE_URL}/scheduling/sessions",
        headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        session_id = data.get("session_id")
        print(f"✅ Created session ID: {session_id}")
        return session_id
    else:
        print(f"Response: {response.text[:300]}")
        return None

def test_reschedule(session_id):
    """Test: Reschedule session"""
    if not session_id:
        print("\n⏭️ Test 5: Reschedule (Skipped - no session)")
        return False
    
    print("\n🧪 Test 5: Reschedule Session")
    print("="*70)
    
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    payload = {
        "scheduled_date": tomorrow,
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "reason": "Time change"
    }
    
    response = requests.put(
        f"{BASE_URL}/scheduling/sessions/{session_id}/reschedule",
        headers={"Authorization": f"Bearer {TUTOR_TOKEN}"},
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    return response.status_code == 200

def test_cancel(session_id):
    """Test: Cancel session"""
    if not session_id:
        print("\n⏭️ Test 6: Cancel (Skipped - no session)")
        return False
    
    print("\n🧪 Test 6: Cancel Session")
    print("="*70)
    
    response = requests.delete(
        f"{BASE_URL}/scheduling/sessions/{session_id}?reason=Test cleanup",
        headers={"Authorization": f"Bearer {TUTOR_TOKEN}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 SCHEDULING API TESTS")
    print("="*70)
    print(f"API: {BASE_URL}")
    print(f"Tutor ID: {TUTOR_ID}")
    
    # Check tokens
    if "YOUR_" in TUTOR_TOKEN or "YOUR_" in STUDENT_TOKEN:
        print("\n❌ ERROR: Please paste your tokens first!")
        print("\n📝 How to get tokens:")
        print("1. Use Postman or curl:")
        print("   POST http://localhost:8000/api/v1/auth/login")
        print("   Body (form-data): username=nhanteacher&password=Password123!")
        print("\n2. Copy 'access_token' from response")
        print("3. Paste as TUTOR_TOKEN in this file")
        print("4. Repeat for student (username=gfmg)")
        return
    
    results = []
    
    # Run tests
    print("\n⏱️ Starting tests...")
    results.append(("Create Availability", test_create_availability()))
    results.append(("Get Availability", test_get_availability()))
    results.append(("Find Slots", test_find_slots()))
    
    session_id = test_schedule_session()
    results.append(("Schedule Session", session_id is not None))
    results.append(("Reschedule Session", test_reschedule(session_id)))
    results.append(("Cancel Session", test_cancel(session_id)))
    
    # Summary
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    for name, passed in results:
        icon = "✅" if passed else "❌"
        print(f"{icon} {name}")
    
    passed = sum(1 for _, p in results if p)
    print(f"\n🎯 Score: {passed}/{len(results)}")
    print("="*70)

if __name__ == "__main__":
    main()

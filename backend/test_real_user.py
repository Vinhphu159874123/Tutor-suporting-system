import requests
import json

API = "http://localhost:8000/api/v1"

# Try to login with your actual user
print("🔐 Testing login...")
r = requests.post(f"{API}/auth/login", data={
    "username": "nhan",  # Auto-appends @hcmut.edu.vn
    "password": "123"
})
print(f"Login Status: {r.status_code}")
print(f"Response: {r.text[:200]}")

if r.status_code == 200:
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*60)
    print("✅ Login successful! Testing endpoints...")
    print("="*60)
    
    # Test 1: Dashboard Stats
    print("\n📊 Dashboard Stats:")
    r1 = requests.get(f"{API}/users/stats/dashboard?mode=student", headers=headers)
    print(f"  Status: {r1.status_code}")
    if r1.status_code == 200:
        print(f"  Data: {json.dumps(r1.json(), indent=2)}")
    else:
        print(f"  Error: {r1.text[:200]}")
    
    # Test 2: My Sessions
    print("\n📅 My Sessions Dashboard:")
    r2 = requests.get(f"{API}/sessions/my-sessions/dashboard?mode=student", headers=headers)
    print(f"  Status: {r2.status_code}")
    if r2.status_code == 200:
        data = r2.json()
        print(f"  Recent: {len(data.get('recent', []))} sessions")
        print(f"  Upcoming: {len(data.get('upcoming', []))} sessions")
        print(f"  Data: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"  Error: {r2.text[:500]}")
    
    # Test 3: Available Courses
    print("\n📚 Available Courses:")
    r3 = requests.get(f"{API}/tutors/available-courses", headers=headers)
    print(f"  Status: {r3.status_code}")
    if r3.status_code == 200:
        courses = r3.json().get("data", [])
        print(f"  Total courses: {len(courses)}")
        if courses:
            print(f"  First course: {courses[0].get('subject_name', 'N/A')}")
    else:
        print(f"  Error: {r3.text[:200]}")
        
    # Check Redis
    print("\n" + "="*60)
    print("🔑 Redis Cache Status:")
    print("="*60)
    import redis as rd
    try:
        r = rd.Redis(decode_responses=True)
        keys = r.keys("*")
        print(f"Total keys: {len(keys)}")
        for k in sorted(keys):
            print(f"  • {k} (TTL: {r.ttl(k)}s)")
    except:
        print("  ⚠️ Redis not connected")
else:
    print("\n❌ Login failed. Try these credentials:")
    print("  - nhan / 123")
    print("  - student / password123") 
    print("  - admin / admin123")

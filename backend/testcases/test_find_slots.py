"""Quick test for find_slots endpoint"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api/v1"
STUDENT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnZm1nQGhjbXV0LmVkdS52biIsImV4cCI6MTc2MzU0MTc3NX0.hyfkMs-9jXY3fjaJCTi2Ycduo1RUC6juKe64jxHLGXs"

tomorrow = (date.today() + timedelta(days=1)).isoformat()

payload = {
    "tutor_id": 27,
    "date": tomorrow,
    "duration_minutes": 60
}

print(f"Testing find-slots with: {payload}")

try:
    response = requests.post(
        f"{BASE_URL}/scheduling/find-slots",
        headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
        json=payload
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Found {len(data)} slots")
        for slot in data[:3]:
            print(f"  {slot}")
    else:
        print(f"\n❌ Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

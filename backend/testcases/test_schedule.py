"""Quick test for schedule session endpoint"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api/v1"
STUDENT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnZm1nQGhjbXV0LmVkdS52biIsImV4cCI6MTc2MzU0MTc3NX0.hyfkMs-9jXY3fjaJCTi2Ycduo1RUC6juKe64jxHLGXs"

tomorrow = (date.today() + timedelta(days=1)).isoformat()

payload = {
    "tutor_id": 27,
    "scheduled_date": tomorrow,
    "start_time": "09:00:00",
    "end_time": "10:00:00",
    "subject_id": 37,
    "notes": "Test session"
}

print(f"Testing schedule session with: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/scheduling/sessions",
        headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
        json=payload
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Session created: {json.dumps(data, indent=2, default=str)[:300]}")
    else:
        print(f"❌ Error:")
        print(response.text[:1000])
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

"""
Performance test for optimized endpoints
Run: python test_performance.py
"""
import asyncio
import time
import httpx
from typing import Dict

BASE_URL = "http://localhost:8000/api/v1"

# You need to get a valid token first by logging in
# Replace with actual token after login
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Replace this

async def test_endpoint(client: httpx.AsyncClient, endpoint: str, name: str) -> Dict:
    """Test an endpoint and measure time"""
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN != "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." else {}
    
    try:
        start = time.time()
        response = await client.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=30.0)
        duration = time.time() - start
        
        return {
            "name": name,
            "endpoint": endpoint,
            "status": response.status_code,
            "duration": f"{duration:.2f}s",
            "size": f"{len(response.content) / 1024:.1f}KB"
        }
    except Exception as e:
        return {
            "name": name,
            "endpoint": endpoint,
            "status": "ERROR",
            "duration": "N/A",
            "error": str(e)
        }

async def main():
    print("🔍 Performance Test for Optimized Endpoints\n")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        tests = [
            ("/tutors/available-courses", "Browse Courses (Optimized)"),
            ("/sessions/my-sessions?limit=10", "My Sessions (10 items)"),
            ("/sessions/my-sessions?limit=100", "My Sessions (100 items)"),
            ("/users/stats/dashboard", "Dashboard Stats"),
        ]
        
        for endpoint, name in tests:
            result = await test_endpoint(client, endpoint, name)
            
            print(f"\n📊 {result['name']}")
            print(f"   Endpoint: {result['endpoint']}")
            print(f"   Status: {result['status']}")
            print(f"   Duration: {result['duration']}")
            if 'size' in result:
                print(f"   Response Size: {result['size']}")
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            
            await asyncio.sleep(0.5)  # Small delay between requests
    
    print("\n" + "=" * 70)
    print("\n✅ Performance test completed!")
    print("\n💡 Tips:")
    print("   - Browse Courses should be < 1s (was 8-24s before optimization)")
    print("   - Dashboard Stats should be < 0.5s")
    print("   - If you see 401 errors, update TOKEN variable with valid JWT")

if __name__ == "__main__":
    asyncio.run(main())

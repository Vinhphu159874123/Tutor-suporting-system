"""
Quick Performance Test - Real-time metrics from deployed system
Tests actual production API performance without heavy load
"""
import asyncio
import time
from httpx import AsyncClient
import statistics

BASE_URL = "https://tutor-suporting-system-production.up.railway.app/api/v1"

TEST_ACCOUNTS = {
    "student": {"email": "student113@hcmut.edu.vn", "password": "TestPass123!"},
    "tutor": {"email": "tutor113@hcmut.edu.vn", "password": "TestPass123!"},
    "coordinator": {"email": "coordinator113@hcmut.edu.vn", "password": "TestPass123!"},
}

async def measure_request(name, func):
    """Measure single request performance"""
    start = time.time()
    try:
        result = await func()
        elapsed = time.time() - start
        return {"name": name, "time": elapsed, "status": "success", "result": result}
    except Exception as e:
        elapsed = time.time() - start
        return {"name": name, "time": elapsed, "status": "error", "error": str(e)}

async def login(client, account_type):
    """Login and get token"""
    response = await client.post("/auth/login", data={
        "username": TEST_ACCOUNTS[account_type]["email"],
        "password": TEST_ACCOUNTS[account_type]["password"]
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    return response.json()["access_token"]

async def test_quick_performance():
    """Quick performance test suite"""
    print("\n" + "="*60)
    print("🚀 QUICK PERFORMANCE TEST - Production API")
    print("="*60)
    
    results = []
    
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Test 1: Login performance
        print("\n📊 Test 1: Login Performance")
        login_times = []
        for i in range(5):
            start = time.time()
            token = await login(client, "student")
            elapsed = time.time() - start
            login_times.append(elapsed)
            print(f"  Login {i+1}: {elapsed:.3f}s")
        
        avg_login = statistics.mean(login_times)
        print(f"  ✅ Average: {avg_login:.3f}s, Min: {min(login_times):.3f}s, Max: {max(login_times):.3f}s")
        results.append({"test": "Login", "avg": avg_login, "min": min(login_times), "max": max(login_times)})
        
        # Get fresh token for other tests
        token = await login(client, "student")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 2: Get user profile
        print("\n📊 Test 2: Get User Profile")
        profile_times = []
        for i in range(5):
            start = time.time()
            response = await client.get("/auth/me", headers=headers)
            elapsed = time.time() - start
            profile_times.append(elapsed)
            print(f"  Request {i+1}: {elapsed:.3f}s")
        
        avg_profile = statistics.mean(profile_times)
        print(f"  ✅ Average: {avg_profile:.3f}s, Min: {min(profile_times):.3f}s, Max: {max(profile_times):.3f}s")
        results.append({"test": "Get Profile", "avg": avg_profile, "min": min(profile_times), "max": max(profile_times)})
        
        # Test 3: List sessions
        print("\n📊 Test 3: List Sessions")
        session_times = []
        for i in range(5):
            start = time.time()
            response = await client.get("/sessions/my-sessions", headers=headers)
            elapsed = time.time() - start
            session_times.append(elapsed)
            print(f"  Request {i+1}: {elapsed:.3f}s")
        
        avg_session = statistics.mean(session_times)
        print(f"  ✅ Average: {avg_session:.3f}s, Min: {min(session_times):.3f}s, Max: {max(session_times):.3f}s")
        results.append({"test": "List Sessions", "avg": avg_session, "min": min(session_times), "max": max(session_times)})
        
        # Test 4: Coordinator dashboard (more complex)
        print("\n📊 Test 4: Coordinator Dashboard Stats")
        coord_token = await login(client, "coordinator")
        coord_headers = {"Authorization": f"Bearer {coord_token}"}
        
        dashboard_times = []
        for i in range(3):
            start = time.time()
            response = await client.get("/users/stats/coordinator", headers=coord_headers)
            elapsed = time.time() - start
            dashboard_times.append(elapsed)
            print(f"  Request {i+1}: {elapsed:.3f}s")
        
        avg_dashboard = statistics.mean(dashboard_times)
        print(f"  ✅ Average: {avg_dashboard:.3f}s, Min: {min(dashboard_times):.3f}s, Max: {max(dashboard_times):.3f}s")
        results.append({"test": "Dashboard Stats", "avg": avg_dashboard, "min": min(dashboard_times), "max": max(dashboard_times)})
        
        # Test 5: Concurrent requests (light load)
        print("\n📊 Test 5: Concurrent Requests (10 simultaneous)")
        async def concurrent_request():
            start = time.time()
            await client.get("/auth/me", headers=headers)
            return time.time() - start
        
        concurrent_start = time.time()
        concurrent_times = await asyncio.gather(*[concurrent_request() for _ in range(10)])
        concurrent_total = time.time() - concurrent_start
        
        avg_concurrent = statistics.mean(concurrent_times)
        print(f"  ✅ Average per request: {avg_concurrent:.3f}s")
        print(f"  ✅ Total time (10 requests): {concurrent_total:.3f}s")
        print(f"  ✅ Throughput: {10/concurrent_total:.1f} req/s")
        results.append({"test": "Concurrent (10)", "avg": avg_concurrent, "total": concurrent_total, "throughput": 10/concurrent_total})
    
    # Summary
    print("\n" + "="*60)
    print("📈 PERFORMANCE SUMMARY")
    print("="*60)
    for r in results:
        test_name = r["test"]
        avg_time = r["avg"]
        status = "✅ Excellent" if avg_time < 1.0 else "⚠️ Good" if avg_time < 2.0 else "⚠️ Acceptable"
        print(f"{test_name:20s}: {avg_time:.3f}s {status}")
    
    print("\n💡 Performance Rating:")
    overall_avg = statistics.mean([r["avg"] for r in results if "avg" in r])
    if overall_avg < 1.0:
        print("   🌟🌟🌟 EXCELLENT - System performs very well!")
    elif overall_avg < 2.0:
        print("   🌟🌟 GOOD - System performs adequately")
    else:
        print("   🌟 ACCEPTABLE - Consider optimization")
    
    print(f"\n   Overall Average Response Time: {overall_avg:.3f}s")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_quick_performance())

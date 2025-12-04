#!/usr/bin/env python3
"""Test Redis cache performance for all cached endpoints"""
import requests
import time
import redis

API_URL = "http://localhost:8000/api/v1"

# Get fresh token
def get_token():
    """Login and get fresh JWT token"""
    try:
        # OAuth2PasswordRequestForm uses form-data with username/password
        response = requests.post(f"{API_URL}/auth/login", data={
            "username": "nhan.nguyenpercy@hcmut.edu.vn",
            "password": "trungnhan2005"
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"⚠️  Login failed: {response.status_code}")
            print(f"    Response: {response.text}")
            return None
    except Exception as e:
        print(f"⚠️  Login error: {e}")
        return None

TOKEN = get_token()
if not TOKEN:
    print("❌ Cannot get auth token. Exiting.")
    exit(1)

headers = {"Authorization": f"Bearer {TOKEN}"}

def test_endpoint(name, url, use_auth=True):
    """Test an endpoint twice to measure cache performance"""
    print(f"\n{'='*60}")
    print(f"📊 Testing: {name}")
    print(f"{'='*60}")
    
    req_headers = headers if use_auth else {}
    
    # First call (CACHE MISS)
    print("⏱️  First call (CACHE MISS)...")
    start = time.time()
    try:
        r1 = requests.get(url, headers=req_headers, timeout=10)
        miss_time = time.time() - start
        print(f"   Status: {r1.status_code}")
        print(f"   Response: {str(r1.json())[:100]}...")
        print(f"   ⚡ Time: {miss_time:.3f}s")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Second call (CACHE HIT)
    print("\n⏱️  Second call (CACHE HIT)...")
    start = time.time()
    try:
        r2 = requests.get(url, headers=req_headers, timeout=10)
        hit_time = time.time() - start
        print(f"   Status: {r2.status_code}")
        print(f"   Response: {str(r2.json())[:100]}...")
        print(f"   ⚡ Time: {hit_time:.3f}s")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Calculate improvement
    if miss_time > 0:
        improvement = ((miss_time - hit_time) / miss_time) * 100
        speedup = miss_time / hit_time if hit_time > 0 else 0
        print(f"\n   📈 Improvement: {improvement:.1f}%")
        print(f"   🚀 Speedup: {speedup:.1f}x faster")

def main():
    print("="*60)
    print("🧪 REDIS CACHE PERFORMANCE TEST")
    print("="*60)
    
    # Clear Redis cache
    print("\n🗑️  Clearing Redis cache...")
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.flushall()
        print("✅ Cache cleared\n")
    except Exception as e:
        print(f"⚠️  Could not clear cache: {e}\n")
    
    # Test all endpoints
    endpoints = [
        ("Dashboard Stats", f"{API_URL}/users/stats/dashboard?mode=student", True),
        ("My Sessions", f"{API_URL}/sessions/my-sessions/dashboard?mode=student", True),
        ("Available Courses", f"{API_URL}/tutors/available-courses", True),
        ("Subjects List", f"{API_URL}/courses/subjects", False),
        ("Admin Stats", f"{API_URL}/admin/stats", True),
        ("Forum Posts", f"{API_URL}/forum/posts?skip=0&limit=10", False),
    ]
    
    for name, url, use_auth in endpoints:
        test_endpoint(name, url, use_auth)
        time.sleep(0.5)  # Small delay between tests
    
    # Check Redis keys
    print(f"\n{'='*60}")
    print("🔑 Redis Cache Keys:")
    print("="*60)
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        keys = r.keys("*")
        if keys:
            for key in sorted(keys):
                ttl = r.ttl(key)
                print(f"  • {key} (TTL: {ttl}s)")
        else:
            print("  (no keys found)")
    except Exception as e:
        print(f"⚠️  Could not retrieve keys: {e}")
    
    # Redis stats
    print(f"\n{'='*60}")
    print("📊 Redis Statistics:")
    print("="*60)
    try:
        info = r.info('stats')
        print(f"  • Total commands: {info.get('total_commands_processed', 0)}")
        print(f"  • Cache hits: {info.get('keyspace_hits', 0)}")
        print(f"  • Cache misses: {info.get('keyspace_misses', 0)}")
        
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        if hits + misses > 0:
            hit_rate = (hits / (hits + misses)) * 100
            print(f"  • Hit rate: {hit_rate:.1f}%")
    except Exception as e:
        print(f"⚠️  Could not retrieve stats: {e}")
    
    print("\n✅ Test completed!\n")

if __name__ == "__main__":
    main()

"""
Web Performance Analyzer - Using Browser DevTools metrics
Generates commands and instructions to test deployed web performance
"""

print("""
🌐 WEB PERFORMANCE TESTING GUIDE
================================

Bạn có thể test performance của web deploy bằng các cách sau:

📊 METHOD 1: Chrome DevTools (Recommended - Fast & Visual)
---------------------------------------------------------
1. Mở Chrome/Edge tại: https://tutor-suporting-system-production.up.railway.app
2. Nhấn F12 hoặc Ctrl+Shift+I để mở DevTools
3. Vào tab "Network"
4. Refresh page (Ctrl+R)
5. Xem metrics ở góc dưới:
   - Total requests: X requests
   - Data transferred: X MB / X MB
   - Load time: X.XX s
   - DOMContentLoaded: X.XX s (màu xanh)
   - Load: X.XX s (màu đỏ)

✅ Good performance:
   - DOMContentLoaded < 1.5s
   - Load < 3s
   - Total requests < 100

📊 METHOD 2: Lighthouse (Detailed Analysis)
------------------------------------------
1. Mở Chrome DevTools (F12)
2. Vào tab "Lighthouse"
3. Chọn categories: Performance, Accessibility, Best Practices, SEO
4. Click "Analyze page load"
5. Đợi ~30s để có report chi tiết
6. Xem scores:
   - Performance: 90+ = Excellent
   - Accessibility: 90+ = Good
   - Best Practices: 90+ = Good
   - SEO: 90+ = Good

🚀 METHOD 3: Quick API Performance Test
---------------------------------------
Run this command to test API response times:
""")

print(f'curl -w "\\n\\nTime: %{{time_total}}s\\nSize: %{{size_download}} bytes\\n" https://tutor-suporting-system-production.up.railway.app/api/v1/health')

print("""

📊 METHOD 4: Online Tools (No installation needed)
--------------------------------------------------
1. GTmetrix: https://gtmetrix.com
   - Paste URL: https://tutor-suporting-system-production.up.railway.app
   - Click "Test your site"
   - Xem Performance Score, Structure Score, Web Vitals

2. PageSpeed Insights: https://pagespeed.web.dev
   - Paste URL
   - Xem Core Web Vitals:
     * LCP (Largest Contentful Paint): < 2.5s = Good
     * FID (First Input Delay): < 100ms = Good
     * CLS (Cumulative Layout Shift): < 0.1 = Good

3. WebPageTest: https://www.webpagetest.org
   - Detailed waterfall analysis
   - Multiple location testing

📊 METHOD 5: Python Script Performance Test
-------------------------------------------
""")

script_content = '''
import time
import requests

BASE_URL = "https://tutor-suporting-system-production.up.railway.app/api/v1"

print("\\n🧪 Testing API Endpoints...")

endpoints = [
    "/health",
    "/auth/login",  # POST with credentials
]

for endpoint in endpoints:
    try:
        start = time.time()
        response = requests.get(BASE_URL + endpoint, timeout=10)
        elapsed = time.time() - start
        print(f"✅ {endpoint}: {elapsed:.3f}s - Status {response.status_code}")
    except Exception as e:
        print(f"❌ {endpoint}: Error - {str(e)}")
'''

print("Save this as 'test_api_speed.py' and run:")
print("-" * 50)
print(script_content)
print("-" * 50)

print("""

💡 PERFORMANCE BENCHMARKS
=========================
Frontend (Browser):
  ⭐⭐⭐ Excellent: < 1s load time
  ⭐⭐ Good: 1-3s load time
  ⭐ Acceptable: 3-5s load time
  ❌ Poor: > 5s load time

Backend API:
  ⭐⭐⭐ Excellent: < 200ms response
  ⭐⭐ Good: 200-500ms response
  ⭐ Acceptable: 500ms-1s response
  ❌ Poor: > 1s response

🎯 QUICK CHECK
==============
Mở browser và chạy trong Console (F12 → Console):

performance.timing.loadEventEnd - performance.timing.navigationStart

Result < 3000 (3 giây) = Good performance!

📈 REAL-TIME MONITORING
======================
Nếu bạn muốn monitor liên tục, có thể dùng:
1. Railway built-in metrics (dashboard)
2. UptimeRobot (free monitoring)
3. New Relic / Datadog (advanced)

""")

print("\n✅ Recommendation: Use METHOD 1 (Chrome DevTools) for fastest visual check!")
print("✅ Or use METHOD 4 (GTmetrix) for comprehensive analysis without setup!\n")

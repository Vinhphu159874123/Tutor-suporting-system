#!/bin/bash

echo "🧪 Testing API Connection..."
echo ""

# Test 1: Health check
echo "1️⃣  Testing backend health..."
curl -s http://localhost:8000/docs > /dev/null && echo "✅ Backend is running" || echo "❌ Backend not running"
echo ""

# Test 2: Login test
echo "2️⃣  Testing login API..."
LOGIN_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/v1/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=student@hcmut.edu.vn&password=password123')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
  echo "✅ Login successful!"
  echo "   Token: ${TOKEN:0:50}..."
else
  echo "❌ Login failed"
  echo "   Response: $LOGIN_RESPONSE"
fi
echo ""

# Test 3: Get profile with token
if [ -n "$TOKEN" ]; then
  echo "3️⃣  Testing /auth/me endpoint..."
  PROFILE=$(curl -s http://localhost:8000/api/v1/auth/me \
    -H "Authorization: Bearer $TOKEN")
  
  EMAIL=$(echo $PROFILE | python3 -c "import sys, json; print(json.load(sys.stdin).get('email', ''))" 2>/dev/null)
  
  if [ -n "$EMAIL" ]; then
    echo "✅ Profile fetch successful!"
    echo "   Email: $EMAIL"
  else
    echo "❌ Profile fetch failed"
  fi
fi
echo ""

# Test 4: Test user update
if [ -n "$TOKEN" ]; then
  echo "4️⃣  Testing profile update..."
  UPDATE=$(curl -s -X PUT 'http://localhost:8000/api/v1/users/profile' \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{"full_name":"Student Test Updated","phone":"0123456789"}')
  
  UPDATED_NAME=$(echo $UPDATE | python3 -c "import sys, json; print(json.load(sys.stdin).get('full_name', ''))" 2>/dev/null)
  
  if [ "$UPDATED_NAME" = "Student Test Updated" ]; then
    echo "✅ Profile update successful!"
  else
    echo "❌ Profile update failed"
    echo "   Response: $UPDATE"
  fi
fi
echo ""

echo "🎉 API Connection Tests Complete!"
echo ""
echo "📋 Summary:"
echo "   - Backend URL: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Test credentials: student@hcmut.edu.vn / password123"
echo ""
echo "🚀 To start frontend:"
echo "   cd frontend && npm start"

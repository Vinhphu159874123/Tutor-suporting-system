#!/bin/bash

# Test cache performance for all cached endpoints
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDciLCJleHAiOjE3NjQ5NjExMDd9.eomXEfzMIvTHxzJaVixCgN2KK1TchGEFWCzJ5HWj4ko"
API_URL="http://localhost:8000/api/v1"

echo "========================================="
echo "🧪 REDIS CACHE PERFORMANCE TEST"
echo "========================================="
echo ""

# Clear cache
echo "🗑️  Clearing Redis cache..."
redis-cli FLUSHALL > /dev/null
echo "✅ Cache cleared"
echo ""

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local with_auth=$3
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Testing: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ "$with_auth" = "true" ]; then
        AUTH_HEADER="-H \"Authorization: Bearer $TOKEN\""
    else
        AUTH_HEADER=""
    fi
    
    echo "⏱️  First call (CACHE MISS):"
    MISS_TIME=$(curl -s -w "%{time_total}" -o /tmp/response.json \
        $([ "$with_auth" = "true" ] && echo "-H \"Authorization: Bearer $TOKEN\"") \
        "$url" 2>/dev/null)
    echo "   Response: $(head -c 100 /tmp/response.json)..."
    echo "   ⚡ Time: ${MISS_TIME}s"
    
    echo ""
    echo "⏱️  Second call (CACHE HIT):"
    HIT_TIME=$(curl -s -w "%{time_total}" -o /tmp/response.json \
        $([ "$with_auth" = "true" ] && echo "-H \"Authorization: Bearer $TOKEN\"") \
        "$url" 2>/dev/null)
    echo "   Response: $(head -c 100 /tmp/response.json)..."
    echo "   ⚡ Time: ${HIT_TIME}s"
    
    # Calculate improvement
    IMPROVEMENT=$(echo "scale=2; ($MISS_TIME - $HIT_TIME) / $MISS_TIME * 100" | bc 2>/dev/null || echo "N/A")
    echo ""
    echo "   📈 Improvement: ${IMPROVEMENT}%"
    echo ""
}

# Test all cached endpoints
test_endpoint "Dashboard Stats" "$API_URL/users/stats/dashboard?mode=student" "true"
test_endpoint "My Sessions" "$API_URL/sessions/my-sessions/dashboard?mode=student" "true"
test_endpoint "Available Courses" "$API_URL/tutors/available-courses" "true"
test_endpoint "Subjects List" "$API_URL/courses/subjects" "false"
test_endpoint "Admin Stats" "$API_URL/admin/stats" "true"
test_endpoint "Forum Posts" "$API_URL/forum/posts?skip=0&limit=10" "false"

# Check Redis keys
echo "========================================="
echo "🔑 Redis Cache Keys:"
echo "========================================="
redis-cli KEYS "*" | sort
echo ""

# Check Redis info
echo "========================================="
echo "📊 Redis Statistics:"
echo "========================================="
redis-cli INFO stats | grep -E "total_commands_processed|keyspace_hits|keyspace_misses|instantaneous_ops_per_sec"
echo ""

echo "✅ Test completed!"

#!/bin/bash

# Script to run tests with server logs visible

cd /Users/nguyentrungnhan/Tutor-suporting-system
source vevn/bin/activate
cd backend

echo "🚀 Starting server with logs..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

echo "⏳ Waiting for server..."
sleep 5

echo ""
echo "🧪 Running tests..."
echo "========================================"
python test_scheduling_simple.py

echo ""
echo "🛑 Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo "✅ Done!"

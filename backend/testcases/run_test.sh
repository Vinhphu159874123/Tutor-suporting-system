#!/bin/bash

# Script to run scheduling tests
# This starts server in background and runs tests

cd /Users/nguyentrungnhan/Tutor-suporting-system
source vevn/bin/activate
cd backend

echo "🚀 Starting server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
SERVER_PID=$!

echo "⏳ Waiting for server to start..."
sleep 5

echo "🧪 Running tests..."
python test_scheduling_simple.py

echo ""
echo "🛑 Stopping server..."
kill $SERVER_PID 2>/dev/null

echo "✅ Done!"

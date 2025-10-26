"""
Quick Test Script for Backend API
Run this to test the API without Docker
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 Starting HCMUT Tutor Support System Backend")
    print("=" * 60)
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("📖 Alternative docs: http://localhost:8000/redoc")
    print("=" * 60)
    print("\n✅ Backend is starting...\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
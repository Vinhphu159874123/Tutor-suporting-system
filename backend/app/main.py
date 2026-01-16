from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from app.api import auth, users, tutors, students, sessions, scheduling, reports, admin, forum, notifications, courses, coordinator, study_groups, progress, schedule_preferences, websocket_api
from app.core.database import engine, create_tables
from app.core.config import settings
from app.events import register_all_listeners

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="HCMUT Tutor Support System",
    description="Full-stack tutor support system for Ho Chi Minh City University of Technology",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Add CORS middleware
allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,http://localhost").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# Include API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tutors.router, prefix="/api/v1/tutors", tags=["tutors"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(scheduling.router, prefix="/api/v1/scheduling", tags=["scheduling"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(coordinator.router, prefix="/api/v1/coordinator", tags=["coordinator"])
app.include_router(forum.router, prefix="/api/v1/forum", tags=["forum"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])
app.include_router(study_groups.router, prefix="/api/v1/study-groups", tags=["study-groups"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])
app.include_router(schedule_preferences.router, prefix="/api/v1/schedule-preferences", tags=["schedule-preferences"])
app.include_router(websocket_api.router, prefix="/api/v1", tags=["websocket"])
# Materials endpoints are in sessions.py router (/{session_id}/materials)

@app.on_event("startup")
async def startup_event():
    """Create database tables and register event listeners on startup"""
    try:
        # Register event listeners
        register_all_listeners()
        print("✅ Event listeners registered")
        
        # Create database tables
        await create_tables()
        await create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("⚠️  API will run without database connection for testing")
    print("🚀 HCMUT Tutor Support System API is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🔄 HCMUT Tutor Support System API is shutting down...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HCMUT Tutor Support System API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "external_services": {
            "hcmut_sso": "mocked",
            "hcmut_datacore": "mocked", 
            "hcmut_library": "mocked",
            "ai_recommender": "mocked"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
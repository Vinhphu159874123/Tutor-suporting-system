from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Mock HCMUT SSO Service")

class LoginRequest(BaseModel):
    username: str
    password: str

class SSOUserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    faculty: str
    major: str
    student_id: str = None
    staff_id: str = None
    role: str

# Mock user database
mock_users = {
    "student@hcmut.edu.vn": {
        "id": "student_001",
        "email": "student@hcmut.edu.vn",
        "full_name": "Nguyễn Văn An",
        "faculty": "Khoa Khoa học và Kỹ thuật Máy tính",
        "major": "Khoa học Máy tính",
        "student_id": "2011234",
        "role": "student"
    },
    "tutor@hcmut.edu.vn": {
        "id": "tutor_001", 
        "email": "tutor@hcmut.edu.vn",
        "full_name": "Trần Thị Bình",
        "faculty": "Khoa Khoa học và Kỹ thuật Máy tính",
        "major": "Kỹ thuật Phần mềm",
        "student_id": "1911234",
        "role": "tutor"
    },
    "admin@hcmut.edu.vn": {
        "id": "admin_001",
        "email": "admin@hcmut.edu.vn", 
        "full_name": "Lê Văn Cường",
        "faculty": "Phòng Đào tạo",
        "major": None,
        "staff_id": "GV001",
        "role": "admin"
    }
}

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Mock SSO login endpoint"""
    if request.password != "password123":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = mock_users.get(request.username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@app.get("/auth/validate")
async def validate_token():
    """Mock token validation"""
    return {"valid": True}

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Mock get user info"""
    for user in mock_users.values():
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/")
async def root():
    return {"message": "Mock HCMUT SSO Service", "status": "active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)
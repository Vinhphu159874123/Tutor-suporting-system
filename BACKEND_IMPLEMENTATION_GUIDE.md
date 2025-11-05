# 🚀 HƯỚNG DẪN TRIỂN KHAI BACKEND - HỆ THỐNG HỖ TRỢ GIẢNG DẠY

## 📋 TỔNG QUAN

Tài liệu này cung cấp hướng dẫn đầy đủ để triển khai các tính năng backend còn thiếu cho hệ thống hỗ trợ giảng dạy. Tất cả các file placeholder và SQL migration đã được tạo sẵn để team có thể bắt đầu development ngay lập tức.

**📁 Cấu trúc dự án hoàn chỉnh sau khi triển khai:**
```
backend/
├── app/
│   ├── api/
│   │   ├── materials.py          # ✅ MỚI - API quản lý materials
│   │   ├── progress.py           # ✅ MỚI - API tracking progress
│   │   └── study_groups.py       # ✅ MỚI - API quản lý groups
│   ├── services/
│   │   ├── materials_service.py  # ✅ MỚI - Business logic materials
│   │   ├── progress_service.py   # ✅ MỚI - Business logic progress
│   │   └── study_groups_service.py # ✅ MỚI - Business logic groups
│   ├── repositories/
│   │   ├── materials_repository.py # ✅ MỚI - Data access materials
│   │   ├── progress_repository.py # ✅ MỚI - Data access progress
│   │   └── study_groups_repository.py # ✅ MỚI - Data access groups
│   └── schemas/
│       ├── materials.py          # ✅ MỚI - Validation schemas
│       ├── progress.py           # ✅ MỚI - Validation schemas
│       └── study_groups.py       # ✅ MỚI - Validation schemas
└── database_migration.sql        # ✅ MỚI - SQL migration script
```

---

## 🗄️ 1. THIẾT LẬP DATABASE

### Bước 1: Chạy Migration Script

```bash
# Kết nối PostgreSQL và chạy migration
psql -U your_username -d tutor_system -f database_migration.sql
```

### Bước 2: Verify Database Setup

```sql
-- Kiểm tra tables đã được tạo
SELECT tablename FROM pg_tables WHERE schemaname = 'public' 
ORDER BY tablename;

-- Kiểm tra indexes
SELECT tablename, indexname FROM pg_indexes WHERE schemaname = 'public'
ORDER BY tablename;
```

### 📊 Database Schema Chi Tiết

**Các bảng mới được tạo:**

| Bảng | Mục đích | Quan hệ |
|------|----------|---------|
| `session_materials` | Lưu tài liệu session | → sessions, users |
| `tutor_availability` | Lịch rảnh của tutor | → tutors |
| `progress_tracking` | Theo dõi tiến độ học | → students, sessions, subjects |
| `learning_achievements` | Thành tích học tập | → students |
| `study_groups` | Nhóm học tập | → subjects, users |
| `study_group_members` | Thành viên nhóm | → study_groups, users |

---

## 🔧 2. CẬP NHẬT BACKEND CODE

### Bước 1: Cập nhật main.py

Thêm vào `backend/app/main.py`:

```python
# Import new routers
from app.api import materials, progress, study_groups

# Add new routes
app.include_router(materials.router, prefix="/api/v1/materials", tags=["materials"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])
app.include_router(study_groups.router, prefix="/api/v1/study-groups", tags=["study-groups"])
```

### Bước 2: Cập nhật dependencies.py

Thêm vào `backend/app/core/dependencies.py`:

```python
from app.services.materials_service import MaterialsService
from app.services.progress_service import ProgressService
from app.services.study_groups_service import StudyGroupsService

from app.repositories.materials_repository import MaterialsRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.study_groups_repository import StudyGroupsRepository

async def get_materials_service(db: AsyncSession = Depends(get_database)) -> MaterialsService:
    repository = MaterialsRepository(db)
    return MaterialsService(repository)

async def get_progress_service(db: AsyncSession = Depends(get_database)) -> ProgressService:
    repository = ProgressRepository(db)
    return ProgressService(repository)

async def get_study_groups_service(db: AsyncSession = Depends(get_database)) -> StudyGroupsService:
    repository = StudyGroupsRepository(db)
    return StudyGroupsService(repository)
```

### Bước 3: Cập nhật database models

Thêm vào `backend/app/models/database.py`:

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Session Materials Model
class SessionMaterial(Base):
    __tablename__ = "session_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="materials")
    uploader = relationship("User")

# Tutor Availability Model
class TutorAvailability(Base):
    __tablename__ = "tutor_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutors.id", ondelete="CASCADE"))
    day_of_week = Column(Integer, nullable=False)  # 0-6 (Monday-Sunday)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_recurring = Column(Boolean, default=True)
    specific_date = Column(Date, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tutor = relationship("Tutor", back_populates="availability")

# Progress Tracking Model
class ProgressTracking(Base):
    __tablename__ = "progress_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    topics_covered = Column(ARRAY(String), default=[])
    understanding_level = Column(Integer, nullable=False)
    notes = Column(Text)
    tutor_feedback = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student")
    session = relationship("Session", back_populates="progress")
    subject = relationship("Subject")

# Learning Achievements Model
class LearningAchievement(Base):
    __tablename__ = "learning_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    achievement_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    metadata = Column(JSON, default={})
    earned_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="achievements")

# Study Groups Model
class StudyGroup(Base):
    __tablename__ = "study_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"))
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    max_members = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    subject = relationship("Subject")
    creator = relationship("User")
    members = relationship("StudyGroupMember", back_populates="group")

# Study Group Members Model
class StudyGroupMember(Base):
    __tablename__ = "study_group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("study_groups.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String(50), default="member")
    joined_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    group = relationship("StudyGroup", back_populates="members")
    user = relationship("User")

# NOTE: Library models removed as this feature is not implemented
```

---

## 🚀 3. WORKFLOW DEVELOPMENT

### 📋 Phase 1: Core Implementation (Week 1-2)

**👨‍💻 Team A - Materials & Progress (2 developers)**
- [ ] Implement `MaterialsService` với file upload/download
- [ ] Implement `ProgressService` với analytics logic
- [ ] Viết unit tests cho Materials module
- [ ] Viết unit tests cho Progress module
- [ ] Integration testing với existing sessions

**👩‍💻 Team B - Study Groups (1-2 developers)**  
- [ ] Implement `StudyGroupsService` với membership management
- [ ] Viết unit tests cho Study Groups module  
- [ ] API documentation với Swagger
- [ ] UI integration testing

### 📋 Phase 2: Advanced Features (Week 3-4)

**🔧 Backend Enhancements**
- [ ] File upload validation và virus scanning
- [ ] Real-time notifications cho study groups
- [ ] Advanced search với Elasticsearch
- [ ] Caching với Redis
- [ ] Rate limiting và security hardening

**📊 Analytics & Reporting**
- [ ] Progress analytics dashboard
- [ ] Performance metrics tracking
- [ ] Usage statistics collection
- [ ] Automated report generation

### 📋 Phase 3: Integration & Deployment (Week 5-6)

**🔗 Frontend Integration**
- [ ] Connect với existing React components
- [ ] Real-time updates với WebSocket
- [ ] Mobile responsiveness testing
- [ ] Cross-browser compatibility

**🚀 Production Deployment**
- [ ] Docker containerization
- [ ] CI/CD pipeline setup
- [ ] Performance testing
- [ ] Security audit
- [ ] Go-live preparation

---

## 📝 4. IMPLEMENTATION CHECKLIST

### ✅ Completed (Đã tạo placeholders)

- [x] **API Layer** - 3 router files với đầy đủ endpoints (Materials, Progress, Study Groups)
- [x] **Service Layer** - 3 service classes với business logic stubs  
- [x] **Repository Layer** - 3 repository classes với database operation stubs
- [x] **Schema Layer** - 3 Pydantic model files với validation rules
- [x] **Database Migration** - SQL script với tables, indexes, triggers
- [x] **Documentation** - Implementation guides và development plan

### 🔄 Cần implement (TODO)

- [ ] **Materials Module**
  - [ ] File upload/download logic
  - [ ] MIME type validation  
  - [ ] File size limits
  - [ ] Storage management (local/S3)
  
- [ ] **Progress Module**
  - [ ] Analytics calculations
  - [ ] Achievement auto-generation
  - [ ] Progress visualization data
  - [ ] Trend analysis algorithms

- [ ] **Study Groups Module**
  - [ ] Group membership workflow
  - [ ] Permission management
  - [ ] Group activity tracking
  - [ ] Invitation system

- [ ] **Library Module** - ❌ REMOVED (không implement)

---

## 🧪 5. TESTING STRATEGY

### Unit Testing

```bash
# Chạy tests cho từng module
python -m pytest tests/test_materials.py -v
python -m pytest tests/test_progress.py -v  
python -m pytest tests/test_study_groups.py -v
python -m pytest tests/test_library.py -v
```

### Integration Testing

```bash
# Test API endpoints
python -m pytest tests/integration/ -v

# Test database operations
python -m pytest tests/test_repositories.py -v
```

### Test Coverage

```bash
# Generate coverage report
python -m pytest --cov=app --cov-report=html
```

---

## 🔧 6. CONFIGURATION & ENVIRONMENT

### Environment Variables Cần Thêm

```bash
# File storage settings
FILE_STORAGE_PATH=/app/uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_MIME_TYPES=image/jpeg,image/png,application/pdf,text/plain

# NOTE: Library API environment variables removed

# Redis for caching
REDIS_URL=redis://localhost:6379/0

# Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Docker Compose Updates

Thêm vào `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    environment:
      - REDIS_URL=redis://redis:6379/0
      - FILE_STORAGE_PATH=/app/uploads
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - db
      - redis

volumes:
  redis_data:
```

---

## 📊 7. API ENDPOINTS REFERENCE

### Materials API (`/api/v1/materials`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/session/{session_id}` | Lấy materials của session |
| POST | `/session/{session_id}` | Upload material mới |
| GET | `/{material_id}` | Lấy thông tin material |
| PUT | `/{material_id}` | Cập nhật material |
| DELETE | `/{material_id}` | Xóa material |
| GET | `/{material_id}/download` | Download file |

### Progress API (`/api/v1/progress`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/student/{student_id}` | Lấy tiến độ học sinh |
| POST | `/session/{session_id}` | Tạo progress record |
| PUT | `/{progress_id}` | Cập nhật progress |
| GET | `/{student_id}/achievements` | Lấy achievements |
| GET | `/{student_id}/analytics` | Analytics data |

### Study Groups API (`/api/v1/study-groups`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Lấy danh sách groups |
| POST | `/` | Tạo group mới |
| GET | `/{group_id}` | Chi tiết group |
| PUT | `/{group_id}` | Cập nhật group |
| POST | `/{group_id}/join` | Tham gia group |
| DELETE | `/{group_id}/leave` | Rời group |
| GET | `/{group_id}/members` | Danh sách members |

### ~~Library API~~ - ❌ REMOVED
*Tính năng thư viện đã được bỏ theo yêu cầu*

---

## 🔒 8. SECURITY CONSIDERATIONS

### File Upload Security

```python
# Implement trong MaterialsService
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.jpg', '.png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file):
    # Check file extension
    if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise ValueError("File type not allowed")
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    # Virus scan (if available)
    # scan_for_viruses(file)
```

### Data Privacy

```python
# Implement access control
class MaterialsService:
    async def get_session_materials(self, session_id: int, user_id: int):
        # Verify user has access to session
        session = await self.session_repo.get_by_id(session_id)
        if not (session.tutor_id == user_id or session.student_id == user_id):
            raise PermissionError("Access denied")
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/session/{session_id}")
@limiter.limit("10/minute")  # Max 10 uploads per minute
async def upload_material(...):
    pass
```

---

## 📈 9. MONITORING & LOGGING

### Logging Configuration

```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Usage in services
class MaterialsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def upload_file(self, file):
        self.logger.info(f"File upload started: {file.filename}")
        # ... implementation
        self.logger.info(f"File upload completed: {file.filename}")
```

### Performance Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log slow queries (>1s)
        if execution_time > 1.0:
            logging.warning(f"Slow operation: {func.__name__} took {execution_time:.2f}s")
        
        return result
    return wrapper

# Usage
@monitor_performance
async def complex_query(...):
    pass
```

---

## 🚀 10. DEPLOYMENT GUIDE

### Local Development Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd tutor-supporting-system

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# 3. Setup database  
createdb tutor_system
psql -U postgres -d tutor_system -f ../database_migration.sql

# 4. Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Setup frontend (new terminal)
cd ../frontend
npm install
npm start
```

### Docker Development

```bash
# Build and start all services
docker-compose up --build

# Check logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Deployment

```bash
# 1. Build production images
docker-compose -f docker-compose.prod.yml build

# 2. Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# 3. Check health
curl http://your-domain.com/health

# 4. Monitor logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 📞 11. SUPPORT & TROUBLESHOOTING

### Common Issues

**❌ Import Errors**
```bash
# Fix: Ensure all new files are in correct locations
# Check: All __init__.py files exist in directories
```

**❌ Database Connection Issues**
```bash
# Check: PostgreSQL is running
sudo service postgresql status

# Check: Database exists
psql -l | grep tutor_system
```

**❌ File Upload Fails**
```bash
# Check: Upload directory permissions
ls -la /app/uploads
chmod 755 /app/uploads
```

### Performance Issues

**🐌 Slow API Responses**
- Enable database query logging
- Check for N+1 query problems  
- Add database indexes
- Implement caching with Redis

**📈 High Memory Usage**
- Monitor file upload sizes
- Implement file cleanup jobs
- Use streaming for large files

### Contact Information

- **Tech Lead**: [Your contact]
- **Database Admin**: [Your contact]  
- **DevOps**: [Your contact]
- **Project Manager**: [Your contact]

---

## 🎯 12. SUCCESS METRICS

### Development KPIs

- [ ] **Code Coverage**: >80% for all new modules
- [ ] **API Response Time**: <200ms average
- [ ] **Database Query Time**: <100ms average  
- [ ] **File Upload Speed**: >1MB/s
- [ ] **Test Pass Rate**: 100%
- [ ] **Documentation Coverage**: 100%

### Business KPIs

- [ ] **User Adoption**: 90% of tutors use materials feature
- [ ] **Progress Tracking**: 85% of sessions have progress records
- [ ] **Study Groups**: 50% of students join at least one group

---

**🎉 CHÚC MỪNG! Bạn đã có đầy đủ foundation để bắt đầu development. Good luck! 🚀**

---

*📅 Last Updated: November 2025*  
*📝 Version: 1.0*  
*👨‍💻 Created by: GitHub Copilot Assistant*
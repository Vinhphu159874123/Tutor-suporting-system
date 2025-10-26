# 🏗️ Backend Architecture Guide

## 📐 Layered Architecture Pattern

```
Client (HTTP Request)
    ↓
FastAPI App (main.py)
    ↓
Middleware Layer
    ├── CORS Middleware
    ├── Database Middleware
    └── Custom Middleware
    ↓
Route Layer (api/*.py)
    ├── Parse request
    ├── Validate with Pydantic (schemas)
    └── Call Service/Controller
    ↓
Service Layer (services/*.py)
    ├── Business Logic
    ├── Orchestration
    └── Call Repository
    ↓
Repository Layer (repositories/*.py)
    ├── Database Operations
    ├── SQL Queries
    └── Data Access
    ↓
Model Layer (models/database.py)
    ├── SQLAlchemy Models
    └── Database Schema
    ↓
Database (PostgreSQL via Supabase)
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                    # 🛣️ ROUTES LAYER (HTTP Endpoints)
│   │   ├── __init__.py        # Router registration
│   │   ├── auth.py            # Authentication endpoints (login, register, me)
│   │   ├── students.py        # Student endpoints (CRUD, profile)
│   │   ├── tutors.py          # Tutor endpoints (CRUD, availability)
│   │   ├── sessions.py        # Session endpoints (create, manage)
│   │   ├── scheduling.py      # Scheduling endpoints (availability, slots)
│   │   ├── reports.py         # Reports endpoints (analytics, statistics)
│   │   ├── admin.py           # Admin endpoints (user management, configs)
│   │   ├── forum.py           # Forum endpoints (posts, comments, discussions)
│   │   └── users.py           # User management endpoints (legacy)
│   │
│   ├── schemas/                # 📋 PYDANTIC SCHEMAS (Data Validation)
│   │   ├── __init__.py        # Export all schemas
│   │   ├── auth.py            # UserCreate, UserResponse, Token, TokenData
│   │   ├── student.py         # StudentCreate, StudentUpdate, StudentResponse
│   │   ├── tutor.py           # TutorCreate, TutorUpdate, TutorResponse
│   │   ├── session.py         # SessionCreate, SessionUpdate, SessionResponse
│   │   ├── scheduling.py      # AvailabilityCreate, SlotRequest
│   │   ├── report.py          # ReportCreate, ReportResponse
│   │   └── forum.py           # PostCreate, CommentCreate
│   │
│   ├── services/               # 🧠 BUSINESS LOGIC LAYER
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Authentication, JWT, password hashing
│   │   ├── student_service.py # Student registration, profile management
│   │   ├── tutor_service.py   # Tutor management, availability
│   │   ├── session_service.py # Session creation, completion, cancellation
│   │   ├── scheduling_service.py # Availability management, slot finding
│   │   ├── reports_service.py # Analytics, performance reports
│   │   ├── admin_service.py   # User management, system configs
│   │   ├── forum_service.py   # Forum posts, comments, moderation
│   │   └── hcmut_sso.py      # Mock HCMUT SSO integration
│   │
│   ├── repositories/           # 🗄️ DATA ACCESS LAYER (Database Operations)
│   │   ├── __init__.py
│   │   ├── user_repository.py # User CRUD operations
│   │   ├── student_repository.py # Student CRUD operations
│   │   ├── tutor_repository.py # Tutor CRUD operations
│   │   ├── session_repository.py # Session CRUD operations
│   │   ├── scheduling_repository.py # Availability CRUD operations
│   │   ├── reports_repository.py # Reports data retrieval
│   │   ├── admin_repository.py # Admin operations
│   │   └── forum_repository.py # Forum data operations
│   │
│   ├── events/                 # 🔔 EVENT SYSTEM (Async Side Effects)
│   │   ├── __init__.py        # Export event bus and listeners
│   │   ├── event_bus.py       # EventBus class (fire-and-forget)
│   │   ├── base_listener.py   # BaseListener abstract class
│   │   ├── event_types.py     # Event constants (SESSION_CREATED, etc.)
│   │   └── listeners/         # Event listeners
│   │       ├── __init__.py    # Register all listeners
│   │       ├── session_listener.py # Session events (created, completed, cancelled)
│   │       ├── notification_listener.py # Email, push notifications
│   │       └── statistics_listener.py # Analytics, audit logs
│   │
│   ├── models/                 # 🗃️ DATABASE MODELS (SQLAlchemy ORM)
│   │   └── database.py        # User, Student, Tutor, Session, TutorAvailability models
│   │
│   ├── core/                   # ⚙️ CORE CONFIGURATION
│   │   ├── config.py          # Environment settings (Pydantic BaseSettings)
│   │   ├── database.py        # Async DB engine, session maker
│   │   └── dependencies.py    # Dependency Injection providers
│   │
│   ├── middleware/             # 🔀 MIDDLEWARE LAYER (optional custom)
│   │   └── (future: logging, rate limiting)
│   │
│   └── main.py                # 🚀 FastAPI App Entry Point
│
├── docs/                       # 📚 DOCUMENTATION
│   ├── ARCHITECTURE_GUIDE.md  # This file
│   ├── EVENT_SYSTEM.md        # Event system documentation
│   ├── QUICK_REFERENCE.md     # Quick commands reference
│   └── ...
│
├── tests/                      # 🧪 TESTS (future)
├── .env                        # 🔐 Environment variables
├── requirements.txt            # 📦 Python dependencies
└── README.md                   # 📖 Project README
```

---

## 🔄 Request Flow Example

### Example: Student Registration - `POST /api/v1/students/register`

```python
# 1️⃣ CLIENT → HTTP Request
POST /api/v1/students/register
Headers: Authorization: Bearer <jwt_token>
Body: {
  "year": 3,
  "gpa": 3.5,
  "interests": ["Math", "Physics"],
  "bio": "Need help with Calculus"
}

# 2️⃣ FASTAPI APP (main.py)
- Receives request
- Routes to appropriate router

# 3️⃣ ROUTES LAYER (api/students.py)
@router.post("/register")
async def register_student(
    data: StudentCreate,                    # ← Pydantic validates request
    student_service: StudentService = Depends(get_student_service),  # ← DI
    current_user: User = Depends(get_current_user)  # ← Auth check
):
    """
    - Parse HTTP request
    - Validate with Pydantic schema
    - Inject StudentService via Depends()
    - Verify JWT token
    """
    return await student_service.register_student(current_user.id, data)
    # ↓ Delegates to Service Layer

# 4️⃣ SERVICE LAYER (services/student_service.py)
async def register_student(self, user_id: int, data: StudentCreate):
    """
    - Check if user already registered as student
    - Validate business rules (year, GPA constraints)
    - Prepare data for database
    - Emit STUDENT_REGISTERED event
    """
    # Business logic
    if await self.student_repo.exists_by_user_id(user_id):
        raise HTTPException(400, "Already registered")
    
    student_data = {
        "user_id": user_id,
        "year": data.year,
        "gpa": data.gpa,
        "interests": data.interests,
        "bio": data.bio,
        "is_active": True
    }
    
    # Call Repository
    student = await self.student_repo.create(student_data)
    
    # Emit event (async, non-blocking)
    await event_bus.emit(EventTypes.STUDENT_REGISTERED, {
        "student_id": student.id,
        "user_id": user_id
    })
    
    return student
    # ↓ Calls Repository Layer

# 5️⃣ REPOSITORY LAYER (repositories/student_repository.py)
async def create(self, student_data: dict) -> Student:
    """
    - Pure database operations
    - No business logic
    - Execute SQL INSERT
    """
    student = Student(**student_data)
    self.db.add(student)
    await self.db.commit()
    await self.db.refresh(student)
    return student
    # ↓ Calls Database

# 6️⃣ DATABASE (PostgreSQL via Supabase)
INSERT INTO students (user_id, year, gpa, interests, bio, is_active, created_at)
VALUES (123, 3, 3.5, '["Math", "Physics"]', 'Need help...', true, NOW())
RETURNING *;

# 7️⃣ EVENT SYSTEM (Async, Non-Blocking)
# SessionCreatedListener.handle() - Send notification email
# StatisticsListener.handle() - Update analytics
# AuditLogListener.handle() - Log action

# 8️⃣ RESPONSE → CLIENT
{
  "id": 1,
  "user_id": 123,
  "year": 3,
  "gpa": 3.5,
  "interests": ["Math", "Physics"],
  "bio": "Need help with Calculus",
  "is_active": true,
  "created_at": "2025-10-27T01:30:00Z"
}
```
@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,  # ← Pydantic validates body
    current_user = Depends(get_current_user),  # ← Dependency injection
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.update_user_profile(
        user_id=current_user.id,
        user_data=user_data
    )

# 4️⃣ SERVICE (services/user_service.py)
class UserService:
    async def update_user_profile(self, user_id, user_data):
        # Business logic
        if not user_data.full_name:
            raise HTTPException(400, "Name required")
        
        # Call repository
        user = await self.user_repo.update(user_id, user_data.dict())
        return user

# 5️⃣ REPOSITORY (repositories/user_repository.py)
class UserRepository:
    async def update(self, user_id, data):
        # SQL query
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**data)
        )
        await self.db.commit()
        return await self.get_by_id(user_id)

# 6️⃣ MODEL (models/database.py)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255))
    # ...

# 7️⃣ DATABASE
PostgreSQL executes: UPDATE users SET full_name = 'New Name' ...

# 8️⃣ RESPONSE ← Flow reversed
Database → Repository → Service → Route → Middleware → Client
```

---

## 🎯 Responsibility of Each Layer

### **1. Route Layer** (`api/`)
**Responsibility:** 
- Accept HTTP requests
- Validate request with Pydantic schemas
- Extract dependencies (auth, services)
- Call service methods
- Return HTTP responses

**DON'T:**
- ❌ Business logic
- ❌ Database queries
- ❌ Complex calculations

**Example:**
```python
@router.post("/tutors/register")
async def register_tutor(
    data: TutorRegisterSchema,
    current_user = Depends(get_current_user),
    tutor_service: TutorService = Depends(get_tutor_service)
):
    """Just route the request to service"""
    return await tutor_service.register_tutor(current_user.id, data)
```

---

### **2. Service Layer** (`services/`)
**Responsibility:**
- Business logic
- Validation rules
- Orchestrate multiple repositories
- Handle errors
- Transaction management

**DON'T:**
- ❌ Direct database queries (use repository)
- ❌ HTTP request handling

**Example:**
```python
class TutorService:
    async def register_tutor(self, user_id, data):
        # Business validation
        if len(data.subjects) == 0:
            raise HTTPException(400, "Must select subjects")
        
        # Check if already tutor
        existing = await self.tutor_repo.get_by_user_id(user_id)
        if existing:
            raise HTTPException(400, "Already registered as tutor")
        
        # Create tutor
        tutor = await self.tutor_repo.create({
            "user_id": user_id,
            "bio": data.bio,
            "status": "pending"  # Business rule
        })
        
        # Add subjects
        for subject in data.subjects:
            await self.tutor_repo.add_subject(tutor.id, subject)
        
        return tutor
```

---

### **3. Repository Layer** (`repositories/`)
**Responsibility:**
- Database operations ONLY
- CRUD methods
- SQL queries
- Data retrieval

**DON'T:**
- ❌ Business logic
- ❌ Validation
- ❌ Error handling (except DB errors)

**Example:**
```python
class TutorRepository:
    async def get_by_user_id(self, user_id: int):
        """Pure database query"""
        result = await self.db.execute(
            select(Tutor).where(Tutor.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, data: dict):
        """Pure database insert"""
        tutor = Tutor(**data)
        self.db.add(tutor)
        await self.db.commit()
        await self.db.refresh(tutor)
        return tutor
```

---

### **4. Schema Layer** (`schemas/`)
**Responsibility:**
- Request validation
- Response serialization
- Type checking
- Documentation

**Example:**
```python
class TutorRegisterSchema(BaseModel):
    bio: str
    subjects: List[str]
    
    @validator('subjects')
    def validate_subjects(cls, v):
        if len(v) == 0:
            raise ValueError('Must provide at least 1 subject')
        return v
```

---

## 🔗 Dependency Injection Pattern

### **Why Dependency Injection?**
- ✅ Easier testing (can mock dependencies)
- ✅ Loose coupling
- ✅ Single Responsibility Principle
- ✅ Dependency Inversion Principle

### **How it works:**

```python
# core/dependencies.py
def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db)

def get_auth_service(user_repo = Depends(get_user_repository)):
    return AuthService(user_repo)

# api/auth.py
@router.post("/login")
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)  # ← Injected!
):
    return await auth_service.login(credentials.email, credentials.password)
```

---

## ✅ Benefits of This Architecture

### **1. Testability**
```python
# Easy to mock
def test_register_tutor():
    mock_repo = Mock()
    mock_repo.get_by_user_id.return_value = None
    
    service = TutorService(mock_repo)
    result = await service.register_tutor(1, data)
    
    assert result.status == "pending"
```

### **2. Maintainability**
- Each layer has clear responsibility
- Easy to find bugs (know which layer to check)
- Easy to add features

### **3. Scalability**
- Can swap implementations (e.g., different database)
- Can add caching layer
- Can add message queues

### **4. Team Collaboration**
- Frontend dev: Work with schemas
- Backend dev: Work with services
- DBA: Work with repositories
- DevOps: Work with config/middleware

---

## 📝 Migration Checklist

### ✅ Completed:
- [x] Create folder structure
- [x] Create schema files (auth, user)
- [x] Create repository (UserRepository)
- [x] Create service (AuthService)
- [x] Create dependencies file

### 🔄 In Progress:
- [ ] Refactor auth.py to use new architecture
- [ ] Refactor users.py to use new architecture
- [ ] Test refactored modules

### 📋 TODO:
- [ ] Create TutorRepository
- [ ] Create TutorService
- [ ] Implement tutors.py with new architecture
- [ ] Create StudentRepository
- [ ] Create StudentService
- [ ] Implement students.py
- [ ] Continue with other modules...

---

## 🎓 Best Practices

1. **Keep routes thin**
   ```python
   # ✅ Good
   @router.post("/")
   async def create_tutor(data, service = Depends(...)):
       return await service.create(data)
   
   # ❌ Bad - too much logic in route
   @router.post("/")
   async def create_tutor(data, db = Depends(...)):
       if len(data.subjects) == 0:
           raise HTTPException(...)
       result = await db.execute(...)
       # ... 20 lines of code
   ```

2. **Services orchestrate, repositories execute**
   ```python
   # Service
   async def create_session(self, data):
       # Orchestrate multiple repo calls
       tutor = await self.tutor_repo.get(data.tutor_id)
       student = await self.student_repo.get(data.student_id)
       session = await self.session_repo.create(data)
       await self.notification_service.notify_both(tutor, student)
   ```

3. **Use schemas for everything**
   - Request validation
   - Response serialization
   - Internal data transfer

4. **Type hints everywhere**
   ```python
   async def get_user(self, user_id: int) -> Optional[User]:
       ...
   ```

---

## 🚀 Next Steps

1. **Refactor existing auth module** to use new architecture
2. **Test** that everything still works
3. **Apply pattern** to new modules (tutors, students)
4. **Document** any deviations or special cases

---

**Remember:** Good architecture is about **separation of concerns**. Each layer should do ONE thing well! 🎯

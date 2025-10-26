# 📝 Naming Conventions & Terminology

## ❓ Tại sao folder tên `api/` thay vì `routes/` hay `controllers/`?

### ✅ **Câu trả lời: `api/` là chuẩn FastAPI và REST API design**

---

## 🎯 **So sánh các tên phổ biến:**

| Framework | Tên folder | Giải thích |
|-----------|-----------|-----------|
| **FastAPI** | `api/` | ✅ **Chuẩn** - Đại diện cho API endpoints |
| **Django** | `views/` | Django gọi là "views" |
| **Flask** | `routes/` hoặc `blueprints/` | Flask linh hoạt hơn |
| **Spring Boot** | `controllers/` | Java gọi là "controllers" |
| **Express.js** | `routes/` | Node.js thường dùng "routes" |
| **ASP.NET** | `Controllers/` | C# dùng MVC pattern |

---

## 📚 **Lý do chọn `api/`:**

### **1. Phù hợp với REST API design**
```
app/
├── api/          ← Các HTTP endpoints (REST API)
│   ├── auth.py   → /api/v1/auth/*
│   ├── students.py → /api/v1/students/*
│   └── tutors.py → /api/v1/tutors/*
```

**URL mapping:**
```
api/students.py  →  /api/v1/students/
api/tutors.py    →  /api/v1/tutors/
api/auth.py      →  /api/v1/auth/
```

---

### **2. Phân biệt rõ với các layer khác**
```
app/
├── api/          ← HTTP/REST API endpoints (giao tiếp với client)
├── services/     ← Business logic (không biết về HTTP)
├── repositories/ ← Database operations (không biết về HTTP)
└── models/       ← Database models
```

- **`api/`** = "Cổng vào" của HTTP requests
- **`services/`** = Xử lý logic nghiệp vụ
- **`repositories/`** = Giao tiếp với database

---

### **3. Terminology chuẩn trong FastAPI**
```python
# FastAPI documentation gọi là "API Routes"
from fastapi import APIRouter

router = APIRouter()  # ← API Router, không phải Controller

@router.get("/users")  # ← API endpoint
async def get_users():
    pass
```

---

### **4. Khác với MVC Controller**

#### **Spring Boot Controller (Java):**
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping
    public List<User> getUsers() {
        return userService.findAll();
    }
}
```
- Controller = Class với nhiều methods
- Chứa cả routing logic

#### **FastAPI Routes (Python):**
```python
# api/users.py
router = APIRouter()

@router.get("/")
async def get_users(
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_all_users()
```
- Routes = Module với functions
- Routing được định nghĩa bởi decorators
- **KHÔNG phải Controller class** → Nên gọi là `api/` hơn

---

## 🔄 **Alternative names và khi nào dùng:**

### ✅ **`api/` - Recommended (Đang dùng)**
```
app/api/auth.py      → REST API endpoints
app/api/students.py  → HTTP routes
app/api/tutors.py    → API handlers
```
**Dùng khi:**
- Build REST API
- Tên URL có prefix `/api/v1/...`
- Following FastAPI best practices

---

### ⚠️ **`routes/` - Alternative (có thể dùng)**
```
app/routes/auth.py
app/routes/students.py
```
**Dùng khi:**
- Muốn nhấn mạnh "routing" logic
- Dùng trong Flask/Express.js
- Không có GraphQL/gRPC endpoints khác

---

### ❌ **`controllers/` - Không khuyến khích**
```
app/controllers/user_controller.py
app/controllers/auth_controller.py
```
**Tại sao không dùng:**
- FastAPI không theo pattern MVC Controller
- Controllers thường là classes, FastAPI dùng functions
- Gây nhầm lẫn với Spring/ASP.NET

---

### ❌ **`views/` - Sai context**
```
app/views/  ← Dành cho templates, không phải API
```
**Tại sao không dùng:**
- "Views" trong Django/Flask = HTML templates
- REST API trả JSON, không phải HTML views

---

## 📋 **Tóm tắt:**

| Tên | Ý nghĩa | Phù hợp với FastAPI |
|-----|---------|---------------------|
| **`api/`** | API endpoints, HTTP handlers | ✅ **Chuẩn nhất** |
| `routes/` | Routing logic | ⚠️ Được (nhưng kém rõ ràng) |
| `controllers/` | MVC controllers (classes) | ❌ Không (FastAPI không phải MVC) |
| `views/` | HTML templates/views | ❌ Sai (API không có views) |
| `endpoints/` | API endpoints | ⚠️ Dài dòng, ít dùng |
| `handlers/` | Request handlers | ⚠️ Ít phổ biến |

---

## 🎯 **Kết luận:**

### **Giữ nguyên `api/` vì:**
1. ✅ Chuẩn FastAPI convention
2. ✅ Phản ánh đúng mục đích: REST API endpoints
3. ✅ Mapping rõ với URL structure: `/api/v1/...`
4. ✅ Phân biệt rõ với GraphQL/gRPC/WebSocket endpoints (nếu có)
5. ✅ Đọc code dễ hiểu: "Đây là API layer"

### **Không đổi thành:**
- ❌ `controllers/` - Không phù hợp với FastAPI functional pattern
- ❌ `views/` - Sai nghĩa (views = templates)
- ❌ `routes/` - Ít rõ ràng hơn `api/`

---

## 📚 **References:**

- [FastAPI Official Docs - Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [REST API Naming Conventions](https://restfulapi.net/resource-naming/)

---

**🎯 Verdict: `api/` là tên chuẩn và phù hợp nhất cho FastAPI project!**

# 🧪 Test Multi-Student Session Feature

## Setup Test Data

### 1. Đăng nhập (Get Access Token)

**Endpoint:** `POST /api/v1/auth/login`

```json
{
  "username": "tutor_user",
  "password": "your_password"
}
```

📋 Copy `access_token` từ response

### 2. Authorize trong Swagger

- Click nút **🔓 Authorize** ở góc trên bên phải
- Nhập: `Bearer YOUR_ACCESS_TOKEN` (có chữ "Bearer " phía trước)
- Click **Authorize** → **Close**

---

## Test Scenarios

### ✅ Scenario 1: Xem danh sách sessions của tutor (EMPTY)

**Endpoint:** `GET /api/v1/tutors/sessions`

**Parameters:**

- status: (empty - lấy tất cả)
- skip: 0
- limit: 10

**Expected Response:**

```json
{
  "total": 0,
  "sessions": [],
  "skip": 0,
  "limit": 10
}
```

---

### ✅ Scenario 2: Tạo session mới với NHIỀU students

**Endpoint:** `POST /api/v1/sessions/` (cần implement create)

**Request Body:**

```json
{
  "title": "Toán cao cấp - Nhóm 3 sinh viên",
  "description": "Ôn tập giữa kỳ",
  "subject_id": 1,
  "tutor_id": 1,
  "student_ids": [1, 2, 3],
  "scheduled_date": "2025-11-25",
  "start_time": "14:00:00",
  "end_time": "16:00:00",
  "duration": 2,
  "location_type": "online",
  "meeting_link": "https://zoom.us/j/123456",
  "max_students": 5
}
```

**Expected Response:**

```json
{
  "session_id": 1,
  "title": "Toán cao cấp - Nhóm 3 sinh viên",
  "tutor": {
    "user_id": 1,
    "tutor_id": 1,
    "email": "tutor@hcmut.edu.vn",
    "full_name": "Nguyễn Văn Tutor",
    "specialization": "Toán"
  },
  "students": [
    {
      "user_id": 2,
      "student_id": 1,
      "email": "student1@hcmut.edu.vn",
      "full_name": "Trần Thị Student 1",
      "status": "confirmed"
    },
    {
      "user_id": 3,
      "student_id": 2,
      "email": "student2@hcmut.edu.vn",
      "full_name": "Lê Văn Student 2",
      "status": "confirmed"
    },
    {
      "user_id": 4,
      "student_id": 3,
      "email": "student3@hcmut.edu.vn",
      "full_name": "Phạm Thị Student 3",
      "status": "confirmed"
    }
  ],
  "status": "draft",
  "max_students": 5
}
```

---

### ✅ Scenario 3: Xem lại sessions với filter

**Endpoint:** `GET /api/v1/tutors/sessions`

**Parameters:**

- status: `draft`
- skip: 0
- limit: 10

**Expected:**

- `total`: 1
- `sessions[0].students.length`: 3 (có 3 students)

---

### ✅ Scenario 4: Thêm student vào session (UPDATE)

**Endpoint:** `PUT /api/v1/sessions/{session_id}/participants` (cần implement)

**Request Body:**

```json
{
  "user_id": 5,
  "role": "student",
  "status": "pending"
}
```

**Expected:**

- Session giờ có 4 students
- Student mới có status = "pending"

---

### ✅ Scenario 5: Remove student khỏi session

**Endpoint:** `DELETE /api/v1/sessions/{session_id}/participants/{user_id}` (cần implement)

**Expected:**

- Session còn 3 students
- Student bị remove không xuất hiện trong `students` array

---

## Verify Database

Sau khi test, check database:

```sql
-- Xem sessions
SELECT * FROM tutor_system.session;

-- Xem participants
SELECT
    sp.participant_id,
    sp.session_id,
    sp.user_id,
    sp.role,
    sp.status,
    u.full_name,
    u.email
FROM tutor_system."SessionParticipant" sp
JOIN tutor_system."User" u ON sp.user_id = u.user_id
ORDER BY sp.session_id, sp.role DESC;
```

**Expected:**

- Mỗi session có 1 tutor + N students trong SessionParticipant
- `session.student_id` = NULL (deprecated field)

---

## Common Issues & Solutions

### ❌ Issue: "Tutor profile not found"

**Solution:** Tạo tutor profile trước:

```http
POST /api/v1/tutors/register
{
  "specialization": "Toán, Vật lý",
  "bio": "5 năm kinh nghiệm",
  "hourly_rate": 150000,
  "experience_years": 5
}
```

### ❌ Issue: "Invalid subject_id"

**Solution:** Tạo subject trước hoặc dùng subject_id có sẵn

### ❌ Issue: "Invalid student_ids"

**Solution:** Đảm bảo students đã register trong hệ thống

---

## 🎯 Success Criteria

✅ Tạo được session với 3+ students  
✅ GET /tutors/sessions trả về danh sách students đầy đủ  
✅ Mỗi student có đầy đủ info: user_id, student_id, email, full_name, status  
✅ Filter by status hoạt động  
✅ Pagination hoạt động  
✅ Database có data trong SessionParticipant table

---

## Next Steps (TODO)

1. ⚠️ **Implement POST /sessions/** - Tạo session với student_ids array
2. ⚠️ **Implement POST /sessions/{id}/participants** - Thêm student
3. ⚠️ **Implement DELETE /sessions/{id}/participants/{user_id}** - Remove student
4. ✅ **GET /tutors/sessions** - DONE (đã implement)

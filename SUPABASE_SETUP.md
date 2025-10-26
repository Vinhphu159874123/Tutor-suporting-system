# 🚀 Setup Supabase cho HCMUT Tutor System

## Bước 1: Khởi tạo Database Schema trên Supabase

1. Truy cập Supabase Dashboard: https://supabase.com/dashboard
2. Chọn project của bạn: `yamlyzztxozrxbeepzyu`
3. Vào **SQL Editor** (icon ở sidebar bên trái)
4. Copy toàn bộ nội dung file `backend/sql/init.sql`
5. Paste vào SQL Editor
6. Click **Run** để execute

✅ Script sẽ tạo:
- Tất cả các bảng (users, tutors, students, sessions, etc.)
- Indexes để tối ưu performance
- Sample data (admin, students, tutors, subjects)

## Bước 2: Lấy Database Password

1. Trong Supabase Dashboard, vào **Settings** → **Database**
2. Scroll xuống phần **Connection string**
3. Click **Copy** connection string
4. Hoặc copy password từ phần **Database password**

## Bước 3: Cập nhật file .env

File `backend/.env` đã được tạo. Bạn chỉ cần:
1. Thay `[YOUR-DATABASE-PASSWORD]` trong `DATABASE_URL` bằng password thực tế
2. Hoặc copy toàn bộ connection string từ Supabase

**Connection string format:**
```
postgresql://postgres.[project-ref]:[password]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

Ví dụ cho project của bạn:
```
DATABASE_URL=postgresql://postgres.yamlyzztxozrxbeepzyu:YOUR_ACTUAL_PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

## Bước 4: Test kết nối

```bash
cd backend
pip install -r requirements.txt
python run_dev.py
```

Truy cập: http://localhost:8000/docs

## 📊 Sample Data đã tạo

### Users:
- **Admin**: admin@hcmut.edu.vn (password: password123)
- **Student 1**: student1@hcmut.edu.vn
- **Student 2**: student2@hcmut.edu.vn  
- **Tutor 1**: tutor1@hcmut.edu.vn
- **Tutor 2**: tutor2@hcmut.edu.vn

### Subjects:
- MT1003: Toán cao cấp A1
- MT1005: Toán cao cấp A3
- PH1003: Vật lý đại cương A1
- CO1007: Cấu trúc dữ liệu và Giải thuật
- CO2013: Hệ quản trị cơ sở dữ liệu

### Sessions:
- 2 sample sessions đã được tạo sẵn

## 🔍 Kiểm tra Database

Sau khi chạy init.sql, vào **Table Editor** trong Supabase để xem:
- ✅ 12 tables đã được tạo
- ✅ Sample data đã có trong các bảng
- ✅ Relationships (foreign keys) đã được setup

## ⚡ Quick Test

```bash
# Test API health
curl http://localhost:8000/health

# Test API docs
# Mở browser: http://localhost:8000/docs

# Test login endpoint
# Sử dụng Swagger UI tại /docs để test login
```

## 🐛 Troubleshooting

### Lỗi: Connection refused
- Kiểm tra DATABASE_URL có đúng không
- Kiểm tra password có đúng không
- Kiểm tra network/firewall

### Lỗi: Table already exists
- Đã chạy init.sql rồi, không cần chạy lại
- Nếu muốn reset: DROP các bảng trước khi chạy lại

### Lỗi: pip install
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

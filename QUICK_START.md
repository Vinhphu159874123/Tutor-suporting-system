# Quick Start Guide - Test Without Docker

## Để test backend NHANH (Không cần Supabase, không cần Docker):

### 1. Cài đặt dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Chạy backend
```bash
python run_dev.py
```

Hoặc:
```bash
uvicorn app.main:app --reload
```

### 3. Truy cập
- API Docs: http://localhost:8000/docs
- Test API: http://localhost:8000/health

## Database
- Đang dùng SQLite (file `tutor_system.db` sẽ tự tạo)
- Không cần cài đặt PostgreSQL hay Supabase
- Để chuyển sang PostgreSQL/Supabase sau, chỉnh file `backend/app/core/config.py`

## Test accounts (khi login hoạt động)
- student@hcmut.edu.vn / password123
- tutor@hcmut.edu.vn / password123
- admin@hcmut.edu.vn / password123

## Nếu gặp lỗi
1. Kiểm tra Python version: `python --version` (cần >= 3.11)
2. Upgrade pip: `python -m pip install --upgrade pip`
3. Cài lại dependencies: `pip install -r requirements.txt`
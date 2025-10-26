# HCMUT Tutor Support System

## 📋 Mô tả dự án
Hệ thống hỗ trợ Tutor cho Trường Đại học Bách Khoa TP.HCM (HCMUT) nhằm quản lý chương trình dạy kèm, kết nối sinh viên-tutor, lên lịch và hỗ trợ học tập.

## 🏗️ Kiến trúc hệ thống
- **Backend**: Python FastAPI
- **Frontend**: React TypeScript 
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Mock HCMUT_SSO integration
- **External Services**: Mock HCMUT_DATACORE, HCMUT_LIBRARY, AI_RECOMMENDER
- **Containerization**: Docker & Docker Compose
- **AI Features**: Intelligent tutor-student matching

## 🚀 Cài đặt và chạy dự án

### Yêu cầu hệ thống
- **Docker & Docker Compose** (Khuyến nghị)
- **Node.js 18+** (cho development)
- **Python 3.11+** (cho development)

### 0. Cài đặt Docker (Nếu chưa có)

#### Windows:
1. Tải Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Cài đặt và khởi động Docker Desktop
3. Kiểm tra: `docker --version` và `docker-compose --version`

#### macOS:
```bash
# Sử dụng Homebrew
brew install --cask docker

# Hoặc tải từ website Docker
```

#### Linux (Ubuntu):
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

### 1. Clone project và cài đặt

```bash
git clone <repository-url>
cd "Tutor support system"
```

### 2. Chạy với Docker Compose (Khuyến nghị)

```bash
# Khởi động toàn bộ hệ thống
docker-compose up -d

# Hoặc xem logs
docker-compose up
```

Hệ thống sẽ chạy tại:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 3. Chạy development mode (Manual)

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### Mock Services
```bash
# HCMUT SSO
cd backend/mock_services/sso
pip install -r requirements.txt
python main.py
```

### 4. Environment Variables

Tạo file `.env` trong thư mục `backend/`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/tutor_system
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
HCMUT_SSO_URL=http://localhost:3001
HCMUT_DATACORE_URL=http://localhost:3002
HCMUT_LIBRARY_URL=http://localhost:3003
AI_RECOMMENDER_URL=http://localhost:3004
REDIS_URL=redis://localhost:6379
```

## 👥 Tài khoản demo

Để test hệ thống, sử dụng các tài khoản sau:

| Role | Email | Password |
|------|-------|----------|
| Student | student@hcmut.edu.vn | password123 |
| Tutor | tutor@hcmut.edu.vn | password123 |
| Admin | admin@hcmut.edu.vn | password123 |

## 📚 Các tính năng chính

### 1. Account Management (Quản lý tài khoản)
- Đăng nhập/Đăng xuất
- Quản lý profile người dùng
- Tích hợp HCMUT_SSO

### 2. Registration Module (Module đăng ký)
- Đăng ký làm Student/Tutor
- Phê duyệt đăng ký
- Quản lý môn học

### 3. Scheduling Module (Module lên lịch)
- Tạo phiên học
- Quản lý thời gian biểu
- Xác nhận/Hủy lịch học

### 4. Session Management (Quản lý phiên học)
- Tiến hành phiên học
- Upload tài liệu
- Feedback và đánh giá

### 5. Report Module (Module báo cáo)
- Báo cáo khóa học
- Báo cáo học tập
- Theo dõi hoạt động

### 6. Administrator Configuration (Cấu hình admin)
- Quản lý người dùng
- Phân quyền
- Cấu hình hệ thống

### 7. Learning Forum (Diễn đàn học tập)
- Tạo forum thảo luận
- Nhóm học tập
- Chia sẻ kiến thức

### 8. AI-powered Matching (Kết nối thông minh)
- Thuật toán gợi ý tutor phù hợp
- Phân tích học tập
- Tối ưu lịch học

## 🛠️ Cấu trúc dự án

```
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── core/            # Core configurations
│   │   ├── models/          # Database models
│   │   └── services/        # Business logic
│   ├── mock_services/       # Mock external services
│   │   ├── sso/            # Mock HCMUT_SSO
│   │   ├── datacore/       # Mock HCMUT_DATACORE
│   │   ├── library/        # Mock HCMUT_LIBRARY
│   │   └── ai_recommender/ # Mock AI_RECOMMENDER
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── stores/         # State management
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml       # Docker orchestration
└── README.md
```

## 🔧 Development

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Database
- **PostgreSQL**: localhost:5432
- **Database Name**: tutor_system
- **Username**: postgres
- **Password**: password

### Commands

```bash
# Xem logs của containers
docker-compose logs -f

# Restart một service
docker-compose restart backend

# Rebuild containers
docker-compose up --build

# Dọn dẹp containers
docker-compose down -v

# Chạy tests (khi có)
cd backend && python -m pytest
cd frontend && npm test
```

## 🤝 Contributing

1. Fork project
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👨‍💻 Authors

- **Team HCMUT** - *Initial work*

## 🆘 Support

Nếu bạn gặp vấn đề gì, vui lòng tạo issue trên GitHub hoặc liên hệ team development.

---

**Happy Coding! 🎉**

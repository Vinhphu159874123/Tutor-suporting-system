# 🎓 HCMUT Tutor Support System# 🎓 HCMUT Tutor Support System



> A comprehensive platform for managing tutoring programs, connecting students with tutors, scheduling sessions, and supporting academic learning at Ho Chi Minh City University of Technology (HCMUT).> A comprehensive platform for managing tutoring programs, connecting students with tutors, scheduling sessions, and supporting academic learning at Ho Chi Minh City University of Technology (HCMUT).



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org/)[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org/)

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)



------



## 📋 Table of Contents## 📋 Table of Contents



- [Overview](#-overview)- [Overview](#-overview)

- [System Architecture](#-system-architecture)- [System Architecture](#-system-architecture)

- [Features](#-features)- [Features](#-features)

- [Quick Start](#-quick-start)- [Quick Start](#-quick-start)

- [Environment Setup](#-environment-setup)- [Environment Setup](#-environment-setup)

- [Project Structure](#-project-structure)- [Project Structure](#-project-structure)

- [API Documentation](#-api-documentation)- [API Documentation](#-api-documentation)

- [Development](#-development)- [Development](#-development)

- [Contributing](#-contributing)- [Contributing](#-contributing)



------



## 🌟 Overview## 🌟 Overview



The HCMUT Tutor Support System is a modern, full-stack web application designed to streamline tutoring services at HCMUT. It provides:The HCMUT Tutor Support System is a modern, full-stack web application designed to streamline tutoring services at HCMUT. It provides:



- **Student-Tutor Matching**: AI-powered recommendation system- **Student-Tutor Matching**: AI-powered recommendation system

- **Session Management**: Comprehensive scheduling and tracking- **Session Management**: Comprehensive scheduling and tracking

- **Learning Analytics**: Progress tracking and performance reports- **Learning Analytics**: Progress tracking and performance reports

- **Community Features**: Forums and study groups- **Community Features**: Forums and study groups

- **External Integration**: HCMUT SSO, DataCore, and Library services- **External Integration**: HCMUT SSO, DataCore, and Library services



------



## 🏗️ System Architecture## 🏗️ System Architecture



### Tech Stack### Tech Stack



**Backend:****Backend:**

- **Framework**: FastAPI (Python 3.11+)- **Framework**: FastAPI (Python 3.11+)

- **Database**: PostgreSQL 14+ (Supabase)- **Database**: PostgreSQL 14+ (Supabase)

- **Cache**: Redis- **Cache**: Redis

- **Authentication**: JWT + HCMUT SSO Integration- **Authentication**: JWT + HCMUT SSO Integration



**Frontend:****Frontend:**

- **Framework**: React 18.2+ with TypeScript- **Framework**: React 18.2+ with TypeScript

- **Styling**: Tailwind CSS- **Styling**: Tailwind CSS

- **State Management**: React Context API- **State Management**: React Context API

- **HTTP Client**: Axios- **HTTP Client**: Axios



**DevOps:****DevOps:**

- **Containerization**: Docker & Docker Compose- **Containerization**: Docker & Docker Compose

- **CI/CD**: GitHub Actions (planned)- **CI/CD**: GitHub Actions (planned)



**Mock Services:****Mock Services:**

- **HCMUT SSO** (Port 3001): Authentication service- **HCMUT SSO** (Port 3001): Authentication service

- **HCMUT DataCore** (Port 3002): Student/course data- **HCMUT DataCore** (Port 3002): Student/course data

- **HCMUT Library** (Port 3003): Library resources- **HCMUT Library** (Port 3003): Library resources



------



## ✨ Features## ✨ Features



### 🔐 Authentication & Authorization### 🔐 Authentication & Authorization

- [x] HCMUT SSO integration- [x] HCMUT SSO integration

- [x] JWT-based authentication- [x] JWT-based authentication

- [x] Role-based access control (Student/Tutor/Coordinator/Admin)- [x] Role-based access control (Student/Tutor/Coordinator/Admin)

- [x] Profile management- [x] Profile management



### 📝 Registration System### 📝 Registration System

- [x] Student registration with subject preferences- [x] Student registration with subject preferences

- [x] Tutor registration with qualifications- [x] Tutor registration with qualifications

- [x] Coordinator approval workflow- [x] Coordinator approval workflow

- [x] Registration status tracking- [x] Registration status tracking



### 📅 Scheduling & Sessions### 📅 Scheduling & Sessions

- [x] Create and manage tutoring sessions- [x] Create and manage tutoring sessions

- [x] Multiple location types (Online/Offline/Hybrid)- [x] Multiple location types (Online/Offline/Hybrid)

- [x] Session status tracking (Draft → Confirmed → Ongoing → Completed)- [x] Session status tracking (Draft → Confirmed → Ongoing → Completed)

- [x] Attendance management- [x] Attendance management

- [x] Session materials upload/download- [x] Session materials upload/download



### 📊 Reports & Analytics### 📊 Reports & Analytics

- [x] Student progress tracking- [x] Student progress tracking

- [x] Tutor performance reports- [x] Tutor performance reports

- [x] Course analytics- [x] Course analytics

- [x] Learning achievements (Gamification)- [x] Learning achievements (Gamification)



### 💬 Community Features### 💬 Community Features

- [x] Discussion forums- [x] Discussion forums

- [x] Study groups- [x] Study groups

- [x] Q&A threads- [x] Q&A threads

- [x] Resource sharing- [x] Resource sharing



### 🤖 AI Features

- [ ] Intelligent tutor-student matching

- [ ] Learning path recommendations### 🤖 AI Features```env

- [ ] Schedule optimization

- [ ] Intelligent tutor-student matchingDATABASE_URL=postgresql://postgres:password@localhost:5432/tutor_system

---

- [ ] Learning path recommendationsSUPABASE_URL=your_supabase_url

## 🚀 Quick Start

- [ ] Schedule optimizationSUPABASE_ANON_KEY=your_supabase_anon_key

### Prerequisites

JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

- **Docker** & **Docker Compose** (Recommended)

- **Node.js** 18+ (for local development)---HCMUT_SSO_URL=http://localhost:3001

- **Python** 3.11+ (for local development)

- **Git**HCMUT_DATACORE_URL=http://localhost:3002



### Installation## 🚀 Quick StartHCMUT_LIBRARY_URL=http://localhost:3003



1. **Clone the repository**AI_RECOMMENDER_URL=http://localhost:3004

   ```bash

   git clone https://github.com/Vinhphu159874123/Tutor-suporting-system.git### PrerequisitesREDIS_URL=redis://localhost:6379

   cd Tutor-suporting-system

   ```````



2. **Run with Docker Compose (Recommended)**- **Docker** & **Docker Compose** (Recommended)

   ```bash

   # Start all services- **Node.js** 18+ (for local development)## 👥 Tài khoản demo

   docker-compose up -d

- **Python** 3.11+ (for local development)

   # View logs

   docker-compose logs -f- **Git**Để test hệ thống, sử dụng các tài khoản sau:

   ```

### Installation| Role | Email | Password |

   ```bash

   # Stop all services|------|-------|----------|

   docker-compose down

   ```1. **Clone the repository**| Student | student@hcmut.edu.vn | password123 |



3. **Access the application**   ````bash| Tutor | tutor@hcmut.edu.vn | password123 |

   - **Frontend**: http://localhost:3000

   - **Backend API**: http://localhost:8000   git clone https://github.com/Vinhphu159874123/Tutor-suporting-system.git| Admin | admin@hcmut.edu.vn | password123 |

   - **API Docs**: http://localhost:8000/docs

   - **Supabase Studio** (if using local): http://localhost:54323   cd Tutor-suporting-system



### Default Demo Accounts   ```## 📚 Các tính năng chính



| Role | Email | Password |   ````

|------|-------|----------|

| Admin | admin@hcmut.edu.vn | admin123 |2. **Run with Docker Compose (Recommended)**### 1. Account Management (Quản lý tài khoản)

| Coordinator (CS) | coordinator.cs@hcmut.edu.vn | coordinator123 |

| Tutor | tutor.hoa@hcmut.edu.vn | tutor123 |   ```bash- Đăng nhập/Đăng xuất

| Student | 2312345@hcmut.edu.vn | student123 |

   # Start all services- Quản lý profile người dùng

---

   docker-compose up -d- Tích hợp HCMUT_SSO

## 🔧 Environment Setup



### Backend Configuration

   # View logs### 2. Registration Module (Module đăng ký)

Create `.env` file in `backend/` directory:

   docker-compose logs -f- Đăng ký làm Student/Tutor

```bash   ```

# Database

DATABASE_URL=postgresql://postgres:password@db:5432/tutor_system- Phê duyệt đăng ký



# Supabase (Optional - if using Supabase)  # Stop all services- Quản lý môn học

SUPABASE_URL=https://your-project.supabase.co

SUPABASE_ANON_KEY=your_anon_key_here  docker-compose down

SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

  ```### 3. Scheduling Module (Module lên lịch)

# JWT

JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production  ```

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30- Tạo phiên học



# External Services (Mock)3. **Access the application**- Quản lý thời gian biểu

HCMUT_SSO_URL=http://mock-sso:3001

HCMUT_DATACORE_URL=http://mock-datacore:3002   - **Frontend**: http://localhost:3000- Xác nhận/Hủy lịch học

HCMUT_LIBRARY_URL=http://mock-library:3003

   - **Backend API**: http://localhost:8000

# Redis

REDIS_URL=redis://redis:6379   - **API Docs**: http://localhost:8000/docs### 4. Session Management (Quản lý phiên học)



# Security   - **Supabase Studio** (if using local): http://localhost:54323- Tiến hành phiên học

BCRYPT_ROUNDS=12

```- Upload tài liệu



### Frontend Configuration### Default Demo Accounts- Feedback và đánh giá



Create `.env` file in `frontend/` directory:| Role | Email | Password |### 5. Report Module (Module báo cáo)



```bash|------|-------|----------|- Báo cáo khóa học

REACT_APP_API_URL=http://localhost:8000

REACT_APP_SUPABASE_URL=https://your-project.supabase.co| Admin | admin@hcmut.edu.vn | admin123 |- Báo cáo học tập

REACT_APP_SUPABASE_ANON_KEY=your_anon_key_here

```| Coordinator (CS) | coordinator.cs@hcmut.edu.vn | coordinator123 |- Theo dõi hoạt động



### Database Setup| Tutor | tutor.hoa@hcmut.edu.vn | tutor123 |



1. **Using Supabase (Recommended)**| Student | 2312345@hcmut.edu.vn | student123 |### 6. Administrator Configuration (Cấu hình admin)

   - Create a project at [supabase.com](https://supabase.com)

   - Run migration scripts:- Quản lý người dùng

     ```bash

     # Copy SQL from backend/sql/add_missing_tables.sql---- Phân quyền

     # Run in Supabase SQL Editor

     ```- Cấu hình hệ thống



2. **Using Local PostgreSQL**## 🔧 Environment Setup

   ```bash

   # Docker Compose includes PostgreSQL### 7. Learning Forum (Diễn đàn học tập)

   docker-compose up db -d

### Backend Configuration- Tạo forum thảo luận

   # Access psql

   docker exec -it tutor-db psql -U postgres -d tutor_system- Nhóm học tập

   ```

Create `.env` file in `backend/` directory:- Chia sẻ kiến thức

---

````bash### 8. AI-powered Matching (Kết nối thông minh)

## 📁 Project Structure

# Database- Thuật toán gợi ý tutor phù hợp

```

Tutor-suporting-system/DATABASE_URL=postgresql://postgres:password@db:5432/tutor_system- Phân tích học tập

├── backend/

│   ├── app/- Tối ưu lịch học

│   │   ├── api/              # API endpoints (auth, users, sessions, etc.)

│   │   ├── core/             # Configuration, database, dependencies# Supabase (Optional - if using Supabase)

│   │   ├── events/           # Event system (notifications, listeners)

│   │   ├── models/           # SQLAlchemy ORM modelsSUPABASE_URL=https://your-project.supabase.co## 🛠️ Cấu trúc dự án

│   │   ├── repositories/     # Data access layer

│   │   ├── schemas/          # Pydantic schemas (DTOs)SUPABASE_ANON_KEY=your_anon_key_here

│   │   └── services/         # Business logic layer

│   ├── mock_services/SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here```

│   │   ├── sso/             # Mock HCMUT SSO (Python/FastAPI)

│   │   ├── datacore/        # Mock DataCore (Node.js/Express)├── backend/                  # FastAPI Python backend

│   │   └── library/         # Mock Library (Node.js/Express)

│   ├── sql/                 # Database migrations & test data# JWT│   ├── app/

│   ├── docs/                # Backend documentation

│   ├── requirements.txt     # Python dependenciesJWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production│   │   ├── api/             # API routes

│   └── Dockerfile

├── frontend/JWT_ALGORITHM=HS256│   │   ├── core/            # Core configurations

│   ├── src/

│   │   ├── components/      # Reusable React componentsACCESS_TOKEN_EXPIRE_MINUTES=30│   │   ├── models/          # Database models

│   │   ├── pages/           # Page components (admin, auth, session, etc.)

│   │   ├── services/        # API service layer (Axios)│   │   └── services/        # Business logic

│   │   └── stores/          # State management (Context API)

│   ├── public/# External Services (Mock)│   ├── mock_services/       # Mock external services

│   ├── package.json

│   └── DockerfileHCMUT_SSO_URL=http://mock-sso:3001│   │   ├── sso/            # Mock HCMUT_SSO

├── docker-compose.yml       # Docker orchestration

├── README.mdHCMUT_DATACORE_URL=http://mock-datacore:3002│   │   ├── datacore/       # Mock HCMUT_DATACORE

└── .gitignore

```HCMUT_LIBRARY_URL=http://mock-library:3003│   │   ├── library/        # Mock HCMUT_LIBRARY



---│   │   └── ai_recommender/ # Mock AI_RECOMMENDER



## 📚 API Documentation# Redis│   ├── requirements.txt



### Interactive API DocsREDIS_URL=redis://redis:6379│   └── Dockerfile



- **Swagger UI**: http://localhost:8000/docs├── frontend/                # React TypeScript frontend

- **ReDoc**: http://localhost:8000/redoc

# Security│   ├── src/

### Main Endpoints

BCRYPT_ROUNDS=12│   │   ├── components/     # Reusable components

#### Authentication

- `POST /auth/login` - User login```│   │   ├── pages/          # Page components

- `POST /auth/register` - User registration

- `POST /auth/logout` - User logout│   │   ├── services/       # API services

- `GET /auth/profile` - Get current user profile

### Frontend Configuration│   │   └── stores/         # State management

#### Students

- `GET /students` - List students│   ├── package.json

- `POST /students/register` - Register as student

- `GET /students/{id}/sessions` - Get student sessionsCreate `.env` file in `frontend/` directory:│   └── Dockerfile



#### Tutors├── docker-compose.yml       # Docker orchestration

- `GET /tutors` - List tutors (with filters)

- `POST /tutors/register` - Register as tutor```bash└── README.md

- `GET /tutors/{id}/reviews` - Get tutor reviews

REACT_APP_API_URL=http://localhost:8000```

#### Sessions

- `POST /sessions` - Create sessionREACT_APP_SUPABASE_URL=https://your-project.supabase.co

- `GET /sessions/{id}` - Get session details

- `PUT /sessions/{id}` - Update sessionREACT_APP_SUPABASE_ANON_KEY=your_anon_key_here## 🔧 Development

- `POST /sessions/{id}/materials` - Upload materials

````

#### Forums

- `GET /forum/posts` - List forum posts### API Documentation

- `POST /forum/posts` - Create new post

- `POST /forum/posts/{id}/comments` - Add comment### Database Setup- **Swagger UI**: http://localhost:8000/docs



For complete API reference, visit `/docs` after starting the backend.- **ReDoc**: http://localhost:8000/redoc



---1. **Using Supabase (Recommended)**



## 💻 Development   - Create a project at [supabase.com](https://supabase.com)### Database



### Running Locally (Without Docker)   - Run migration scripts:- **PostgreSQL**: localhost:5432



#### Backend     ```bash- **Database Name**: tutor_system



```bash     # Copy SQL from backend/sql/add_missing_tables.sql- **Username**: postgres

cd backend

     # Run in Supabase SQL Editor- **Password**: password

# Create virtual environment

python -m venv venv     ```

source venv/bin/activate  # On Windows: venv\Scripts\activate

### Commands

# Install dependencies

pip install -r requirements.txt2. **Using Local PostgreSQL**



# Run FastAPI server   `bash`bash

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```   # Docker Compose includes PostgreSQL# Xem logs của containers



#### Frontend   docker-compose up db -ddocker-compose logs -f



```bash   # Access psql# Restart một service

cd frontend

   docker exec -it tutor-db psql -U postgres -d tutor_systemdocker-compose restart backend

# Install dependencies

npm install   ```



# Start development server   ```

npm start

```# Rebuild containers



#### Mock Services---docker-compose up --build



**SSO (Python):**## 📁 Project Structure# Dọn dẹp containers

```bash

cd backend/mock_services/ssodocker-compose down -v

pip install -r requirements.txt

python main.py  # Runs on port 3001````

```

Tutor-suporting-system/# Chạy tests (khi có)

**DataCore (Node.js):**

```bash├── backend/cd backend && python -m pytest

cd backend/mock_services/datacore

npm install│   ├── app/cd frontend && npm test

npm start  # Runs on port 3002

```│   │   ├── api/              # API endpoints (auth, users, sessions, etc.)```



**Library (Node.js):**│   │   ├── core/             # Configuration, database, dependencies

```bash

cd backend/mock_services/library│   │   ├── events/           # Event system (notifications, listeners)## 🤝 Contributing

npm install

npm start  # Runs on port 3003│   │   ├── models/           # SQLAlchemy ORM models

```

│   │   ├── repositories/     # Data access layer1. Fork project

### Useful Commands

│   │   ├── schemas/          # Pydantic schemas (DTOs)2. Tạo feature branch (`git checkout -b feature/amazing-feature`)

```bash

# Docker Compose│   │   └── services/         # Business logic layer3. Commit changes (`git commit -m 'Add amazing feature'`)

docker-compose up --build        # Rebuild and start

docker-compose down -v           # Stop and remove volumes│   ├── mock_services/4. Push to branch (`git push origin feature/amazing-feature`)

docker-compose logs -f backend   # View backend logs

docker-compose restart frontend  # Restart frontend only│   │   ├── sso/             # Mock HCMUT SSO (Python/FastAPI)5. Tạo Pull Request



# Database│   │   ├── datacore/        # Mock DataCore (Node.js/Express)

docker exec -it tutor-db psql -U postgres -d tutor_system

│   │   └── library/         # Mock Library (Node.js/Express)## 📄 License

# Backend tests

cd backend && python -m pytest│   ├── sql/                 # Database migrations & test data



# Frontend tests│   ├── docs/                # Backend documentationDistributed under the MIT License. See `LICENSE` for more information.

cd frontend && npm test

│   ├── requirements.txt     # Python dependencies

# Code formatting

cd backend && black .│   └── Dockerfile## 👨‍💻 Authors

cd frontend && npm run format

```├── frontend/



---│   ├── src/- **Team HCMUT** - *Initial work*



## 🤝 Contributing│   │   ├── components/      # Reusable React components



We welcome contributions! Please follow these steps:│   │   ├── pages/           # Page components (admin, auth, session, etc.)## 🆘 Support



1. **Fork** the repository│   │   ├── services/        # API service layer (Axios)

2. **Create** a feature branch

   ```bash│   │   └── stores/          # State management (Context API)Nếu bạn gặp vấn đề gì, vui lòng tạo issue trên GitHub hoặc liên hệ team development.

   git checkout -b feature/amazing-feature

   ```│   ├── public/

3. **Commit** your changes

   ```bash│   ├── package.json---

   git commit -m 'feat: add amazing feature'

   ```│   └── Dockerfile

4. **Push** to your branch

   ```bash├── docker-compose.yml       # Docker orchestration**Happy Coding! 🎉**

   git push origin feature/amazing-feature

   ```├── README.md

5. **Open** a Pull Request└── .gitignore

````

### Commit Message Convention

---

We follow [Conventional Commits](https://www.conventionalcommits.org/):

## 📚 API Documentation

- `feat:` New feature

- `fix:` Bug fix### Interactive API Docs

- `docs:` Documentation changes

- `refactor:` Code refactoring- **Swagger UI**: http://localhost:8000/docs

- `test:` Adding tests- **ReDoc**: http://localhost:8000/redoc

- `chore:` Maintenance tasks

### Main Endpoints

---

#### Authentication

## 📄 License

- `POST /auth/login` - User login

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.- `POST /auth/register` - User registration

- `POST /auth/logout` - User logout

---- `GET /auth/profile` - Get current user profile



## 👥 Team#### Students



- **Backend Development**: FastAPI architecture, API design, database modeling- `GET /students` - List students

- **Frontend Development**: React UI/UX, component library, state management  - `POST /students/register` - Register as student

- **DevOps & Infrastructure**: Docker containerization, deployment automation- `GET /students/{id}/sessions` - Get student sessions



---#### Tutors



## 🙏 Acknowledgments- `GET /tutors` - List tutors (with filters)

- `POST /tutors/register` - Register as tutor

- HCMUT for institutional support and resources- `GET /tutors/{id}/reviews` - Get tutor reviews

- FastAPI framework for excellent documentation

- React community for valuable learning resources#### Sessions

- Supabase for backend infrastructure platform

- `POST /sessions` - Create session

---- `GET /sessions/{id}` - Get session details

- `PUT /sessions/{id}` - Update session

## 📞 Support- `POST /sessions/{id}/materials` - Upload materials



If you encounter any issues or have questions:#### Forums



1. Check existing [GitHub Issues](https://github.com/Vinhphu159874123/Tutor-suporting-system/issues)- `GET /forum/posts` - List forum posts

2. Create a new issue with detailed description- `POST /forum/posts` - Create new post

3. Contact the development team- `POST /forum/posts/{id}/comments` - Add comment



---For complete API reference, visit `/docs` after starting the backend.



**Made with ❤️ by Nguyen Trung Nhan & Nguyen Vinh Phu**---



**Happy Coding! 🚀**## 💻 Development


### Running Locally (Without Docker)

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

#### Mock Services

**SSO (Python):**

```bash
cd backend/mock_services/sso
pip install -r requirements.txt
python main.py  # Runs on port 3001
```

**DataCore (Node.js):**

```bash
cd backend/mock_services/datacore
npm install
npm start  # Runs on port 3002
```

**Library (Node.js):**

```bash
cd backend/mock_services/library
npm install
npm start  # Runs on port 3003
```

### Useful Commands

```bash
# Docker Compose
docker-compose up --build        # Rebuild and start
docker-compose down -v           # Stop and remove volumes
docker-compose logs -f backend   # View backend logs
docker-compose restart frontend  # Restart frontend only

# Database
docker exec -it tutor-db psql -U postgres -d tutor_system

# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test

# Code formatting
cd backend && black .
cd frontend && npm run format
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m 'feat: add amazing feature'
   ```
4. **Push** to your branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

- **Backend Team**: FastAPI development, API design, database architecture
- **Frontend Team**: React development, UI/UX implementation
- **DevOps Team**: Docker configuration, deployment setup

---

## 🙏 Acknowledgments

- HCMUT for institutional support
- FastAPI for excellent documentation
- React community for valuable resources
- Supabase for backend infrastructure

---

## 📞 Support

If you encounter any issues or have questions:

1. Check existing [GitHub Issues](https://github.com/Vinhphu159874123/Tutor-suporting-system/issues)
2. Create a new issue with detailed description
3. Contact the development team

---

**Made with ❤️ by HCMUT Development Team**

**Happy Coding! 🚀**

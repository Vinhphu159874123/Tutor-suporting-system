# 🎓 HCMUT Tutor Support System

> A comprehensive platform for managing tutoring programs, connecting students with tutors, scheduling sessions, and supporting academic learning at Ho Chi Minh City University of Technology (HCMUT).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Environment Setup](#-environment-setup)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Contributing](#-contributing)

---

## 🌟 Overview

The HCMUT Tutor Support System is a modern, full-stack web application designed to streamline tutoring services at HCMUT. It provides:

- **Student-Tutor Matching**: AI-powered recommendation system
- **Session Management**: Comprehensive scheduling and tracking
- **Learning Analytics**: Progress tracking and performance reports
- **Community Features**: Forums and study groups
- **External Integration**: HCMUT SSO, DataCore, and Library services

---

## 🏗️ System Architecture

### Tech Stack

**Backend:**

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 14+ (Supabase - external)
- **Cache**: Redis 7 (with AOF persistence)
- **Authentication**: JWT + HCMUT SSO Integration

**Frontend:**

- **Framework**: React 18.2+ with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Axios

**Infrastructure:**

- **Reverse Proxy**: Nginx (SSL termination)
- **Containerization**: Docker & Docker Compose
- **Deployment**: VPS / Cloud Run
- **Frontend Hosting**: Vercel

### Production Architecture

```
Client → Nginx (port 80/443, SSL) → Backend API (port 8000, internal)
                                  → Redis (port 6379, internal)
                                  → Supabase (external PostgreSQL)
```

---

## ✨ Features

### 🔐 Authentication & Authorization

- [x] HCMUT SSO integration
- [x] JWT-based authentication
- [x] Role-based access control (Student/Tutor/Coordinator/Admin)
- [x] Profile management

### 📝 Registration System

- [x] Student registration with subject preferences
- [x] Tutor registration with qualifications
- [x] Coordinator approval workflow
- [x] Registration status tracking

### 📅 Scheduling & Sessions

- [x] Create and manage tutoring sessions
- [x] Multiple location types (Online/Offline/Hybrid)
- [x] Session status tracking (Draft → Confirmed → Ongoing → Completed)
- [x] Attendance management
- [x] Session materials upload/download

### 📊 Reports & Analytics

- [x] Student progress tracking
- [x] Tutor performance reports
- [x] Course analytics
- [x] Learning achievements (Gamification)

### 💬 Community Features

- [x] Discussion forums
- [x] Study groups
- [x] Q&A threads
- [x] Resource sharing

### 🤖 AI Features

- [ ] Intelligent tutor-student matching
- [ ] Learning path recommendations
- [ ] Schedule optimization

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose**
- **Node.js** 18+ (for local frontend development)
- **Python** 3.11+ (for local backend development)
- **Git**

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Vinhphu159874123/Tutor-suporting-system.git
   cd Tutor-suporting-system
   ```

2. **Set up environment variables**

   ```bash
   cp .env.prod.template ./backend/.env
   # Edit backend/.env with your actual credentials
   ```

3. **Deploy with Docker Compose**

   ```bash
   # Build and start all services (Nginx + Backend + Redis)
   docker compose -f docker-compose.prod.yml up --build -d

   # View logs
   docker compose -f docker-compose.prod.yml logs -f

   # Stop all services
   docker compose -f docker-compose.prod.yml down
   ```

4. **Access the application**

   - **Frontend**: Deployed on Vercel (or locally at http://localhost:3000)
   - **Backend API**: https://your-domain.com (via Nginx)
   - **API Docs**: https://your-domain.com/docs

### Demo Accounts

| Role        | Email                       | Password      |
| ----------- | --------------------------- | ------------- |
| Admin       | admin@hcmut.edu.vn          | admin123      |
| Coordinator | coordinator.cs@hcmut.edu.vn | coordinator123|
| Tutor       | tutor.hoa@hcmut.edu.vn      | tutor123      |
| Student     | 2312345@hcmut.edu.vn        | student123    |

---

## 🔧 Environment Setup

### Backend Configuration

Create `.env` file in `backend/` directory (or copy from `.env.prod.template`):

```bash
# Database (Supabase)
DATABASE_URL=postgresql://postgres:password@your-supabase-host:5432/postgres

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://:securepassword@redis:6379
REDIS_PASSWORD=securepassword

# Security
BCRYPT_ROUNDS=12
```

### Frontend Configuration

Create `.env` file in `frontend/` directory:

```bash
REACT_APP_API_URL=https://your-domain.com/api/v1
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_anon_key_here
```

### Database Setup

This project uses **Supabase** as the hosted PostgreSQL database:

1. Create a project at [supabase.com](https://supabase.com)
2. Run migration scripts in the Supabase SQL Editor:
   ```bash
   # Copy SQL from backend/sql/ directory
   # Run in Supabase SQL Editor
   ```

---

## 📁 Project Structure

```
Tutor-suporting-system/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints (auth, users, sessions, etc.)
│   │   ├── core/             # Configuration, database, dependencies
│   │   ├── events/           # Event system (notifications, listeners)
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── repositories/     # Data access layer
│   │   ├── schemas/          # Pydantic schemas (DTOs)
│   │   ├── services/         # Business logic layer
│   │   └── websocket/        # WebSocket handlers
│   ├── sql/                  # Database migrations & seed data
│   ├── uploads/              # Uploaded files (served via Nginx)
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile.prod       # Production Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable React components
│   │   ├── pages/            # Page components (admin, auth, session, etc.)
│   │   ├── services/         # API service layer (Axios)
│   │   └── stores/           # State management (Context API)
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.prod.yml   # Production Docker orchestration
├── nginx.prod.conf           # Nginx reverse proxy config
├── vercel.json               # Vercel frontend deployment config
├── .env.prod.template        # Environment variables template
├── README.md
└── .gitignore
```

---

## 📚 API Documentation

### Interactive API Docs

- **Swagger UI**: https://your-domain.com/docs
- **ReDoc**: https://your-domain.com/redoc

### Main Endpoints

#### Authentication

- `POST /api/v1/auth/login` — User login
- `POST /api/v1/auth/register` — User registration
- `POST /api/v1/auth/logout` — User logout
- `GET /api/v1/auth/profile` — Get current user profile

#### Students

- `GET /api/v1/students` — List students
- `POST /api/v1/students/register` — Register as student
- `GET /api/v1/students/{id}/sessions` — Get student sessions

#### Tutors

- `GET /api/v1/tutors` — List tutors (with filters)
- `POST /api/v1/tutors/register` — Register as tutor
- `GET /api/v1/tutors/{id}/reviews` — Get tutor reviews

#### Sessions

- `POST /api/v1/sessions` — Create session
- `GET /api/v1/sessions/{id}` — Get session details
- `PUT /api/v1/sessions/{id}` — Update session
- `POST /api/v1/sessions/{id}/materials` — Upload materials

#### Forums

- `GET /api/v1/forum/posts` — List forum posts
- `POST /api/v1/forum/posts` — Create new post
- `POST /api/v1/forum/posts/{id}/comments` — Add comment

For complete API reference, visit `/docs` after starting the backend.

---

## 💻 Development

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

### Useful Commands

```bash
# Production Docker Compose
docker compose -f docker-compose.prod.yml up --build -d    # Build and start
docker compose -f docker-compose.prod.yml down              # Stop services
docker compose -f docker-compose.prod.yml down -v           # Stop and remove volumes
docker compose -f docker-compose.prod.yml logs -f backend   # View backend logs
docker compose -f docker-compose.prod.yml restart backend   # Restart backend

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

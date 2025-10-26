# Tutor Support System - HCMUT

## Project Overview
Full-stack Tutor Support System for Ho Chi Minh City University of Technology (HCMUT) to manage tutoring programs, student-tutor matching, scheduling, and academic support.

## Tech Stack
- **Backend**: Python FastAPI
- **Frontend**: React TypeScript
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Mock HCMUT_SSO integration
- **External Services**: Mock HCMUT_DATACORE, HCMUT_LIBRARY, AI_RECOMMENDER
- **Containerization**: Docker & Docker Compose
- **AI Features**: Intelligent tutor-student matching

## Key Features
1. Account Management (Login/Logout/Profile)
2. Registration Module (Student/Tutor registration)
3. Scheduling Module (Session scheduling)
4. Session Management (Conduct sessions, materials)
5. Report Module (Academic reports, analytics)
6. Administrator Configuration (User/Role management)
7. Learning Forum (Community features)
8. AI-powered tutor-student matching

## Development Guidelines
- Use TypeScript for type safety
- Follow RESTful API design principles
- Implement proper authentication and authorization
- Use proper error handling and validation
- Follow clean code practices
- Implement comprehensive testing

## Project Structure
```
├── backend/          # FastAPI Python backend
├── frontend/         # React TypeScript frontend
├── mock_services/    # Mock external services
├── .vscode/         # VS Code configuration
└── docker-compose.yml # Docker orchestration
```

## Quick Start
1. Install Docker Desktop
2. Run: `docker-compose up --build`
3. Access frontend: http://localhost:3000
4. Access API docs: http://localhost:8000/docs

## Development Commands
- **Start full stack**: Use VS Code Task "Start Full Stack" or `docker-compose up`
- **Backend only**: Use VS Code Task "Start Backend Only"  
- **Frontend only**: Use VS Code Task "Start Frontend Only (Dev)"
- **View logs**: Use VS Code Task "View Logs"
- **Stop services**: Use VS Code Task "Stop All Services"
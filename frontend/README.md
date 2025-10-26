# Frontend Setup & Development Guide

## 📦 Prerequisites
- Node.js 16+ and npm
- Backend server running on http://localhost:8000

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Environment Setup
Copy `.env` file is already created with default values.
Edit if you need different API URL:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### 3. Start Development Server
```bash
npm start
```

App will open at: http://localhost:3000

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Layout.tsx
│   │   ├── Navbar.tsx
│   │   └── ...
│   ├── pages/          # Page components (routes)
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   └── ...
│   ├── services/       # API service layer
│   │   ├── api.ts      # Axios instance
│   │   ├── authService.ts
│   │   └── ...
│   ├── stores/         # Zustand state management
│   │   ├── authStore.ts
│   │   └── ...
│   ├── App.tsx         # Root component
│   └── index.tsx       # Entry point
├── public/             # Static assets
├── package.json
├── tailwind.config.js  # Tailwind CSS config
└── tsconfig.json       # TypeScript config
```

## 🛠️ Available Scripts

```bash
# Development
npm start              # Start dev server (hot reload)

# Production
npm run build         # Build for production
npm run preview       # Preview production build

# Testing
npm test              # Run tests
npm run test:coverage # Test with coverage

# Code Quality
npm run lint          # Run ESLint
npm run format        # Format with Prettier
```

## 🎨 Tech Stack

- **Framework**: React 18 + TypeScript
- **Routing**: React Router v6
- **State Management**: Zustand
- **API Client**: Axios + React Query
- **Styling**: Tailwind CSS
- **UI Components**: Headless UI + Heroicons
- **Forms**: React Hook Form
- **Notifications**: React Toastify
- **Date Handling**: date-fns
- **Calendar**: React Calendar

## 🔐 Authentication Flow

1. User logs in via `/login`
2. Token stored in Zustand store + localStorage
3. Axios interceptor adds token to all requests
4. Protected routes check `isAuthenticated` state
5. Redirect to `/login` if not authenticated

## 📡 API Integration

```typescript
// Example: Using API service
import { authService } from './services/authService';

const login = async (email: string, password: string) => {
  const response = await authService.login(email, password);
  // Token automatically saved by authStore
};
```

## 🎯 Key Features

- ✅ Authentication (Login/Register/Logout)
- ✅ Role-based routing (Student/Tutor/Admin)
- ✅ Dashboard with analytics
- ✅ Session scheduling
- ✅ Learning forum
- ✅ Reports & analytics
- ✅ Profile management
- ✅ Responsive design

## 🐛 Troubleshooting

### Port 3000 already in use
```bash
# Kill process on port 3000 (Windows)
npx kill-port 3000

# Or use different port
PORT=3001 npm start
```

### Module not found
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Tailwind styles not working
```bash
# Rebuild Tailwind
npm run build:css
```

## 🔄 Connecting to Backend

Make sure backend is running:
```bash
# In backend directory
uvicorn app.main:app --reload
```

Frontend will proxy API requests to backend via `REACT_APP_API_URL`.

## 📚 Documentation

- [React Docs](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Router](https://reactrouter.com/)
- [Zustand](https://github.com/pmndrs/zustand)

## 🚢 Deployment

### Build for production
```bash
npm run build
```

Output will be in `build/` directory.

### Deploy to:
- Vercel: `vercel deploy`
- Netlify: Drag & drop `build/` folder
- Docker: Use included `Dockerfile`

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `REACT_APP_ENV` | Environment | `development` |
| `REACT_APP_ENABLE_MOCK_SSO` | Enable mock SSO | `true` |

## ✨ Development Tips

1. Use React DevTools for debugging
2. Check browser console for errors
3. API calls visible in Network tab
4. Hot reload enabled - save to see changes
5. TypeScript will show type errors in editor

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Create pull request

---

**Happy Coding! 🚀**

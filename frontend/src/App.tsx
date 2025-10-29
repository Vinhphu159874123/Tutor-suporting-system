import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { useAuthStore } from './stores/authStore';
import Layout from './components/Layout';

// Auth pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';
import ResetPassword from './pages/auth/ResetPassword';

// Common pages
import Dashboard from './pages/common/Dashboard';
import Reports from './pages/common/Reports';
import Forum from './pages/common/Forum';

// User pages
import Profile from './pages/user/Profile';
import Notifications from './pages/user/Notifications';
import Settings from './pages/user/Settings';

// Tutor pages
import TutorList from './pages/tutor/TutorList';
import TutorDetail from './pages/tutor/TutorDetail';

// Session pages
import Sessions from './pages/session/Sessions';
import SessionDetail from './pages/session/SessionDetail';
import SessionHistory from './pages/session/SessionHistory';
import Scheduling from './pages/session/Scheduling';

// Admin pages
import Admin from './pages/admin/Admin';

import './index.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route 
              path="/login" 
              element={
                isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
              } 
            />
            <Route 
              path="/register" 
              element={
                isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />
              } 
            />
            <Route 
              path="/forgot-password" 
              element={
                isAuthenticated ? <Navigate to="/dashboard" replace /> : <ForgotPassword />
              } 
            />
            <Route 
              path="/reset-password/:token" 
              element={
                isAuthenticated ? <Navigate to="/dashboard" replace /> : <ResetPassword />
              } 
            />
            
            {/* Protected Routes */}
            <Route
              path="/*"
              element={
                isAuthenticated ? (
                  <Layout>
                    <Routes>
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/profile" element={<Profile />} />
                      <Route path="/sessions" element={<Sessions />} />
                      <Route path="/sessions/:id" element={<SessionDetail />} />
                      <Route path="/history" element={<SessionHistory />} />
                      <Route path="/scheduling" element={<Scheduling />} />
                      <Route path="/reports" element={<Reports />} />
                      <Route path="/forum" element={<Forum />} />
                      <Route path="/admin" element={<Admin />} />
                      <Route path="/tutors" element={<TutorList />} />
                      <Route path="/tutors/:id" element={<TutorDetail />} />
                      <Route path="/notifications" element={<Notifications />} />
                      <Route path="/settings" element={<Settings />} />
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                  </Layout>
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
          </Routes>
          
          <ToastContainer
            position="top-right"
            autoClose={3000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { useAuthStore } from './stores/authStore';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Sessions from './pages/Sessions';
import Scheduling from './pages/Scheduling';
import Reports from './pages/Reports';
import Forum from './pages/Forum';
import Admin from './pages/Admin';
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
            <Route 
              path="/login" 
              element={
                isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
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
                      <Route path="/scheduling" element={<Scheduling />} />
                      <Route path="/reports" element={<Reports />} />
                      <Route path="/forum" element={<Forum />} />
                      <Route path="/admin" element={<Admin />} />
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
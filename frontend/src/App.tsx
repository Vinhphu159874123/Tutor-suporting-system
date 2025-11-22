import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "react-query";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { useAuthStore } from "./stores/authStore.ts";
import Layout from "./components/Layout.tsx";

// Auth pages
import Login from "./pages/auth/Login.tsx";
import Register from "./pages/auth/Register.tsx";
import ForgotPassword from "./pages/auth/ForgotPassword.tsx";
import ResetPassword from "./pages/auth/ResetPassword.tsx";
import Landing from "./pages/auth/Landing.tsx";
import SessionExpired from "./pages/auth/SessionExpired.tsx";

// Common pages
import Dashboard from "./pages/common/Dashboard.tsx";
import Reports from "./pages/common/Reports.tsx";
import Forum from "./pages/common/Forum.tsx";
import ForumDetail from "./pages/common/ForumDetail.tsx";
import CreateForum from "./pages/common/CreateForum.tsx";
import ExportReport from "./pages/common/ExportReport.tsx";
import StudyGroups from "./pages/common/StudyGroups.tsx";
import StudyGroupDetail from "./pages/common/StudyGroupDetail.tsx";

// User pages
import Profile from "./pages/user/Profile.tsx";
import Notifications from "./pages/user/Notifications.tsx";
import Settings from "./pages/user/Settings.tsx";

// Tutor pages
import TutorList from "./pages/tutor/TutorList.tsx";
import TutorDetail from "./pages/tutor/TutorDetail.tsx";

// Session pages
import Sessions from "./pages/session/Sessions.tsx";
import SessionDetail from "./pages/session/SessionDetail.tsx";
import SessionHistory from "./pages/session/SessionHistory.tsx";
import Scheduling from "./pages/session/Scheduling.tsx";
import UploadMaterials from "./pages/session/UploadMaterials.tsx";
import MaterialsList from "./pages/session/MaterialsList.tsx";
import OnlineSession from "./pages/session/OnlineSession.tsx";
import LearningProgress from "./pages/session/LearningProgress.tsx";

// Course pages
import MyCourses from "./pages/courses/MyCourses.tsx";

// Admin pages
import Admin from "./pages/admin/Admin.tsx";
import CoordinatorReview from "./pages/admin/CoordinatorReview.tsx";
import CoordinatorSessions from "./pages/admin/CoordinatorSessions.tsx";

import "./index.css";

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
              path="/landing"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Landing />
                )
              }
            />
            <Route path="/session-expired" element={<SessionExpired />} />
            <Route
              path="/login"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Login />
                )
              }
            />
            <Route
              path="/register"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Register />
                )
              }
            />
            <Route
              path="/forgot-password"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <ForgotPassword />
                )
              }
            />
            <Route
              path="/reset-password/:token"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <ResetPassword />
                )
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
                      <Route path="/courses" element={<MyCourses />} />
                      <Route path="/sessions" element={<Sessions />} />
                      <Route path="/sessions/:id" element={<SessionDetail />} />
                      <Route path="/history" element={<SessionHistory />} />
                      <Route path="/scheduling" element={<Scheduling />} />
                      <Route path="/upload-materials" element={<UploadMaterials />} />
                      <Route path="/materials" element={<MaterialsList />} />
                      <Route path="/online-session/:id" element={<OnlineSession />} />
                      <Route path="/learning-progress" element={<LearningProgress />} />
                      <Route path="/reports" element={<Reports />} />
                      <Route path="/export-report" element={<ExportReport />} />
                      <Route path="/forum" element={<Forum />} />
                      <Route path="/forum/:id" element={<ForumDetail />} />
                      <Route path="/forum/create" element={<CreateForum />} />
                      <Route path="/study-groups" element={<StudyGroups />} />
                      <Route path="/study-groups/:id" element={<StudyGroupDetail />} />
                      <Route path="/admin" element={<Admin />} />
                      <Route path="/admin/review" element={<CoordinatorReview />} />
                      <Route path="/admin/sessions" element={<CoordinatorSessions />} />
                      <Route path="/tutors" element={<TutorList />} />
                      <Route path="/tutors/:id" element={<TutorDetail />} />
                      <Route
                        path="/notifications"
                        element={<Notifications />}
                      />
                      <Route path="/settings" element={<Settings />} />
                      <Route
                        path="/"
                        element={<Navigate to="/dashboard" replace />}
                      />
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

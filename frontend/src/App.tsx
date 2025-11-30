import React, { useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "react-query";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { useAuthStore } from "./stores/authStore";
import { authApi } from "./services/api";
import Layout from "./components/Layout";

// Auth pages
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import Landing from "./pages/auth/Landing";
import SessionExpired from "./pages/auth/SessionExpired";

// Common pages
import Dashboard from "./pages/common/Dashboard";
import Reports from "./pages/common/Reports";
import Forum from "./pages/common/Forum";
import ForumDetail from "./pages/common/ForumDetail";
import CreateForum from "./pages/common/CreateForum";
import ExportReport from "./pages/common/ExportReport";
import StudyGroups from "./pages/common/StudyGroups";
import CreateStudyGroup from "./pages/common/CreateStudyGroup";
import StudyGroupDetail from "./pages/common/StudyGroupDetail";

// User pages
import Profile from "./pages/user/Profile";
import Notifications from "./pages/user/Notifications";
import Settings from "./pages/user/Settings";

// Tutor pages
import TutorList from "./pages/tutor/TutorList";
import TutorDetail from "./pages/tutor/TutorDetail";
import RegisterTutor from "./pages/tutor/RegisterTutor";

// Session pages
import Sessions from "./pages/session/Sessions";
import BookSession from "./pages/student/BookSession";
import SessionDetail from "./pages/session/SessionDetail";
import SessionHistory from "./pages/session/SessionHistory";
import Scheduling from "./pages/session/Scheduling";
import UploadMaterials from "./pages/session/UploadMaterials";
import MaterialsList from "./pages/session/MaterialsList";
import OnlineSession from "./pages/session/OnlineSession";
import LearningProgress from "./pages/session/LearningProgress";

// Course pages
import MyCourses from "./pages/courses/MyCourses";
import CourseDetail from "./pages/courses/CourseDetail";

// Admin pages
import Admin from "./pages/admin/Admin";

// Coordinator pages
import CoordinatorDashboard from "./pages/coordinator/CoordinatorDashboard";
import CoordinatorReview from "./pages/coordinator/CoordinatorReview";
import CoordinatorSessions from "./pages/coordinator/CoordinatorSessions";

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
  const { isAuthenticated, token, setUser } = useAuthStore();

  // Refresh user profile on app load if authenticated
  useEffect(() => {
    const refreshUserProfile = async () => {
      if (isAuthenticated && token) {
        try {
          const response: any = await authApi.getProfile(token);
          setUser(response.data);
        } catch (error) {
          console.error("Failed to refresh user profile:", error);
        }
      }
    };
    
    refreshUserProfile();
  }, []); // Only run once on mount

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
                      <Route path="/courses/:code" element={<CourseDetail />} />
                      <Route path="/sessions" element={<Sessions />} />
                      <Route path="/sessions/book" element={<BookSession />} />
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
                      <Route path="/study-groups/create" element={<CreateStudyGroup />} />
                      <Route path="/study-groups/:id" element={<StudyGroupDetail />} />
                      <Route path="/admin" element={<Admin />} />
                      <Route path="/coor" element={<CoordinatorDashboard />} />
                      <Route path="/coor/review" element={<CoordinatorReview />} />
                      <Route path="/coor/sessions" element={<CoordinatorSessions />} />
                      <Route path="/tutors" element={<TutorList />} />
                      <Route path="/tutors/register" element={<RegisterTutor />} />
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

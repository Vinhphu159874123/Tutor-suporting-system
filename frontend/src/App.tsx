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
// import NotificationListener from "./components/NotificationListener"; // Disabled - component not found

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
import SessionRequests from "./pages/tutor/SessionRequests";

// Course pages
import MyCourses from "./pages/course/MyCourses";
import CourseDetail from "./pages/course/CourseDetail";
import CourseProgress from "./pages/course/CourseProgress";

// Tutor pages
import TutorStatistics from "./pages/tutor/TutorStatistics";

// Coordinator pages
import TutorsList from "./pages/coordinator/TutorsList";
import TutorCourses from "./pages/coordinator/TutorCourses";
import CourseReport from "./pages/coordinator/CourseReport";

// Student pages
import BrowseCourses from "./pages/student/BrowseCourses";
import StudentScheduling from "./pages/student/StudentScheduling";

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        {/* Global notification listener - DISABLED: component not found */}
        {/* {isAuthenticated && <NotificationListener />} */}

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
                      <Route path="/my-courses" element={<MyCourses />} />
                      <Route path="/my-courses/:subjectId" element={<CourseDetail />} />
                      <Route path="/courses/:subjectId/progress" element={<CourseProgress />} />
                      <Route path="/reports" element={<Reports />} />
                      <Route path="/export-report" element={<ExportReport />} />
                      <Route path="/forum" element={<Forum />} />
                      <Route path="/forum/:id" element={<ForumDetail />} />
                      <Route path="/forum/create" element={<CreateForum />} />
                      <Route path="/study-groups" element={<StudyGroups />} />
                      <Route path="/study-groups/create" element={<CreateStudyGroup />} />
                      <Route path="/study-groups/:id" element={<StudyGroupDetail />} />
                      <Route path="/admin/*" element={<Admin />} />
                      <Route path="/coor" element={<CoordinatorDashboard />} />
                      <Route path="/coor/review" element={<CoordinatorReview />} />
                      <Route path="/coor/sessions" element={<CoordinatorSessions />} />
                      <Route path="/coordinator/tutors" element={<TutorsList />} />
                      <Route path="/coordinator/tutors/:tutorId/courses" element={<TutorCourses />} />
                      <Route path="/coordinator/tutors/:tutorId/courses/:subjectId" element={<CourseReport />} />
                      <Route path="/tutors" element={<TutorList />} />
                      <Route path="/tutors/register" element={<RegisterTutor />} />
                      <Route path="/tutors/:id" element={<TutorDetail />} />
                      <Route path="/tutors/requests" element={<SessionRequests />} />
                      <Route path="/browse-courses" element={<BrowseCourses />} />
                      <Route path="/student/scheduling" element={<StudentScheduling />} />
                      <Route path="/tutor/statistics" element={<TutorStatistics />} />
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

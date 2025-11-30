import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// 🟢 REAL MODE - Connect to backend API
const MOCK_MODE = false;

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth-storage");
  if (token) {
    const parsedToken = JSON.parse(token);
    if (parsedToken.state?.token) {
      config.headers.Authorization = `Bearer ${parsedToken.state.token}`;
    }
  }
  return config;
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth storage on 401
      localStorage.removeItem("auth-storage");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Mock helper
const mockResponse = (data: any, delay = 500) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data, status: 200, statusText: "OK", headers: {}, config: {} });
    }, delay);
  });
};

// Auth API
export const authApi = {
  login: (email: string, password: string) => {
    if (MOCK_MODE) {
      return mockResponse({
        access_token: "mock-token-12345",
        token_type: "bearer",
        user: {
          user_id: 1,
          email: email,
          full_name: "Mock User",
          role: "student",
        },
      });
    }
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    return apiClient.post("/api/v1/auth/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
  },

  register: (userData: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Registration successful" });
    }
    return apiClient.post("/api/v1/auth/register", userData);
  },

  getProfile: (token?: string) => {
    if (MOCK_MODE) {
      return mockResponse({
        user_id: 1,
        email: "mock@example.com",
        full_name: "Mock User",
        role: "student",
        phone: "0123456789",
        avatar_url: null,
        is_active: true,
      });
    }
    const config = token
      ? { headers: { Authorization: `Bearer ${token}` } }
      : {};
    return apiClient.get("/api/v1/auth/me", config);
  },

  logout: () => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Logged out" });
    }
    return apiClient.post("/api/v1/auth/logout");
  },

  refreshToken: () => {
    if (MOCK_MODE) {
      return mockResponse({ access_token: "new-mock-token" });
    }
    return apiClient.post("/api/v1/auth/refresh-token");
  },
};

// Users API
export const usersApi = {
  getProfile: () => {
    if (MOCK_MODE) {
      return mockResponse({
        user_id: 1,
        email: "mock@example.com",
        full_name: "Mock User",
        role: "student",
      });
    }
    return apiClient.get("/api/v1/users/profile");
  },

  updateProfile: (userData: any) => {
    if (MOCK_MODE) {
      return mockResponse({ ...userData, message: "Profile updated" });
    }
    return apiClient.put("/api/v1/users/profile", userData);
  },

  getUsers: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse([
        {
          user_id: 1,
          email: "user1@example.com",
          full_name: "User 1",
          role: "student",
        },
        {
          user_id: 2,
          email: "user2@example.com",
          full_name: "User 2",
          role: "tutor",
        },
      ]);
    }
    return apiClient.get("/api/v1/users", { params });
  },

  getUser: (userId: number) => {
    if (MOCK_MODE) {
      return mockResponse({
        user_id: userId,
        email: `user${userId}@example.com`,
        full_name: `User ${userId}`,
        role: "student",
      });
    }
    return apiClient.get(`/api/v1/users/${userId}`);
  },

  deleteUser: (userId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "User deleted" });
    }
    return apiClient.delete(`/api/v1/users/${userId}`);
  },

  getDashboardStats: () => {
    if (MOCK_MODE) {
      return mockResponse({
        total_sessions: 24,
        completed_sessions: 18,
        upcoming_sessions: 6,
        average_rating: 4.8
      });
    }
    return apiClient.get("/api/v1/users/stats/dashboard");
  },

  getCoordinatorStats: () => {
    if (MOCK_MODE) {
      return mockResponse({
        total_sessions: 240,
        pending_tutors: 2,
        pending_sessions: 14,
        average_rating: 4.8
      });
    }
    return apiClient.get("/api/v1/users/stats/coordinator");
  },
};

// Tutors API
export const tutorsApi = {
  getTutors: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse([
        {
          tutor_id: 1,
          full_name: "Tutor 1",
          specialization: "Math",
          rating: 4.5,
        },
        {
          tutor_id: 2,
          full_name: "Tutor 2",
          specialization: "Physics",
          rating: 4.8,
        },
      ]);
    }
    return apiClient.get("/api/v1/tutors", { params });
  },

  getTutor: (tutorId: number) => {
    return apiClient.get(`/api/v1/tutors/${tutorId}`);
  },

  getTutorAvailability: (tutorId: number) => {
    return apiClient.get(`/api/v1/tutors/${tutorId}/availability`);
  },

  getMyTutorProfile: () => {
    return apiClient.get("/api/v1/tutors/me");
  },

  registerTutor: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Tutor registered" });
    }
    return apiClient.post("/api/v1/tutors/register", data);
  },

  updateTutor: (tutorId: number, data: any) => {
    return apiClient.put(`/api/v1/tutors/${tutorId}`, data);
  },

  getTutorSessions: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse([
        {
          session_id: 1,
          subject: "Math",
          date: "2025-11-20",
          status: "scheduled",
        },
      ]);
    }
    return apiClient.get("/api/v1/tutors/sessions", { params });
  },

  setAvailability: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Availability set" });
    }
    return apiClient.post("/api/v1/tutors/availability", data);
  },
};

// Students API
export const studentsApi = {
  getStudents: () => {
    if (MOCK_MODE) {
      return mockResponse([
        {
          student_id: 1,
          full_name: "Student 1",
          email: "student1@example.com",
        },
      ]);
    }
    return apiClient.get("/api/v1/students");
  },

  registerStudent: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Student registered" });
    }
    return apiClient.post("/api/v1/students/register", data);
  },

  getStudentSessions: () => {
    if (MOCK_MODE) {
      return mockResponse([
        {
          session_id: 1,
          subject: "Math",
          date: "2025-11-20",
          status: "scheduled",
        },
      ]);
    }
    return apiClient.get("/api/v1/students/sessions");
  },

  submitFeedback: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Feedback submitted" });
    }
    return apiClient.post("/api/v1/students/feedback", data);
  },
};

// Sessions API
export const sessionsApi = {
  getSessions: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse([
        {
          session_id: 1,
          subject: "Math",
          date: "2025-11-20",
          status: "scheduled",
          tutor_name: "Tutor 1",
        },
        {
          session_id: 2,
          subject: "Physics",
          date: "2025-11-21",
          status: "completed",
          tutor_name: "Tutor 2",
        },
      ]);
    }
    return apiClient.get("/api/v1/sessions", { params });
  },

  createSession: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        session_id: 999,
        ...data,
        message: "Session created",
      });
    }
    return apiClient.post("/api/v1/sessions", data);
  },

  getSession: (sessionId: number) => {
    if (MOCK_MODE) {
      return mockResponse({
        session_id: sessionId,
        subject: "Math",
        date: "2025-11-20",
        status: "scheduled",
        tutor_name: "Tutor 1",
      });
    }
    return apiClient.get(`/api/v1/sessions/${sessionId}`);
  },

  updateSession: (sessionId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        session_id: sessionId,
        ...data,
        message: "Session updated",
      });
    }
    return apiClient.put(`/api/v1/sessions/${sessionId}`, data);
  },

  completeSession: (sessionId: number) => {
    return apiClient.post(`/api/v1/sessions/${sessionId}/complete`);
  },

  publishSession: (sessionId: number) => {
    return apiClient.post(`/api/v1/sessions/${sessionId}/publish`);
  },

  joinSession: (sessionId: number, data: any) => {
    return apiClient.post(`/api/v1/sessions/${sessionId}/join`, data);
  },

  acceptParticipant: (sessionId: number, participantId: number) => {
    return apiClient.post(`/api/v1/sessions/${sessionId}/participants/${participantId}/accept`);
  },

  rejectParticipant: (sessionId: number, participantId: number, data: any) => {
    return apiClient.post(`/api/v1/sessions/${sessionId}/participants/${participantId}/reject`, data);
  },

  uploadMaterials: (sessionId: number, formData: FormData) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Materials uploaded" });
    }
    return apiClient.post(`/api/v1/sessions/${sessionId}/materials`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// Scheduling API
export const schedulingApi = {
  getTutorAvailability: (tutorId: string | number) => {
    if (MOCK_MODE) {
      return mockResponse({
        availability: [
          {
            availability_id: 1,
            tutor_id: Number(tutorId),
            date: "2025-11-20",
            start_time: "09:00",
            end_time: "10:00",
          },
          {
            availability_id: 2,
            tutor_id: Number(tutorId),
            date: "2025-11-21",
            start_time: "14:00",
            end_time: "15:30",
          },
        ],
      });
    }
    return apiClient.get(`/api/v1/scheduling/availability/${tutorId}`);
  },

  createAvailability: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        availability_id: Math.floor(Math.random() * 100000),
        ...data,
      });
    }
    return apiClient.post("/api/v1/scheduling/availability", data);
  },

  updateAvailability: (availabilityId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        availability_id: availabilityId,
        ...data,
      });
    }
    return apiClient.put(`/api/v1/scheduling/availability/${availabilityId}`, data);
  },

  deleteAvailability: (availabilityId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Availability removed" });
    }
    return apiClient.delete(`/api/v1/scheduling/availability/${availabilityId}`);
  },

  findSlots: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        slots: [
          { date: "2025-11-22", start_time: "08:00", end_time: "09:00" },
          { date: "2025-11-22", start_time: "13:00", end_time: "14:00" },
        ],
      });
    }
    return apiClient.post("/api/v1/scheduling/find-slots", data);
  },

  scheduleSession: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        session_id: Math.floor(Math.random() * 100000),
        ...data,
        message: "Session scheduled",
      });
    }
    return apiClient.post("/api/v1/scheduling/sessions", data);
  },

  rescheduleSession: (sessionId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Session rescheduled", session_id: sessionId, ...data });
    }
    return apiClient.put(
      `/api/v1/scheduling/sessions/${sessionId}/reschedule`,
      data
    );
  },

  cancelSession: (sessionId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Session cancelled", session_id: sessionId });
    }
    return apiClient.delete(`/api/v1/scheduling/sessions/${sessionId}`);
  },
};

// Reports API
export const reportsApi = {
  getCourseReports: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse({ reports: [] });
    }
    return apiClient.get("/api/v1/reports/courses", { params });
  },

  getAcademicReports: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse({ reports: [] });
    }
    return apiClient.get("/api/v1/reports/academic", { params });
  },

  getTutorActivityReports: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse({ reports: [] });
    }
    return apiClient.get("/api/v1/reports/tutor-activities", { params });
  },

  generateReport: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Report generated" });
    }
    return apiClient.post("/api/v1/reports/generate", data);
  },
};

// Admin API
export const adminApi = {
  getAllUsers: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse([
        { user_id: 1, email: "user1@example.com", role: "student" },
        { user_id: 2, email: "user2@example.com", role: "tutor" },
      ]);
    }
    return apiClient.get("/api/v1/admin/users", { params });
  },

  getAdminStats: () => {
    if (MOCK_MODE) {
      return mockResponse({
        total_users: 1004,
        total_students: 986,
        total_tutors: 18,
        total_sessions: 120,
        average_rating: 4.8
      });
    }
    return apiClient.get("/api/v1/admin/stats");
  },

  updateUserRole: (userId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Role updated" });
    }
    return apiClient.put(`/api/v1/admin/users/${userId}/role`, data);
  },

  getPendingRegistrations: () => {
    if (MOCK_MODE) {
      return mockResponse([]);
    }
    return apiClient.get("/api/v1/admin/registrations");
  },

  approveRegistration: (registrationId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Registration approved" });
    }
    return apiClient.put(
      `/api/v1/admin/registrations/${registrationId}/approve`
    );
  },
};

// Notifications API
export const notificationsApi = {
  getNotifications: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse([
        {
          id: 1,
          type: 'session',
          title: 'Phiên học sắp diễn ra',
          message: 'Bạn có phiên học vào ngày mai',
          time: '2 giờ trước',
          read: false
        }
      ]);
    }
    return apiClient.get("/api/v1/notifications", { params });
  },

  getUnreadCount: () => {
    if (MOCK_MODE) {
      return mockResponse({ unread_count: 5 });
    }
    return apiClient.get("/api/v1/notifications/unread-count");
  },

  markAsRead: (notificationId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Marked as read" });
    }
    return apiClient.put(`/api/v1/notifications/${notificationId}/read`);
  },
};

// Forum API
export const forumApi = {
  getForums: () => {
    if (MOCK_MODE) {
      return mockResponse([]);
    }
    return apiClient.get("/api/v1/forum");
  },

  createForum: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Forum created" });
    }
    return apiClient.post("/api/v1/forum", data);
  },

  getForumPosts: (forumId: number) => {
    if (MOCK_MODE) {
      return mockResponse([]);
    }
    return apiClient.get(`/api/v1/forum/${forumId}/posts`);
  },

  createPost: (forumId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Post created" });
    }
    return apiClient.post(`/api/v1/forum/${forumId}/posts`, data);
  },

  createStudyGroup: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Study group created" });
    }
    return apiClient.post("/api/v1/forum/study-groups", data);
  },
};

// Courses API
export const coursesApi = {
  getMyCourses: () => {
    if (MOCK_MODE) {
      return mockResponse([
        {
          code: "CO3001",
          name: "Software Engineering",
          credits: 4
        }
      ]);
    }
    return apiClient.get("/api/v1/courses/my-courses");
  },

  getCourseInfo: (courseCode: string) => {
    if (MOCK_MODE) {
      return mockResponse({
        code: courseCode,
        name: "Mock Course",
        credits: 4
      });
    }
    return apiClient.get(`/api/v1/courses/courses/${courseCode}`);
  },
};

// Coordinator API
export const coordinatorApi = {
  // Tutor Registration Approval
  getTutorRegistrations: (status: string = "pending", skip: number = 0, limit: number = 50) => {
    return apiClient.get("/api/v1/coordinator/tutor-registrations", {
      params: { status_filter: status, skip, limit }
    });
  },

  approveTutorRegistration: (registrationId: number) => {
    return apiClient.put(`/api/v1/coordinator/tutor-registrations/${registrationId}/approve`);
  },

  rejectTutorRegistration: (registrationId: number, reason: string) => {
    return apiClient.put(`/api/v1/coordinator/tutor-registrations/${registrationId}/reject`, null, {
      params: { reason }
    });
  },

  // Session Approval
  getPendingSessions: (skip: number = 0, limit: number = 50) => {
    return apiClient.get("/api/v1/coordinator/sessions/pending", {
      params: { skip, limit }
    });
  },

  approveSession: (sessionId: number) => {
    return apiClient.put(`/api/v1/coordinator/sessions/${sessionId}/approve`);
  },

  rejectSession: (sessionId: number, reason: string) => {
    return apiClient.put(`/api/v1/coordinator/sessions/${sessionId}/reject`, null, {
      params: { reason }
    });
  },
};

export default apiClient;

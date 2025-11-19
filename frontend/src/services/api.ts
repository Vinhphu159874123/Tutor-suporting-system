import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// 🔴 MOCK MODE - Backend disabled for UI testing
const MOCK_MODE = true;

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
};

// Tutors API
export const tutorsApi = {
  getTutors: () => {
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
    return apiClient.get("/api/v1/tutors");
  },

  registerTutor: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Tutor registered" });
    }
    return apiClient.post("/api/v1/tutors/register", data);
  },

  getTutorSessions: () => {
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
    return apiClient.get("/api/v1/tutors/sessions");
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

  uploadMaterials: (sessionId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Materials uploaded" });
    }
    return apiClient.post(`/api/v1/sessions/${sessionId}/materials`, data);
  },
};

// Scheduling API
export const schedulingApi = {
  scheduleSession: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        session_id: 999,
        ...data,
        message: "Session scheduled",
      });
    }
    return apiClient.post("/api/v1/scheduling/sessions", data);
  },

  getAvailability: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        available_slots: [
          { date: "2025-11-20", time: "09:00-10:00" },
          { date: "2025-11-20", time: "10:00-11:00" },
        ],
      });
    }
    return apiClient.get("/api/v1/scheduling/availability", { params });
  },

  rescheduleSession: (sessionId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Session rescheduled" });
    }
    return apiClient.put(
      `/api/v1/scheduling/sessions/${sessionId}/reschedule`,
      data
    );
  },

  cancelSession: (sessionId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Session cancelled" });
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

export default apiClient;

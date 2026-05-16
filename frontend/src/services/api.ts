import axios from "axios";

// Smart API URL detection:
// - Vercel production: Use Railway HTTPS from env or fallback
// - Local dev (localhost:3000): Use local backend
const isVercelProduction = window.location.hostname.includes('vercel.app');
const API_BASE_URL = process.env.REACT_APP_API_URL;


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
      // Only redirect if NOT on login page (to avoid reload loop)
      const isLoginPage = window.location.pathname === '/login' || window.location.pathname === '/';
      
      if (!isLoginPage) {
        // Clear auth storage on 401
        localStorage.removeItem("auth-storage");
        window.location.href = "/login";
      }
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

    return apiClient.post("/auth/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
  },

  register: (userData: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Registration successful" });
    }
    return apiClient.post("/auth/register", userData);
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
    // If token is explicitly passed (e.g. during login flow before persist),
    // use it directly to avoid race condition with localStorage
    if (token) {
      return apiClient.get("/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
    }
    // Otherwise rely on interceptor (for refresh/subsequent calls)
    return apiClient.get("/auth/me");
  },

  logout: () => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Logged out" });
    }
    return apiClient.post("/auth/logout");
  },

  refreshToken: () => {
    if (MOCK_MODE) {
      return mockResponse({ access_token: "new-mock-token" });
    }
    return apiClient.post("/auth/refresh-token");
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
    return apiClient.get("/users/profile");
  },

  updateProfile: (userData: any) => {
    if (MOCK_MODE) {
      return mockResponse({ ...userData, message: "Profile updated" });
    }
    return apiClient.put("/users/profile", userData);
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
    return apiClient.get("/users/", { params });
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
    return apiClient.get(`/users/${userId}`);
  },

  deleteUser: (userId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "User deleted" });
    }
    return apiClient.delete(`/users/${userId}`);
  },

  getDashboardStats: (mode?: string) => {
    if (MOCK_MODE) {
      return mockResponse({
        total_sessions: 24,
        completed_sessions: 18,
        upcoming_sessions: 6,
        average_rating: 4.8
      });
    }
    const params = mode ? { mode } : {};
    return apiClient.get("/users/stats/dashboard", { params });
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
    return apiClient.get("/users/stats/coordinator");
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
    return apiClient.get("/tutors/", { params });
  },

  getTutor: (tutorId: number) => {
    return apiClient.get(`/tutors/${tutorId}`);
  },

  getTutorAvailability: (tutorId: number) => {
    return apiClient.get(`/tutors/${tutorId}/availability`);
  },

  getMyTutorProfile: () => {
    return apiClient.get("/tutors/me");
  },

  registerTutor: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Tutor registered" });
    }
    return apiClient.post("/tutors/register", data);
  },

  updateTutor: (tutorId: number, data: any) => {
    return apiClient.put(`/tutors/${tutorId}`, data);
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
    return apiClient.get("/tutors/sessions", { params });
  },

  setAvailability: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Availability set" });
    }
    return apiClient.post("/tutors/availability", data);
  },

  registerSubject: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ 
        registration_id: 1,
        status: "pending",
        message: "Subject registration submitted" 
      });
    }
    return apiClient.post("/tutors/register-subject", data);
  },

  getMyRegistrations: (status?: string) => {
    return apiClient.get("/tutors/my-registrations", {
      params: { status }
    });
  },

  // Get available courses for students to browse
  getAvailableCourses: () => {
    return apiClient.get("/tutors/available-courses");
  },

  // Request to join a course
  requestJoinCourse: (registrationId: number) => {
    return apiClient.post(`/tutors/courses/${registrationId}/request-join`);
  },

  // Get enrolled students in tutor's courses
  getEnrolledStudents: () => {
    return apiClient.get("/tutors/courses/enrolled-students");
  },

  // Generate sessions for an approved course
  generateSessionsForCourse: (subjectId: number) => {
    return apiClient.post(`/tutors/courses/${subjectId}/generate-sessions`);
  },
  
  // Check schedule conflicts for course registrations
  checkScheduleConflicts: (registrationIds: number[]) => {
    return apiClient.post("/tutors/check-schedule-conflicts", registrationIds);
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
    return apiClient.get("/students/");
  },

  registerStudent: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Student registered" });
    }
    return apiClient.post("/students/register", data);
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
    return apiClient.get("/students/sessions");
  },

  submitFeedback: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Feedback submitted" });
    }
    return apiClient.post("/students/feedback", data);
  },

  getStudentProfile: (studentId: number) => {
    return apiClient.get(`/students/${studentId}`);
  },

  getStudentProfileByUserId: (userId: number) => {
    return apiClient.get(`/students/by-user/${userId}`);
  },

  getStudentEnrolledCourses: (studentId: number) => {
    return apiClient.get(`/students/${studentId}/enrolled-courses`);
  },
};

// Sessions API
export const sessionsApi = {
  getMySessions: (params?: any) => {
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
    return apiClient.get("/sessions/my-sessions", { params });
  },

  // Get dashboard sessions (optimized + cached) - 3 recent + 3 upcoming only
  getMySessionsDashboard: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        recent: [],
        upcoming: [
          {
            session_id: 1,
            subject: "Math",
            date: "2025-11-20",
            status: "scheduled",
            tutor_name: "Tutor 1",
          }
        ]
      });
    }
    return apiClient.get("/sessions/my-sessions/dashboard", { params });
  },

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
    return apiClient.get("/sessions/", { params });
  },

  createSession: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        session_id: 999,
        ...data,
        message: "Session created",
      });
    }
    return apiClient.post("/sessions/", data);
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
    return apiClient.get(`/sessions/${sessionId}`);
  },

  updateSession: (sessionId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        session_id: sessionId,
        ...data,
        message: "Session updated",
      });
    }
    return apiClient.put(`/sessions/${sessionId}`, data);
  },

  completeSession: (sessionId: number) => {
    return apiClient.post(`/sessions/${sessionId}/complete`);
  },

  publishSession: (sessionId: number) => {
    return apiClient.post(`/sessions/${sessionId}/publish`);
  },

  joinSession: (sessionId: number, data: any) => {
    return apiClient.post(`/sessions/${sessionId}/join`, data);
  },

  acceptParticipant: (sessionId: number, participantId: number) => {
    return apiClient.post(`/sessions/${sessionId}/participants/${participantId}/accept`);
  },

  rejectParticipant: (sessionId: number, participantId: number, data: any) => {
    return apiClient.post(`/sessions/${sessionId}/participants/${participantId}/reject`, data);
  },

  uploadMaterials: (sessionId: number, formData: FormData) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Materials uploaded" });
    }
    return apiClient.post(`/sessions/${sessionId}/materials`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // Upload with progress tracking
  uploadMaterialsWithProgress: (
    sessionId: number, 
    formData: FormData, 
    onUploadProgress: (progressEvent: any) => void
  ) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Materials uploaded" });
    }
    return apiClient.post(`/sessions/${sessionId}/materials`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress
    });
  },

  getSessionMaterials: (sessionId: number) => {
    if (MOCK_MODE) {
      return mockResponse([]);
    }
    return apiClient.get(`/sessions/${sessionId}/materials`);
  },

  // Get materials for multiple sessions in one call - OPTIMIZED
  getBulkMaterials: (sessionIds: number[]) => {
    if (MOCK_MODE) {
      return mockResponse({});
    }
    const ids = sessionIds.join(',');
    return apiClient.get(`/sessions/materials/bulk?session_ids=${ids}`);
  },

  downloadMaterial: (sessionId: number, materialId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Download initiated" });
    }
    return apiClient.get(`/sessions/${sessionId}/materials/${materialId}/download`, {
      responseType: 'blob'
    });
  },

  deleteMaterial: (sessionId: number, materialId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Material deleted" });
    }
    return apiClient.delete(`/sessions/${sessionId}/materials/${materialId}`);
  },

  bulkSaveForSubject: (subjectId: number, sessionsData: any[]) => {
    return apiClient.post(`/sessions/bulk-save-for-subject?subject_id=${subjectId}`, sessionsData);
  },

  // Feedback APIs
  submitFeedback: (sessionId: number, feedbackData: { rating: number; comment?: string; is_anonymous: boolean }) => {
    const formData = new FormData();
    formData.append('rating', feedbackData.rating.toString());
    if (feedbackData.comment) {
      formData.append('comment', feedbackData.comment);
    }
    formData.append('is_anonymous', feedbackData.is_anonymous.toString());
    
    // Token automatically added by request interceptor
    // Don't set Content-Type header, let axios set it with boundary
    return apiClient.post(`/sessions/${sessionId}/feedback`, formData);
  },

  getFeedback: (sessionId: number) => {
    return apiClient.get(`/sessions/${sessionId}/feedback`);
  },

  getBulkFeedbacks: (sessionIds: string) => {
    return apiClient.get(`/sessions/feedback/bulk?session_ids=${sessionIds}`);
  },

  getSubjectFeedbacks: (subjectId: number, tutorId?: number) => {
    const params = tutorId ? { tutor_id: tutorId } : {};
    return apiClient.get(`/sessions/subject/${subjectId}/feedbacks`, { params });
  },

  // Attendance APIs
  getParticipants: (sessionId: number) => {
    return apiClient.get(`/sessions/${sessionId}/participants`);
  },

  markAttendance: (sessionId: number, attendanceData: Array<{user_id: number, is_present: boolean, is_late: boolean, is_excused: boolean}>) => {
    return apiClient.post(`/sessions/${sessionId}/attendance`, attendanceData);
  },

  removeStudentFromSubject: (subjectId: number, studentId: number, tutorId: number) => {
    return apiClient.delete(`/sessions/remove-student-from-subject`, {
      params: {
        subject_id: subjectId,
        student_id: studentId,
        tutor_id: tutorId,
      },
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
    return apiClient.get(`/scheduling/availability/${tutorId}`);
  },

  createAvailability: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        availability_id: Math.floor(Math.random() * 100000),
        ...data,
      });
    }
    return apiClient.post("/scheduling/availability", data);
  },

  updateAvailability: (availabilityId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        availability_id: availabilityId,
        ...data,
      });
    }
    return apiClient.put(`/scheduling/availability/${availabilityId}`, data);
  },

  deleteAvailability: (availabilityId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Availability removed" });
    }
    return apiClient.delete(`/scheduling/availability/${availabilityId}`);
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
    return apiClient.post("/scheduling/find-slots", data);
  },

  scheduleSession: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({
        session_id: Math.floor(Math.random() * 100000),
        ...data,
        message: "Session scheduled",
      });
    }
    return apiClient.post("/scheduling/sessions", data);
  },

  rescheduleSession: (sessionId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Session rescheduled", session_id: sessionId, ...data });
    }
    return apiClient.put(
      `/scheduling/sessions/${sessionId}/reschedule`,
      data
    );
  },

  cancelSession: (sessionId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Session cancelled", session_id: sessionId });
    }
    return apiClient.delete(`/scheduling/sessions/${sessionId}`);
  },
};

// Reports API
export const reportsApi = {
  getCourseReports: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse({ reports: [] });
    }
    return apiClient.get("/reports/courses", { params });
  },

  getAcademicReports: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse({ reports: [] });
    }
    return apiClient.get("/reports/academic", { params });
  },

  getTutorActivityReports: (params?: any) => {
    if (MOCK_MODE) {
      return mockResponse({ reports: [] });
    }
    return apiClient.get("/reports/tutor-activities", { params });
  },

  generateReport: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Report generated" });
    }
    return apiClient.post("/reports/generate", data);
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
    return apiClient.get("/admin/users", { params });
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
    return apiClient.get("/admin/stats");
  },

  updateUserRole: (userId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Role updated" });
    }
    return apiClient.put(`/admin/users/${userId}/role`, data);
  },

  getPendingRegistrations: () => {
    if (MOCK_MODE) {
      return mockResponse([]);
    }
    return apiClient.get("/admin/registrations");
  },

  approveRegistration: (registrationId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Registration approved" });
    }
    return apiClient.put(
      `/admin/registrations/${registrationId}/approve`
    );
  },

  deleteUser: (userId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "User deleted" });
    }
    return apiClient.delete(`/admin/users/${userId}`);
  },

  updateUser: (userId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "User updated" });
    }
    return apiClient.put(`/admin/users/${userId}`, data);
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
          title: 'PhiÃªn há»c sáº¯p diá»…n ra',
          message: 'Báº¡n cÃ³ phiÃªn há»c vÃ o ngÃ y mai',
          time: '2 giá» trÆ°á»›c',
          read: false
        }
      ]);
    }
    return apiClient.get("/notifications/", { params });
  },

  getUnreadCount: () => {
    if (MOCK_MODE) {
      return mockResponse({ unread_count: 5 });
    }
    return apiClient.get("/notifications/unread-count");
  },

  markAsRead: (notificationId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Marked as read" });
    }
    return apiClient.put(`/notifications/${notificationId}/read`);
  },

  markAllAsRead: () => {
    if (MOCK_MODE) {
      return mockResponse({ message: "All marked as read" });
    }
    return apiClient.put("/notifications/mark-all-read");
  },

  deleteReadNotifications: () => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Read notifications deleted" });
    }
    return apiClient.delete("/notifications/delete-read");
  },
};

// Forum API
export const forumApi = {
  getForums: () => {
    if (MOCK_MODE) {
      return mockResponse([]);
    }
    return apiClient.get("/forum/");
  },

  createForum: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Forum created" });
    }
    return apiClient.post("/forum/", data);
  },

  getForumPosts: (forumId: number) => {
    if (MOCK_MODE) {
      return mockResponse([]);
    }
    return apiClient.get(`/forum/${forumId}/posts`);
  },

  createPost: (forumId: number, data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Post created" });
    }
    return apiClient.post(`/forum/${forumId}/posts`, data);
  },

  createStudyGroup: (data: any) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Study group created" });
    }
    return apiClient.post("/forum/study-groups", data);
  },

  joinStudyGroup: (groupId: string) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Joined study group" });
    }
    return apiClient.post(`/study-groups/${groupId}/join`);
  },

  leaveStudyGroup: (groupId: string) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Left study group" });
    }
    return apiClient.post(`/study-groups/${groupId}/leave`);
  },
};

// Study Groups API
export const studyGroupsApi = {
  getMessages: (groupId: number, limit: number = 50) => {
    if (MOCK_MODE) {
      return mockResponse([]);
    }
    return apiClient.get(`/study-groups/${groupId}/messages`, { params: { limit } });
  },

  sendMessage: (groupId: number, messageText: string) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Message sent" });
    }
    return apiClient.post(`/study-groups/${groupId}/messages`, { message_text: messageText });
  },

  deleteMessage: (groupId: number, messageId: number) => {
    if (MOCK_MODE) {
      return mockResponse({ message: "Message deleted" });
    }
    return apiClient.delete(`/study-groups/${groupId}/messages/${messageId}`);
  },
};

// Courses API
export const coursesApi = {
  getMyCourses: (mode?: string) => {
    if (MOCK_MODE) {
      return mockResponse([
        {
          code: "CO3001",
          name: "Software Engineering",
          credits: 4
        }
      ]);
    }
    const params = mode ? { mode } : {};
    return apiClient.get("/courses/my-courses", { params });
  },

  getCourseInfo: (courseCode: string) => {
    if (MOCK_MODE) {
      return mockResponse({
        code: courseCode,
        name: "Mock Course",
        credits: 4
      });
    }
    return apiClient.get(`/courses/${courseCode}`);
  },

  getCourseByCode: (subjectId: string) => {
    if (MOCK_MODE) {
      return mockResponse({
        subject_id: parseInt(subjectId),
        subject_code: "MT1001",
        subject_name: "Mock Course",
        department: "KHMT",
        credits: 4
      });
    }
    return apiClient.get(`/courses/subjects/${subjectId}`);
  },

  getAllSubjects: () => {
    if (MOCK_MODE) {
      return mockResponse([
        { subject_id: 1, subject_code: "MT1001", subject_name: "Giải tích 1", department: "Toán", credits: 4 },
        { subject_id: 2, subject_code: "PH1001", subject_name: "Vật lý đại cương 1", department: "Vật lý", credits: 3 },
        { subject_id: 3, subject_code: "CO1001", subject_name: "Nhập môn lập trình", department: "KHMT", credits: 4 },
      ]);
    }
    return apiClient.get("/courses/subjects");
  },
};

// Coordinator API
export const coordinatorApi = {
  // Tutor Registration Approval
  getTutorRegistrations: (status: string = "pending", skip: number = 0, limit: number = 50) => {
    return apiClient.get("/coordinator/tutor-registrations", {
      params: { status_filter: status, skip, limit }
    });
  },

  getRegistrationSchedules: (registrationId: number) => {
    return apiClient.get(`/coordinator/tutor-registrations/${registrationId}/schedules`);
  },

  approveTutorRegistration: (registrationId: number, scheduleId?: number) => {
    return apiClient.put(`/coordinator/tutor-registrations/${registrationId}/approve`, {
      schedule_id: scheduleId
    });
  },

  rejectTutorRegistration: (registrationId: number, reason: string) => {
    return apiClient.put(`/coordinator/tutor-registrations/${registrationId}/reject`, null, {
      params: { reason }
    });
  },

  // Session Approval
  getPendingSessions: (skip: number = 0, limit: number = 50) => {
    return apiClient.get("/coordinator/sessions/pending", {
      params: { skip, limit }
    });
  },

  approveSession: (sessionId: number) => {
    return apiClient.put(`/coordinator/sessions/${sessionId}/approve`);
  },

  rejectSession: (sessionId: number, reason: string) => {
    return apiClient.put(`/coordinator/sessions/${sessionId}/reject`, null, {
      params: { reason }
    });
  },

  // Tutor Management & Reports
  getTutors: (skip: number = 0, limit: number = 50) => {
    return apiClient.get("/coordinator/tutors", {
      params: { skip, limit }
    });
  },

  searchTutors: (search: string, skip: number = 0, limit: number = 50) => {
    return apiClient.get("/coordinator/tutors", {
      params: { search, skip, limit }
    });
  },

  getTutorCourses: (tutorId: number) => {
    return apiClient.get(`/coordinator/tutors/${tutorId}/courses`);
  },

  getCourseDetails: (tutorId: number, subjectId: number) => {
    return apiClient.get(`/coordinator/tutors/${tutorId}/courses/${subjectId}/details`);
  },

  exportCourseReport: (tutorId: number, subjectId: number, format: string = 'csv') => {
    return apiClient.get(`/coordinator/tutors/${tutorId}/courses/${subjectId}/export`, {
      params: { format },
      responseType: format === 'csv' ? 'blob' : 'json'
    });
  },

  updateTutorRating: (tutorId: number) => {
    return apiClient.post(`/coordinator/tutors/${tutorId}/update-rating`);
  },

  updateAllTutorsRatings: () => {
    return apiClient.post("/coordinator/tutors/update-all-ratings");
  },
};

export default apiClient;

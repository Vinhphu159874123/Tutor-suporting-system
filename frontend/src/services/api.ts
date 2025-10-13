import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-storage');
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
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    return apiClient.post('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  
  register: (userData: any) => 
    apiClient.post('/api/v1/auth/register', userData),
  
  getProfile: (token?: string) => {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    return apiClient.get('/api/v1/auth/me', config);
  },
  
  logout: () => 
    apiClient.post('/api/v1/auth/logout'),
    
  refreshToken: () => 
    apiClient.post('/api/v1/auth/refresh-token'),
};

// Users API
export const usersApi = {
  getProfile: () => 
    apiClient.get('/api/v1/users/profile'),
    
  updateProfile: (userData: any) => 
    apiClient.put('/api/v1/users/profile', userData),
    
  getUsers: (params?: any) => 
    apiClient.get('/api/v1/users', { params }),
    
  getUser: (userId: number) => 
    apiClient.get(`/api/v1/users/${userId}`),
    
  deleteUser: (userId: number) => 
    apiClient.delete(`/api/v1/users/${userId}`),
};

// Tutors API
export const tutorsApi = {
  getTutors: () => 
    apiClient.get('/api/v1/tutors'),
    
  registerTutor: (data: any) => 
    apiClient.post('/api/v1/tutors/register', data),
    
  getTutorSessions: () => 
    apiClient.get('/api/v1/tutors/sessions'),
    
  setAvailability: (data: any) => 
    apiClient.post('/api/v1/tutors/availability', data),
};

// Students API
export const studentsApi = {
  getStudents: () => 
    apiClient.get('/api/v1/students'),
    
  registerStudent: (data: any) => 
    apiClient.post('/api/v1/students/register', data),
    
  getStudentSessions: () => 
    apiClient.get('/api/v1/students/sessions'),
    
  submitFeedback: (data: any) => 
    apiClient.post('/api/v1/students/feedback', data),
};

// Sessions API
export const sessionsApi = {
  getSessions: (params?: any) => 
    apiClient.get('/api/v1/sessions', { params }),
    
  createSession: (data: any) => 
    apiClient.post('/api/v1/sessions', data),
    
  getSession: (sessionId: number) => 
    apiClient.get(`/api/v1/sessions/${sessionId}`),
    
  updateSession: (sessionId: number, data: any) => 
    apiClient.put(`/api/v1/sessions/${sessionId}`, data),
    
  uploadMaterials: (sessionId: number, data: any) => 
    apiClient.post(`/api/v1/sessions/${sessionId}/materials`, data),
};

// Scheduling API
export const schedulingApi = {
  scheduleSession: (data: any) => 
    apiClient.post('/api/v1/scheduling/sessions', data),
    
  getAvailability: (params?: any) => 
    apiClient.get('/api/v1/scheduling/availability', { params }),
    
  rescheduleSession: (sessionId: number, data: any) => 
    apiClient.put(`/api/v1/scheduling/sessions/${sessionId}/reschedule`, data),
    
  cancelSession: (sessionId: number) => 
    apiClient.delete(`/api/v1/scheduling/sessions/${sessionId}`),
};

// Reports API
export const reportsApi = {
  getCourseReports: (params?: any) => 
    apiClient.get('/api/v1/reports/courses', { params }),
    
  getAcademicReports: (params?: any) => 
    apiClient.get('/api/v1/reports/academic', { params }),
    
  getTutorActivityReports: (params?: any) => 
    apiClient.get('/api/v1/reports/tutor-activities', { params }),
    
  generateReport: (data: any) => 
    apiClient.post('/api/v1/reports/generate', data),
};

// Admin API
export const adminApi = {
  getAllUsers: (params?: any) => 
    apiClient.get('/api/v1/admin/users', { params }),
    
  updateUserRole: (userId: number, data: any) => 
    apiClient.put(`/api/v1/admin/users/${userId}/role`, data),
    
  getPendingRegistrations: () => 
    apiClient.get('/api/v1/admin/registrations'),
    
  approveRegistration: (registrationId: number) => 
    apiClient.put(`/api/v1/admin/registrations/${registrationId}/approve`),
};

// Forum API
export const forumApi = {
  getForums: () => 
    apiClient.get('/api/v1/forum'),
    
  createForum: (data: any) => 
    apiClient.post('/api/v1/forum', data),
    
  getForumPosts: (forumId: number) => 
    apiClient.get(`/api/v1/forum/${forumId}/posts`),
    
  createPost: (forumId: number, data: any) => 
    apiClient.post(`/api/v1/forum/${forumId}/posts`, data),
    
  createStudyGroup: (data: any) => 
    apiClient.post('/api/v1/forum/study-groups', data),
};

export default apiClient;
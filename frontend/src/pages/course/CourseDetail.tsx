import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  BookOpen, ArrowLeft, Clock, MapPin, Video, 
  FileText, Edit2, Save, X, ChevronDown, ChevronUp, Upload, Trash2, Calendar as CalendarIcon,
  Star, Users, MessageSquare, CheckCircle
} from 'lucide-react';
import { coursesApi, tutorsApi, sessionsApi } from '../../services/api';
import { useAuthStore } from '../../stores/authStore';
import { toast } from 'react-toastify';

interface CourseDetail {
  subject_id: number;
  subject_code: string;
  subject_name: string;
  department: string;
  credits: number;
  tutor_name?: string;
  tutor_id?: number;
}

interface WeeklySession {
  session_id?: number;  // Real DB session ID
  session_number: number;
  day: string;
  day_name: string;
  time_slots: string[];
  date?: Date;
  meeting_link: string;
  location: string;
  materials: string[];
  description: string;
}

const CourseDetail: React.FC = () => {
  const { subjectId } = useParams<{ subjectId: string }>();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [sessions, setSessions] = useState<WeeklySession[]>([]);
  const [expandedSession, setExpandedSession] = useState<number | null>(null);
  const [editingSession, setEditingSession] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Feedback modal state
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [selectedSessionForFeedback, setSelectedSessionForFeedback] = useState<number | null>(null);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [feedbackAnonymous, setFeedbackAnonymous] = useState(false);
  const [sessionFeedbacks, setSessionFeedbacks] = useState<Record<number, any>>({});  // Track feedbacks by session_id
  
  // Attendance modal state
  const [showAttendanceModal, setShowAttendanceModal] = useState(false);
  const [selectedSessionForAttendance, setSelectedSessionForAttendance] = useState<number | null>(null);
  const [participants, setParticipants] = useState<any[]>([]);
  const [attendanceData, setAttendanceData] = useState<Record<string, boolean>>({});
  
  // Enrolled students modal state
  const [showEnrolledStudentsModal, setShowEnrolledStudentsModal] = useState(false);
  const [enrolledStudents, setEnrolledStudents] = useState<any[]>([]);
  
  // PDF preview modal state
  const [showPdfPreview, setShowPdfPreview] = useState(false);
  const [previewPdfUrl, setPreviewPdfUrl] = useState<string | null>(null);
  const [previewPdfName, setPreviewPdfName] = useState<string>('');
  
  const { user } = useAuthStore();

  useEffect(() => {
    if (subjectId) {
      fetchCourseData();
    }
  }, [subjectId]);

  const fetchCourseData = async () => {
    if (!subjectId) return;
    
    try {
      setLoading(true);
      // Fetch course details
      const courseResponse = await coursesApi.getCourseByCode(subjectId) as any;
      setCourse(courseResponse.data);

      // Get current user's tutor_id if they are a tutor
      let currentUserTutorId: number | null = null;
      if (user?.role === 'tutor') {
        try {
          const tutorResponse = await tutorsApi.getMyTutorProfile() as any;
          currentUserTutorId = tutorResponse.data?.tutor_id;
        } catch (err) {
          console.log('Could not fetch tutor profile');
        }
      } else if (user?.role === 'student') {
        // For students, get the tutor_id and tutor_name from their enrolled sessions
        try {
          const myCoursesResponse = await coursesApi.getMyCourses() as any;
          const enrolledCourse = myCoursesResponse.data?.find((c: any) => c.subject_id === parseInt(subjectId));
          if (enrolledCourse?.tutor_id) {
            const tutorId = enrolledCourse.tutor_id;
            currentUserTutorId = tutorId;
            
            // Fetch tutor details to get name
            try {
              const tutorDetailResponse = await tutorsApi.getTutor(tutorId) as any;
              if (tutorDetailResponse.data) {
                setCourse(prev => prev ? {
                  ...prev,
                  tutor_name: tutorDetailResponse.data.user?.full_name || tutorDetailResponse.data.full_name,
                  tutor_id: tutorId
                } : prev);
              }
            } catch (err) {
              console.log('Could not fetch tutor details');
            }
          }
        } catch (err) {
          console.log('Could not fetch enrolled course info');
        }
      }

      // Step 1: Try to fetch saved sessions from database first
      try {
        // Call the sessions API to get sessions for this subject
        const params: any = { subject_id: parseInt(subjectId) };
        
        // Filter by tutor_id for both tutors and students
        if (currentUserTutorId) {
          params.tutor_id = currentUserTutorId;
        }
        
        const sessionsResponse = await sessionsApi.getSessions(params) as any;
        const savedSessions = sessionsResponse.data || [];
        
        console.log('Fetched sessions from DB:', savedSessions);
        console.log('Filter params:', params);
        
        if (savedSessions.length > 0) {
          // Convert DB sessions to WeeklySession format
          const convertedSessions: WeeklySession[] = savedSessions.map((s: any, index: number) => ({
            session_id: s.session_id,  // Save real DB session_id
            session_number: index + 1,
            day: new Date(s.scheduled_date).toLocaleDateString('vi-VN', { weekday: 'long' }),
            day_name: new Date(s.scheduled_date).toLocaleDateString('vi-VN', { weekday: 'long' }),
            time_slots: [`${s.start_time}-${s.end_time}`],
            date: new Date(s.scheduled_date),
            meeting_link: s.meeting_link || '',
            location: s.physical_address || (s.location_type === 'online' ? 'Online' : ''),
            materials: s.materials || [],
            description: s.description || ''
          }));
          
          setSessions(convertedSessions);
          console.log('✅ Loaded saved sessions from database');
          
          // Load existing feedbacks for student
          if (user?.role === 'student') {
            await loadSessionFeedbacks(convertedSessions);
          }
          
          setLoading(false);
          return; // Exit early if we have saved sessions
        }
      } catch (sessionError) {
        console.log('No saved sessions found, will generate from availability');
      }

      // Step 2: If no saved sessions, try to fetch tutor's registrations and generate
      try {
        const registrationsResponse = await tutorsApi.getMyRegistrations('approved') as any;
        const myRegistration = registrationsResponse.data.find((r: any) => 
          r.subject_id === parseInt(subjectId)
        );

        if (myRegistration) {
          generateSessionsFromAvailability(myRegistration);
        } else {
          // Fallback to mock data if no registration found
          console.log('No registration found, using mock data');
          generateSessionsFromAvailability({
            total_sessions: 12,
            start_date: '2025-01-06',
            availability: {
              monday: ['07:00-09:00', '13:00-15:00'],
              wednesday: ['09:00-11:00'],
              friday: ['15:00-17:00']
            }
          });
        }
      } catch (regError) {
        console.error('Failed to fetch registrations, using mock data:', regError);
        // Fallback to mock data if API fails
        generateSessionsFromAvailability({
          total_sessions: 12,
          start_date: '2025-01-06',
          availability: {
            monday: ['07:00-09:00', '13:00-15:00'],
            wednesday: ['09:00-11:00'],
            friday: ['15:00-17:00']
          }
        });
      }
    } catch (error) {
      console.error('Failed to fetch course data:', error);
      toast.error('Không thể tải thông tin môn học');
    } finally {
      setLoading(false);
    }
  };

  const generateSessionsFromAvailability = (reg: any) => {
    console.log('=== REGISTRATION DATA ===');
    console.log('Registration:', reg);
    console.log('Availability:', reg.availability);
    console.log('Total Sessions:', reg.total_sessions);
    console.log('Start Date:', reg.start_date);
    
    const availability = reg.availability || {};
    const totalSessions = reg.total_sessions || 10;
    const startDate = reg.start_date ? new Date(reg.start_date) : new Date();
    
    console.log('Parsed Start Date:', startDate);
    
    const dayMap: { [key: string]: number } = {
      'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4,
      'friday': 5, 'saturday': 6, 'sunday': 0
    };

    const dayNames: { [key: string]: string } = {
      'monday': 'Thứ Hai', 'tuesday': 'Thứ Ba', 'wednesday': 'Thứ Tư',
      'thursday': 'Thứ Năm', 'friday': 'Thứ Sáu', 'saturday': 'Thứ Bảy',
      'sunday': 'Chủ Nhật'
    };

    // Get all days with time slots and pick the first one for weekly schedule
    const daySlots: Array<{day: string, dayName: string, dayNum: number, slots: string[]}> = [];
    Object.entries(availability).forEach(([day, slots]) => {
      if (Array.isArray(slots) && slots.length > 0) {
        daySlots.push({ day, dayName: dayNames[day], dayNum: dayMap[day], slots: slots as string[] });
      }
    });

    if (daySlots.length === 0) {
      console.warn('No availability found');
      setSessions([]);
      return;
    }

    // Sort by day number and pick the first day for weekly sessions
    daySlots.sort((a, b) => a.dayNum - b.dayNum);
    const primaryDay = daySlots[0]; // Use first available day as the weekly session day

    console.log('Primary Day:', primaryDay);
    console.log('All Day Slots:', daySlots);

    // Generate sessions - one per week on the same day
    const generatedSessions: WeeklySession[] = [];
    let currentDate = new Date(startDate);

    // Calculate the first session date (next occurrence of the primary day)
    const startDayOfWeek = currentDate.getDay();
    const targetDay = primaryDay.dayNum;
    let daysUntilFirst = (targetDay - startDayOfWeek + 7) % 7;
    if (daysUntilFirst === 0 && currentDate > startDate) {
      daysUntilFirst = 7; // If same day but past time, go to next week
    }
    
    console.log('Start Day of Week:', startDayOfWeek);
    console.log('Target Day:', targetDay);
    console.log('Days Until First Session:', daysUntilFirst);
    
    currentDate.setDate(currentDate.getDate() + daysUntilFirst);
    console.log('First Session Date:', currentDate);

    // Generate totalSessions sessions, one per week
    for (let i = 0; i < totalSessions; i++) {
      const sessionDate = new Date(currentDate);
      
      generatedSessions.push({
        session_number: i + 1,
        day: primaryDay.day,
        day_name: primaryDay.dayName,
        time_slots: primaryDay.slots,
        date: sessionDate,
        meeting_link: '',
        location: 'Online',
        materials: [],
        description: ''
      });

      // Move to next week (same day)
      currentDate.setDate(currentDate.getDate() + 7);
    }

    setSessions(generatedSessions);
  };

  const handleUpdateSession = (sessionNum: number, field: string, value: string) => {
    setSessions(prev => prev.map(s => 
      s.session_number === sessionNum ? { ...s, [field]: value } : s
    ));
  };

  const handleSaveSession = (sessionNum: number) => {
    setEditingSession(null);
    toast.info('Nhớ nhấn "Lưu tất cả" để lưu thay đổi vào hệ thống');
  };

  const handleSaveAllSessions = async () => {
    if (!subjectId) return;
    
    try {
      setLoading(true);
      
      // Prepare sessions data for API
      const sessionsData = sessions.map(s => ({
        session_number: s.session_number,
        date: s.date?.toISOString(),
        time_slots: s.time_slots,
        meeting_link: s.meeting_link,
        location: s.location,
        description: s.description,
        materials: s.materials
      }));

      // Call API to save all sessions using apiClient with proper auth
      await sessionsApi.bulkSaveForSubject(parseInt(subjectId), sessionsData);

      toast.success('Đã lưu tất cả các buổi học!');
    } catch (error) {
      console.error('Failed to save sessions:', error);
      toast.error('Không thể lưu buổi học');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (sessionNum: number, event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const session = sessions.find(s => s.session_number === sessionNum);
    if (!session || !session.session_id) {
      toast.error('Vui lòng lưu buổi học trước khi upload tài liệu');
      return;
    }

    const userId = user?.user_id || (user as any)?.id;
    if (!userId) {
      console.error('User object:', user);
      toast.error('Vui lòng đăng nhập lại');
      return;
    }

    try {
      // Upload each file to server
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('uploaded_by', userId.toString());
        
        await sessionsApi.uploadMaterials(session.session_id, formData);
      }

      // Add filenames to local state
      const fileNames = Array.from(files).map(f => f.name);
      setSessions(prev => prev.map(s => 
        s.session_number === sessionNum 
          ? { ...s, materials: [...s.materials, ...fileNames] } 
          : s
      ));
      
      toast.success(`Đã upload ${files.length} tài liệu thành công!`);
    } catch (error: any) {
      console.error('Upload error:', error);
      console.error('Error response:', error.response?.data);
      toast.error(error.response?.data?.detail || 'Không thể upload tài liệu');
    }
  };

  const handleRemoveMaterial = async (sessionNum: number, materialIndex: number) => {
    const session = sessions.find(s => s.session_number === sessionNum);
    const materialName = session?.materials[materialIndex];
    if (!materialName) return;

    // If session not saved yet, just remove from local state
    if (!session.session_id) {
      setSessions(prev => prev.map(s => 
        s.session_number === sessionNum 
          ? { ...s, materials: s.materials.filter((_, idx) => idx !== materialIndex) } 
          : s
      ));
      toast.success('Đã xóa tài liệu');
      return;
    }

    try {
      // Try to delete from server
      await sessionsApi.deleteMaterial(session.session_id, materialName);
      
      // Remove from local state
      setSessions(prev => prev.map(s => 
        s.session_number === sessionNum 
          ? { ...s, materials: s.materials.filter((_, idx) => idx !== materialIndex) } 
          : s
      ));
      
      toast.success('Đã xóa tài liệu');
    } catch (error: any) {
      console.error('Delete error:', error);
      
      // If 404, file doesn't exist on server - just remove from UI
      if (error.response?.status === 404) {
        setSessions(prev => prev.map(s => 
          s.session_number === sessionNum 
            ? { ...s, materials: s.materials.filter((_, idx) => idx !== materialIndex) } 
            : s
        ));
        toast.success('Đã xóa tài liệu (chỉ trong UI)');
      } else {
        toast.error(error.response?.data?.detail || 'Không thể xóa tài liệu');
      }
    }
  };

  // Download material with authentication
  const handleDownloadMaterial = async (sessionId: number, materialName: string) => {
    try {
      // For PDFs, try to open backend URL directly in new tab
      // Browser will use existing auth cookies/session
      if (materialName.toLowerCase().endsWith('.pdf')) {
        const backendUrl = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/sessions/${sessionId}/materials/${encodeURIComponent(materialName)}/download`;
        
        // Open directly - browser handles PDF rendering
        window.open(backendUrl, '_blank');
        toast.success('Đang mở PDF...');
        return;
      }

      // For non-PDF files, download with auth
      const token = localStorage.getItem('auth-storage');
      let authToken = '';
      
      if (token) {
        const parsed = JSON.parse(token);
        authToken = parsed.state?.token || '';
      }

      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/sessions/${sessionId}/materials/${materialName}/download`,
        {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to download file');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = materialName;
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }, 100);
      
      toast.success(`Đã tải xuống ${materialName}`);
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Không thể tải xuống tài liệu');
    }
  };

  const handleClosePdfPreview = () => {
    // No need to revoke if using base64 data URL
    setShowPdfPreview(false);
    setPreviewPdfUrl(null);
    setPreviewPdfName('');
  };

  const handleDownloadFromPreview = () => {
    if (previewPdfUrl && previewPdfName) {
      const a = document.createElement('a');
      a.href = previewPdfUrl;
      a.download = previewPdfName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      toast.success('Đang tải xuống...');
    }
  };

  // Load feedbacks for all sessions - OPTIMIZED with single API call
  const loadSessionFeedbacks = async (sessions: WeeklySession[]) => {
    const sessionIds = sessions
      .filter(s => s.session_id)
      .map(s => s.session_id)
      .join(',');
    
    if (!sessionIds) {
      setSessionFeedbacks({});
      return;
    }
    
    try {
      const response = await sessionsApi.getBulkFeedbacks(sessionIds) as any;
      const feedbacksMap: Record<number, any> = {};
      
      // Response is already a map: { session_id: [feedback1, feedback2] }
      const data = response.data || {};
      
      // For students, they only see their own feedback (first in array)
      Object.keys(data).forEach(sessionId => {
        const feedbacks = data[sessionId];
        if (feedbacks && feedbacks.length > 0) {
          feedbacksMap[parseInt(sessionId)] = feedbacks[0];
        }
      });
      
      setSessionFeedbacks(feedbacksMap);
    } catch (err) {
      console.error('Failed to load feedbacks:', err);
      setSessionFeedbacks({});
    }
  };

  // Enrolled students handler
  const handleViewEnrolledStudents = async () => {
    try {
      const response = await tutorsApi.getEnrolledStudents() as any;
      // The API returns { data: courses }, and courses is an array
      const courses = response.data?.data || response.data || [];
      
      // Ensure courses is an array
      const coursesList = Array.isArray(courses) ? courses : [];
      
      // Find the current course
      const currentCourse = coursesList.find((c: any) => c.subject_id === parseInt(subjectId || '0'));
      
      if (currentCourse && currentCourse.students && currentCourse.students.length > 0) {
        setEnrolledStudents(currentCourse.students);
        setShowEnrolledStudentsModal(true);
      } else {
        toast.info('Chưa có học sinh nào đăng ký khóa học này');
      }
    } catch (error) {
      console.error('Error fetching enrolled students:', error);
      toast.error('Không thể tải danh sách học sinh');
    }
  };

  // Feedback handlers
  const handleOpenFeedback = (sessionId: number) => {
    setSelectedSessionForFeedback(sessionId);
    setFeedbackRating(0);
    setFeedbackComment('');
    setFeedbackAnonymous(false);
    setShowFeedbackModal(true);
  };

  const handleSubmitFeedback = async () => {
    if (feedbackRating === 0) {
      toast.error('Vui lòng chọn số sao đánh giá');
      return;
    }

    if (!selectedSessionForFeedback) {
      toast.error('Không tìm thấy session');
      return;
    }

    console.log('Submitting feedback for session:', selectedSessionForFeedback);
    console.log('Feedback data:', { rating: feedbackRating, comment: feedbackComment, is_anonymous: feedbackAnonymous });

    try {
      const response = await sessionsApi.submitFeedback(selectedSessionForFeedback, {
        rating: feedbackRating,
        comment: feedbackComment,
        is_anonymous: feedbackAnonymous
      });
      console.log('Feedback response:', response);
      toast.success('Đã gửi đánh giá thành công!');
      
      // Reload feedback for this session
      try {
        const feedbackResponse = await sessionsApi.getFeedback(selectedSessionForFeedback) as any;
        if (feedbackResponse.data && feedbackResponse.data.length > 0) {
          setSessionFeedbacks(prev => ({
            ...prev,
            [selectedSessionForFeedback]: feedbackResponse.data[0]
          }));
        }
      } catch (err) {
        console.log('Could not reload feedback');
      }
      
      setShowFeedbackModal(false);
    } catch (error: any) {
      console.error('Error submitting feedback:', error);
      console.error('Error response:', error.response?.data);
      toast.error(error.response?.data?.detail || 'Không thể gửi đánh giá');
    }
  };

  // Attendance handlers
  const handleOpenAttendance = async (sessionId: number) => {
    if (!sessionId) {
      toast.error('Không tìm thấy session');
      return;
    }
    setSelectedSessionForAttendance(sessionId);
    try {
      const response = await sessionsApi.getParticipants(sessionId) as any;
      const participantsList = response.data || [];
      setParticipants(participantsList);
      
      // Initialize attendance data
      const initialAttendance: Record<string, boolean> = {};
      participantsList.forEach((p: any) => {
        initialAttendance[p.user_id] = p.attended || false;
      });
      setAttendanceData(initialAttendance);
      setShowAttendanceModal(true);
    } catch (error) {
      console.error('Error loading participants:', error);
      toast.error('Không thể tải danh sách sinh viên');
    }
  };

  const handleToggleAttendance = (userId: string) => {
    setAttendanceData(prev => ({
      ...prev,
      [userId]: !prev[userId]
    }));
  };

  const handleSaveAttendance = async () => {
    if (!selectedSessionForAttendance) {
      toast.error('Không tìm thấy session');
      return;
    }
    try {
      await sessionsApi.markAttendance(selectedSessionForAttendance, attendanceData);
      toast.success('Đã lưu điểm danh thành công!');
      setShowAttendanceModal(false);
    } catch (error) {
      console.error('Error saving attendance:', error);
      toast.error('Không thể lưu điểm danh');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Không tìm thấy môn học</p>
        <Link to="/my-courses" className="text-blue-600 hover:underline mt-4 inline-block">
          Quay lại
        </Link>
      </div>
    );
  }

  const isTutor = user?.role === 'tutor';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <Link to="/my-courses" className="inline-flex items-center gap-2 text-blue-100 hover:text-white mb-4">
          <ArrowLeft className="h-5 w-5" />
          Quay lại
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="px-3 py-1 bg-white/20 text-white text-sm font-medium rounded-full">
                {course.subject_code}
              </span>
              <span className="text-sm text-blue-100">{course.credits} tín chỉ</span>
            </div>
            <h1 className="text-3xl font-bold mb-2">{course.subject_name}</h1>
            <p className="text-blue-100">Khoa: {course.department}</p>
            {course.tutor_name && (
              <p className="text-blue-100 mt-1">
                <span className="font-medium">Giáo viên:</span> {course.tutor_name}
              </p>
            )}
          </div>
          <BookOpen className="h-12 w-12 opacity-50" />
        </div>
      </div>

      {/* Sessions List */}
      <div className="card">
        <div className="border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Danh sách buổi học ({sessions.length} buổi)</h2>
              <p className="text-sm text-gray-600 mt-1">
                {isTutor ? 'Quản lý thông tin từng buổi học' : 'Xem lịch học và tham gia các buổi học'}
              </p>
            </div>
            {isTutor && sessions.length > 0 && (
              <div className="flex gap-3">
                <button
                  onClick={handleViewEnrolledStudents}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <Users className="h-4 w-4" />
                  Xem danh sách học sinh
                </button>
                <button
                  onClick={handleSaveAllSessions}
                  disabled={loading}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                >
                  <Save className="h-4 w-4" />
                  Lưu tất cả
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="p-6 space-y-3">
          {sessions.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Chưa có buổi học nào được tạo</p>
            </div>
          ) : (
            sessions.map((session) => {
              const isExpanded = expandedSession === session.session_number;
              const isEditing = editingSession === session.session_number;
              
              return (
                <div key={session.session_number} className="border-2 border-gray-200 rounded-lg overflow-hidden">
                  {/* Session Header */}
                  <div 
                    className="p-4 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => setExpandedSession(isExpanded ? null : session.session_number)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-bold text-blue-600">
                            Session {session.session_number}
                          </h3>
                          <span className="text-sm text-gray-600">
                            {session.day_name}
                          </span>
                          <span className="text-sm font-medium text-gray-700">
                            {session.time_slots.join(', ')}
                          </span>
                        </div>
                        {session.date && (
                          <p className="text-sm text-gray-600 flex items-center gap-1">
                            <CalendarIcon className="w-4 h-4" />
                            {session.date.toLocaleDateString('vi-VN', {
                              day: '2-digit',
                              month: '2-digit',
                              year: 'numeric'
                            })}
                          </p>
                        )}
                      </div>
                      {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                    </div>
                  </div>

                  {/* Session Details (Expanded) */}
                  {isExpanded && (
                    <div className="p-6 border-t border-gray-200 bg-white">
                      {isEditing ? (
                        /* Edit Mode */
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Link Google Meet
                            </label>
                            <input
                              type="url"
                              value={session.meeting_link}
                              onChange={(e) => handleUpdateSession(session.session_number, 'meeting_link', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md"
                              placeholder="https://meet.google.com/xxx-xxxx-xxx"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Địa điểm
                            </label>
                            <input
                              type="text"
                              value={session.location}
                              onChange={(e) => handleUpdateSession(session.session_number, 'location', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md"
                              placeholder="Online, H1-101, ..."
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Mô tả buổi học
                            </label>
                            <textarea
                              value={session.description}
                              onChange={(e) => handleUpdateSession(session.session_number, 'description', e.target.value)}
                              rows={3}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md"
                              placeholder="Nội dung buổi học, yêu cầu chuẩn bị..."
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Tài liệu học tập
                            </label>
                            <div className="space-y-2">
                              {session.materials.length > 0 && (
                                <div className="space-y-2 mb-3">
                                  {session.materials.map((material, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded border border-gray-200">
                                      <div className="flex items-center gap-2">
                                        <FileText className="h-4 w-4 text-gray-500" />
                                        <span className="text-sm">{material}</span>
                                      </div>
                                      <button
                                        onClick={() => handleRemoveMaterial(session.session_number, idx)}
                                        className="text-red-600 hover:text-red-800"
                                      >
                                        <Trash2 className="h-4 w-4" />
                                      </button>
                                    </div>
                                  ))}
                                </div>
                              )}
                              <label className="flex items-center justify-center gap-2 px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors">
                                <Upload className="h-4 w-4 text-gray-500" />
                                <span className="text-sm text-gray-600">Tải lên tài liệu</span>
                                <input
                                  type="file"
                                  multiple
                                  className="hidden"
                                  onChange={(e) => handleFileUpload(session.session_number, e)}
                                  accept=".pdf,.doc,.docx,.ppt,.pptx,.txt"
                                />
                              </label>
                            </div>
                          </div>

                          <div className="flex gap-2 justify-end">
                            <button
                              onClick={() => setEditingSession(null)}
                              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                            >
                              <X className="h-4 w-4 inline mr-1" />
                              Hủy
                            </button>
                            <button
                              onClick={() => handleSaveSession(session.session_number)}
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                              <Save className="h-4 w-4 inline mr-1" />
                              Lưu
                            </button>
                          </div>
                        </div>
                      ) : (
                        /* View Mode */
                        <div className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="flex items-start gap-3">
                              <Clock className="h-5 w-5 text-gray-500 mt-0.5" />
                              <div>
                                <p className="text-sm text-gray-600">Thời gian</p>
                                <p className="font-medium">{session.time_slots.join(', ')}</p>
                              </div>
                            </div>

                            <div className="flex items-start gap-3">
                              <MapPin className="h-5 w-5 text-gray-500 mt-0.5" />
                              <div>
                                <p className="text-sm text-gray-600">Địa điểm</p>
                                <p className="font-medium">{session.location || 'Chưa cập nhật'}</p>
                              </div>
                            </div>
                          </div>

                          {session.meeting_link && (
                            <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                              <Video className="h-5 w-5 text-blue-600 mt-0.5" />
                              <div className="flex-1">
                                <p className="text-sm text-gray-600">Link tham gia</p>
                                <a 
                                  href={session.meeting_link} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-blue-600 hover:underline font-medium break-all"
                                >
                                  {session.meeting_link}
                                </a>
                              </div>
                            </div>
                          )}

                          {session.description && (
                            <div className="flex items-start gap-3">
                              <FileText className="h-5 w-5 text-gray-500 mt-0.5" />
                              <div>
                                <p className="text-sm text-gray-600">Mô tả</p>
                                <p className="text-gray-900">{session.description}</p>
                              </div>
                            </div>
                          )}

                          {session.materials.length > 0 && (
                            <div>
                              <p className="text-sm text-gray-600 mb-2">Tài liệu</p>
                              <div className="space-y-2">
                                {session.materials.map((material, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => handleDownloadMaterial(session.session_id!, material)}
                                    className="w-full flex items-center gap-2 p-2 bg-gray-50 rounded hover:bg-blue-50 transition-colors group text-left"
                                  >
                                    <FileText className="h-4 w-4 text-gray-500 group-hover:text-blue-600" />
                                    <span className="text-sm text-gray-700 group-hover:text-blue-600 underline">{material}</span>
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}

                          {isTutor && (
                            <div className="pt-4 border-t border-gray-200 flex gap-3">
                              <button
                                onClick={() => setEditingSession(session.session_number)}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                              >
                                <Edit2 className="h-4 w-4" />
                                Chỉnh sửa
                              </button>
                              {session.session_id && (
                                <button
                                  onClick={() => handleOpenAttendance(session.session_id!)}
                                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                                >
                                  <Users className="h-4 w-4" />
                                  Điểm danh
                                </button>
                              )}
                            </div>
                          )}

                          {!isTutor && session.session_id && (
                            <div className="pt-4 border-t border-gray-200">
                              {session.session_id && sessionFeedbacks[session.session_id] ? (
                                <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                                  <div className="flex items-center gap-2 mb-2">
                                    <div className="flex gap-1">
                                      {[1, 2, 3, 4, 5].map((star) => (
                                        <Star
                                          key={star}
                                          className={`h-5 w-5 ${
                                            star <= sessionFeedbacks[session.session_id!].rating
                                              ? 'fill-yellow-500 text-yellow-500'
                                              : 'text-gray-300'
                                          }`}
                                        />
                                      ))}
                                    </div>
                                    <span className="text-sm font-medium text-gray-700">
                                      Bạn đã đánh giá {sessionFeedbacks[session.session_id!].rating} sao
                                    </span>
                                  </div>
                                  {sessionFeedbacks[session.session_id!].comment && (
                                    <p className="text-sm text-gray-600 italic">
                                      "{sessionFeedbacks[session.session_id!].comment}"
                                    </p>
                                  )}
                                  {sessionFeedbacks[session.session_id!].is_anonymous && (
                                    <p className="text-xs text-gray-500 mt-2">Đánh giá ẩn danh</p>
                                  )}
                                </div>
                              ) : (
                                <button
                                  onClick={() => handleOpenFeedback(session.session_id!)}
                                  className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 flex items-center gap-2"
                                >
                                  <Star className="h-4 w-4" />
                                  Đánh giá buổi học
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-bold mb-4">Đánh giá buổi học</h3>
            
            {/* Rating Stars */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Đánh giá của bạn
              </label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setFeedbackRating(star)}
                    className="focus:outline-none"
                  >
                    <Star
                      className={`h-8 w-8 ${
                        star <= feedbackRating
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  </button>
                ))}
              </div>
            </div>

            {/* Comment */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nhận xét (không bắt buộc)
              </label>
              <textarea
                value={feedbackComment}
                onChange={(e) => setFeedbackComment(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Chia sẻ trải nghiệm của bạn về buổi học..."
              />
            </div>

            {/* Anonymous checkbox */}
            <div className="mb-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={feedbackAnonymous}
                  onChange={(e) => setFeedbackAnonymous(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Gửi đánh giá ẩn danh</span>
              </label>
            </div>

            {/* Actions */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowFeedbackModal(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Hủy
              </button>
              <button
                onClick={handleSubmitFeedback}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <CheckCircle className="h-4 w-4" />
                Gửi đánh giá
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Attendance Modal */}
      {showAttendanceModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[80vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">Điểm danh buổi học</h3>
            
            {participants.length === 0 ? (
              <p className="text-gray-600 text-center py-8">Chưa có sinh viên đăng ký</p>
            ) : (
              <div className="space-y-2 mb-6">
                {participants.map((participant) => (
                  <div
                    key={participant.user_id}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{participant.full_name}</p>
                      <p className="text-sm text-gray-600">{participant.email}</p>
                    </div>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={attendanceData[participant.user_id] || false}
                        onChange={() => handleToggleAttendance(participant.user_id.toString())}
                        className="w-5 h-5 text-green-600 rounded focus:ring-2 focus:ring-green-500"
                      />
                      <span className={`text-sm font-medium ${
                        attendanceData[participant.user_id] ? 'text-green-600' : 'text-gray-400'
                      }`}>
                        {attendanceData[participant.user_id] ? 'Có mặt' : 'Vắng'}
                      </span>
                    </label>
                  </div>
                ))}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 justify-end border-t border-gray-200 pt-4">
              <button
                onClick={() => setShowAttendanceModal(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Hủy
              </button>
              <button
                onClick={handleSaveAttendance}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <CheckCircle className="h-4 w-4" />
                Lưu điểm danh
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Enrolled Students Modal */}
      {showEnrolledStudentsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Users className="h-6 w-6 text-blue-600" />
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">Danh sách học sinh</h2>
                    <p className="text-sm text-gray-600">{enrolledStudents.length} học sinh đã đăng ký</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowEnrolledStudentsModal(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="p-6">
              {enrolledStudents.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Chưa có học sinh nào đăng ký khóa học này</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {enrolledStudents.map((student, index) => (
                    <div
                      key={student.user_id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-semibold">{index + 1}</span>
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{student.full_name}</h3>
                          <p className="text-sm text-gray-600">{student.email}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <CalendarIcon className="h-4 w-4" />
                          <span>{student.sessions_enrolled} buổi học</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4">
              <button
                onClick={() => setShowEnrolledStudentsModal(false)}
                className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* PDF Preview Modal */}
      {showPdfPreview && previewPdfUrl && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full h-full max-w-6xl max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">{previewPdfName}</h2>
              <div className="flex gap-3">
                <button
                  onClick={handleDownloadFromPreview}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <FileText className="h-4 w-4" />
                  Tải xuống
                </button>
                <button
                  onClick={handleClosePdfPreview}
                  className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
            <div className="flex-1 overflow-hidden">
              <iframe
                src={previewPdfUrl}
                className="w-full h-full border-0"
                title={previewPdfName}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseDetail;

import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  BookOpen, ArrowLeft, Clock, MapPin, Video,
  FileText, Edit2, Save, X, ChevronDown, ChevronUp, Upload, Trash2, Calendar as CalendarIcon,
  Star, Users, MessageSquare, CheckCircle
} from 'lucide-react';
import { coursesApi, tutorsApi, sessionsApi, studentsApi } from '../../services/api';
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
  const navigate = useNavigate();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [sessions, setSessions] = useState<WeeklySession[]>([]);
  const [sessionMaterials, setSessionMaterials] = useState<Record<number, any[]>>({});  // session_id -> materials[]
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
  const [attendanceData, setAttendanceData] = useState<Record<string, 'present' | 'absent' | 'late' | 'excused' | null>>({});

  // Enrolled students modal state
  const [showEnrolledStudentsModal, setShowEnrolledStudentsModal] = useState(false);
  const [enrolledStudents, setEnrolledStudents] = useState<any[]>([]);

  // Feedbacks summary modal state (for tutor)
  const [showFeedbacksModal, setShowFeedbacksModal] = useState(false);
  const [subjectFeedbacks, setSubjectFeedbacks] = useState<any>(null);
  const [loadingFeedbacks, setLoadingFeedbacks] = useState(false);

  // Student profile modal state (for tutor)
  const [showStudentProfileModal, setShowStudentProfileModal] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<any>(null);
  const [studentProfile, setStudentProfile] = useState<any>(null);
  const [studentCourses, setStudentCourses] = useState<any>(null);
  const [loadingStudentProfile, setLoadingStudentProfile] = useState(false);

  // PDF preview modal state
  const [showPdfPreview, setShowPdfPreview] = useState(false);
  const [previewPdfUrl, setPreviewPdfUrl] = useState<string | null>(null);
  const [previewPdfName, setPreviewPdfName] = useState<string>('');

  const { user } = useAuthStore();
  const hasFetched = useRef(false);
  const lastSubjectId = useRef<string | null>(null);
  const lastMode = useRef<string | null>(null);

  // Determine active mode (prioritize currentMode if available)
  const { currentMode } = useAuthStore();
  const activeMode = currentMode || (user?.role && user.role[0]) || 'student';  // role[0] is first role in array
  const isTutor = activeMode === 'tutor';

  // Debug log
  console.log('🔍 CourseDetail Mode Check:', {
    user: user?.email,
    userRole: user?.role,
    currentMode,
    activeMode,
    isTutor,
    availableRoles: user?.role  // role is now array of all roles
  });

  useEffect(() => {
    // Reset flag if subjectId changed OR mode changed
    if (subjectId !== lastSubjectId.current || activeMode !== lastMode.current) {
      console.log('🔄 Mode or Subject changed - resetting and refetching', {
        oldMode: lastMode.current,
        newMode: activeMode,
        oldSubject: lastSubjectId.current,
        newSubject: subjectId
      });
      hasFetched.current = false;
      lastSubjectId.current = subjectId || null;
      lastMode.current = activeMode;
    }

    if (subjectId && user && !hasFetched.current) {
      console.log('📡 Fetching course data...', { subjectId, activeMode });
      hasFetched.current = true;
      fetchCourseData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [subjectId, activeMode, user]); // Re-fetch when subjectId, activeMode, or user changes

  const fetchCourseData = async () => {
    if (!subjectId) return;

    try {
      setLoading(true);
      // Fetch course details
      const courseResponse = await coursesApi.getCourseByCode(subjectId) as any;
      let courseData = courseResponse.data;

      // Get current user's tutor_id if they are a tutor
      let currentUserTutorId: number | null = null;
      if (activeMode === 'tutor') {
        try {
          const tutorResponse = await tutorsApi.getMyTutorProfile() as any;
          currentUserTutorId = tutorResponse.data?.tutor_id;
          // Add tutor_id to course data
          if (currentUserTutorId) {
            courseData = { ...courseData, tutor_id: currentUserTutorId };
          }
        } catch (err) {
          console.log('Could not fetch tutor profile');
        }
      } else if (activeMode === 'student') {
        // For students, get the tutor_id and tutor_name from their enrolled sessions
        try {
          const myCoursesResponse = await coursesApi.getMyCourses(activeMode) as any;
          const enrolledCourse = myCoursesResponse.data?.find((c: any) => c.subject_id === parseInt(subjectId));
          if (enrolledCourse?.tutor_id) {
            const tutorId = enrolledCourse.tutor_id;
            currentUserTutorId = tutorId;

            // Fetch tutor details to get name
            try {
              const tutorDetailResponse = await tutorsApi.getTutor(tutorId) as any;
              if (tutorDetailResponse.data) {
                courseData = {
                  ...courseData,
                  tutor_name: tutorDetailResponse.data.user?.full_name || tutorDetailResponse.data.full_name,
                  tutor_id: tutorId
                };
              }
            } catch (err) {
              console.log('Could not fetch tutor details');
            }
          }
        } catch (err) {
          console.log('Could not fetch enrolled course info');
        }
      }

      // Set course data ONCE with all updates
      setCourse(courseData);

      // Step 1: Try to fetch saved sessions from database first
      try {
        // Call the sessions API to get sessions for this subject
        const params: any = { subject_id: parseInt(subjectId) };

        console.log('🔍 Checking user for session filter:', {
          user,
          role: activeMode,
          user_id: user?.user_id,
          currentUserTutorId
        });

        // IMPORTANT: Filter based on active mode
        if (activeMode === 'tutor' && currentUserTutorId) {
          // Tutor mode: Show sessions for this tutor
          params.tutor_id = currentUserTutorId;
          console.log('✅ Tutor mode - Using tutor_id filter:', currentUserTutorId);
        } else if (activeMode === 'student') {
          // Student mode: Show ALL sessions for the course (no student_id filter for now)
          if (currentUserTutorId) {
            params.tutor_id = currentUserTutorId;
            console.log('✅ Student mode - Using tutor_id filter:', currentUserTutorId);
          }

          // TEMPORARILY DISABLED - Show all sessions
          // if (user?.user_id) {
          //   params.student_id = user.user_id;
          //   console.log('✅ Student mode - Using student_id filter:', user.user_id);
          // }
          console.log('⚠️ Student mode - Showing ALL sessions (no student_id filter)');
        } else {
          console.log('⚠️ No tutor_id found - user may not be enrolled yet');
        }

        console.log('📤 API Request params:', JSON.stringify(params));
        const sessionsResponse = await sessionsApi.getSessions(params) as any;
        const savedSessions = sessionsResponse.data || [];

        console.log('📥 API Response - Fetched sessions count:', savedSessions.length);
        console.log('Filter params used:', params);

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

          // Load materials for all sessions in ONE call - OPTIMIZED
          const sessionIds = convertedSessions
            .filter(s => s.session_id)
            .map(s => s.session_id!);

          if (sessionIds.length > 0) {
            try {
              const materialsResponse: any = await sessionsApi.getBulkMaterials(sessionIds);
              const materialsData = materialsResponse.data || {};

              // Set materials for all sessions at once
              const materialsMap: { [key: number]: any[] } = {};
              for (const sessionId of sessionIds) {
                materialsMap[sessionId] = materialsData[sessionId] || [];
              }
              setSessionMaterials(materialsMap);
              console.log(`✅ Loaded materials for ${sessionIds.length} sessions in 1 request`);
            } catch (error) {
              console.error('Failed to load bulk materials:', error);
            }
          }

          // Load existing feedbacks for student
          if (activeMode === 'student') {
            await loadSessionFeedbacks(convertedSessions);
          }

          setLoading(false);
          return; // Exit early if we have saved sessions
        }
      } catch (sessionError) {
        console.log('No saved sessions found. Tutor needs to manually generate sessions.');
      }

      // Step 2: If no saved sessions, just show empty state
      // Tutor must click "Generate Sessions" button to create sessions
      console.log('✅ No sessions found - showing empty state with generate button');
      setSessions([]);
      setLoading(false);
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
    const daySlots: Array<{ day: string, dayName: string, dayNum: number, slots: string[] }> = [];
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

  const handleGenerateSessions = async () => {
    if (!subjectId) return;

    try {
      setLoading(true);

      // Call API to generate sessions
      const response = await tutorsApi.generateSessionsForCourse(parseInt(subjectId)) as any;

      toast.success(response.data?.message || 'Đã tạo lịch học thành công!');

      // Reload course data to show newly generated sessions
      await fetchCourseData();
    } catch (error: any) {
      console.error('Failed to generate sessions:', error);
      const errorMsg = error.response?.data?.detail || 'Không thể tạo lịch học';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAllSessions = async () => {
    if (!subjectId) return;

    // Prevent duplicate calls
    if (loading) {
      console.log('⚠️ Already saving, ignoring duplicate call');
      return;
    }

    console.log('🚀 handleSaveAllSessions called');

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

      console.log('📤 Calling bulkSaveForSubject with', sessionsData.length, 'sessions');

      // Call API to save all sessions using apiClient with proper auth
      await sessionsApi.bulkSaveForSubject(parseInt(subjectId), sessionsData);

      console.log('✅ Successfully saved all sessions');
      toast.success('Đã lưu tất cả các buổi học!');
    } catch (error) {
      console.error('❌ Failed to save sessions:', error);
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

      // Refresh materials list
      await fetchSessionMaterials(session.session_id);

      toast.success(`Đã upload ${files.length} tài liệu thành công!`);
    } catch (error: any) {
      console.error('Upload error:', error);
      console.error('Error response:', error.response?.data);
      toast.error(error.response?.data?.detail || 'Không thể upload tài liệu');
    }
  };

  // Fetch materials for a specific session
  const fetchSessionMaterials = async (sessionId: number) => {
    try {
      const response: any = await sessionsApi.getSessionMaterials(sessionId);
      setSessionMaterials(prev => ({
        ...prev,
        [sessionId]: response.data || []
      }));
    } catch (error: any) {
      console.error('Failed to fetch materials:', error);
    }
  };

  const handleRemoveMaterial = async (sessionNum: number, materialId: number) => {
    const session = sessions.find(s => s.session_number === sessionNum);
    if (!session?.session_id) {
      toast.error('Session chưa được lưu');
      return;
    }

    if (!window.confirm('Bạn có chắc muốn xóa tài liệu này?')) return;

    try {
      await sessionsApi.deleteMaterial(session.session_id, materialId);
      toast.success('Xóa tài liệu thành công');
      await fetchSessionMaterials(session.session_id); // Refresh materials
    } catch (error: any) {
      console.error('Delete error:', error);
      toast.error(error.response?.data?.detail || 'Không thể xóa tài liệu');
    }
  };

  // Download material with authentication
  const handleDownloadMaterial = async (sessionId: number, materialId: number, fileName: string) => {
    try {
      const response: any = await sessionsApi.downloadMaterial(sessionId, materialId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Tải xuống thành công');
    } catch (error: any) {
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

  const handleViewFeedbacks = async () => {
    if (!subjectId) return;

    try {
      setLoadingFeedbacks(true);
      setShowFeedbacksModal(true);
      const response = await sessionsApi.getSubjectFeedbacks(parseInt(subjectId)) as any;
      setSubjectFeedbacks(response.data);
    } catch (error) {
      console.error('Error fetching feedbacks:', error);
      toast.error('Không thể tải đánh giá');
      setShowFeedbacksModal(false);
    } finally {
      setLoadingFeedbacks(false);
    }
  };

  const handleViewStudentProfile = async (student: any) => {
    try {
      setLoadingStudentProfile(true);
      setSelectedStudent(student);
      setShowStudentProfileModal(true);

      // Fetch student profile by user_id to get correct student_id
      // The enrolled students list might not have student_id, only user_id
      const profileResponse = await studentsApi.getStudentProfileByUserId(student.user_id) as any;
      const studentId = profileResponse.data.student_id;
      setStudentProfile(profileResponse.data);

      // Fetch enrolled courses
      const coursesResponse = await studentsApi.getStudentEnrolledCourses(studentId) as any;
      setStudentCourses(coursesResponse.data);
    } catch (error) {
      console.error('Error fetching student profile:', error);
      toast.error('Không thể tải thông tin học sinh');
      setShowStudentProfileModal(false);
    } finally {
      setLoadingStudentProfile(false);
    }
  };

  // Kick student handler
  const handleKickStudent = async (studentId: number, studentName: string) => {
    if (!course?.subject_id || !course?.tutor_id) {
      toast.error('Không thể xác định thông tin khóa học');
      return;
    }

    const confirmed = window.confirm(
      `Bạn có chắc chắn muốn xóa học sinh "${studentName}" khỏi khóa học này?\n\nHọc sinh sẽ bị xóa khỏi tất cả ${enrolledStudents.find(s => s.user_id === studentId)?.sessions_enrolled || 0} buổi học.`
    );

    if (!confirmed) return;

    try {
      await sessionsApi.removeStudentFromSubject(course.subject_id, studentId, course.tutor_id);
      toast.success(`Đã xóa học sinh "${studentName}" khỏi khóa học`);

      // Refresh enrolled students list
      setEnrolledStudents(prev => prev.filter(s => s.user_id !== studentId));
    } catch (error: any) {
      console.error('Error removing student:', error);
      toast.error(error.response?.data?.detail || 'Không thể xóa học sinh khỏi khóa học');
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
      console.log('🔍 Raw API response:', response);
      console.log('🔍 Response.data:', response.data);

      // Handle both direct array and nested object response
      const participantsList = Array.isArray(response.data) ? response.data : (response.data?.data || response || []);
      console.log('📋 Participants list:', participantsList);

      setParticipants(participantsList);

      // Initialize attendance data - DON'T pre-fill from DB
      // This allows fresh attendance marking each time
      setAttendanceData({});
      setShowAttendanceModal(true);
    } catch (error) {
      console.error('Error loading participants:', error);
      toast.error('Không thể tải danh sách sinh viên');
    }
  };

  const handleSetAttendance = (userId: string, status: 'present' | 'absent' | 'late' | 'excused') => {
    setAttendanceData(prev => ({
      ...prev,
      [userId]: status
    }));
  };

  const handleSaveAttendance = async () => {
    if (!selectedSessionForAttendance) {
      toast.error('Không tìm thấy session');
      return;
    }
    try {
      // Convert to format backend expects
      const attendanceRecords = Object.entries(attendanceData)
        .filter(([_, status]) => status !== null)
        .map(([userId, status]) => ({
          user_id: parseInt(userId),
          is_present: status === 'present',
          is_late: status === 'late',
          is_excused: status === 'excused'
        }));

      if (attendanceRecords.length === 0) {
        toast.warning('Vui lòng chọn trạng thái điểm danh cho ít nhất một học viên');
        return;
      }

      await sessionsApi.markAttendance(selectedSessionForAttendance, attendanceRecords);
      toast.success('Đã lưu điểm danh thành công!');

      // Close modal after successful save
      setShowAttendanceModal(false);
      setAttendanceData({});
      setParticipants([]);

    } catch (error: any) {
      console.error('Error saving attendance:', error);
      const message = error.response?.data?.detail || 'Không thể lưu điểm danh';
      toast.error(message);
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
                  onClick={() => navigate(`/courses/${subjectId}/progress`)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
                >
                  <Clock className="h-4 w-4" />
                  Xem tiến trình học tập
                </button>
                <button
                  onClick={handleViewFeedbacks}
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 flex items-center gap-2"
                >
                  <Star className="h-4 w-4" />
                  Xem đánh giá
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
            {!isTutor && sessions.length > 0 && (
              <button
                onClick={() => navigate(`/courses/${subjectId}/progress`)}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
              >
                <Clock className="h-4 w-4" />
                Xem tiến trình học tập của tôi
              </button>
            )}
          </div>
        </div>

        <div className="p-6 space-y-3">
          {sessions.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">Chưa có buổi học nào được tạo</p>
              {isTutor && (
                <button
                  onClick={handleGenerateSessions}
                  disabled={loading}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2 mx-auto"
                >
                  <CalendarIcon className="h-5 w-5" />
                  {loading ? 'Đang tạo...' : 'Tạo lịch học từ lịch đã đăng ký'}
                </button>
              )}
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
                              {session.session_id && sessionMaterials[session.session_id]?.length > 0 && (
                                <div className="space-y-2 mb-3">
                                  {sessionMaterials[session.session_id].map((material: any) => (
                                    <div key={material.material_id} className="flex items-center justify-between p-2 bg-gray-50 rounded border border-gray-200">
                                      <div className="flex items-center gap-2">
                                        <FileText className="h-4 w-4 text-gray-500" />
                                        <span className="text-sm">{material.file_name}</span>
                                      </div>
                                      <button
                                        onClick={() => handleRemoveMaterial(session.session_number, material.material_id)}
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

                          {session.session_id && sessionMaterials[session.session_id]?.length > 0 && (
                            <div>
                              <p className="text-sm text-gray-600 mb-2">Tài liệu</p>
                              <div className="space-y-2">
                                {sessionMaterials[session.session_id].map((material: any) => {
                                  const isPDF = material.file_name?.toLowerCase().endsWith('.pdf');

                                  return (
                                    <div
                                      key={material.material_id}
                                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                                    >
                                      <div className="flex items-center gap-2 flex-1">
                                        <FileText className="h-4 w-4 text-gray-500" />
                                        <div>
                                          <span className="text-sm text-gray-700">{material.file_name}</span>
                                          <p className="text-xs text-gray-500">
                                            {material.file_size ? `${(material.file_size / 1024).toFixed(2)} KB` : 'N/A'} •
                                            {material.uploaded_at ? new Date(material.uploaded_at).toLocaleDateString('vi-VN') : ''}
                                          </p>
                                        </div>
                                      </div>
                                      <div className="flex gap-2">
                                        <button
                                          onClick={() => handleDownloadMaterial(session.session_id!, material.material_id, material.file_name)}
                                          className="px-3 py-1 text-sm border border-gray-300 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                                        >
                                          Tải về
                                        </button>
                                        {isTutor && (
                                          <button
                                            onClick={() => handleRemoveMaterial(session.session_number, material.material_id)}
                                            className="px-3 py-1 text-sm border border-red-300 text-red-700 rounded hover:bg-red-50 transition-colors flex items-center gap-1"
                                          >
                                            <Trash2 className="h-3 w-3" />
                                            Xóa
                                          </button>
                                        )}
                                      </div>
                                    </div>
                                  );
                                })}
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
                                          className={`h-5 w-5 ${star <= sessionFeedbacks[session.session_id!].rating
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
                      className={`h-8 w-8 ${star <= feedbackRating
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
              <div className="space-y-3 mb-6">
                {participants.map((participant) => {
                  // Check if already marked in database OR just marked in current session
                  const hasStatusInDB = participant.attendance_status !== null && participant.attendance_status !== undefined;
                  const hasStatusInState = attendanceData[participant.user_id] !== null && attendanceData[participant.user_id] !== undefined;
                  const isAlreadyMarked = hasStatusInDB || hasStatusInState;
                  const currentStatus = attendanceData[participant.user_id] || participant.attendance_status;

                  console.log(`👤 ${participant.full_name}:`, {
                    attendance_status: participant.attendance_status,
                    hasStatusInDB,
                    hasStatusInState,
                    isAlreadyMarked,
                    currentStatus
                  });

                  return (
                    <div
                      key={participant.user_id}
                      className={`p-4 rounded-lg ${isAlreadyMarked
                        ? 'bg-white border-2 border-gray-200'
                        : 'border-2 border-gray-200 hover:bg-gray-50'
                        }`}
                    >
                      {isAlreadyMarked ? (
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{participant.full_name}</p>
                          </div>
                          <span className={`px-4 py-2 rounded-full text-base font-semibold ${currentStatus === 'present' ? 'bg-green-100 text-green-800' :
                            currentStatus === 'late' ? 'bg-yellow-100 text-yellow-800' :
                              currentStatus === 'excused' ? 'bg-blue-100 text-blue-800' :
                                'bg-red-100 text-red-800'
                            }`}>
                            {currentStatus === 'present' ? '✓ Có mặt' :
                              currentStatus === 'late' ? '⏰ Trễ' :
                                currentStatus === 'excused' ? '📋 Có phép' :
                                  '✗ Vắng'}
                          </span>
                        </div>
                      ) : (
                        <>
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex-1">
                              <p className="font-medium text-gray-900">{participant.full_name}</p>
                              <p className="text-sm text-gray-600">{participant.email}</p>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            <label className="flex items-center gap-2 cursor-pointer p-3 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all">
                              <input
                                type="radio"
                                name={`attendance-${participant.user_id}`}
                                checked={attendanceData[participant.user_id] === 'present'}
                                onChange={() => handleSetAttendance(participant.user_id.toString(), 'present')}
                                className="w-4 h-4 text-green-600 focus:ring-2 focus:ring-green-500"
                              />
                              <span className={`text-sm font-medium ${attendanceData[participant.user_id] === 'present' ? 'text-green-600' : 'text-gray-600'
                                }`}>
                                ✓ Có mặt
                              </span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer p-3 border-2 border-gray-200 rounded-lg hover:border-yellow-500 hover:bg-yellow-50 transition-all">
                              <input
                                type="radio"
                                name={`attendance-${participant.user_id}`}
                                checked={attendanceData[participant.user_id] === 'late'}
                                onChange={() => handleSetAttendance(participant.user_id.toString(), 'late')}
                                className="w-4 h-4 text-yellow-600 focus:ring-2 focus:ring-yellow-500"
                              />
                              <span className={`text-sm font-medium ${attendanceData[participant.user_id] === 'late' ? 'text-yellow-600' : 'text-gray-600'
                                }`}>
                                ⏰ Trễ
                              </span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer p-3 border-2 border-gray-200 rounded-lg hover:border-red-500 hover:bg-red-50 transition-all">
                              <input
                                type="radio"
                                name={`attendance-${participant.user_id}`}
                                checked={attendanceData[participant.user_id] === 'absent'}
                                onChange={() => handleSetAttendance(participant.user_id.toString(), 'absent')}
                                className="w-4 h-4 text-red-600 focus:ring-2 focus:ring-red-500"
                              />
                              <span className={`text-sm font-medium ${attendanceData[participant.user_id] === 'absent' ? 'text-red-600' : 'text-gray-600'
                                }`}>
                                ✗ Vắng
                              </span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer p-3 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all">
                              <input
                                type="radio"
                                name={`attendance-${participant.user_id}`}
                                checked={attendanceData[participant.user_id] === 'excused'}
                                onChange={() => handleSetAttendance(participant.user_id.toString(), 'excused')}
                                className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                              />
                              <span className={`text-sm font-medium ${attendanceData[participant.user_id] === 'excused' ? 'text-blue-600' : 'text-gray-600'
                                }`}>
                                📋 Có phép
                              </span>
                            </label>
                          </div>
                        </>
                      )}
                    </div>
                  );
                })}
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
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-blue-50 transition-colors border border-transparent hover:border-blue-300 cursor-pointer"
                      onClick={() => handleViewStudentProfile(student)}
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
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <CalendarIcon className="h-4 w-4" />
                          <span>{student.sessions_enrolled} buổi học</span>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleKickStudent(student.user_id, student.full_name);
                          }}
                          className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                          title="Xóa học sinh khỏi khóa học"
                        >
                          <X className="h-5 w-5" />
                        </button>
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

      {/* Feedbacks Summary Modal (for Tutor) */}
      {showFeedbacksModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Đánh giá từ học sinh</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Xem tổng hợp đánh giá của học sinh về các buổi học
                </p>
              </div>
              <button
                onClick={() => setShowFeedbacksModal(false)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {loadingFeedbacks ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
              ) : subjectFeedbacks ? (
                <div className="space-y-6">
                  {/* Summary Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg p-4 border border-amber-200">
                      <div className="flex items-center gap-3">
                        <div className="p-3 bg-amber-500 rounded-lg">
                          <Star className="h-6 w-6 text-white fill-current" />
                        </div>
                        <div>
                          <p className="text-sm text-amber-700 font-medium">Điểm trung bình</p>
                          <p className="text-3xl font-bold text-amber-900">
                            {subjectFeedbacks.average_rating.toFixed(1)}
                            <span className="text-lg text-amber-600">/5.0</span>
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                      <div className="flex items-center gap-3">
                        <div className="p-3 bg-blue-500 rounded-lg">
                          <MessageSquare className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <p className="text-sm text-blue-700 font-medium">Tổng đánh giá</p>
                          <p className="text-3xl font-bold text-blue-900">
                            {subjectFeedbacks.total_feedbacks}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                      <div className="flex items-center gap-3">
                        <div className="p-3 bg-green-500 rounded-lg">
                          <CheckCircle className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <p className="text-sm text-green-700 font-medium">Phân bổ đánh giá</p>
                          <div className="space-y-1 mt-1">
                            {Object.entries(subjectFeedbacks.rating_distribution)
                              .sort(([a], [b]) => Number(b) - Number(a))
                              .map(([rating, count]) => (
                                <div key={rating} className="flex items-center gap-2 text-xs">
                                  <span className="inline-flex items-center gap-1 text-green-700">
                                    <Star className="w-3 h-3 fill-green-600" />{rating}
                                  </span>
                                  <div className="flex-1 bg-green-200 rounded-full h-2">
                                    <div
                                      className="bg-green-600 h-2 rounded-full"
                                      style={{
                                        width: `${subjectFeedbacks.total_feedbacks > 0
                                          ? ((count as number) / subjectFeedbacks.total_feedbacks) * 100
                                          : 0}%`
                                      }}
                                    />
                                  </div>
                                  <span className="text-green-700 font-medium">{count as number}</span>
                                </div>
                              ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Individual Feedbacks */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Chi tiết đánh giá ({subjectFeedbacks.feedbacks.length})
                    </h3>

                    {subjectFeedbacks.feedbacks.length === 0 ? (
                      <div className="text-center py-8 bg-gray-50 rounded-lg">
                        <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                        <p className="text-gray-600">Chưa có đánh giá nào</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {subjectFeedbacks.feedbacks.map((feedback: any) => (
                          <div key={feedback.feedback_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center gap-3">
                                <div className="flex items-center gap-1">
                                  {[1, 2, 3, 4, 5].map((star) => (
                                    <Star
                                      key={star}
                                      className={`h-5 w-5 ${star <= feedback.rating
                                        ? 'text-amber-500 fill-current'
                                        : 'text-gray-300'
                                        }`}
                                    />
                                  ))}
                                </div>
                                <span className="text-sm font-medium text-gray-700">
                                  {feedback.rating}.0/5.0
                                </span>
                              </div>
                              <div className="text-right">
                                <p className="text-sm text-gray-600">
                                  {new Date(feedback.session_date).toLocaleDateString('vi-VN')}
                                </p>
                                <p className="text-xs text-gray-500">
                                  {new Date(feedback.created_at).toLocaleDateString('vi-VN')}
                                </p>
                              </div>
                            </div>

                            {feedback.comment && (
                              <p className="text-gray-700 mb-2 italic">"{feedback.comment}"</p>
                            )}

                            <div className="flex items-center justify-between text-sm">
                              <p className="text-gray-600">
                                {feedback.is_anonymous ? (
                                  <span className="flex items-center gap-1">
                                    <span>👤 Ẩn danh</span>
                                  </span>
                                ) : (
                                  <span className="flex items-center gap-1">
                                    <span>👤 {feedback.reviewer_name}</span>
                                    {feedback.reviewer_email && (
                                      <span className="text-gray-500">({feedback.reviewer_email})</span>
                                    )}
                                  </span>
                                )}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-600">Không thể tải đánh giá</p>
                </div>
              )}
            </div>

            <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => setShowFeedbacksModal(false)}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Student Profile Modal (for Tutor) */}
      {showStudentProfileModal && selectedStudent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedStudent.full_name}</h2>
                  <p className="text-sm text-gray-600">{selectedStudent.email}</p>
                </div>
              </div>
              <button
                onClick={() => setShowStudentProfileModal(false)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {loadingStudentProfile ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
              ) : studentCourses ? (
                <div className="space-y-6">
                  {/* Student Info Summary */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Thông tin học sinh</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Họ tên</p>
                        <p className="font-semibold text-gray-900">{selectedStudent.full_name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Email</p>
                        <p className="font-semibold text-gray-900">{selectedStudent.email}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Tổng số môn học</p>
                        <p className="font-semibold text-gray-900">{studentCourses.total_courses} môn</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Tổng buổi học đăng ký</p>
                        <p className="font-semibold text-gray-900">
                          {studentCourses.courses.reduce((sum: number, c: any) => sum + c.enrolled_sessions, 0)} buổi
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Enrolled Courses */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Các lớp học đang tham gia ({studentCourses.courses.length})
                    </h3>

                    {studentCourses.courses.length === 0 ? (
                      <div className="text-center py-8 bg-gray-50 rounded-lg">
                        <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                        <p className="text-gray-600">Chưa tham gia lớp học nào</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 gap-4">
                        {studentCourses.courses.map((course: any) => (
                          <div
                            key={course.subject_id}
                            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full">
                                    {course.subject_code}
                                  </span>
                                  <span className="text-sm text-gray-500">{course.credits} TC</span>
                                </div>
                                <h4 className="text-lg font-semibold text-gray-900">
                                  {course.subject_name}
                                </h4>
                                <p className="text-sm text-gray-600 mt-1">
                                  Khoa: {course.department}
                                </p>
                              </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4 pt-3 border-t border-gray-200">
                              <div>
                                <p className="text-sm text-gray-600">Giảng viên</p>
                                <p className="font-semibold text-gray-900">
                                  {course.tutor_name || 'Chưa có'}
                                </p>
                                {course.tutor_email && (
                                  <p className="text-xs text-gray-500">{course.tutor_email}</p>
                                )}
                              </div>
                              <div>
                                <p className="text-sm text-gray-600">Tiến độ học tập</p>
                                <div className="flex items-center gap-2">
                                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                                    <div
                                      className="bg-blue-600 h-2 rounded-full"
                                      style={{
                                        width: `${course.total_sessions > 0
                                          ? (course.enrolled_sessions / course.total_sessions) * 100
                                          : 0}%`
                                      }}
                                    />
                                  </div>
                                  <span className="text-sm font-semibold text-gray-700">
                                    {course.enrolled_sessions}/{course.total_sessions}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-600">Không thể tải thông tin học sinh</p>
                </div>
              )}
            </div>

            <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => setShowStudentProfileModal(false)}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseDetail;

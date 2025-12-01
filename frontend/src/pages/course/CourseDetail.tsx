import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  BookOpen, ArrowLeft, Clock, MapPin, Video, 
  FileText, Edit2, Save, X, ChevronDown, ChevronUp, Upload, Trash2
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
}

interface WeeklySession {
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

      // Step 1: Try to fetch saved sessions from database first
      try {
        // Call the sessions API to get sessions for this subject
        const sessionsResponse = await sessionsApi.getSessions({ subject_id: parseInt(subjectId) }) as any;
        const savedSessions = sessionsResponse.data || [];
        
        console.log('Fetched sessions from DB:', savedSessions);
        
        if (savedSessions.length > 0) {
          // Convert DB sessions to WeeklySession format
          const convertedSessions: WeeklySession[] = savedSessions.map((s: any, index: number) => ({
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

  const handleFileUpload = (sessionNum: number, event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const fileNames = Array.from(files).map(f => f.name);
    setSessions(prev => prev.map(s => 
      s.session_number === sessionNum 
        ? { ...s, materials: [...s.materials, ...fileNames] } 
        : s
    ));
    toast.success(`Đã thêm ${fileNames.length} tài liệu`);
  };

  const handleRemoveMaterial = (sessionNum: number, materialIndex: number) => {
    setSessions(prev => prev.map(s => 
      s.session_number === sessionNum 
        ? { ...s, materials: s.materials.filter((_, idx) => idx !== materialIndex) } 
        : s
    ));
    toast.success('Đã xóa tài liệu');
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
              <button
                onClick={handleSaveAllSessions}
                disabled={loading}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
              >
                <Save className="h-4 w-4" />
                Lưu tất cả
              </button>
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
                          <p className="text-sm text-gray-600">
                            📅 {session.date.toLocaleDateString('vi-VN', {
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
                                  <div key={idx} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                                    <FileText className="h-4 w-4 text-gray-500" />
                                    <span className="text-sm">{material}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {isTutor && (
                            <div className="pt-4 border-t border-gray-200">
                              <button
                                onClick={() => setEditingSession(session.session_number)}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                              >
                                <Edit2 className="h-4 w-4 inline mr-1" />
                                Chỉnh sửa
                              </button>
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
    </div>
  );
};

export default CourseDetail;

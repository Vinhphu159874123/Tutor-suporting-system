import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  BookOpen, Calendar, FileText, Users, ArrowLeft,
  Clock, MapPin, CheckCircle, XCircle, AlertCircle, 
  Video, Upload, Download, TrendingUp, CheckSquare
} from 'lucide-react';
import { coursesApi, sessionsApi } from '../../services/api';
import { useAuthStore } from '../../stores/authStore';
import { toast } from 'react-toastify';

interface CourseDetail {
  subject_id: number;
  subject_code: string;
  subject_name: string;
  department: string;
  credits: number;
  description?: string;
}

interface Session {
  session_id: number;
  title: string;
  description: string;
  start_time?: string;
  end_time?: string;
  start_datetime?: string;
  end_datetime?: string;
  location?: string;
  meeting_link?: string;
  status: string;
  tutor_name?: string;
  participant_count?: number;
}

interface WeeklySchedule {
  day_of_week: number; // 0=Sunday, 1=Monday, etc.
  start_time: string;
  end_time: string;
  location: string;
  meeting_link?: string;
}

const CourseDetail: React.FC = () => {
  const { subjectId } = useParams<{ subjectId: string }>();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [weeklySchedule, setWeeklySchedule] = useState<WeeklySchedule[]>([]);
  const [activeTab, setActiveTab] = useState<'sessions' | 'schedule' | 'materials' | 'progress' | 'attendance'>('sessions');
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();

  useEffect(() => {
    if (subjectId) {
      fetchCourseData();
    } else {
      setLoading(false);
      toast.error('Không tìm thấy môn học');
    }
  }, [subjectId]);

  const fetchCourseData = async () => {
    if (!subjectId) return;
    
    try {
      setLoading(true);
      // Fetch course details
      const courseResponse = await coursesApi.getCourseByCode(subjectId) as any;
      setCourse(courseResponse.data);

      // Fetch sessions for this course
      const sessionsResponse = await sessionsApi.getSessions({ subject_id: parseInt(subjectId) }) as any;
      setSessions(sessionsResponse.data || []);
      
      // Generate weekly schedule from sessions (group by day of week)
      generateWeeklySchedule(sessionsResponse.data || []);
    } catch (error) {
      console.error('Failed to fetch course data:', error);
      toast.error('Không thể tải thông tin môn học');
    } finally {
      setLoading(false);
    }
  };

  const generateWeeklySchedule = (allSessions: Session[]) => {
    // Group sessions by day of week and time
    const scheduleMap = new Map<string, WeeklySchedule>();
    
    allSessions.forEach(session => {
      // Prefer start_datetime, fall back to start_time
      const timeStr = session.start_datetime || session.start_time;
      const endStr = session.end_datetime || session.end_time;
      
      if (!timeStr || !endStr) return;
      
      const startDate = new Date(timeStr);
      const endDate = new Date(endStr);
      
      if (isNaN(startDate.getTime())) return;
      
      const dayOfWeek = startDate.getDay();
      const startTime = startDate.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
      const endTime = endDate.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
      const key = `${dayOfWeek}-${startTime}-${endTime}`;
      
      if (!scheduleMap.has(key)) {
        scheduleMap.set(key, {
          day_of_week: dayOfWeek,
          start_time: startTime,
          end_time: endTime,
          location: session.location || 'Online',
          meeting_link: session.meeting_link
        });
      }
    });
    
    setWeeklySchedule(Array.from(scheduleMap.values()).sort((a, b) => a.day_of_week - b.day_of_week));
  };

  const getDayName = (dayOfWeek: number) => {
    const days = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
    return days[dayOfWeek];
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      published: { color: 'bg-blue-100 text-blue-700 border-blue-300', icon: AlertCircle, text: 'Đang mở' },
      confirmed: { color: 'bg-green-100 text-green-700 border-green-300', icon: CheckCircle, text: 'Đã xác nhận' },
      ongoing: { color: 'bg-purple-100 text-purple-700 border-purple-300', icon: Clock, text: 'Đang diễn ra' },
      completed: { color: 'bg-gray-100 text-gray-700 border-gray-300', icon: CheckCircle, text: 'Hoàn thành' },
      cancelled: { color: 'bg-red-100 text-red-700 border-red-300', icon: XCircle, text: 'Đã hủy' },
    };
    const badge = badges[status as keyof typeof badges] || badges.published;
    const Icon = badge.icon;
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium border ${badge.color}`}>
        <Icon className="h-4 w-4" />
        {badge.text}
      </span>
    );
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
          Quay lại danh sách
        </Link>
      </div>
    );
  }

  const isTutor = user?.role === 'tutor';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <Link
          to="/my-courses"
          className="inline-flex items-center gap-2 text-blue-100 hover:text-white mb-4"
        >
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

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <div className="flex gap-8 px-6 overflow-x-auto">
            <button
              onClick={() => setActiveTab('sessions')}
              className={`py-4 border-b-2 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'sessions'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Phiên học ({sessions.length})
              </div>
            </button>
            <button
              onClick={() => setActiveTab('schedule')}
              className={`py-4 border-b-2 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'schedule'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Lịch học hàng tuần
              </div>
            </button>
            <button
              onClick={() => setActiveTab('materials')}
              className={`py-4 border-b-2 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'materials'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Tài liệu
              </div>
            </button>
            <button
              onClick={() => setActiveTab('progress')}
              className={`py-4 border-b-2 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'progress'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Tiến trình
              </div>
            </button>
            {!isTutor && (
              <button
                onClick={() => setActiveTab('attendance')}
                className={`py-4 border-b-2 font-medium transition-colors whitespace-nowrap ${
                  activeTab === 'attendance'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <div className="flex items-center gap-2">
                  <CheckSquare className="h-5 w-5" />
                  Điểm danh
                </div>
              </button>
            )}
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Sessions Tab */}
          {activeTab === 'sessions' && (
            <div className="space-y-4">
              {sessions.length === 0 ? (
                <div className="text-center py-12">
                  <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Chưa có phiên học nào</p>
                </div>
              ) : (
                <>
                  {sessions.map((session) => {
                    // Prefer start_datetime, fall back to start_time
                    const timeStr = session.start_datetime || session.start_time;
                    const startDate = timeStr ? new Date(timeStr) : null;
                    const isValidDate = startDate && !isNaN(startDate.getTime());
                    
                    return (
                      <Link
                        key={session.session_id}
                        to={`/sessions/${session.session_id}`}
                        className="block border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 hover:shadow-md transition-all"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {session.title}
                            </h3>
                            <p className="text-gray-600 text-sm">{session.description}</p>
                          </div>
                          {getStatusBadge(session.status)}
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div className="flex items-center gap-2 text-gray-600">
                            <Clock className="h-4 w-4" />
                            <span>
                              {isValidDate ? startDate.toLocaleString('vi-VN', {
                                day: '2-digit',
                                month: '2-digit',
                                hour: '2-digit',
                                minute: '2-digit',
                              }) : 'Chưa có lịch'}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 text-gray-600">
                            <MapPin className="h-4 w-4" />
                            <span>{session.location || 'Online'}</span>
                          </div>
                          {session.meeting_link && (
                            <div className="flex items-center gap-2 text-blue-600">
                              <Video className="h-4 w-4" />
                              <span>Google Meet</span>
                            </div>
                          )}
                          {session.participant_count !== undefined && (
                            <div className="flex items-center gap-2 text-gray-600">
                              <Users className="h-4 w-4" />
                              <span>{session.participant_count} người</span>
                            </div>
                          )}
                        </div>
                      </Link>
                    );
                  })}
                </>
              )}
            </div>
          )}

          {/* Weekly Schedule Tab */}
          {activeTab === 'schedule' && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <h3 className="font-semibold text-blue-900 mb-2">📅 Lịch học cố định hàng tuần</h3>
                <p className="text-sm text-blue-700">
                  Lịch học được tạo tự động dựa trên các phiên học đã lên lịch
                </p>
              </div>
              
              {weeklySchedule.length === 0 ? (
                <div className="text-center py-12">
                  <Clock className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Chưa có lịch học cố định</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {weeklySchedule.map((schedule, index) => (
                    <div key={index} className="border-2 border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-semibold text-blue-600">
                          {getDayName(schedule.day_of_week)}
                        </h3>
                        <span className="text-sm text-gray-600">
                          {schedule.start_time} - {schedule.end_time}
                        </span>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-gray-700">
                          <MapPin className="h-4 w-4" />
                          <span>{schedule.location}</span>
                        </div>
                        {schedule.meeting_link && (
                          <div className="flex items-center gap-2">
                            <Video className="h-4 w-4 text-blue-600" />
                            <a 
                              href={schedule.meeting_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline"
                            >
                              Tham gia Google Meet
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Materials Tab */}
          {activeTab === 'materials' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Tài liệu môn học</h3>
                {isTutor && (
                  <button className="btn-primary flex items-center gap-2">
                    <Upload className="h-4 w-4" />
                    Tải lên tài liệu
                  </button>
                )}
              </div>
              
              <div className="text-center py-12">
                <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Chưa có tài liệu nào</p>
                {isTutor && (
                  <p className="text-sm text-gray-500 mt-2">
                    Tải lên tài liệu giảng dạy, bài tập, slide để sinh viên có thể truy cập
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Progress Tab */}
          {activeTab === 'progress' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Tiến trình học tập</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <div className="text-2xl font-bold text-blue-600">{sessions.length}</div>
                    <div className="text-sm text-gray-600">Tổng số buổi học</div>
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <div className="text-2xl font-bold text-green-600">
                      {sessions.filter(s => s.status === 'completed').length}
                    </div>
                    <div className="text-sm text-gray-600">Đã hoàn thành</div>
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <div className="text-2xl font-bold text-orange-600">
                      {sessions.filter(s => ['published', 'confirmed'].includes(s.status)).length}
                    </div>
                    <div className="text-sm text-gray-600">Sắp diễn ra</div>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Hoàn thành</span>
                    <span className="text-sm font-semibold text-blue-600">
                      {sessions.length > 0 
                        ? Math.round((sessions.filter(s => s.status === 'completed').length / sessions.length) * 100)
                        : 0}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all"
                      style={{ 
                        width: `${sessions.length > 0 
                          ? (sessions.filter(s => s.status === 'completed').length / sessions.length) * 100
                          : 0}%` 
                      }}
                    ></div>
                  </div>
                </div>
              </div>
              
              <div className="text-center py-8">
                <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">Chi tiết tiến trình học tập sẽ được cập nhật</p>
              </div>
            </div>
          )}

          {/* Attendance Tab (Student only) */}
          {activeTab === 'attendance' && !isTutor && (
            <div className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <h3 className="font-semibold text-yellow-900 mb-2">✋ Điểm danh</h3>
                <p className="text-sm text-yellow-700">
                  Nhấn nút điểm danh khi buổi học bắt đầu. Bạn chỉ có thể điểm danh trong khung giờ học.
                </p>
              </div>
              
              <div className="space-y-3">
                {sessions.filter(s => ['confirmed', 'ongoing'].includes(s.status)).map((session) => {
                  const timeStr = session.start_datetime || session.start_time;
                  const startDate = timeStr ? new Date(timeStr) : null;
                  const isValidDate = startDate && !isNaN(startDate.getTime());
                  
                  return (
                    <div key={session.session_id} className="border-2 border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">{session.title}</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {isValidDate ? startDate.toLocaleString('vi-VN', {
                              weekday: 'long',
                              day: '2-digit',
                              month: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                            }) : 'Chưa có lịch'}
                          </p>
                        </div>
                        <button 
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                          onClick={() => toast.info('Tính năng điểm danh đang phát triển')}
                        >
                          <CheckSquare className="h-4 w-4" />
                          Điểm danh
                        </button>
                      </div>
                    </div>
                  );
                })}
                
                {sessions.filter(s => ['confirmed', 'ongoing'].includes(s.status)).length === 0 && (
                  <div className="text-center py-12">
                    <CheckSquare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Không có buổi học nào cần điểm danh</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;

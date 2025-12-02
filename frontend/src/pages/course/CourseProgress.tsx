import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, TrendingUp, CheckCircle, XCircle, Clock, AlertCircle, User } from 'lucide-react';
import { toast } from 'react-toastify';
import api from '../../services/api';

interface AttendanceStats {
  present: number;
  late: number;
  absent: number;
  excused: number;
  attendance_rate: number;
}

interface SessionDetail {
  session_id: number;
  title: string;
  scheduled_date: string | null;
  start_time: string | null;
  end_time: string | null;
  status: string;
  is_past: boolean;
  attendance: {
    status: string;
    check_in_time: string | null;
    duration_minutes: number | null;
  } | null;
}

interface StudentProgress {
  student_id: number;
  user_id: number;
  student_name: string;
  student_code: string;
  email: string;
  progress: {
    total_sessions: number;
    completed_sessions: number;
    progress_percentage: number;
    attendance: AttendanceStats;
  };
}

interface ProgressData {
  subject_id: number;
  subject_name: string;
  subject_code: string;
  total_sessions?: number;
  total_students?: number;
  students?: StudentProgress[];
  student_progress?: {
    total_sessions: number;
    completed_sessions: number;
    progress_percentage: number;
    attendance: AttendanceStats;
    sessions: SessionDetail[];
  };
}

const CourseProgress: React.FC = () => {
  const { subjectId } = useParams<{ subjectId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [progressData, setProgressData] = useState<ProgressData | null>(null);
  const [isTutor, setIsTutor] = useState(false);

  useEffect(() => {
    fetchProgressData();
  }, [subjectId]);

  const fetchProgressData = async () => {
    try {
      setLoading(true);
      
      // Check user role
      const userResponse = await api.get('/auth/me');
      const userRole = userResponse.data.role;
      setIsTutor(userRole === 'tutor');

      // Fetch progress data
      const response = await api.get(`/progress/courses/${subjectId}/study-progress`);
      setProgressData(response.data);
    } catch (error: any) {
      console.error('Error fetching progress:', error);
      toast.error('Không thể tải thông tin tiến trình học tập');
    } finally {
      setLoading(false);
    }
  };

  const getAttendanceStatusBadge = (status: string) => {
    const badges = {
      present: { bg: 'bg-green-100', text: 'text-green-800', label: 'Có mặt', icon: CheckCircle },
      late: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Trễ', icon: Clock },
      absent: { bg: 'bg-red-100', text: 'text-red-800', label: 'Vắng', icon: XCircle },
      excused: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Có phép', icon: AlertCircle },
    };
    const badge = badges[status as keyof typeof badges] || badges.absent;
    const Icon = badge.icon;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
        <Icon className="w-3 h-3" />
        {badge.label}
      </span>
    );
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-600';
    if (percentage >= 50) return 'bg-yellow-600';
    return 'bg-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Đang tải tiến trình học tập...</p>
        </div>
      </div>
    );
  }

  if (!progressData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Không tìm thấy dữ liệu</p>
          <button onClick={() => navigate(-1)} className="mt-4 text-blue-600 hover:underline">
            Quay lại
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
        <div className="container mx-auto px-6 py-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-white hover:text-gray-200 font-medium mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Quay lại
          </button>
          
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-8 h-8" />
            <h1 className="text-3xl font-bold">Tiến Trình Học Tập</h1>
          </div>
          <p className="text-lg opacity-90">
            {progressData.subject_code} - {progressData.subject_name}
          </p>
          {progressData.total_sessions && (
            <p className="mt-2 text-sm opacity-80">
              Tổng số buổi học: {progressData.total_sessions}
            </p>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 py-6">
        {isTutor && progressData.students ? (
          // Tutor view - all students
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-bold mb-2">Tổng quan</h2>
              <p className="text-gray-600">
                Tổng số học sinh: <span className="font-semibold">{progressData.total_students}</span>
              </p>
            </div>

            {progressData.students.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <User className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Chưa có học sinh nào đăng ký khóa học này</p>
              </div>
            ) : (
              progressData.students.map((student) => (
                <div key={student.student_id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  {/* Student Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">{student.student_name}</h3>
                      <p className="text-sm text-gray-600">
                        MSSV: {student.student_code} • {student.email}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-purple-600">
                        {student.progress.progress_percentage}%
                      </div>
                      <p className="text-xs text-gray-600">Hoàn thành</p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full ${getProgressColor(student.progress.progress_percentage)}`}
                        style={{ width: `${student.progress.progress_percentage}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between mt-1 text-sm text-gray-600">
                      <span>{student.progress.completed_sessions} / {student.progress.total_sessions} buổi</span>
                      <span>Tỷ lệ tham gia: {student.progress.attendance.attendance_rate}%</span>
                    </div>
                  </div>

                  {/* Attendance Stats */}
                  <div className="grid grid-cols-4 gap-3">
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{student.progress.attendance.present}</div>
                      <div className="text-xs text-gray-600">Có mặt</div>
                    </div>
                    <div className="text-center p-3 bg-yellow-50 rounded-lg">
                      <div className="text-2xl font-bold text-yellow-600">{student.progress.attendance.late}</div>
                      <div className="text-xs text-gray-600">Trễ</div>
                    </div>
                    <div className="text-center p-3 bg-red-50 rounded-lg">
                      <div className="text-2xl font-bold text-red-600">{student.progress.attendance.absent}</div>
                      <div className="text-xs text-gray-600">Vắng</div>
                    </div>
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{student.progress.attendance.excused}</div>
                      <div className="text-xs text-gray-600">Có phép</div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : progressData.student_progress ? (
          // Student view - own progress
          <div className="space-y-6">
            {/* Overview Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-bold mb-4">Tiến Trình Của Bạn</h2>
              
              <div className="mb-6">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Hoàn thành</span>
                  <span className="text-2xl font-bold text-purple-600">
                    {progressData.student_progress.progress_percentage}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div
                    className={`h-4 rounded-full ${getProgressColor(progressData.student_progress.progress_percentage)}`}
                    style={{ width: `${progressData.student_progress.progress_percentage}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {progressData.student_progress.completed_sessions} / {progressData.student_progress.total_sessions} buổi học đã hoàn thành
                </p>
              </div>

              {/* Attendance Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-green-600">
                    {progressData.student_progress.attendance.present}
                  </div>
                  <div className="text-sm text-gray-600">Có mặt</div>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <Clock className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-yellow-600">
                    {progressData.student_progress.attendance.late}
                  </div>
                  <div className="text-sm text-gray-600">Trễ</div>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <XCircle className="w-8 h-8 text-red-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-red-600">
                    {progressData.student_progress.attendance.absent}
                  </div>
                  <div className="text-sm text-gray-600">Vắng</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <AlertCircle className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-blue-600">
                    {progressData.student_progress.attendance.excused}
                  </div>
                  <div className="text-sm text-gray-600">Có phép</div>
                </div>
              </div>

              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Tỷ lệ tham gia:</strong> {progressData.student_progress.attendance.attendance_rate}%
                </p>
              </div>
            </div>

            {/* Sessions Detail */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-bold">Chi Tiết Các Buổi Học</h2>
              </div>
              
              <div className="divide-y divide-gray-200">
                {progressData.student_progress.sessions.map((session) => (
                  <div key={session.session_id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-bold text-gray-900 mb-2">{session.title}</h3>
                        <div className="space-y-1 text-sm text-gray-600">
                          {session.scheduled_date && (
                            <p>
                              📅 {new Date(session.scheduled_date).toLocaleDateString('vi-VN')}
                              {session.start_time && ` • ${session.start_time.substring(0, 5)}`}
                              {session.end_time && ` - ${session.end_time.substring(0, 5)}`}
                            </p>
                          )}
                          <p>Trạng thái: <span className="font-medium">{session.status}</span></p>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        {session.attendance ? (
                          <div>
                            {getAttendanceStatusBadge(session.attendance.status)}
                            {session.attendance.check_in_time && (
                              <p className="text-xs text-gray-500 mt-1">
                                Check-in: {new Date(session.attendance.check_in_time).toLocaleTimeString('vi-VN', {
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </p>
                            )}
                          </div>
                        ) : session.is_past ? (
                          <span className="text-xs text-gray-500">Chưa điểm danh</span>
                        ) : (
                          <span className="text-xs text-gray-500">Chưa diễn ra</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default CourseProgress;

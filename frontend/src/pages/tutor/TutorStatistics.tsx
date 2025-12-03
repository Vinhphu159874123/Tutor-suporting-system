import React, { useState, useEffect } from 'react';
import { BarChart, Users, Clock, Calendar, TrendingUp, MapPin, BookOpen, Eye, Monitor, Building2, RefreshCw } from 'lucide-react';
import api from '../../services/api';
import { toast } from 'react-toastify';
import { useAuthStore } from '../../stores/authStore';

interface TimeSlotStat {
  time_slot: string;
  count: number;
  percentage: number;
}

interface PreferenceStatistics {
  subject_id: number;
  subject_code: string;
  subject_name: string;
  total_requests: number;
  popular_time_slots: TimeSlotStat[];
  format_distribution: { [key: string]: number };
  average_duration: number;
  duration_distribution: { [key: number]: number };
  average_sessions: number;
  earliest_start_date: string | null;
  latest_start_date: string | null;
  existing_sessions_count?: number;
}

interface PreferenceDetail {
  preference_id: number;
  student_name: string;
  student_code: string;
  preferred_start_date: string;
  total_sessions: number;
  session_duration: number;
  session_format: string;
  available_time_slots: Array<{
    day: string;
    start_time: string;
    end_time: string;
  }>;
  notes?: string;
  created_at: string;
}

const TutorStatistics: React.FC = () => {
  const { user, currentMode } = useAuthStore();
  const [statistics, setStatistics] = useState<PreferenceStatistics[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState<PreferenceStatistics | null>(null);
  const [subjectDetails, setSubjectDetails] = useState<PreferenceDetail[]>([]);
  
  // Determine active mode
  const activeMode = currentMode || (user?.role && user.role[0]) || 'tutor';

  useEffect(() => {
    loadStatistics();
  }, [activeMode]);

  const loadStatistics = async () => {
    try {
      setLoading(true);
      const response = await api.get('/schedule-preferences/statistics', {
        params: { mode: activeMode }
      });
      const stats = response.data;
      
      // Fetch existing sessions count for each subject
      const statsWithSessions = await Promise.all(
        stats.map(async (stat: PreferenceStatistics) => {
          try {
            const sessionsResponse = await api.get('/sessions', {
              params: { subject_id: stat.subject_id }
            });
            return {
              ...stat,
              existing_sessions_count: sessionsResponse.data?.length || 0
            };
          } catch (error) {
            console.error(`Error fetching sessions for subject ${stat.subject_id}:`, error);
            return {
              ...stat,
              existing_sessions_count: 0
            };
          }
        })
      );
      
      setStatistics(statsWithSessions);
    } catch (error: any) {
      console.error('Error loading statistics:', error);
      toast.error('Không thể tải thống kê');
    } finally {
      setLoading(false);
    }
  };

  const loadSubjectDetails = async (subjectId: number) => {
    try {
      const response = await api.get(`/schedule-preferences/statistics/${subjectId}/details`, {
        params: { mode: activeMode }
      });
      setSubjectDetails(response.data.preferences);
      setShowDetails(true);
    } catch (error: any) {
      console.error('Error loading subject details:', error);
      toast.error('Không thể tải chi tiết');
    }
  };

  const handleViewDetails = (stat: PreferenceStatistics) => {
    setSelectedSubject(stat);
    loadSubjectDetails(stat.subject_id);
  };

  const getFormatLabel = (format: string) => {
    switch (format) {
      case 'online': return 'Online';
      case 'offline': return 'Offline';
      case 'both': return 'Cả hai';
      default: return format;
    }
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'online': return <Monitor className="w-4 h-4" />;
      case 'offline': return <Building2 className="w-4 h-4" />;
      case 'both': return <RefreshCw className="w-4 h-4" />;
      default: return null;
    }
  };

  const getDayLabel = (day: string) => {
    const days: { [key: string]: string } = {
      'monday': 'T2',
      'tuesday': 'T3',
      'wednesday': 'T4',
      'thursday': 'T5',
      'friday': 'T6',
      'saturday': 'T7',
      'sunday': 'CN'
    };
    return days[day] || day;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Thống kê nguyện vọng học sinh</h1>
        <p className="text-gray-600">
          Xem thống kê nguyện vọng của học sinh để quyết định mở lớp phù hợp
        </p>
      </div>

      {/* Statistics Cards */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Đang tải thống kê...</p>
        </div>
      ) : statistics.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <BarChart className="mx-auto text-gray-400 mb-4" size={64} />
          <p className="text-gray-600 text-lg">Chưa có nguyện vọng nào</p>
          <p className="text-gray-500 text-sm mt-2">Khi học sinh đăng ký nguyện vọng, thống kê sẽ hiện ở đây</p>
        </div>
      ) : (
        <div className="space-y-6">
          {statistics.map((stat) => (
            <div key={stat.subject_id} className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow">
              <div className="p-6">
                {/* Subject Header */}
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{stat.subject_code}</h2>
                    <p className="text-gray-600">{stat.subject_name}</p>
                  </div>
                  <div className="text-right">
                    <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg">
                      <Users className="inline mr-2" size={20} />
                      <span className="text-2xl font-bold">{stat.total_requests}</span>
                      <span className="text-sm ml-1">nguyện vọng</span>
                    </div>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  {/* Existing Sessions Count */}
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                    <div className="flex items-center mb-2">
                      <BookOpen className="text-blue-600 mr-2" size={20} />
                      <span className="text-sm font-medium text-blue-900">Courses đã có</span>
                    </div>
                    <p className="text-2xl font-bold text-blue-900">{stat.existing_sessions_count || 0}</p>
                    <p className="text-xs text-blue-700 mt-1">sessions đang mở</p>
                  </div>

                  {/* Average Duration */}
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                    <div className="flex items-center mb-2">
                      <Clock className="text-purple-600 mr-2" size={20} />
                      <span className="text-sm font-medium text-purple-900">Thời lượng TB</span>
                    </div>
                    <p className="text-2xl font-bold text-purple-900">{stat.average_duration} phút</p>
                  </div>

                  {/* Average Sessions */}
                  <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                    <div className="flex items-center mb-2">
                      <BookOpen className="text-green-600 mr-2" size={20} />
                      <span className="text-sm font-medium text-green-900">Số buổi TB</span>
                    </div>
                    <p className="text-2xl font-bold text-green-900">{stat.average_sessions}</p>
                  </div>

                  {/* Date Range */}
                  <div className="bg-gradient-to-br from-amber-50 to-amber-100 p-4 rounded-lg">
                    <div className="flex items-center mb-2">
                      <Calendar className="text-amber-600 mr-2" size={20} />
                      <span className="text-sm font-medium text-amber-900">Khung thời gian</span>
                    </div>
                    <p className="text-sm font-bold text-amber-900">
                      {stat.earliest_start_date && new Date(stat.earliest_start_date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })}
                      {' - '}
                      {stat.latest_start_date && new Date(stat.latest_start_date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })}
                    </p>
                  </div>
                </div>

                {/* Format Distribution */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <MapPin className="mr-2 text-blue-600" size={20} />
                    Hình thức học ưa thích
                  </h3>
                  <div className="grid grid-cols-3 gap-3">
                    {Object.entries(stat.format_distribution).map(([format, count]) => (
                      <div key={format} className="bg-gray-50 p-3 rounded-lg text-center">
                        <div className="flex items-center justify-center gap-1 text-sm text-gray-600 mb-1">
                          {getFormatIcon(format)}
                          <span>{getFormatLabel(format)}</span>
                        </div>
                        <p className="text-2xl font-bold text-gray-900">{count}</p>
                        <p className="text-xs text-gray-500">
                          {Math.round((count / stat.total_requests) * 100)}%
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Popular Time Slots */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <TrendingUp className="mr-2 text-blue-600" size={20} />
                    Khung giờ phổ biến
                  </h3>
                  <div className="space-y-2">
                    {stat.popular_time_slots.slice(0, 5).map((slot, idx) => (
                      <div key={idx} className="relative">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium text-gray-700">{slot.time_slot}</span>
                          <span className="text-sm font-bold text-blue-600">
                            {slot.count} SV ({slot.percentage}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ width: `${slot.percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Duration Distribution */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">
                    Phân bố thời lượng buổi học
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(stat.duration_distribution)
                      .sort((a, b) => Number(a[0]) - Number(b[0]))
                      .map(([duration, count]) => (
                        <div key={duration} className="bg-indigo-50 border border-indigo-200 px-3 py-2 rounded-lg">
                          <span className="font-medium text-indigo-900">{duration} phút</span>
                          <span className="text-indigo-600 ml-2">× {count}</span>
                        </div>
                      ))}
                  </div>
                </div>

                {/* View Details Button */}
                <button
                  onClick={() => handleViewDetails(stat)}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 transition-colors"
                >
                  <Eye size={20} />
                  Xem chi tiết nguyện vọng
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Details Modal */}
      {showDetails && selectedSubject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold">{selectedSubject.subject_code}</h2>
                  <p className="opacity-90">{selectedSubject.subject_name}</p>
                  <p className="text-sm mt-2 opacity-75">
                    {subjectDetails.length} học sinh đã đăng ký nguyện vọng
                  </p>
                </div>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-4">
                {subjectDetails.map((detail) => (
                  <div key={detail.preference_id} className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-bold text-gray-900">{detail.student_name}</h4>
                        <p className="text-sm text-gray-600">{detail.student_code}</p>
                      </div>
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        {new Date(detail.created_at).toLocaleDateString('vi-VN')}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                      <div className="text-sm">
                        <p className="text-gray-500">Bắt đầu</p>
                        <p className="font-medium text-gray-900">
                          {new Date(detail.preferred_start_date).toLocaleDateString('vi-VN')}
                        </p>
                      </div>
                      <div className="text-sm">
                        <p className="text-gray-500">Số buổi</p>
                        <p className="font-medium text-gray-900">{detail.total_sessions} buổi</p>
                      </div>
                      <div className="text-sm">
                        <p className="text-gray-500">Thời lượng</p>
                        <p className="font-medium text-gray-900">{detail.session_duration} phút</p>
                      </div>
                      <div className="text-sm">
                        <p className="text-gray-500">Hình thức</p>
                        <p className="flex items-center gap-1 font-medium text-gray-900">
                          {getFormatIcon(detail.session_format)}
                          {getFormatLabel(detail.session_format)}
                        </p>
                      </div>
                    </div>

                    <div className="mb-3">
                      <p className="text-xs text-gray-500 mb-2">Khung giờ rảnh:</p>
                      <div className="flex flex-wrap gap-2">
                        {detail.available_time_slots.map((slot, idx) => (
                          <span key={idx} className="bg-white border border-gray-300 text-xs px-2 py-1 rounded">
                            {getDayLabel(slot.day)} {slot.start_time}-{slot.end_time}
                          </span>
                        ))}
                      </div>
                    </div>

                    {detail.notes && (
                      <div className="bg-white p-3 rounded border border-gray-200">
                        <p className="text-xs text-gray-500 mb-1">Ghi chú:</p>
                        <p className="text-sm text-gray-700">{detail.notes}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TutorStatistics;

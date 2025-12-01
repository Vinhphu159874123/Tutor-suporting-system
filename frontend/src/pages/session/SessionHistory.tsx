import React, { useState, useEffect } from 'react';
import SessionBackButton from './SessionBackButton';
import {
  BookOpen,
  CheckCircle2,
  Clock3,
  Star,
  FileBarChart2,
  CalendarX2,
} from 'lucide-react';
import { sessionsApi, authApi } from '../../services/api';
import { toast } from 'react-toastify';
import { useAuthStore } from '../../stores/authStore';
import { AxiosResponse } from 'axios';

const SessionHistory: React.FC = () => {
  const { user } = useAuthStore();
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const params: any = { limit: 100 };
        
        // Get tutor_id or student_id based on role
        if (user?.role === 'student' || user?.role === 'tutor') {
          try {
            // Get full user profile which includes tutor_id or student_id
            const meResponse: any = await authApi.getProfile();
            const userData = meResponse.data;
            
            console.log('User data from API:', userData);
            console.log('Current user role:', user?.role);
            console.log('User ID:', user?.user_id);
            
            if (user?.role === 'student' && userData.student_id) {
              params.student_id = userData.student_id;
              console.log('Filtering by student_id:', userData.student_id);
            } else if (user?.role === 'tutor' && userData.tutor_id) {
              params.tutor_id = userData.tutor_id;
              console.log('Filtering by tutor_id:', userData.tutor_id);
            } else {
              console.warn('No tutor_id or student_id found in user data');
            }
          } catch (err) {
            console.error('Error fetching user profile:', err);
          }
        }
        
        console.log('Final params for getSessions:', params);
        
        if (filter !== 'all') {
          params.status = filter;
        }
        
        const response = await sessionsApi.getSessions(params) as AxiosResponse<any>;
        setSessions(response.data);
      } catch (error: any) {
        toast.error('Không thể tải lịch sử phiên học');
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, [filter, user]);

  const filteredSessions = sessions.filter(session => {
    const matchesSearch = 
      (session.subject || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (session.tutor_name || session.tutor?.full_name || '').toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const stats = {
    total: sessions.length,
    completed: sessions.filter((s: any) => s.status === 'completed').length,
    cancelled: sessions.filter((s: any) => s.status === 'cancelled').length,
    totalHours: sessions
      .filter((s: any) => s.status === 'completed')
      .reduce((sum: number, s: any) => sum + (s.duration || 0), 0),
    totalSpent: sessions
      .filter((s: any) => s.status === 'completed')
      .reduce((sum: number, s: any) => sum + (s.price || 0), 0),
    avgRating: sessions.length > 0 
      ? sessions
          .filter((s: any) => s.rating)
          .reduce((sum: number, s: any, _: any, arr: any[]) => sum + (s.rating || 0) / arr.length, 0)
          .toFixed(1)
      : '0.0',
  };

  const exportHistory = () => {
    // Export to CSV or PDF
    console.log('Export history');
  };

  return (
    <div className="space-y-6">
      <SessionBackButton />
      {/* Header */}
      
      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Đang tải lịch sử...</p>
        </div>
      )}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Lịch sử học tập</h1>
        <p className="text-purple-100">
          Xem lại tất cả các phiên học đã tham gia
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="mr-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
              <BookOpen className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Tổng phiên học</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="mr-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-green-50 text-green-600">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Hoàn thành</p>
              <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="mr-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
              <Clock3 className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Tổng giờ học</p>
              <p className="text-2xl font-bold text-blue-600">{stats.totalHours}h</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="mr-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-yellow-50 text-yellow-600">
              <Star className="h-6 w-6 fill-yellow-400 text-yellow-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Đánh giá TB</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.avgRating}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Tất cả
            </button>
            <button
              onClick={() => setFilter('completed')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'completed'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Hoàn thành
            </button>
            <button
              onClick={() => setFilter('cancelled')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'cancelled'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Đã hủy
            </button>
          </div>

          <div className="flex gap-3 w-full md:w-auto">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm kiếm..."
              className="flex-1 md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <button
              onClick={exportHistory}
              className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors whitespace-nowrap"
            >
              <FileBarChart2 className="h-4 w-4" />
              Xuất báo cáo
            </button>
          </div>
        </div>
      </div>

      {/* Sessions List */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Ngày</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Môn học</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Gia sư</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Thời lượng</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Học phí</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Trạng thái</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Đánh giá</th>
              </tr>
            </thead>
            <tbody>
              {filteredSessions.map((session) => (
                <tr key={session.session_id || session.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div>
                      <p className="font-medium">{session.scheduled_date || session.date || 'N/A'}</p>
                      <p className="text-sm text-gray-600">{session.start_time?.substring(0, 5) || session.time || 'N/A'}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4 font-medium">{session.subject || session.title || 'N/A'}</td>
                  <td className="py-3 px-4">{session.tutor_name || session.tutor?.full_name || 'N/A'}</td>
                  <td className="py-3 px-4">{session.duration || 0}h</td>
                  <td className="py-3 px-4 font-semibold text-green-600">
                    {(session.price || 0).toLocaleString()}đ
                  </td>
                  <td className="py-3 px-4">
                    {session.status === 'completed' ? (
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                        Hoàn thành
                      </span>
                    ) : session.status === 'cancelled' ? (
                      <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                        Đã hủy
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium">
                        {session.status || 'N/A'}
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    {session.rating ? (
                      <div className="flex items-center">
                        <Star className="mr-1 h-4 w-4 fill-yellow-400 text-yellow-500" />
                        <span className="font-medium">{session.rating}</span>
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredSessions.length === 0 && (
          <div className="text-center py-12">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-purple-50 text-purple-600">
              <CalendarX2 className="h-8 w-8" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Không tìm thấy phiên học
            </h3>
            <p className="text-gray-600">
              Thử thay đổi bộ lọc hoặc tìm kiếm với từ khóa khác
            </p>
          </div>
        )}
      </div>

      {/* Total Spending */}
      <div className="card bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              Tổng chi phí học tập
            </h3>
            <p className="text-sm text-gray-600">
              Từ {stats.completed} phiên học hoàn thành
            </p>
          </div>
          <div className="text-3xl font-bold text-green-600">
            {stats.totalSpent.toLocaleString()}đ
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionHistory;

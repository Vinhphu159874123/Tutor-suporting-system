import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import { CheckSquare, UserCheck, Clock, Star, FileText, Calendar, BarChart3, Users } from "lucide-react";
import { usersApi, coordinatorApi, sessionsApi } from "../../services/api";
import { AxiosResponse } from "axios";


const CoordinatorDashboard: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [pendingSessions, setPendingSessions] = useState<any[]>([]);
  const [upcomingSessions, setUpcomingSessions] = useState<any[]>([]);
  const [statsData, setStatsData] = useState({
    total_sessions: 0,
    pending_tutors: 0,
    pending_sessions: 0,
    average_rating: 0
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch stats
        const statsResponse = await usersApi.getCoordinatorStats() as AxiosResponse<any>;
        setStatsData(statsResponse.data);

        // Fetch pending sessions
        const pendingResponse = await coordinatorApi.getPendingSessions(0, 3) as AxiosResponse<any>;
        setPendingSessions(pendingResponse.data.sessions || []);

        // Fetch upcoming sessions
        const upcomingResponse = await sessionsApi.getSessions({
          status: 'scheduled',
          skip: 0,
          limit: 3
        }) as AxiosResponse<any>;
        setUpcomingSessions(upcomingResponse.data || []);
      } catch (error: any) {
        console.error('Failed to fetch coordinator data:', error);
        setStatsData({
          total_sessions: 0,
          pending_tutors: 0,
          pending_sessions: 0,
          average_rating: 0
        });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const stats = [
    { name: "Tổng số phiên học", value: loading ? "..." : String(statsData.total_sessions), icon: <CheckSquare size={32} className="text-green-500" /> },
    { name: "Số Tutor chờ duyệt", value: loading ? "..." : String(statsData.pending_tutors), icon: <UserCheck size={32} className="text-blue-500" /> },
    { name: "Số phiên học chờ duyệt", value: loading ? "..." : String(statsData.pending_sessions), icon: <Clock size={32} className="text-yellow-500" /> },
  ];
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">
          Chào mừng, {user?.full_name}!
        </h1>
        <p className="text-blue-100">
          Vai trò: <span className="font-semibold">{user?.role}</span>
          {user?.faculty && ` • Khoa: ${user.faculty}`}
          {user?.major && ` • Ngành: ${user.major}`}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className="text-3xl mr-4">{stat.icon}</div>
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Phiên học cần duyệt */}
        <div className="card p-6 bg-white rounded-lg shadow">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Phiên học cần duyệt
          </h2>
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-4">
                <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              </div>
            ) : pendingSessions.length > 0 ? (
              pendingSessions.map((session) => (
                <div
                  key={session.session_id}
                  className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                  onClick={() => navigate('/coor/sessions')}
                >
                  <div className="text-2xl mr-3">
                    <FileText className="w-8 h-8 text-yellow-600" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">Tutor: {session.tutor?.full_name || session.tutor_name || 'N/A'}</p>
                    <p className="text-sm text-gray-600">
                      Môn: {session.subject_name || session.subject_code} • Ngày: {session.scheduled_date || new Date(session.start_datetime || session.created_at).toLocaleDateString('vi-VN')}, {session.start_time?.slice(0, 5) || new Date(session.start_datetime).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })} - {session.end_time?.slice(0, 5) || new Date(session.end_datetime).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  <div className="text-yellow-600 font-medium">Chờ duyệt</div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                <p>Không có phiên học nào cần duyệt</p>
              </div>
            )}
          </div>
        </div>

        {/* Lịch các phiên học sắp tới */}
        <div className="card p-6 bg-white rounded-lg shadow">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Lịch các phiên học sắp tới
          </h2>
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-4">
                <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              </div>
            ) : upcomingSessions.length > 0 ? (
              upcomingSessions.map((session) => (
                <div
                  key={session.session_id}
                  className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                  onClick={() => navigate('/coor/sessions')}
                >
                  <div className="text-2xl mr-3">
                    <Calendar className="w-8 h-8 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{session.subject_name || session.subject_code} - Tutor: {session.tutor?.full_name || session.tutor_name || 'N/A'}</p>
                    <p className="text-sm text-gray-600">
                      {session.scheduled_date || new Date(session.start_datetime || session.created_at).toLocaleDateString('vi-VN')}, {session.start_time?.slice(0, 5) || new Date(session.start_datetime).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })} - {session.end_time?.slice(0, 5) || new Date(session.end_datetime).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  <div className="text-blue-600 font-medium">Đã lên lịch</div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                <p>Không có phiên học sắp tới</p>
              </div>
            )}
          </div>
        </div>
      </div>


      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Hành động nhanh
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Duyệt Tutor */}
          <button
            onClick={() => navigate("/coor/review")}
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
          >
            <div className="text-2xl mr-3">
              <Users className="w-7 h-7 text-blue-600" />
            </div>
            <div className="text-left">
              <p className="font-medium">Duyệt Tutor</p>
              <p className="text-sm text-gray-600">Xét duyệt đăng ký tutor</p>
            </div>
          </button>

          {/* Quản lý Buổi học */}
          <button
            onClick={() => navigate("/coor/sessions")}
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
          >
            <div className="text-2xl mr-3">
              <Calendar className="w-7 h-7 text-green-600" />
            </div>
            <div className="text-left">
              <p className="font-medium">Quản lý Buổi học</p>
              <p className="text-sm text-gray-600">Kiểm tra & phê duyệt buổi học</p>
            </div>
          </button>

          {/* Xem báo cáo */}
          <button
            onClick={() => navigate("/reports")}
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors"
          >
            <div className="text-2xl mr-3">
              <BarChart3 className="w-7 h-7 text-purple-600" />
            </div>
            <div className="text-left">
              <p className="font-medium">Xem báo cáo</p>
              <p className="text-sm text-gray-600">Báo cáo tổng quan</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};
export default CoordinatorDashboard;
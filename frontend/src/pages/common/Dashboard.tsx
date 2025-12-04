import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  BookOpen,
  CalendarDays,
  CheckCircle2,
  Clock3,
  MessageSquareText,
  NotebookPen,
  UserRound,
} from "lucide-react";
import { useAuthStore } from "../../stores/authStore";
import { usersApi, sessionsApi } from "../../services/api";
import { toast } from "react-toastify";
import { AxiosResponse } from "axios";

interface Session {
  session_id: number;
  subject_id: number;
  subject_name: string;
  subject_code: string;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  status: string;
}

const Dashboard: React.FC = () => {
  const { user, currentMode } = useAuthStore();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recentSessions, setRecentSessions] = useState<Session[]>([]);
  const [upcomingSessions, setUpcomingSessions] = useState<Session[]>([]);
  const [statsData, setStatsData] = useState({
    total_sessions: 0,
    completed_sessions: 0,
    upcoming_sessions: 0,
    average_rating: 0
  });

  // Determine active mode
  const activeMode = currentMode || (user?.role && user.role[0]) || 'student';

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch stats - pass activeMode to get correct stats
        const statsResponse = await usersApi.getDashboardStats(activeMode) as AxiosResponse<any>;
        setStatsData(statsResponse.data);

        // Fetch recent and upcoming sessions - OPTIMIZED: Use new cached endpoint
        // Backend returns pre-filtered: {recent: [...], upcoming: [...]}
        const sessionsResponse = await sessionsApi.getMySessionsDashboard({ mode: activeMode }) as AxiosResponse<any>;
        const data = sessionsResponse.data || { recent: [], upcoming: [] };

        // Backend already returns sorted & limited data (3 each)
        setRecentSessions(data.recent || []);
        setUpcomingSessions(data.upcoming || []);
      } catch (error: any) {
        console.error('Failed to fetch dashboard data:', error);
        toast.error('Không thể tải thông tin dashboard');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [activeMode]); // Re-fetch when mode changes

  const stats = [
    { name: "Tổng số phiên học", value: String(statsData.total_sessions || 0), icon: BookOpen },
    { name: "Phiên hoàn thành", value: String(statsData.completed_sessions || 0), icon: CheckCircle2 },
    { name: "Phiên sắp tới", value: String(statsData.upcoming_sessions || 0), icon: Clock3 },
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center mr-4">
                  <Icon className="w-6 h-6 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  {loading ? (
                    <div className="h-8 w-20 bg-gray-200 animate-pulse rounded mt-1"></div>
                  ) : (
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Phiên học gần đây
          </h2>
          <div className="space-y-4">
            {recentSessions.length > 0 ? (
              recentSessions.map((session) => (
                <div
                  key={session.session_id}
                  className="flex items-center p-3 bg-gray-50 rounded-lg"
                >
                  <div className="text-2xl mr-3">
                    <UserRound className="w-8 h-8 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{session.subject_name}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(session.scheduled_date).toLocaleDateString('vi-VN')}, {session.start_time} - {session.end_time}
                    </p>
                  </div>
                  <div className="text-green-600 font-medium">Hoàn thành</div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">Chưa có phiên học nào</p>
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Lịch sắp tới</h2>
          <div className="space-y-4">
            {upcomingSessions.length > 0 ? (
              upcomingSessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => navigate(`/my-courses/${session.subject_id}`)}
                  className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                >
                  <div className="text-2xl mr-3">
                    <CalendarDays className="w-8 h-8 text-indigo-600" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-blue-600">{session.subject_name}</p>
                    <p className="text-xs text-gray-500 mb-1">{session.subject_code}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(session.scheduled_date).toLocaleDateString('vi-VN')}, {session.start_time} - {session.end_time}
                    </p>
                  </div>
                  <div className="text-blue-600 font-medium text-sm">Đã lên lịch</div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">Chưa có lịch học nào</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Hành động nhanh
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => navigate("/tutors/register")}
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
          >
            <div className="text-2xl mr-3">
              <NotebookPen className="w-7 h-7 text-green-600" />
            </div>
            <div className="text-left">
              <p className="font-medium">Đăng ký làm Tutor</p>
              <p className="text-sm text-gray-600">Chia sẻ kiến thức</p>
            </div>
          </button>

          <button
            onClick={() => navigate("/forum")}
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors"
          >
            <div className="text-2xl mr-3">
              <MessageSquareText className="w-7 h-7 text-purple-600" />
            </div>
            <div className="text-left">
              <p className="font-medium">Tham gia Forum</p>
              <p className="text-sm text-gray-600">Thảo luận học tập</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

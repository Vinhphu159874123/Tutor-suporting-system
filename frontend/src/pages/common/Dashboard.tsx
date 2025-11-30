import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  BookOpen,
  CalendarDays,
  CheckCircle2,
  Clock3,
  MessageSquareText,
  NotebookPen,
  PlusCircle,
  Star,
  UserRound,
} from "lucide-react";
import { useAuthStore } from "../../stores/authStore";
import { usersApi } from "../../services/api";
import { toast } from "react-toastify";
import { AxiosResponse } from "axios";

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [statsData, setStatsData] = useState({
    total_sessions: 0,
    completed_sessions: 0,
    upcoming_sessions: 0,
    average_rating: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await usersApi.getDashboardStats() as AxiosResponse<any>;
        setStatsData(response.data);
      } catch (error: any) {
        console.error('Failed to fetch stats:', error);
        toast.error('Không thể tải thống kê');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const stats = [
    { name: "Tổng số phiên học", value: loading ? "..." : String(statsData.total_sessions), icon: BookOpen },
    { name: "Phiên hoàn thành", value: loading ? "..." : String(statsData.completed_sessions), icon: CheckCircle2 },
    { name: "Phiên sắp tới", value: loading ? "..." : String(statsData.upcoming_sessions), icon: Clock3 },
    { name: "Đánh giá trung bình", value: loading ? "..." : `${statsData.average_rating}/5`, icon: Star },
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center mr-4">
                  <Icon className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
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
            {[1, 2, 3].map((item) => (
              <div
                key={item}
                className="flex items-center p-3 bg-gray-50 rounded-lg"
              >
                <div className="text-2xl mr-3">
                  <UserRound className="w-8 h-8 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="font-medium">Toán cao cấp A1</p>
                  <p className="text-sm text-gray-600">
                    Hôm qua, 14:00 - 16:00
                  </p>
                </div>
                <div className="text-green-600 font-medium">Hoàn thành</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Lịch sắp tới</h2>
          <div className="space-y-4">
            {[1, 2, 3].map((item) => (
              <div
                key={item}
                className="flex items-center p-3 bg-gray-50 rounded-lg"
              >
                <div className="text-2xl mr-3">
                  <CalendarDays className="w-8 h-8 text-indigo-600" />
                </div>
                <div className="flex-1">
                  <p className="font-medium">Vật lý đại cương</p>
                  <p className="text-sm text-gray-600">
                    Ngày mai, 09:00 - 11:00
                  </p>
                </div>
                <div className="text-blue-600 font-medium">Đã lên lịch</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Hành động nhanh
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="text-2xl mr-3">
              <PlusCircle className="w-7 h-7 text-blue-600" />
            </div>
            <div className="text-left">
              <p className="font-medium">Tạo phiên học mới</p>
              <p className="text-sm text-gray-600">Lên lịch phiên học</p>
            </div>
          </button>

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

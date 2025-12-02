import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { Calendar, CheckCircle, Clock, Users, MapPin, Check, X } from 'lucide-react';
import { coordinatorApi, sessionsApi } from "../../services/api";
import { AxiosResponse } from "axios";

const CoordinatorSessions: React.FC = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const [stats, setStats] = useState({
    total: 0,
    scheduled: 0,
    pending: 0,
    students: 0
  });

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await sessionsApi.getSessions({}) as AxiosResponse<any>;
      const sessionsData = response.data || [];
      setSessions(sessionsData);

      // Calculate stats
      setStats({
        total: sessionsData.length,
        scheduled: sessionsData.filter((s: any) => s.status === 'scheduled').length,
        pending: sessionsData.filter((s: any) => s.status === 'pending').length,
        students: sessionsData.reduce((sum: number, s: any) => sum + (s.student_count || 0), 0)
      });
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
      toast.error('Không thể tải danh sách buổi học');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "scheduled":
        return "bg-green-100 text-green-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "full":
        return "bg-blue-100 text-blue-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "scheduled":
        return "Đã lên lịch";
      case "pending":
        return "Chờ duyệt";
      case "full":
        return "Đã đầy";
      case "cancelled":
        return "Đã hủy";
      default:
        return status;
    }
  };

  const handleApprove = async (id: number) => {
    try {
      await coordinatorApi.approveSession(id);
      toast.success("Đã phê duyệt buổi học");
      fetchSessions(); // Refresh list
    } catch (error) {
      toast.error("Không thể phê duyệt buổi học");
    }
  };

  const handleCancel = async (id: number, reason: string = "Coordinator rejected") => {
    try {
      await coordinatorApi.rejectSession(id, reason);
      toast.success("Đã từ chối buổi học");
      fetchSessions(); // Refresh list
    } catch (error) {
      toast.error("Không thể từ chối buổi học");
    }
  };

  const filteredSessions = sessions.filter(
    (s) => filter === "all" || s.status === filter
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <button
        onClick={() => navigate("/coor")}
        className="mb-4 text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-2">
        ← Quay lại trang chủ
      </button>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Quản lý lịch học
      </h1>

      {/* Stats */}
      <div className="grid md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-center mb-2">
            <Calendar className="w-10 h-10 text-blue-600" />
          </div>
          <p className="text-sm text-gray-600 mb-1">Tổng phiên học</p>
          <p className="text-3xl font-bold text-gray-900">{loading ? '...' : stats.total}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-center mb-2">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <p className="text-sm text-gray-600 mb-1">Đã lên lịch</p>
          <p className="text-3xl font-bold text-green-600">{loading ? '...' : stats.scheduled}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-center mb-2">
            <Clock className="w-10 h-10 text-yellow-600" />
          </div>
          <p className="text-sm text-gray-600 mb-1">Chờ duyệt</p>
          <p className="text-3xl font-bold text-yellow-600">{loading ? '...' : stats.pending}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-center mb-2">
            <Users className="w-10 h-10 text-purple-600" />
          </div>
          <p className="text-sm text-gray-600 mb-1">Tổng học viên</p>
          <p className="text-3xl font-bold text-blue-600">{loading ? '...' : stats.students}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setFilter("all")}
          className={`px-4 py-2 rounded-lg font-semibold ${filter === "all"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
            }`}
        >
          Tất cả
        </button>
        <button
          onClick={() => setFilter("pending")}
          className={`px-4 py-2 rounded-lg font-semibold ${filter === "pending"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
            }`}
        >
          Chờ duyệt
        </button>
        <button
          onClick={() => setFilter("scheduled")}
          className={`px-4 py-2 rounded-lg font-semibold ${filter === "scheduled"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
            }`}
        >
          Đã lên lịch
        </button>
        <button
          onClick={() => setFilter("full")}
          className={`px-4 py-2 rounded-lg font-semibold ${filter === "full"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
            }`}
        >
          Đã đầy
        </button>
      </div>

      {/* Sessions List */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Đang tải danh sách buổi học...</p>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow-md">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Không có buổi học nào</p>
          </div>
        ) : (
          filteredSessions.map((session) => (
            <div key={session.session_id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-1">
                    {session.subject_name || session.subject_code || 'N/A'}
                  </h3>
                  <p className="text-gray-600">Tutor: {session.tutor?.full_name || session.tutor_name || 'N/A'}</p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusBadge(
                    session.status
                  )}`}
                >
                  {getStatusText(session.status)}
                </span>
              </div>

              <div className="grid md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500">Ngày</p>
                  <p className="font-semibold flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {session.scheduled_date || new Date(session.start_datetime || session.created_at).toLocaleDateString('vi-VN')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Giờ</p>
                  <p className="font-semibold flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {session.start_time && session.end_time
                      ? `${session.start_time.slice(0, 5)} - ${session.end_time.slice(0, 5)}`
                      : session.start_datetime && session.end_datetime
                        ? `${new Date(session.start_datetime).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })} - ${new Date(session.end_datetime).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}`
                        : 'N/A'
                    }
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Địa điểm</p>
                  <p className="font-semibold flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {session.location || session.meeting_link || 'Online'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Học viên</p>
                  <p className="font-semibold flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    {session.students?.length || session.student_count || 0}/{session.max_students || 30}
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                {session.status === "pending" && (
                  <>
                    <button
                      onClick={() => handleApprove(session.session_id)}
                      className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition flex items-center justify-center gap-2"
                    >
                      <Check className="w-5 h-5" />
                      Phê duyệt
                    </button>
                    <button
                      onClick={() => handleCancel(session.session_id)}
                      className="flex-1 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition flex items-center justify-center gap-2"
                    >
                      <X className="w-5 h-5" />
                      Từ chối
                    </button>
                  </>
                )}
                {session.status === "scheduled" && (
                  <button className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition">
                    Xem chi tiết
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CoordinatorSessions;

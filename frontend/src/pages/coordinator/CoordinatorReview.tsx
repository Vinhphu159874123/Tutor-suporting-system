import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { Clock } from "lucide-react";
import { coordinatorApi } from "../../services/api";

interface RegistrationRequest {
  registration_id: number;
  tutor_id: number;
  tutor_name: string;
  tutor_email: string;
  tutor_bio?: string | null;
  subject_id: number;
  subject_name: string;
  subject_code: string;
  gpa: number | null;
  qualifications: string | null;
  status: "pending" | "approved" | "rejected";
  registered_at: string;
  responded_at: string | null;
  rejection_reason: string | null;
  availability?: {
    [day: string]: string[];
  };
  total_sessions?: number;
  start_date?: string | null;
  end_date?: string | null;
  max_students?: number;
}

const CoordinatorReview: React.FC = () => {
  const navigate = useNavigate();
  const [requests, setRequests] = useState<RegistrationRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "pending" | "approved" | "rejected">("pending");
  const [processingId, setProcessingId] = useState<number | null>(null);

  // Load tutor registrations
  useEffect(() => {
    loadRegistrations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  const loadRegistrations = async () => {
    setLoading(true);
    try {
      const statusFilter = filter === "all" ? "pending" : filter;
      const response: any = await coordinatorApi.getTutorRegistrations(statusFilter);
      
      let data = response.data || [];
      
      // If filter is "all", we need to fetch all statuses
      if (filter === "all") {
        const [pending, approved, rejected] = await Promise.all([
          coordinatorApi.getTutorRegistrations("pending"),
          coordinatorApi.getTutorRegistrations("approved"),
          coordinatorApi.getTutorRegistrations("rejected"),
        ]);
        data = [
          ...(pending.data || []),
          ...(approved.data || []),
          ...(rejected.data || []),
        ];
      }
      
      setRequests(data);
    } catch (error: any) {
      console.error("Failed to load registrations:", error);
      toast.error("Không thể tải danh sách đăng ký");
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (registrationId: number) => {
    if (processingId) return; // Prevent double-click
    
    setProcessingId(registrationId);
    try {
      await coordinatorApi.approveTutorRegistration(registrationId);
      toast.success("Đã phê duyệt đăng ký");
      loadRegistrations(); // Reload list
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Không thể phê duyệt");
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (registrationId: number) => {
    if (processingId) return; // Prevent double-click
    
    const reason = prompt("Lý do từ chối:");
    if (!reason) return;

    setProcessingId(registrationId);
    try {
      await coordinatorApi.rejectTutorRegistration(registrationId, reason);
      toast.success("Đã từ chối đăng ký");
      loadRegistrations(); // Reload list
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Không thể từ chối");
    } finally {
      setProcessingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "approved":
        return "bg-green-100 text-green-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "pending":
        return "Chờ duyệt";
      case "approved":
        return "Đã duyệt";
      case "rejected":
        return "Từ chối";
      default:
        return status;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <button
        onClick={()=> navigate("/coor")}
        className="mb-4 text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-2">
          ← Quay lại trang chủ
      </button>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Xét duyệt đăng ký Tutor
      </h1>

      {/* Filter Tabs */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setFilter("all")}
          className={`px-4 py-2 rounded-lg ${
            filter === "all"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Tất cả
        </button>
        <button
          onClick={() => setFilter("pending")}
          className={`px-4 py-2 rounded-lg ${
            filter === "pending"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Chờ duyệt {!loading && filter === "pending" && `(${requests.length})`}
        </button>
        <button
          onClick={() => setFilter("approved")}
          className={`px-4 py-2 rounded-lg ${
            filter === "approved"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Đã duyệt {!loading && filter === "approved" && `(${requests.length})`}
        </button>
        <button
          onClick={() => setFilter("rejected")}
          className={`px-4 py-2 rounded-lg ${
            filter === "rejected"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Từ chối {!loading && filter === "rejected" && `(${requests.length})`}
        </button>
      </div>

      {/* Requests List */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-500 mt-4">Đang tải...</p>
          </div>
        ) : requests.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            Không có đơn đăng ký nào
          </div>
        ) : (
          requests.map((request) => (
            <div key={request.registration_id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    {request.tutor_name}
                  </h3>
                  <p className="text-gray-600">Email: {request.tutor_email}</p>
                  <p className="text-gray-600">Tutor ID: #{request.tutor_id}</p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusBadge(
                    request.status
                  )}`}
                >
                  {getStatusText(request.status)}
                </span>
              </div>

              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500">Môn học đăng ký</p>
                  <p className="font-semibold">{request.subject_code} - {request.subject_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">GPA</p>
                  <p className="font-semibold">{request.gpa ? request.gpa.toFixed(2) : "N/A"}</p>
                </div>
              </div>

              {request.tutor_bio && (
                <div className="mb-4">
                  <p className="text-sm text-gray-500">Giới thiệu bản thân</p>
                  <p className="text-gray-700">{request.tutor_bio}</p>
                </div>
              )}

              {request.qualifications && (
                <div className="mb-4">
                  <p className="text-sm text-gray-500">Trình độ/Kinh nghiệm</p>
                  <p className="text-gray-700">{request.qualifications}</p>
                </div>
              )}

              {request.availability && Object.keys(request.availability).some(day => 
                Array.isArray(request.availability![day]) && request.availability![day].length > 0
              ) && (
                <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <Clock className="h-5 w-5 text-blue-600" />
                    <p className="text-sm font-semibold text-blue-900">Lịch rảnh đăng ký</p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {Object.entries(request.availability).map(([day, times]: [string, string[]]) => {
                      if (!Array.isArray(times) || times.length === 0) return null;
                      const dayNames: { [key: string]: string } = {
                        monday: 'Thứ Hai',
                        tuesday: 'Thứ Ba',
                        wednesday: 'Thứ Tư',
                        thursday: 'Thứ Năm',
                        friday: 'Thứ Sáu',
                        saturday: 'Thứ Bảy',
                        sunday: 'Chủ Nhật'
                      };
                      return (
                        <div key={day} className="flex items-center gap-2 text-sm">
                          <span className="font-medium text-blue-700 min-w-[90px]">{dayNames[day]}:</span>
                          <span className="text-gray-900">{times.join(', ')}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Course Schedule Information */}
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm font-semibold text-green-900 mb-2">Thông tin khóa học</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                  <div>
                    <span className="text-gray-600">Số buổi học:</span>
                    <span className="ml-2 font-medium text-gray-900">
                      {request.total_sessions || 10} buổi
                    </span>
                  </div>
                  {request.start_date && (
                    <div>
                      <span className="text-gray-600">Ngày bắt đầu:</span>
                      <span className="ml-2 font-medium text-gray-900">
                        {new Date(request.start_date).toLocaleDateString("vi-VN")}
                      </span>
                    </div>
                  )}
                  {request.max_students && (
                    <div>
                      <span className="text-gray-600">Số sinh viên tối đa:</span>
                      <span className="ml-2 font-medium text-gray-900">
                        {request.max_students} sinh viên/buổi
                      </span>
                    </div>
                  )}
                  {request.end_date && (
                    <div>
                      <span className="text-gray-600">Ngày kết thúc:</span>
                      <span className="ml-2 font-medium text-gray-900">
                        {new Date(request.end_date).toLocaleDateString("vi-VN")}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <p className="text-sm text-gray-500 mb-4">
                Ngày nộp: {new Date(request.registered_at).toLocaleString("vi-VN")}
              </p>

              {request.rejection_reason && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
                  <p className="text-sm text-gray-500">Lý do từ chối:</p>
                  <p className="text-red-700">{request.rejection_reason}</p>
                </div>
              )}

              {request.status === "pending" && (
                <div className="flex gap-2">
                  <button
                    onClick={() => handleApprove(request.registration_id)}
                    disabled={processingId !== null}
                    className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {processingId === request.registration_id ? "Đang xử lý..." : "✓ Phê duyệt"}
                  </button>
                  <button
                    onClick={() => handleReject(request.registration_id)}
                    disabled={processingId !== null}
                    className="flex-1 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {processingId === request.registration_id ? "Đang xử lý..." : "✗ Từ chối"}
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CoordinatorReview;

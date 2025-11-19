import React, { useState } from "react";
import { toast } from "react-toastify";

interface RegistrationRequest {
  id: string;
  studentName: string;
  studentId: string;
  email: string;
  department: string;
  courseRequested: string;
  submittedAt: string;
  status: "pending" | "approved" | "rejected";
}

const CoordinatorReview: React.FC = () => {
  const [requests, setRequests] = useState<RegistrationRequest[]>([
    {
      id: "1",
      studentName: "Nguyễn Văn A",
      studentId: "2012345",
      email: "a.nguyen@hcmut.edu.vn",
      department: "Khoa học máy tính",
      courseRequested: "CO3005 - Công nghệ phần mềm",
      submittedAt: "2025-11-15 10:30:00",
      status: "pending",
    },
    {
      id: "2",
      studentName: "Trần Thị B",
      studentId: "2012346",
      email: "b.tran@hcmut.edu.vn",
      department: "Khoa học máy tính",
      courseRequested: "CO3001 - Cấu trúc dữ liệu",
      submittedAt: "2025-11-16 14:20:00",
      status: "pending",
    },
  ]);

  const [filter, setFilter] = useState<"all" | "pending" | "approved" | "rejected">("all");

  const handleApprove = (id: string) => {
    setRequests((prev) =>
      prev.map((req) => (req.id === id ? { ...req, status: "approved" as const } : req))
    );
    toast.success("Đã phê duyệt đăng ký");
  };

  const handleReject = (id: string) => {
    setRequests((prev) =>
      prev.map((req) => (req.id === id ? { ...req, status: "rejected" as const } : req))
    );
    toast.error("Đã từ chối đăng ký");
  };

  const filteredRequests = requests.filter(
    (req) => filter === "all" || req.status === filter
  );

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
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Phê duyệt đăng ký Tutor
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
          Tất cả ({requests.length})
        </button>
        <button
          onClick={() => setFilter("pending")}
          className={`px-4 py-2 rounded-lg ${
            filter === "pending"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Chờ duyệt ({requests.filter((r) => r.status === "pending").length})
        </button>
        <button
          onClick={() => setFilter("approved")}
          className={`px-4 py-2 rounded-lg ${
            filter === "approved"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Đã duyệt ({requests.filter((r) => r.status === "approved").length})
        </button>
        <button
          onClick={() => setFilter("rejected")}
          className={`px-4 py-2 rounded-lg ${
            filter === "rejected"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Từ chối ({requests.filter((r) => r.status === "rejected").length})
        </button>
      </div>

      {/* Requests List */}
      <div className="space-y-4">
        {filteredRequests.map((request) => (
          <div key={request.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  {request.studentName}
                </h3>
                <p className="text-gray-600">MSSV: {request.studentId}</p>
                <p className="text-gray-600">Email: {request.email}</p>
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
                <p className="text-sm text-gray-500">Khoa</p>
                <p className="font-semibold">{request.department}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Môn học đăng ký</p>
                <p className="font-semibold">{request.courseRequested}</p>
              </div>
            </div>

            <p className="text-sm text-gray-500 mb-4">
              Ngày nộp: {request.submittedAt}
            </p>

            {request.status === "pending" && (
              <div className="flex gap-2">
                <button
                  onClick={() => handleApprove(request.id)}
                  className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
                >
                  ✓ Phê duyệt
                </button>
                <button
                  onClick={() => handleReject(request.id)}
                  className="flex-1 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition"
                >
                  ✗ Từ chối
                </button>
              </div>
            )}
          </div>
        ))}

        {filteredRequests.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            Không có yêu cầu nào
          </div>
        )}
      </div>
    </div>
  );
};

export default CoordinatorReview;

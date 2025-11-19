import React, { useState } from "react";
import { toast } from "react-toastify";

const CoordinatorSessions: React.FC = () => {
  const [sessions] = useState([
    {
      id: "1",
      tutorName: "TS. Nguyễn Văn A",
      courseName: "CO3005 - Công nghệ phần mềm",
      date: "2025-11-20",
      time: "14:00 - 16:00",
      location: "H1-101",
      studentsEnrolled: 25,
      maxStudents: 30,
      status: "scheduled",
    },
    {
      id: "2",
      tutorName: "TS. Trần Thị B",
      courseName: "CO3001 - Cấu trúc dữ liệu",
      date: "2025-11-21",
      time: "09:00 - 11:00",
      location: "H2-203",
      studentsEnrolled: 30,
      maxStudents: 30,
      status: "full",
    },
    {
      id: "3",
      tutorName: "TS. Lê Văn C",
      courseName: "CO2003 - Lập trình OOP",
      date: "2025-11-22",
      time: "15:00 - 17:00",
      location: "Online",
      studentsEnrolled: 18,
      maxStudents: 25,
      status: "pending",
    },
  ]);

  const [filter, setFilter] = useState<string>("all");

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

  const handleApprove = (id: string) => {
    toast.success("Đã phê duyệt session");
  };

  const handleCancel = (id: string) => {
    toast.error("Đã hủy session");
  };

  const filteredSessions = sessions.filter(
    (s) => filter === "all" || s.status === filter
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Quản lý lịch học - Coordinator
      </h1>

      {/* Stats */}
      <div className="grid md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-3xl mb-2">📅</div>
          <p className="text-sm text-gray-600 mb-1">Tổng sessions</p>
          <p className="text-3xl font-bold text-gray-900">{sessions.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-3xl mb-2">✅</div>
          <p className="text-sm text-gray-600 mb-1">Đã lên lịch</p>
          <p className="text-3xl font-bold text-green-600">
            {sessions.filter((s) => s.status === "scheduled").length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-3xl mb-2">⏳</div>
          <p className="text-sm text-gray-600 mb-1">Chờ duyệt</p>
          <p className="text-3xl font-bold text-yellow-600">
            {sessions.filter((s) => s.status === "pending").length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-3xl mb-2">👥</div>
          <p className="text-sm text-gray-600 mb-1">Tổng học viên</p>
          <p className="text-3xl font-bold text-blue-600">
            {sessions.reduce((sum, s) => sum + s.studentsEnrolled, 0)}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setFilter("all")}
          className={`px-4 py-2 rounded-lg font-semibold ${
            filter === "all"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Tất cả
        </button>
        <button
          onClick={() => setFilter("pending")}
          className={`px-4 py-2 rounded-lg font-semibold ${
            filter === "pending"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Chờ duyệt
        </button>
        <button
          onClick={() => setFilter("scheduled")}
          className={`px-4 py-2 rounded-lg font-semibold ${
            filter === "scheduled"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Đã lên lịch
        </button>
        <button
          onClick={() => setFilter("full")}
          className={`px-4 py-2 rounded-lg font-semibold ${
            filter === "full"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          Đã đầy
        </button>
      </div>

      {/* Sessions List */}
      <div className="space-y-4">
        {filteredSessions.map((session) => (
          <div key={session.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-1">
                  {session.courseName}
                </h3>
                <p className="text-gray-600">Tutor: {session.tutorName}</p>
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
                <p className="font-semibold">📅 {session.date}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Giờ</p>
                <p className="font-semibold">⏰ {session.time}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Địa điểm</p>
                <p className="font-semibold">📍 {session.location}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Học viên</p>
                <p className="font-semibold">
                  👥 {session.studentsEnrolled}/{session.maxStudents}
                </p>
              </div>
            </div>

            <div className="flex gap-2">
              {session.status === "pending" && (
                <>
                  <button
                    onClick={() => handleApprove(session.id)}
                    className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
                  >
                    ✓ Phê duyệt
                  </button>
                  <button
                    onClick={() => handleCancel(session.id)}
                    className="flex-1 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition"
                  >
                    ✗ Từ chối
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
        ))}

        {filteredSessions.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            Không có session nào
          </div>
        )}
      </div>
    </div>
  );
};

export default CoordinatorSessions;

import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  ArrowLeftRight,
  CalendarDays,
  MapPin,
  NotebookPen,
  MessageSquare,
  UserRound,
  Users,
} from "lucide-react";

const StudyGroupDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const group = {
    id: id || "1",
    name: "Nhóm học Python cơ bản",
    course: "CO3001 - Lập trình Python",
    members: 5,
    maxMembers: 10,
    description:
      "Nhóm học Python từ cơ bản đến nâng cao, tập trung vào thực hành và làm project thực tế",
    createdBy: "Nguyễn Văn A",
    schedule: "T2, T4 - 18:00-20:00",
    location: "Online - Google Meet",
    status: "open",
    createdAt: "2025-11-10",
  };

  const members = [
    { id: "1", name: "Nguyễn Văn A", role: "Trưởng nhóm", joinedAt: "2025-11-10" },
    { id: "2", name: "Trần Thị B", role: "Thành viên", joinedAt: "2025-11-11" },
    { id: "3", name: "Lê Văn C", role: "Thành viên", joinedAt: "2025-11-12" },
    { id: "4", name: "Phạm Thị D", role: "Thành viên", joinedAt: "2025-11-13" },
    { id: "5", name: "Hoàng Văn E", role: "Thành viên", joinedAt: "2025-11-14" },
  ];

  const activities = [
    {
      id: "1",
      type: "meeting",
      title: "Buổi học tuần 1 - Giới thiệu Python",
      date: "2025-11-18 18:00",
      status: "upcoming",
    },
    {
      id: "2",
      type: "assignment",
      title: "Bài tập - Variables và Data Types",
      date: "2025-11-20",
      status: "active",
    },
    {
      id: "3",
      type: "discussion",
      title: "Thảo luận về project cuối khóa",
      date: "2025-11-15 20:00",
      status: "completed",
    },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-wrap gap-2 mb-4">
        <button
          onClick={() => navigate("/study-groups")}
          className="text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Quay lại danh sách
        </button>
        <button
          onClick={() => navigate("/forum")}
          className="text-gray-600 hover:text-gray-800 font-semibold flex items-center gap-2"
        >
          <ArrowLeftRight className="w-4 h-4" />
          Về Forum
        </button>
      </div>

      {/* Group Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {group.name}
            </h1>
            <p className="text-gray-600 mb-2">{group.course}</p>
            <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold">
              {group.status === "open" ? "Đang mở" : "Đã đủ"}
            </span>
          </div>
          <button className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition font-semibold">
            Tham gia nhóm
          </button>
        </div>

        <p className="text-gray-700 mb-4">{group.description}</p>

        <div className="grid md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
          <div>
            <p className="text-sm text-gray-500">Trưởng nhóm</p>
            <p className="font-semibold inline-flex items-center gap-1">
              <UserRound className="w-4 h-4" />
              {group.createdBy}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Thành viên</p>
            <p className="font-semibold inline-flex items-center gap-1">
              <Users className="w-4 h-4" />
              {group.members}/{group.maxMembers}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Lịch học</p>
            <p className="font-semibold inline-flex items-center gap-1">
              <CalendarDays className="w-4 h-4" />
              {group.schedule}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Địa điểm</p>
            <p className="font-semibold inline-flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              {group.location}
            </p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Members List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Thành viên ({members.length})
          </h2>
          <div className="space-y-3">
            {members.map((member) => (
              <div
                key={member.id}
                className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
                    <UserRound className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{member.name}</p>
                    <p className="text-sm text-gray-500">{member.role}</p>
                  </div>
                </div>
                <p className="text-sm text-gray-500">
                  Tham gia: {member.joinedAt}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Activities */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Hoạt động gần đây
          </h2>
          <div className="space-y-3">
            {activities.map((activity) => (
              <div
                key={activity.id}
                className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <div className="flex items-start gap-3">
                  <div className="text-blue-600">
                    {activity.type === "meeting" ? (
                      <CalendarDays className="w-6 h-6" />
                    ) : activity.type === "assignment" ? (
                      <NotebookPen className="w-6 h-6" />
                    ) : (
                      <MessageSquare className="w-6 h-6" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900 mb-1">
                      {activity.title}
                    </p>
                    <p className="text-sm text-gray-500">{activity.date}</p>
                    <span
                      className={`inline-block mt-2 px-2 py-1 rounded-full text-xs font-semibold ${
                        activity.status === "upcoming"
                          ? "bg-blue-100 text-blue-800"
                          : activity.status === "active"
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {activity.status === "upcoming"
                        ? "Sắp diễn ra"
                        : activity.status === "active"
                        ? "Đang diễn ra"
                        : "Đã hoàn thành"}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudyGroupDetail;

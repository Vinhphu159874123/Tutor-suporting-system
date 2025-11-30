import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import apiClient from "../../services/api";
import { ArrowLeft, CalendarDays, UserRound, Users } from "lucide-react";

interface StudyGroup {
  id: string;
  name: string;
  course: string;
  members: number;
  maxMembers: number;
  description: string;
  createdBy: string;
  schedule: string;
  status: "open" | "full" | "closed";
}

const StudyGroups: React.FC = () => {
  const navigate = useNavigate();
  const [groups, setGroups] = useState<StudyGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "open" | "full">("all");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get("/api/v1/study-groups/");
        setGroups(response.data || []);
      } catch (error: any) {
        console.error("Error fetching study groups:", error);
        toast.error("Không thể tải danh sách nhóm học");
      } finally {
        setLoading(false);
      }
    };
    
    fetchGroups();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "open":
        return "bg-green-100 text-green-800";
      case "full":
        return "bg-yellow-100 text-yellow-800";
      case "closed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "open":
        return "Đang mở";
      case "full":
        return "Đã đủ";
      case "closed":
        return "Đã đóng";
      default:
        return status;
    }
  };

  const filteredGroups = groups.filter((group) => {
    const matchesSearch =
      group.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      group.course.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === "all" || group.status === filter;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Đang tải danh sách nhóm học...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">\n      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-6">
        <div>
          <p className="text-sm uppercase tracking-wide text-blue-600 font-semibold">
            Cộng đồng học tập
          </p>
          <h1 className="text-3xl font-bold text-gray-900">Study Groups</h1>
          <p className="text-gray-500">
            Kết nối với bạn học, luyện thi và chia sẻ tài liệu theo từng môn học.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => navigate("/forum")}
            className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-50"
          >
            <ArrowLeft className="w-4 h-4" />
            Quay lại Forum
          </button>
          <button
            onClick={() => navigate("/study-groups/create")}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-semibold"
          >
            + Tạo nhóm mới
          </button>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid md:grid-cols-2 gap-4">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Tìm kiếm nhóm học..."
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <div className="flex gap-2">
            <button
              onClick={() => setFilter("all")}
              className={`flex-1 px-4 py-2 rounded-lg font-semibold ${
                filter === "all"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700"
              }`}
            >
              Tất cả
            </button>
            <button
              onClick={() => setFilter("open")}
              className={`flex-1 px-4 py-2 rounded-lg font-semibold ${
                filter === "open"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700"
              }`}
            >
              Đang mở
            </button>
            <button
              onClick={() => setFilter("full")}
              className={`flex-1 px-4 py-2 rounded-lg font-semibold ${
                filter === "full"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700"
              }`}
            >
              Đã đủ
            </button>
          </div>
        </div>
      </div>

      {/* Groups List */}
      <div className="space-y-4">
        {filteredGroups.map((group) => (
          <div
            key={group.id}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer"
            onClick={() => navigate(`/study-groups/${group.id}`)}
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-1">
                  {group.name}
                </h3>
                <p className="text-gray-600 mb-2">{group.course}</p>
                <p className="text-gray-700">{group.description}</p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusBadge(
                  group.status
                )}`}
              >
                {getStatusText(group.status)}
              </span>
            </div>

            <div className="grid md:grid-cols-3 gap-4 mb-4">
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
            </div>

            <div className="flex gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  navigate(`/study-groups/${group.id}`);
                }}
                className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Xem chi tiết
              </button>
              {group.status === "open" && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    console.log("Join group:", group.id);
                  }}
                  className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
                >
                  Tham gia
                </button>
              )}
            </div>
          </div>
        ))}

        {filteredGroups.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            Không tìm thấy nhóm học nào
          </div>
        )}
      </div>
    </div>
  );
};

export default StudyGroups;

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import apiClient from "../../services/api";
import {
  ArrowLeft,
  ArrowLeftRight,
  CalendarDays,
  MapPin,
  NotebookPen,
  MessageSquare,
  UserRound,
  Users,
  Plus,
  FileText,
  X,
  Trash2,
  Download,
  Eye,
} from "lucide-react";

const StudyGroupDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [group, setGroup] = useState<any>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [activities, setActivities] = useState<any[]>([]);
  const [materials, setMaterials] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);

  // Modal states
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [showMaterialModal, setShowMaterialModal] = useState(false);
  const [showAddMemberModal, setShowAddMemberModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // Add member form
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  // Activity form
  const [activityType, setActivityType] = useState("meeting");
  const [activityTitle, setActivityTitle] = useState("");
  const [activityDesc, setActivityDesc] = useState("");
  const [activityDate, setActivityDate] = useState("");
  const [activityTime, setActivityTime] = useState("");
  const [activityLink, setActivityLink] = useState("");

  // Material form
  const [materialTitle, setMaterialTitle] = useState("");
  const [materialDesc, setMaterialDesc] = useState("");
  const [materialUrl, setMaterialUrl] = useState("");
  const [materialType, setMaterialType] = useState("pdf");
  const [materialFile, setMaterialFile] = useState<File | null>(null);
  const [uploadMode, setUploadMode] = useState<"file" | "link">("file");

  useEffect(() => {
    fetchGroupDetail();
  }, [id]);

  const fetchGroupDetail = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/study-groups/${id}`);
      const data = response.data;

      setGroup({
        id: data.id,
        name: data.name,
        course: data.course,
        members: data.members,
        maxMembers: data.maxMembers,
        description: data.description,
        createdBy: data.createdBy,
        schedule: data.schedule,
        location: data.location,
        status: data.status,
        createdAt: data.createdAt,
        is_member: data.is_member
      });

      setMembers(data.members_list || []);
      setActivities(data.activities || []);
      setMaterials(data.materials || []);
    } catch (error: any) {
      console.error("Error fetching group:", error);
      toast.error("Không thể tải thông tin nhóm");
      navigate("/study-groups");
    } finally {
      setLoading(false);
    }
  };

  const handleJoinGroup = async () => {
    try {
      setJoining(true);
      await apiClient.post(`/study-groups/${id}/join`);
      toast.success("Tham gia nhóm thành công!");
      await fetchGroupDetail();
    } catch (error: any) {
      console.error("Error joining group:", error);
      toast.error(error.response?.data?.detail || "Không thể tham gia nhóm");
    } finally {
      setJoining(false);
    }
  };

  const handleLeaveGroup = async () => {
    if (!window.confirm("Bạn có chắc muốn rời khỏi nhóm này?")) return;
    
    try {
      setJoining(true);
      await apiClient.post(`/study-groups/${id}/leave`);
      toast.success("Đã rời nhóm thành công!");
      await fetchGroupDetail();
    } catch (error: any) {
      console.error("Error leaving group:", error);
      toast.error(error.response?.data?.detail || "Không thể rời nhóm");
    } finally {
      setJoining(false);
    }
  };

  const handleCreateActivity = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await apiClient.post(`/study-groups/${id}/activities`, {
        activity_type: activityType,
        title: activityTitle,
        description: activityDesc,
        scheduled_date: activityDate,
        scheduled_time: activityTime,
        meeting_link: activityLink,
        location: activityType === "meeting" ? "Online" : ""
      });

      toast.success("Hoạt động đã được tạo!");
      setShowActivityModal(false);

      // Reset form
      setActivityTitle("");
      setActivityDesc("");
      setActivityDate("");
      setActivityTime("");
      setActivityLink("");

      await fetchGroupDetail();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Không thể tạo hoạt động");
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateMaterial = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);

      const formData = new FormData();
      formData.append("description", materialDesc || "");

      if (uploadMode === "file" && materialFile) {
        formData.append("file", materialFile);
        formData.append("title", materialTitle || materialFile.name);
      } else if (uploadMode === "link") {
        formData.append("title", materialTitle);
        formData.append("file_url", materialUrl);
        formData.append("file_type", materialType);
      } else {
        toast.error("Vui lòng chọn file hoặc nhập link");
        return;
      }

      await apiClient.post(`/study-groups/${id}/materials`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      toast.success("Tài liệu đã được thêm!");
      setShowMaterialModal(false);

      // Reset form
      setMaterialTitle("");
      setMaterialDesc("");
      setMaterialUrl("");
      setMaterialFile(null);
      setUploadMode("file");

      await fetchGroupDetail();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Không thể thêm tài liệu");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSearchUsers = async (query: string) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      setSearching(true);
      const response = await apiClient.get(`/users/search`, {
        params: { query, limit: 10 }
      });
      setSearchResults(response.data || []);
    } catch (error: any) {
      console.error("Error searching users:", error);
      toast.error("Không thể tìm kiếm người dùng");
    } finally {
      setSearching(false);
    }
  };

  const handleAddMember = async (userId: number, userName: string) => {
    try {
      await apiClient.post(`/study-groups/${id}/members`, { user_id: userId });
      toast.success(`Đã thêm ${userName} vào nhóm!`);
      setShowAddMemberModal(false);
      setSearchQuery("");
      setSearchResults([]);
      await fetchGroupDetail();
    } catch (error: any) {
      console.error("Error adding member:", error);
      toast.error(error.response?.data?.detail || "Không thể thêm thành viên");
    }
  };

  const handleDeleteMaterial = async (materialId: number) => {
    if (!window.confirm("Bạn có chắc muốn xóa tài liệu này?")) return;

    try {
      await apiClient.delete(`/study-groups/${id}/materials/${materialId}`);
      toast.success("Đã xóa tài liệu!");
      await fetchGroupDetail();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Không thể xóa tài liệu");
    }
  };

  const handleViewMaterial = async (materialId: number, title: string) => {
    try {
      const response = await apiClient.get(`/study-groups/${id}/materials/${materialId}`, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: response.headers['content-type'] || 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');

      setTimeout(() => window.URL.revokeObjectURL(url), 100);
    } catch (error: any) {
      toast.error("Không thể xem tài liệu");
      console.error("View error:", error);
    }
  };

  const handleDownloadMaterial = async (materialId: number, title: string) => {
    try {
      const response = await apiClient.get(`/study-groups/${id}/materials/${materialId}`, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: response.headers['content-type'] || 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = title;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setTimeout(() => window.URL.revokeObjectURL(url), 100);
      toast.success("Đang tải xuống...");
    } catch (error: any) {
      toast.error("Không thể tải tài liệu");
      console.error("Download error:", error);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Đang tải thông tin nhóm...</p>
        </div>
      </div>
    );
  }

  if (!group) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <p className="text-gray-600">Không tìm thấy nhóm học</p>
          <button
            onClick={() => navigate("/study-groups")}
            className="mt-4 text-blue-600 hover:underline"
          >
            Quay lại danh sách
          </button>
        </div>
      </div>
    );
  }

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
          {!group.is_member ? (
            <button
              onClick={handleJoinGroup}
              disabled={joining || group.status === "full"}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {joining ? "Đang tham gia..." : group.status === "full" ? "Nhóm đã đầy" : "Tham gia nhóm"}
            </button>
          ) : (
            <button
              onClick={handleLeaveGroup}
              disabled={joining}
              className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {joining ? "Đang xử lý..." : "Rời nhóm"}
            </button>
          )}
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
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              Thành viên ({members.length})
            </h2>
            {group.is_member && (
              <button
                onClick={() => setShowAddMemberModal(true)}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2 text-sm"
              >
                <Plus className="w-4 h-4" />
                Thêm thành viên
              </button>
            )}
          </div>
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
                  Tham gia: {member.joinedAt ? new Date(member.joinedAt).toLocaleDateString('vi-VN') : 'N/A'}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Activities */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              Hoạt động gần đây
            </h2>
            {group.is_member && (
              <button
                onClick={() => setShowActivityModal(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Thêm hoạt động
              </button>
            )}
          </div>
          <div className="space-y-3">
            {activities.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Chưa có hoạt động nào</p>
            ) : (
              activities.map((activity) => (
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
                      {activity.meeting_link && (
                        <a href={activity.meeting_link} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline">
                          Link tham gia
                        </a>
                      )}
                      <span
                        className={`inline-block mt-2 px-2 py-1 rounded-full text-xs font-semibold ${activity.status === "upcoming"
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
              ))
            )}
          </div>
        </div>
      </div>

      {/* Materials Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mt-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Tài liệu ({materials.length})
          </h2>
          {group.is_member && (
            <button
              onClick={() => setShowMaterialModal(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Thêm tài liệu
            </button>
          )}
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {materials.length === 0 ? (
            <p className="text-gray-500 text-center py-8 col-span-2">Chưa có tài liệu nào</p>
          ) : (
            materials.map((material) => (
              <div key={material.id} className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                <div className="flex items-start gap-3">
                  <FileText className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 truncate">
                      {material.title}
                    </h3>
                    {material.description && (
                      <p className="text-sm text-gray-500 line-clamp-2 mt-1">{material.description}</p>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <p className="text-xs text-gray-400">
                        Đăng bởi {material.uploader} • {new Date(material.created_at).toLocaleDateString('vi-VN')}
                      </p>
                      {material.file_size && (
                        <span className="text-xs text-gray-400">
                          • {(material.file_size / 1024).toFixed(1)} KB
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-3">
                      <button
                        onClick={() => handleViewMaterial(material.id, material.title)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        <Eye className="w-4 h-4" />
                        Xem tài liệu
                      </button>
                      <button
                        onClick={() => handleDownloadMaterial(material.id, material.title)}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
                      >
                        <Download className="w-4 h-4" />
                        Tải về
                      </button>
                      {group.is_member && (
                        <button
                          onClick={() => handleDeleteMaterial(material.id)}
                          className="ml-auto p-2 text-red-600 hover:bg-red-50 rounded-lg"
                          title="Xóa tài liệu"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Activity Modal */}
      {showActivityModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Thêm hoạt động mới</h3>
              <button onClick={() => setShowActivityModal(false)}>
                <X className="w-6 h-6" />
              </button>
            </div>
            <form onSubmit={handleCreateActivity} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Loại hoạt động</label>
                <select value={activityType} onChange={(e) => setActivityType(e.target.value)} className="w-full px-3 py-2 border rounded-lg">
                  <option value="meeting">Họp/Học tập</option>
                  <option value="assignment">Bài tập</option>
                  <option value="discussion">Thảo luận</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Tiêu đề *</label>
                <input type="text" required value={activityTitle} onChange={(e) => setActivityTitle(e.target.value)} className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Mô tả</label>
                <textarea value={activityDesc} onChange={(e) => setActivityDesc(e.target.value)} className="w-full px-3 py-2 border rounded-lg" rows={3} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Ngày</label>
                  <input type="date" value={activityDate} onChange={(e) => setActivityDate(e.target.value)} className="w-full px-3 py-2 border rounded-lg" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Giờ</label>
                  <input type="time" value={activityTime} onChange={(e) => setActivityTime(e.target.value)} className="w-full px-3 py-2 border rounded-lg" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Link tham gia</label>
                <input type="url" value={activityLink} onChange={(e) => setActivityLink(e.target.value)} placeholder="https://meet.google.com/..." className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <div className="flex gap-2">
                <button type="button" onClick={() => setShowActivityModal(false)} className="flex-1 px-4 py-2 border rounded-lg">Hủy</button>
                <button type="submit" disabled={submitting} className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400">
                  {submitting ? "Đang tạo..." : "Tạo hoạt động"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Material Modal */}
      {showMaterialModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Thêm tài liệu mới</h3>
              <button onClick={() => setShowMaterialModal(false)}>
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Upload Mode Toggle */}
            <div className="flex gap-2 mb-4">
              <button
                type="button"
                onClick={() => setUploadMode("file")}
                className={`flex-1 px-4 py-2 rounded-lg font-medium ${uploadMode === "file"
                    ? "bg-green-600 text-white"
                    : "bg-gray-100 text-gray-700"
                  }`}
              >
                Upload File
              </button>
              <button
                type="button"
                onClick={() => setUploadMode("link")}
                className={`flex-1 px-4 py-2 rounded-lg font-medium ${uploadMode === "link"
                    ? "bg-green-600 text-white"
                    : "bg-gray-100 text-gray-700"
                  }`}
              >
                Paste Link
              </button>
            </div>

            <form onSubmit={handleCreateMaterial} className="space-y-4">
              {uploadMode === "file" ? (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-1">Chọn file *</label>
                    <input
                      type="file"
                      required
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          setMaterialFile(file);
                          if (!materialTitle) setMaterialTitle(file.name);
                        }
                      }}
                      className="w-full px-3 py-2 border rounded-lg"
                      accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.zip,.rar"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Max 10MB. Hỗ trợ: PDF, Word, Excel, PowerPoint, ZIP
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Tiêu đề</label>
                    <input
                      type="text"
                      value={materialTitle}
                      onChange={(e) => setMaterialTitle(e.target.value)}
                      placeholder="Tự động lấy tên file..."
                      className="w-full px-3 py-2 border rounded-lg"
                    />
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-1">Tiêu đề *</label>
                    <input
                      type="text"
                      required
                      value={materialTitle}
                      onChange={(e) => setMaterialTitle(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Link tài liệu *</label>
                    <input
                      type="url"
                      required
                      value={materialUrl}
                      onChange={(e) => setMaterialUrl(e.target.value)}
                      placeholder="https://drive.google.com/..."
                      className="w-full px-3 py-2 border rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Loại tài liệu</label>
                    <select
                      value={materialType}
                      onChange={(e) => setMaterialType(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg"
                    >
                      <option value="pdf">PDF</option>
                      <option value="doc">Word/Doc</option>
                      <option value="video">Video</option>
                      <option value="link">Link khác</option>
                    </select>
                  </div>
                </>
              )}

              <div>
                <label className="block text-sm font-medium mb-1">Mô tả</label>
                <textarea
                  value={materialDesc}
                  onChange={(e) => setMaterialDesc(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={2}
                />
              </div>

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setShowMaterialModal(false)}
                  className="flex-1 px-4 py-2 border rounded-lg"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                >
                  {submitting ? "Đang thêm..." : "Thêm tài liệu"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Member Modal */}
      {showAddMemberModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Thêm thành viên</h3>
              <button
                onClick={() => {
                  setShowAddMemberModal(false);
                  setSearchQuery("");
                  setSearchResults([]);
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Search input */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Tìm kiếm người dùng</label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  handleSearchUsers(e.target.value);
                }}
                placeholder="Nhập tên hoặc email..."
                className="w-full px-3 py-2 border rounded-lg"
              />
              <p className="text-xs text-gray-500 mt-1">Nhập ít nhất 2 ký tự để tìm kiếm</p>
            </div>

            {/* Search results */}
            <div className="space-y-2">
              {searching ? (
                <p className="text-center text-gray-500 py-4">Đang tìm kiếm...</p>
              ) : searchResults.length > 0 ? (
                searchResults.map((user) => (
                  <div
                    key={user.user_id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
                        <UserRound className="w-5 h-5" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">{user.full_name}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleAddMember(user.user_id, user.full_name)}
                      className="bg-green-600 text-white px-3 py-1 rounded-lg hover:bg-green-700 text-sm"
                    >
                      Thêm
                    </button>
                  </div>
                ))
              ) : searchQuery.length >= 2 ? (
                <p className="text-center text-gray-500 py-4">Không tìm thấy người dùng</p>
              ) : (
                <p className="text-center text-gray-500 py-4">Nhập tên để tìm kiếm</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudyGroupDetail;

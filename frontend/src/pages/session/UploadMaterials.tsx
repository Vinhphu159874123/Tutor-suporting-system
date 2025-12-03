import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";
import SessionBackButton from "./SessionBackButton";
import { useAuthStore } from "../../stores/authStore";
import { sessionsApi } from "../../services/api";
import {
  UploadCloud,
  FileText,
  Archive,
  FileType,
  Presentation,
  Paperclip,
  Download,
  Trash2,
  Loader,
} from "lucide-react";

interface UploadedFile {
  material_id: number;
  file_name: string;
  file_size: number;
  uploaded_at: string;
  file_type: string;
  description?: string;
}

interface Session {
  session_id: number;
  subject_name?: string;
  course_name?: string;
  title?: string;
}

const UploadMaterials: React.FC = () => {
  const { user } = useAuthStore();
  const userRole = (user?.role && user.role[0]) || "";  // Get first role from array
  const isTutor = ["tutor", "coordinator", "admin"].includes(userRole);

  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [sessionId, setSessionId] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingSessions, setLoadingSessions] = useState(true);

  // Fetch sessions when component mounts
  useEffect(() => {
    fetchMySessions();
  }, []);

  // Fetch materials when session changes
  useEffect(() => {
    if (sessionId) {
      fetchMaterials();
    } else {
      setFiles([]);
    }
  }, [sessionId]);

  const fetchMySessions = async () => {
    try {
      setLoadingSessions(true);
      const response: any = await sessionsApi.getMySessions({ mode: 'tutor' });
      setSessions(response.data || []);
    } catch (error: any) {
      console.error("Error fetching sessions:", error);
      toast.error("Không thể tải danh sách sessions");
    } finally {
      setLoadingSessions(false);
    }
  };

  const fetchMaterials = async () => {
    if (!sessionId) return;

    try {
      const response: any = await sessionsApi.getSessionMaterials(parseInt(sessionId));
      setFiles(response.data || []);
    } catch (error: any) {
      console.error("Error fetching materials:", error);
      toast.error("Không thể tải danh sách tài liệu");
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = e.target.files;

    if (!sessionId) {
      toast.error("Vui lòng chọn session trước");
      return;
    }

    if (!uploadedFiles || uploadedFiles.length === 0) return;

    setLoading(true);

    try {
      // Upload each file
      for (let i = 0; i < uploadedFiles.length; i++) {
        const file = uploadedFiles[i];

        const formData = new FormData();
        formData.append("file", file);
        formData.append("uploaded_by", user?.user_id?.toString() || "");
        if (description) {
          formData.append("description", description);
        }

        await sessionsApi.uploadMaterials(parseInt(sessionId), formData);
      }

      toast.success(`Tải lên ${uploadedFiles.length} tài liệu thành công`);
      setDescription(""); // Clear description

      // Refresh materials list
      await fetchMaterials();

      // Reset file input
      e.target.value = "";
    } catch (error: any) {
      console.error("Error uploading file:", error);
      toast.error(error.response?.data?.detail || "Không thể tải tài liệu lên");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (materialId: number) => {
    if (!sessionId) {
      toast.error("Không tìm thấy session ID");
      return;
    }

    if (!window.confirm("Bạn có chắc muốn xóa tài liệu này?")) return;

    try {
      await sessionsApi.deleteMaterial(parseInt(sessionId), materialId);
      toast.success("Xóa tài liệu thành công");

      // Refresh materials list
      await fetchMaterials();
    } catch (error: any) {
      console.error("Error deleting material:", error);
      toast.error(error.response?.data?.detail || "Không thể xóa tài liệu");
    }
  };

  const handleDownload = async (materialId: number, fileName: string) => {
    if (!sessionId) {
      toast.error("Không tìm thấy session ID");
      return;
    }

    try {
      const response: any = await sessionsApi.downloadMaterial(parseInt(sessionId), materialId);

      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success("Tải xuống thành công");
    } catch (error: any) {
      console.error("Error downloading material:", error);
      toast.error("Không thể tải xuống tài liệu");
    }
  };

  const getFileIcon = (type: string) => {
    const fileType = type?.toLowerCase() || '';

    if (fileType.includes('pdf')) {
      return <FileText className="h-5 w-5" />;
    } else if (fileType.includes('zip') || fileType.includes('rar') || fileType.includes('7z')) {
      return <Archive className="h-5 w-5" />;
    } else if (fileType.includes('doc') || fileType.includes('docx')) {
      return <FileType className="h-5 w-5" />;
    } else if (fileType.includes('ppt') || fileType.includes('pptx')) {
      return <Presentation className="h-5 w-5" />;
    } else {
      return <Paperclip className="h-5 w-5" />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('vi-VN');
  };

  if (!isTutor) {
    return (
      <div className="container mx-auto px-4 py-8">
        <SessionBackButton className="mb-6" />
        <div className="card text-center space-y-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Tính năng dành riêng cho Tutor
          </h1>
          <p className="text-gray-600">
            Chỉ tutor hoặc điều phối viên mới có thể tải tài liệu. Bạn vẫn có
            thể xem và tải tài liệu đã được chia sẻ ở mục danh sách tài liệu.
          </p>
          <Link
            to="/materials"
            className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition"
          >
            Đến danh sách tài liệu
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <SessionBackButton className="mb-6" />
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Tải lên tài liệu học tập
      </h1>

      {/* Upload Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="mb-4">
          <label
            htmlFor="session-select"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Chọn Session *
          </label>
          {loadingSessions ? (
            <div className="flex items-center gap-2 text-gray-500">
              <Loader className="h-4 w-4 animate-spin" />
              Đang tải sessions...
            </div>
          ) : (
            <select
              id="session-select"
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">-- Chọn session --</option>
              {sessions.map((session) => (
                <option key={session.session_id} value={session.session_id}>
                  Session {session.session_id} - {session.subject_name || session.course_name || session.title || 'Untitled'}
                </option>
              ))}
            </select>
          )}
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mô tả tài liệu
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Nhập mô tả về tài liệu..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
            disabled={!sessionId || loading}
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Chọn file tải lên
          </label>
          <div className={`border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition ${!sessionId || loading ? 'opacity-50 cursor-not-allowed' : ''}`}>
            <input
              type="file"
              multiple
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
              disabled={!sessionId || loading}
            />
            <label
              htmlFor="file-upload"
              className={`${!sessionId || loading ? 'cursor-not-allowed' : 'cursor-pointer'} flex flex-col items-center`}
            >
              <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                {loading ? <Loader className="h-8 w-8 animate-spin" /> : <UploadCloud className="h-8 w-8" />}
              </div>
              <p className="text-gray-600 mb-1">
                {loading ? 'Đang tải lên...' : 'Kéo thả file vào đây hoặc click để chọn'}
              </p>
              <p className="text-sm text-gray-500">
                Hỗ trợ: PDF, DOC, PPT, ZIP (tối đa 50MB)
              </p>
            </label>
          </div>
        </div>
      </div>

      {/* Uploaded Files List */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Tài liệu đã tải lên ({files.length})
        </h2>
        <div className="space-y-3">
          {files.map((file) => (
            <div
              key={file.material_id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                  {getFileIcon(file.file_type)}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{file.file_name}</p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(file.file_size)} • {formatDate(file.uploaded_at)}
                  </p>
                  {file.description && (
                    <p className="text-sm text-gray-600 mt-1">{file.description}</p>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleDownload(file.material_id, file.file_name)}
                  className="text-blue-600 hover:text-blue-700 px-4 py-2 rounded-lg hover:bg-blue-50 transition inline-flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Tải về
                </button>
                <button
                  onClick={() => handleDelete(file.material_id)}
                  className="text-red-600 hover:text-red-700 px-4 py-2 rounded-lg hover:bg-red-50 transition inline-flex items-center gap-2"
                >
                  <Trash2 className="h-4 w-4" />
                  Xóa
                </button>
              </div>
            </div>
          ))}

          {files.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              {sessionId ? 'Chưa có tài liệu nào được tải lên' : 'Vui lòng chọn session để xem tài liệu'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadMaterials;

import React, { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";
import SessionBackButton from "./SessionBackButton";
import { useAuthStore } from "../../stores/authStore";
import {
  UploadCloud,
  FileText,
  Archive,
  FileType,
  Presentation,
  Paperclip,
  Download,
  Trash2,
} from "lucide-react";

interface UploadedFile {
  id: string;
  name: string;
  size: string;
  uploadedAt: string;
  type: string;
}

const UploadMaterials: React.FC = () => {
  const { user } = useAuthStore();
  const isTutor =
    ["tutor", "coordinator", "admin"].includes(user?.role || "");
  const [files, setFiles] = useState<UploadedFile[]>([
    {
      id: "1",
      name: "Bai_giang_1.pdf",
      size: "2.5 MB",
      uploadedAt: "2025-11-15 10:30:00",
      type: "pdf",
    },
    {
      id: "2",
      name: "Code_demo.zip",
      size: "1.2 MB",
      uploadedAt: "2025-11-16 14:20:00",
      type: "zip",
    },
  ]);

  const [sessionId, setSessionId] = useState("");
  const [description, setDescription] = useState("");

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = e.target.files;
    if (uploadedFiles) {
      Array.from(uploadedFiles).forEach((file) => {
        const newFile: UploadedFile = {
          id: Date.now().toString(),
          name: file.name,
          size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
          uploadedAt: new Date().toLocaleString(),
          type: file.name.split(".").pop() || "unknown",
        };
        setFiles((prev) => [...prev, newFile]);
      });
      toast.success("Tải tài liệu lên thành công");
    }
  };

  const handleDelete = (id: string) => {
    setFiles((prev) => prev.filter((file) => file.id !== id));
    toast.info("Đã xóa tài liệu");
  };

  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "pdf":
        return <FileText className="h-5 w-5" />;
      case "zip":
      case "rar":
        return <Archive className="h-5 w-5" />;
      case "doc":
      case "docx":
        return <FileType className="h-5 w-5" />;
      case "ppt":
      case "pptx":
        return <Presentation className="h-5 w-5" />;
      default:
        return <Paperclip className="h-5 w-5" />;
    }
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
            Chọn Session
          </label>
          <select
            id="session-select"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">-- Chọn session --</option>
            <option value="1">Session 1 - Giới thiệu Python cơ bản</option>
            <option value="2">Session 2 - OOP trong Python</option>
            <option value="3">Session 3 - Data Structures</option>
          </select>
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
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Chọn file tải lên
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition">
            <input
              type="file"
              multiple
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center"
            >
              <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                <UploadCloud className="h-8 w-8" />
              </div>
              <p className="text-gray-600 mb-1">
                Kéo thả file vào đây hoặc click để chọn
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
              key={file.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                  {getFileIcon(file.type)}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {file.size} • {file.uploadedAt}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="text-blue-600 hover:text-blue-700 px-4 py-2 rounded-lg hover:bg-blue-50 transition inline-flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  Tải về
                </button>
                <button
                  onClick={() => handleDelete(file.id)}
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
              Chưa có tài liệu nào được tải lên
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadMaterials;

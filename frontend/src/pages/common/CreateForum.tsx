import React, { useState } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import apiClient from "../../services/api";

const CreateForum: React.FC = () => {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    category: "",
    content: "",
    tags: "",
    isPinned: false,
    allowComments: true,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title || !formData.category || !formData.content) {
      toast.error("Vui lòng điền đầy đủ thông tin");
      return;
    }

    setIsSubmitting(true);
    
    try {
      const response = await apiClient.post("/forum/posts", {
        title: formData.title,
        content: formData.content,
        category: formData.category,
        is_pinned: formData.isPinned,
        forum_id: 1  // Default forum
      });
      
      toast.success("Tạo bài viết thành công!");
      navigate("/forum");
    } catch (error: any) {
      console.error("Error creating post:", error);
      toast.error(error?.response?.data?.detail || "Không thể tạo bài viết");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Tạo chủ đề mới
      </h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6">
        {/* Title */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tiêu đề <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Nhập tiêu đề chủ đề..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Category */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Danh mục <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.category}
            onChange={(e) =>
              setFormData({ ...formData, category: e.target.value })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">-- Chọn danh mục --</option>
            <option value="study">Học tập</option>
            <option value="exam">Ôn thi</option>
            <option value="project">Dự án</option>
            <option value="career">Nghề nghiệp</option>
            <option value="other">Khác</option>
          </select>
        </div>

        {/* Content */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nội dung <span className="text-red-500">*</span>
          </label>
          <textarea
            value={formData.content}
            onChange={(e) =>
              setFormData({ ...formData, content: e.target.value })
            }
            placeholder="Nhập nội dung chi tiết..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={8}
          />
        </div>

        {/* Tags */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags (phân cách bằng dấu phẩy)
          </label>
          <input
            type="text"
            value={formData.tags}
            onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
            placeholder="Ví dụ: python, web development, database"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Options */}
        <div className="mb-6 space-y-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.isPinned}
              onChange={(e) =>
                setFormData({ ...formData, isPinned: e.target.checked })
              }
              className="mr-2"
            />
            Ghim bài viết lên đầu
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.allowComments}
              onChange={(e) =>
                setFormData({ ...formData, allowComments: e.target.checked })
              }
              className="mr-2"
            />
            Cho phép bình luận
          </label>
        </div>

        {/* Buttons */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? "Đang đăng..." : "Đăng bài"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/forum")}
            disabled={isSubmitting}
            className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 transition font-semibold disabled:opacity-50"
          >
            Hủy
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateForum;

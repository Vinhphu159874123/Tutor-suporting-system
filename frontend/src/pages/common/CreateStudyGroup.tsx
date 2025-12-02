import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import apiClient from "../../services/api";
import { ArrowLeft } from "lucide-react";

interface Subject {
  subject_id: number;
  subject_code: string;
  subject_name: string;
}

const CreateStudyGroup: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [formData, setFormData] = useState({
    group_name: "",
    subject_id: "",
    description: "",
    topic: "",
    max_members: 10,
    is_public: true,
    require_approval: false,
  });

  useEffect(() => {
    // Fetch subjects for dropdown
    const fetchSubjects = async () => {
      try {
        const response = await apiClient.get("/courses/subjects");
        setSubjects(response.data || []);
      } catch (error) {
        console.error("Error fetching subjects:", error);
      }
    };
    fetchSubjects();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.subject-search-container')) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.group_name.trim()) {
      toast.error("Vui lòng nhập tên nhóm");
      return;
    }

    if (!formData.subject_id) {
      toast.error("Vui lòng chọn môn học");
      return;
    }

    try {
      setLoading(true);
      await apiClient.post("/study-groups/", {
        ...formData,
        subject_id: parseInt(formData.subject_id),
      });
      toast.success("Tạo nhóm học thành công!");
      navigate("/study-groups");
    } catch (error: any) {
      console.error("Error creating study group:", error);
      toast.error(
        error.response?.data?.detail || "Không thể tạo nhóm học. Vui lòng thử lại!"
      );
    } finally {
      setLoading(false);
    }
  };

  const filteredSubjects = subjects.filter((subject) =>
    `${subject.subject_code} ${subject.subject_name}`
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  const selectedSubject = subjects.find(
    (s) => s.subject_id.toString() === formData.subject_id
  );

  const handleSubjectSelect = (subject: Subject) => {
    setFormData((prev) => ({ ...prev, subject_id: subject.subject_id.toString() }));
    setSearchTerm(`${subject.subject_code} - ${subject.subject_name}`);
    setShowDropdown(false);
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate("/study-groups")}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Quay lại danh sách nhóm
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Tạo Nhóm Học Mới</h1>
          <p className="text-gray-600 mt-2">
            Tạo nhóm học để cùng nhau học tập và chia sẻ kiến thức
          </p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <form onSubmit={handleSubmit}>
            {/* Tên nhóm */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tên nhóm <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="group_name"
                value={formData.group_name}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="VD: Nhóm học Database Systems"
                required
              />
            </div>

            {/* Môn học */}
            <div className="mb-6 relative subject-search-container">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Môn học <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setShowDropdown(true);
                  if (!e.target.value) {
                    setFormData((prev) => ({ ...prev, subject_id: "" }));
                  }
                }}
                onFocus={() => setShowDropdown(true)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Gõ để tìm kiếm môn học..."
                required
              />
              {showDropdown && searchTerm && filteredSubjects.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {filteredSubjects.map((subject) => (
                    <div
                      key={subject.subject_id}
                      onClick={() => handleSubjectSelect(subject)}
                      className="px-4 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                    >
                      <div className="font-medium text-gray-900">
                        {subject.subject_code}
                      </div>
                      <div className="text-sm text-gray-600">
                        {subject.subject_name}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {showDropdown && searchTerm && filteredSubjects.length === 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-4 text-center text-gray-500">
                  Không tìm thấy môn học
                </div>
              )}
            </div>

            {/* Mô tả */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mô tả nhóm
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Mô tả về nhóm học, mục đích, yêu cầu thành viên..."
              />
            </div>

            {/* Chủ đề/Lịch học */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Chủ đề/Lịch học
              </label>
              <input
                type="text"
                name="topic"
                value={formData.topic}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="VD: Thứ 2, 4, 6 - 18:00-20:00"
              />
            </div>

            {/* Số thành viên tối đa */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Số thành viên tối đa
              </label>
              <input
                type="number"
                name="max_members"
                value={formData.max_members}
                onChange={handleChange}
                min="2"
                max="50"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Công khai */}
            <div className="mb-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="is_public"
                  checked={formData.is_public}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Công khai (cho phép mọi người tìm thấy nhóm)
                </span>
              </label>
            </div>

            {/* Yêu cầu duyệt */}
            <div className="mb-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="require_approval"
                  checked={formData.require_approval}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Yêu cầu duyệt thành viên (người tham gia cần được chấp nhận)
                </span>
              </label>
            </div>

            {/* Buttons */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Đang tạo..." : "Tạo Nhóm"}
              </button>
              <button
                type="button"
                onClick={() => navigate("/study-groups")}
                className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Hủy
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateStudyGroup;

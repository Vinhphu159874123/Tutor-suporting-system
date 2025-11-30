import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { toast } from "react-toastify";
import apiClient from "../../services/api";
import { ArrowLeft, Calendar, Clock, User } from "lucide-react";

const BookSession: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const tutorId = searchParams.get("tutor");
  const slot = searchParams.get("slot");

  const [loading, setLoading] = useState(false);
  const [tutor, setTutor] = useState<any>(null);
  const [formData, setFormData] = useState({
    subject_id: "",
    session_date: "",
    start_time: "",
    end_time: "",
    location: "Online - Google Meet",
    notes: "",
  });

  useEffect(() => {
    // Fetch tutor info
    const fetchTutor = async () => {
      if (!tutorId) return;
      try {
        const response = await apiClient.get(`/api/v1/tutors/${tutorId}`);
        setTutor(response.data);
      } catch (error) {
        console.error("Error fetching tutor:", error);
      }
    };
    fetchTutor();

    // Parse slot if provided (format: "Day-TimeRange")
    if (slot) {
      const [day, timeRange] = slot.split("-");
      const [start, end] = timeRange.split("-");
      setFormData((prev) => ({
        ...prev,
        start_time: start || "",
        end_time: end || "",
      }));
    }
  }, [tutorId, slot]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.subject_id || !formData.session_date || !formData.start_time || !formData.end_time) {
      toast.error("Vui lòng điền đầy đủ thông tin");
      return;
    }

    try {
      setLoading(true);
      await apiClient.post("/api/v1/sessions/", {
        tutor_id: parseInt(tutorId || "0"),
        subject_id: parseInt(formData.subject_id),
        session_date: formData.session_date,
        start_time: formData.start_time,
        end_time: formData.end_time,
        location: formData.location,
        notes: formData.notes,
      });
      toast.success("Đặt lịch học thành công!");
      navigate("/sessions");
    } catch (error: any) {
      console.error("Error booking session:", error);
      toast.error(
        error.response?.data?.detail || "Không thể đặt lịch học. Vui lòng thử lại!"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto p-6">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Quay lại
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Đặt Lịch Học</h1>
          <p className="text-gray-600 mt-2">
            Điền thông tin để đặt lịch học với gia sư
          </p>
        </div>

        {/* Tutor Info */}
        {tutor && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                {tutor.full_name?.charAt(0) || "T"}
              </div>
              <div className="ml-4">
                <h3 className="text-xl font-bold text-gray-900">
                  {tutor.full_name}
                </h3>
                <p className="text-gray-600">{tutor.major}</p>
              </div>
            </div>
          </div>
        )}

        {/* Booking Form */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <form onSubmit={handleSubmit}>
            {/* Subject */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Môn học <span className="text-red-500">*</span>
              </label>
              <select
                name="subject_id"
                value={formData.subject_id}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">-- Chọn môn học --</option>
                {(tutor?.subjects || []).map((subject: string, index: number) => (
                  <option key={index} value={index + 1}>
                    {subject}
                  </option>
                ))}
              </select>
            </div>

            {/* Session Date */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                Ngày học <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                name="session_date"
                value={formData.session_date}
                onChange={handleChange}
                min={new Date().toISOString().split("T")[0]}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {/* Time Range */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Clock className="w-4 h-4 inline mr-1" />
                  Giờ bắt đầu <span className="text-red-500">*</span>
                </label>
                <input
                  type="time"
                  name="start_time"
                  value={formData.start_time}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Clock className="w-4 h-4 inline mr-1" />
                  Giờ kết thúc <span className="text-red-500">*</span>
                </label>
                <input
                  type="time"
                  name="end_time"
                  value={formData.end_time}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            {/* Location */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Địa điểm
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Online - Google Meet"
              />
            </div>

            {/* Notes */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ghi chú
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Nội dung cần học, yêu cầu đặc biệt..."
              />
            </div>

            {/* Buttons */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Đang đặt lịch..." : "Xác nhận đặt lịch"}
              </button>
              <button
                type="button"
                onClick={() => navigate(-1)}
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

export default BookSession;

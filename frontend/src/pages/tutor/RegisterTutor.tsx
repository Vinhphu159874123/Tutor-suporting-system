import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { tutorsApi, coursesApi, sessionsApi } from "../../services/api";
import { useAuthStore } from "../../stores/authStore";
import SubjectAutocomplete from "../../components/SubjectAutocomplete";
import { FACULTY_MAJORS_MAP } from "../../utils/constants";

const DAYS_OF_WEEK = [
  { value: "monday", label: "Thứ 2" },
  { value: "tuesday", label: "Thứ 3" },
  { value: "wednesday", label: "Thứ 4" },
  { value: "thursday", label: "Thứ 5" },
  { value: "friday", label: "Thứ 6" },
  { value: "saturday", label: "Thứ 7" },
  { value: "sunday", label: "Chủ nhật" },
];

const TIME_SLOTS = [
  { value: "07:00-09:00", label: "7:00 - 9:00" },
  { value: "09:00-11:00", label: "9:00 - 11:00" },
  { value: "13:00-15:00", label: "13:00 - 15:00" },
  { value: "15:00-17:00", label: "15:00 - 17:00" },
  { value: "17:00-19:00", label: "17:00 - 19:00" },
  { value: "19:00-21:00", label: "19:00 - 21:00" },
];

const RegisterTutor: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [subjects, setSubjects] = useState<any[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>("");
  const [formData, setFormData] = useState({
    bio: "",
    gpa: "",
    qualifications: "",
    experience_years: "",
    faculty: user?.faculty || "",
    total_sessions: "10", // Default 10 sessions
    start_date: "", // Start date for teaching
    max_students: "25", // Default 25 students
  });

  // State for availability
  const [availability, setAvailability] = useState<Record<string, string[]>>({
    monday: [],
    tuesday: [],
    wednesday: [],
    thursday: [],
    friday: [],
    saturday: [],
    sunday: [],
  });

  // State for existing schedules (approved registrations)
  const [existingSchedules, setExistingSchedules] = useState<Record<string, Array<{ timeSlot: string, subjectName: string }>>>({});

  // State for registered subject IDs
  const [registeredSubjectIds, setRegisteredSubjectIds] = useState<Set<number>>(new Set());

  // Helper function to check if two time ranges overlap
  const timeRangesOverlap = (slot1: string, slot2: string): boolean => {
    const [start1, end1] = slot1.split('-');
    const [start2, end2] = slot2.split('-');

    const toMinutes = (time: string) => {
      const [hours, minutes] = time.split(':').map(Number);
      return hours * 60 + minutes;
    };

    const start1Min = toMinutes(start1);
    const end1Min = toMinutes(end1);
    const start2Min = toMinutes(start2);
    const end2Min = toMinutes(end2);

    // Two ranges overlap if: start1 < end2 AND start2 < end1
    return start1Min < end2Min && start2Min < end1Min;
  };

  // Load subjects and existing schedules on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load subjects
        const response: any = await coursesApi.getAllSubjects();
        setSubjects(response.data || []);

        // Load tutor's all registrations to check which subjects are registered
        const registrationsResponse: any = await tutorsApi.getMyRegistrations();
        const allRegs = registrationsResponse.data || [];

        const registeredIds = new Set<number>();
        for (const reg of allRegs) {
          if (reg.status === 'approved' || reg.status === 'pending') {
            registeredIds.add(reg.subject_id);
          }
        }
        setRegisteredSubjectIds(registeredIds);

        // Load actual sessions from the same API that Timetable uses
        const sessionsResponse: any = await sessionsApi.getMySessions({ mode: 'tutor' });
        const allSessions = sessionsResponse.data || [];

        // Build schedule map from actual sessions
        // Map JS day (0=Sunday, 1=Monday, ..., 6=Saturday) to our format
        const dayMap = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
        const scheduleMap: Record<string, Array<{ timeSlot: string, subjectName: string }>> = {};

        for (const session of allSessions) {
          if (session.scheduled_date && session.start_time && session.end_time) {
            // Convert scheduled_date to day of week
            const sessionDate = new Date(session.scheduled_date + 'T00:00:00');
            const dayOfWeek = dayMap[sessionDate.getDay()];

            const timeSlot = `${session.start_time.substring(0, 5)}-${session.end_time.substring(0, 5)}`;

            if (!scheduleMap[dayOfWeek]) {
              scheduleMap[dayOfWeek] = [];
            }

            scheduleMap[dayOfWeek].push({
              timeSlot: timeSlot,
              subjectName: session.subject_name || session.subject?.name || 'Môn đã đăng ký'
            });
          }
        }

        setExistingSchedules(scheduleMap);
      } catch (error) {
        console.error("Failed to load data:", error);
        toast.error("Không thể tải danh sách môn học");
      }
    };
    loadData();
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const toggleTimeSlot = (day: string, timeSlot: string) => {
    setAvailability((prev) => {
      const daySlots = prev[day] || [];
      const isSelected = daySlots.includes(timeSlot);

      return {
        ...prev,
        [day]: isSelected
          ? daySlots.filter((slot) => slot !== timeSlot)
          : [...daySlots, timeSlot],
      };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate
    if (!formData.bio) {
      toast.error("Vui lòng nhập giới thiệu bản thân!");
      return;
    }

    if (!selectedSubject) {
      toast.error("Vui lòng chọn môn học muốn dạy!");
      return;
    }

    setLoading(true);
    try {
      // Step 1: Create/Update tutor profile
      const profileData = {
        bio: formData.bio,
        faculty: formData.faculty,
        experience_years: formData.experience_years
          ? Number(formData.experience_years)
          : 0,
        availability: availability,
      };

      await tutorsApi.registerTutor(profileData);

      // Step 2: Register for the selected subject
      const subjectData = {
        subject_id: Number(selectedSubject),
        gpa: formData.gpa ? Number(formData.gpa) : undefined,
        qualifications: formData.qualifications || undefined,
        availability: availability,
        total_sessions: formData.total_sessions ? Number(formData.total_sessions) : 10,
        start_date: formData.start_date || undefined,
        max_students: formData.max_students ? Number(formData.max_students) : 25,
      };

      await tutorsApi.registerSubject(subjectData);

      toast.success(
        "Đăng ký làm Tutor thành công! Đơn đăng ký môn học đang chờ phê duyệt."
      );
      navigate("/dashboard");
    } catch (error: any) {
      console.error('Registration error:', error);
      console.error('Error response:', error.response?.data);
      toast.error(
        error.response?.data?.detail || "Đăng ký thất bại. Vui lòng thử lại!"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          Đăng ký làm Tutor
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Bio */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Giới thiệu bản thân <span className="text-red-500">*</span>
            </label>
            <textarea
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Giới thiệu về bản thân, kinh nghiệm giảng dạy, phương pháp học tập..."
              required
            />
          </div>

          {/* Subject Selection with Autocomplete */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chọn môn học muốn dạy <span className="text-red-500">*</span>
            </label>
            <SubjectAutocomplete
              subjects={subjects}
              selectedSubject={selectedSubject}
              onSelect={setSelectedSubject}
              registeredSubjectIds={registeredSubjectIds}
            />
          </div>

          {/* GPA for this subject */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Điểm GPA môn này (tùy chọn)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="4.0"
              name="gpa"
              value={formData.gpa}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ví dụ: 3.5"
            />
          </div>

          {/* Qualifications */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Trình độ/Kinh nghiệm dạy môn này (tùy chọn)
            </label>
            <textarea
              name="qualifications"
              value={formData.qualifications}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ví dụ: Đã học A+, từng làm trợ giảng, có kinh nghiệm gia sư..."
            />
          </div>

          {/* Total Sessions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Số buổi học trong khóa
            </label>
            <input
              type="number"
              min="1"
              max="100"
              name="total_sessions"
              value={formData.total_sessions}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Mặc định: 10 buổi"
            />
            <p className="text-sm text-gray-500 mt-1">
              Số buổi dự kiến trong khóa học (mặc định 10 buổi)
            </p>
          </div>

          {/* Start Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ngày bắt đầu dạy (tùy chọn)
            </label>
            <input
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-sm text-gray-500 mt-1">
              Ngày dự kiến bắt đầu giảng dạy
            </p>
          </div>

          {/* Maximum Students */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Số sinh viên tối đa mỗi buổi
            </label>
            <input
              type="number"
              min="1"
              max="35"
              name="max_students"
              value={formData.max_students}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Mặc định: 25 sinh viên"
            />
            <p className="text-sm text-gray-500 mt-1">
              Số sinh viên tối đa trong mỗi buổi học (từ 1-35, mặc định 25)
            </p>
          </div>

          {/* Availability Schedule */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Khung thời gian rảnh <span className="text-red-500">*</span>
            </label>
            <div className="border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-blue-50 to-indigo-50">
              {DAYS_OF_WEEK.map((day) => (
                <div key={day.value} className="mb-6 last:mb-0">
                  <div className="font-semibold text-gray-800 mb-3 flex items-center">
                    <span className="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
                    {day.label}
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {TIME_SLOTS.map((slot) => {
                      const isSelected = availability[day.value]?.includes(slot.value);
                      // Check for time overlap instead of exact match
                      const conflict = existingSchedules[day.value]?.find(s => timeRangesOverlap(s.timeSlot, slot.value));
                      const hasConflict = !!conflict;

                      return (
                        <div key={slot.value} className="relative group">
                          <button
                            type="button"
                            onClick={() => toggleTimeSlot(day.value, slot.value)}
                            disabled={hasConflict}
                            className={`w-full px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${hasConflict
                                ? "bg-red-100 text-red-700 border-2 border-red-400 cursor-not-allowed opacity-75"
                                : isSelected
                                  ? "bg-blue-600 text-white shadow-md hover:bg-blue-700"
                                  : "bg-white text-gray-700 border border-gray-300 hover:border-blue-400 hover:bg-blue-50"
                              }`}
                          >
                            {slot.label}
                          </button>
                          {hasConflict && (
                            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-gray-900 text-white text-xs rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                              Trùng {conflict.subjectName}
                              <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
            <p className="text-sm text-blue-600 mt-2 flex items-center">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              Click vào các khung giờ bạn có thể dạy
            </p>
          </div>

          {/* Faculty */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Khoa
            </label>
            <select
              name="faculty"
              value={formData.faculty}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">-- Chọn khoa --</option>
              {Object.keys(FACULTY_MAJORS_MAP).sort().map((faculty) => (
                <option key={faculty} value={faculty}>
                  {faculty}
                </option>
              ))}
            </select>
          </div>

          {/* Experience Years */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Số năm kinh nghiệm
            </label>
            <input
              type="number"
              name="experience_years"
              value={formData.experience_years}
              onChange={handleChange}
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0"
            />
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Đang xử lý..." : "Đăng ký"}
            </button>
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors"
            >
              Hủy
            </button>
          </div>
        </form>

        {/* Info */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <h3 className="font-medium text-blue-900 mb-2">Lưu ý:</h3>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>
              Thông tin đăng ký sẽ được admin xem xét và phê duyệt trong 1-2
              ngày làm việc
            </li>
            <li>Bạn cần cung cấp thông tin chính xác và đầy đủ</li>
            <li>
              Sau khi được phê duyệt, bạn có thể bắt đầu tạo lịch học và nhận
              học sinh
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default RegisterTutor;

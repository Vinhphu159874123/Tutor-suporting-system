import React, { useMemo, useState } from "react";
import { useAuthStore } from "../../stores/authStore";
import { toast } from "react-toastify";
import api from "../../services/api";
import {
  Edit3,
  Save,
  Ban,
  ShieldCheck,
  ShieldAlert,
  LockKeyhole,
  KeyRound,
} from "lucide-react";

const TRAINING_PROGRAMS = [
  "Chương trình Tiêu chuẩn",
  "Chương trình Kỹ sư Chất lượng cao Việt-Pháp",
  "Chương trình Tài năng",
  "Chương trình Tiên tiến",
  "Chương trình Dạy và học bằng tiếng Anh",
  "Chương trình Liên kết Cử nhân Kỹ thuật Quốc tế",
  "Chương trình Chuyển tiếp Quốc tế",
  "Chương trình Định hướng Nhật Bản",
];

const FACULTY_STRUCTURE: Record<
  string,
  { name: string; majors: string[] }
> = {
  electrical: {
    name: "Khoa Điện - Điện tử",
    majors: [
      "Thiết kế Vi mạch",
      "Kỹ thuật Điện tử - Viễn thông",
      "Kỹ thuật Điều khiển - Tự động hóa",
      "Kỹ thuật Điện",
    ],
  },
  construction: {
    name: "Khoa Kỹ thuật Xây dựng",
    majors: [
      "Kinh tế Xây dựng",
      "Kỹ thuật Xây dựng Công trình Giao thông",
      "Kỹ thuật Trắc địa - Bản đồ",
      "Kỹ thuật Xây dựng",
      "Kỹ thuật Xây dựng Công trình Thủy",
      "Kỹ thuật Xây dựng Công trình Biển",
      "Kỹ thuật Cơ sở Hạ tầng",
      "Kiến Trúc",
      "Công nghệ Kỹ thuật Vật liệu Xây dựng",
    ],
  },
  mechanical: {
    name: "Khoa Cơ khí",
    majors: [
      "Cơ - Điện tử",
      "Kỹ thuật Nhiệt",
      "Logistics & Quản lý chuỗi cung ứng",
      "Kỹ thuật Hệ thống Công nghiệp",
      "Kỹ thuật Dệt",
      "Kỹ thuật Cơ khí",
      "Kỹ thuật Dệt May",
      "Bảo dưỡng Công nghiệp",
    ],
  },
  chemical: {
    name: "Khoa Kỹ thuật Hóa học",
    majors: ["Kỹ thuật Hóa học", "Công nghệ Thực phẩm", "Công nghệ Sinh học"],
  },
  computerScience: {
    name: "Khoa Khoa học và Kỹ thuật Máy tính",
    majors: ["Kỹ thuật Máy tính", "Khoa học Máy tính"],
  },
  materials: {
    name: "Khoa Công nghệ Vật liệu",
    majors: ["Kỹ thuật Vật liệu"],
  },
  appliedSciences: {
    name: "Khoa Khoa học Ứng dụng",
    majors: ["Khoa học Dữ liệu", "Vật lý kỹ thuật", "Cơ Kỹ thuật"],
  },
  transportation: {
    name: "Khoa Kỹ thuật Giao thông",
    majors: ["Kỹ thuật Tàu thủy", "Kỹ thuật Ô tô", "Kỹ thuật Hàng không"],
  },
  industrialManagement: {
    name: "Khoa Quản lý Công nghiệp",
    majors: ["Quản lý Công nghiệp"],
  },
  geoPetroleum: {
    name: "Khoa Kỹ thuật Địa chất và Dầu khí",
    majors: ["Địa Kỹ thuật Xây dựng", "Kỹ thuật Dầu khí", "Kỹ thuật Địa chất"],
  },
  environment: {
    name: "Khoa Môi trường và Tài nguyên",
    majors: ["Quản lý Tài nguyên và Môi trường", "Kỹ thuật Môi trường"],
  },
};

const facultyOptions = Object.entries(FACULTY_STRUCTURE).map(([key, value]) => ({
  id: key,
  label: value.name,
}));

const Profile: React.FC = () => {
  const { user, setUser } = useAuthStore();
  const [isEditing, setIsEditing] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    full_name: user?.full_name || "",
    program: (user as any)?.program || "",
    faculty: user?.faculty || "",
    major: user?.major || "",
    phone: user?.phone || "",
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const availableMajors = useMemo(() => {
    const facultyEntry = facultyOptions.find(
      (option) => option.label === formData.faculty
    );
    if (!facultyEntry) return [];
    return FACULTY_STRUCTURE[facultyEntry.id].majors;
  }, [formData.faculty]);

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    try {
      const response = await api.put("/users/profile", formData);
      setUser(response.data);
      toast.success("Cập nhật thông tin thành công!");
      setIsEditing(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Cập nhật thất bại!");
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error("Mật khẩu mới không khớp!");
      return;
    }

    if (passwordData.newPassword.length < 6) {
      toast.error("Mật khẩu phải có ít nhất 6 ký tự!");
      return;
    }

    setLoading(true);
    try {
      await api.post("/auth/change-password", {
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
      });
      toast.success("Đổi mật khẩu thành công!");
      setIsChangingPassword(false);
      setPasswordData({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Đổi mật khẩu thất bại!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Thông tin cá nhân</h1>
        <p className="text-purple-100">Quản lý thông tin tài khoản của bạn</p>
      </div>

      {/* Profile Info */}
      <div className="card">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <div className="ml-4">
              <h2 className="text-2xl font-bold text-gray-900">
                {user?.full_name}
              </h2>
              <p className="text-gray-600">{user?.email}</p>
              <span className="mt-2 inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                {user?.role === "student"
                  ? "Sinh viên"
                  : user?.role === "tutor"
                  ? "Gia sư"
                  : "Admin"}
              </span>
            </div>
          </div>

          <button
            onClick={() => setIsEditing(!isEditing)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            {isEditing ? (
              <>
                <Ban className="h-4 w-4" />
                Hủy
              </>
            ) : (
              <>
                <Edit3 className="h-4 w-4" />
                Chỉnh sửa
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="profile-name" className="block text-sm font-medium text-gray-700 mb-2">
              Họ và tên
            </label>
            {isEditing ? (
              <input
                id="profile-name"
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            ) : (
              <p className="text-gray-900 font-medium">{user?.full_name}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <p className="text-gray-900 font-medium">{user?.email}</p>
            <p className="text-xs text-gray-500 mt-1">
              Email không thể thay đổi
            </p>
          </div>

          <div>
            <label
              htmlFor="profile-program"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Chương trình đào tạo
            </label>
            {isEditing ? (
              <select
                id="profile-program"
                name="program"
                value={formData.program}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="" disabled>
                  Chọn chương trình
                </option>
                {TRAINING_PROGRAMS.map((program) => (
                  <option key={program} value={program}>
                    {program}
                  </option>
                ))}
              </select>
            ) : (
              <p className="text-gray-900 font-medium">
                {formData.program || "-"}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="profile-faculty" className="block text-sm font-medium text-gray-700 mb-2">
              Khoa
            </label>
            {isEditing ? (
              <select
                id="profile-faculty"
                name="faculty"
                value={formData.faculty}
                onChange={(e) => {
                  const selected = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    faculty: selected,
                    major: "",
                  }));
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="" disabled>
                  Chọn khoa
                </option>
                {facultyOptions.map((option) => (
                  <option key={option.id} value={option.label}>
                    {option.label}
                  </option>
                ))}
              </select>
            ) : (
              <p className="text-gray-900 font-medium">
                {formData.faculty || "-"}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="profile-major" className="block text-sm font-medium text-gray-700 mb-2">
              Ngành
            </label>
            {isEditing ? (
              <select
                id="profile-major"
                name="major"
                value={formData.major}
                onChange={handleInputChange}
                disabled={!formData.faculty}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500"
              >
                <option value="" disabled>
                  {formData.faculty
                    ? "Chọn ngành"
                    : "Chọn khoa trước để xem ngành"}
                </option>
                {availableMajors.map((major: string) => (
                  <option key={major} value={major}>
                    {major}
                  </option>
                ))}
              </select>
            ) : (
              <p className="text-gray-900 font-medium">{formData.major || "-"}</p>
            )}
          </div>

          <div>
            <label htmlFor="profile-phone" className="block text-sm font-medium text-gray-700 mb-2">
              Số điện thoại
            </label>
            {isEditing ? (
              <input
                id="profile-phone"
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            ) : (
              <p className="text-gray-900 font-medium">{user?.phone || "-"}</p>
            )}
          </div>

          <div>
            <label htmlFor="profile-role" className="block text-sm font-medium text-gray-700 mb-2">
              Vai trò
            </label>
            <p className="text-gray-900 font-medium capitalize">{user?.role}</p>
          </div>
        </div>

        {isEditing && (
          <div className="mt-6 flex gap-3">
            <button
              onClick={handleSaveProfile}
              disabled={loading}
              className="inline-flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {loading ? (
                "Đang lưu..."
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  Lưu thay đổi
                </>
              )}
            </button>
            <button
              onClick={() => setIsEditing(false)}
              className="inline-flex items-center gap-2 px-6 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              <Ban className="h-4 w-4" />
              Hủy
            </button>
          </div>
        )}
      </div>

      {/* Change Password */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Đổi mật khẩu</h2>
            <p className="text-sm text-gray-600 mt-1">
              Cập nhật mật khẩu để bảo mật tài khoản
            </p>
          </div>
          <button
            onClick={() => setIsChangingPassword(!isChangingPassword)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors"
          >
            {isChangingPassword ? (
              <>
                <Ban className="h-4 w-4" />
                Hủy
              </>
            ) : (
              <>
                <KeyRound className="h-4 w-4" />
                Đổi mật khẩu
              </>
            )}
          </button>
        </div>

        {isChangingPassword && (
          <div className="space-y-4">
            <div>
              <label htmlFor="password-current" className="block text-sm font-medium text-gray-700 mb-2">
                Mật khẩu hiện tại
              </label>
              <input
                id="password-current"
                type="password"
                name="currentPassword"
                value={passwordData.currentPassword}
                onChange={handlePasswordChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="password-new" className="block text-sm font-medium text-gray-700 mb-2">
                Mật khẩu mới
              </label>
              <input
                id="password-new"
                type="password"
                name="newPassword"
                value={passwordData.newPassword}
                onChange={handlePasswordChange}
                placeholder="Ít nhất 6 ký tự"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="password-confirm" className="block text-sm font-medium text-gray-700 mb-2">
                Xác nhận mật khẩu mới
              </label>
              <input
                id="password-confirm"
                type="password"
                name="confirmPassword"
                value={passwordData.confirmPassword}
                onChange={handlePasswordChange}
                placeholder="Nhập lại mật khẩu mới"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleChangePassword}
                disabled={loading}
                className="inline-flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50"
              >
                {loading ? (
                  "Đang xử lý..."
                ) : (
                  <>
                    <LockKeyhole className="h-4 w-4" />
                    Cập nhật mật khẩu
                  </>
                )}
              </button>
              <button
                onClick={() => setIsChangingPassword(false)}
                className="inline-flex items-center gap-2 px-6 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                <Ban className="h-4 w-4" />
                Hủy
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Account Info */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Thông tin tài khoản
        </h2>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between py-2 border-b">
            <span className="text-gray-600">Trạng thái tài khoản</span>
            <span
              className={`font-medium ${
                user?.is_active ? "text-green-600" : "text-red-600"
              }`}
            >
              {user?.is_active ? (
                <span className="inline-flex items-center gap-1">
                  <ShieldCheck className="h-4 w-4" />
                  Đang hoạt động
                </span>
              ) : (
                <span className="inline-flex items-center gap-1">
                  <ShieldAlert className="h-4 w-4" />
                  Bị khóa
                </span>
              )}
            </span>
          </div>
          <div className="flex justify-between py-2 border-b">
            <span className="text-gray-600">Email đã xác thực</span>
            <span
              className={`font-medium ${
                user?.is_verified ? "text-green-600" : "text-yellow-600"
              }`}
            >
              {user?.is_verified ? "✅ Đã xác thực" : "⚠️ Chưa xác thực"}
            </span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-gray-600">Ngày tạo tài khoản</span>
            <span className="font-medium text-gray-900">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString("vi-VN")
                : "-"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;

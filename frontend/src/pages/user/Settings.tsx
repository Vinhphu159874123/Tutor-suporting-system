import React, { useState } from "react";
import { useAuthStore } from "../../stores/authStore.ts";
import { toast } from "react-toastify";

const Settings: React.FC = () => {
  const { user } = useAuthStore();

  const [notifications, setNotifications] = useState({
    email: true,
    session_reminder: true,
    new_message: true,
    marketing: false,
  });

  const [privacy, setPrivacy] = useState({
    show_profile: true,
    show_sessions: false,
    show_ratings: true,
  });

  const handleSaveNotifications = () => {
    // Save to API
    toast.success("Đã lưu cài đặt thông báo!");
  };

  const handleSavePrivacy = () => {
    // Save to API
    toast.success("Đã lưu cài đặt riêng tư!");
  };

  const handleDeleteAccount = () => {
    if (
      window.confirm(
        "Bạn có chắc muốn xóa tài khoản? Hành động này không thể hoàn tác!"
      )
    ) {
      // Call API to delete account
      toast.error("Chức năng xóa tài khoản đang được phát triển");
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Cài đặt</h1>
        <p className="text-indigo-100">
          Tùy chỉnh trải nghiệm sử dụng hệ thống
        </p>
      </div>

      {/* Notification Settings */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Cài đặt thông báo
        </h2>
        <p className="text-sm text-gray-600 mb-6">
          Quản lý các thông báo bạn muốn nhận
        </p>

        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium text-gray-900">Thông báo qua email</p>
              <p className="text-sm text-gray-600">
                Nhận thông báo quan trọng qua email
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications.email}
                onChange={(e) =>
                  setNotifications({
                    ...notifications,
                    email: e.target.checked,
                  })
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium text-gray-900">Nhắc nhở phiên học</p>
              <p className="text-sm text-gray-600">
                Nhắc nhở trước khi phiên học bắt đầu
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications.session_reminder}
                onChange={(e) =>
                  setNotifications({
                    ...notifications,
                    session_reminder: e.target.checked,
                  })
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium text-gray-900">Tin nhắn mới</p>
              <p className="text-sm text-gray-600">
                Thông báo khi có tin nhắn mới
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications.new_message}
                onChange={(e) =>
                  setNotifications({
                    ...notifications,
                    new_message: e.target.checked,
                  })
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <p className="font-medium text-gray-900">Thông tin marketing</p>
              <p className="text-sm text-gray-600">
                Nhận thông tin về tính năng mới và ưu đãi
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications.marketing}
                onChange={(e) =>
                  setNotifications({
                    ...notifications,
                    marketing: e.target.checked,
                  })
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>

        <button
          onClick={handleSaveNotifications}
          className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Lưu cài đặt
        </button>
      </div>

      {/* Privacy Settings */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quyền riêng tư</h2>
        <p className="text-sm text-gray-600 mb-6">
          Kiểm soát ai có thể xem thông tin của bạn
        </p>

        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium text-gray-900">
                Hiển thị profile công khai
              </p>
              <p className="text-sm text-gray-600">
                Người khác có thể tìm kiếm profile của bạn
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={privacy.show_profile}
                onChange={(e) =>
                  setPrivacy({ ...privacy, show_profile: e.target.checked })
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium text-gray-900">
                Hiển thị lịch sử phiên học
              </p>
              <p className="text-sm text-gray-600">
                Người khác có thể xem phiên học đã hoàn thành
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={privacy.show_sessions}
                onChange={(e) =>
                  setPrivacy({ ...privacy, show_sessions: e.target.checked })
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <p className="font-medium text-gray-900">Hiển thị đánh giá</p>
              <p className="text-sm text-gray-600">
                Hiển thị rating và reviews từ học viên
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={privacy.show_ratings}
                onChange={(e) =>
                  setPrivacy({ ...privacy, show_ratings: e.target.checked })
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>

        <button
          onClick={handleSavePrivacy}
          className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Lưu cài đặt
        </button>
      </div>

      {/* Danger Zone */}
      <div className="card border-2 border-red-200 bg-red-50">
        <h2 className="text-xl font-bold text-red-900 mb-4">
          ⚠️ Vùng nguy hiểm
        </h2>
        <p className="text-sm text-red-700 mb-6">
          Các hành động dưới đây không thể hoàn tác
        </p>

        <button
          onClick={handleDeleteAccount}
          className="px-6 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
        >
          Xóa tài khoản
        </button>
      </div>
    </div>
  );
};

export default Settings;

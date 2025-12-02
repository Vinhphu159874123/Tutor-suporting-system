import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Clock } from "lucide-react";
import { useAuthStore } from "../../stores/authStore";

const SessionExpired: React.FC = () => {
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);

  useEffect(() => {
    // Clear authentication state
    logout();
  }, [logout]);

  const handleLogin = () => {
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full text-center">
        <div className="flex justify-center mb-4">
          <Clock className="w-20 h-20 text-orange-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Phiên làm việc đã hết hạn
        </h1>
        <p className="text-gray-600 mb-6">
          Phiên đăng nhập của bạn đã hết hạn vì lý do bảo mật. Vui lòng đăng
          nhập lại để tiếp tục sử dụng hệ thống.
        </p>
        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-semibold"
        >
          Đăng nhập lại
        </button>
        <p className="text-sm text-gray-500 mt-4">
          Nếu bạn không thực hiện hành động này, vui lòng liên hệ quản trị viên
        </p>
      </div>
    </div>
  );
};

export default SessionExpired;

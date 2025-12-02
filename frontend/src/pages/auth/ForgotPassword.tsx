import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Mail } from "lucide-react";
import { toast } from "react-toastify";
import api from "../../services/api";

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.endsWith("@hcmut.edu.vn")) {
      toast.error("Vui lòng sử dụng email HCMUT!");
      return;
    }

    setLoading(true);

    try {
      await api.post("/auth/forgot-password", { email });
      setEmailSent(true);
      toast.success("Email khôi phục mật khẩu đã được gửi!");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Có lỗi xảy ra!");
    } finally {
      setLoading(false);
    }
  };

  if (emailSent) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-xl p-8 text-center">
          <div className="flex justify-center mb-4">
            <Mail className="w-20 h-20 text-blue-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Email đã được gửi!
          </h1>
          <p className="text-gray-600 mb-6">
            Chúng tôi đã gửi hướng dẫn khôi phục mật khẩu đến email{" "}
            <strong>{email}</strong>. Vui lòng kiểm tra hộp thư của bạn.
          </p>
          <div className="space-y-3">
            <Link
              to="/login"
              className="block w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Quay lại đăng nhập
            </Link>
            <button
              onClick={() => setEmailSent(false)}
              className="w-full py-3 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Gửi lại email
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-xl p-8">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🔐</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Quên mật khẩu?
          </h1>
          <p className="text-gray-600">
            Nhập email HCMUT của bạn để nhận hướng dẫn khôi phục mật khẩu
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email HCMUT
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="student@hcmut.edu.vn"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Đang gửi..." : "Gửi email khôi phục"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <Link
            to="/login"
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            ← Quay lại đăng nhập
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;

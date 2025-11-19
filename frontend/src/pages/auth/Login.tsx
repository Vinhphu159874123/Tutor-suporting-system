import React, { useState } from "react";
import { useAuthStore } from "../../stores/authStore";
import { toast } from "react-toastify";
import logoBK from "../../png/logobk.png";

const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const { login, isLoading } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      toast.error("Vui lòng nhập đầy đủ thông tin");
      return;
    }

    try {
      await login(email, password);
      toast.success("Đăng nhập thành công!");
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Đăng nhập thất bại");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Blue Header Bar */}
      <div className="bg-[#1A0F7A] text-white py-3 px-8 shadow-lg">
        <div className="container mx-auto flex items-center">
          <img src={logoBK} alt="HCMUT Logo" className="w-16 h-16 mr-4" />
          <h1 className="text-2xl font-bold tracking-wider uppercase">
            DỊCH VỤ XÁC THỰC TẬP TRUNG
          </h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 container mx-auto py-12 px-4">
        <div className="w-full mx-auto bg-white shadow-xl rounded-sm">
          <div className="flex flex-col lg:flex-row">
            {/* Left Panel - Login Form */}
            <div className="w-full lg:w-4/12 p-8 bg-white border-r border-gray-200">
              {/* Red Alert Box */}
              <div className="bg-red-50 border-l-4 border-red-600 p-4 mb-6">
                <h2 className="text-red-700 font-bold text-base">
                  Nhập thông tin tài khoản của bạn
                </h2>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Tên tài khoản
                  </label>
                  <input
                    id="email"
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-yellow-50"
                    placeholder="Nhập email hoặc username"
                    required
                  />
                </div>

                <div>
                  <label
                    htmlFor="password"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Mật khẩu
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-yellow-50"
                    placeholder="Nhập mật khẩu"
                    required
                  />
                </div>

                <div className="flex items-start pt-1">
                  <input
                    id="remember"
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label
                    htmlFor="remember"
                    className="ml-2 text-sm text-gray-600 leading-tight"
                  >
                    Cảnh báo trước khi tôi đăng nhập vào các trang web khác.
                  </label>
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="px-10 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded shadow disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isLoading ? "Đang xử lý..." : "Đăng nhập"}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setEmail("");
                      setPassword("");
                      setRememberMe(false);
                    }}
                    className="px-10 py-2.5 bg-gray-400 hover:bg-gray-500 text-white font-medium rounded shadow transition-all"
                  >
                    Xóa
                  </button>
                </div>
              </form>

              <div className="mt-4">
                <a
                  href="#forgot-password"
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  Thay đổi mật khẩu?
                </a>
              </div>
            </div>

            {/* Right Panel - Info */}
            <div className="w-full lg:w-7/12 p-8 bg-white">
              {/* Language Selector */}
              <div className="mb-8">
                <h2 className="text-base font-bold text-gray-700 mb-3">
                  Ngôn ngữ
                </h2>
                <div className="flex gap-4 text-sm">
                  <a
                    href="#vi"
                    className="text-blue-600 underline font-semibold hover:text-blue-800"
                  >
                    Tiếng Việt
                  </a>
                  <a
                    href="#en"
                    className="text-blue-600 hover:underline hover:text-blue-800"
                  >
                    Tiếng Anh
                  </a>
                </div>
              </div>

              {/* Luu y Section */}
              <div className="mb-8">
                <h3 className="text-base font-bold text-red-600 mb-4">Lưu ý</h3>
                <div className="space-y-4 text-sm text-gray-700 leading-relaxed">
                  <p>
                    Trang đăng nhập này cho phép đăng nhập một lần vào nhiều hệ
                    thống web ở Trường Đại học Bách Khoa-ĐHQG-HCM. Điều này có
                    nghĩa là bạn chỉ đăng nhập một lần cho tất cả các hệ thống
                    web có đăng ký với hệ thống xác thực quản lý truy cập tập
                    trung.
                  </p>
                  <p>
                    Bạn chỉ dùng tài khoản HCMUT để đăng nhập. Tài khoản HCMUT
                    đòi hỏi tài nguyên bao gồm họ tên, thông tin liên lạc, thư
                    điện tử,...
                  </p>
                  <p>
                    Vì vấn đề an ninh, hãy Thoát khỏi trình duyệt Web khi bạn
                    kết thúc việc truy cập các dịch vụ đòi hỏi xác thực!
                  </p>
                </div>
              </div>

              {/* Support Info */}
              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-base font-bold text-red-600 mb-3">
                  Hỗ trợ kỹ thuật
                </h3>
                <div className="text-sm text-gray-700 space-y-1">
                  <p>
                    E-mail:{" "}
                    <a
                      href="mailto:support@hcmut.edu.vn"
                      className="text-blue-600 underline hover:text-blue-800"
                    >
                      support@hcmut.edu.vn
                    </a>
                  </p>
                  <p>ĐT: (84-8) 38647256 - 7304</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t border-gray-200 py-4 text-center text-xs text-gray-600">
        <p className="mb-1">
          Bản quyền © 2011 - 2012 Trường Đại học Bách Khoa - ĐHQG-HCM.
        </p>
        <p>
          Được hỗ trợ bởi{" "}
          <a href="#" className="text-blue-600 underline hover:text-blue-800">
            Jasig CAS 3.5.1
          </a>
        </p>
      </div>
    </div>
  );
};

export default Login;

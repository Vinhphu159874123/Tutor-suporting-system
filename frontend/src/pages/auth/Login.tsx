import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import { toast } from "react-toastify";
import { AlertCircle, X, Copy, CheckCircle, User, Mail, Lock, LogIn } from "lucide-react";
import logoBK from "../../png/logobk.png";

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [showTestAccounts, setShowTestAccounts] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const { login, isLoading } = useAuthStore();

  const testAccounts = [
    {
      name: "Tài khoản Student",
      username: "student_test",
      email: "student_test",
      password: "student",
      role: "student",
      color: "blue"
    },
    {
      name: "Tài khoản Tutor",
      username: "tutor_test",
      email: "tutor_test",
      password: "tutor",
      role: "tutor",
      color: "green"
    },
    {
      name: "Tài khoản Coordinator",
      username: "coordinator_test",
      email: "coordinator_test",
      password: "coordinator",
      role: "coordinator",
      color: "purple"
    }
  ];

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
    toast.success(`Đã copy ${field}!`);
  };

  const fillCredentials = (email: string, password: string) => {
    setEmail(email);
    setPassword(password);
    setShowTestAccounts(false);
    toast.info("Đã điền thông tin đăng nhập!");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(""); // Clear previous errors

    if (!email || !password) {
      setErrorMessage("Vui lòng nhập đầy đủ thông tin");
      return;
    }

    try {
      await login(email, password);
      toast.success("Đăng nhập thành công!");
      
      // Get user from store to determine redirect
      const user = useAuthStore.getState().user;
      
      // Redirect based on role (role is now array)
      const primaryRole = user?.role?.[0] || 'student';
      switch (primaryRole) {
        case 'admin':
          navigate('/admin');
          break;
        case 'coordinator':
          navigate('/coor');
          break;
        case 'tutor':
          navigate('/dashboard');
          break;
        case 'student':
          navigate('/dashboard');
          break;
        default:
          navigate('/dashboard');
      }
    } catch (error: any) {
      const errorMsg = error?.response?.data?.detail || "Email hoặc mật khẩu không đúng";
      setErrorMessage(errorMsg);
      // Don't show toast here to avoid duplicate error messages
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Blue Header Bar */}
      <div className="bg-[#1A0F7A] text-white py-3 px-4 sm:px-8 shadow-lg">
        <div className="container mx-auto flex items-center">
          <img src={logoBK} alt="HCMUT Logo" className="w-12 h-12 sm:w-16 sm:h-16 mr-3 sm:mr-4" />
          <h1 className="text-base sm:text-2xl font-bold tracking-wider uppercase">
            DỊCH VỤ XÁC THỰC TẬP TRUNG
          </h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 container mx-auto py-12 px-4">
        <div className="w-full max-w-7xl mx-auto bg-white shadow-xl rounded-sm">
          <div className="flex flex-col lg:flex-row">
            {/* Left Panel - Login Form */}
            <div className="w-full lg:w-5/12 p-6 sm:p-8 bg-white border-r border-gray-200">
              {/* Error Alert Box */}
              {errorMessage && (
                <div className="bg-red-50 border-l-4 border-red-600 p-4 mb-6 flex items-start">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5 flex-shrink-0" />
                  <div>
                    <h2 className="text-red-700 font-bold text-base mb-1">
                      Các thông tin mà bạn cung cấp không đúng
                    </h2>
                    <p className="text-red-600 text-sm">
                      {errorMessage}
                    </p>
                  </div>
                </div>
              )}

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

              <div className="mt-4 flex items-center gap-4">
                <a
                  href="/forgot-password"
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  Quên mật khẩu?
                </a>
                <a
                  href="/landing"
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  Trang chủ
                </a>
              </div>

              {/* Test Accounts Section */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Tài khoản test
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {testAccounts.map((account, index) => {
                    const colorClasses = {
                      blue: {
                        bg: 'bg-blue-50',
                        border: 'border-blue-300',
                        text: 'text-blue-700',
                        button: 'bg-blue-600 hover:bg-blue-700'
                      },
                      green: {
                        bg: 'bg-green-50',
                        border: 'border-green-300',
                        text: 'text-green-700',
                        button: 'bg-green-600 hover:bg-green-700'
                      },
                      purple: {
                        bg: 'bg-purple-50',
                        border: 'border-purple-300',
                        text: 'text-purple-700',
                        button: 'bg-purple-600 hover:bg-purple-700'
                      }
                    };
                    const colors = colorClasses[account.color as keyof typeof colorClasses];
                    
                    return (
                      <div key={index} className={`border-2 ${colors.border} ${colors.bg} rounded-lg p-3`}>
                        <p className={`text-xs font-bold ${colors.text} mb-3 uppercase flex items-center gap-1`}>
                          <User className="w-3 h-3" />
                          {account.role}
                        </p>
                        <div className="space-y-2 mb-3">
                          <div className="flex items-center gap-1.5 text-xs text-gray-700">
                            <Mail className="w-3 h-3 flex-shrink-0" />
                            <span className="font-mono font-semibold">{account.username}</span>
                          </div>
                          <div className="flex items-center gap-1.5 text-xs text-gray-700">
                            <Lock className="w-3 h-3 flex-shrink-0" />
                            <span className="font-mono font-semibold">{"•".repeat(account.password.length)}</span>
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            fillCredentials(account.email, account.password);
                            setTimeout(() => {
                              const form = document.querySelector('form');
                              if (form) form.requestSubmit();
                            }, 100);
                          }}
                          className={`w-full px-3 py-1.5 ${colors.button} text-white rounded text-xs font-medium transition-colors flex items-center justify-center gap-1`}
                        >
                          <LogIn className="w-3 h-3" />
                          Đăng nhập
                        </button>
                      </div>
                    );
                  })}
                </div>
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
                    Vì vấn đề an ninh, hãy thoát khỏi trình duyệt Web khi bạn
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
          {" • "}
          <button 
            onClick={() => setShowTestAccounts(true)}
            className="text-blue-600 underline hover:text-blue-800 font-medium"
          >
            Xem tài khoản test
          </button>
        </p>
      </div>

      {/* Test Accounts Modal */}
      {showTestAccounts && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-t-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold mb-1">🧪 Tài khoản Test</h2>
                  <p className="text-blue-100 text-sm">Sử dụng các tài khoản mẫu để trải nghiệm hệ thống</p>
                </div>
                <button
                  onClick={() => setShowTestAccounts(false)}
                  className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              {testAccounts.map((account, index) => {
                // Define colors based on role
                const colorClasses = {
                  blue: {
                    border: 'border-blue-200',
                    bg: 'bg-blue-50/30',
                    text: 'text-blue-700',
                    badge: 'bg-blue-100 text-blue-700',
                    button: 'bg-blue-600 hover:bg-blue-700'
                  },
                  green: {
                    border: 'border-green-200',
                    bg: 'bg-green-50/30',
                    text: 'text-green-700',
                    badge: 'bg-green-100 text-green-700',
                    button: 'bg-green-600 hover:bg-green-700'
                  },
                  purple: {
                    border: 'border-purple-200',
                    bg: 'bg-purple-50/30',
                    text: 'text-purple-700',
                    badge: 'bg-purple-100 text-purple-700',
                    button: 'bg-purple-600 hover:bg-purple-700'
                  }
                };
                
                const colors = colorClasses[account.color as keyof typeof colorClasses];
                
                return (
                  <div
                    key={index}
                    className={`border-2 ${colors.border} rounded-lg p-5 hover:shadow-lg transition-all duration-200 ${colors.bg}`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className={`text-lg font-bold ${colors.text} mb-1`}>
                          {account.name}
                        </h3>
                        <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${colors.badge} capitalize`}>
                          {account.role}
                        </span>
                      </div>
                      <button
                        onClick={() => fillCredentials(account.email, account.password)}
                        className={`px-4 py-2 ${colors.button} text-white rounded-lg font-medium text-sm transition-colors`}
                      >
                        Dùng ngay
                      </button>
                    </div>

                  <div className="space-y-3 mt-4">
                    {/* Email */}
                    <div className="bg-white rounded-lg p-3 border border-gray-200">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="text-xs text-gray-500 mb-1 font-medium">Email</p>
                          <p className="text-sm font-mono text-gray-800">{account.email}</p>
                        </div>
                        <button
                          onClick={() => copyToClipboard(account.email, `email-${index}`)}
                          className="ml-3 p-2 hover:bg-gray-100 rounded-lg transition-colors"
                          title="Copy email"
                        >
                          {copiedField === `email-${index}` ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <Copy className="w-4 h-4 text-gray-500" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Password */}
                    <div className="bg-white rounded-lg p-3 border border-gray-200">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="text-xs text-gray-500 mb-1 font-medium">Mật khẩu</p>
                          <p className="text-sm font-mono text-gray-800">{account.password}</p>
                        </div>
                        <button
                          onClick={() => copyToClipboard(account.password, `password-${index}`)}
                          className="ml-3 p-2 hover:bg-gray-100 rounded-lg transition-colors"
                          title="Copy password"
                        >
                          {copiedField === `password-${index}` ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <Copy className="w-4 h-4 text-gray-500" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
              })}

              {/* Note */}
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mt-6">
                <p className="text-sm text-amber-800">
                  <strong> Lưu ý:</strong> Các tài khoản này chỉ dành cho mục đích test và demo. 
                  Dữ liệu có thể được reset bất kỳ lúc nào.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;

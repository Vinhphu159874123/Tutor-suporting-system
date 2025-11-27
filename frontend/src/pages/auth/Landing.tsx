import React from "react";
import { useNavigate } from "react-router-dom";

const Landing: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            HCMUT Tutor Support System
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Hệ thống hỗ trợ học tập dành cho sinh viên Trường Đại học Bách Khoa - ĐHQG TP.HCM
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => navigate("/login")}
              className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition text-lg font-semibold"
            >
              Đăng nhập
            </button>
            <button
              onClick={() => navigate("/register")}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg hover:bg-gray-50 transition text-lg font-semibold border-2 border-blue-600"
            >
              Đăng ký
            </button>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
            <div className="text-4xl mb-4">📅</div>
            <h3 className="text-xl font-bold mb-2">Đặt lịch học</h3>
            <p className="text-gray-600">
              Dễ dàng đặt lịch học với tutor phù hợp với thời gian của bạn
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
            <div className="text-4xl mb-4">📚</div>
            <h3 className="text-xl font-bold mb-2">Tài liệu học tập</h3>
            <p className="text-gray-600">
              Truy cập và chia sẻ tài liệu học tập chất lượng cao
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-xl font-bold mb-2">Diễn đàn & Nhóm học tập</h3>
            <p className="text-gray-600">
              Tham gia thảo luận và học nhóm cùng sinh viên khác
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold mb-2">Theo dõi tiến độ</h3>
            <p className="text-gray-600">
              Giám sát quá trình học tập, nhận phản hồi và cải thiện hiệu quả
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-16">
          <h2 className="text-3xl font-bold text-center mb-8">
            Cách hoạt động
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-blue-600">
                1
              </div>
              <h3 className="font-bold mb-2">Đăng ký tài khoản</h3>
              <p className="text-gray-600">
                Tạo tài khoản với email @hcmut.edu.vn
              </p>
            </div>

            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-blue-600">
                2
              </div>
              <h3 className="font-bold mb-2">Tìm tutor</h3>
              <p className="text-gray-600">Chọn tutor phù hợp với nhu cầu</p>
            </div>

            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-blue-600">
                3
              </div>
              <h3 className="font-bold mb-2">Đặt lịch học</h3>
              <p className="text-gray-600">
                Chọn thời gian và hình thức học tập
              </p>
            </div>

            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-blue-600">
                4
              </div>
              <h3 className="font-bold mb-2">Bắt đầu học</h3>
              <p className="text-gray-600">
                Tham gia session và nâng cao kiến thức
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-600">
          <p className="mb-2">
            © 2025 HCMUT Tutor Support System. All rights reserved.
          </p>
          <p>Trường Đại học Bách Khoa - ĐHQG TP.HCM</p>
        </div>
      </div>
    </div>
  );
};

export default Landing;

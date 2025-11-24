import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Briefcase, GraduationCap, MessageCircle, Star, UserRound } from 'lucide-react';

const TutorDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<string | null>(null);

  // Mock data - sẽ thay bằng API call
  const tutor = {
    id: Number(id),
    full_name: 'Nguyễn Văn A',
    email: 'student@hcmut.edu.vn',
    faculty: 'Khoa Khoa học & Kỹ thuật Máy tính',
    major: 'Khoa học Máy tính',
    subjects: ['Toán cao cấp A1', 'Toán cao cấp A2', 'Cấu trúc dữ liệu', 'Giải tích'],
    hourly_rate: 150000,
    rating: 4.8,
    total_sessions: 45,
    bio: 'Sinh viên năm 4 chuyên ngành Khoa học Máy tính. Có 2 năm kinh nghiệm dạy kèm các môn Toán và Lập trình. GPA 3.7/4.0. Đam mê chia sẻ kiến thức và giúp đỡ các bạn sinh viên.',
    experience: '2 năm kinh nghiệm dạy kèm',
    education: 'Sinh viên năm 4 - HCMUT',
    availability: [
      { day: 'Thứ 2', slots: ['14:00-16:00', '18:00-20:00'] },
      { day: 'Thứ 4', slots: ['14:00-16:00', '16:00-18:00'] },
      { day: 'Thứ 6', slots: ['18:00-20:00'] },
      { day: 'Thứ 7', slots: ['09:00-11:00', '14:00-16:00', '16:00-18:00'] },
    ],
    reviews: [
      {
        id: 1,
        student_name: 'Trần Văn B',
        rating: 5,
        comment: 'Giảng dạy rất tốt, dễ hiểu. Nhiệt tình hỗ trợ học sinh.',
        date: '2025-10-20',
      },
      {
        id: 2,
        student_name: 'Lê Thị C',
        rating: 4,
        comment: 'Kiến thức vững, giải thích chi tiết. Recommend!',
        date: '2025-10-15',
      },
      {
        id: 3,
        student_name: 'Phạm Văn D',
        rating: 5,
        comment: 'Tuyệt vời! Đã giúp mình hiểu rõ môn Toán cao cấp.',
        date: '2025-10-10',
      },
    ],
  };

  const handleBookSession = () => {
    if (!selectedTimeSlot) {
      alert('Vui lòng chọn khung giờ học!');
      return;
    }
    // Navigate to booking page or open booking modal
    navigate(`/sessions/book?tutor=${id}&slot=${selectedTimeSlot}`);
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
      >
        <ArrowLeft className="w-4 h-4" />
        Quay lại danh sách
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Tutor Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Profile Card */}
          <div className="card">
            <div className="flex items-start">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-4xl font-bold flex-shrink-0">
                {tutor.full_name.charAt(0)}
              </div>
              <div className="ml-6 flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {tutor.full_name}
                </h1>
                <p className="text-gray-600 mb-2">{tutor.faculty}</p>
                <p className="text-gray-600 mb-4">{tutor.major}</p>
                
                <div className="flex items-center gap-4 mb-4">
                  <div className="flex items-center">
                    <Star className="w-5 h-5 text-yellow-500 mr-1" />
                    <span className="font-semibold text-gray-900">{tutor.rating.toFixed(1)}</span>
                    <span className="text-sm text-gray-600 ml-1">
                      ({tutor.total_sessions} phiên)
                    </span>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleBookSession}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                  >
                    Đặt lịch học
                  </button>
                  <button className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2">
                    <MessageCircle className="w-4 h-4" />
                    Nhắn tin
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* About */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Giới thiệu</h2>
            <p className="text-gray-700 leading-relaxed">{tutor.bio}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              <div className="flex items-center">
                <GraduationCap className="w-6 h-6 text-blue-600 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Trình độ</p>
                  <p className="font-medium text-gray-900">{tutor.education}</p>
                </div>
              </div>
              <div className="flex items-center">
                <Briefcase className="w-6 h-6 text-indigo-600 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Kinh nghiệm</p>
                  <p className="font-medium text-gray-900">{tutor.experience}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Subjects */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Môn học dạy</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {tutor.subjects.map(subject => (
                <div key={subject} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-blue-700 font-medium">{subject}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Reviews */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Đánh giá từ học viên ({tutor.reviews.length})
            </h2>
            <div className="space-y-4">
              {tutor.reviews.map(review => (
                <div key={review.id} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-teal-600 rounded-full flex items-center justify-center text-white">
                        <UserRound className="w-5 h-5" />
                      </div>
                      <div className="ml-3">
                        <p className="font-medium text-gray-900">{review.student_name}</p>
                        <div className="flex items-center">
                          {[...Array(review.rating)].map((_, i) => (
                            <Star key={i} className="w-4 h-4 text-yellow-500" />
                          ))}
                        </div>
                      </div>
                    </div>
                    <span className="text-sm text-gray-600">{review.date}</span>
                  </div>
                  <p className="text-gray-700">{review.comment}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Availability */}
        <div className="space-y-6">
          <div className="card sticky top-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Lịch trống
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Chọn khung giờ phù hợp để đặt lịch học
            </p>

            <div className="space-y-4">
              {tutor.availability.map((schedule) => (
                <div key={schedule.day}>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    {schedule.day}
                  </h3>
                  <div className="space-y-2">
                    {schedule.slots.map((slot) => {
                      const slotKey = `${schedule.day}-${slot}`;
                      const isSelected = selectedTimeSlot === slotKey;
                      
                      return (
                        <button
                          key={slot}
                          onClick={() => setSelectedTimeSlot(slotKey)}
                          className={`w-full px-4 py-2 rounded-lg border-2 transition-all ${
                            isSelected
                              ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                              : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50'
                          }`}
                        >
                          {slot}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            {selectedTimeSlot && (
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Khung giờ đã chọn:</p>
                <p className="font-semibold text-blue-700">{selectedTimeSlot}</p>
              </div>
            )}

            <button
              onClick={handleBookSession}
              className="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Đặt lịch ngay
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TutorDetail;

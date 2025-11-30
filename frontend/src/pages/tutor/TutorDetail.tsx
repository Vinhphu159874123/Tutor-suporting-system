import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Briefcase, GraduationCap, MessageCircle, Star, UserRound } from 'lucide-react';
import { tutorsApi } from '../../services/api';
import { toast } from 'react-toastify';
import { AxiosResponse } from 'axios';

const TutorDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<string | null>(null);
  const [tutor, setTutor] = useState<any>(null);
  const [availability, setAvailability] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTutor = async () => {
      if (!id) return;
      try {
        const response = await tutorsApi.getTutor(Number(id)) as AxiosResponse<any>;
        setTutor(response.data);
        
        // Fetch availability
        try {
          const availResponse = await tutorsApi.getTutorAvailability(Number(id)) as AxiosResponse<any>;
          setAvailability(availResponse.data.availability || []);
        } catch (availError) {
          console.error('Failed to fetch availability:', availError);
          setAvailability([]);
        }
      } catch (error: any) {
        console.error('Failed to fetch tutor:', error);
        toast.error('Không thể tải thông tin gia sư');
      } finally {
        setLoading(false);
      }
    };
    fetchTutor();
  }, [id]);

  const handleBookSession = () => {
    if (!selectedTimeSlot) {
      alert('Vui lòng chọn khung giờ học!');
      return;
    }
    // Navigate to booking page or open booking modal
    navigate(`/sessions/book?tutor=${id}&slot=${selectedTimeSlot}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Đang tải...</p>
        </div>
      </div>
    );
  }

  if (!tutor) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600">Không tìm thấy gia sư</p>
          <button onClick={() => navigate(-1)} className="mt-4 text-blue-600 hover:underline">
            Quay lại
          </button>
        </div>
      </div>
    );
  }

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
                    <span className="font-semibold text-gray-900">
                      {typeof tutor.rating === 'number' ? tutor.rating.toFixed(1) : '0.0'}
                    </span>
                    <span className="text-sm text-gray-600 ml-1">
                      ({tutor.total_sessions || 0} phiên)
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
              {(tutor.subjects || []).map((subject: string) => (
                <div key={subject} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-blue-700 font-medium">{subject}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Reviews */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Đánh giá từ học viên ({(tutor.reviews || []).length})
            </h2>
            <div className="space-y-4">
              {(tutor.reviews || []).map((review: any) => (
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

            {availability.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>Gia sư chưa cập nhật lịch trống</p>
              </div>
            ) : (
              <div className="space-y-4">
                {availability.map((schedule: any) => (
                  <div key={schedule.day}>
                    <h3 className="font-semibold text-gray-900 mb-2">
                      {schedule.day}
                    </h3>
                    <div className="space-y-2">
                      {(schedule.slots || []).map((slot: string) => {
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
            )}

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

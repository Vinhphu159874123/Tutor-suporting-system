import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import SessionBackButton from './SessionBackButton';
import {
  CalendarDays,
  Clock3,
  MapPin,
  Hourglass,
  MessageCircle,
  FileText,
  CreditCard,
  Edit3,
  XCircle,
  Star,
  Download,
} from 'lucide-react';
import { sessionsApi } from '../../services/api';
import { AxiosResponse } from 'axios';

const SessionDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [rating, setRating] = useState(5);
  const [feedback, setFeedback] = useState('');
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSession = async () => {
      if (!id) return;
      try {
        const response = await sessionsApi.getSession(Number(id)) as AxiosResponse<any>;
        setSession(response.data);
      } catch (error: any) {
        console.error('Failed to fetch session:', error);
        toast.error('Không thể tải thông tin phiên học');
      } finally {
        setLoading(false);
      }
    };
    fetchSession();
  }, [id]);

  const handleCancelSession = () => {
    if (window.confirm('Bạn có chắc muốn hủy phiên học này?')) {
      // Call API to cancel
      toast.success('Đã hủy phiên học thành công');
      navigate('/sessions');
    }
  };

  const handleSubmitFeedback = () => {
    if (!feedback.trim()) {
      toast.error('Vui lòng nhập đánh giá!');
      return;
    }
    // Call API to submit feedback
    toast.success('Đã gửi đánh giá thành công!');
    setShowFeedbackModal(false);
  };

  const getStatusBadge = (status: string) => {
    const badges: any = {
      scheduled: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Đã lên lịch' },
      completed: { bg: 'bg-green-100', text: 'text-green-700', label: 'Hoàn thành' },
      cancelled: { bg: 'bg-red-100', text: 'text-red-700', label: 'Đã hủy' },
    };
    const badge = badges[status] || badges.scheduled;
    return (
      <span className={`px-3 py-1 ${badge.bg} ${badge.text} rounded-full text-sm font-medium`}>
        {badge.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Không tìm thấy phiên học</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <SessionBackButton className="w-fit" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Session Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Header */}
          <div className="card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {session.title || session.subject}
                </h1>
                <p className="text-gray-600">Phiên học #{session.session_id}</p>
              </div>
              {getStatusBadge(session.status)}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center">
              <span className="mr-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                <CalendarDays className="h-6 w-6" />
              </span>
                <div>
                  <p className="text-sm text-gray-600">Ngày học</p>
                  <p className="font-medium text-gray-900">{session.date}</p>
                </div>
              </div>
              <div className="flex items-center">
              <span className="mr-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
                <Clock3 className="h-6 w-6" />
              </span>
                <div>
                  <p className="text-sm text-gray-600">Giờ học</p>
                  <p className="font-medium text-gray-900">{session.time}</p>
                </div>
              </div>
              <div className="flex items-center">
              <span className="mr-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
                <MapPin className="h-6 w-6" />
              </span>
                <div>
                  <p className="text-sm text-gray-600">Địa điểm</p>
                  <p className="font-medium text-gray-900">{session.location}</p>
                </div>
              </div>
              <div className="flex items-center">
              <span className="mr-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-purple-50 text-purple-600">
                <Hourglass className="h-6 w-6" />
              </span>
                <div>
                  <p className="text-sm text-gray-600">Thời lượng</p>
                  <p className="font-medium text-gray-900">{session.duration} giờ</p>
                </div>
              </div>
            </div>
          </div>

          {/* Participants */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Người tham gia
            </h2>
            
            <div className="space-y-4">
              <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-lg font-bold">
                  {session.tutor_name.charAt(0)}
                </div>
                <div className="ml-4 flex-1">
                  <p className="font-medium text-gray-900">{session.tutor_name}</p>
                  <p className="text-sm text-gray-600">Gia sư</p>
                </div>
                <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-white transition-colors inline-flex items-center gap-2">
                  <MessageCircle className="h-4 w-4 text-gray-600" />
                  Nhắn tin
                </button>
              </div>

              <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-teal-600 rounded-full flex items-center justify-center text-white text-lg font-bold">
                  {session.student_name.charAt(0)}
                </div>
                <div className="ml-4 flex-1">
                  <p className="font-medium text-gray-900">{session.student_name}</p>
                  <p className="text-sm text-gray-600">Học viên</p>
                </div>
                <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-white transition-colors inline-flex items-center gap-2">
                  <MessageCircle className="h-4 w-4 text-gray-600" />
                  Nhắn tin
                </button>
              </div>
            </div>
          </div>

          {/* Notes */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Ghi chú
            </h2>
            <p className="text-gray-700">{session.notes}</p>
          </div>

          {/* Materials */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Tài liệu học tập
            </h2>
            <div className="space-y-3">
              {session.materials.map((material: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <span className="mr-3 flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                      <FileText className="h-5 w-5" />
                    </span>
                    <div>
                      <p className="font-medium text-gray-900">{material.name}</p>
                      <p className="text-sm text-gray-600">{material.size}</p>
                    </div>
                  </div>
                  <button className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center gap-2">
                    <Download className="h-4 w-4" />
                    Tải xuống
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Feedback (for completed sessions) */}
          {session.status === 'completed' && (
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Đánh giá phiên học
              </h2>
              <button
                onClick={() => setShowFeedbackModal(true)}
                className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition-all inline-flex items-center justify-center gap-2"
              >
                <Star className="h-5 w-5 text-yellow-500" />
                Để lại đánh giá
              </button>
            </div>
          )}
        </div>

        {/* Right Column - Actions & Info */}
        <div className="space-y-6">
          {/* Payment Info */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Thông tin thanh toán
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Học phí</span>
                <span className="font-medium">{session.price.toLocaleString()}đ</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Thời lượng</span>
                <span className="font-medium">{session.duration} giờ</span>
              </div>
              <div className="border-t pt-3 flex justify-between">
                <span className="font-semibold">Tổng cộng</span>
                <span className="font-bold text-green-600 text-lg">
                  {(session.price * session.duration).toLocaleString()}đ
                </span>
              </div>
            </div>
            
            {session.status === 'scheduled' && (
              <button className="w-full mt-4 bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 transition-colors inline-flex items-center justify-center gap-2">
                <CreditCard className="h-5 w-5" />
                Thanh toán
              </button>
            )}
          </div>

          {/* Actions */}
          {session.status === 'scheduled' && (
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Hành động
              </h2>
              <div className="space-y-3">
                <button className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors inline-flex items-center justify-center gap-2">
                  <Edit3 className="h-4 w-4" />
                  Sửa lịch học
                </button>
                <button
                  onClick={handleCancelSession}
                  className="w-full bg-red-600 text-white py-2 rounded-lg font-medium hover:bg-red-700 transition-colors inline-flex items-center justify-center gap-2"
                >
                  <XCircle className="h-4 w-4" />
                  Hủy phiên học
                </button>
              </div>
            </div>
          )}

          {/* Info */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Thông tin thêm
            </h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Đã tạo</span>
                <span className="font-medium">{session.created_at}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Mã phiên học</span>
                <span className="font-medium">#{session.id}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Đánh giá phiên học
            </h3>
            
            {/* Rating */}
            <div className="mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Đánh giá</p>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((starValue) => (
                  <button
                    key={starValue}
                    onClick={() => setRating(starValue)}
                    type="button"
                    aria-label={`Đánh giá ${starValue} sao`}
                    className="rounded-full p-1 transition-transform hover:scale-110"
                  >
                    <Star
                      className={`h-8 w-8 ${
                        starValue <= rating
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  </button>
                ))}
              </div>
            </div>

            {/* Feedback */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nhận xét
              </label>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Chia sẻ trải nghiệm của bạn về phiên học này..."
              />
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => setShowFeedbackModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Hủy
              </button>
              <button
                onClick={handleSubmitFeedback}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Gửi đánh giá
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionDetail;

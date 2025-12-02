import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Search, Star, BookOpen, TrendingUp, RefreshCw } from 'lucide-react';
import { coordinatorApi } from '../../services/api';
import { toast } from 'react-toastify';

interface Tutor {
  tutor_id: number;
  user_id: number;
  full_name: string;
  email: string;
  staff_code: string;
  faculty: string;
  rating: number;
  total_sessions: number;
  total_courses: number;
  is_verified: boolean;
  created_at: string;
}

const TutorsList: React.FC = () => {
  const [tutors, setTutors] = useState<Tutor[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingRatings, setUpdatingRatings] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchTutors();
  }, []);

  const fetchTutors = async () => {
    try {
      const response = await coordinatorApi.getTutors() as any;
      setTutors(response.data.tutors);
    } catch (error) {
      console.error('Failed to fetch tutors:', error);
      toast.error('Không thể tải danh sách giảng viên');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateAllRatings = async () => {
    try {
      setUpdatingRatings(true);
      const response = await coordinatorApi.updateAllTutorsRatings() as any;
      toast.success(response.data.message || 'Đã cập nhật đánh giá cho tất cả giảng viên');
      // Refresh the list to show updated ratings
      await fetchTutors();
    } catch (error) {
      console.error('Failed to update ratings:', error);
      toast.error('Không thể cập nhật đánh giá');
    } finally {
      setUpdatingRatings(false);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      fetchTutors();
      return;
    }
    
    try {
      setLoading(true);
      const response = await coordinatorApi.searchTutors(searchTerm) as any;
      setTutors(response.data.tutors);
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Tìm kiếm thất bại');
    } finally {
      setLoading(false);
    }
  };

  const viewTutorDetails = (tutorId: number) => {
    navigate(`/coordinator/tutors/${tutorId}/courses`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Users className="h-8 w-8" />
          <h1 className="text-3xl font-bold">Quản Lý Giảng Viên</h1>
        </div>
        <p className="text-blue-100">
          Xem thông tin và báo cáo của {tutors.length} giảng viên
        </p>
      </div>

      {/* Search */}
      <div className="card">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Tìm theo tên, email, mã giảng viên..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={handleSearch}
            className="btn-primary px-6"
          >
            Tìm kiếm
          </button>
          <button
            onClick={handleUpdateAllRatings}
            disabled={updatingRatings}
            className="btn-secondary px-6 flex items-center gap-2"
            title="Cập nhật đánh giá của tất cả giảng viên từ feedback"
          >
            <RefreshCw className={`h-4 w-4 ${updatingRatings ? 'animate-spin' : ''}`} />
            {updatingRatings ? 'Đang cập nhật...' : 'Cập nhật đánh giá'}
          </button>
        </div>
      </div>

      {/* Tutors Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Đang tải...</p>
        </div>
      ) : tutors.length === 0 ? (
        <div className="card text-center py-12">
          <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Không tìm thấy giảng viên nào</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tutors.map((tutor) => (
            <div
              key={tutor.tutor_id}
              className="card hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => viewTutorDetails(tutor.tutor_id)}
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {tutor.full_name}
                  </h3>
                  <p className="text-sm text-gray-500">{tutor.staff_code}</p>
                  <p className="text-sm text-gray-500">{tutor.email}</p>
                </div>
                {tutor.is_verified && (
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
                    Đã xác thực
                  </span>
                )}
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Khoa:</span>
                  <span className="font-medium">{tutor.faculty || 'N/A'}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 flex items-center gap-1">
                    <Star className="h-4 w-4" />
                    Đánh giá:
                  </span>
                  <span className="font-medium text-yellow-600">
                    {tutor.rating.toFixed(1)} / 5.0
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-600 flex items-center gap-1">
                    <BookOpen className="h-4 w-4" />
                    Môn học:
                  </span>
                  <span className="font-medium">{tutor.total_courses}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-600 flex items-center gap-1">
                    <TrendingUp className="h-4 w-4" />
                    Phiên học:
                  </span>
                  <span className="font-medium">{tutor.total_sessions}</span>
                </div>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  viewTutorDetails(tutor.tutor_id);
                }}
                className="mt-4 w-full btn-primary text-sm"
              >
                Xem chi tiết →
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TutorsList;

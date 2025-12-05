import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, Users, Star, TrendingUp, FileText, RefreshCw } from 'lucide-react';
import { coordinatorApi } from '../../services/api';
import { toast } from 'react-toastify';

interface Course {
  subject_id: number;
  subject_code: string;
  subject_name: string;
  department: string;
  total_sessions: number;
  completed_sessions: number;
  student_count: number;
  average_rating: number;
}

interface TutorInfo {
  tutor_id: number;
  full_name: string;
  email: string;
  staff_code: string;
  faculty: string;
  rating: number;
}

const TutorCourses: React.FC = () => {
  const { tutorId } = useParams<{ tutorId: string }>();
  const navigate = useNavigate();
  const [tutor, setTutor] = useState<TutorInfo | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingRating, setUpdatingRating] = useState(false);

  useEffect(() => {
    if (tutorId) {
      fetchTutorCourses();
    }
  }, [tutorId]);

  const fetchTutorCourses = async () => {
    try {
      const response = await coordinatorApi.getTutorCourses(parseInt(tutorId!)) as any;
      setTutor(response.data.tutor);
      setCourses(response.data.courses);
    } catch (error) {
      console.error('Failed to fetch tutor courses:', error);
      toast.error('Không thể tải danh sách môn học');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRating = async () => {
    try {
      setUpdatingRating(true);
      const response = await coordinatorApi.updateTutorRating(parseInt(tutorId!)) as any;
      toast.success(response.data.message || 'Đã cập nhật đánh giá');
      // Refresh to show updated rating
      await fetchTutorCourses();
    } catch (error) {
      console.error('Failed to update rating:', error);
      toast.error('Không thể cập nhật đánh giá');
    } finally {
      setUpdatingRating(false);
    }
  };

  const viewCourseDetails = (subjectId: number) => {
    navigate(`/coordinator/tutors/${tutorId}/courses/${subjectId}`);
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate('/coordinator/tutors')}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="h-5 w-5" />
        Quay lại danh sách
      </button>

      {/* Header */}
      {tutor && (
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">{tutor.full_name}</h1>
              <div className="space-y-1 text-blue-100">
                <p>Mã giảng viên: {tutor.staff_code}</p>
                <p>Email: {tutor.email}</p>
                <p>Khoa: {tutor.faculty || 'N/A'}</p>
              </div>
            </div>
            <div className="flex flex-col items-end gap-3">
              <div className="flex items-center gap-2 bg-white/20 px-4 py-2 rounded-lg">
                <Star className="h-5 w-5 text-yellow-300" />
                <span className="text-xl font-bold">{tutor.rating.toFixed(1)}</span>
              </div>
              <button
                onClick={handleUpdateRating}
                disabled={updatingRating}
                className="flex items-center gap-2 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm transition-colors"
                title="Tính lại đánh giá từ tất cả feedback"
              >
                <RefreshCw className={`h-4 w-4 ${updatingRating ? 'animate-spin' : ''}`} />
                {updatingRating ? 'Đang cập nhật...' : 'Cập nhật đánh giá'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Courses */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <BookOpen className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold">Môn Học Giảng Dạy ({courses.length})</h2>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Đang tải...</p>
          </div>
        ) : courses.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Chưa có môn học nào</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {courses.map((course) => (
              <div
                key={course.subject_id}
                className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
              >
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {course.subject_name}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {course.subject_code} • {course.department}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <p className="text-xs text-gray-600 mb-1">Tổng phiên học</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {course.total_sessions}
                    </p>
                  </div>

                  <div className="bg-green-50 p-3 rounded-lg">
                    <p className="text-xs text-gray-600 mb-1">Đã hoàn thành</p>
                    <p className="text-2xl font-bold text-green-600">
                      {course.completed_sessions}
                    </p>
                  </div>

                  <div className="bg-purple-50 p-3 rounded-lg">
                    <p className="text-xs text-gray-600 mb-1">Học viên</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {course.student_count}
                    </p>
                  </div>

                  <div className="bg-yellow-50 p-3 rounded-lg">
                    <p className="text-xs text-gray-600 mb-1">Đánh giá TB</p>
                    <div className="flex items-center gap-1">
                      <Star className="h-5 w-5 text-yellow-500" />
                      <p className="text-2xl font-bold text-yellow-600">
                        {course.average_rating.toFixed(1)}
                      </p>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => viewCourseDetails(course.subject_id)}
                  className="w-full btn-primary flex items-center justify-center gap-2"
                >
                  <FileText className="h-4 w-4" />
                  Xem báo cáo chi tiết
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TutorCourses;

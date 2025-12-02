import React, { useState, useEffect } from 'react';
import { Search, Users, Calendar, BookOpen, UserPlus, CheckCircle, ExternalLink, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { coursesApi, tutorsApi } from '../../services/api';
import { toast } from 'react-toastify';
import { useAuthStore } from '../../stores/authStore';

interface CourseOffer {
  registration_id: number;
  subject_id: number;
  subject_code: string;
  subject_name: string;
  department: string;
  tutor_id: number;
  tutor_name: string;
  total_sessions: number;
  max_students: number;
  current_students: number;
  available_slots: number;
  start_date: string | null;
  status: string;
}

const BrowseCourses: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [courses, setCourses] = useState<CourseOffer[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<CourseOffer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [departments, setDepartments] = useState<string[]>([]);
  const [enrollingId, setEnrollingId] = useState<number | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<CourseOffer | null>(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [enrollmentResult, setEnrollmentResult] = useState<{sessions_joined: number} | null>(null);

  useEffect(() => {
    fetchAvailableCourses();
  }, []);

  useEffect(() => {
    filterCourses();
  }, [searchTerm, selectedDepartment, courses]);

  const fetchAvailableCourses = async () => {
    try {
      setLoading(true);
      // Call API to get available courses (approved tutor registrations with slots)
      const response: any = await tutorsApi.getAvailableCourses();
      // Backend returns {data: [...]}
      const coursesData = response.data?.data || response.data || [];
      
      setCourses(coursesData);
      
      // Extract unique departments
      const depts = Array.from(new Set(coursesData.map((c: CourseOffer) => c.department)));
      setDepartments(depts as string[]);
      
    } catch (error) {
      console.error('Failed to fetch courses:', error);
      toast.error('Không thể tải danh sách khóa học');
    } finally {
      setLoading(false);
    }
  };

  const filterCourses = () => {
    let filtered = courses;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(course =>
        course.subject_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.subject_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.tutor_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by department
    if (selectedDepartment !== 'all') {
      filtered = filtered.filter(course => course.department === selectedDepartment);
    }

    setFilteredCourses(filtered);
  };

  const handleRequestJoin = async (course: CourseOffer) => {
    setSelectedCourse(course);
    setShowConfirmModal(true);
  };

  const confirmEnrollment = async () => {
    if (!selectedCourse) return;
    
    try {
      setEnrollingId(selectedCourse.registration_id);
      setShowConfirmModal(false);
      
      const response: any = await tutorsApi.requestJoinCourse(selectedCourse.registration_id);
      const result = response.data;
      
      setEnrollmentResult(result);
      setShowSuccessModal(true);
      
      toast.success(`Đăng ký thành công khóa ${selectedCourse.subject_name}!`);
      
      // Refresh courses to update available slots
      await fetchAvailableCourses();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Không thể đăng ký khóa học';
      toast.error(errorMsg);
    } finally {
      setEnrollingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          <BookOpen className="inline mr-2" size={32} />
          Tìm Kiếm Khóa Học
        </h1>
        <p className="text-gray-600">
          Khám phá và đăng ký các khóa học phù hợp với nhu cầu của bạn
        </p>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Tìm kiếm môn học, mã môn, giảng viên..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Department Filter */}
          <select
            value={selectedDepartment}
            onChange={(e) => setSelectedDepartment(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Tất cả khoa</option>
            {departments.map(dept => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Results */}
      <div className="text-sm text-gray-600 mb-4">
        Tìm thấy {filteredCourses.length} khóa học
      </div>

      {filteredCourses.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <BookOpen className="mx-auto text-gray-400 mb-4" size={64} />
          <p className="text-gray-600 text-lg">Không tìm thấy khóa học phù hợp</p>
          <p className="text-gray-500 text-sm mt-2">Thử thay đổi tiêu chí tìm kiếm</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map(course => (
            <div
              key={course.registration_id}
              className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden"
            >
              <div className="bg-gradient-to-r from-blue-500 to-indigo-600 p-4 text-white">
                <h3 className="font-bold text-lg mb-1">{course.subject_code}</h3>
                <p className="text-sm opacity-90">{course.subject_name}</p>
              </div>

              <div className="p-4 space-y-3">
                <div className="flex items-center text-gray-700">
                  <Users size={18} className="mr-2 text-blue-600" />
                  <span className="text-sm">
                    Giảng viên: <span className="font-medium">{course.tutor_name}</span>
                  </span>
                </div>

                <div className="flex items-center text-gray-700">
                  <Calendar size={18} className="mr-2 text-green-600" />
                  <span className="text-sm">
                    {course.total_sessions} buổi học
                  </span>
                </div>

                <div className="flex items-center text-gray-700">
                  <UserPlus size={18} className="mr-2 text-purple-600" />
                  <span className="text-sm">
                    Còn <span className="font-bold text-green-600">{course.available_slots}</span>/{course.max_students} chỗ
                  </span>
                </div>

                {course.start_date && (
                  <div className="text-sm text-gray-600">
                    Bắt đầu: {new Date(course.start_date).toLocaleDateString('vi-VN')}
                  </div>
                )}

                <div className="pt-2">
                  {course.available_slots > 0 ? (
                    <button
                      onClick={() => handleRequestJoin(course)}
                      disabled={enrollingId === course.registration_id}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {enrollingId === course.registration_id ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          Đang xử lý...
                        </>
                      ) : (
                        <>
                          <UserPlus size={18} className="mr-2" />
                          Đăng Ký Tham Gia
                        </>
                      )}
                    </button>
                  ) : (
                    <button
                      disabled
                      className="w-full bg-gray-300 text-gray-500 font-medium py-2 px-4 rounded-lg cursor-not-allowed flex items-center justify-center"
                    >
                      <CheckCircle size={18} className="mr-2" />
                      Đã Đầy
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmModal && selectedCourse && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-gray-900">Xác nhận đăng ký</h3>
              <button
                onClick={() => setShowConfirmModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="space-y-4 mb-6">
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                <h4 className="font-bold text-blue-900 mb-2">{selectedCourse.subject_code}</h4>
                <p className="text-blue-800 text-sm">{selectedCourse.subject_name}</p>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Giảng viên:</span>
                  <span className="font-medium">{selectedCourse.tutor_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Số buổi học:</span>
                  <span className="font-medium">{selectedCourse.total_sessions} buổi</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Chỗ còn trống:</span>
                  <span className="font-medium text-green-600">{selectedCourse.available_slots}/{selectedCourse.max_students}</span>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                <p className="text-sm text-yellow-800">
                  <strong>Lưu ý:</strong> Bạn sẽ được tự động thêm vào tất cả {selectedCourse.total_sessions} buổi học của khóa này.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Hủy
              </button>
              <button
                onClick={confirmEnrollment}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Xác nhận đăng ký
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Success Modal */}
      {showSuccessModal && selectedCourse && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="text-center mb-6">
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Đăng ký thành công!</h3>
              <p className="text-gray-600">
                Bạn đã đăng ký thành công khóa học <strong>{selectedCourse.subject_name}</strong>
              </p>
            </div>

            {enrollmentResult && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-green-800">Số buổi học đã đăng ký:</span>
                  <span className="font-bold text-green-900 text-lg">{enrollmentResult.sessions_joined} buổi</span>
                </div>
              </div>
            )}

            <div className="space-y-3">
              <button
                onClick={() => navigate('/my-courses')}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center"
              >
                <BookOpen size={20} className="mr-2" />
                Xem Khóa Học Của Tôi
              </button>
              <button
                onClick={() => {
                  setShowSuccessModal(false);
                  setSelectedCourse(null);
                  setEnrollmentResult(null);
                }}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Tiếp tục duyệt khóa học
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BrowseCourses;

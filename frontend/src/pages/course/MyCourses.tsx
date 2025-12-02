import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Users, Calendar, ArrowRight, GraduationCap } from 'lucide-react';
import { coursesApi } from '../../services/api';
import { useAuthStore } from '../../stores/authStore';
import { toast } from 'react-toastify';

interface Course {
  subject_id: number;
  subject_code: string;
  subject_name: string;
  department: string;
  credits: number;
  session_count?: number;
  student_count?: number;
  tutor_name?: string;
}

const MyCourses: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();

  useEffect(() => {
    fetchMyCourses();
  }, []);

  const fetchMyCourses = async () => {
    try {
      const response = await coursesApi.getMyCourses() as any;
      console.log('My Courses API Response:', response);
      console.log('Courses data:', response.data);
      setCourses(response.data);
    } catch (error) {
      console.error('Failed to fetch courses:', error);
      toast.error('Không thể tải danh sách môn học');
    } finally {
      setLoading(false);
    }
  };

  const isTutor = user?.role === 'tutor';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <div className="flex items-center gap-3 mb-2">
          <BookOpen className="h-8 w-8" />
          <h1 className="text-3xl font-bold">
            {isTutor ? 'Môn Học Tôi Dạy' : 'Môn Học Của Tôi'}
          </h1>
        </div>
        <p className="text-blue-100">
          {isTutor 
            ? `Quản lý ${courses.length} môn học bạn đang giảng dạy`
            : `Theo dõi tiến độ ${courses.length} môn học bạn đang theo học`
          }
        </p>
      </div>

      {/* Courses Grid */}
      <div className="card">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Đang tải...</p>
          </div>
        ) : courses.length === 0 ? (
          <div className="text-center py-12">
            <div className="flex justify-center mb-4">
              <BookOpen className="w-20 h-20 text-gray-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              {isTutor ? 'Chưa có môn học nào' : 'Chưa đăng ký môn học'}
            </h3>
            <p className="text-gray-600 mb-6">
              {isTutor 
                ? 'Bạn chưa được phân công dạy môn học nào'
                : 'Hãy đăng ký các môn học để bắt đầu học tập'
              }
            </p>
            {!isTutor && (
              <Link
                to="/sessions"
                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Calendar className="h-5 w-5" />
                Tìm phiên học
              </Link>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <Link
                key={course.subject_id}
                to={`/my-courses/${course.subject_id}`}
                className="block group"
              >
                <div className="h-full border-2 border-gray-200 rounded-lg p-6 hover:border-blue-500 hover:shadow-lg transition-all">
                  {/* Course Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full">
                          {course.subject_code}
                        </span>
                        <span className="text-sm text-gray-500">{course.credits} TC</span>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {course.subject_name}
                      </h3>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                  </div>

                  {/* Course Info */}
                  <div className="space-y-2 mb-4">
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Khoa:</span> {course.department}
                    </p>
                    {isTutor && course.student_count !== undefined && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Users className="h-4 w-4" />
                        <span>{course.student_count} sinh viên</span>
                      </div>
                    )}
                    {!isTutor && course.tutor_name && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <GraduationCap className="h-4 w-4" />
                        <span>Giảng viên: {course.tutor_name}</span>
                      </div>
                    )}
                  </div>

                  {/* Stats */}
                  <div className="pt-4 border-t border-gray-200">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Calendar className="h-4 w-4" />
                      <span>{course.session_count || 0} phiên học</span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyCourses;

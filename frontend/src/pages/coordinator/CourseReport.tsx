import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Star, Users, BookOpen, MessageSquare, CheckCircle } from 'lucide-react';
import { coordinatorApi } from '../../services/api';
import { toast } from 'react-toastify';

interface Student {
  user_id: number;
  full_name: string;
  email: string;
  total_sessions: number;
  attended_sessions: number;
  attendance_rate: number;
}

interface Feedback {
  session_id: number;
  session_title: string;
  session_date: string;
  student_name: string;
  student_email: string;
  rating: number;
  comment: string;
  created_at: string;
}

interface CourseDetails {
  tutor: {
    tutor_id: number;
    full_name: string;
    email: string;
    staff_code: string;
  };
  course: {
    subject_id: number;
    subject_code: string;
    subject_name: string;
    department: string;
  };
  statistics: {
    total_sessions: number;
    completed_sessions: number;
    total_students: number;
    average_rating: number;
    total_feedbacks: number;
  };
  students: Student[];
  feedbacks: Feedback[];
}

const CourseReport: React.FC = () => {
  const { tutorId, subjectId } = useParams<{ tutorId: string; subjectId: string }>();
  const navigate = useNavigate();
  const [details, setDetails] = useState<CourseDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (tutorId && subjectId) {
      fetchCourseDetails();
    }
  }, [tutorId, subjectId]);

  const fetchCourseDetails = async () => {
    try {
      const response = await coordinatorApi.getCourseDetails(
        parseInt(tutorId!),
        parseInt(subjectId!)
      ) as any;
      setDetails(response.data);
    } catch (error) {
      console.error('Failed to fetch course details:', error);
      toast.error('Không thể tải chi tiết môn học');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      setExporting(true);
      const response = await coordinatorApi.exportCourseReport(
        parseInt(tutorId!),
        parseInt(subjectId!),
        format
      );
      
      if (format === 'csv') {
        // Download CSV file
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${details?.tutor.staff_code}_${details?.course.subject_code}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        toast.success('Xuất báo cáo CSV thành công');
      } else {
        // Download JSON file
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${details?.tutor.staff_code}_${details?.course.subject_code}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
        toast.success('Xuất báo cáo JSON thành công');
      }
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Xuất báo cáo thất bại');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Đang tải...</p>
      </div>
    );
  }

  if (!details) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Không tìm thấy dữ liệu</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate(`/coordinator/tutors/${tutorId}/courses`)}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="h-5 w-5" />
        Quay lại
      </button>

      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">Báo Cáo Chi Tiết</h1>
            <div className="space-y-1 text-blue-100">
              <p className="text-lg font-semibold">{details.course.subject_name}</p>
              <p>{details.course.subject_code} • {details.course.department}</p>
              <p className="mt-2">Giảng viên: {details.tutor.full_name} ({details.tutor.staff_code})</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleExport('csv')}
              disabled={exporting}
              className="flex items-center gap-2 bg-white text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50"
            >
              <Download className="h-5 w-5" />
              {exporting ? 'Đang xuất...' : 'Xuất CSV'}
            </button>
            <button
              onClick={() => handleExport('json')}
              disabled={exporting}
              className="flex items-center gap-2 bg-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/30 transition-colors disabled:opacity-50"
            >
              <Download className="h-5 w-5" />
              JSON
            </button>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card bg-blue-50">
          <div className="flex items-center gap-3">
            <BookOpen className="h-8 w-8 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Tổng phiên học</p>
              <p className="text-2xl font-bold text-blue-600">
                {details.statistics.total_sessions}
              </p>
            </div>
          </div>
        </div>

        <div className="card bg-green-50">
          <div className="flex items-center gap-3">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div>
              <p className="text-sm text-gray-600">Đã hoàn thành</p>
              <p className="text-2xl font-bold text-green-600">
                {details.statistics.completed_sessions}
              </p>
            </div>
          </div>
        </div>

        <div className="card bg-purple-50">
          <div className="flex items-center gap-3">
            <Users className="h-8 w-8 text-purple-600" />
            <div>
              <p className="text-sm text-gray-600">Học viên</p>
              <p className="text-2xl font-bold text-purple-600">
                {details.statistics.total_students}
              </p>
            </div>
          </div>
        </div>

        <div className="card bg-yellow-50">
          <div className="flex items-center gap-3">
            <Star className="h-8 w-8 text-yellow-600" />
            <div>
              <p className="text-sm text-gray-600">Đánh giá TB</p>
              <p className="text-2xl font-bold text-yellow-600">
                {details.statistics.average_rating.toFixed(2)} / 5.0
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Students Table */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Users className="h-6 w-6 text-blue-600" />
          Danh Sách Học Viên & Điểm Danh
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Học viên
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tổng phiên
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Đã tham gia
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tỷ lệ điểm danh
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {details.students.map((student) => (
                <tr key={student.user_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{student.full_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {student.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-sm">
                    {student.total_sessions}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                    {student.attended_sessions}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      student.attendance_rate >= 80
                        ? 'bg-green-100 text-green-800'
                        : student.attendance_rate >= 50
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {student.attendance_rate.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Feedbacks */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <MessageSquare className="h-6 w-6 text-blue-600" />
          Đánh Giá Các Buổi Học ({details.feedbacks.length})
        </h2>
        
        {details.feedbacks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Chưa có đánh giá nào
          </div>
        ) : (
          <div className="space-y-4">
            {details.feedbacks.map((feedback, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-semibold text-gray-900">{feedback.session_title}</h3>
                    <p className="text-sm text-gray-500">
                      {new Date(feedback.session_date).toLocaleDateString('vi-VN')}
                    </p>
                  </div>
                  <div className="flex items-center gap-1 bg-yellow-50 px-3 py-1 rounded">
                    <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                    <span className="font-bold text-yellow-700">{feedback.rating}</span>
                  </div>
                </div>
                
                <div className="mb-2">
                  <p className="text-sm font-medium text-gray-700">{feedback.student_name}</p>
                  <p className="text-xs text-gray-500">{feedback.student_email}</p>
                </div>
                
                {feedback.comment && (
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-700 italic">"{feedback.comment}"</p>
                  </div>
                )}
                
                <p className="text-xs text-gray-400 mt-2">
                  {new Date(feedback.created_at).toLocaleString('vi-VN')}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CourseReport;

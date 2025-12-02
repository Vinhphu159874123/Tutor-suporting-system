import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { AxiosResponse } from "axios";
import { coursesApi } from "../../services/api";
import { 
  ArrowLeft, 
  BookOpen, 
  Calendar, 
  Users, 
  FileText,
  Clock,
  Video,
  Download,
  Link as LinkIcon
} from "lucide-react";

interface CourseInfo {
  code: string;
  name: string;
  credits?: number;
  instructor?: string;
  description?: string;
  semester?: string;
  schedule?: string;
  classroom?: string;
  enrolled?: number;
  maxStudents?: number;
}

const CourseDetailPage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<CourseInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'materials' | 'activities'>('overview');

  useEffect(() => {
    const fetchCourseDetail = async () => {
      try {
        setLoading(true);
        const response = await coursesApi.getCourseInfo(code!) as AxiosResponse<any>;
        const data = response.data;
        
        setCourse({
          code: data.code || code,
          name: data.name || "Course Name",
          credits: data.credits || 4,
          instructor: data.instructor || "Chưa có thông tin",
          description: data.description || "Thông tin chi tiết về môn học sẽ được cập nhật sớm.",
          semester: data.semester || "HK1 2024-2025",
          schedule: data.schedule || "Thứ 2, Thứ 4: 13:30 - 15:30",
          classroom: data.classroom || "H1-101",
          enrolled: data.enrolled || 45,
          maxStudents: data.maxStudents || 60
        });
      } catch (error: any) {
        console.error("Error fetching course detail:", error);
        toast.error("Không thể tải thông tin môn học");
        navigate("/courses");
      } finally {
        setLoading(false);
      }
    };
    
    if (code) {
      fetchCourseDetail();
    }
  }, [code, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Đang tải thông tin môn học...</p>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Không tìm thấy môn học</p>
          <button 
            onClick={() => navigate("/courses")}
            className="mt-4 text-blue-600 hover:underline"
          >
            Quay lại danh sách
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-6 py-4">
          <button
            onClick={() => navigate("/courses")}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Quay lại danh sách môn học
          </button>
          
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {course.name}
              </h1>
              <p className="text-gray-600 text-lg">
                {course.code} • {course.credits} tín chỉ
              </p>
            </div>
            
            <div className="text-right">
              <p className="text-sm text-gray-600">Học kỳ</p>
              <p className="font-semibold text-gray-900">{course.semester}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Course Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Tabs */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="border-b border-gray-200">
                <nav className="flex">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`px-6 py-3 font-medium transition-colors ${
                      activeTab === 'overview'
                        ? 'border-b-2 border-blue-600 text-blue-600'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Tổng quan
                  </button>
                  <button
                    onClick={() => setActiveTab('materials')}
                    className={`px-6 py-3 font-medium transition-colors ${
                      activeTab === 'materials'
                        ? 'border-b-2 border-blue-600 text-blue-600'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Tài liệu
                  </button>
                  <button
                    onClick={() => setActiveTab('activities')}
                    className={`px-6 py-3 font-medium transition-colors ${
                      activeTab === 'activities'
                        ? 'border-b-2 border-blue-600 text-blue-600'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Hoạt động
                  </button>
                </nav>
              </div>

              <div className="p-6">
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900 mb-3">
                        Mô tả môn học
                      </h2>
                      <p className="text-gray-700 leading-relaxed">
                        {course.description}
                      </p>
                    </div>

                    <div>
                      <h2 className="text-xl font-bold text-gray-900 mb-3">
                        Thông tin chung
                      </h2>
                      <div className="space-y-3">
                        <div className="flex items-start">
                          <Users className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                          <div>
                            <p className="text-sm text-gray-600">Giảng viên</p>
                            <p className="font-medium text-gray-900">{course.instructor}</p>
                          </div>
                        </div>
                        <div className="flex items-start">
                          <Calendar className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                          <div>
                            <p className="text-sm text-gray-600">Lịch học</p>
                            <p className="font-medium text-gray-900">{course.schedule}</p>
                          </div>
                        </div>
                        <div className="flex items-start">
                          <BookOpen className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                          <div>
                            <p className="text-sm text-gray-600">Phòng học</p>
                            <p className="font-medium text-gray-900">{course.classroom}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'materials' && (
                  <div className="space-y-4">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">
                      Tài liệu học tập
                    </h2>
                    
                    {/* Sample materials */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                        <div className="flex items-center">
                          <FileText className="w-5 h-5 text-blue-600 mr-3" />
                          <div>
                            <p className="font-medium text-gray-900">Slide bài giảng - Tuần 1</p>
                            <p className="text-sm text-gray-600">PDF • 2.5 MB</p>
                          </div>
                        </div>
                        <button className="text-blue-600 hover:text-blue-700">
                          <Download className="w-5 h-5" />
                        </button>
                      </div>

                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                        <div className="flex items-center">
                          <Video className="w-5 h-5 text-red-600 mr-3" />
                          <div>
                            <p className="font-medium text-gray-900">Video bài giảng - Chương 1</p>
                            <p className="text-sm text-gray-600">MP4 • 45 phút</p>
                          </div>
                        </div>
                        <button className="text-blue-600 hover:text-blue-700">
                          <LinkIcon className="w-5 h-5" />
                        </button>
                      </div>

                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                        <div className="flex items-center">
                          <FileText className="w-5 h-5 text-green-600 mr-3" />
                          <div>
                            <p className="font-medium text-gray-900">Bài tập thực hành</p>
                            <p className="text-sm text-gray-600">DOCX • 1.2 MB</p>
                          </div>
                        </div>
                        <button className="text-blue-600 hover:text-blue-700">
                          <Download className="w-5 h-5" />
                        </button>
                      </div>
                    </div>

                    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm text-blue-800">
                        <strong>Lưu ý:</strong> Tài liệu được cập nhật thường xuyên. 
                        Vui lòng kiểm tra định kỳ để nhận tài liệu mới nhất.
                      </p>
                    </div>
                  </div>
                )}

                {activeTab === 'activities' && (
                  <div className="space-y-4">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">
                      Hoạt động học tập
                    </h2>
                    
                    <div className="text-center py-12 text-gray-500">
                      <p>Chưa có hoạt động học tập nào</p>
                      <p className="text-sm mt-2">Thông tin hoạt động sẽ được cập nhật từ hệ thống</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Quick Info */}
          <div className="space-y-6">
            {/* Progress Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
              <h3 className="font-bold text-gray-900 mb-4">Tiến độ học tập</h3>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600">Hoàn thành</span>
                    <span className="text-sm font-medium text-gray-900">65%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: '65%' }}></div>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Bài giảng</span>
                    <span className="text-sm font-medium">8/12</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Bài tập</span>
                    <span className="text-sm font-medium">5/8</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Điểm trung bình</span>
                    <span className="text-sm font-medium text-green-600">8.5/10</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Enrollment Info */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
              <h3 className="font-bold text-gray-900 mb-4">Thông tin lớp</h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Sinh viên đăng ký</span>
                  <span className="text-sm font-medium">{course.enrolled}/{course.maxStudents}</span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${((course.enrolled || 0) / (course.maxStudents || 1)) * 100}%` }}
                  ></div>
                </div>

                <div className="pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    Lớp học đang trong trạng thái hoạt động
                  </p>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
              <h3 className="font-bold text-gray-900 mb-4">Hành động nhanh</h3>
              
              <div className="space-y-2">
                <button className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Tham gia lớp học
                </button>
                <button className="w-full py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                  Xem điểm danh
                </button>
                <button className="w-full py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                  Diễn đàn thảo luận
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetailPage;

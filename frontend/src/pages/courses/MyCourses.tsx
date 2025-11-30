import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { AxiosResponse } from "axios";
import { coursesApi } from "../../services/api";

interface Course {
  id: string;
  code: string;
  name: string;
  instructor: string;
  color: string;
}

const MyCourses: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("short_name");
  const [viewMode, setViewMode] = useState("card");
  const [filter, setFilter] = useState("all");
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch courses from API
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await coursesApi.getMyCourses() as AxiosResponse<any>;
        const apiCourses = response.data || [];
        
        // Transform API data to match Course interface
        const colors = ["bg-purple-400", "bg-blue-500", "bg-gray-400", "bg-blue-300", "bg-green-500", "bg-purple-600"];
        const transformedCourses = apiCourses.map((course: any, index: number) => ({
          id: course.code,
          code: course.code,
          name: `${course.name} (${course.code})`,
          instructor: "",
          color: colors[index % colors.length]
        }));
        
        setCourses(transformedCourses);
      } catch (error: any) {
        console.error("Error fetching courses:", error);
        toast.error("Không thể tải danh sách môn học");
      } finally {
        setLoading(false);
      }
    };
    
    fetchCourses();
  }, []);

  const filteredCourses = courses.filter((course) =>
    course.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Page Title */}
      <div className="bg-white border-b border-gray-200 mb-4">
        <div className="container mx-auto px-6 py-4"></div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-4">
        {/* Course Overview Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-4">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">
              Tổng quan về khoá học
            </h2>
          </div>

          <div className="p-4">
            <hr className="mb-4 border-gray-200" />

            {/* Filter Controls */}
            <div className="flex flex-wrap items-center gap-3 mb-4">
              {/* Status Filter */}
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-3 py-2 text-sm border border-gray-300 rounded bg-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="inprogress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="all">All</option>
              </select>

              {/* Search */}
              <input
                type="text"
                placeholder="Tìm kiếm khoá học"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="flex-1 min-w-[220px] max-w-md px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 text-sm border border-gray-300 rounded bg-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="short_name">Sort by short name</option>
                <option value="full_name">Sort by full name</option>
                <option value="last_accessed">Last accessed</option>
              </select>

              {/* View Mode */}
              <select
                value={viewMode}
                onChange={(e) => setViewMode(e.target.value)}
                className="px-3 py-2 text-sm border border-gray-300 rounded bg-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="card">Card</option>
                <option value="list">List</option>
                <option value="summary">Summary</option>
              </select>

            </div>

            {/* Semester Heading */}
            <div className="mb-4">
              <button className="flex items-center text-blue-600 font-medium hover:underline text-sm">
                <span className="mr-2">▶</span>
                Học kỳ (Semester) 1/2025-2026
              </button>
            </div>

            {/* Loading State */}
            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Đang tải môn học...</p>
              </div>
            ) : filteredCourses.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                Không tìm thấy môn học nào
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">{filteredCourses.map((course) => (
                <div
                  key={course.id}
                  onClick={() => window.location.href = `/courses/${course.code}`}
                  className="bg-white rounded border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer overflow-hidden"
                >
                  {/* Course Header with Pattern/Color */}
                  <div className={`${course.color} h-24 relative`}>
                    <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-black/10"></div>
                    {/* Pattern overlay similar to BK-LMS */}
                    <div className="absolute inset-0 opacity-20">
                      <svg className="w-full h-full">
                        <pattern
                          id={`pattern-${course.id}`}
                          x="0"
                          y="0"
                          width="40"
                          height="40"
                          patternUnits="userSpaceOnUse"
                        >
                          <circle
                            cx="20"
                            cy="20"
                            r="15"
                            fill="white"
                            opacity="0.3"
                          />
                        </pattern>
                        <rect
                          width="100%"
                          height="100%"
                          fill={`url(#pattern-${course.id})`}
                        />
                      </svg>
                    </div>
                  </div>

                  {/* Course Info */}
                  <div className="p-3">
                    <p className="text-xs text-gray-500 mb-1 leading-tight">
                      {course.code}
                    </p>
                    <h3 className="text-sm font-medium text-blue-600 hover:underline line-clamp-2 leading-snug">
                      {course.name}
                    </h3>
                  </div>
                </div>
              ))}
            </div>
            )}
          </div>
        </div>

        {/* Footer Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded p-4 text-sm text-gray-700">
          <p className="mb-2">
            <strong>Liên hệ hỗ trợ kỹ thuật:</strong>
          </p>
          <p>Email: ddthu@hcmut.edu.vn</p>
          <p className="mt-2 italic">
            Quý Thầy/Cô chưa có tài khoản (hoặc quên mật khẩu) nhà trường vui
            lòng liên hệ Trung tâm Dữ liệu & Công nghệ Thông tin, phòng 109 nhà
            A5 để được hỗ trợ.
          </p>
          <p className="mt-2 italic">
            (For HCMUT account, please contact to: Data and Information
            Technology Center)
          </p>
          <p>Email: nhan.nguyenpercy@hcmut.edu.vn</p>
          <p>ĐT (Tel.): 0834614120</p>
        </div>
      </div>
    </div>
  );
};

export default MyCourses;

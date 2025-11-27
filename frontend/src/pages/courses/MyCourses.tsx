import React, { useState } from "react";
import logoBK from "../../png/logobk.png";

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

  // Mock data - thay bằng dữ liệu thật từ API
  const courses: Course[] = [
    {
      id: "1",
      code: "79748_CO1007_003778_CLC",
      name: "Discrete Structures for Computing (CO1007)_Trần Tuấn Anh",
      instructor: "Trần Tuấn",
      color: "bg-purple-400",
    },
    {
      id: "2",
      code: "79748_CO1007_010190_CLC",
      name: "Discrete Structures for Computing (CO1007)_NGUYỄN Văn Minh Mẫn",
      instructor: "NGUYỄN",
      color: "bg-blue-500",
    },
    {
      id: "3",
      code: "79748_CO2013_003183_CLC",
      name: "Database Systems (CO2013)_NGUYỄN THỊ ÁI THẢO ...",
      instructor: "NGUYỄN THỊ AI THẢO",
      color: "bg-gray-400",
    },
    {
      id: "4",
      code: "79748_CO2014_010865_CLC",
      name: "Database Systems (Lab) (CO2014)_LÊ ĐỨC HOÀNG NAM ...",
      instructor: "LÊ ĐỨC HOÀNG NAM",
      color: "bg-blue-300",
    },
    {
      id: "5",
      code: "79748_CO3001_004282_CLC",
      name: "Software Engineering (CO3001)_Trần Trương Tuấn Phát ...",
      instructor: "Trần Trường Tuấn Phát",
      color: "bg-green-500",
    },
    {
      id: "6",
      code: "79748_CO3093_002921_CLC",
      name: "Computer Networks (CO3093)_NGUYỄN LÊ DUY LAI ...",
      instructor: "NGUYỄN LÊ DUY LAI",
      color: "bg-purple-600",
    },
    {
      id: "7",
      code: "79748_CO3094_010360_CLC",
      name: "Computer Networks (Lab) (CO3094)_NGUYỄN THÀNH NHÂN",
      instructor: "NGUYỄN THÀNH NHÂN",
      color: "bg-gray-300",
    },
    {
      id: "8",
      code: "79748_CO3103_004206_CLC",
      name: "Programming Integration Project (CO3103)_Phan Trung Hiếu.",
      instructor: "Phan Trung",
      color: "bg-gray-200",
    },
  ];

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

            {/* Course Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredCourses.map((course) => (
                <div
                  key={course.id}
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

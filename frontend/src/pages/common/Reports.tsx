import React, { useMemo, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { AxiosResponse } from "axios";
import apiClient from "../../services/api";
import { FileText } from "lucide-react";

interface CourseStat {
  id: string;
  course: string;
  faculty: string;
  completion: number;
  averageScore: number;
  tutorHours: number;
  activeStudents: number;
}

const kpiCards = [
  {
    label: "Phiên học hoàn thành",
    value: "128",
    trend: "+12% so với kỳ trước",
    trendColor: "text-green-600",
  },
  {
    label: "Sinh viên hoạt động",
    value: "432",
    trend: "+36 sinh viên mới",
    trendColor: "text-blue-600",
  },
  {
    label: "Điểm hài lòng trung bình",
    value: "4.7/5",
    trend: "↑ 0.2 điểm",
    trendColor: "text-purple-600",
  },
  {
    label: "Giờ tutor đóng góp",
    value: "312h",
    trend: "-18h so với mục tiêu",
    trendColor: "text-yellow-600",
  },
];

const facultyOptions = [
  { value: "all", label: "Tất cả khoa" },
  { value: "CS", label: "Khoa Khoa học & Kỹ thuật Máy tính" },
  { value: "EE", label: "Khoa Điện - Điện tử" },
  { value: "BS", label: "Khoa Cơ khí" },
];


const satisfactionByRole = [
  { role: "Student", score: 4.6 },
  { role: "Tutor", score: 4.8 },
  { role: "Coordinator", score: 4.4 },
];

const recentReports = [
  {
    name: "Tổng quan hoạt động tháng 11/2025",
    createdAt: "2025-11-15",
    author: "Nguyễn Thị Hằng",
    status: "Hoàn thành",
  },
  {
    name: "Tiến độ sinh viên khoa CSE",
    createdAt: "2025-11-10",
    author: "Phạm Quốc Bảo",
    status: "Đang soạn",
  },
  {
    name: "Đánh giá chất lượng tutor",
    createdAt: "2025-11-02",
    author: "Lê Mỹ Anh",
    status: "Hoàn thành",
  },
];

const Reports: React.FC = () => {
  const navigate = useNavigate();
  const [timeRange, setTimeRange] = useState("quarter");
  const [faculty, setFaculty] = useState("all");
  const [courseStats, setCourseStats] = useState<CourseStat[]>([]);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await apiClient.get("/api/v1/reports/courses") as AxiosResponse<any>;
        setCourseStats(response.data || []);
      } catch (error: any) {
        console.error("Error fetching reports:", error);
        toast.error("Không thể tải báo cáo");
      }
    };
    
    fetchReports();
  }, []);

  const filteredCourses = useMemo(() => {
    if (faculty === "all") return courseStats;
    return courseStats.filter((course) => course.faculty === faculty);
  }, [faculty, courseStats]);

  const formatDate = (value: string) =>
    new Date(value).toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-wide text-blue-600 font-semibold">
            Báo cáo & Phân tích
          </p>
          <h1 className="text-3xl font-bold text-gray-900">Bảng điều khiển báo cáo</h1>
          <p className="text-gray-500">
            Theo dõi hiệu suất học tập, hoạt động tutor và mức độ tham gia của sinh viên
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="month">Tháng này</option>
            <option value="quarter">Quý hiện tại</option>
            <option value="year">Năm học</option>
          </select>
          <button
            onClick={() => navigate("/export-report")}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-semibold inline-flex items-center gap-2"
          >
            <FileText className="w-5 h-5" />
            Xuất báo cáo
          </button>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((card) => (
          <div key={card.label} className="bg-white rounded-lg shadow-md p-5">
            <p className="text-sm text-gray-500">{card.label}</p>
            <p className="text-3xl font-bold text-gray-900 my-2">{card.value}</p>
            <p className={`text-sm font-semibold ${card.trendColor}`}>{card.trend}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Tổng quan khoá học</h2>
            <p className="text-gray-500 text-sm">
              Dữ liệu đã chuẩn hóa theo mốc thời gian: {timeRange === "month" ? "Tháng hiện tại" : timeRange === "quarter" ? "Quý hiện tại" : "Năm học"}
            </p>
          </div>
          <select
            value={faculty}
            onChange={(e) => setFaculty(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {facultyOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="text-gray-500 border-b">
                <th className="py-3 pr-4">Môn học</th>
                <th className="py-3 pr-4">Hoàn thành</th>
                <th className="py-3 pr-4">Điểm TB</th>
                <th className="py-3 pr-4">Giờ tutor</th>
                <th className="py-3">SV hoạt động</th>
              </tr>
            </thead>
            <tbody>
              {filteredCourses.map((course) => (
                <tr key={course.id} className="border-b last:border-0">
                  <td className="py-4 pr-4">
                    <p className="font-semibold text-gray-900">{course.course}</p>
                    <p className="text-xs text-gray-500">
                      {facultyOptions.find((opt) => opt.value === course.faculty)?.label}
                    </p>
                  </td>
                  <td className="py-4 pr-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-gray-100 rounded-full">
                        <div
                          className="h-full rounded-full bg-blue-500"
                          style={{ width: `${course.completion}%` }}
                        />
                      </div>
                      <span className="font-semibold text-gray-900">
                        {course.completion}%
                      </span>
                    </div>
                  </td>
                  <td className="py-4 pr-4 font-semibold text-gray-900">
                    {course.averageScore.toFixed(1)} / 10
                  </td>
                  <td className="py-4 pr-4 text-gray-700">{course.tutorHours}h</td>
                  <td className="py-4 text-gray-700">{course.activeStudents} SV</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Satisfaction & recent reports */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Mức độ hài lòng</h3>
          <div className="space-y-4">
            {satisfactionByRole.map((item) => (
              <div key={item.role}>
                <div className="flex items-center justify-between mb-1">
                  <p className="font-semibold text-gray-800">{item.role}</p>
                  <p className="text-sm text-gray-600">{item.score}/5</p>
                </div>
                <div className="h-2 bg-gray-100 rounded-full">
                  <div
                    className="h-full bg-green-500 rounded-full"
                    style={{ width: `${(item.score / 5) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-900">Báo cáo gần đây</h3>
            <button className="text-blue-600 text-sm font-semibold hover:text-blue-700" onClick={() => navigate("/export-report")}>Xem tất cả</button>
          </div>
          <div className="space-y-3">
            {recentReports.map((report) => (
              <div
                key={report.name}
                className="p-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition"
              >
                <div className="flex items-center justify-between mb-1">
                  <p className="font-semibold text-gray-900">{report.name}</p>
                  <span
                    className={`text-xs font-semibold px-2 py-1 rounded-full ${
                      report.status === "Hoàn thành"
                        ? "bg-green-100 text-green-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {report.status}
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Người lập: {report.author} • {formatDate(report.createdAt)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;
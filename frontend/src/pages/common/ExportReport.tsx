import React, { useState } from "react";
import { toast } from "react-toastify";

interface ExportOptions {
  reportType: string;
  dateFrom: string;
  dateTo: string;
  format: string;
  includeCharts: boolean;
  includeDetails: boolean;
}

const ExportReport: React.FC = () => {
  const [options, setOptions] = useState<ExportOptions>({
    reportType: "tutor-activity",
    dateFrom: "",
    dateTo: "",
    format: "pdf",
    includeCharts: true,
    includeDetails: true,
  });

  const [isGenerating, setIsGenerating] = useState(false);

  const handleExport = async () => {
    if (!options.dateFrom || !options.dateTo) {
      toast.error("Vui lòng chọn khoảng thời gian");
      return;
    }

    setIsGenerating(true);
    // Simulate export process
    setTimeout(() => {
      toast.success("Báo cáo đã được tạo và tải xuống thành công!");
      setIsGenerating(false);
    }, 2000);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Xuất báo cáo</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        {/* Report Type */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Loại báo cáo
          </label>
          <select
            value={options.reportType}
            onChange={(e) =>
              setOptions({ ...options, reportType: e.target.value })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="tutor-activity">Hoạt động Tutor</option>
            <option value="student-progress">Tiến độ học tập sinh viên</option>
            <option value="course-statistics">Thống kê môn học</option>
            <option value="session-summary">Tổng hợp buổi học</option>
            <option value="overall-academic">Tổng quan học thuật</option>
          </select>
        </div>

        {/* Date Range */}
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Từ ngày
            </label>
            <input
              type="date"
              value={options.dateFrom}
              onChange={(e) =>
                setOptions({ ...options, dateFrom: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Đến ngày
            </label>
            <input
              type="date"
              value={options.dateTo}
              onChange={(e) =>
                setOptions({ ...options, dateTo: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Format */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Định dạng file
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="pdf"
                checked={options.format === "pdf"}
                onChange={(e) =>
                  setOptions({ ...options, format: e.target.value })
                }
                className="mr-2"
              />
              PDF
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="excel"
                checked={options.format === "excel"}
                onChange={(e) =>
                  setOptions({ ...options, format: e.target.value })
                }
                className="mr-2"
              />
              Excel
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="csv"
                checked={options.format === "csv"}
                onChange={(e) =>
                  setOptions({ ...options, format: e.target.value })
                }
                className="mr-2"
              />
              CSV
            </label>
          </div>
        </div>

        {/* Options */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tùy chọn
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={options.includeCharts}
                onChange={(e) =>
                  setOptions({ ...options, includeCharts: e.target.checked })
                }
                className="mr-2"
              />
              Bao gồm biểu đồ thống kê
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={options.includeDetails}
                onChange={(e) =>
                  setOptions({ ...options, includeDetails: e.target.checked })
                }
                className="mr-2"
              />
              Bao gồm chi tiết từng mục
            </label>
          </div>
        </div>

        {/* Export Button */}
        <button
          onClick={handleExport}
          disabled={isGenerating}
          className={`w-full py-3 rounded-lg font-semibold text-white transition ${
            isGenerating
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {isGenerating ? "Đang tạo báo cáo..." : "📄 Xuất báo cáo"}
        </button>
      </div>

      {/* Recent Reports */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Báo cáo gần đây
        </h2>
        <div className="space-y-3">
          {[
            {
              name: "Hoạt động Tutor - Tháng 11/2025",
              date: "2025-11-15",
              format: "PDF",
            },
            {
              name: "Tiến độ sinh viên - Q3/2025",
              date: "2025-10-30",
              format: "Excel",
            },
            {
              name: "Thống kê môn học - Học kỳ 1",
              date: "2025-10-15",
              format: "PDF",
            },
          ].map((report, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
            >
              <div className="flex items-center gap-3">
                <div className="text-2xl">
                  {report.format === "PDF" ? "📄" : "📊"}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{report.name}</p>
                  <p className="text-sm text-gray-500">
                    Ngày tạo: {report.date}
                  </p>
                </div>
              </div>
              <button className="text-blue-600 hover:text-blue-700 px-4 py-2 rounded-lg hover:bg-blue-50 transition">
                Tải lại
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ExportReport;

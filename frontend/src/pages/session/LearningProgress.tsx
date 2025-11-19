import React from "react";

interface CourseProgress {
  courseId: string;
  courseName: string;
  totalSessions: number;
  completedSessions: number;
  averageScore: number;
  attendance: number;
}

const LearningProgress: React.FC = () => {
  const courses: CourseProgress[] = [
    {
      courseId: "CO3005",
      courseName: "Công nghệ phần mềm",
      totalSessions: 10,
      completedSessions: 7,
      averageScore: 8.5,
      attendance: 85,
    },
    {
      courseId: "CO3001",
      courseName: "Cấu trúc dữ liệu và giải thuật",
      totalSessions: 12,
      completedSessions: 9,
      averageScore: 9.0,
      attendance: 92,
    },
    {
      courseId: "CO2003",
      courseName: "Lập trình hướng đối tượng",
      totalSessions: 8,
      completedSessions: 8,
      averageScore: 8.8,
      attendance: 100,
    },
  ];

  const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return "bg-green-500";
    if (percentage >= 60) return "bg-yellow-500";
    return "bg-red-500";
  };

  const getScoreColor = (score: number) => {
    if (score >= 8.5) return "text-green-600";
    if (score >= 7.0) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Theo dõi tiến độ học tập
      </h1>

      {/* Overall Statistics */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-3xl mb-2">📚</div>
          <p className="text-sm text-gray-600 mb-1">Tổng môn học</p>
          <p className="text-3xl font-bold text-gray-900">{courses.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-3xl mb-2">✅</div>
          <p className="text-sm text-gray-600 mb-1">Sessions hoàn thành</p>
          <p className="text-3xl font-bold text-gray-900">
            {courses.reduce((sum, c) => sum + c.completedSessions, 0)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-3xl mb-2">⭐</div>
          <p className="text-sm text-gray-600 mb-1">Điểm trung bình</p>
          <p className="text-3xl font-bold text-green-600">
            {(
              courses.reduce((sum, c) => sum + c.averageScore, 0) /
              courses.length
            ).toFixed(1)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-3xl mb-2">📊</div>
          <p className="text-sm text-gray-600 mb-1">Tỷ lệ tham gia</p>
          <p className="text-3xl font-bold text-blue-600">
            {(
              courses.reduce((sum, c) => sum + c.attendance, 0) / courses.length
            ).toFixed(0)}
            %
          </p>
        </div>
      </div>

      {/* Course Progress List */}
      <div className="space-y-6">
        {courses.map((course) => {
          const progressPercentage =
            (course.completedSessions / course.totalSessions) * 100;

          return (
            <div key={course.courseId} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    {course.courseName}
                  </h3>
                  <p className="text-gray-600">Mã môn: {course.courseId}</p>
                </div>
                <span
                  className={`text-2xl font-bold ${getScoreColor(
                    course.averageScore
                  )}`}
                >
                  {course.averageScore.toFixed(1)}/10
                </span>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <p className="text-sm font-medium text-gray-700">
                    Tiến độ sessions
                  </p>
                  <p className="text-sm text-gray-600">
                    {course.completedSessions}/{course.totalSessions} sessions
                  </p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${getProgressColor(
                      progressPercentage
                    )}`}
                    style={{ width: `${progressPercentage}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {progressPercentage.toFixed(0)}% hoàn thành
                </p>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Tham gia</p>
                  <p className="text-lg font-bold text-gray-900">
                    {course.attendance}%
                  </p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Hoàn thành</p>
                  <p className="text-lg font-bold text-gray-900">
                    {course.completedSessions}
                  </p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Còn lại</p>
                  <p className="text-lg font-bold text-gray-900">
                    {course.totalSessions - course.completedSessions}
                  </p>
                </div>
              </div>

              <button className="w-full mt-4 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition">
                Xem chi tiết
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LearningProgress;

import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { AxiosResponse } from "axios";
import SessionBackButton from "./SessionBackButton";
import { BookOpen, CheckCircle2, Star, BarChart3 } from "lucide-react";
import apiClient from "../../services/api";

interface CourseProgress {
  courseId: string;
  courseName: string;
  totalSessions: number;
  completedSessions: number;
  averageScore: number;
  attendance: number;
}

const LearningProgress: React.FC = () => {
  const [courses, setCourses] = useState<CourseProgress[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        // TODO: Get actual student_id from auth context
        const studentId = 94; // Placeholder
        const response = await apiClient.get(
          `/progress/students/${studentId}/progress`
        ) as AxiosResponse<any>;
        
        // Transform API data
        const progressData = response.data || [];
        
        // Aggregate by course
        const courseMap = new Map<string, CourseProgress>();
        progressData.forEach((item: any) => {
          const key = item.courseId;
          if (!courseMap.has(key)) {
            courseMap.set(key, {
              courseId: item.courseId,
              courseName: item.courseName,
              totalSessions: 0,
              completedSessions: 0,
              averageScore: 0,
              attendance: 0
            });
          }
          const course = courseMap.get(key)!;
          course.totalSessions += 1;
          course.completedSessions += item.completedSessions || 0;
          course.averageScore = (course.averageScore + (item.averageScore || 0)) / 2;
          course.attendance = (course.attendance + (item.attendance || 0)) / 2;
        });
        
        setCourses(Array.from(courseMap.values()));
      } catch (error: any) {
        console.error("Error fetching progress:", error);
        toast.error("Không thể tải tiến độ học tập");
      } finally {
        setLoading(false);
      }
    };
    
    fetchProgress();
  }, []);

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

  const progressWidthClassMap: Record<number, string> = {
    0: "w-[0%]",
    10: "w-[10%]",
    20: "w-[20%]",
    30: "w-[30%]",
    40: "w-[40%]",
    50: "w-[50%]",
    60: "w-[60%]",
    70: "w-[70%]",
    80: "w-[80%]",
    90: "w-[90%]",
    100: "w-[100%]",
  };

  const getProgressWidthClass = (percentage: number) => {
    const steps = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0];
    for (const step of steps) {
      if (percentage >= step) {
        return progressWidthClassMap[step];
      }
    }
    return progressWidthClassMap[0];
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <SessionBackButton className="mb-6" />
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Theo dõi tiến độ học tập
      </h1>

      {/* Overall Statistics */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Đang tải tiến độ...</p>
        </div>
      ) : courses.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <p className="text-gray-500">Chưa có dữ liệu tiến độ học tập</p>
        </div>
      ) : (
        <>
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
            <BookOpen className="h-6 w-6" />
          </div>
          <p className="text-sm text-gray-600 mb-1">Tổng môn học</p>
          <p className="text-3xl font-bold text-gray-900">{courses.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-green-50 text-green-600">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <p className="text-sm text-gray-600 mb-1">Sessions hoàn thành</p>
          <p className="text-3xl font-bold text-gray-900">
            {courses.reduce((sum, c) => sum + c.completedSessions, 0)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-yellow-50 text-yellow-600">
            <Star className="h-6 w-6 fill-yellow-400 text-yellow-500" />
          </div>
          <p className="text-sm text-gray-600 mb-1">Điểm trung bình</p>
          <p className="text-3xl font-bold text-green-600">
            {(
              courses.reduce((sum, c) => sum + c.averageScore, 0) /
              courses.length
            ).toFixed(1)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
            <BarChart3 className="h-6 w-6" />
          </div>
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
                    )} ${getProgressWidthClass(progressPercentage)}`}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {progressPercentage.toFixed(0)}% hoàn thành
                </p>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
        </>
      )}
    </div>
  );
};

export default LearningProgress;

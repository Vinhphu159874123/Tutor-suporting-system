import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { Calendar, Clock, User, CheckCircle, XCircle } from "lucide-react";
import apiClient from "../../services/api";

interface Session {
  session_id: number;
  title: string;
  description: string;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  status: string;
  students: Array<{
    full_name: string;
    email: string;
  }>;
  subject_id: number;
}

const SessionRequests: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      // Get sessions with status 'published' (pending tutor confirmation)
      const response = await apiClient.get("/sessions/", {
        params: { status: "published" },
      });
      setSessions(response.data);
    } catch (error) {
      console.error("Error fetching sessions:", error);
      toast.error("Không thể tải danh sách lịch học");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleConfirm = async (sessionId: number) => {
    try {
      await apiClient.put(`/sessions/${sessionId}`, {
        status: "confirmed",
      });
      toast.success("Đã xác nhận lịch học!");
      
      // Optionally send notification to student
      // TODO: Implement notification API
      
      fetchSessions();
    } catch (error: any) {
      console.error("Error confirming session:", error);
      toast.error(error.response?.data?.detail || "Không thể xác nhận lịch học");
    }
  };

  const handleReject = async (sessionId: number) => {
    try {
      await apiClient.put(`/sessions/${sessionId}`, {
        status: "cancelled",
      });
      toast.success("Đã từ chối lịch học");
      
      // Optionally send notification to student
      // TODO: Implement notification API
      
      fetchSessions();
    } catch (error: any) {
      console.error("Error rejecting session:", error);
      toast.error(error.response?.data?.detail || "Không thể từ chối lịch học");
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Yêu Cầu Đặt Lịch
      </h1>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Đang tải...</p>
        </div>
      ) : sessions.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <p className="text-gray-500">Chưa có yêu cầu đặt lịch nào</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((session) => (
            <div
              key={session.session_id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    {session.title}
                  </h3>
                  {session.description && (
                    <p className="text-gray-600 mt-1">{session.description}</p>
                  )}
                </div>
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                  Chờ xác nhận
                </span>
              </div>

              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div className="flex items-center text-gray-700">
                  <Calendar className="w-5 h-5 mr-2 text-blue-600" />
                  <span>
                    {new Date(session.scheduled_date).toLocaleDateString(
                      "vi-VN"
                    )}
                  </span>
                </div>
                <div className="flex items-center text-gray-700">
                  <Clock className="w-5 h-5 mr-2 text-blue-600" />
                  <span>
                    {session.start_time.substring(0, 5)} -{" "}
                    {session.end_time.substring(0, 5)}
                  </span>
                </div>
              </div>

              {session.students && session.students.length > 0 && (
                <div className="mb-4">
                  <div className="flex items-center text-gray-700 mb-2">
                    <User className="w-5 h-5 mr-2 text-blue-600" />
                    <span className="font-medium">Học viên:</span>
                  </div>
                  <div className="ml-7">
                    {session.students.map((student, idx) => (
                      <div key={idx} className="text-gray-600">
                        {student.full_name} ({student.email})
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => handleConfirm(session.session_id)}
                  className="flex-1 flex items-center justify-center gap-2 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors"
                >
                  <CheckCircle className="w-5 h-5" />
                  Xác nhận
                </button>
                <button
                  onClick={() => handleReject(session.session_id)}
                  className="flex-1 flex items-center justify-center gap-2 bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 transition-colors"
                >
                  <XCircle className="w-5 h-5" />
                  Từ chối
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SessionRequests;

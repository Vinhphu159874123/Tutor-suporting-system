import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Calendar, Clock } from 'lucide-react';
import { sessionsApi } from '../services/api';
import { toast } from 'react-toastify';
import { AxiosResponse } from 'axios';

interface Session {
  session_id: number;
  subject_id: number;
  subject_name: string;
  subject_code: string;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  status: string;
}

interface TimetableProps {
  mode: string;
}

// Color palette for different courses (Google Calendar style)
const courseColors = [
  { bg: 'bg-blue-500', text: 'text-white', hover: 'hover:bg-blue-600', border: 'border-blue-600' },
  { bg: 'bg-green-500', text: 'text-white', hover: 'hover:bg-green-600', border: 'border-green-600' },
  { bg: 'bg-purple-500', text: 'text-white', hover: 'hover:bg-purple-600', border: 'border-purple-600' },
  { bg: 'bg-orange-500', text: 'text-white', hover: 'hover:bg-orange-600', border: 'border-orange-600' },
  { bg: 'bg-pink-500', text: 'text-white', hover: 'hover:bg-pink-600', border: 'border-pink-600' },
  { bg: 'bg-indigo-500', text: 'text-white', hover: 'hover:bg-indigo-600', border: 'border-indigo-600' },
  { bg: 'bg-teal-500', text: 'text-white', hover: 'hover:bg-teal-600', border: 'border-teal-600' },
  { bg: 'bg-red-500', text: 'text-white', hover: 'hover:bg-red-600', border: 'border-red-600' },
];

const getColorForCourse = (subjectId: number) => {
  return courseColors[subjectId % courseColors.length];
};

const Timetable: React.FC<TimetableProps> = ({ mode }) => {
  const navigate = useNavigate();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  useEffect(() => {
    fetchSessions();
  }, [currentDate, mode]);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth() + 1;
      
      // Fetch sessions for current month
      const response = await sessionsApi.getMySessions({ mode }) as AxiosResponse<any>;
      const allSessions = response.data || [];
      
      // Filter sessions for current month
      const filteredSessions = allSessions.filter((session: Session) => {
        const sessionDate = new Date(session.scheduled_date);
        return sessionDate.getFullYear() === year && sessionDate.getMonth() === month - 1;
      });
      
      setSessions(filteredSessions);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
      toast.error('Không thể tải lịch học');
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const day = new Date(year, month, 1).getDay();
    // Convert Sunday (0) to 7 to match our weekDays array [CN=0, T2=1, T3=2, ..., T7=6]
    // But weekDays is [CN, T2, T3, T4, T5, T6, T7]
    // JS: Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6
    // We want: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    return day === 0 ? 6 : day - 1;
  };

  const getSessionsForDate = (date: Date) => {
    // Format date for comparison (YYYY-MM-DD)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    
    return sessions.filter(session => {
      // Convert UTC to Vietnam timezone (UTC+7)
      const sessionDateUTC = new Date(session.scheduled_date);
      const vietnamOffset = 7 * 60; // 7 hours in minutes
      const vietnamDate = new Date(sessionDateUTC.getTime() + vietnamOffset * 60 * 1000);
      
      const sessionYear = vietnamDate.getUTCFullYear();
      const sessionMonth = String(vietnamDate.getUTCMonth() + 1).padStart(2, '0');
      const sessionDay = String(vietnamDate.getUTCDate()).padStart(2, '0');
      const sessionDateStr = `${sessionYear}-${sessionMonth}-${sessionDay}`;
      
      return sessionDateStr === dateStr;
    });
  };

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const daysInMonth = getDaysInMonth(currentDate);
  const firstDayOfMonth = getFirstDayOfMonth(currentDate);
  const monthName = currentDate.toLocaleDateString('vi-VN', { month: 'long', year: 'numeric' });

  const weekDays = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];
  const calendarDays = [];

  // Add empty cells for days before month starts
  for (let i = 0; i < firstDayOfMonth; i++) {
    calendarDays.push(null);
  }

  // Add days of month
  for (let day = 1; day <= daysInMonth; day++) {
    calendarDays.push(day);
  }

  return (
    <div className="card bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center mr-3">
            <Calendar className="w-6 h-6 text-white" />
          </div>
          Thời khóa biểu
        </h2>
        <div className="flex items-center space-x-3">
          <button
            onClick={previousMonth}
            className="p-2 hover:bg-gray-100 rounded-full transition-all hover:shadow-md"
            title="Tháng trước"
          >
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>
          <span className="font-bold text-gray-800 min-w-[180px] text-center capitalize text-lg">
            {monthName}
          </span>
          <button
            onClick={nextMonth}
            className="p-2 hover:bg-gray-100 rounded-full transition-all hover:shadow-md"
            title="Tháng sau"
          >
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="h-96 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Đang tải lịch học...</p>
          </div>
        </div>
      ) : (
        <div className="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          {/* Week day headers - Google Calendar style */}
          <div className="grid grid-cols-7 bg-gradient-to-r from-gray-50 to-gray-100 border-b-2 border-gray-300">
            {weekDays.map((day, idx) => (
              <div 
                key={day} 
                className={`text-center py-3 text-sm font-bold ${
                  idx === 0 ? 'text-red-600' : 'text-gray-700'
                }`}
              >
                {day}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7">
            {calendarDays.map((day, index) => {
              if (day === null) {
                return (
                  <div 
                    key={`empty-${index}`} 
                    className="border-b border-r border-gray-100 p-2 min-h-[120px] bg-gray-50/50"
                  ></div>
                );
              }

              const cellDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
              cellDate.setHours(0, 0, 0, 0);
              const isToday = cellDate.getTime() === today.getTime();
              const daySessions = getSessionsForDate(cellDate);
              const isSunday = cellDate.getDay() === 0;

              return (
                <div
                  key={day}
                  className={`border-b border-r border-gray-100 p-2 min-h-[120px] transition-all ${
                    isToday 
                      ? 'bg-blue-50/70' 
                      : 'bg-white hover:bg-gray-50'
                  }`}
                >
                  {/* Day number */}
                  <div className="flex items-center justify-between mb-2">
                    <span 
                      className={`text-sm font-semibold ${
                        isToday 
                          ? 'bg-blue-600 text-white w-7 h-7 rounded-full flex items-center justify-center text-xs' 
                          : isSunday
                          ? 'text-red-500'
                          : 'text-gray-700'
                      }`}
                    >
                      {day}
                    </span>
                    {daySessions.length > 2 && (
                      <span className="text-[10px] text-gray-500 font-medium">
                        +{daySessions.length - 2}
                      </span>
                    )}
                  </div>

                  {/* Sessions - Google Calendar style */}
                  <div className="space-y-1">
                    {daySessions.slice(0, 3).map(session => {
                      const colors = getColorForCourse(session.subject_id);
                      return (
                        <div
                          key={session.session_id}
                          onClick={() => navigate(`/my-courses/${session.subject_id}`)}
                          className={`${colors.bg} ${colors.text} ${colors.hover} rounded-md p-1.5 cursor-pointer transition-all shadow-sm hover:shadow-md transform hover:scale-[1.02] border-l-4 ${colors.border}`}
                          title={`${session.subject_name}\n${session.start_time} - ${session.end_time}`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                              <div className="font-bold text-xs truncate">
                                {session.subject_code}
                              </div>
                              <div className="flex items-center text-[10px] opacity-90 mt-0.5">
                                <Clock className="w-2.5 h-2.5 mr-1" />
                                {session.start_time.substring(0, 5)}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-600">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-blue-600 mr-2"></div>
              <span>Hôm nay</span>
            </div>
            <div className="flex items-center">
              <Clock className="w-3 h-3 mr-1 text-gray-500" />
              <span>Click vào buổi học để xem chi tiết</span>
            </div>
          </div>
          <div className="text-gray-500">
            Tổng: <span className="font-semibold text-gray-700">{sessions.length}</span> buổi học
          </div>
        </div>
      </div>
    </div>
  );
};

export default Timetable;

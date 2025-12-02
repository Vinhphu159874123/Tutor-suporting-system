import React, { useState, useEffect } from 'react';
import { Calendar, Clock, BookOpen, Plus, X, MapPin, FileText, Trash2, Edit2, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../../services/api';
import { toast } from 'react-toastify';

interface TimeSlot {
  day: string;
  start_time: string;
  end_time: string;
}

interface Subject {
  subject_id: number;
  subject_code: string;
  subject_name: string;
  department: string;
  credits: number;
}

interface SchedulePreference {
  preference_id: number;
  student_id: number;
  student_name: string;
  subject_id: number;
  subject_code: string;
  subject_name: string;
  preferred_start_date: string;
  total_sessions: number;
  session_duration: number;
  session_format: string;
  available_time_slots: TimeSlot[];
  notes?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

const DAYS_OF_WEEK = [
  { value: 'monday', label: 'Thứ 2' },
  { value: 'tuesday', label: 'Thứ 3' },
  { value: 'wednesday', label: 'Thứ 4' },
  { value: 'thursday', label: 'Thứ 5' },
  { value: 'friday', label: 'Thứ 6' },
  { value: 'saturday', label: 'Thứ 7' },
  { value: 'sunday', label: 'Chủ nhật' }
];

const SESSION_FORMATS = [
  { value: 'online', label: 'Online', icon: '💻' },
  { value: 'offline', label: 'Offline', icon: '🏫' },
  { value: 'both', label: 'Cả hai', icon: '🔄' }
];

const StudentScheduling: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [preferences, setPreferences] = useState<SchedulePreference[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Form state
  const [selectedSubject, setSelectedSubject] = useState<number | null>(null);
  const [startDate, setStartDate] = useState('');
  const [totalSessions, setTotalSessions] = useState(10);
  const [sessionDuration, setSessionDuration] = useState(90);
  const [sessionFormat, setSessionFormat] = useState('both');
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [notes, setNotes] = useState('');
  
  // Current time slot being added
  const [currentDay, setCurrentDay] = useState('monday');
  const [currentStartTime, setCurrentStartTime] = useState('08:00');
  const [currentEndTime, setCurrentEndTime] = useState('10:00');

  useEffect(() => {
    loadSubjects();
    loadPreferences();
  }, []);

  const loadSubjects = async () => {
    try {
      const response = await api.get('/courses/subjects');
      setSubjects(response.data);
    } catch (error: any) {
      console.error('Error loading subjects:', error);
      toast.error('Không thể tải danh sách môn học');
    }
  };

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const response = await api.get('/schedule-preferences/my-preferences');
      setPreferences(response.data);
    } catch (error: any) {
      console.error('Error loading preferences:', error);
      toast.error('Không thể tải danh sách nguyện vọng');
    } finally {
      setLoading(false);
    }
  };

  const addTimeSlot = () => {
    if (!currentDay || !currentStartTime || !currentEndTime) {
      toast.error('Vui lòng chọn đầy đủ thông tin khung giờ');
      return;
    }

    if (currentStartTime >= currentEndTime) {
      toast.error('Giờ bắt đầu phải nhỏ hơn giờ kết thúc');
      return;
    }

    const newSlot: TimeSlot = {
      day: currentDay,
      start_time: currentStartTime,
      end_time: currentEndTime
    };

    setTimeSlots([...timeSlots, newSlot]);
    toast.success('Đã thêm khung giờ');
  };

  const removeTimeSlot = (index: number) => {
    setTimeSlots(timeSlots.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedSubject) {
      toast.error('Vui lòng chọn môn học');
      return;
    }

    if (timeSlots.length === 0) {
      toast.error('Vui lòng thêm ít nhất một khung giờ rảnh');
      return;
    }

    try {
      setLoading(true);
      await api.post('/schedule-preferences/', {
        subject_id: selectedSubject,
        preferred_start_date: startDate,
        total_sessions: totalSessions,
        session_duration: sessionDuration,
        session_format: sessionFormat,
        available_time_slots: timeSlots,
        notes: notes || null
      });

      toast.success('Đã đăng ký nguyện vọng thành công!');
      resetForm();
      setShowForm(false);
      loadPreferences();
    } catch (error: any) {
      console.error('Error creating preference:', error);
      toast.error(error.response?.data?.detail || 'Không thể đăng ký nguyện vọng');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setSelectedSubject(null);
    setStartDate('');
    setTotalSessions(10);
    setSessionDuration(90);
    setSessionFormat('both');
    setTimeSlots([]);
    setNotes('');
  };

  const deletePreference = async (preferenceId: number) => {
    if (!window.confirm('Bạn có chắc muốn xóa nguyện vọng này?')) {
      return;
    }

    try {
      await api.delete(`/schedule-preferences/${preferenceId}`);
      toast.success('Đã xóa nguyện vọng');
      loadPreferences();
    } catch (error: any) {
      console.error('Error deleting preference:', error);
      toast.error('Không thể xóa nguyện vọng');
    }
  };

  const getDayLabel = (day: string) => {
    return DAYS_OF_WEEK.find(d => d.value === day)?.label || day;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'fulfilled': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'expired': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending': return 'Đang chờ';
      case 'fulfilled': return 'Đã mở lớp';
      case 'cancelled': return 'Đã hủy';
      case 'expired': return 'Hết hạn';
      default: return status;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Đăng ký lịch học</h1>
          <p className="text-gray-600 mt-2">Đăng ký nguyện vọng môn học và khung giờ bạn mong muốn</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center gap-2 transition-colors"
        >
          {showForm ? <X size={20} /> : <Plus size={20} />}
          {showForm ? 'Đóng' : 'Đăng ký nguyện vọng'}
        </button>
      </div>

      {/* Registration Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Thông tin nguyện vọng</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Subject Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <BookOpen className="inline mr-2" size={18} />
                Môn học
              </label>
              <select
                value={selectedSubject || ''}
                onChange={(e) => setSelectedSubject(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">-- Chọn môn học --</option>
                {subjects.map(subject => (
                  <option key={subject.subject_id} value={subject.subject_id}>
                    {subject.subject_code} - {subject.subject_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Start Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Calendar className="inline mr-2" size={18} />
                  Ngày bắt đầu mong muốn
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              {/* Total Sessions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Số buổi học: {totalSessions}
                </label>
                <input
                  type="range"
                  min="1"
                  max="30"
                  value={totalSessions}
                  onChange={(e) => setTotalSessions(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Session Duration */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Clock className="inline mr-2" size={18} />
                  Thời lượng mỗi buổi (phút): {sessionDuration}
                </label>
                <input
                  type="range"
                  min="30"
                  max="180"
                  step="15"
                  value={sessionDuration}
                  onChange={(e) => setSessionDuration(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Session Format */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPin className="inline mr-2" size={18} />
                  Hình thức học
                </label>
                <div className="flex gap-2">
                  {SESSION_FORMATS.map(format => (
                    <button
                      key={format.value}
                      type="button"
                      onClick={() => setSessionFormat(format.value)}
                      className={`flex-1 px-4 py-2 rounded-lg border-2 transition-all ${
                        sessionFormat === format.value
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                    >
                      <span className="text-2xl">{format.icon}</span>
                      <div className="text-sm mt-1">{format.label}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Time Slots */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Khung giờ rảnh trong tuần
              </label>
              
              {/* Add Time Slot Form */}
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                  <select
                    value={currentDay}
                    onChange={(e) => setCurrentDay(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {DAYS_OF_WEEK.map(day => (
                      <option key={day.value} value={day.value}>{day.label}</option>
                    ))}
                  </select>
                  
                  <input
                    type="time"
                    value={currentStartTime}
                    onChange={(e) => setCurrentStartTime(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  
                  <input
                    type="time"
                    value={currentEndTime}
                    onChange={(e) => setCurrentEndTime(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  
                  <button
                    type="button"
                    onClick={addTimeSlot}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                  >
                    <Plus size={18} />
                    Thêm
                  </button>
                </div>
              </div>

              {/* Time Slots List */}
              {timeSlots.length > 0 && (
                <div className="space-y-2">
                  {timeSlots.map((slot, index) => (
                    <div key={index} className="flex items-center justify-between bg-white border border-gray-200 rounded-lg p-3">
                      <span className="text-gray-700">
                        <span className="font-medium">{getDayLabel(slot.day)}</span>
                        {' '}từ {slot.start_time} đến {slot.end_time}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeTimeSlot(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <X size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <FileText className="inline mr-2" size={18} />
                Ghi chú thêm (không bắt buộc)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ví dụ: Ưu tiên học buổi tối, có thể học cả cuối tuần..."
              />
            </div>

            {/* Submit Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Hủy
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Đang xử lý...' : 'Đăng ký nguyện vọng'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Preferences List */}
      <div>
        <h2 className="text-2xl font-bold mb-4 text-gray-900">Danh sách nguyện vọng của bạn</h2>
        
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Đang tải...</p>
          </div>
        ) : preferences.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <AlertCircle className="mx-auto text-gray-400 mb-4" size={64} />
            <p className="text-gray-600 text-lg">Bạn chưa đăng ký nguyện vọng nào</p>
            <p className="text-gray-500 text-sm mt-2">Nhấn "Đăng ký nguyện vọng" để bắt đầu</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {preferences.map(pref => (
              <div key={pref.preference_id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <div className="p-6">
                  {/* Header */}
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-bold text-lg text-gray-900">{pref.subject_code}</h3>
                      <p className="text-gray-600 text-sm">{pref.subject_name}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(pref.status)}`}>
                      {getStatusLabel(pref.status)}
                    </span>
                  </div>

                  {/* Info */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-gray-700">
                      <Calendar size={16} className="mr-2 text-blue-600" />
                      Bắt đầu: {new Date(pref.preferred_start_date).toLocaleDateString('vi-VN')}
                    </div>
                    <div className="flex items-center text-sm text-gray-700">
                      <BookOpen size={16} className="mr-2 text-green-600" />
                      {pref.total_sessions} buổi × {pref.session_duration} phút
                    </div>
                    <div className="flex items-center text-sm text-gray-700">
                      <MapPin size={16} className="mr-2 text-purple-600" />
                      {SESSION_FORMATS.find(f => f.value === pref.session_format)?.label}
                    </div>
                  </div>

                  {/* Time Slots */}
                  <div className="mb-4">
                    <p className="text-xs font-medium text-gray-500 mb-2">Khung giờ rảnh:</p>
                    <div className="flex flex-wrap gap-2">
                      {pref.available_time_slots.map((slot, idx) => (
                        <span key={idx} className="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded">
                          {getDayLabel(slot.day)} {slot.start_time}-{slot.end_time}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Notes */}
                  {pref.notes && (
                    <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-600">{pref.notes}</p>
                    </div>
                  )}

                  {/* Actions */}
                  {pref.status === 'pending' && (
                    <div className="flex gap-2 pt-4 border-t border-gray-200">
                      <button
                        onClick={() => deletePreference(pref.preference_id)}
                        className="flex-1 bg-red-50 text-red-700 px-4 py-2 rounded-lg hover:bg-red-100 flex items-center justify-center gap-2"
                      >
                        <Trash2 size={16} />
                        Xóa
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentScheduling;

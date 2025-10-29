import React, { useState } from 'react';

const SessionHistory: React.FC = () => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data - sẽ thay bằng API call
  const sessions = [
    {
      id: 1,
      subject: 'Toán cao cấp A1',
      tutor_name: 'Nguyễn Văn A',
      date: '2025-10-25',
      time: '14:00 - 16:00',
      duration: 2,
      price: 300000,
      status: 'completed',
      rating: 5,
      feedback: 'Rất hài lòng với phiên học',
    },
    {
      id: 2,
      subject: 'Vật lý đại cương',
      tutor_name: 'Trần Thị B',
      date: '2025-10-20',
      time: '09:00 - 11:00',
      duration: 2,
      price: 240000,
      status: 'completed',
      rating: 4,
      feedback: 'Giảng dễ hiểu',
    },
    {
      id: 3,
      subject: 'Cấu trúc dữ liệu',
      tutor_name: 'Lê Văn C',
      date: '2025-10-15',
      time: '16:00 - 18:00',
      duration: 2,
      price: 360000,
      status: 'completed',
      rating: 5,
      feedback: 'Excellent!',
    },
    {
      id: 4,
      subject: 'Toán cao cấp A2',
      tutor_name: 'Nguyễn Văn A',
      date: '2025-10-10',
      time: '14:00 - 16:00',
      duration: 2,
      price: 300000,
      status: 'cancelled',
      rating: null,
      feedback: null,
    },
  ];

  const filteredSessions = sessions.filter(session => {
    const matchesFilter = filter === 'all' || session.status === filter;
    const matchesSearch = 
      session.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      session.tutor_name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const stats = {
    total: sessions.length,
    completed: sessions.filter(s => s.status === 'completed').length,
    cancelled: sessions.filter(s => s.status === 'cancelled').length,
    totalHours: sessions
      .filter(s => s.status === 'completed')
      .reduce((sum, s) => sum + s.duration, 0),
    totalSpent: sessions
      .filter(s => s.status === 'completed')
      .reduce((sum, s) => sum + s.price, 0),
    avgRating: sessions
      .filter(s => s.rating)
      .reduce((sum, s, _, arr) => sum + (s.rating || 0) / arr.length, 0)
      .toFixed(1),
  };

  const exportHistory = () => {
    // Export to CSV or PDF
    console.log('Export history');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Lịch sử học tập</h1>
        <p className="text-purple-100">
          Xem lại tất cả các phiên học đã tham gia
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="text-3xl mr-4">📚</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Tổng phiên học</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="text-3xl mr-4">✅</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Hoàn thành</p>
              <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="text-3xl mr-4">⏱️</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Tổng giờ học</p>
              <p className="text-2xl font-bold text-blue-600">{stats.totalHours}h</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="text-3xl mr-4">⭐</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Đánh giá TB</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.avgRating}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Tất cả
            </button>
            <button
              onClick={() => setFilter('completed')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'completed'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Hoàn thành
            </button>
            <button
              onClick={() => setFilter('cancelled')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'cancelled'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Đã hủy
            </button>
          </div>

          <div className="flex gap-3 w-full md:w-auto">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm kiếm..."
              className="flex-1 md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <button
              onClick={exportHistory}
              className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors whitespace-nowrap"
            >
              📊 Xuất báo cáo
            </button>
          </div>
        </div>
      </div>

      {/* Sessions List */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Ngày</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Môn học</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Gia sư</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Thời lượng</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Học phí</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Trạng thái</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Đánh giá</th>
              </tr>
            </thead>
            <tbody>
              {filteredSessions.map((session) => (
                <tr key={session.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div>
                      <p className="font-medium">{session.date}</p>
                      <p className="text-sm text-gray-600">{session.time}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4 font-medium">{session.subject}</td>
                  <td className="py-3 px-4">{session.tutor_name}</td>
                  <td className="py-3 px-4">{session.duration}h</td>
                  <td className="py-3 px-4 font-semibold text-green-600">
                    {session.price.toLocaleString()}đ
                  </td>
                  <td className="py-3 px-4">
                    {session.status === 'completed' ? (
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                        Hoàn thành
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                        Đã hủy
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    {session.rating ? (
                      <div className="flex items-center">
                        <span className="text-yellow-500 mr-1">⭐</span>
                        <span className="font-medium">{session.rating}</span>
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredSessions.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📚</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Không tìm thấy phiên học
            </h3>
            <p className="text-gray-600">
              Thử thay đổi bộ lọc hoặc tìm kiếm với từ khóa khác
            </p>
          </div>
        )}
      </div>

      {/* Total Spending */}
      <div className="card bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              Tổng chi phí học tập
            </h3>
            <p className="text-sm text-gray-600">
              Từ {stats.completed} phiên học hoàn thành
            </p>
          </div>
          <div className="text-3xl font-bold text-green-600">
            {stats.totalSpent.toLocaleString()}đ
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionHistory;

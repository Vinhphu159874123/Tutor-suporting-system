import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { MessageCircle, Star } from 'lucide-react';

interface Tutor {
  id: number;
  user_id: number;
  full_name: string;
  faculty: string;
  subjects: string[];
  hourly_rate: number;
  rating: number;
  total_sessions: number;
  bio: string;
  avatar?: string;
}

const TutorList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [minRating, setMinRating] = useState(0);

  // Mock data - sẽ thay bằng API call
  const tutors: Tutor[] = [
    {
      id: 1,
      user_id: 1,
      full_name: 'Nguyễn Văn A',
      faculty: 'Khoa KHMT',
      subjects: ['Toán cao cấp', 'Cấu trúc dữ liệu', 'Giải tích'],
      hourly_rate: 150000,
      rating: 4.8,
      total_sessions: 45,
      bio: 'Sinh viên năm 4, có kinh nghiệm dạy kèm 2 năm',
    },
    {
      id: 2,
      user_id: 2,
      full_name: 'Trần Thị B',
      faculty: 'Khoa Cơ khí',
      subjects: ['Vật lý đại cương', 'Cơ học kỹ thuật'],
      hourly_rate: 120000,
      rating: 4.5,
      total_sessions: 30,
      bio: 'Có nhiều kinh nghiệm giảng dạy vật lý',
    },
    {
      id: 3,
      user_id: 3,
      full_name: 'Lê Văn C',
      faculty: 'Khoa Điện - Điện tử',
      subjects: ['Mạch điện', 'Điện tử số', 'Vi xử lý'],
      hourly_rate: 180000,
      rating: 4.9,
      total_sessions: 60,
      bio: 'Giảng viên thỉnh giảng, 5 năm kinh nghiệm',
    },
  ];

  const allSubjects = Array.from(new Set(tutors.flatMap(t => t.subjects)));

  const filteredTutors = tutors.filter(tutor => {
    const matchesSearch = tutor.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tutor.subjects.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesSubject = selectedSubject === 'all' || tutor.subjects.includes(selectedSubject);
    const matchesRating = tutor.rating >= minRating;
    
    return matchesSearch && matchesSubject && matchesRating;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Danh sách Gia sư</h1>
        <p className="text-blue-100">
          Tìm kiếm gia sư phù hợp với nhu cầu học tập của bạn
        </p>
      </div>

      {/* Filters */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Tìm kiếm & Lọc</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tìm kiếm
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tên gia sư hoặc môn học..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Subject Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Môn học
            </label>
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Tất cả môn học</option>
              {allSubjects.map(subject => (
                <option key={subject} value={subject}>{subject}</option>
              ))}
            </select>
          </div>

          {/* Rating Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Đánh giá tối thiểu
            </label>
            <select
              value={minRating}
              onChange={(e) => setMinRating(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={0}>Tất cả</option>
              <option value={4}>Từ 4.0</option>
              <option value={4.5}>Từ 4.5</option>
              <option value={4.8}>Từ 4.8</option>
            </select>
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-600">
          Tìm thấy <span className="font-semibold text-blue-600">{filteredTutors.length}</span> gia sư
        </div>
      </div>

      {/* Tutor Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTutors.map(tutor => (
          <div key={tutor.id} className="card hover:shadow-lg transition-shadow">
            {/* Avatar */}
            <div className="flex items-center mb-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                {tutor.full_name.charAt(0)}
              </div>
              <div className="ml-4 flex-1">
                <h3 className="text-lg font-bold text-gray-900">{tutor.full_name}</h3>
                <p className="text-sm text-gray-600">{tutor.faculty}</p>
              </div>
            </div>

            {/* Rating */}
            <div className="flex items-center mb-3">
              <Star className="w-5 h-5 text-yellow-500" />
              <span className="ml-1 font-semibold text-gray-900">{tutor.rating.toFixed(1)}</span>
              <span className="ml-2 text-sm text-gray-600">
                ({tutor.total_sessions} phiên)
              </span>
            </div>

            {/* Subjects */}
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-2">Môn dạy:</p>
              <div className="flex flex-wrap gap-2">
                {tutor.subjects.slice(0, 3).map(subject => (
                  <span key={subject} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                    {subject}
                  </span>
                ))}
                {tutor.subjects.length > 3 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                    +{tutor.subjects.length - 3}
                  </span>
                )}
              </div>
            </div>

            {/* Bio */}
            <p className="text-sm text-gray-600 mb-4 line-clamp-2">
              {tutor.bio}
            </p>

            {/* Actions */}
            <div className="flex gap-2">
              <Link
                to={`/tutors/${tutor.id}`}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg text-center font-medium hover:bg-blue-700 transition-colors"
              >
                Xem chi tiết
              </Link>
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
                <MessageCircle className="w-4 h-4" />
                Nhắn tin
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredTutors.length === 0 && (
        <div className="card text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            Không tìm thấy gia sư
          </h3>
          <p className="text-gray-600">
            Thử thay đổi bộ lọc hoặc tìm kiếm với từ khóa khác
          </p>
        </div>
      )}
    </div>
  );
};

export default TutorList;

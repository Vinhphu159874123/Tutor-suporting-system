import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MessageCircle, Star, Search } from 'lucide-react';
import { tutorsApi, coursesApi } from '../../services/api';
import { toast } from 'react-toastify';
import { AxiosResponse } from 'axios';

interface Tutor {
  tutor_id: number;
  user_id: number;
  full_name: string;
  faculty?: string;
  subjects: string[];
  hourly_rate: number;
  rating: number;
  total_sessions: number;
  bio: string;
  avatar_url?: string;
}

interface Subject {
  subject_id: number;
  subject_code: string;
  subject_name: string;
}

const TutorList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [minRating, setMinRating] = useState(0);
  const [tutors, setTutors] = useState<Tutor[]>([]);
  const [allTutors, setAllTutors] = useState<Tutor[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch subjects
        const subjectsResponse = await coursesApi.getAllSubjects() as AxiosResponse<any>;
        setSubjects(subjectsResponse.data || []);

        // Fetch all tutors
        const tutorsResponse = await tutorsApi.getTutors({}) as AxiosResponse<any>;
        setAllTutors(tutorsResponse.data || []);
        setTutors(tutorsResponse.data || []);
      } catch (error: any) {
        toast.error('Không thể tải danh sách gia sư');
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Apply filters whenever filter values change
  useEffect(() => {
    let filtered = [...allTutors];

    // Filter by subject
    if (selectedSubject !== 'all') {
      filtered = filtered.filter(tutor => 
        (tutor.subjects || []).includes(selectedSubject)
      );
    }

    // Filter by rating
    if (minRating > 0) {
      filtered = filtered.filter(tutor => tutor.rating >= minRating);
    }

    // Filter by search term
    if (searchTerm.trim()) {
      filtered = filtered.filter(tutor => 
        tutor.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (tutor.subjects || []).some(s => s.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    setTutors(filtered);
  }, [selectedSubject, minRating, searchTerm, allTutors]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Danh sách Gia sư</h1>
        <p className="text-blue-100">
          Tìm kiếm gia sư phù hợp với nhu cầu học tập của bạn
        </p>
      </div>

      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Đang tải danh sách gia sư...</p>
        </div>
      )}

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
              {subjects.map((subject: Subject) => (
                <option key={subject.subject_id} value={subject.subject_name}>
                  {subject.subject_code} - {subject.subject_name}
                </option>
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
          Tìm thấy <span className="font-semibold text-blue-600">{tutors.length}</span> gia sư
        </div>
      </div>

      {/* Tutor Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tutors.map((tutor: Tutor) => (
          <div key={tutor.tutor_id} className="card hover:shadow-lg transition-shadow">
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
              <span className="ml-1 font-semibold text-gray-900">
                {typeof tutor.rating === 'number' ? tutor.rating.toFixed(1) : '0.0'}
              </span>
              <span className="ml-2 text-sm text-gray-600">
                ({tutor.total_sessions || 0} phiên)
              </span>
            </div>

            {/* Subjects */}
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-2">Môn dạy:</p>
              <div className="flex flex-wrap gap-2">
                {(tutor.subjects || []).slice(0, 3).map((subject: string, idx: number) => (
                  <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                    {subject}
                  </span>
                ))}
                {(tutor.subjects || []).length > 3 && (
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
                to={`/tutors/${tutor.tutor_id}`}
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
      {tutors.length === 0 && !loading && (
        <div className="card text-center py-12">
          <div className="flex justify-center mb-4">
            <Search className="w-16 h-16 text-gray-400" />
          </div>
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

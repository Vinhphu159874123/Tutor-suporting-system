import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {Pencil, Trash2, User as UserIcon, Users, Calendar, Star, Plus, X} from "lucide-react";
import { adminApi, authApi } from "../../services/api";
import { toast } from "react-toastify";
import { AxiosResponse } from "axios";

interface User {
  user_id: number;
  email: string;
  full_name: string;
  role: "student" | "tutor" | "coordinator" | "admin" | "department_chair";
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  faculty?: string;
  major?: string;
  student_code?: string;
  phone?: string;
}

interface SyncService {
  id: string;
  name: string;
  status: "connected" | "syncing" | "error";
  lastSync: string;
  recordsCount: number;
}


const Admin: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Determine initial tab from URL
  const getInitialTab = () => {
    const path = location.pathname;
    if (path.includes('/users')) return 'users';
    if (path.includes('/sync')) return 'sync';
    return 'overview';
  };
  
  const [activeTab, setActiveTab] = useState(getInitialTab());
  const [loading, setLoading] = useState(true);
  const [showCreateUserModal, setShowCreateUserModal] = useState(false);
  const [showEditUserModal, setShowEditUserModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [newUser, setNewUser] = useState({
    email: "",
    full_name: "",
    password: "",
    role: "student" as "student" | "tutor" | "coordinator" | "admin",
    student_code: "",
    year: "",
    phone: "",
    faculty: "",
    major: ""
  });
  const [statsData, setStatsData] = useState({
    total_users: 0,
    total_students: 0,
    total_tutors: 0,
    total_sessions: 0,
    average_rating: 0
  });
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const params = roleFilter !== 'all' ? { role: roleFilter } : {};
        const [statsRes, usersRes] = await Promise.all([
          adminApi.getAdminStats() as Promise<AxiosResponse<any>>,
          adminApi.getAllUsers(params) as Promise<AxiosResponse<any>>
        ]);
        setStatsData(statsRes.data);
        setUsers(usersRes.data);
      } catch (error: any) {
        console.error('Failed to fetch admin data:', error);
        toast.error('Không thể tải dữ liệu quản trị');
      } finally {
        setLoading(false);
      }
    };
    fetchAdminData();
  }, [roleFilter]); // Re-fetch when role filter changes

  // Update tab when URL changes
  useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    // Update URL to match tab
    const basePath = '/admin';
    const newPath = tabId === 'overview' ? basePath : `${basePath}/${tabId}`;
    navigate(newPath);
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Prepare data for registration
      const userData = {
        ...newUser,
        year: newUser.year ? parseInt(newUser.year) : undefined,
        student_code: newUser.student_code || undefined
      };

      await authApi.register(userData) as AxiosResponse<any>;
      toast.success('Tạo tài khoản thành công!');
      setShowCreateUserModal(false);
      
      // Reset form
      setNewUser({
        email: "",
        full_name: "",
        password: "",
        role: "student",
        student_code: "",
        year: "",
        phone: "",
        faculty: "",
        major: ""
      });

      // Refresh users list
      const usersRes = await adminApi.getAllUsers() as AxiosResponse<any>;
      setUsers(usersRes.data);
    } catch (error: any) {
      console.error('Failed to create user:', error);
      toast.error(error.response?.data?.detail || 'Không thể tạo tài khoản');
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm('Bạn có chắc muốn xóa người dùng này?')) {
      return;
    }
    
    try {
      await adminApi.deleteUser(userId) as AxiosResponse<any>;
      toast.success('Xóa người dùng thành công!');
      
      // Refresh users list
      const usersRes = await adminApi.getAllUsers() as AxiosResponse<any>;
      setUsers(usersRes.data);
    } catch (error: any) {
      console.error('Failed to delete user:', error);
      toast.error(error.response?.data?.detail || 'Không thể xóa người dùng');
    }
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setShowEditUserModal(true);
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;

    try {
      await adminApi.updateUser(editingUser.user_id, {
        full_name: editingUser.full_name,
        phone: editingUser.phone,
        role: editingUser.role,
        is_active: editingUser.is_active
      }) as AxiosResponse<any>;
      
      toast.success('Cập nhật thành công!');
      setShowEditUserModal(false);
      setEditingUser(null);
      
      // Refresh users list
      const usersRes = await adminApi.getAllUsers() as AxiosResponse<any>;
      setUsers(usersRes.data);
    } catch (error: any) {
      console.error('Failed to update user:', error);
      toast.error(error.response?.data?.detail || 'Không thể cập nhật người dùng');
    }
  };

  const stats = [
    { name: "Tổng số người dùng", value: loading ? "..." : String(statsData.total_users), icon: <UserIcon size={24} className="text-blue-500" />},
    { name: "Tổng số tutor", value: loading ? "..." : String(statsData.total_tutors), icon: <Users size={24} className="text-green-500" /> },
    { name: "Tổng số phiên học", value: loading ? "..." : String(statsData.total_sessions), icon: <Calendar size={24} className="text-yellow-500" /> },
    { name: "Đánh giá trung bình", value: loading ? "..." : `${statsData.average_rating}/5`, icon: <Star size={24} className="text-orange-400" /> },
  ];

  const tabs = [
    { id: "overview", label: "Tổng quan" },
    { id: "users", label: "Quản lý người dùng" },
    { id: "sync", label: "Trạng thái đồng bộ" },
  ];

  const services: SyncService[] = [
  { id: 'sso', name: 'HCMUT_SSO', status: 'connected', lastSync: '2025-11-21T14:30:00Z', recordsCount: 1247 },
  { id: 'datacore', name: 'HCMUT_DATACORE', status: 'connected', lastSync: '2025-11-21T14:15:00Z', recordsCount: 5432 },
  { id: 'library', name: 'HCMUT_LIBRARY', status: 'error', lastSync: '2025-11-21T13:00:00Z', recordsCount: 12458 },
];

  return (
    <div className="bg-gray-50 min-h-screen p-6 space-y-8">
      {/* Header */}
      <div className="bg-white border border-gray-200 shadow-sm rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Quản trị hệ thống
        </h1>
        <p className="text-gray-600">
          Trang điều khiển dành cho quản trị viên hệ thống.
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white border border-gray-200 shadow-sm rounded-lg p-4 flex gap-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`px-4 py-2 text-sm rounded 
              ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            onClick={() => handleTabChange(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content - single container */}
      <div className="bg-white border border-gray-200 shadow-sm rounded-lg p-6">
        {activeTab === "overview" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-800 mb-4">
                Tổng quan hệ thống
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat) => (
                  <div key={stat.name} className="border border-gray-200 shadow-sm bg-white p-6 rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm text-gray-600 mb-1">{stat.name}</p>
                        <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                      </div>
                      <div className="ml-4">{stat.icon}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-md font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5 text-blue-600" />
                  Phân bổ người dùng
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Students</span>
                    <span className="text-sm font-semibold text-gray-900">{statsData.total_students}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${statsData.total_users > 0 ? (statsData.total_students / statsData.total_users) * 100 : 0}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex items-center justify-between mt-4">
                    <span className="text-sm text-gray-600">Tutors</span>
                    <span className="text-sm font-semibold text-gray-900">{statsData.total_tutors}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{ width: `${statsData.total_users > 0 ? (statsData.total_tutors / statsData.total_users) * 100 : 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-md font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-yellow-600" />
                  Thống kê phiên học
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-xs text-gray-600">Tổng số phiên</p>
                      <p className="text-2xl font-bold text-gray-900">{statsData.total_sessions}</p>
                    </div>
                    <Calendar className="w-8 h-8 text-gray-400" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-xs text-gray-600">Đánh giá TB</p>
                      <p className="text-2xl font-bold text-gray-900">{statsData.average_rating}/5</p>
                    </div>
                    <Star className="w-8 h-8 text-yellow-400 fill-yellow-400" />
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Users */}
            <div className="border border-gray-200 rounded-lg p-6">
              <h3 className="text-md font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <UserIcon className="w-5 h-5 text-purple-600" />
                Người dùng mới nhất
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead>
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Tên</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Email</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Vai trò</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Ngày tạo</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {users.slice(0, 5).map((user) => (
                      <tr key={user.user_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900">{user.full_name}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{user.email}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded text-xs ${
                            user.role?.includes('admin') ? 'bg-red-100 text-red-700' :
                            user.role?.includes('coordinator') ? 'bg-purple-100 text-purple-700' :
                            user.role?.includes('tutor') ? 'bg-blue-100 text-blue-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {Array.isArray(user.role) ? user.role.join(', ') : user.role}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {new Date(user.created_at).toLocaleDateString('vi-VN')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === "users" && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-800">
                Quản lý người dùng
              </h2>
              <div className="flex items-center gap-3">
                <select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                >
                  <option value="all">Tất cả vai trò</option>
                  <option value="student">Student</option>
                  <option value="tutor">Tutor</option>
                  <option value="coordinator">Coordinator</option>
                  <option value="admin">Admin</option>
                </select>
                <button
                  onClick={() => setShowCreateUserModal(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus size={20} />
                  Tạo tài khoản
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Tên</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Email</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Vai trò</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Khoa</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">MSSV</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Thao tác</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.user_id}>
                      <td className="px-4 py-2 text-sm text-gray-900">{user.full_name}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{user.email}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">
                        <span className={`px-2 py-1 rounded text-xs ${
                          user.role?.includes('admin') ? 'bg-red-100 text-red-700' :
                          user.role?.includes('coordinator') ? 'bg-purple-100 text-purple-700' :
                          user.role?.includes('tutor') ? 'bg-blue-100 text-blue-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {Array.isArray(user.role) ? user.role.join(', ') : user.role}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-900">{user.faculty || '-'}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{user.student_code || '-'}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">
                        <div className="flex gap-2">
                          <button 
                            onClick={() => handleEditUser(user)}
                            className="text-blue-600 hover:text-blue-800 transition-colors" 
                            title="Edit"
                          >
                            <Pencil size={18} />
                          </button>
                          <button 
                            onClick={() => handleDeleteUser(user.user_id)}
                            className="text-red-600 hover:text-red-800 transition-colors" 
                            title="Delete"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}


        {activeTab === "sync" && (
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              Trạng thái đồng bộ
             </h2>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Service</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Status</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Records</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Last Sync</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Action</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {services.map((s) => (
                    <tr key={s.id}>
                      <td className="px-4 py-2 text-sm text-gray-900">{s.name}</td>
                      <td className="px-4 py-2 text-sm">
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium
                            ${ s.status === "connected" ? "bg-green-100 text-green-800"
                            : s.status === "syncing"? "bg-blue-100 text-blue-800 animate-pulse"
                            : "bg-red-100 text-red-800"}`}>
                          {s.status.charAt(0).toUpperCase() + s.status.slice(1)}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-900">{s.recordsCount.toLocaleString()}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{new Date(s.lastSync).toLocaleString()}</td>
                      <td className="px-4 py-2 text-sm">
                        <button
                          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
                          Sync Now
                        </button>
                      </td>
                    </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Create User Modal */}
      {showCreateUserModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-xl font-semibold text-gray-900">Tạo tài khoản mới</h3>
              <button
                onClick={() => setShowCreateUserModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    value={newUser.email}
                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="student@hcmut.edu.vn"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Họ và tên <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={newUser.full_name}
                    onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Nguyễn Văn A"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Mật khẩu <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    required
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="********"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Vai trò <span className="text-red-500">*</span>
                  </label>
                  <select
                    required
                    value={newUser.role}
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value as any })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="student">Student</option>
                    <option value="tutor">Tutor</option>
                    <option value="coordinator">Coordinator</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Số điện thoại
                  </label>
                  <input
                    type="tel"
                    value={newUser.phone}
                    onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="0123456789"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    MSSV (nếu là student)
                  </label>
                  <input
                    type="text"
                    value={newUser.student_code}
                    onChange={(e) => setNewUser({ ...newUser, student_code: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="2152001"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Khoa
                  </label>
                  <input
                    type="text"
                    value={newUser.faculty}
                    onChange={(e) => setNewUser({ ...newUser, faculty: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Khoa KH-KT Máy Tính"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Chuyên ngành
                  </label>
                  <input
                    type="text"
                    value={newUser.major}
                    onChange={(e) => setNewUser({ ...newUser, major: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Khoa học Máy Tính"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Năm học (nếu là student)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={newUser.year}
                    onChange={(e) => setNewUser({ ...newUser, year: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="1-5"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowCreateUserModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Tạo tài khoản
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {showEditUserModal && editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-xl font-semibold text-gray-900">Chỉnh sửa người dùng</h3>
              <button
                onClick={() => {
                  setShowEditUserModal(false);
                  setEditingUser(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleUpdateUser} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    disabled
                    value={editingUser.email}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed"
                  />
                  <p className="text-xs text-gray-500 mt-1">Email không thể thay đổi</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Họ và tên <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={editingUser.full_name}
                    onChange={(e) => setEditingUser({ ...editingUser, full_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Vai trò <span className="text-red-500">*</span>
                  </label>
                  <select
                    required
                    value={editingUser.role}
                    onChange={(e) => setEditingUser({ ...editingUser, role: e.target.value as any })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="student">Student</option>
                    <option value="tutor">Tutor</option>
                    <option value="coordinator">Coordinator</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Số điện thoại
                  </label>
                  <input
                    type="tel"
                    value={editingUser.phone || ''}
                    onChange={(e) => setEditingUser({ ...editingUser, phone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Trạng thái
                  </label>
                  <select
                    value={editingUser.is_active ? 'active' : 'inactive'}
                    onChange={(e) => setEditingUser({ ...editingUser, is_active: e.target.value === 'active' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="active">Hoạt động</option>
                    <option value="inactive">Vô hiệu hóa</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    MSSV
                  </label>
                  <input
                    type="text"
                    disabled
                    value={editingUser.student_code || '-'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed"
                  />
                  <p className="text-xs text-gray-500 mt-1">MSSV không thể thay đổi</p>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditUserModal(false);
                    setEditingUser(null);
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Cập nhật
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin;

import React, { useState, useEffect } from "react";
import {Pencil, Trash2, User as UserIcon, Users, Calendar, Star} from "lucide-react";
import { adminApi } from "../../services/api";
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
}

interface SyncService {
  id: string;
  name: string;
  status: "connected" | "syncing" | "error";
  lastSync: string;
  recordsCount: number;
}


const Admin: React.FC = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);
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
        const [statsRes, usersRes] = await Promise.all([
          adminApi.getAdminStats() as Promise<AxiosResponse<any>>,
          adminApi.getAllUsers() as Promise<AxiosResponse<any>>
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
  }, []);

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
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content - single container */}
      <div className="bg-white border border-gray-200 shadow-sm rounded-lg p-6">
        {activeTab === "overview" && (
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              Tổng quan hệ thống
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {stats.map((stat) => (
                <div key={stat.name} className="border border-gray-200 shadow-sm bg-white p-4 rounded">
                  <div className="flex items-center">
                    <div className="text-3xl mr-4">{stat.icon}</div>
                    <div>
                      <p className="text-sm text-gray-600">{stat.name}</p>
                      <p className="text-xl font-bold text-gray-900">{stat.value}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "users" && (
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              Quản lý người dùng
            </h2>

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
                          user.role === 'admin' ? 'bg-red-100 text-red-700' :
                          user.role === 'tutor' ? 'bg-blue-100 text-blue-700' :
                          user.role === 'coordinator' ? 'bg-purple-100 text-purple-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-900">-</td>
                      <td className="px-4 py-2 text-sm text-gray-900">-</td>
                      <td className="px-4 py-2 text-sm text-gray-900 flex gap-4">
                        <button className="hover:text-blue-800" title="Edit">
                         <Pencil size={18} />
                        </button>
                        <button className="hover:text-red-800" title="Delete">
                        <Trash2 size={18} />
                        </button>
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
    </div>
  );
};

export default Admin;

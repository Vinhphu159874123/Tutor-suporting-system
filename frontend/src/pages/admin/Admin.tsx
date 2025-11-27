import React, { useState } from "react";
import {Pencil, Trash2, User, Users, Calendar, Star} from "lucide-react";

interface User {
  id: string;
  name: string;
  email: string;
  role: "student" | "tutor" | "coordinator" | "admin" | "department_chair";
  studentId?: string;
  department?: string;
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

  const stats = [
    { name: "Tổng số sinh viên", value: "1004", icon: <User size={24} className="text-blue-500" />},
    { name: "Tổng số tutor", value: "18", icon: <Users size={24} className="text-green-500" /> },
    { name: "Tổng số phiên học", value: "120", icon: <Calendar size={24} className="text-yellow-500" /> },
    { name: "Đánh giá trung bình", value: "4.8/5", icon: <Star size={24} className="text-orange-400" /> },
  ];

  const tabs = [
    { id: "overview", label: "Tổng quan" },
    { id: "users", label: "Quản lý người dùng" },
    { id: "sync", label: "Trạng thái đồng bộ" },
  ];

  const mockUsers: User[] = [
    { id: "u1", name: "Nguyễn Văn A", email: "a@hcmut.edu.vn", role: "student", studentId: "2021001", department: "Computer Science" },
    { id: "u2", name: "Trần Thị B", email: "b@hcmut.edu.vn", role: "tutor", department: "Software Engineering" },
    { id: "u3", name: "Lê Văn C", email: "c@hcmut.edu.vn", role: "coordinator", department: "Chemistry" },
    { id: "u4", name: "Phạm Thị D", email: "d@hcmut.edu.vn", role: "admin" },
    { id: "u5", name: "Ngô Văn E", email: "e@hcmut.edu.vn", role: "student", studentId: "2351111", department: "Computer Science" },
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
                  {mockUsers.map((user) => (
                    <tr key={user.id}>
                      <td className="px-4 py-2 text-sm text-gray-900">{user.name}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{user.email}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{user.role}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{user.department || "-"}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{user.studentId || "-"}</td>
                      <td className="px-4 py-2 text-sm text-gray-900 flex gap-4">
                        <button className="hover:text-blue-800" title="Edit">
                         < Pencil size={18} />
                        </button>
                        <button className="hover:text-red-800" title="Delete">
                        < Trash2 size={18} />
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

import React, { ReactNode, useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { useUnreadMessagesStore } from "../stores/unreadMessagesStore";
import { notificationsApi } from "../services/api";
import { 
  LayoutDashboard, 
  BookOpen, 
  Calendar, 
  Clock, 
  GraduationCap, 
  Bell, 
  Settings as SettingsIcon, 
  MessageSquare, 
  BarChart3, 
  Shield,
  Users,
  RefreshCw
} from "lucide-react";

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout, currentMode, switchMode } = useAuthStore();
  const { getTotalUnread } = useUnreadMessagesStore();
  const location = useLocation();
  const [unreadCount, setUnreadCount] = useState(0);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const totalUnreadMessages = getTotalUnread();

  // Determine active mode (use currentMode if available, fallback to user.role)
  const userRoles = user ? (Array.isArray(user.role) ? user.role : [user.role]) : ['student'];
  const activeMode = currentMode || userRoles[0] || 'student';

  // Check if user has multiple roles
  const hasMultipleRoles = userRoles.length > 1;

  // Fetch unread notifications count
  useEffect(() => {
    const fetchUnreadCount = async () => {
      try {
        const response: any = await notificationsApi.getUnreadCount();
        setUnreadCount(response.data?.unread_count || 0);
      } catch (error) {
        console.error("Failed to fetch unread notifications:", error);
      }
    };

    if (user) {
      fetchUnreadCount();
      // Poll every 30 seconds
      const interval = setInterval(fetchUnreadCount, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  // Navigation for Coordinator
  const coordinatorNavigation = [
    { name: "Dashboard", href: "/coor", icon: <LayoutDashboard size={20} /> },
    { name: "Duyệt Tutor", href: "/coor/review", icon: <GraduationCap size={20} /> },
    { name: "Quản lý Giảng viên", href: "/coordinator/tutors", icon: <Users size={20} /> },
    { name: "Quản lý Buổi học", href: "/coor/sessions", icon: <Calendar size={20} /> },
    { name: "Báo cáo", href: "/reports", icon: <BarChart3 size={20} /> },
    { name: "Thông báo", href: "/notifications", icon: <Bell size={20} /> },
    { name: "Cài đặt", href: "/settings", icon: <SettingsIcon size={20} /> },
  ];

  // Navigation for Admin
  const adminNavigation = [
    { name: "Dashboard", href: "/admin", icon: <Shield size={20} /> },
    { name: "Quản lý người dùng", href: "/admin/users", icon: <GraduationCap size={20} /> },
    { name: "Báo cáo", href: "/reports", icon: <BarChart3 size={20} /> },
    { name: "Cài đặt", href: "/settings", icon: <SettingsIcon size={20} /> },
  ];

  // Navigation for Students and Tutors (default)
  const defaultNavigation = [
    { name: "Dashboard", href: "/dashboard", icon: <LayoutDashboard size={20} /> },
    { name: "Tìm kiếm khóa học", href: "/browse-courses", icon: <BookOpen size={20} /> },
    { name: "Môn học của tôi", href: "/my-courses", icon: <BookOpen size={20} /> },
    { name: "Đăng ký lịch học", href: "/student/scheduling", icon: <Calendar size={20} /> },
    { name: "Study Groups", href: "/study-groups", icon: <Users size={20} /> },
    { name: "Forum", href: "/forum", icon: <MessageSquare size={20} /> },
    { name: "Notifications", href: "/notifications", icon: <Bell size={20} /> },
    { name: "Settings", href: "/settings", icon: <SettingsIcon size={20} /> },
  ];

  // Navigation for Tutors (with session requests)
  const tutorNavigation = [
    { name: "Dashboard", href: "/dashboard", icon: <LayoutDashboard size={20} /> },
    { name: "Môn học tôi dạy", href: "/my-courses", icon: <BookOpen size={20} /> },
    { name: "Thống kê nguyện vọng", href: "/tutor/statistics", icon: <BarChart3 size={20} /> },
    { name: "Study Groups", href: "/study-groups", icon: <Users size={20} /> },
    { name: "Forum", href: "/forum", icon: <MessageSquare size={20} /> },
    { name: "Notifications", href: "/notifications", icon: <Bell size={20} /> },
    { name: "Settings", href: "/settings", icon: <SettingsIcon size={20} /> },
  ];

  // Select navigation based on active mode
  let navigation = defaultNavigation;
  if (activeMode === 'coordinator') {
    navigation = coordinatorNavigation;
  } else if (activeMode === 'admin') {
    navigation = adminNavigation;
  } else if (activeMode === 'tutor') {
    navigation = tutorNavigation;
  } else {
    navigation = defaultNavigation; // student mode
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <h1 className="text-lg font-bold text-blue-600">HCMUT Tutor</h1>
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 rounded-md text-gray-600 hover:bg-gray-100"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {isMobileMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {/* Sidebar - responsive */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-gradient-to-b from-white to-blue-50/30 shadow-2xl transition-transform duration-300 lg:translate-x-0 backdrop-blur-sm ${
        isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <Link to="/dashboard" className="flex h-16 items-center justify-center border-b border-blue-100 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 transition-all duration-300 cursor-pointer group">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent group-hover:scale-105 transition-transform duration-300">
            HCMUT Tutor System
          </h1>
        </Link>

        <nav className="mt-8 px-3">
          <div className="space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              const isNotificationItem = item.href === "/notifications";
              const isStudyGroupsItem = item.href === "/study-groups";
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    group flex items-center px-4 py-3 text-sm font-medium transition-all duration-300 rounded-xl relative overflow-hidden
                    ${isActive
                      ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg shadow-blue-500/50 scale-105"
                      : "text-gray-700 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 hover:text-blue-600 hover:scale-105 hover:shadow-md"
                    }
                  `}
                >
                  {/* Active indicator */}
                  {isActive && (
                    <span className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full"></span>
                  )}
                  
                  <span className={`mr-3 relative transition-transform duration-300 ${
                    isActive ? 'scale-110' : 'group-hover:scale-110 group-hover:rotate-12'
                  }`}>
                    {item.icon}
                    {isNotificationItem && unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white animate-pulse shadow-lg shadow-red-500/50">
                        {unreadCount > 9 ? '9+' : unreadCount}
                      </span>
                    )}
                    {isStudyGroupsItem && totalUnreadMessages > 0 && (
                      <span className="absolute -top-1 -right-1 group/badge">
                        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-br from-green-400 to-green-600 text-[11px] font-extrabold text-white animate-bounce shadow-xl shadow-green-500/60 ring-2 ring-white">
                          {totalUnreadMessages > 9 ? '9+' : totalUnreadMessages}
                        </span>
                        <span className="absolute left-1/2 -translate-x-1/2 top-full mt-2 hidden group-hover/badge:block w-max px-3 py-1.5 bg-gray-900 text-white text-xs rounded-lg shadow-lg z-50 whitespace-nowrap">
                          Bạn có {totalUnreadMessages} tin nhắn chưa đọc từ nhóm học tập
                          <span className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45"></span>
                        </span>
                      </span>
                    )}
                  </span>
                  <span className="relative z-10">{item.name}</span>
                  
                  {/* Hover effect */}
                  {!isActive && (
                    <span className="absolute inset-0 bg-gradient-to-r from-blue-400/0 via-purple-400/0 to-blue-400/0 group-hover:from-blue-400/10 group-hover:via-purple-400/10 group-hover:to-blue-400/10 transition-all duration-500"></span>
                  )}
                </Link>
              );
            })}
          </div>
        </nav>
      </div>

      {/* Mobile overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Main content - responsive padding */}
      <div className="lg:pl-64 pt-16 lg:pt-0">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex h-16 items-center justify-between px-4 lg:px-6">
            <h2 className="text-lg lg:text-2xl font-semibold text-gray-900 truncate">
              {navigation.find((item) => item.href === location.pathname)
                ?.name || "Dashboard"}
            </h2>

            <div className="flex items-center gap-2 lg:gap-4">
              <div className="text-xs lg:text-sm text-gray-600 hidden sm:block">
                Xin chào, {user?.full_name}
              </div>

              {/* Role Switcher */}
              {hasMultipleRoles && (
                <div className="relative group">
                  <button className="flex items-center space-x-1 lg:space-x-2 px-2 lg:px-3 py-2 text-xs lg:text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors">
                    <RefreshCw className="w-3 h-3 lg:w-4 lg:h-4" />
                    <span className="font-medium capitalize hidden sm:inline">{activeMode}</span>
                  </button>

                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                    {userRoles.map((role) => (
                      <button
                        key={role}
                        onClick={() => switchMode(role)}
                        className={`block w-full text-left px-4 py-2 text-sm transition-colors ${
                          activeMode === role
                            ? 'bg-blue-50 text-blue-700 font-medium'
                            : 'text-gray-700 hover:bg-gray-100'
                        }`}
                      >
                        <span className="capitalize">{role}</span>
                        {activeMode === role && (
                          <span className="ml-2 text-xs">✓</span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="relative group">
                <button className="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500">
                  {user?.avatar_url ? (
                    <img
                      className="h-8 w-8 rounded-full bg-gray-300"
                      src={user.avatar_url}
                      alt={user?.full_name}
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                      {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                  )}
                </button>

                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Thông tin cá nhân
                  </Link>
                  <button
                    onClick={logout}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Đăng xuất
                  </button>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page content - responsive padding */}
        <main className="p-4 lg:p-6">{children}</main>
      </div>
    </div>
  );
};

export default Layout;

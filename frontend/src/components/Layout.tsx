import React, { ReactNode, useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
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
  Shield 
} from "lucide-react";

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const [unreadCount, setUnreadCount] = useState(0);

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
    { name: "Các khóa học của tôi", href: "/courses", icon: <BookOpen size={20} /> },
    { name: "Sessions", href: "/sessions", icon: <Calendar size={20} /> },
    { name: "Scheduling", href: "/scheduling", icon: <Clock size={20} /> },
    { name: "Tutors", href: "/tutors", icon: <GraduationCap size={20} /> },
    { name: "Notifications", href: "/notifications", icon: <Bell size={20} /> },
    { name: "Settings", href: "/settings", icon: <SettingsIcon size={20} /> },
    { name: "Forum", href: "/forum", icon: <MessageSquare size={20} /> },
  ];

  // Navigation for Tutors (with session requests)
  const tutorNavigation = [
    { name: "Dashboard", href: "/dashboard", icon: <LayoutDashboard size={20} /> },
    { name: "Yêu cầu đặt lịch", href: "/tutors/requests", icon: <Calendar size={20} /> },
    { name: "Sessions", href: "/sessions", icon: <Calendar size={20} /> },
    { name: "Scheduling", href: "/scheduling", icon: <Clock size={20} /> },
    { name: "Notifications", href: "/notifications", icon: <Bell size={20} /> },
    { name: "Settings", href: "/settings", icon: <SettingsIcon size={20} /> },
    { name: "Forum", href: "/forum", icon: <MessageSquare size={20} /> },
  ];

  // Select navigation based on role
  let navigation = defaultNavigation;
  if (user?.role === 'coordinator') {
    navigation = coordinatorNavigation;
  } else if (user?.role === 'admin') {
    navigation = adminNavigation;
  } else if (user?.role === 'tutor') {
    navigation = tutorNavigation;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-16 items-center justify-center border-b border-gray-200">
          <h1 className="text-xl font-bold text-blue-600">
            HCMUT Tutor System
          </h1>
        </div>

        <nav className="mt-8">
          <div className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              const isNotificationItem = item.href === "/notifications";
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    group flex items-center px-4 py-3 text-sm font-medium transition-colors
                    ${isActive
                      ? "bg-blue-50 text-blue-600 border-r-2 border-blue-600"
                      : "text-gray-700 hover:bg-gray-50 hover:text-blue-600"
                    }
                  `}
                >
                  <span className="mr-3 relative">
                    {item.icon}
                    {isNotificationItem && unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                        {unreadCount > 9 ? '9+' : unreadCount}
                      </span>
                    )}
                  </span>
                  {item.name}
                </Link>
              );
            })}
          </div>
        </nav>
      </div>

      {/* Main content */}
      <div className="pl-64">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex h-16 items-center justify-between px-6">
            <h2 className="text-2xl font-semibold text-gray-900">
              {navigation.find((item) => item.href === location.pathname)
                ?.name || "Dashboard"}
            </h2>

            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Xin chào, {user?.full_name}
              </div>

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

        {/* Page content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
};

export default Layout;

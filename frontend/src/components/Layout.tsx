import React, { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { 
  LayoutDashboard, 
  BookOpen, 
  Calendar, 
  Clock, 
  GraduationCap, 
  Bell, 
  Settings as SettingsIcon, 
  MessageSquare, 
  CheckSquare, 
  BarChart3, 
  Shield 
} from "lucide-react";

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuthStore();
  const location = useLocation();

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: <LayoutDashboard size={20} /> },
    { name: "Các khóa học của tôi", href: "/courses", icon: <BookOpen size={20} /> },
    { name: "Sessions", href: "/sessions", icon: <Calendar size={20} /> },
    { name: "Scheduling", href: "/scheduling", icon: <Clock size={20} /> },
    { name: "Tutors", href: "/tutors", icon: <GraduationCap size={20} /> },
    { name: "Notifications", href: "/notifications", icon: <Bell size={20} /> },
    { name: "Settings", href: "/settings", icon: <SettingsIcon size={20} /> },
    { name: "Forum", href: "/forum", icon: <MessageSquare size={20} /> },
    { name: "Review Sessions", href: "/review-sessions", icon: <CheckSquare size={20} />, roles: ["coordinator"] },
    {
      name: "Reports",
      href: "/reports",
      icon: <BarChart3 size={20} />,
      roles: ["admin", "coordinator", "department_chair"],
    },
    { name: "Admin", href: "/admin", icon: <Shield size={20} />, roles: ["admin"] },
  ];

  const filteredNavigation = navigation.filter(
    (item) => !item.roles || item.roles.includes(user?.role || "")
  );

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
            {filteredNavigation.map((item) => {
              const isActive = location.pathname === item.href;
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
                  <span className="mr-3">{item.icon}</span>
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

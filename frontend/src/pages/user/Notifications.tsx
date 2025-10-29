import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Notifications: React.FC = () => {
  const [filter, setFilter] = useState('all');

  // Mock data - sẽ thay bằng API call
  const notifications = [
    {
      id: 1,
      type: 'session',
      title: 'Phiên học sắp diễn ra',
      message: 'Bạn có phiên học "Toán cao cấp A1" vào ngày mai lúc 14:00',
      time: '2 giờ trước',
      read: false,
      icon: '📚',
      link: '/sessions/1',
    },
    {
      id: 2,
      type: 'payment',
      title: 'Thanh toán thành công',
      message: 'Bạn đã thanh toán thành công 300,000đ cho phiên học #123',
      time: '5 giờ trước',
      read: false,
      icon: '💳',
      link: '/sessions/123',
    },
    {
      id: 3,
      type: 'review',
      title: 'Đánh giá mới',
      message: 'Nguyễn Văn A đã đánh giá 5⭐ cho phiên học của bạn',
      time: '1 ngày trước',
      read: true,
      icon: '⭐',
      link: '/sessions/120',
    },
    {
      id: 4,
      type: 'system',
      title: 'Cập nhật hệ thống',
      message: 'Hệ thống đã được cập nhật phiên bản mới với nhiều tính năng',
      time: '2 ngày trước',
      read: true,
      icon: '🔔',
      link: null,
    },
    {
      id: 5,
      type: 'message',
      title: 'Tin nhắn mới',
      message: 'Trần Thị B đã gửi tin nhắn cho bạn',
      time: '3 ngày trước',
      read: true,
      icon: '💬',
      link: '/forum',
    },
  ];

  const filteredNotifications = filter === 'all' 
    ? notifications 
    : filter === 'unread'
    ? notifications.filter(n => !n.read)
    : notifications.filter(n => n.type === filter);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAllAsRead = () => {
    // Call API to mark all as read
    console.log('Mark all as read');
  };

  const markAsRead = (id: number) => {
    // Call API to mark specific notification as read
    console.log('Mark as read:', id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Thông báo</h1>
        <p className="text-blue-100">
          Bạn có {unreadCount} thông báo chưa đọc
        </p>
      </div>

      <div className="card">
        {/* Filters */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Tất cả
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'unread'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Chưa đọc ({unreadCount})
            </button>
            <button
              onClick={() => setFilter('session')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'session'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Phiên học
            </button>
            <button
              onClick={() => setFilter('message')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'message'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Tin nhắn
            </button>
            <button
              onClick={() => setFilter('system')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'system'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Hệ thống
            </button>
          </div>

          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Đánh dấu tất cả đã đọc
            </button>
          )}
        </div>

        {/* Notifications List */}
        <div className="space-y-3">
          {filteredNotifications.map((notification) => (
            <div
              key={notification.id}
              className={`p-4 rounded-lg border-2 transition-all ${
                notification.read
                  ? 'border-gray-200 bg-white'
                  : 'border-blue-200 bg-blue-50'
              }`}
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">{notification.icon}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">
                        {notification.title}
                      </h3>
                      <p className="text-gray-700 mb-2">{notification.message}</p>
                      <p className="text-sm text-gray-500">{notification.time}</p>
                    </div>
                    {!notification.read && (
                      <span className="w-3 h-3 bg-blue-600 rounded-full flex-shrink-0 mt-1"></span>
                    )}
                  </div>
                  <div className="flex gap-3 mt-3">
                    {notification.link && (
                      <Link
                        to={notification.link}
                        className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                      >
                        Xem chi tiết →
                      </Link>
                    )}
                    {!notification.read && (
                      <button
                        onClick={() => markAsRead(notification.id)}
                        className="text-gray-600 hover:text-gray-700 font-medium text-sm"
                      >
                        Đánh dấu đã đọc
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredNotifications.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔔</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Không có thông báo
            </h3>
            <p className="text-gray-600">
              {filter === 'unread' 
                ? 'Bạn đã đọc hết tất cả thông báo' 
                : 'Chưa có thông báo nào'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Notifications;

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  CalendarClock,
  CreditCard,
  Star,
  BellRing,
  MessageSquareText,
  AlertCircle,
} from 'lucide-react';
import { notificationsApi } from '../../services/api';
import { toast } from 'react-toastify';
import { AxiosResponse } from 'axios';

type NotificationItem = {
  id: number;
  type: string;
  title: string;
  message: string;
  time: string;
  read: boolean;
  icon: React.ComponentType<{ className?: string }>;
  link: string | null;
};

const iconClasses =
  'h-5 w-5 text-blue-600';

const Notifications: React.FC = () => {
  const [filter, setFilter] = useState('all');
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const params = filter !== 'all' ? { is_read: filter === 'read' } : {};
        const response = await notificationsApi.getNotifications(params) as AxiosResponse<any>;
        setNotifications(response.data);
      } catch (error: any) {
        console.error('Failed to fetch notifications:', error);
        toast.error('Không thể tải thông báo');
      } finally {
        setLoading(false);
      }
    };
    fetchNotifications();
  }, [filter]);

  const getIcon = (type: string) => {
    switch (type) {
      case 'session': return CalendarClock;
      case 'payment': return CreditCard;
      case 'review': return Star;
      case 'message': return MessageSquareText;
      default: return BellRing;
    }
  };

  const filteredNotifications = notifications.filter((notif) => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !notif.is_read;
    if (filter === 'read') return notif.is_read;
    return true;
  });

  const unreadCount = notifications.filter(n => !n.is_read).length;

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
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Đang tải...</p>
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Không có thông báo nào
            </div>
          ) : (
            filteredNotifications.map((notification) => {
              const Icon = getIcon(notification.type);
              return (
                <div
                  key={notification.notification_id}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    notification.is_read
                      ? 'border-gray-200 bg-white'
                      : 'border-blue-200 bg-blue-50'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">
                      <Icon className={iconClasses} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 mb-1">
                            {notification.title}
                          </h3>
                          <p className="text-gray-700 mb-2">{notification.message}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(notification.created_at).toLocaleDateString('vi-VN')}
                          </p>
                        </div>
                        {!notification.is_read && (
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
                        {!notification.is_read && (
                          <button
                            onClick={() => markAsRead(notification.notification_id)}
                            className="text-gray-600 hover:text-gray-700 font-medium text-sm"
                          >
                            Đánh dấu đã đọc
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
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

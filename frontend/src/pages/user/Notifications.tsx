import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  CalendarClock,
  CreditCard,
  Star,
  BellRing,
  MessageSquareText,
  AlertCircle,
  X,
  Clock,
  BookOpen,
  User,
  FileText,
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
  const [selectedNotification, setSelectedNotification] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);

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
      case 'subject_registration': return AlertCircle;
      case 'subject_registration_submitted': return BellRing;
      case 'tutor_registration': return AlertCircle;
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

  const markAllAsRead = async () => {
    try {
      await notificationsApi.markAllAsRead();
      // Update all notifications to read
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      toast.success('Đã đánh dấu tất cả là đã đọc');
    } catch (error) {
      console.error('Failed to mark all as read:', error);
      toast.error('Không thể đánh dấu tất cả là đã đọc');
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await notificationsApi.markAsRead(id);
      // Refresh notifications
      setNotifications(prev => 
        prev.map(n => n.notification_id === id ? { ...n, is_read: true } : n)
      );
      toast.success('Đã đánh dấu là đã đọc');
    } catch (error) {
      console.error('Failed to mark as read:', error);
      toast.error('Không thể đánh dấu là đã đọc');
    }
  };

  const handleNotificationClick = async (notification: any) => {
    console.log('=== NOTIFICATION CLICKED ===');
    console.log('Full notification:', notification);
    console.log('notification.data:', notification.data);
    console.log('typeof data:', typeof notification.data);
    
    setSelectedNotification(notification);
    setShowModal(true);
    
    // Mark as read when opening
    if (!notification.is_read) {
      await markAsRead(notification.notification_id);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'approved': return 'bg-green-100 text-green-800 border-green-300';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return 'Đang chờ duyệt';
      case 'approved': return 'Đã duyệt';
      case 'rejected': return 'Đã từ chối';
      default: return status;
    }
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

          <div className="flex gap-3">
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Đánh dấu tất cả đã đọc
              </button>
            )}
            {notifications.some(n => n.is_read) && (
              <button
                onClick={async () => {
                  if (window.confirm('Bạn có chắc muốn xóa tất cả thông báo đã đọc?')) {
                    try {
                      await notificationsApi.deleteReadNotifications();
                      setNotifications(prev => prev.filter(n => !n.is_read));
                      toast.success('Đã xóa tất cả thông báo đã đọc');
                    } catch (error) {
                      console.error('Failed to delete read notifications:', error);
                      toast.error('Không thể xóa thông báo');
                    }
                  }
                }}
                className="text-red-600 hover:text-red-700 font-medium"
              >
                Xóa thông báo đã đọc
              </button>
            )}
          </div>
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
              const notificationData = notification.data 
                ? (typeof notification.data === 'string' ? JSON.parse(notification.data) : notification.data)
                : {};
              const isPending = notificationData.status === 'pending';
              
              return (
                <div
                  key={notification.notification_id}
                  onClick={() => handleNotificationClick(notification)}
                  className={`p-4 rounded-lg border-2 transition-all cursor-pointer hover:shadow-md ${
                    isPending
                      ? 'border-orange-300 bg-orange-50'
                      : notification.is_read
                      ? 'border-gray-200 bg-white'
                      : 'border-blue-200 bg-blue-50'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${
                      isPending ? 'bg-orange-100' : 'bg-blue-50'
                    }`}>
                      <Icon className={isPending ? 'h-5 w-5 text-orange-600' : iconClasses} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-gray-900">
                              {notification.title}
                            </h3>
                            {isPending && (
                              <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor('pending')}`}>
                                <Clock className="inline h-3 w-3 mr-1" />
                                {getStatusText('pending')}
                              </span>
                            )}
                          </div>
                          <p className="text-gray-700 mb-2">{notification.message}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(notification.created_at).toLocaleDateString('vi-VN', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>
                        {!notification.is_read && (
                          <span className={`w-3 h-3 rounded-full flex-shrink-0 mt-1 ${
                            isPending ? 'bg-orange-600' : 'bg-blue-600'
                          }`}></span>
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

      {/* Modal Chi Tiết */}
      {showModal && selectedNotification && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Chi tiết thông báo</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-6">
              {/* Notification Info */}
              <div>
                <div className="flex items-start gap-4 mb-4">
                  <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${
                    selectedNotification.data && (typeof selectedNotification.data === 'string' ? JSON.parse(selectedNotification.data) : selectedNotification.data).status === 'pending'
                      ? 'bg-orange-100'
                      : 'bg-blue-50'
                  }`}>
                    {React.createElement(getIcon(selectedNotification.type), {
                      className: selectedNotification.data && (typeof selectedNotification.data === 'string' ? JSON.parse(selectedNotification.data) : selectedNotification.data).status === 'pending'
                        ? 'h-7 w-7 text-orange-600'
                        : 'h-7 w-7 text-blue-600'
                    })}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {selectedNotification.title}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {new Date(selectedNotification.created_at).toLocaleDateString('vi-VN', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>

                <p className="text-gray-700 mb-4">{selectedNotification.message}</p>
              </div>

              {/* Registration Details */}
              {selectedNotification.data && (() => {
                const data = typeof selectedNotification.data === 'string' 
                  ? JSON.parse(selectedNotification.data) 
                  : selectedNotification.data;
                console.log('Modal data:', data);
                return (
                  <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                    <h4 className="font-semibold text-gray-900 mb-3">Thông tin đăng ký</h4>
                    
                    {data.subject_code && (
                      <div className="flex items-start gap-3">
                        <BookOpen className="h-5 w-5 text-gray-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-gray-600">Môn học</p>
                          <p className="font-medium text-gray-900">
                            {data.subject_code} - {data.subject_name}
                          </p>
                        </div>
                      </div>
                    )}

                    {data.gpa && (
                      <div className="flex items-start gap-3">
                        <Star className="h-5 w-5 text-gray-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-gray-600">GPA</p>
                          <p className="font-medium text-gray-900">{data.gpa}</p>
                        </div>
                      </div>
                    )}

                    {data.bio && (
                      <div className="flex items-start gap-3">
                        <FileText className="h-5 w-5 text-gray-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-gray-600">Giới thiệu bản thân</p>
                          <p className="font-medium text-gray-900">{data.bio}</p>
                        </div>
                      </div>
                    )}

                    {data.qualifications && (
                      <div className="flex items-start gap-3">
                        <FileText className="h-5 w-5 text-gray-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-gray-600">Chứng chỉ / Kinh nghiệm</p>
                          <p className="font-medium text-gray-900">{data.qualifications}</p>
                        </div>
                      </div>
                    )}

                    {data.status && (
                      <div className="flex items-start gap-3">
                        <AlertCircle className="h-5 w-5 text-gray-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-gray-600">Trạng thái</p>
                          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium border mt-1 ${getStatusColor(data.status)}`}>
                            {getStatusText(data.status)}
                          </span>
                        </div>
                      </div>
                    )}

                    {data.registration_id && (
                      <div className="flex items-start gap-3">
                        <User className="h-5 w-5 text-gray-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-gray-600">Mã đăng ký</p>
                          <p className="font-mono text-sm text-gray-900">#{data.registration_id}</p>
                        </div>
                      </div>
                    )}

                    {/* Course Schedule Information */}
                    {(data.total_sessions || data.start_date || data.end_date) && (
                      <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <p className="text-sm font-semibold text-green-900 mb-2">Thông tin khóa học</p>
                        <div className="space-y-1 text-sm">
                          {data.total_sessions && (
                            <div>
                              <span className="text-gray-600">Số buổi học:</span>
                              <span className="ml-2 font-medium text-gray-900">
                                {data.total_sessions} buổi
                              </span>
                            </div>
                          )}
                          {data.start_date && (
                            <div>
                              <span className="text-gray-600">Ngày bắt đầu:</span>
                              <span className="ml-2 font-medium text-gray-900">
                                {new Date(data.start_date).toLocaleDateString("vi-VN")}
                              </span>
                            </div>
                          )}
                          {data.end_date && (
                            <div>
                              <span className="text-gray-600">Ngày kết thúc:</span>
                              <span className="ml-2 font-medium text-gray-900">
                                {new Date(data.end_date).toLocaleDateString("vi-VN")}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {data.availability && Object.keys(data.availability).some(day => 
                      Array.isArray(data.availability[day]) && data.availability[day].length > 0
                    ) && (
                      <div className="flex items-start gap-3">
                        <Clock className="h-5 w-5 text-gray-500 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-sm text-gray-600 mb-2">Lịch rảnh đăng ký</p>
                          <div className="space-y-1">
                            {Object.entries(data.availability).map(([day, times]: [string, any]) => {
                              if (!Array.isArray(times) || times.length === 0) return null;
                              const dayNames: { [key: string]: string } = {
                                monday: 'Thứ Hai',
                                tuesday: 'Thứ Ba',
                                wednesday: 'Thứ Tư',
                                thursday: 'Thứ Năm',
                                friday: 'Thứ Sáu',
                                saturday: 'Thứ Bảy',
                                sunday: 'Chủ Nhật'
                              };
                              return (
                                <div key={day} className="flex items-center gap-2 text-sm">
                                  <span className="font-medium text-gray-700 min-w-[80px]">{dayNames[day]}:</span>
                                  <span className="text-gray-900">{times.join(', ')}</span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })()}

              {/* Status Message */}
              {selectedNotification.data && (() => {
                const data = typeof selectedNotification.data === 'string' 
                  ? JSON.parse(selectedNotification.data) 
                  : selectedNotification.data;
                if (data.status === 'pending') {
                  return (
                    <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                      <div className="flex gap-3">
                        <Clock className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="font-medium text-orange-900 mb-1">Đơn đăng ký đang chờ xử lý</p>
                          <p className="text-sm text-orange-700">
                            Đơn đăng ký của bạn đang được coordinator xem xét. Bạn sẽ nhận được thông báo khi đơn được phê duyệt.
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                }
                return null;
              })()}
            </div>

            {/* Modal Footer */}
            <div className="border-t px-6 py-4 bg-gray-50">
              <div className="flex gap-3">
                {!selectedNotification.is_read && (
                  <button
                    onClick={async () => {
                      await markAsRead(selectedNotification.notification_id);
                      setSelectedNotification({ ...selectedNotification, is_read: true });
                    }}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                  >
                    Đánh dấu đã đọc
                  </button>
                )}
                <button
                  onClick={() => setShowModal(false)}
                  className={`${selectedNotification.is_read ? 'w-full' : 'flex-1'} px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium`}
                >
                  Đóng
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Notifications;

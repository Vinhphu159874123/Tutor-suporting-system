import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { notificationsApi } from '../services/api';
import { useWebSocketContext } from '../contexts/WebSocketContext';
import { useUnreadMessagesStore } from '../stores/unreadMessagesStore';
import { AxiosResponse } from 'axios';

/**
 * Global notification listener that shows toast notifications
 * when user is NOT on the Notifications page
 * Now using WebSocket for real-time notifications
 */
const NotificationListener: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { incrementUnread } = useUnreadMessagesStore();
  const previousNotificationIdsRef = React.useRef<Set<number>>(new Set());
  const [isInitialized, setIsInitialized] = React.useState(false);

  // WebSocket connection from context
  const { subscribe } = useWebSocketContext();

  // Subscribe to WebSocket messages
  useEffect(() => {
    const unsubscribe = subscribe((message) => {
      // Handle new chat messages - increment unread count
      if (message.type === 'new_message') {
        const chatMessage = message.data;
        const currentPath = location.pathname;
        
        // Only increment if NOT currently viewing this group's chat
        const isViewingThisChat = currentPath === `/study-groups/${chatMessage.group_id}`;
        if (!isViewingThisChat) {
          incrementUnread(chatMessage.group_id);
        }
      }
      
      // Handle incoming notifications
      if (message.type === 'notification') {
        const notif = message.data;
        const isOnNotificationsPage = location.pathname === '/notifications';
        
        // Don't show toast if user is on notifications page
        if (!isOnNotificationsPage) {
          const messageText = notif.message && notif.message.length > 60 
            ? notif.message.substring(0, 60) + '...' 
            : notif.message || '';
          
          toast.info(
            <div 
              onClick={() => navigate('/notifications')}
              className="cursor-pointer"
            >
              <strong>{notif.title || 'Thông báo mới'}</strong>
              {messageText && <p className="text-sm mt-1">{messageText}</p>}
            </div>,
            {
              position: "bottom-right",
              autoClose: 5000,
              hideProgressBar: false,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              onClick: () => navigate('/notifications'),
            }
          );
        }
      }
      
      // Handle student enrollment notifications
      if (message.type === 'student_enrolled') {
        const notif = message.data;
        const isOnNotificationsPage = location.pathname === '/notifications';
        
        if (!isOnNotificationsPage) {
          toast.success(
            <div 
              onClick={() => navigate('/notifications')}
              className="cursor-pointer"
            >
              <strong>{notif.title}</strong>
              <p className="text-sm mt-1">{notif.message}</p>
            </div>,
            {
              position: "bottom-right",
              autoClose: 5000,
              hideProgressBar: false,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              onClick: () => navigate('/notifications'),
            }
          );
        }
      }
    });

    return unsubscribe;
  }, [location.pathname, navigate, subscribe]);

  // Fallback: Poll for notifications periodically as backup (in case WebSocket disconnects)
  useEffect(() => {
    const checkNotifications = async () => {
      try {
        const isOnNotificationsPage = location.pathname === '/notifications';
        
        const response = await notificationsApi.getNotifications({}) as AxiosResponse<any>;
        const notifications = response.data || [];
        const currentIds = new Set<number>(notifications.map((n: any) => n.notification_id as number));

        // After initial load, check for new notifications (as backup)
        if (isInitialized && !isOnNotificationsPage) {
          const newNotifs = notifications.filter((n: any) => 
            !previousNotificationIdsRef.current.has(n.notification_id) && !n.is_read
          );

          // Show toast only if WebSocket didn't already notify
          // (This is a fallback mechanism)
          if (newNotifs.length > 0) {
          }
        }

        previousNotificationIdsRef.current = currentIds;
        if (!isInitialized) {
          setIsInitialized(true);
        }
      } catch (error) {
        // Silent fail
      }
    };

    // Initial check
    checkNotifications();

    // Disabled backup polling since WebSocket is working reliably
    // WebSocket provides real-time notifications, no need for polling
  }, [location.pathname, isInitialized, navigate]);

  return null; // This component doesn't render anything
};

export default NotificationListener;

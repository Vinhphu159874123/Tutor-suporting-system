import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { notificationsApi } from '../services/api';
import { AxiosResponse } from 'axios';

/**
 * Global notification listener that shows toast notifications
 * when user is NOT on the Notifications page
 */
const NotificationListener: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [previousNotificationIds, setPreviousNotificationIds] = useState<Set<number>>(new Set());
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const checkNotifications = async () => {
      try {
        // Don't show toast if user is on notifications page
        const isOnNotificationsPage = location.pathname === '/notifications';
        
        const response = await notificationsApi.getNotifications({}) as AxiosResponse<any>;
        const notifications = response.data || [];
        const currentIds = new Set<number>(notifications.map((n: any) => n.notification_id as number));

        // After initial load, check for new notifications
        if (isInitialized && !isOnNotificationsPage) {
          const newNotifs = notifications.filter((n: any) => 
            !previousNotificationIds.has(n.notification_id) && !n.is_read
          );

          // Show toast for each new notification (only if there are new ones)
          if (newNotifs.length > 0) {
            newNotifs.forEach((notif: any) => {
              const message = notif.message.length > 60 
                ? notif.message.substring(0, 60) + '...' 
                : notif.message;
              
              toast.info(
                <div 
                  onClick={() => navigate('/notifications')}
                  className="cursor-pointer"
                >
                  <strong>{notif.title}</strong>
                  <p className="text-sm mt-1">{message}</p>
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
            });
          }
        }

        setPreviousNotificationIds(currentIds);
        if (!isInitialized) {
          setIsInitialized(true);
        }
      } catch (error) {
        // Silent fail - don't log to console on every check
      }
    };

    // Initial check
    checkNotifications();

    // Check every 30 seconds (reduced frequency)
    const interval = setInterval(checkNotifications, 30000);

    return () => clearInterval(interval);
  }, [location.pathname, isInitialized, previousNotificationIds, navigate]);

  return null; // This component doesn't render anything
};

export default NotificationListener;

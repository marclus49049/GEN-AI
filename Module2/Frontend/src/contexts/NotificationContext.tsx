import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from './AuthContext';
import { axiosInstance } from '../api/axiosConfig';

interface Notification {
  id: number;
  user_id: number;
  todo_id?: number;
  actor_id: number;
  action_type: string;
  message: string;
  is_read: boolean;
  delivered_at?: string;
  created_at: string;
  actor_username?: string;
  todo_title?: string;
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  isConnected: boolean;
  markAsRead: (notificationId: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  refreshNotifications: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const { isAuthenticated } = useAuth();
  
  // WebSocket connection for live notifications
  const { isConnected, lastMessage, sendMessage } = useWebSocket(
    process.env.NODE_ENV === 'production' 
      ? 'wss://your-domain.com/ws/notifications'
      : 'ws://localhost:8000/ws/notifications'
  );

  // Fetch notifications from API
  const refreshNotifications = async () => {
    if (!isAuthenticated) {
      setNotifications([]);
      setUnreadCount(0);
      return;
    }

    try {
      const response = await axiosInstance.get('/api/v1/notifications');
      const fetchedNotifications = response.data;
      setNotifications(fetchedNotifications);
      
      // Calculate unread count
      const unread = fetchedNotifications.filter((n: Notification) => !n.is_read).length;
      setUnreadCount(unread);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  // Fetch unread count
  const refreshUnreadCount = async () => {
    if (!isAuthenticated) {
      setUnreadCount(0);
      return;
    }

    try {
      const response = await axiosInstance.get('/api/v1/notifications/unread-count');
      setUnreadCount(response.data.unread_count);
    } catch (error) {
      console.error('Error fetching unread count:', error);
    }
  };

  // Mark notification as read
  const markAsRead = async (notificationId: number) => {
    try {
      // Call API - backend will update DB and send WebSocket message
      await axiosInstance.put(`/api/v1/notifications/${notificationId}/read`);
      // Note: State updates will happen via WebSocket message handler
      
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Mark all notifications as read
  const markAllAsRead = async () => {
    try {
      // Call API - backend will update DB and send WebSocket message
      await axiosInstance.put('/api/v1/notifications/mark-all-read');
      // Note: State updates will happen via WebSocket message handler
      
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  // Handle WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;

    const { type, data } = lastMessage;

    switch (type) {
      case 'connection_ack':
        console.log('Notification WebSocket connected:', data);
        // Refresh notifications when connected
        refreshNotifications();
        break;

      case 'new_notification':
        console.log('New notification received:', data);
        // Add new notification to the beginning of the list
        setNotifications(prev => [data, ...prev]);
        setUnreadCount(prev => prev + 1);
        
        // Optional: Show browser notification if permission granted
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification('New Todo Notification', {
            body: data.message,
            icon: '/favicon.ico'
          });
        }
        break;

      case 'notification_marked_read':
        console.log('Notification marked as read:', data);
        // Update specific notification as read
        setNotifications(prev => 
          prev.map(n => 
            n.id === data.notification_id ? { ...n, is_read: true } : n
          )
        );
        // Decrease unread count
        setUnreadCount(prev => Math.max(0, prev - 1));
        break;

      case 'notifications_all_marked_read':
        console.log('All notifications marked as read:', data);
        // Mark all notifications as read
        setNotifications(prev => 
          prev.map(n => ({ ...n, is_read: true }))
        );
        // Set unread count to 0
        setUnreadCount(0);
        break;

      case 'mark_read_ack':
        console.log('Mark read acknowledged:', data);
        break;

      case 'pong':
        // Handle ping-pong for connection health
        break;

      default:
        console.log('Unknown WebSocket message type:', type);
    }
  }, [lastMessage]);

  // Initial load of notifications when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      refreshNotifications();
    } else {
      setNotifications([]);
      setUnreadCount(0);
    }
  }, [isAuthenticated]);

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  // Send periodic ping to keep connection alive
  useEffect(() => {
    if (isConnected) {
      const pingInterval = setInterval(() => {
        sendMessage({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
      }, 30000); // Ping every 30 seconds

      return () => clearInterval(pingInterval);
    }
  }, [isConnected, sendMessage]);

  const value: NotificationContextType = {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    markAllAsRead,
    refreshNotifications,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};
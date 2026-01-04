import { useEffect, useState, useCallback } from 'react';
import { getWebSocketClient } from '@/lib/websocket';
import type { Notification } from '@/lib/websocket';

interface UseNotificationsOptions {
  onNotification?: (notification: Notification) => void;
  autoConnect?: boolean;
}

export function useNotifications(options: UseNotificationsOptions = {}) {
  const { onNotification, autoConnect = true } = options;
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch initial notifications
  const fetchNotifications = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/notifications?limit=50`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (res.ok) {
        const data = await res.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
      setError('Failed to load notifications');
    }
  }, []);

  // Connect WebSocket and fetch initial notifications
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token || !autoConnect) return;

    // Fetch initial notifications
    fetchNotifications();

    // Connect to WebSocket
    const ws = getWebSocketClient();
    ws.connect(token)
      .then(() => {
        setIsConnected(true);
        setError(null);
      })
      .catch(err => {
        console.warn('WebSocket connection failed, using polling:', err);
        setIsConnected(false);
        // Fall back to polling
        const interval = setInterval(fetchNotifications, 30000); // Poll every 30s
        return () => clearInterval(interval);
      });

    // Subscribe to real-time notifications
    const unsubscribe = ws.subscribe((notification: Notification) => {
      setNotifications(prev => [notification, ...prev]);
      setUnreadCount(prev => prev + 1);

      if (onNotification) {
        onNotification(notification);
      }
    });

    return () => {
      unsubscribe();
    };
  }, [autoConnect, fetchNotifications, onNotification]);

  // Mark notification as read
  const markAsRead = useCallback(async (notificationId: number) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/notifications/${notificationId}/mark-read`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (res.ok) {
        setNotifications(prev =>
          prev.map(n =>
            n.id === notificationId ? { ...n, is_read: true } : n
          )
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  }, []);

  // Mark all as read
  const markAllAsRead = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/notifications/mark-all-read`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (res.ok) {
        setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
        setUnreadCount(0);
      }
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    }
  }, []);

  // Delete notification
  const deleteNotification = useCallback(async (notificationId: number) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/notifications/${notificationId}`,
        {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (res.ok) {
        setNotifications(prev => prev.filter(n => n.id !== notificationId));
      }
    } catch (err) {
      console.error('Failed to delete notification:', err);
    }
  }, []);

  // Request notification permission
  const requestPermission = useCallback(async () => {
    if (!('Notification' in window)) {
      console.log('Notifications not supported');
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission === 'denied') {
      console.log('Notification permission denied');
      return false;
    }

    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }, []);

  return {
    notifications,
    unreadCount,
    isConnected,
    error,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    requestPermission,
    refetch: fetchNotifications,
  };
}

export default useNotifications;

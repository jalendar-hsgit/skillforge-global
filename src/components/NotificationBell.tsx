import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { apiCall } from '@/lib/api';

export interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  action_url: string | null;
  created_at: string;
  related_type: string | null;
  related_id: number | null;
}

interface NotificationBellProps {
  className?: string;
}

export const NotificationBell: React.FC<NotificationBellProps> = ({ className = '' }) => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch unread count on mount
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const stats = await apiCall('/api/v1x/notifications/stats', { method: 'GET' });
        setUnreadCount(stats.unread_count || 0);
      } catch (err) {
        console.error('Failed to fetch notification stats:', err);
      }
    };

    fetchStats();
    // Poll every 10 seconds
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch notifications when dropdown opens
  useEffect(() => {
    if (isOpen && notifications.length === 0) {
      const fetchNotifications = async () => {
        try {
          setLoading(true);
          const data = await apiCall('/api/v1x/notifications?limit=10', { method: 'GET' });
          setNotifications(data.notifications || []);
        } catch (err) {
          console.error('Failed to fetch notifications:', err);
        } finally {
          setLoading(false);
        }
      };

      fetchNotifications();
    }
  }, [isOpen]);

  const handleMarkAllRead = async () => {
    try {
      await apiCall('/api/v1x/notifications/mark-all-read', { method: 'POST' });
      setUnreadCount(0);
      setNotifications(notifications.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };

  const handleMarkRead = async (notificationId: number) => {
    try {
      await apiCall(`/api/v1x/notifications/${notificationId}/mark-read`, { method: 'POST' });
      setUnreadCount(Math.max(0, unreadCount - 1));
      setNotifications(
        notifications.map((n) => (n.id === notificationId ? { ...n, is_read: true } : n))
      );
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'achievement_unlocked':
        return '🏆';
      case 'challenge_solved':
        return '✅';
      case 'contest_update':
        return '🎯';
      case 'friend_activity':
        return '👥';
      case 'mention':
        return '🎯';
      case 'comment_reply':
        return '💬';
      default:
        return '📢';
    }
  };

  return (
    <div className="relative">
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`relative p-2 rounded-lg hover:bg-gray-100 transition-colors ${className}`}
      >
        <span className="text-2xl">🔔</span>
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-xl z-50">
          {/* Header */}
          <div className="flex justify-between items-center p-4 border-b border-gray-200">
            <h3 className="font-bold text-lg">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="text-sm text-blue-600 hover:underline"
              >
                Mark all as read
              </button>
            )}
          </div>

          {/* Content */}
          <div className="max-h-96 overflow-y-auto">
            {loading && <p className="p-4 text-center text-gray-600">Loading...</p>}

            {!loading && notifications.length === 0 && (
              <p className="p-4 text-center text-gray-600">No notifications yet</p>
            )}

            {!loading &&
              notifications.map((notif) => (
                <div
                  key={notif.id}
                  className={`p-4 border-b border-gray-100 cursor-pointer transition-colors ${
                    notif.is_read ? 'bg-white hover:bg-gray-50' : 'bg-blue-50 hover:bg-blue-100'
                  }`}
                  onClick={() => {
                    if (!notif.is_read) {
                      handleMarkRead(notif.id);
                    }
                    if (notif.action_url) {
                      window.location.href = notif.action_url;
                    }
                  }}
                >
                  <div className="flex gap-3">
                    <span className="text-2xl flex-shrink-0">
                      {getNotificationIcon(notif.notification_type)}
                    </span>
                    <div className="flex-1">
                      <p className="font-semibold text-sm">{notif.title}</p>
                      <p className="text-sm text-gray-600 line-clamp-2">{notif.message}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(notif.created_at).toLocaleString()}
                      </p>
                    </div>
                    {!notif.is_read && (
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-1 flex-shrink-0"></div>
                    )}
                  </div>
                </div>
              ))}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="p-3 border-t border-gray-200 text-center">
              <Link href="/notifications">
                <span className="text-sm text-blue-600 hover:underline cursor-pointer">
                  View all notifications
                </span>
              </Link>
            </div>
          )}
        </div>
      )}

      {/* Close on outside click */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default NotificationBell;

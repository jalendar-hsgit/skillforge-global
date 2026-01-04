import { useState, useRef, useEffect } from 'react';
import { Bell, X, Check, Trash2, AlertCircle, Info, CheckCircle } from 'lucide-react';
import { useNotifications, Notification } from '@/hooks/useNotifications';

interface NotificationCenterProps {
  className?: string;
}

export default function NotificationCenter({ className = '' }: NotificationCenterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    requestPermission,
  } = useNotifications();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />;
      case 'info':
      default:
        return <Info className="w-4 h-4 text-blue-600 dark:text-blue-400" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'error':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      case 'info':
      default:
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
    }
  };

  const timeAgo = (date: string) => {
    const now = new Date();
    const then = new Date(date);
    const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  return (
    <div ref={dropdownRef} className={`relative ${className}`}>
      {/* Bell Icon Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
        title="Notifications"
      >
        <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />

        {/* Unread Badge */}
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}

        {/* Connection Status Indicator */}
        {!isConnected && (
          <div className="absolute bottom-0 right-0 w-2 h-2 bg-yellow-500 rounded-full" title="Reconnecting..."></div>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
          {/* Header */}
          <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Notifications
              {unreadCount > 0 && (
                <span className="ml-2 inline-block px-2 py-1 text-xs font-bold bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300 rounded">
                  {unreadCount} unread
                </span>
              )}
            </h3>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Notifications List */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center">
                <Bell className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600 dark:text-gray-400">No notifications yet</p>
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition cursor-pointer last:border-b-0 ${
                    !notification.is_read ? 'bg-gray-50 dark:bg-gray-700/30' : ''
                  }`}
                >
                  <div className="flex gap-3">
                    {/* Icon */}
                    <div className="flex-shrink-0">
                      {getNotificationIcon(notification.type)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="text-sm font-semibold text-gray-900 dark:text-white">
                            {notification.title}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                            {notification.message}
                          </p>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-1 flex-shrink-0">
                          {!notification.is_read && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                markAsRead(notification.id);
                              }}
                              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                              title="Mark as read"
                            >
                              <Check className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                            </button>
                          )}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteNotification(notification.id);
                            }}
                            className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                          </button>
                        </div>
                      </div>

                      {/* Time */}
                      <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                        {timeAgo(notification.created_at)}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="flex gap-2 p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/30">
              {unreadCount > 0 && (
                <button
                  onClick={() => markAllAsRead()}
                  className="flex-1 text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 py-2 px-3 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition"
                >
                  Mark all as read
                </button>
              )}
              <button
                onClick={() => requestPermission()}
                className="flex-1 text-xs font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 py-2 px-3 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition"
              >
                Enable notifications
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import NotificationItem from '@/components/social/NotificationItem';

interface Notification {
  id: number;
  type: 'mention' | 'reply' | 'follow' | 'like' | 'message';
  actor: {
    id: number;
    name: string;
    avatar?: string;
  };
  action: string;
  target?: string;
  timestamp: string;
  isRead: boolean;
  actionUrl: string;
}

export default function NotificationsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    fetchNotifications();
  }, [isAuthenticated, filter]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(
        `${apiBase}/api/v1x/notifications${filter !== 'all' ? `?type=${filter}` : ''}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!response.ok) throw new Error('Failed to fetch notifications');
      const data = await response.json();
      setNotifications(data.notifications || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading notifications');
      console.error('Notification fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const markAllAsRead = async () => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      await fetch(`${apiBase}/api/v1x/notifications/mark-all-read`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      fetchNotifications();
    } catch (err) {
      console.error('Mark as read error:', err);
    }
  };

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading notifications...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Notifications - SkillForge</title>
        <meta name="description" content="Your notifications and activity updates" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
        <div className="max-w-2xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                🔔 Notifications
              </h1>
              {unreadCount > 0 && (
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                  {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
                </p>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
              >
                Mark all as read
              </button>
            )}
          </div>

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-8">
              {error}
            </div>
          )}

          {/* Filter Tabs */}
          <div className="mb-8 flex gap-2 overflow-x-auto pb-2">
            {[
              { id: 'all', label: '📋 All' },
              { id: 'mention', label: '👤 Mentions' },
              { id: 'reply', label: '💬 Replies' },
              { id: 'follow', label: '➕ Follows' },
              { id: 'like', label: '❤️ Likes' },
              { id: 'message', label: '📧 Messages' }
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setFilter(f.id)}
                className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
                  filter === f.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:border-blue-600'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Notifications List */}
          {notifications.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-5xl mb-4">🎉</div>
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                {filter === 'all'
                  ? 'All caught up! No new notifications'
                  : `No ${filter} notifications`}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {notifications.map((notification) => (
                <NotificationItem
                  key={notification.id}
                  id={notification.id}
                  type={notification.type}
                  actor={notification.actor}
                  action={notification.action}
                  target={notification.target}
                  timestamp={notification.timestamp}
                  isRead={notification.isRead}
                  actionUrl={notification.actionUrl}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

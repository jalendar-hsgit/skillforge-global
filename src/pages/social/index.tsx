import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import type { GetServerSideProps } from 'next';
import Layout from '@/components/Layout';
import { PageHeader, PageContainer, LoadingState } from '@/components/PageLayout';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import { requireAuthSSR } from '@/lib/auth';

interface SocialStats {
  followers: number;
  following: number;
  posts: number;
  likes: number;
  achievements: number;
}

interface RecentActivity {
  id: number;
  type: string;
  title: string;
  timestamp: string;
}

interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  actor?: {
    id: number;
    username: string;
  };
}

export const getServerSideProps: GetServerSideProps = requireAuthSSR();

export default function SocialIndexPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [stats, setStats] = useState<SocialStats | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    fetchData();
  }, [isAuthenticated]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      // Fetch notifications
      const notifResponse = await fetch(`${apiBase}/api/v1x/users/me/notifications?limit=5`, { headers });
      if (notifResponse.ok) {
        const data = await notifResponse.json();
        setNotifications(data.notifications || []);
      }

      // Set mock stats for now
      setStats({
        followers: 24,
        following: 18,
        posts: 12,
        likes: 156,
        achievements: 8,
      });
    } catch (err) {
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');
      
      await fetch(`${apiBase}/api/v1x/users/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      setNotifications(notifications.map(n => 
        n.id === notificationId ? { ...n, is_read: true } : n
      ));
    } catch (err) {
      console.error('Mark as read error:', err);
    }
  };

  const quickLinks = [
    { href: '/social/feed', label: 'Activity Feed', icon: '📰', desc: 'See latest updates' },
    { href: '/social/following', label: 'Connections', icon: '👥', desc: 'Manage followers' },
    { href: '/leaderboard', label: 'Leaderboard', icon: '🏆', desc: 'Top performers' },
    { href: '/achievements', label: 'Achievements', icon: '🎖️', desc: 'Your badges' },
  ];

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
          <LoadingState message="Loading social dashboard..." />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <Head>
        <title>Social - SkillForge</title>
        <meta name="description" content="Your social hub on SkillForge" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <PageHeader
            title="Social Hub"
            subtitle="Connect, share, and grow with the community"
            icon="🌐"
          />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-8">
              {/* Quick Stats */}
              {stats && (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <PageContainer variant="glass" className="text-center">
                    <div className="text-3xl font-bold text-white">{stats.following}</div>
                    <div className="text-sm text-white/60">Following</div>
                  </PageContainer>
                  <PageContainer variant="glass" className="text-center">
                    <div className="text-3xl font-bold text-white">{stats.followers}</div>
                    <div className="text-sm text-white/60">Followers</div>
                  </PageContainer>
                  <PageContainer variant="glass" className="text-center">
                    <div className="text-3xl font-bold text-blue-400">{stats.posts}</div>
                    <div className="text-sm text-white/60">Posts</div>
                  </PageContainer>
                  <PageContainer variant="glass" className="text-center">
                    <div className="text-3xl font-bold text-red-400">{stats.likes}</div>
                    <div className="text-sm text-white/60">Likes</div>
                  </PageContainer>
                  <PageContainer variant="glass" className="text-center">
                    <div className="text-3xl font-bold text-yellow-400">{stats.achievements}</div>
                    <div className="text-sm text-white/60">Badges</div>
                  </PageContainer>
                </div>
              )}

              {/* Quick Links */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {quickLinks.map((link) => (
                  <Link key={link.href} href={link.href} className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-xl p-5 border border-white/10 transition-all hover:border-purple-500/30 hover:shadow-lg hover:scale-105 group">
                      <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">{link.icon}</div>
                      <h3 className="font-bold text-white mb-1">{link.label}</h3>
                      <p className="text-sm text-white/50">{link.desc}</p>
                  </Link>
                ))}
              </div>

              {/* Create Post CTA */}
              <PageContainer variant="glass">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-xl font-bold shadow-lg">
                    {user?.full_name?.[0]?.toUpperCase() || 'U'}
                  </div>
                  <Link href="/social/feed" className="flex-1 px-4 py-3 bg-white/10 text-white/40 rounded-xl border border-white/10 hover:bg-white/20 hover:text-white/60 transition cursor-pointer">
                      What's on your mind? Share your learning journey...
                  </Link>
                  <Link href="/social/feed" className="px-5 py-3 bg-gradient-to-r from-forgePurple to-neuralBlue text-white rounded-xl font-semibold hover:opacity-90 transition shadow-lg shadow-purple-500/25">
                      Post
                  </Link>
                </div>
              </PageContainer>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Notifications */}
              <PageContainer variant="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <span>🔔</span> Notifications
                  </h3>
                  {notifications.filter(n => !n.is_read).length > 0 && (
                    <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded-full text-xs font-semibold">
                      {notifications.filter(n => !n.is_read).length} new
                    </span>
                  )}
                </div>
                
                {notifications.length === 0 ? (
                  <p className="text-white/50 text-sm py-4 text-center">
                    No new notifications
                  </p>
                ) : (
                  <div className="space-y-3">
                    {notifications.slice(0, 5).map((notif) => (
                      <div
                        key={notif.id}
                        onClick={() => !notif.is_read && markAsRead(notif.id)}
                        className={`p-3 rounded-lg transition cursor-pointer ${
                          notif.is_read 
                            ? 'bg-white/5' 
                            : 'bg-purple-500/10 border border-purple-500/20 hover:bg-purple-500/20'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-lg">
                            {notif.type === 'FRIEND_ACTIVITY' ? '👥' : 
                             notif.type === 'ACHIEVEMENT' ? '🏆' : 
                             notif.type === 'COMMENT' ? '💬' : '🔔'}
                          </span>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm ${notif.is_read ? 'text-white/70' : 'text-white font-medium'}`}>
                              {notif.title}
                            </p>
                            <p className="text-xs text-white/50 mt-0.5">
                              {formatDate(notif.created_at)}
                            </p>
                          </div>
                          {!notif.is_read && (
                            <span className="w-2 h-2 bg-purple-500 rounded-full flex-shrink-0 mt-1" />
                          )}
                        </div>
                      </div>
                    ))}
                    
                    <Link href="/notifications" className="block text-center text-sm text-purple-400 hover:text-purple-300 py-2 transition">
                        View all notifications →
                    </Link>
                  </div>
                )}
              </PageContainer>

              {/* Suggested Connections */}
              <PageContainer variant="card">
                <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                  <span>🌟</span> People to Follow
                </h3>
                <div className="space-y-3">
                  {[
                    { name: 'Sarah Chen', username: 'sarahc', level: 15 },
                    { name: 'David Kumar', username: 'davidk', level: 12 },
                    { name: 'Emily Rodriguez', username: 'emilyr', level: 18 },
                  ].map((person, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-sm font-bold">
                        {person.name[0]}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white truncate">{person.name}</p>
                        <p className="text-xs text-white/50">Level {person.level}</p>
                      </div>
                      <button className="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white/70 rounded-lg text-sm transition">
                        Follow
                      </button>
                    </div>
                  ))}
                </div>
                <Link href="/social/following" className="block text-center text-sm text-purple-400 hover:text-purple-300 py-2 mt-4 transition">
                    Discover more →
                </Link>
              </PageContainer>

              {/* Trending Topics */}
              <PageContainer variant="card">
                <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                  <span>🔥</span> Trending
                </h3>
                <div className="space-y-2">
                  {['#python', '#webdev', '#machinelearning', '#javascript', '#career'].map((tag) => (
                    <Link key={tag} href={`/forums?tag=${tag.slice(1)}`} className="block px-3 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-white/70 hover:text-white transition">
                        {tag}
                    </Link>
                  ))}
                </div>
              </PageContainer>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import AnalyticsCard from '@/components/admin/AnalyticsCard';

interface DashboardStats {
  users: {
    total: number;
    newThisWeek: number;
    weeklyTrend: number;
    activeToday: number;
  };
  courses: {
    total: number;
    enrollmentsTotal: number;
    completionRate: number;
    avgRating: number;
  };
  revenue: {
    total: number;
    pending: number;
    thisMonth: number;
    monthlyTrend: number;
  };
  engagement: {
    avgSessionDuration: number;
    dailyActiveUsers: number;
    bounceRate: number;
    courseCompletionRate: number;
  };
}

export default function AdminDashboard() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Check if user is admin
    if (user && !['ADMIN', 'SUPERADMIN'].includes(user.role)) {
      router.push('/');
      return;
    }

    if (isAuthenticated && user?.id) {
      fetchDashboardStats();
    }
  }, [isAuthenticated, user?.id, user?.role]);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/admin/analytics/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        if (response.status === 403) {
          router.push('/');
          return;
        }
        throw new Error('Failed to fetch dashboard stats');
      }

      const data = await response.json();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading dashboard');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Admin Dashboard - SkillForge</title>
        <meta name="description" content="SkillForge admin dashboard with analytics" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              📊 Admin Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Platform analytics and management
            </p>
          </div>

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Quick Navigation */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Quick Links</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
              <Link href="/admin/dashboard">
                <button className="w-full px-4 py-3 rounded-lg bg-blue-500 text-white font-semibold hover:bg-blue-600 transition">
                  📊 Dashboard
                </button>
              </Link>
              <Link href="/admin/courses">
                <button className="w-full px-4 py-3 rounded-lg bg-purple-500 text-white font-semibold hover:bg-purple-600 transition">
                  📚 Courses
                </button>
              </Link>
              <Link href="/admin/revenue">
                <button className="w-full px-4 py-3 rounded-lg bg-green-500 text-white font-semibold hover:bg-green-600 transition">
                  💰 Revenue
                </button>
              </Link>
              <Link href="/admin/engagement">
                <button className="w-full px-4 py-3 rounded-lg bg-orange-500 text-white font-semibold hover:bg-orange-600 transition">
                  📈 Engagement
                </button>
              </Link>
              <Link href="/admin/users">
                <button className="w-full px-4 py-3 rounded-lg bg-red-500 text-white font-semibold hover:bg-red-600 transition">
                  👥 Users
                </button>
              </Link>
            </div>
          </div>

          {stats && (
            <>
              {/* User Analytics */}
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  👥 User Analytics
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <AnalyticsCard
                    title="Total Users"
                    value={stats.users.total}
                    icon="👤"
                    color="blue"
                    trend={{
                      direction: 'up',
                      percentage: stats.users.weeklyTrend,
                      period: 'vs last week'
                    }}
                  />
                  <AnalyticsCard
                    title="New Users (Week)"
                    value={stats.users.newThisWeek}
                    icon="✨"
                    color="green"
                  />
                  <AnalyticsCard
                    title="Active Today"
                    value={stats.users.activeToday}
                    icon="🔥"
                    color="yellow"
                  />
                  <AnalyticsCard
                    title="Growth Rate"
                    value={`${stats.users.weeklyTrend}%`}
                    icon="📈"
                    color="purple"
                    subtext="Weekly growth"
                  />
                </div>
              </div>

              {/* Course Analytics */}
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  📚 Course Analytics
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <AnalyticsCard
                    title="Total Courses"
                    value={stats.courses.total}
                    icon="📖"
                    color="blue"
                  />
                  <AnalyticsCard
                    title="Total Enrollments"
                    value={stats.courses.enrollmentsTotal}
                    icon="📝"
                    color="purple"
                  />
                  <AnalyticsCard
                    title="Completion Rate"
                    value={`${stats.courses.completionRate}%`}
                    icon="✅"
                    color="green"
                  />
                  <AnalyticsCard
                    title="Avg Course Rating"
                    value={stats.courses.avgRating.toFixed(1)}
                    icon="⭐"
                    color="yellow"
                    subtext="out of 5"
                  />
                </div>
              </div>

              {/* Revenue Analytics */}
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  💰 Revenue Analytics
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <AnalyticsCard
                    title="Total Revenue"
                    value={`$${stats.revenue.total.toLocaleString()}`}
                    icon="💵"
                    color="green"
                    trend={{
                      direction: 'up',
                      percentage: stats.revenue.monthlyTrend,
                      period: 'vs last month'
                    }}
                  />
                  <AnalyticsCard
                    title="This Month"
                    value={`$${stats.revenue.thisMonth.toLocaleString()}`}
                    icon="📅"
                    color="green"
                  />
                  <AnalyticsCard
                    title="Pending Payouts"
                    value={`$${stats.revenue.pending.toLocaleString()}`}
                    icon="⏳"
                    color="yellow"
                  />
                  <AnalyticsCard
                    title="Growth"
                    value={`${stats.revenue.monthlyTrend}%`}
                    icon="📈"
                    color="green"
                    subtext="Monthly growth"
                  />
                </div>
              </div>

              {/* Engagement Metrics */}
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  📊 Engagement Metrics
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <AnalyticsCard
                    title="Avg Session Duration"
                    value={`${stats.engagement.avgSessionDuration}m`}
                    icon="⏱️"
                    color="blue"
                  />
                  <AnalyticsCard
                    title="Daily Active Users"
                    value={stats.engagement.dailyActiveUsers}
                    icon="👥"
                    color="purple"
                  />
                  <AnalyticsCard
                    title="Bounce Rate"
                    value={`${stats.engagement.bounceRate}%`}
                    icon="🚪"
                    color="red"
                    subtext="Lower is better"
                  />
                  <AnalyticsCard
                    title="Course Completion"
                    value={`${stats.engagement.courseCompletionRate}%`}
                    icon="🎯"
                    color="green"
                  />
                </div>
              </div>

              {/* Admin Actions */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                  🔧 Admin Actions
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button className="px-4 py-3 rounded-lg bg-blue-500 text-white font-semibold hover:bg-blue-600 transition">
                    📋 Review Pending Content
                  </button>
                  <button className="px-4 py-3 rounded-lg bg-yellow-500 text-white font-semibold hover:bg-yellow-600 transition">
                    ⚠️ Manage Reports
                  </button>
                  <button className="px-4 py-3 rounded-lg bg-purple-500 text-white font-semibold hover:bg-purple-600 transition">
                    📧 Send Campaign Email
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}


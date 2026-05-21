import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import AnalyticsCard from '@/components/admin/AnalyticsCard';

interface EngagementMetrics {
  dailyActiveUsers: number;
  weeklyActiveUsers: number;
  monthlyActiveUsers: number;
  averageSessionDuration: number;
  totalSessions: number;
  bounceRate: number;
  courseCompletionRate: number;
  userRetentionRate: number;
  peakHours: Array<{ hour: number; users: number }>;
  engagementTrend: number;
}

export default function EngagementPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [data, setData] = useState<EngagementMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('7d');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (user && !['ADMIN', 'SUPERADMIN'].includes(user.role)) {
      router.push('/');
      return;
    }

    if (isAuthenticated && user?.id) {
      fetchEngagementData();
    }
  }, [isAuthenticated, user?.id, user?.role, timeRange]);

  const fetchEngagementData = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(
        `${apiBase}/api/v1x/admin/analytics/engagement?range=${timeRange}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!response.ok) throw new Error('Failed to fetch engagement data');
      const engagementData = await response.json();
      setData(engagementData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading engagement data');
      console.error('Engagement fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading engagement metrics...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Engagement Metrics - SkillForge Admin</title>
        <meta name="description" content="User engagement and activity metrics" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                📊 Engagement Metrics
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                User activity and interaction analytics
              </p>
            </div>
            <Link href="/admin/dashboard">
              <button className="px-4 py-2 rounded-lg bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600">
                ← Back
              </button>
            </Link>
          </div>

          {/* Time Range Selector */}
          <div className="mb-6 flex gap-2">
            {(['24h', '7d', '30d'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  timeRange === range
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                {range === '24h' && 'Last 24 Hours'}
                {range === '7d' && 'Last 7 Days'}
                {range === '30d' && 'Last 30 Days'}
              </button>
            ))}
          </div>

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {data && (
            <>
              {/* Active Users Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <AnalyticsCard
                  title="Daily Active Users"
                  value={data.dailyActiveUsers.toLocaleString()}
                  icon="👤"
                  color="blue"
                  trend={{
                    direction: 'up',
                    percentage: data.engagementTrend,
                    period: 'vs last period'
                  }}
                />
                <AnalyticsCard
                  title="Weekly Active Users"
                  value={data.weeklyActiveUsers.toLocaleString()}
                  icon="👥"
                  color="purple"
                />
                <AnalyticsCard
                  title="Monthly Active Users"
                  value={data.monthlyActiveUsers.toLocaleString()}
                  icon="🌍"
                  color="green"
                />
              </div>

              {/* Session & Quality Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <AnalyticsCard
                  title="Total Sessions"
                  value={data.totalSessions.toLocaleString()}
                  icon="💬"
                  color="blue"
                  subtext={`Avg: ${data.averageSessionDuration.toFixed(1)} min`}
                />
                <AnalyticsCard
                  title="Avg Session Duration"
                  value={`${data.averageSessionDuration.toFixed(1)}m`}
                  icon="⏱️"
                  color="yellow"
                />
                <AnalyticsCard
                  title="Bounce Rate"
                  value={`${data.bounceRate.toFixed(1)}%`}
                  icon="📉"
                  color="red"
                />
                <AnalyticsCard
                  title="Course Completion"
                  value={`${data.courseCompletionRate.toFixed(1)}%`}
                  icon="✅"
                  color="green"
                />
              </div>

              {/* Retention & Engagement */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                    📊 Retention Rate
                  </h3>
                  <div className="flex items-end justify-between h-32">
                    <div className="text-center flex-1">
                      <div className="text-4xl font-bold text-blue-600 mb-2">
                        {data.userRetentionRate.toFixed(1)}%
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Returning Users</p>
                    </div>
                    <div className="flex-1 h-24 bg-gradient-to-t from-blue-500/30 to-transparent rounded-lg ml-4" />
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                    ⏰ Peak Hours
                  </h3>
                  <div className="space-y-2">
                    {data.peakHours.slice(0, 5).map((peak) => (
                      <div key={peak.hour} className="flex items-center gap-2">
                        <span className="text-sm font-semibold w-12 text-gray-600 dark:text-gray-400">
                          {peak.hour}:00
                        </span>
                        <div className="flex-1 h-6 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500 transition-all duration-300"
                            style={{
                              width: `${Math.min(
                                (peak.users / Math.max(...data.peakHours.map((p) => p.users))) *
                                100,
                                100
                              )}%`
                            }}
                          />
                        </div>
                        <span className="text-sm font-semibold text-gray-900 dark:text-white w-12 text-right">
                          {peak.users}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Engagement Score */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">
                  💡 Engagement Health
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {[
                    {
                      label: 'User Growth',
                      value: data.engagementTrend,
                      icon: '📈',
                      status: data.engagementTrend > 10 ? 'Excellent' : 'Good'
                    },
                    {
                      label: 'Course Engagement',
                      value: data.courseCompletionRate,
                      icon: '📚',
                      status: data.courseCompletionRate > 70 ? 'Strong' : 'Moderate'
                    },
                    {
                      label: 'Session Quality',
                      value: 100 - data.bounceRate,
                      icon: '⭐',
                      status: data.bounceRate < 30 ? 'Good' : 'Fair'
                    },
                    {
                      label: 'Retention Health',
                      value: data.userRetentionRate,
                      icon: '💪',
                      status: data.userRetentionRate > 60 ? 'Strong' : 'Moderate'
                    }
                  ].map((metric) => (
                    <div
                      key={metric.label}
                      className="p-4 rounded-lg bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200 dark:border-blue-800"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-2xl">{metric.icon}</span>
                        <span className="text-xs font-semibold px-2 py-1 rounded-full bg-blue-200 dark:bg-blue-800 text-blue-900 dark:text-blue-100">
                          {metric.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 dark:text-gray-300 font-semibold">
                        {metric.label}
                      </p>
                      <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">
                        {metric.value.toFixed(1)}%
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

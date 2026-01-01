import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import AnalyticsCard from '@/components/admin/AnalyticsCard';

interface RevenueData {
  totalRevenue: number;
  monthlyRevenue: number;
  pendingPayouts: number;
  completedPayouts: number;
  refunds: number;
  bySource: { courses: number; products: number; mentoring: number };
  monthlyTrend: number;
}

export default function RevenueAnalyticsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [data, setData] = useState<RevenueData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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
      fetchRevenueData();
    }
  }, [isAuthenticated, user?.id, user?.role]);

  const fetchRevenueData = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/admin/analytics/revenue`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch revenue data');
      const revenueData = await response.json();
      setData(revenueData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading revenue data');
      console.error('Revenue fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading revenue data...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Revenue Analytics - SkillForge Admin</title>
        <meta name="description" content="Revenue analytics and financial metrics" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                💰 Revenue Analytics
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Financial metrics and payment tracking
              </p>
            </div>
            <Link href="/admin/dashboard">
              <button className="px-4 py-2 rounded-lg bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600">
                ← Back
              </button>
            </Link>
          </div>

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {data && (
            <>
              {/* Main Revenue Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <AnalyticsCard
                  title="Total Revenue"
                  value={`$${data.totalRevenue.toLocaleString()}`}
                  icon="💵"
                  color="green"
                  trend={{
                    direction: 'up',
                    percentage: data.monthlyTrend,
                    period: 'vs last month'
                  }}
                />
                <AnalyticsCard
                  title="This Month"
                  value={`$${data.monthlyRevenue.toLocaleString()}`}
                  icon="📅"
                  color="green"
                />
                <AnalyticsCard
                  title="Pending Payouts"
                  value={`$${data.pendingPayouts.toLocaleString()}`}
                  icon="⏳"
                  color="yellow"
                />
                <AnalyticsCard
                  title="Refunds (Month)"
                  value={`$${data.refunds.toLocaleString()}`}
                  icon="↩️"
                  color="red"
                />
              </div>

              {/* Revenue by Source */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <AnalyticsCard
                  title="Courses Revenue"
                  value={`$${data.bySource.courses.toLocaleString()}`}
                  icon="📚"
                  color="blue"
                  subtext={`${((data.bySource.courses / data.totalRevenue) * 100).toFixed(1)}% of total`}
                />
                <AnalyticsCard
                  title="Products Revenue"
                  value={`$${data.bySource.products.toLocaleString()}`}
                  icon="🛍️"
                  color="purple"
                  subtext={`${((data.bySource.products / data.totalRevenue) * 100).toFixed(1)}% of total`}
                />
                <AnalyticsCard
                  title="Mentoring Revenue"
                  value={`$${data.bySource.mentoring.toLocaleString()}`}
                  icon="👨‍🏫"
                  color="orange"
                  subtext={`${((data.bySource.mentoring / data.totalRevenue) * 100).toFixed(1)}% of total`}
                />
              </div>

              {/* Revenue Distribution Chart */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                  📊 Revenue Distribution
                </h2>
                <div className="space-y-4">
                  {[
                    { label: 'Courses', value: data.bySource.courses, total: data.totalRevenue, color: 'bg-blue-500' },
                    { label: 'Products', value: data.bySource.products, total: data.totalRevenue, color: 'bg-purple-500' },
                    { label: 'Mentoring', value: data.bySource.mentoring, total: data.totalRevenue, color: 'bg-orange-500' }
                  ].map((item) => {
                    const percentage = (item.value / item.total) * 100;
                    return (
                      <div key={item.label}>
                        <div className="flex justify-between mb-2">
                          <span className="font-semibold text-gray-900 dark:text-white">
                            {item.label}
                          </span>
                          <span className="text-gray-600 dark:text-gray-400">
                            ${item.value.toLocaleString()} ({Math.round(percentage)}%)
                          </span>
                        </div>
                        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${item.color}`}
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

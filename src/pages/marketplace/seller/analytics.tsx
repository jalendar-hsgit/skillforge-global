import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { useRouter } from 'next/router';
import { BarChart3, TrendingUp, Activity, DollarSign, Eye, ShoppingCart } from 'lucide-react';
import { useAuthCheck } from '@/lib/protectedRoute';

interface Analytics {
  period: string;
  total_products: number;
  total_sales: number;
  total_revenue: number;
  total_views: number;
  average_product_rating: number;
  sales_by_product: Record<string, number>;
  revenue_trend: Record<string, number>;
  conversion_rate: number;
  average_order_value: number;
}

export default function SellerAnalytics() {
  const router = useRouter();
  const { isAuthorized, loading: authLoading } = useAuthCheck('seller');
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [period, setPeriod] = useState('month');

  useEffect(() => {
    if (!authLoading && isAuthorized) {
      fetchAnalytics();
    }
  }, [period, authLoading, isAuthorized]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);

      const url = new URL(`/api/session/v1x/seller/analytics`);
      url.searchParams.append('period', period);

      const res = await fetch(url.toString(), {
        credentials: 'include',
      });

      if (res.ok) {
        const data = await res.json();
        setAnalytics(data);
        setError('');
      } else if (res.status === 401) {
        router.push('/login');
      } else {
        setError('Failed to load analytics');
      }
    } catch (err) {
      setError('Error fetching analytics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!isAuthorized) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-yellow-800 dark:text-yellow-200">
            You must be a seller to access this page. Please contact support if you need seller access.
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Sales Analytics</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Monitor your sales performance and trends</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg text-red-600 dark:text-red-400">
            {error}
          </div>
        )}

        {/* Period Selector */}
        <div className="mb-6">
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Total Revenue */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Total Revenue</p>
              <DollarSign className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              ${analytics?.total_revenue?.toFixed(2) || '0.00'}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">From all sales</p>
          </div>

          {/* Total Sales */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Total Sales</p>
              <ShoppingCart className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {analytics?.total_sales || 0}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">Products sold</p>
          </div>

          {/* Average Order Value */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Avg Order Value</p>
              <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              ${analytics?.average_order_value?.toFixed(2) || '0.00'}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">Per transaction</p>
          </div>

          {/* Total Views */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Total Views</p>
              <Eye className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {analytics?.total_views || 0}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">Product page visits</p>
          </div>

          {/* Conversion Rate */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Conversion Rate</p>
              <Activity className="w-5 h-5 text-orange-600 dark:text-orange-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {analytics?.conversion_rate?.toFixed(2) || '0'}%
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">Views to sales</p>
          </div>

          {/* Avg Product Rating */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Avg Rating</p>
              <BarChart3 className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {analytics?.average_product_rating?.toFixed(2) || '0'} ⭐
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">Across all products</p>
          </div>
        </div>

        {/* Revenue Trend */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Trend Chart */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Revenue Trend (Last 6 Months)</h2>
            
            {analytics?.revenue_trend && Object.keys(analytics.revenue_trend).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(analytics.revenue_trend).map(([month, revenue]) => {
                  const maxRevenue = Math.max(...Object.values(analytics.revenue_trend as Record<string, number>));
                  const percentage = maxRevenue > 0 ? (revenue / maxRevenue) * 100 : 0;
                  
                  return (
                    <div key={month}>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{month}</span>
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">
                          ${revenue.toFixed(2)}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-400">No revenue data yet</p>
            )}
          </div>

          {/* Sales by Product */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Sales by Product</h2>
            
            {analytics?.sales_by_product && Object.keys(analytics.sales_by_product).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(analytics.sales_by_product)
                  .sort((a, b) => (b[1] as number) - (a[1] as number))
                  .map(([productName, sales]) => (
                    <div key={productName} className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {productName.length > 30 ? productName.substring(0, 30) + '...' : productName}
                        </p>
                      </div>
                      <div className="ml-4 text-right">
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">
                          {sales} {sales === 1 ? 'sale' : 'sales'}
                        </span>
                      </div>
                    </div>
                  ))}
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-400">No sales yet</p>
            )}
          </div>
        </div>

        {/* Stats Summary */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Summary</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border-l-4 border-blue-500 pl-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Products</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics?.total_products || 0}</p>
            </div>
            
            <div className="border-l-4 border-green-500 pl-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Period</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white capitalize">{period}</p>
            </div>
            
            <div className="border-l-4 border-purple-500 pl-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Best Performing</p>
              <p className="text-lg font-bold text-gray-900 dark:text-white">
                {analytics?.sales_by_product 
                  ? Object.entries(analytics.sales_by_product)
                      .sort((a, b) => (b[1] as number) - (a[1] as number))[0]?.[0]?.substring(0, 20) || 'N/A'
                  : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { useRouter } from 'next/router';
import { BarChart3, TrendingUp, Package, DollarSign, ShoppingBag, Star } from 'lucide-react';
import Link from 'next/link';
import { useAuthCheck } from '@/lib/protectedRoute';

interface SellerStats {
  total_revenue: number;
  total_sales: number;
  product_count: number;
  average_rating: number;
  active_products: number;
  pending_orders: number;
}

interface RecentOrder {
  id: number;
  product_name: string;
  buyer_name: string;
  amount: number;
  status: string;
  created_at: string;
}

export default function SellerDashboard() {
  const router = useRouter();
  const { isAuthorized, loading: authLoading } = useAuthCheck('seller');
  const [stats, setStats] = useState<SellerStats | null>(null);
  const [recentOrders, setRecentOrders] = useState<RecentOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authLoading && isAuthorized) {
      fetchSellerStats();
    }
  }, [authLoading, isAuthorized]);

  const fetchSellerStats = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login?redirect=/marketplace/seller');
        return;
      }

      const [statsRes, ordersRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/seller/stats`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/seller/orders?limit=5`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data);
      }

      if (ordersRes.ok) {
        const data = await ordersRes.json();
        setRecentOrders(data.orders || []);
      }
    } catch (err) {
      setError('Failed to load seller dashboard');
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

  if (error) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-800 dark:text-red-200">
            {error}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Seller Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your products and monitor sales</p>
          </div>
          <Link href="/marketplace/seller/products">
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition">
              Add Product
            </button>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {/* Revenue Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Total Revenue</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  ${stats?.total_revenue?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="bg-green-100 dark:bg-green-900/20 p-3 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          {/* Sales Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Total Sales</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{stats?.total_sales || 0}</p>
              </div>
              <div className="bg-blue-100 dark:bg-blue-900/20 p-3 rounded-lg">
                <ShoppingBag className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>

          {/* Products Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Products</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{stats?.product_count || 0}</p>
              </div>
              <div className="bg-purple-100 dark:bg-purple-900/20 p-3 rounded-lg">
                <Package className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </div>

          {/* Rating Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Rating</p>
                <div className="flex items-center mt-2">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.average_rating?.toFixed(1) || '0.0'}</p>
                  <Star className="w-5 h-5 text-yellow-400 ml-2" />
                </div>
              </div>
              <div className="bg-yellow-100 dark:bg-yellow-900/20 p-3 rounded-lg">
                <Star className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Link href="/marketplace/seller/products">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 cursor-pointer transition">
              <Package className="w-8 h-8 text-blue-600 dark:text-blue-400 mb-2" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Manage Products</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Add, edit, or delete products</p>
            </div>
          </Link>

          <Link href="/marketplace/seller/orders">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 hover:border-green-400 dark:hover:border-green-600 cursor-pointer transition">
              <ShoppingBag className="w-8 h-8 text-green-600 dark:text-green-400 mb-2" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">View Orders</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Track and manage orders</p>
            </div>
          </Link>

          <Link href="/marketplace/seller/analytics">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-600 cursor-pointer transition">
              <BarChart3 className="w-8 h-8 text-purple-600 dark:text-purple-400 mb-2" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Analytics</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">View sales analytics</p>
            </div>
          </Link>
        </div>

        {/* Recent Orders */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Recent Orders</h2>
          </div>
          
          {recentOrders.length === 0 ? (
            <div className="p-6 text-center text-gray-600 dark:text-gray-400">
              No orders yet. When customers buy your products, they'll appear here.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Product</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Buyer</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {recentOrders.map((order) => (
                    <tr key={order.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <td className="px-6 py-3 text-sm text-gray-900 dark:text-white">{order.product_name}</td>
                      <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-400">{order.buyer_name}</td>
                      <td className="px-6 py-3 text-sm font-semibold text-gray-900 dark:text-white">${order.amount.toFixed(2)}</td>
                      <td className="px-6 py-3">
                        <span className={`text-xs font-semibold px-3 py-1 rounded-full ${
                          order.status === 'completed' ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300' :
                          order.status === 'pending' ? 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300' :
                          'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                        }`}>
                          {order.status}
                        </span>
                      </td>
                      <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-400">
                        {new Date(order.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {recentOrders.length > 0 && (
            <div className="p-4 text-center border-t border-gray-200 dark:border-gray-700">
              <Link href="/marketplace/seller/orders" className="text-blue-600 dark:text-blue-400 hover:underline text-sm font-medium">
                View all orders
              </Link>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

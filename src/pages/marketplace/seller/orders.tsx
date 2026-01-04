import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { useRouter } from 'next/router';
import { Search, Filter, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { useAuthCheck } from '@/lib/protectedRoute';

interface Order {
  id: number;
  product_name: string;
  buyer_name: string;
  buyer_email: string;
  amount: number;
  status: string;
  payment_method: string;
  created_at: string;
  quantity: number;
}

export default function SellerOrders() {
  const router = useRouter();
  const { isAuthorized, loading: authLoading } = useAuthCheck('seller');
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    if (!authLoading && isAuthorized) {
      fetchOrders();
    }
  }, [filterStatus, authLoading, isAuthorized]);

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login?redirect=/marketplace/seller/orders');
        return;
      }

      const url = new URL(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/seller/orders`);
      if (filterStatus !== 'all') {
        url.searchParams.append('status', filterStatus);
      }

      const res = await fetch(url.toString(), {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const data = await res.json();
        setOrders(data.orders || []);
      } else if (res.status === 401) {
        router.push('/login');
      }
    } catch (err) {
      setError('Failed to load orders');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredOrders = orders.filter(o =>
    o.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.buyer_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.buyer_email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300';
      case 'pending':
        return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300';
      case 'failed':
        return 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300';
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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Orders</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Track and manage customer orders</p>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-800 dark:text-red-200 mb-6">
            {error}
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Total Orders</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{orders.length}</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Completed</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">
              {orders.filter(o => o.status === 'completed').length}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <p className="text-gray-600 dark:text-gray-400 text-sm">Pending</p>
            <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">
              {orders.filter(o => o.status === 'pending').length}
            </p>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by product, buyer, or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
          >
            <option value="all">All Status</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        {/* Orders Table */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          {filteredOrders.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-600 dark:text-gray-400">
                {searchQuery ? 'No orders found.' : 'No orders yet. When customers purchase, they will appear here.'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Order ID</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Product</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Buyer</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredOrders.map((order) => (
                    <tr key={order.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition">
                      <td className="px-6 py-4">
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">#{order.id}</span>
                      </td>
                      <td className="px-6 py-4">
                        <p className="font-medium text-gray-900 dark:text-white">{order.product_name}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Qty: {order.quantity}</p>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{order.buyer_name}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{order.buyer_email}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="font-semibold text-gray-900 dark:text-white">${order.amount.toFixed(2)}</span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(order.status)}
                          <span className={`text-xs font-semibold px-3 py-1 rounded-full ${getStatusColor(order.status)}`}>
                            {order.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {new Date(order.created_at).toLocaleDateString()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

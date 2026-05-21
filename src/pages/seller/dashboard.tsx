/**
 * Seller Dashboard Component
 * Main dashboard for sellers to view metrics, orders, and analytics
 */

import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const SellerDashboard = () => {
  const [dashboard, setDashboard] = useState(null);
  const [orders, setOrders] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');

      // Fetch dashboard metrics
      const dashResponse = await fetch('/api/v1x/seller/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const dashData = await dashResponse.json();
      setDashboard(dashData);

      // Fetch orders
      const ordersResponse = await fetch('/api/v1x/seller/orders', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const ordersData = await ordersResponse.json();
      setOrders(ordersData.orders);

      // Fetch analytics
      const analyticsResponse = await fetch('/api/v1x/seller/analytics/timeline?days=30', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const analyticsData = await analyticsResponse.json();
      setAnalytics(analyticsData);

      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 m-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Seller Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage your products, sales, and analytics</p>
        </div>

        {/* Key Metrics */}
        {dashboard && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <MetricCard
              title="Total Sales"
              value={dashboard.total_sales}
              icon="📊"
            />
            <MetricCard
              title="Total Revenue"
              value={`$${dashboard.total_revenue.toFixed(2)}`}
              icon="💰"
            />
            <MetricCard
              title="Average Rating"
              value={dashboard.average_rating.toFixed(1)}
              suffix="⭐"
              icon="⭐"
            />
            <MetricCard
              title="Total Products"
              value={dashboard.total_products}
              icon="📦"
            />
          </div>
        )}

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Revenue Timeline */}
          {analytics && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Revenue Trend (30 Days)</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={Array.isArray(analytics.timeline) ? analytics.timeline : []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="revenue"
                    stroke="#3b82f6"
                    name="Revenue"
                  />
                </LineChart>
              </ResponsiveContainer>
              <p className="text-sm text-gray-600 mt-4">
                Total: ${analytics.total_period_revenue?.toFixed(2) || 0}
              </p>
            </div>
          )}

          {/* Top Products */}
          {dashboard && dashboard.top_products && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Top Products</h2>
              <div className="space-y-4">
                {dashboard.top_products.map((product, idx) => (
                  <div key={idx} className="border-b pb-3 last:border-b-0">
                    <h3 className="font-semibold text-gray-800">{product.name}</h3>
                    <div className="grid grid-cols-3 gap-4 mt-2 text-sm">
                      <div>
                        <p className="text-gray-500">Sales</p>
                        <p className="font-bold text-gray-900">{product.sales_count}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Revenue</p>
                        <p className="font-bold text-gray-900">${product.total_revenue?.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Rating</p>
                        <p className="font-bold text-gray-900">{product.average_rating?.toFixed(1)}⭐</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Recent Orders */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Orders</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4 text-gray-600">Order #</th>
                  <th className="text-left py-2 px-4 text-gray-600">Amount</th>
                  <th className="text-left py-2 px-4 text-gray-600">Status</th>
                  <th className="text-left py-2 px-4 text-gray-600">Date</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-mono text-blue-600">{order.order_number}</td>
                    <td className="py-3 px-4 font-semibold text-gray-900">${order.amount?.toFixed(2)}</td>
                    <td className="py-3 px-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        order.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : order.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {order.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-600">
                      {new Date(order.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex gap-4">
          <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            View All Orders
          </button>
          <button className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700">
            Request Payout
          </button>
          <button className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700">
            Refresh Data
          </button>
        </div>
      </div>
    </div>
  );
};

// Metric Card Component
const MetricCard = ({ title, value, suffix, icon }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-600 text-sm font-medium">{title}</p>
        <p className="text-2xl font-bold text-gray-900 mt-2">
          {value}{suffix}
        </p>
      </div>
      <div className="text-4xl">{icon}</div>
    </div>
  </div>
);

export default SellerDashboard;

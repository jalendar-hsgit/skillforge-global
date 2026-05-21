/**
 * Order Details & Tracking Page
 * Display order details, payment status, and refund options
 */

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

interface OrderDetails {
  order_id: string;
  order_number: string;
  user_id: number;
  course_id: number | null;
  product_ids: number[];
  amount: number;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  payment_status: string;
  payment_id: string;
  paid_at: string | null;
  created_at: string;
  updated_at: string;
  payment_method: string;
}

interface PaymentStatus {
  payment_id: string;
  status: string;
  amount: number;
  provider: string;
  paid_at: string | null;
}

const OrderDetailsPage = () => {
  const router = useRouter();
  const { id } = router.query;
  const [order, setOrder] = useState<OrderDetails | null>(null);
  const [payment, setPayment] = useState<PaymentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refunding, setRefunding] = useState(false);
  const [refundReason, setRefundReason] = useState('');
  const [refundAmount, setRefundAmount] = useState(0);

  useEffect(() => {
    if (!id) return;

    const fetchOrder = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          router.push('/login');
          return;
        }

        // Fetch order details
        const orderRes = await fetch(`/api/v1x/orders/${id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!orderRes.ok) {
          throw new Error('Failed to fetch order');
        }

        const orderData = await orderRes.json();
        setOrder(orderData);

        // Fetch payment status
        const paymentRes = await fetch(`/api/v1x/payments/status/${id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (paymentRes.ok) {
          const paymentData = await paymentRes.json();
          setPayment(paymentData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load order');
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [id, router]);

  const handleRefund = async (e: React.FormEvent) => {
    e.preventDefault();
    setRefunding(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1x/payments/refund', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          order_id: id,
          amount: refundAmount || null,
          reason: refundReason
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Refund failed');
      }

      // Refresh order status
      const orderRes = await fetch(`/api/v1x/orders/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const updatedOrder = await orderRes.json();
      setOrder(updatedOrder);

      setRefundReason('');
      setRefundAmount(0);
      alert('Refund processed successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Refund failed');
    } finally {
      setRefunding(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading order details...</p>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h1 className="text-xl font-bold text-red-800 mb-2">Error</h1>
            <p className="text-red-700">{error || 'Order not found'}</p>
            <button
              onClick={() => router.push('/marketplace')}
              className="mt-4 bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700"
            >
              Back to Marketplace
            </button>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'pending': return 'yellow';
      case 'failed': return 'red';
      case 'refunded': return 'gray';
      default: return 'blue';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'pending': return '⏳';
      case 'failed': return '❌';
      case 'refunded': return '↩️';
      default: return '📦';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Order Details</h1>
          <p className="text-gray-600">Order ID: {order.order_number}</p>
        </div>

        {/* Status Card */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Order Status</h2>
              <div className="flex items-center gap-3">
                <span className="text-3xl">{getStatusIcon(order.status)}</span>
                <div>
                  <p className="text-2xl font-bold capitalize" style={{
                    color: getStatusColor(order.status) === 'green' ? '#16A34A' : 
                           getStatusColor(order.status) === 'yellow' ? '#EAB308' :
                           getStatusColor(order.status) === 'red' ? '#DC2626' :
                           getStatusColor(order.status) === 'gray' ? '#6B7280' : '#3B82F6'
                  }}>
                    {order.status}
                  </p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="text-gray-600 text-sm mb-2">Total Amount</p>
              <p className="text-3xl font-bold text-blue-600">${order.amount.toFixed(2)}</p>
            </div>
          </div>

          {/* Order Timeline */}
          <div className="space-y-4 mt-6 border-t pt-6">
            <div className="flex gap-4">
              <div className="text-center">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">✓</div>
              </div>
              <div>
                <p className="font-semibold text-gray-900">Order Placed</p>
                <p className="text-sm text-gray-600">{new Date(order.created_at).toLocaleDateString()}</p>
              </div>
            </div>

            {order.status === 'completed' && payment?.paid_at && (
              <div className="flex gap-4">
                <div className="text-center">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-bold">✓</div>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Payment Completed</p>
                  <p className="text-sm text-gray-600">{new Date(payment.paid_at).toLocaleDateString()}</p>
                  <p className="text-xs text-gray-500 mt-1">via {payment.provider}</p>
                </div>
              </div>
            )}

            {order.status === 'refunded' && (
              <div className="flex gap-4">
                <div className="text-center">
                  <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 font-bold">↩️</div>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Refunded</p>
                  <p className="text-sm text-gray-600">{new Date(order.updated_at).toLocaleDateString()}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Payment Information */}
        {payment && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Payment ID</p>
                <p className="font-mono text-sm text-gray-900">{payment.payment_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Provider</p>
                <p className="capitalize font-semibold text-gray-900">{payment.provider}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Amount</p>
                <p className="font-bold text-gray-900">${payment.amount.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="capitalize font-semibold text-gray-900">{payment.status}</p>
              </div>
            </div>
          </div>
        )}

        {/* Refund Section - Only show if completed */}
        {order.status === 'completed' && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Request Refund</h2>
            <p className="text-gray-600 text-sm mb-4">
              You can request a refund within 30 days of purchase.
            </p>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleRefund}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Refund Reason
                  </label>
                  <select
                    value={refundReason}
                    onChange={(e) => setRefundReason(e.target.value)}
                    disabled={refunding}
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Select a reason...</option>
                    <option value="not_satisfied">Not satisfied with product</option>
                    <option value="duplicate">Duplicate purchase</option>
                    <option value="changed_mind">Changed my mind</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Refund Amount (Optional)
                  </label>
                  <div className="flex gap-2">
                    <span className="px-4 py-2 bg-gray-100 rounded-lg text-gray-600">$</span>
                    <input
                      type="number"
                      min="0"
                      max={order.amount}
                      step="0.01"
                      value={refundAmount || ''}
                      onChange={(e) => setRefundAmount(e.target.value ? parseFloat(e.target.value) : 0)}
                      disabled={refunding}
                      placeholder="Leave blank for full refund"
                      className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Full refund amount: ${order.amount.toFixed(2)}</p>
                </div>

                <button
                  type="submit"
                  disabled={refunding || !refundReason}
                  className={`w-full py-2 px-4 rounded-lg font-semibold text-white ${
                    refunding || !refundReason
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-orange-600 hover:bg-orange-700'
                  }`}
                >
                  {refunding ? 'Processing Refund...' : 'Request Refund'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Order Summary */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Order Summary</h2>
          <div className="space-y-3 border-b pb-4 mb-4">
            <div className="flex justify-between">
              <span className="text-gray-600">Order Number</span>
              <span className="font-mono font-semibold">{order.order_number}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Payment Method</span>
              <span className="capitalize">{order.payment_method}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Created</span>
              <span>{new Date(order.created_at).toLocaleDateString()}</span>
            </div>
          </div>
          <div className="flex justify-between">
            <span className="font-bold text-gray-900">Total</span>
            <span className="text-xl font-bold text-blue-600">${order.amount.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetailsPage;

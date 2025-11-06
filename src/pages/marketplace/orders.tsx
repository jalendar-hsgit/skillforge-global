import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/Button';
import { Package, CheckCircle, XCircle, Clock, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { API_BASE } from '@/lib/apiBase';

interface Order {
  id: number;
  order_number: string;
  status: string;
  subtotal: number;
  discount_amount: number;
  tax_amount: number;
  amount: number;
  currency: string;
  payment_method: string | null;
  payment_status: string | null;
  created_at: string;
  course_title: string | null;
}

export default function OrdersPage() {
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/session/v1x/marketplace/orders`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setOrders(data);
      } else if (response.status === 401) {
        router.push('/login?redirect=/marketplace/orders');
      }
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <Package className="w-5 h-5 text-techGray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-500 border-green-500/50';
      case 'failed':
        return 'bg-red-500/20 text-red-500 border-red-500/50';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/50';
      default:
        return 'bg-techGray-500/20 text-techGray-500 border-techGray-500/50';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-deepTech flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-forgePurple border-t-transparent mb-4"></div>
            <p className="text-techGray-400">Loading your orders...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech py-12">
        <div className="container">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <Link href="/marketplace">
                <Button variant="ghost" size="sm" className="mb-4">
                  <ArrowLeft className="w-5 h-5 mr-2" />
                  Back to Marketplace
                </Button>
              </Link>
              <h1 className="text-4xl font-display font-black text-white mb-2">My Orders</h1>
              <p className="text-techGray-400">View your purchase history and order status</p>
            </div>
            <Link href="/marketplace">
              <Button>Browse More Courses</Button>
            </Link>
          </div>

          {/* Orders List */}
          <div className="space-y-4">
            {orders.length === 0 ? (
              <div className="bg-deepTech-800 rounded-2xl p-12 text-center shadow-glow border border-techGray-800">
                <Package className="w-16 h-16 text-techGray-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">No orders yet</h3>
                <p className="text-techGray-400 mb-6">Start learning by purchasing your first course!</p>
                <Link href="/marketplace">
                  <Button>Browse Courses</Button>
                </Link>
              </div>
            ) : (
              orders.map(order => (
                <div
                  key={order.id}
                  className="bg-deepTech-800 rounded-2xl p-6 shadow-lg border border-techGray-800 hover:border-forgePurple transition-all animate-slide-up"
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                    {/* Order Info */}
                    <div className="flex-1">
                      <div className="flex items-start gap-4 mb-4">
                        <div className="p-3 bg-forgePurple/10 rounded-xl">
                          {getStatusIcon(order.status)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-bold text-white">
                              Order #{order.order_number}
                            </h3>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getStatusColor(order.status)}`}>
                              {order.status.toUpperCase()}
                            </span>
                          </div>
                          
                          <p className="text-techGray-400 text-sm mb-1">
                            {order.course_title || 'Course'}
                          </p>
                          
                          <p className="text-techGray-500 text-xs">
                            Ordered on {new Date(order.created_at).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>
                      </div>

                      {/* Price Breakdown */}
                      <div className="bg-deepTech-900 rounded-xl p-4 space-y-2">
                        <div className="flex justify-between text-sm text-techGray-300">
                          <span>Subtotal</span>
                          <span>${order.subtotal.toFixed(2)}</span>
                        </div>
                        {order.discount_amount > 0 && (
                          <div className="flex justify-between text-sm text-green-500">
                            <span>Discount</span>
                            <span>-${order.discount_amount.toFixed(2)}</span>
                          </div>
                        )}
                        {order.tax_amount > 0 && (
                          <div className="flex justify-between text-sm text-techGray-300">
                            <span>Tax</span>
                            <span>${order.tax_amount.toFixed(2)}</span>
                          </div>
                        )}
                        <div className="flex justify-between pt-2 border-t border-techGray-700">
                          <span className="font-bold text-white">Total</span>
                          <span className="text-xl font-black text-forgePurple">
                            ${order.amount.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col gap-3 lg:w-48">
                      {order.status === 'completed' && order.course_title && (
                        <Link href="/dashboard">
                          <Button className="w-full bg-gradient-to-r from-forgePurple to-neuralBlue">
                            Start Learning
                          </Button>
                        </Link>
                      )}
                      
                      {order.payment_method && (
                        <div className="text-center p-3 bg-deepTech-900 rounded-lg border border-techGray-700">
                          <p className="text-xs text-techGray-500 mb-1">Payment Method</p>
                          <p className="text-sm font-semibold text-white capitalize">
                            {order.payment_method}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}

// Enable SSR to avoid static export issues with authenticated endpoints
export async function getServerSideProps() {
  return { props: {} };
}

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { getMyOrders, getOrderDetails } from '@/lib/orderApi';
import styles from '@/styles/orders.module.css';

interface Order {
  id: number;
  order_number: string;
  course_id: number;
  amount: number;
  currency: string;
  status: string;
  payment_status: string;
  created_at: string;
  paid_at?: string;
}

interface OrdersResponse {
  success: boolean;
  data: {
    orders: Order[];
    total: number;
    page: number;
    page_size: number;
  };
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const response: OrdersResponse = await getMyOrders(1, 20);
      if (response.success) {
        setOrders(response.data.orders || []);
        setError('');
      } else {
        setError('Failed to load orders');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load orders';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'pending':
        return 'pending';
      case 'failed':
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>My Orders - SkillForge Global</title>
      </Head>

      <div className={styles.pageContent}>
        <div className={styles.header}>
          <h1>My Orders</h1>
          <Link href="/checkout">
            <button className={styles.buyButton}>Buy More Courses</button>
          </Link>
        </div>

        {error && <div className={styles.errorMessage}>{error}</div>}

        {loading ? (
          <div className={styles.loading}>Loading your orders...</div>
        ) : orders.length === 0 ? (
          <div className={styles.emptyState}>
            <h2>No Orders Yet</h2>
            <p>You haven't purchased any courses yet.</p>
            <Link href="/checkout">
              <button className={styles.primaryButton}>Browse Courses</button>
            </Link>
          </div>
        ) : (
          <div className={styles.ordersTable}>
            <table>
              <thead>
                <tr>
                  <th>Order Number</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Payment Status</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id}>
                    <td className={styles.orderNumber}>{order.order_number}</td>
                    <td className={styles.amount}>
                      ${order.amount?.toFixed(2) || '0.00'} {order.currency?.toUpperCase()}
                    </td>
                    <td>
                      <span className={`${styles.status} ${styles[getStatusColor(order.status)]}`}>
                        {order.status}
                      </span>
                    </td>
                    <td>
                      <span className={`${styles.status} ${styles[getStatusColor(order.payment_status)]}`}>
                        {order.payment_status}
                      </span>
                    </td>
                    <td>{new Date(order.created_at).toLocaleDateString()}</td>
                    <td>
                      <Link href={`/orders/${order.id}`}>
                        <button className={styles.viewButton}>View</button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

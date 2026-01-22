/**
 * Checkout Page
 * Complete checkout flow with payment processing
 */

import React, { useEffect, useState } from 'react';
import Layout from '@/components/Layout'
import { API_BASE } from '@/lib/apiBase';

const CheckoutPage = () => {
  const [cartItems, setCartItems] = useState([]);
  const [couponCode, setCouponCode] = useState('');
  const [subtotal, setSubtotal] = useState(0);
  const [discount, setDiscount] = useState(0);
  const [total, setTotal] = useState(0);
  const [paymentMethod, setPaymentMethod] = useState('stripe');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [orderNumber, setOrderNumber] = useState('');

  useEffect(() => {
    // Load cart from localStorage
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    setCartItems(cart);
    calculateTotals(cart);
  }, []);

  const calculateTotals = (items) => {
    const sub = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    setSubtotal(sub);
    // Discount would be calculated here if coupon is applied
    setTotal(sub - discount);
  };

  const handleApplyCoupon = async () => {
    if (!couponCode) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE}/api/v1x/marketplace/validate-coupon`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ coupon_code: couponCode })
      });

      if (response.ok) {
        const data = await response.json();
        setDiscount(data.discount_amount);
        setTotal(subtotal - data.discount_amount);
        setError('');
      } else {
        setError('Invalid coupon code');
      }
    } catch (err) {
      setError('Failed to apply coupon');
    }
  };

  const handleCheckout = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const productIds = cartItems.map(item => item.id);

      // Step 1: Create order (checkout)
      const checkoutResponse = await fetch(`${API_BASE}/api/v1x/marketplace/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          product_ids: productIds,
          coupon_code: couponCode || null,
          payment_method: paymentMethod
        })
      });

      if (!checkoutResponse.ok) {
        const data = await checkoutResponse.json();
        throw new Error(data.detail || 'Checkout failed');
      }

      const orderData = await checkoutResponse.json();
      setOrderNumber(orderData.order_number);

      // Complete checkout (payment handled server-side for demo)
      setSuccess(true);
      localStorage.removeItem('cart');
      setTimeout(() => {
        window.location.href = `/orders/${orderData.order_id}`;
      }, 1500);
    } catch (err) {
      setError(err.message || 'Checkout failed');
    } finally {
      setProcessing(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-green-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <div className="text-5xl mb-4">✅</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Order Confirmed!</h1>
          <p className="text-gray-600 mb-4">
            Your order {orderNumber} has been successfully processed.
          </p>
          <p className="text-sm text-gray-500">
            Redirecting to order details...
          </p>
        </div>
      </div>
    );
  }

  return (
    <Layout maxWidth="7xl" showFooter={true}>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Your Cart</h1>

            {cartItems.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Your cart is empty</p>
            ) : (
              <div className="space-y-4">
                {cartItems.map((item) => (
                  <div key={item.id} className="border rounded-lg p-4 flex justify-between items-center">
                    <div>
                      <h3 className="font-semibold text-gray-900">{item.name}</h3>
                      <p className="text-gray-600 text-sm mt-1">Qty: {item.quantity}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-gray-900">${(item.price * item.quantity).toFixed(2)}</p>
                      <p className="text-gray-600 text-sm">${item.price.toFixed(2)} each</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Coupon Section */}
            <div className="mt-8 border-t pt-6">
              <h2 className="font-semibold text-gray-900 mb-4">Apply Coupon Code</h2>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter coupon code"
                  value={couponCode}
                  onChange={(e) => setCouponCode(e.target.value)}
                  className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={processing}
                />
                <button
                  onClick={handleApplyCoupon}
                  disabled={processing || !couponCode}
                  className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
                >
                  Apply
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Order Summary & Payment */}
        <div>
          {/* Order Summary */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>
            <div className="space-y-3 border-b pb-4 mb-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-semibold">${subtotal.toFixed(2)}</span>
              </div>
              {discount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Discount</span>
                  <span>-${discount.toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between text-gray-600 text-sm">
                <span>Shipping</span>
                <span>FREE</span>
              </div>
            </div>
            <div className="flex justify-between items-center mb-6">
              <span className="text-lg font-bold text-gray-900">Total</span>
              <span className="text-2xl font-bold text-blue-600">${total.toFixed(2)}</span>
            </div>
          </div>

          {/* Payment Method Selection */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="font-bold text-gray-900 mb-4">Payment Method</h2>
            <div className="space-y-3">
              {['stripe', 'paypal'].map((method) => (
                <label key={method} className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
                  style={{
                    backgroundColor: paymentMethod === method ? '#EBF8FF' : 'white',
                    borderColor: paymentMethod === method ? '#3B82F6' : '#D1D5DB'
                  }}
                >
                  <input
                    type="radio"
                    name="payment"
                    value={method}
                    checked={paymentMethod === method}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    disabled={processing}
                    className="mr-3"
                  />
                  <span className="font-semibold capitalize">{method}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {/* Checkout Button */}
          <form onSubmit={handleCheckout}>
            <button
              type="submit"
              disabled={processing || cartItems.length === 0}
              className={`w-full py-3 px-4 rounded-lg font-bold text-white text-lg ${
                processing
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {processing ? 'Processing...' : `Pay $${total.toFixed(2)}`}
            </button>
          </form>

          {/* Trust Badges */}
          <div className="mt-6 text-center text-sm text-gray-600">
            <p className="mb-3">🔒 Secure checkout powered by Stripe & PayPal</p>
            <p>✅ Money-back guarantee within 30 days</p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CheckoutPage;

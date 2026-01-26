/**
 * Checkout Page
 * Complete checkout flow with payment processing using Stripe
 */

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout'
import { CardElement, useStripe, useElements, Elements } from '@stripe/react-stripe-js';
import { stripePromise } from '@/lib/stripe';
import { useMe } from '@/hooks/useMe';
import { API_BASE } from '@/lib/apiBase';

interface OrderData {
  order_id: number;
  order_number: string;
  total_amount: number;
  items_count: number;
  discount_amount: number;
  status: string;
  client_secret?: string;
  payment_intent_id?: string;
}

const CARD_ELEMENT_OPTIONS = {
  style: {
    base: {
      fontSize: '16px',
      color: '#424770',
      '::placeholder': {
        color: '#aab7c4',
      },
    },
    invalid: {
      color: '#9e2146',
    },
  },
};

const CheckoutFormContent: React.FC<{ orderData: OrderData }> = ({ orderData }) => {
  const stripe = useStripe();
  const elements = useElements();
  const router = useRouter();
  const { user } = useMe();
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      setErrorMessage('Stripe is not loaded');
      return;
    }

    const cardElement = elements.getElement(CardElement);

    if (!cardElement) {
      setErrorMessage('Card element not found');
      return;
    }

    setIsLoading(true);
    setErrorMessage('');

    try {
      // Confirm payment with Stripe
      const result = await stripe.confirmCardPayment(orderData.client_secret || '', {
        payment_method: {
          card: cardElement,
          billing_details: {
            name: user?.name || 'Guest',
            email: user?.email,
          },
        },
      });

      if (result.error) {
        setErrorMessage(result.error.message || 'Payment failed');
      } else if (result.paymentIntent?.status === 'succeeded') {
        // Payment successful - confirm order and redirect
        try {
          await fetch(`${API_BASE}/api/session/v1x/marketplace/confirm-payment/${orderData.order_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
          });
          router.push(`/marketplace/order-confirmation/${orderData.order_id}`);
        } catch (confirmError: any) {
          // Still redirect even if confirmation fails - payment went through
          router.push(`/marketplace/order-confirmation/${orderData.order_id}`);
        }
      } else if (result.paymentIntent?.status === 'requires_action') {
        setErrorMessage('Additional authentication required. Please complete the verification.');
      }
    } catch (error: any) {
      setErrorMessage(error.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">
          Card Details
        </label>
        <div className="p-4 border border-gray-300 rounded-lg">
          <CardElement options={CARD_ELEMENT_OPTIONS} />
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm font-medium">{errorMessage}</p>
        </div>
      )}

      <button
        type="submit"
        disabled={!stripe || isLoading}
        className="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Processing Payment...' : `Pay $${orderData.total_amount.toFixed(2)}`}
      </button>
    </form>
  );
};

const CheckoutPage = () => {
  const router = useRouter();
  const [orderData, setOrderData] = useState<OrderData | null>(null);
  const [cartSummary, setCartSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [couponCode, setCouponCode] = useState('');

  useEffect(() => {
    loadCheckout();
  }, []);

  const loadCheckout = async () => {
    try {
      setLoading(true);
      
      // Fetch current cart
      const cartResponse = await fetch(`${API_BASE}/api/session/v1x/marketplace/cart`, {
        credentials: 'include'
      });
      
      if (cartResponse.ok) {
        const cart = await cartResponse.json();
        setCartSummary(cart);
      } else if (cartResponse.status === 401) {
        router.push('/login?redirect=/marketplace/checkout');
      }
    } catch (err) {
      console.error('Error loading cart:', err);
      // Continue anyway - user can still proceed
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Get product IDs from cart summary
      const productIds = cartSummary?.items?.map((item: any) => item.id) || [];

      if (productIds.length === 0) {
        setError('Your cart is empty');
        return;
      }

      // Create order with Stripe payment
      const checkoutResponse = await fetch(`${API_BASE}/api/session/v1x/marketplace/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          product_ids: productIds,
          coupon_code: couponCode || undefined,
          payment_method: 'stripe'
        })
      });

      if (!checkoutResponse.ok) {
        const data = await checkoutResponse.json();
        throw new Error(data.detail || 'Checkout failed');
      }

      const order = await checkoutResponse.json();
      setOrderData(order);
    } catch (err: any) {
      setError(err.message || 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout maxWidth="7xl" showFooter={true}>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
            <p className="text-gray-600">Loading checkout...</p>
          </div>
        </div>
      </Layout>
    );
  }

  // Show payment form if we have order data
  if (orderData?.client_secret) {
    return (
      <Layout maxWidth="2xl" showFooter={true}>
        <div className="py-12">
          <div className="bg-white rounded-lg shadow p-8">
            <h1 className="text-3xl font-bold mb-2">Complete Your Purchase</h1>
            <p className="text-gray-600 mb-8">Order {orderData.order_number}</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="md:col-span-2">
                <Elements stripe={stripePromise}>
                  <CheckoutFormContent orderData={orderData} />
                </Elements>

                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-700">
                    💳 <strong>Test Cards (in test mode):</strong>
                  </p>
                  <ul className="text-xs text-gray-600 mt-2 space-y-1">
                    <li>Success: 4242 4242 4242 4242</li>
                    <li>Decline: 4000 0000 0000 0002</li>
                    <li>Exp: Any future date | CVC: Any 3 digits</li>
                  </ul>
                </div>
              </div>

              <div>
                <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                  <h2 className="font-bold text-gray-900 mb-4">Order Summary</h2>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Items:</span>
                      <span>{orderData.items_count}</span>
                    </div>
                    {orderData.discount_amount > 0 && (
                      <div className="flex justify-between text-green-600">
                        <span>Discount:</span>
                        <span>-${orderData.discount_amount.toFixed(2)}</span>
                      </div>
                    )}
                    <div className="border-t border-gray-200 pt-2 mt-2">
                      <div className="flex justify-between font-bold">
                        <span>Total:</span>
                        <span className="text-xl text-blue-600">${orderData.total_amount.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // Show cart summary before payment
  return (
    <Layout maxWidth="7xl" showFooter={true}>
      <div className="py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <h1 className="text-2xl font-bold text-gray-900 mb-6">Review Your Cart</h1>

              {!cartSummary?.items || cartSummary.items.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Your cart is empty</p>
              ) : (
                <div className="space-y-4">
                  {cartSummary.items.map((item: any) => (
                    <div key={item.id} className="border rounded-lg p-4 flex justify-between items-center">
                      <div>
                        <h3 className="font-semibold text-gray-900">{item.course_title || item.name}</h3>
                        <p className="text-gray-600 text-sm mt-1">ID: {item.id}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-gray-900">${item.price.toFixed(2)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Order Summary & Checkout */}
          <div>
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>
              <div className="space-y-3 border-b pb-4 mb-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-semibold">${cartSummary?.subtotal?.toFixed(2) || '0.00'}</span>
                </div>
                {cartSummary?.discount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Discount</span>
                    <span>-${cartSummary.discount.toFixed(2)}</span>
                  </div>
                )}
              </div>
              <div className="flex justify-between items-center mb-6">
                <span className="text-lg font-bold text-gray-900">Total</span>
                <span className="text-2xl font-bold text-blue-600">${(cartSummary?.total || 0).toFixed(2)}</span>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              <button
                onClick={handleCheckout}
                disabled={loading || !cartSummary?.items?.length}
                className="w-full py-3 px-4 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Processing...' : `Continue to Payment`}
              </button>

              <p className="text-xs text-gray-500 mt-4 text-center">
                🔒 Secure checkout powered by Stripe
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CheckoutPage;

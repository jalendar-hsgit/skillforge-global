import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/Button';
import { Trash2, ShoppingBag, Tag, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { API_BASE } from '@/lib/apiBase';

interface CartItem {
  id: number;
  course_id: number;
  course_title: string;
  course_path: string;
  price: number;
  added_at: string;
}

interface CartSummary {
  items: CartItem[];
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
  coupon_code?: string;
}

export default function CartPage() {
  const router = useRouter();
  const [cart, setCart] = useState<CartSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [couponCode, setCouponCode] = useState('');
  const [couponMessage, setCouponMessage] = useState('');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/session/v1x/marketplace/cart`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setCart(data);
      } else if (response.status === 401) {
        router.push('/login?redirect=/marketplace/cart');
      }
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeItem = async (itemId: number) => {
    try {
      console.log(`[Remove Item] Starting removal of cart item ${itemId}`);
      console.log(`[Remove Item] Calling DELETE /api/session/v1x/marketplace/cart/${itemId}`);
      console.log(`[Remove Item] Current cart before deletion:`, cart?.items.map(i => ({ id: i.id, courseId: i.course_id })));
      
      const response = await fetch(`${API_BASE}/api/session/v1x/marketplace/cart/${itemId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      console.log(`[Remove Item] Response status: ${response.status}, statusText: ${response.statusText}`);

      if (response.ok) {
        // Success - refresh cart
        console.log(`[Remove Item] Successfully removed item ${itemId}`);
        await fetchCart();
        console.log(`[Remove Item] Cart refreshed after deletion`);
      } else {
        // Log error details
        let errorMessage = 'Unknown error';
        try {
          const error = await response.json();
          errorMessage = error.detail || JSON.stringify(error);
          console.error('[Remove Item] 400+ error:', { 
            status: response.status, 
            statusText: response.statusText,
            itemId,
            error 
          });
          
          // Show specific error based on status code
          if (response.status === 404) {
            alert(`Item not found (ID: ${itemId}). It may have been already removed. Refreshing cart...`);
            await fetchCart();
          } else if (response.status === 403) {
            alert(`You don't have permission to remove this item.`);
          } else {
            alert(`Failed to remove item: ${errorMessage}`);
          }
        } catch (jsonError) {
          const text = await response.text();
          console.error('[Remove Item] Non-JSON error response:', { 
            status: response.status,
            statusText: response.statusText,
            itemId,
            text 
          });
          alert(`Failed to remove item: Status ${response.status} - ${response.statusText}`);
        }
      }
    } catch (error) {
      console.error('[Remove Item] Exception:', error);
      alert('Failed to remove item: Network error - ' + (error instanceof Error ? error.message : String(error)));
    }
  };

  const applyCoupon = async () => {
    if (!couponCode.trim()) return;

    try {
      const response = await fetch(`${API_BASE}/api/session/v1x/marketplace/coupons/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ coupon_code: couponCode })
      });

      if (response.ok) {
        const data = await response.json();
        setCouponMessage(`✓ Coupon applied: ${data.discount_type === 'percentage' ? data.discount_value + '%' : '$' + data.discount_value} off`);
        // Recalculate with coupon (in real app, backend should return updated cart)
        fetchCart();
      } else {
        const error = await response.json();
        setCouponMessage(`✗ ${error.detail || 'Invalid coupon'}`);
      }
    } catch (error) {
      setCouponMessage('✗ Failed to apply coupon');
    }
  };

  const handleCheckout = async () => {
    setProcessing(true);
    try {
      const response = await fetch(`${API_BASE}/api/session/v1x/marketplace/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          payment_method: 'coins', // Demo: use coins
          coupon_code: couponCode || undefined
        })
      });

      if (response.ok) {
        const order = await response.json();
        alert(`Order placed successfully! Order #${order.order_number}`);
        router.push('/marketplace/orders');
      } else {
        const error = await response.json();
        alert(error.detail || 'Checkout failed');
      }
    } catch (error) {
      console.error('Error during checkout:', error);
      alert('Checkout failed');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-deepTech flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-forgePurple border-t-transparent mb-4"></div>
            <p className="text-techGray-400">Loading your cart...</p>
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
          <div className="flex items-center gap-4 mb-8">
            <Link href="/marketplace">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Marketplace
              </Button>
            </Link>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Cart Items */}
            <div className="lg:col-span-2">
              <div className="bg-deepTech-800 rounded-2xl p-6 shadow-glow border border-techGray-800">
                <h2 className="text-2xl font-display font-black text-white mb-6 flex items-center gap-3">
                  <ShoppingBag className="w-7 h-7 text-forgePurple" />
                  Shopping Cart ({cart?.items.length || 0})
                </h2>

                {cart && cart.items.length === 0 ? (
                  <div className="text-center py-12">
                    <ShoppingBag className="w-16 h-16 text-techGray-600 mx-auto mb-4" />
                    <p className="text-techGray-400 text-lg mb-4">Your cart is empty</p>
                    <Link href="/marketplace">
                      <Button>Browse Courses</Button>
                    </Link>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {cart?.items.map(item => (
                      <div
                        key={item.id}
                        className="bg-deepTech-900 rounded-xl p-4 border border-techGray-700 hover:border-forgePurple transition-colors"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <h3 className="text-lg font-bold text-white mb-1">{item.course_title}</h3>
                            <p className="text-sm text-techGray-400">Added {new Date(item.added_at).toLocaleDateString()}</p>
                          </div>
                          
                          <div className="text-right">
                            <p className="text-2xl font-black text-forgePurple mb-2">
                              ${item.price.toFixed(2)}
                            </p>
                            <button
                              onClick={() => removeItem(item.id)}
                              className="text-red-500 hover:text-red-400 transition-colors p-2"
                            >
                              <Trash2 className="w-5 h-5" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Order Summary */}
            {cart && cart.items.length > 0 && (
              <div className="lg:col-span-1">
                <div className="bg-deepTech-800 rounded-2xl p-6 shadow-glow border border-techGray-800 sticky top-24">
                  <h3 className="text-xl font-display font-black text-white mb-6">Order Summary</h3>

                  {/* Coupon */}
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-techGray-300 mb-2">
                      Coupon Code
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={couponCode}
                        onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                        placeholder="SAVE20"
                        className="flex-1 px-4 py-2 bg-deepTech-900 border-2 border-techGray-700 rounded-lg text-white focus:border-forgePurple focus:outline-none"
                      />
                      <Button size="sm" onClick={applyCoupon}>
                        <Tag className="w-4 h-4" />
                      </Button>
                    </div>
                    {couponMessage && (
                      <p className={`text-sm mt-2 ${couponMessage.startsWith('✓') ? 'text-green-500' : 'text-red-500'}`}>
                        {couponMessage}
                      </p>
                    )}
                  </div>

                  {/* Price Breakdown */}
                  <div className="space-y-3 mb-6 pb-6 border-b border-techGray-700">
                    <div className="flex justify-between text-techGray-300">
                      <span>Subtotal</span>
                      <span className="font-semibold">${cart.subtotal.toFixed(2)}</span>
                    </div>
                    {cart.discount > 0 && (
                      <div className="flex justify-between text-green-500">
                        <span>Discount</span>
                        <span className="font-semibold">-${cart.discount.toFixed(2)}</span>
                      </div>
                    )}
                    {cart.tax > 0 && (
                      <div className="flex justify-between text-techGray-300">
                        <span>Tax</span>
                        <span className="font-semibold">${cart.tax.toFixed(2)}</span>
                      </div>
                    )}
                  </div>

                  {/* Total */}
                  <div className="flex justify-between items-center mb-6">
                    <span className="text-lg font-bold text-white">Total</span>
                    <span className="text-3xl font-black text-forgePurple">
                      ${cart.total.toFixed(2)}
                    </span>
                  </div>

                  {/* Checkout Button */}
                  <Button
                    onClick={handleCheckout}
                    disabled={processing}
                    className="w-full bg-gradient-to-r from-forgePurple via-neuralBlue to-aiElectric hover:opacity-90 text-lg font-bold py-4"
                  >
                    {processing ? 'Processing...' : 'Proceed to Checkout'}
                  </Button>

                  <p className="text-xs text-techGray-500 text-center mt-4">
                    🔒 Secure checkout powered by SkillForge
                  </p>
                </div>
              </div>
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

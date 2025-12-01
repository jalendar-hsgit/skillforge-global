import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'

type MarketplaceStats = {
  timeframe: string
  total_orders: number
  total_revenue: number
  avg_order_value: number
  active_coupons: number
  top_courses: {
    course_id: number
    title: string
    sales: number
    revenue: number
  }[]
}

type Order = {
  id: number
  order_number: string
  user_email: string
  course_title: string
  status: string
  amount: number
  discount_amount: number
  payment_method: string
  payment_status: string
  created_at: string
  coupon_code: string | null
}

type Coupon = {
  id: number
  code: string
  discount_type: string
  discount_value: number
  is_active: boolean
  expires_at: string | null
  max_uses: number | null
  current_uses: number
  created_at: string
}

export default function AdminMarketplace({ me }: AdminSSRProps) {
  const [stats, setStats] = useState<MarketplaceStats | null>(null)
  const [orders, setOrders] = useState<Order[]>([])
  const [coupons, setCoupons] = useState<Coupon[]>([])
  const [timeframe, setTimeframe] = useState<'7d' | '30d' | '90d' | '1y' | 'all'>('30d')
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'orders' | 'coupons'>('overview')
  const [showCreateCoupon, setShowCreateCoupon] = useState(false)
  
  const [couponForm, setCouponForm] = useState({
    code: '',
    discount_type: 'percentage',
    discount_value: 0,
    max_uses: null as number | null,
    expires_at: ''
  })

  useEffect(() => {
    loadMarketplaceData()
  }, [timeframe])

  async function loadMarketplaceData() {
    setLoading(true)
    try {
      const [statsRes, ordersRes, couponsRes] = await Promise.all([
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/stats?timeframe=${timeframe}`,
          { credentials: 'include' }
        ),
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/orders?limit=50`,
          { credentials: 'include' }
        ),
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/coupons`,
          { credentials: 'include' }
        )
      ])

      if (statsRes.ok) {
        const data = await statsRes.json()
        setStats(data)
      }

      if (ordersRes.ok) {
        const data = await ordersRes.json()
        setOrders(data.orders || [])
      }

      if (couponsRes.ok) {
        const data = await couponsRes.json()
        setCoupons(data)
      }
    } catch (err) {
      console.error('Failed to load marketplace data:', err)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreateCoupon() {
    if (!couponForm.code || couponForm.discount_value <= 0) {
      alert('Please fill in all required fields')
      return
    }

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/coupons`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            code: couponForm.code.toUpperCase(),
            discount_type: couponForm.discount_type,
            discount_value: couponForm.discount_value,
            max_uses: couponForm.max_uses,
            expires_at: couponForm.expires_at || null
          })
        }
      )

      if (!res.ok) {
        const err = await res.json()
        alert(`Failed: ${err.detail || 'Unknown error'}`)
        return
      }

      alert('Coupon created successfully!')
      setShowCreateCoupon(false)
      setCouponForm({ code: '', discount_type: 'percentage', discount_value: 0, max_uses: null, expires_at: '' })
      loadMarketplaceData()
    } catch (err) {
      console.error(err)
      alert('An error occurred')
    }
  }

  async function toggleCoupon(couponId: number) {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/coupons/${couponId}/toggle`,
        {
          method: 'PATCH',
          credentials: 'include'
        }
      )

      if (!res.ok) throw new Error('Failed')

      loadMarketplaceData()
    } catch (err) {
      console.error(err)
      alert('Failed to toggle coupon')
    }
  }

  async function deleteCoupon(couponId: number) {
    if (!confirm('Delete this coupon? This cannot be undone.')) return

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/coupons/${couponId}`,
        {
          method: 'DELETE',
          credentials: 'include'
        }
      )

      if (!res.ok) throw new Error('Failed')

      alert('Coupon deleted')
      loadMarketplaceData()
    } catch (err) {
      console.error(err)
      alert('Failed to delete coupon')
    }
  }

  async function refundOrder(orderId: number, orderNumber: string) {
    if (!confirm(`Refund order ${orderNumber}? This will mark the order as refunded.`)) return

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/orders/${orderId}/refund`,
        {
          method: 'POST',
          credentials: 'include'
        }
      )

      if (!res.ok) throw new Error('Failed')

      alert('Order refunded successfully')
      loadMarketplaceData()
    } catch (err) {
      console.error(err)
      alert('Failed to refund order')
    }
  }

  function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <Layout>
      <Head>
        <title>Marketplace Admin – SkillForge Global</title>
      </Head>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Marketplace Management</h1>
          <p className="text-techGray">Orders, coupons, and sales analytics</p>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-2 border-b border-white/10">
          {(['overview', 'orders', 'coupons'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === tab
                  ? 'text-white border-b-2 border-forgePurple'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading...</div>
        ) : (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && stats && (
              <div className="space-y-6">
                {/* Timeframe Selector */}
                <div className="flex gap-2">
                  {(['7d', '30d', '90d', '1y', 'all'] as const).map((tf) => (
                    <button
                      key={tf}
                      onClick={() => setTimeframe(tf)}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        timeframe === tf
                          ? 'bg-forgePurple text-white'
                          : 'bg-white/5 text-gray-400 hover:bg-white/10'
                      }`}
                    >
                      {tf === 'all' ? 'All Time' : `Last ${tf.toUpperCase()}`}
                    </button>
                  ))}
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <MetricCard title="Total Orders" value={stats.total_orders.toString()} icon="🛒" />
                  <MetricCard title="Total Revenue" value={formatCurrency(stats.total_revenue)} icon="💰" />
                  <MetricCard title="Avg Order Value" value={formatCurrency(stats.avg_order_value)} icon="📊" />
                  <MetricCard title="Active Coupons" value={stats.active_coupons.toString()} icon="🎫" />
                </div>

                {/* Top Selling Courses */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                  <h2 className="text-xl font-bold text-white mb-4">Top Selling Courses</h2>
                  <div className="space-y-3">
                    {stats.top_courses.map((course, idx) => (
                      <div
                        key={course.course_id}
                        className="flex items-center justify-between p-4 rounded-lg bg-white/5"
                      >
                        <div className="flex items-center gap-4">
                          <span className="text-2xl font-bold text-gray-400">#{idx + 1}</span>
                          <div>
                            <p className="text-white font-medium">{course.title}</p>
                            <p className="text-sm text-gray-400">{course.sales} sales</p>
                          </div>
                        </div>
                        <p className="text-green-400 font-bold text-lg">
                          {formatCurrency(course.revenue)}
                        </p>
                      </div>
                    ))}
                    {stats.top_courses.length === 0 && (
                      <p className="text-center py-6 text-gray-400">No sales data available</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Orders Tab */}
            {activeTab === 'orders' && (
              <div className="rounded-xl border border-white/10 bg-white/5 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-sm text-gray-400 border-b border-white/10 bg-white/5">
                        <th className="p-4">Order #</th>
                        <th className="p-4">Customer</th>
                        <th className="p-4">Course</th>
                        <th className="p-4">Amount</th>
                        <th className="p-4">Status</th>
                        <th className="p-4">Date</th>
                        <th className="p-4">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.map((order) => (
                        <tr key={order.id} className="border-b border-white/5">
                          <td className="p-4 text-white font-mono">{order.order_number}</td>
                          <td className="p-4 text-gray-300">{order.user_email}</td>
                          <td className="p-4 text-white">{order.course_title}</td>
                          <td className="p-4 text-green-400 font-medium">
                            {formatCurrency(order.amount)}
                            {order.discount_amount > 0 && (
                              <span className="text-xs text-yellow-400 ml-2">
                                (-{formatCurrency(order.discount_amount)})
                              </span>
                            )}
                          </td>
                          <td className="p-4">
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              order.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                              order.status === 'refunded' ? 'bg-red-500/20 text-red-300' :
                              'bg-yellow-500/20 text-yellow-300'
                            }`}>
                              {order.status}
                            </span>
                          </td>
                          <td className="p-4 text-gray-400 text-sm">
                            {formatDate(order.created_at)}
                          </td>
                          <td className="p-4">
                            {order.status !== 'refunded' && (
                              <button
                                onClick={() => refundOrder(order.id, order.order_number)}
                                className="text-red-400 hover:text-red-300 text-sm"
                              >
                                Refund
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                      {orders.length === 0 && (
                        <tr>
                          <td colSpan={7} className="py-12 text-center text-gray-400">
                            No orders found
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Coupons Tab */}
            {activeTab === 'coupons' && (
              <div className="space-y-6">
                <button
                  onClick={() => setShowCreateCoupon(true)}
                  className="px-6 py-3 bg-forgePurple hover:bg-forgePurple/80 rounded-lg font-medium transition-colors"
                >
                  ➕ Create Coupon
                </button>

                <div className="rounded-xl border border-white/10 bg-white/5 overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="text-left text-sm text-gray-400 border-b border-white/10 bg-white/5">
                          <th className="p-4">Code</th>
                          <th className="p-4">Discount</th>
                          <th className="p-4">Uses</th>
                          <th className="p-4">Expires</th>
                          <th className="p-4">Status</th>
                          <th className="p-4">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {coupons.map((coupon) => (
                          <tr key={coupon.id} className="border-b border-white/5">
                            <td className="p-4 text-white font-mono font-bold">{coupon.code}</td>
                            <td className="p-4 text-gray-300">
                              {coupon.discount_type === 'percentage' 
                                ? `${coupon.discount_value}%`
                                : formatCurrency(coupon.discount_value)}
                            </td>
                            <td className="p-4 text-gray-400">
                              {coupon.current_uses}
                              {coupon.max_uses && ` / ${coupon.max_uses}`}
                            </td>
                            <td className="p-4 text-gray-400 text-sm">
                              {coupon.expires_at ? formatDate(coupon.expires_at) : 'Never'}
                            </td>
                            <td className="p-4">
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                coupon.is_active
                                  ? 'bg-green-500/20 text-green-300'
                                  : 'bg-gray-500/20 text-gray-400'
                              }`}>
                                {coupon.is_active ? 'Active' : 'Inactive'}
                              </span>
                            </td>
                            <td className="p-4 flex gap-2">
                              <button
                                onClick={() => toggleCoupon(coupon.id)}
                                className="text-blue-400 hover:text-blue-300 text-sm"
                              >
                                {coupon.is_active ? 'Deactivate' : 'Activate'}
                              </button>
                              <button
                                onClick={() => deleteCoupon(coupon.id)}
                                className="text-red-400 hover:text-red-300 text-sm"
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))}
                        {coupons.length === 0 && (
                          <tr>
                            <td colSpan={6} className="py-12 text-center text-gray-400">
                              No coupons created yet
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* Create Coupon Modal */}
        {showCreateCoupon && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-6 max-w-md w-full">
              <h2 className="text-2xl font-bold text-white mb-6">Create Coupon</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Coupon Code *</label>
                  <input
                    type="text"
                    value={couponForm.code}
                    onChange={(e) => setCouponForm({ ...couponForm, code: e.target.value.toUpperCase() })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white font-mono"
                    placeholder="e.g., SAVE20"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Discount Type *</label>
                  <select
                    value={couponForm.discount_type}
                    onChange={(e) => setCouponForm({ ...couponForm, discount_type: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white"
                  >
                    <option value="percentage">Percentage (%)</option>
                    <option value="fixed">Fixed Amount ($)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Discount Value * {couponForm.discount_type === 'percentage' ? '(0-100)' : '($)'}
                  </label>
                  <input
                    type="number"
                    value={couponForm.discount_value}
                    onChange={(e) => setCouponForm({ ...couponForm, discount_value: parseFloat(e.target.value) })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white"
                    min="0"
                    max={couponForm.discount_type === 'percentage' ? 100 : undefined}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Max Uses (Optional)</label>
                  <input
                    type="number"
                    value={couponForm.max_uses || ''}
                    onChange={(e) => setCouponForm({ ...couponForm, max_uses: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white"
                    placeholder="Unlimited"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Expires At (Optional)</label>
                  <input
                    type="datetime-local"
                    value={couponForm.expires_at}
                    onChange={(e) => setCouponForm({ ...couponForm, expires_at: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleCreateCoupon}
                  className="flex-1 px-6 py-3 bg-forgePurple hover:bg-forgePurple/80 rounded-lg font-medium transition-colors"
                >
                  Create Coupon
                </button>
                <button
                  onClick={() => setShowCreateCoupon(false)}
                  className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

function MetricCard({ title, value, icon }: { title: string; value: string; icon: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-6">
      <div className="flex items-start justify-between mb-2">
        <p className="text-sm text-gray-400">{title}</p>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  )
}

export const getServerSideProps = requireAdminSSR

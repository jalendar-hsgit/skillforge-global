import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'
import { CheckCircle, XCircle, AlertCircle, Search, Filter, Eye, EyeOff, Trash2 } from 'lucide-react'

type Product = {
  id: number
  name: string
  seller_id: number
  seller_email: string
  price: number
  status: 'draft' | 'published' | 'suspended' | 'archived'
  sales_count: number
  created_at: string
  suspension_reason?: string
  views_count: number
  average_rating: number
}

type Seller = {
  seller_id: number
  user_id: number
  email: string
  store_name: string
  status: string
  products_count: number
  sales_count: number
  total_revenue: number
  created_at: string
}

type DashboardStats = {
  products: {
    total: number
    published: number
    draft: number
    suspended: number
  }
  sellers: {
    total: number
    verified: number
    pending: number
  }
  sales: {
    total_transactions: number
    total_revenue: number
    platform_fee: number
    seller_earnings: number
  }
}

export default function AdminMarketplace({ me }: AdminSSRProps) {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [sellers, setSellers] = useState<Seller[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'dashboard' | 'products' | 'sellers'>('dashboard')
  const [productSearch, setProductSearch] = useState('')
  const [productStatusFilter, setProductStatusFilter] = useState<string>('')
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [suspensionReason, setSuspensionReason] = useState('')
  
  useEffect(() => {
    loadMarketplaceData()
  }, [])

  async function loadMarketplaceData() {
    setLoading(true)
    try {
      const [dashRes, productsRes, sellersRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/dashboard`, { credentials: 'include' }),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/products`, { credentials: 'include' }),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/sellers`, { credentials: 'include' })
      ])

      if (dashRes.ok) setStats(await dashRes.json())
      if (productsRes.ok) {
        const data = await productsRes.json()
        setProducts(data.products || [])
      }
      if (sellersRes.ok) {
        const data = await sellersRes.json()
        setSellers(data.sellers || [])
      }
    } catch (err) {
      console.error('Failed to load data:', err)
    } finally {
      setLoading(false)
    }
  }

  async function approveProduct(productId: number) {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/products/${productId}/approve`,
        { method: 'PUT', credentials: 'include' }
      )
      if (res.ok) {
        alert('Product approved!')
        loadMarketplaceData()
      }
    } catch (err) {
      alert('Failed to approve product')
    }
  }

  async function suspendProduct(productId: number) {
    if (!suspensionReason.trim()) {
      alert('Please provide a suspension reason')
      return
    }
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/products/${productId}/suspend`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ reason: suspensionReason })
        }
      )
      if (res.ok) {
        alert('Product suspended!')
        setSuspensionReason('')
        setSelectedProduct(null)
        loadMarketplaceData()
      }
    } catch (err) {
      alert('Failed to suspend product')
    }
  }

  async function verifySeller(sellerId: number) {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/marketplace/sellers/${sellerId}/verify`,
        { method: 'PUT', credentials: 'include' }
      )
      if (res.ok) {
        alert('Seller verified!')
        loadMarketplaceData()
      }
    } catch (err) {
      alert('Failed to verify seller')
    }
  }

  const filteredProducts = products.filter(p => {
    const matchSearch = p.name.toLowerCase().includes(productSearch.toLowerCase())
    const matchStatus = !productStatusFilter || p.status === productStatusFilter
    return matchSearch && matchStatus
  })

  return (
    <Layout>
      <Head>
        <title>Marketplace Admin – SkillForge Global</title>
      </Head>

      <div className="min-h-screen bg-deepTech-950 bg-neural">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-forgePurple-400 via-neuralBlue-400 to-aiElectric-400 mb-2">
              Marketplace Admin
            </h1>
            <p className="text-techGray-400">Manage products, sellers, and digital marketplace</p>
          </div>

          {/* Tabs */}
          <div className="mb-6 flex gap-2 border-b border-white/10">
            {(['dashboard', 'products', 'sellers'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-3 font-semibold transition-all ${
                  activeTab === tab
                    ? 'text-white border-b-2 border-forgePurple-400'
                    : 'text-techGray-400 hover:text-white'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-forgePurple-400 border-t-transparent"></div>
              <p className="mt-4 text-techGray-400">Loading...</p>
            </div>
          ) : (
            <>
              {/* Dashboard Tab */}
              {activeTab === 'dashboard' && stats && (
                <div className="space-y-6">
                  {/* Stats Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <StatCard
                      title="Total Products"
                      value={stats.products.total.toString()}
                      color="from-forgePurple-500 to-forgePurple-600"
                      icon="📦"
                    />
                    <StatCard
                      title="Published"
                      value={stats.products.published.toString()}
                      color="from-green-500 to-green-600"
                      icon="✓"
                    />
                    <StatCard
                      title="Draft / Pending"
                      value={stats.products.draft.toString()}
                      color="from-yellow-500 to-yellow-600"
                      icon="⏳"
                    />
                    <StatCard
                      title="Suspended"
                      value={stats.products.suspended.toString()}
                      color="from-red-500 to-red-600"
                      icon="⚠️"
                    />
                  </div>

                  {/* Revenue Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <StatCard
                      title="Total Revenue"
                      value={`$${stats.sales.total_revenue.toFixed(2)}`}
                      color="from-aiElectric-500 to-aiElectric-600"
                      icon="💰"
                    />
                    <StatCard
                      title="Platform Fee (20%)"
                      value={`$${stats.sales.platform_fee.toFixed(2)}`}
                      color="from-neuralBlue-500 to-neuralBlue-600"
                      icon="🏦"
                    />
                  </div>

                  {/* Seller Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <StatCard
                      title="Total Sellers"
                      value={stats.sellers.total.toString()}
                      color="from-purple-500 to-purple-600"
                      icon="👥"
                    />
                    <StatCard
                      title="Verified Sellers"
                      value={stats.sellers.verified.toString()}
                      color="from-green-500 to-green-600"
                      icon="✅"
                    />
                    <StatCard
                      title="Pending Verification"
                      value={stats.sellers.pending.toString()}
                      color="from-yellow-500 to-yellow-600"
                      icon="⏳"
                    />
                  </div>
                </div>
              )}

              {/* Products Tab */}
              {activeTab === 'products' && (
                <div className="space-y-4">
                  {/* Search & Filter */}
                  <div className="flex gap-4 mb-6">
                    <div className="flex-1 relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-techGray-400" />
                      <input
                        type="text"
                        value={productSearch}
                        onChange={(e) => setProductSearch(e.target.value)}
                        placeholder="Search products..."
                        className="w-full pl-10 pr-4 py-2 bg-deepTech-800 border border-white/10 rounded-lg text-white placeholder-techGray-400 focus:border-forgePurple-400 focus:outline-none"
                      />
                    </div>
                    <select
                      value={productStatusFilter}
                      onChange={(e) => setProductStatusFilter(e.target.value)}
                      className="px-4 py-2 bg-deepTech-800 border border-white/10 rounded-lg text-white focus:border-forgePurple-400 focus:outline-none"
                    >
                      <option value="">All Status</option>
                      <option value="draft">Draft</option>
                      <option value="published">Published</option>
                      <option value="suspended">Suspended</option>
                    </select>
                  </div>

                  {/* Products Table */}
                  <div className="bg-glass backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="text-left text-techGray-300 bg-deepTech-800/50 border-b border-white/10">
                            <th className="px-6 py-3 font-semibold">Product</th>
                            <th className="px-6 py-3 font-semibold">Seller</th>
                            <th className="px-6 py-3 font-semibold text-right">Price</th>
                            <th className="px-6 py-3 font-semibold text-center">Status</th>
                            <th className="px-6 py-3 font-semibold text-right">Sales</th>
                            <th className="px-6 py-3 font-semibold">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredProducts.length === 0 ? (
                            <tr>
                              <td colSpan={6} className="px-6 py-8 text-center text-techGray-400">
                                No products found
                              </td>
                            </tr>
                          ) : (
                            filteredProducts.map((product) => (
                              <tr key={product.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                <td className="px-6 py-4">
                                  <div>
                                    <p className="text-white font-medium">{product.name}</p>
                                    <p className="text-xs text-techGray-400"># {product.id}</p>
                                  </div>
                                </td>
                                <td className="px-6 py-4">
                                  <p className="text-techGray-300">{product.seller_email}</p>
                                </td>
                                <td className="px-6 py-4 text-right">
                                  <span className="text-aiElectric-400 font-semibold">${product.price.toFixed(2)}</span>
                                </td>
                                <td className="px-6 py-4 text-center">
                                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                                    product.status === 'published' ? 'bg-green-500/20 text-green-300' :
                                    product.status === 'draft' ? 'bg-yellow-500/20 text-yellow-300' :
                                    product.status === 'suspended' ? 'bg-red-500/20 text-red-300' :
                                    'bg-gray-500/20 text-gray-300'
                                  }`}>
                                    {product.status}
                                  </span>
                                </td>
                                <td className="px-6 py-4 text-right">
                                  <span className="text-white font-semibold">{product.sales_count}</span>
                                </td>
                                <td className="px-6 py-4">
                                  <div className="flex gap-2">
                                    {product.status === 'draft' && (
                                      <button
                                        onClick={() => approveProduct(product.id)}
                                        className="px-3 py-1 bg-green-500/20 text-green-300 rounded text-xs hover:bg-green-500/30 transition-colors flex items-center gap-1"
                                        title="Approve"
                                      >
                                        <CheckCircle className="w-4 h-4" />
                                        Approve
                                      </button>
                                    )}
                                    {product.status !== 'suspended' && (
                                      <button
                                        onClick={() => setSelectedProduct(product)}
                                        className="px-3 py-1 bg-red-500/20 text-red-300 rounded text-xs hover:bg-red-500/30 transition-colors flex items-center gap-1"
                                        title="Suspend"
                                      >
                                        <AlertCircle className="w-4 h-4" />
                                        Suspend
                                      </button>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* Sellers Tab */}
              {activeTab === 'sellers' && (
                <div className="space-y-4">
                  <div className="bg-glass backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="text-left text-techGray-300 bg-deepTech-800/50 border-b border-white/10">
                            <th className="px-6 py-3 font-semibold">Store</th>
                            <th className="px-6 py-3 font-semibold">Email</th>
                            <th className="px-6 py-3 font-semibold text-center">Products</th>
                            <th className="px-6 py-3 font-semibold text-center">Sales</th>
                            <th className="px-6 py-3 font-semibold text-right">Revenue</th>
                            <th className="px-6 py-3 font-semibold text-center">Status</th>
                            <th className="px-6 py-3 font-semibold">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {sellers.map((seller) => (
                            <tr key={seller.seller_id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                              <td className="px-6 py-4">
                                <p className="text-white font-medium">{seller.store_name}</p>
                              </td>
                              <td className="px-6 py-4">
                                <p className="text-techGray-300">{seller.email}</p>
                              </td>
                              <td className="px-6 py-4 text-center">
                                <span className="text-white font-semibold">{seller.products_count}</span>
                              </td>
                              <td className="px-6 py-4 text-center">
                                <span className="text-white font-semibold">{seller.sales_count}</span>
                              </td>
                              <td className="px-6 py-4 text-right">
                                <span className="text-aiElectric-400 font-semibold">${seller.total_revenue.toFixed(2)}</span>
                              </td>
                              <td className="px-6 py-4 text-center">
                                <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                                  seller.status === 'verified' ? 'bg-green-500/20 text-green-300' :
                                  'bg-yellow-500/20 text-yellow-300'
                                }`}>
                                  {seller.status}
                                </span>
                              </td>
                              <td className="px-6 py-4">
                                {seller.status !== 'verified' && (
                                  <button
                                    onClick={() => verifySeller(seller.seller_id)}
                                    className="px-3 py-1 bg-green-500/20 text-green-300 rounded text-xs hover:bg-green-500/30 transition-colors"
                                  >
                                    Verify
                                  </button>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Suspension Modal */}
        {selectedProduct && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-deepTech-800 border border-white/10 rounded-2xl p-8 max-w-md w-full">
              <h3 className="text-xl font-bold text-white mb-4">Suspend Product</h3>
              <p className="text-techGray-300 mb-4">
                Product: <strong>{selectedProduct.name}</strong>
              </p>
              <textarea
                value={suspensionReason}
                onChange={(e) => setSuspensionReason(e.target.value)}
                placeholder="Reason for suspension..."
                className="w-full p-3 bg-deepTech-900 border border-white/10 rounded-lg text-white placeholder-techGray-400 focus:border-red-400 focus:outline-none mb-4 min-h-24"
              />
              <div className="flex gap-3">
                <button
                  onClick={() => suspendProduct(selectedProduct.id)}
                  className="flex-1 px-4 py-2 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg transition-colors"
                >
                  Suspend
                </button>
                <button
                  onClick={() => {
                    setSelectedProduct(null)
                    setSuspensionReason('')
                  }}
                  className="flex-1 px-4 py-2 bg-deepTech-700 hover:bg-deepTech-600 text-white font-semibold rounded-lg transition-colors"
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

function StatCard({ title, value, color, icon }: { title: string; value: string; color: string; icon: string }) {
  return (
    <div className={`bg-gradient-to-br ${color} rounded-xl p-6 text-white`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium opacity-90">{title}</p>
          <p className="text-3xl font-black mt-2">{value}</p>
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  )
}

export async function getServerSideProps(context: any) {
  return requireAdminSSR(context)
}

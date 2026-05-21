import React, { useState, useEffect } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { useAuth } from '@/hooks/useAuth'
import Link from 'next/link'
import Layout from '@/components/Layout'

interface PayoutStats {
  pending_requests: number
  processing_requests: number
  pending_amount: number
  approved_amount: number
  completed_amount: number
  unverified_payment_methods: number
}

interface PayoutRequest {
  id: number
  mentor_id: number
  mentor_name: string
  mentor_email: string
  amount: number
  status: string
  payment_method_id: number | null
  payment_method_info: string | null
  created_at: string
  updated_at: string
  approved_at: string | null
  completed_at: string | null
  rejection_reason: string | null
  admin_notes: string | null
}

interface PaymentMethod {
  id: number
  mentor_id: number
  mentor_name: string
  account_holder_name: string
  bank_name: string
  account_last_four: string
  status: string
  is_default: boolean
  created_at: string
}

export default function AdminPayoutsPage() {
  const router = useRouter()
  const { user, isAuthenticated, isLoading } = useAuth()

  // State
  const [stats, setStats] = useState<PayoutStats | null>(null)
  const [payoutRequests, setPayoutRequests] = useState<PayoutRequest[]>([])
  const [unverifiedMethods, setUnverifiedMethods] = useState<PaymentMethod[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedPayout, setSelectedPayout] = useState<PayoutRequest | null>(null)
  const [actionNotes, setActionNotes] = useState('')
  const [rejectionReason, setRejectionReason] = useState('')
  const [activeTab, setActiveTab] = useState('pending')

  useEffect(() => {
    if (isLoading) return

    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    if (user && user.role && !['ADMIN', 'SUPERADMIN'].includes(user.role)) {
      router.push('/')
      return
    }

    if (isAuthenticated && user?.id) {
      loadData()
    }
  }, [isLoading, isAuthenticated, user?.id, user?.role])

  const loadData = async () => {
    setLoading(true)
    setError('')

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

      const [statsRes, payoutsRes, methodsRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1x/admin/payouts/stats`, {
          credentials: 'include',
        }),
        fetch(`${API_BASE}/api/v1x/admin/payouts/pending`, {
          credentials: 'include',
        }),
        fetch(`${API_BASE}/api/v1x/admin/payouts/payment-methods/unverified`, {
          credentials: 'include',
        }),
      ])

      if (statsRes.ok) {
        setStats(await statsRes.json())
      }

      if (payoutsRes.ok) {
        setPayoutRequests(await payoutsRes.json())
      }

      if (methodsRes.ok) {
        setUnverifiedMethods(await methodsRes.json())
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load payout data')
      console.error('Error loading data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleApprovePayout = async (payoutId: number) => {
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

      const res = await fetch(
        `${API_BASE}/api/v1x/admin/payouts/${payoutId}/approve`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ admin_notes: actionNotes }),
          credentials: 'include',
        }
      )

      if (res.ok) {
        setActionNotes('')
        setSelectedPayout(null)
        loadData()
      } else {
        const data = await res.json()
        alert(data.detail || 'Failed to approve payout')
      }
    } catch (err) {
      alert('Error approving payout')
      console.error(err)
    }
  }

  const handleRejectPayout = async (payoutId: number) => {
    if (!rejectionReason.trim()) {
      alert('Please provide a rejection reason')
      return
    }

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

      const res = await fetch(
        `${API_BASE}/api/v1x/admin/payouts/${payoutId}/reject`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            rejection_reason: rejectionReason,
            admin_notes: actionNotes,
          }),
          credentials: 'include',
        }
      )

      if (res.ok) {
        setRejectionReason('')
        setActionNotes('')
        setSelectedPayout(null)
        loadData()
      } else {
        const data = await res.json()
        alert(data.detail || 'Failed to reject payout')
      }
    } catch (err) {
      alert('Error rejecting payout')
      console.error(err)
    }
  }

  const handleVerifyPaymentMethod = async (
    methodId: number,
    status: 'VERIFIED' | 'REJECTED'
  ) => {
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

      const res = await fetch(
        `${API_BASE}/api/v1x/admin/payouts/payment-methods/${methodId}/verify`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status }),
          credentials: 'include',
        }
      )

      if (res.ok) {
        loadData()
      } else {
        const data = await res.json()
        alert(data.detail || 'Failed to verify payment method')
      }
    } catch (err) {
      alert('Error verifying payment method')
      console.error(err)
    }
  }

  if (loading || isLoading) {
    return (
      <div className="min-h-screen bg-deepTech flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-techGray">Loading payout data...</p>
        </div>
      </div>
    )
  }

  return (
    <Layout>
      <Head>
        <title>Mentor Payouts - SkillForge Admin</title>
        <meta name="description" content="Manage mentor payouts and payments" />
      </Head>

      <div className="bg-deepTech py-8">
        <div className="max-w-7xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                💰 Mentor Payouts Management
              </h1>
              <p className="text-techGray">
                Review and approve mentor withdrawal requests
              </p>
            </div>
            <Link href="/admin/dashboard">
              <button className="px-4 py-2 rounded-lg bg-forgePurple hover:bg-forgePurple/80 text-white">
                ← Back
              </button>
            </Link>
          </div>

          {error && (
            <div className="bg-red-500/20 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white/5 border border-white/10 rounded-lg p-6">
                <div className="text-techGray text-sm mb-2">Pending Requests</div>
                <div className="text-3xl font-bold text-yellow-400">
                  {stats.pending_requests}
                </div>
                <div className="text-techGray text-sm mt-2">
                  ${stats.pending_amount.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-lg p-6">
                <div className="text-techGray text-sm mb-2">Processing</div>
                <div className="text-3xl font-bold text-blue-400">
                  {stats.processing_requests}
                </div>
                <div className="text-techGray text-sm mt-2">
                  Awaiting bank confirmation
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-lg p-6">
                <div className="text-techGray text-sm mb-2">Unverified Payment Methods</div>
                <div className="text-3xl font-bold text-orange-400">
                  {stats.unverified_payment_methods}
                </div>
                <div className="text-techGray text-sm mt-2">
                  Awaiting review
                </div>
              </div>
            </div>
          )}

          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b border-white/10">
            <button
              onClick={() => setActiveTab('pending')}
              className={`px-4 py-2 font-medium transition-colors ${
                activeTab === 'pending'
                  ? 'text-forgePurple border-b-2 border-forgePurple'
                  : 'text-techGray hover:text-white'
              }`}
            >
              Pending Requests ({stats?.pending_requests || 0})
            </button>
            <button
              onClick={() => setActiveTab('methods')}
              className={`px-4 py-2 font-medium transition-colors ${
                activeTab === 'methods'
                  ? 'text-forgePurple border-b-2 border-forgePurple'
                  : 'text-techGray hover:text-white'
              }`}
            >
              Payment Methods ({stats?.unverified_payment_methods || 0})
            </button>
          </div>

          {/* Pending Payouts Section */}
          {activeTab === 'pending' && (
            <div>
              {payoutRequests.length === 0 ? (
                <div className="bg-white/5 border border-white/10 rounded-lg p-12 text-center">
                  <p className="text-techGray text-lg">No pending payout requests</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {payoutRequests.map((payout) => (
                    <div
                      key={payout.id}
                      className="bg-white/5 border border-white/10 rounded-lg p-6"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-white font-bold text-lg">
                            {payout.mentor_name}
                          </h3>
                          <p className="text-techGray text-sm">{payout.mentor_email}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-green-400">
                            ${payout.amount.toLocaleString('en-US', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                          </div>
                          <span
                            className={`text-xs px-2 py-1 rounded inline-block mt-2 ${
                              payout.status === 'PENDING'
                                ? 'bg-yellow-600/20 text-yellow-400'
                                : 'bg-blue-600/20 text-blue-400'
                            }`}
                          >
                            {payout.status}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                        <div>
                          <span className="text-techGray">Requested:</span>
                          <p className="text-white">
                            {new Date(payout.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        {payout.payment_method_info && (
                          <div>
                            <span className="text-techGray">Payment Method:</span>
                            <p className="text-white">{payout.payment_method_info}</p>
                          </div>
                        )}
                      </div>

                      {selectedPayout?.id === payout.id ? (
                        <div className="bg-white/5 p-4 rounded border border-white/10">
                          <div className="mb-4">
                            <label className="block text-sm text-techGray mb-2">
                              Admin Notes (Optional)
                            </label>
                            <textarea
                              value={actionNotes}
                              onChange={(e) => setActionNotes(e.target.value)}
                              placeholder="Add any notes about this approval..."
                              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white placeholder-gray-400 focus:outline-none focus:border-techBlue text-sm"
                              rows={3}
                            />
                          </div>

                          {payout.status === 'PENDING' && (
                            <>
                              <div className="mb-4">
                                <label className="block text-sm text-techGray mb-2">
                                  Rejection Reason (if rejecting)
                                </label>
                                <input
                                  type="text"
                                  value={rejectionReason}
                                  onChange={(e) => setRejectionReason(e.target.value)}
                                  placeholder="Reason for rejection..."
                                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white placeholder-gray-400 focus:outline-none focus:border-techBlue text-sm"
                                />
                              </div>

                              <div className="flex gap-3">
                                <button
                                  onClick={() => handleApprovePayout(payout.id)}
                                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded transition-colors"
                                >
                                  ✓ Approve
                                </button>
                                <button
                                  onClick={() => handleRejectPayout(payout.id)}
                                  className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded transition-colors"
                                >
                                  ✕ Reject
                                </button>
                                <button
                                  onClick={() => {
                                    setSelectedPayout(null)
                                    setActionNotes('')
                                    setRejectionReason('')
                                  }}
                                  className="flex-1 px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium rounded transition-colors"
                                >
                                  Cancel
                                </button>
                              </div>
                            </>
                          )}
                        </div>
                      ) : (
                        <button
                          onClick={() => setSelectedPayout(payout)}
                          className="w-full px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium rounded transition-colors"
                        >
                          Review Request
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Payment Methods Section */}
          {activeTab === 'methods' && (
            <div>
              {unverifiedMethods.length === 0 ? (
                <div className="bg-white/5 border border-white/10 rounded-lg p-12 text-center">
                  <p className="text-techGray text-lg">
                    All payment methods verified
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {unverifiedMethods.map((method) => (
                    <div
                      key={method.id}
                      className="bg-white/5 border border-white/10 rounded-lg p-6"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-white font-bold">
                            {method.mentor_name}
                          </h3>
                          <p className="text-techGray text-sm">
                            {method.account_holder_name} • {method.bank_name}
                          </p>
                          <p className="text-techGray text-xs mt-1">
                            ••••{method.account_last_four}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() =>
                              handleVerifyPaymentMethod(method.id, 'VERIFIED')
                            }
                            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded transition-colors"
                          >
                            ✓ Verify
                          </button>
                          <button
                            onClick={() =>
                              handleVerifyPaymentMethod(method.id, 'REJECTED')
                            }
                            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded transition-colors"
                          >
                            ✕ Reject
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

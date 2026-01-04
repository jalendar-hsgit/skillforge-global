import Head from 'next/head'
import DashboardLayout from '@/components/DashboardLayout'
import DashboardStatCard from '@/components/DashboardStatCard'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { DashboardGridSkeleton, DashboardListSkeleton } from '@/components/DashboardSkeletons'

type Balance = {
  available_balance: number
  pending_payouts: number
  total_earned: number
  last_payout: string | null
  next_payout_eligible_date: string
}

type Payout = {
  id: number
  amount: number
  status: string
  requested_at: string
  completed_at: string | null
  bank_account_last4: string
  failure_reason: string | null
  notes: string
}

type PaymentMethod = {
  id: number
  type: string
  account_holder: string
  account_number: string
  routing_number: string
  bank_name: string
  is_default: boolean
  verified: boolean
  created_at: string
}

export default function MentorPayouts() {
  const router = useRouter()
  const [balance, setBalance] = useState<Balance | null>(null)
  const [payouts, setPayouts] = useState<Payout[]>([])
  const [methods, setMethods] = useState<PaymentMethod[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Payout form state
  const [showPayoutForm, setShowPayoutForm] = useState(false)
  const [payoutAmount, setPayoutAmount] = useState('')
  const [payoutSubmitting, setPayoutSubmitting] = useState(false)
  const [payoutError, setPayoutError] = useState('')
  const [payoutSuccess, setPayoutSuccess] = useState('')
  
  // Payment method form state
  const [showMethodForm, setShowMethodForm] = useState(false)
  const [methodForm, setMethodForm] = useState({
    account_holder_name: '',
    account_number: '',
    routing_number: '',
    account_type: 'checking',
    country: 'US',
    is_default: false
  })
  const [methodSubmitting, setMethodSubmitting] = useState(false)
  const [methodError, setMethodError] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
      
      const [balanceRes, payoutsRes, methodsRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1x/mentors/balance`, { credentials: 'include' }),
        fetch(`${API_BASE}/api/v1x/mentors/payouts`, { credentials: 'include' }),
        fetch(`${API_BASE}/api/v1x/mentors/payment-methods`, { credentials: 'include' })
      ])

      if (balanceRes.ok) {
        setBalance(await balanceRes.json())
      }
      if (payoutsRes.ok) {
        const data = await payoutsRes.json()
        setPayouts(data.payouts || [])
      }
      if (methodsRes.ok) {
        const data = await methodsRes.json()
        setMethods(data.accounts || [])
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleRequestPayout = async () => {
    if (!payoutAmount || !methods.length) {
      setPayoutError(methods.length === 0 ? 'Please add a payment method first' : 'Enter amount')
      return
    }

    setPayoutSubmitting(true)
    setPayoutError('')
    setPayoutSuccess('')

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
      const res = await fetch(`${API_BASE}/api/v1x/mentors/payouts/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(payoutAmount),
          payment_method: 'bank_transfer'
        }),
        credentials: 'include'
      })

      if (res.ok) {
        const data = await res.json()
        setPayoutSuccess(`Payout request submitted! (ID: #${data.payout_id})`)
        setPayoutAmount('')
        setShowPayoutForm(false)
        loadData() // Refresh data
      } else {
        const data = await res.json()
        setPayoutError(data.detail || 'Failed to request payout')
      }
    } catch (err: any) {
      setPayoutError(err?.message || 'Error submitting payout')
    } finally {
      setPayoutSubmitting(false)
    }
  }

  const handleAddPaymentMethod = async () => {
    if (!methodForm.account_holder_name || !methodForm.account_number || !methodForm.routing_number) {
      setMethodError('Please fill in all fields')
      return
    }

    setMethodSubmitting(true)
    setMethodError('')
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
      const res = await fetch(`${API_BASE}/api/v1x/mentors/payment-methods`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(methodForm),
        credentials: 'include'
      })

      if (res.ok) {
        setShowMethodForm(false)
        setMethodForm({
          account_holder_name: '',
          account_number: '',
          routing_number: '',
          account_type: 'checking',
          country: 'US',
          is_default: false
        })
        loadData() // Refresh payment methods
      } else {
        const data = await res.json()
        setMethodError(data.detail || 'Failed to add payment method')
      }
    } catch (err: any) {
      setMethodError(err?.message || 'Error adding payment method')
    } finally {
      setMethodSubmitting(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout
        title="Payouts & Withdrawals"
        breadcrumbs={[
          { label: 'Dashboard', href: '/mentors/dashboard' },
          { label: 'Payouts' }
        ]}
      >
        <div className="space-y-8">
          <DashboardGridSkeleton count={3} />
          <DashboardListSkeleton count={5} />
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout
      title="Payouts & Withdrawals"
      breadcrumbs={[
        { label: 'Dashboard', href: '/mentors/dashboard' },
        { label: 'Payouts' }
      ]}
    >
      <Head>
        <title>Payouts & Withdrawals – Mentor Dashboard</title>
      </Head>

      <div className="space-y-8">
        {error && (
          <div className="mb-6 bg-red-500/20 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Balance Summary */}
        {balance && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <DashboardStatCard
              label="Available Balance"
              value={`$${balance.available_balance.toFixed(2)}`}
              color="green"
            />
            <DashboardStatCard
              label="Pending Payouts"
              value={`$${balance.pending_payouts.toFixed(2)}`}
              color="purple"
            />
            <DashboardStatCard
              label="Total Earned"
              value={`$${balance.total_earned.toFixed(2)}`}
              color="blue"
            />
          </div>
        )}

        {/* Payment Methods Section */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Payment Methods</h2>
            <button
              onClick={() => setShowMethodForm(!showMethodForm)}
              className="px-4 py-2 bg-forgePurple hover:bg-forgePurple/80 text-white font-medium rounded-lg transition-colors"
            >
              {showMethodForm ? '✕ Close' : '+ Add Method'}
            </button>
          </div>

          {showMethodForm && (
            <div className="bg-white/5 p-6 rounded-lg mb-6 border border-white/10">
              {methodError && (
                <div className="mb-4 bg-red-500/20 border border-red-500/30 text-red-400 px-3 py-2 rounded text-sm">
                  {methodError}
                </div>
              )}
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Account Holder Name"
                  value={methodForm.account_holder_name}
                  onChange={(e) => setMethodForm({...methodForm, account_holder_name: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                />
                <input
                  type="text"
                  placeholder="Account Number"
                  value={methodForm.account_number}
                  onChange={(e) => setMethodForm({...methodForm, account_number: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                />
                <input
                  type="text"
                  placeholder="Routing Number"
                  value={methodForm.routing_number}
                  onChange={(e) => setMethodForm({...methodForm, routing_number: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                />
                <select
                  value={methodForm.account_type}
                  onChange={(e) => setMethodForm({...methodForm, account_type: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-techBlue"
                >
                  <option value="checking">Checking</option>
                  <option value="savings">Savings</option>
                </select>
                <button
                  onClick={handleAddPaymentMethod}
                  disabled={methodSubmitting}
                  className="w-full px-4 py-2 bg-techBlue hover:bg-techBlue/80 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
                >
                  {methodSubmitting ? 'Adding...' : 'Add Payment Method'}
                </button>
              </div>
            </div>
          )}

          {methods.length === 0 ? (
            <div className="text-center py-8 text-techGray">
              <div className="text-4xl mb-3">💳</div>
              <p className="mb-4">No payment methods added yet</p>
              <button
                onClick={() => setShowMethodForm(true)}
                className="px-4 py-2 bg-techBlue text-white rounded-lg hover:bg-techBlue/80"
              >
                Add Your First Method
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {methods.map((method) => (
                <div key={method.id} className="bg-white/5 p-4 rounded-lg border border-white/10 hover:border-techBlue/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-white font-medium">{method.account_holder}</h3>
                        {method.is_default && (
                          <span className="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded">Default</span>
                        )}
                        {!method.verified && (
                          <span className="text-xs bg-yellow-600/20 text-yellow-400 px-2 py-1 rounded">Pending Verification</span>
                        )}
                      </div>
                      <div className="text-sm text-techGray">
                        {method.bank_name} - ****{method.account_number.slice(-4)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-techGray">Added {new Date(method.created_at).toLocaleDateString()}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Request Payout Section */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Request a Payout</h2>
            <button
              onClick={() => setShowPayoutForm(!showPayoutForm)}
              disabled={!balance || balance.available_balance === 0}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
            >
              {showPayoutForm ? '✕ Close' : '💰 Request Withdrawal'}
            </button>
          </div>

          {showPayoutForm && (
            <div className="bg-white/5 p-6 rounded-lg border border-white/10 mb-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-techGray mb-2">Amount ($)</label>
                  <input
                    type="number"
                    min="50"
                    step="0.01"
                    placeholder="500.00"
                    value={payoutAmount}
                    onChange={(e) => setPayoutAmount(e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                  />
                  {balance && (
                    <div className="text-xs text-techGray mt-2">
                      Available: ${balance.available_balance.toFixed(2)} | Minimum: $50
                    </div>
                  )}
                </div>

                {payoutError && (
                  <div className="bg-red-500/20 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-sm">
                    {payoutError}
                  </div>
                )}

                {payoutSuccess && (
                  <div className="bg-green-500/20 border border-green-500/30 text-green-400 px-4 py-3 rounded-lg text-sm">
                    {payoutSuccess}
                  </div>
                )}

                <button
                  onClick={handleRequestPayout}
                  disabled={payoutSubmitting || !payoutAmount}
                  className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
                >
                  {payoutSubmitting ? 'Processing...' : 'Submit Payout Request'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Payout History */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Payout History</h2>

          {payouts.length === 0 ? (
            <div className="text-center py-8 text-techGray">
              <p className="text-4xl mb-3">📋</p>
              <p>No payouts yet. Request your first withdrawal above.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {payouts.map((payout) => (
                <div key={payout.id} className="bg-white/5 p-4 rounded-lg border border-white/10">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <div className="text-white font-medium">Payout #{payout.id}</div>
                      <div className="text-sm text-techGray">
                        {new Date(payout.requested_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-green-400">
                        ${payout.amount.toFixed(2)}
                      </div>
                      <span className={`text-xs px-2 py-1 rounded inline-block ${
                        payout.status === 'completed' ? 'bg-green-600/20 text-green-400'
                        : payout.status === 'processing' ? 'bg-yellow-600/20 text-yellow-400'
                        : payout.status === 'failed' ? 'bg-red-600/20 text-red-400'
                        : 'bg-blue-600/20 text-blue-400'
                      }`}>
                        {payout.status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  {payout.failure_reason && (
                    <div className="text-sm text-red-400 mt-2">Reason: {payout.failure_reason}</div>
                  )}
                  {payout.completed_at && (
                    <div className="text-sm text-techGray mt-2">
                      Completed: {new Date(payout.completed_at).toLocaleDateString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}

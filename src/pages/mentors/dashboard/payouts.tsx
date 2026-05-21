import Head from 'next/head'
import DashboardLayout from '@/components/DashboardLayout'
import DashboardStatCard from '@/components/DashboardStatCard'
import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/router'
import mentorEarningsPageApi from '@/lib/mentorEarningsApi'
import type {
  EarningsSummary,
  PaymentMethod,
  PayoutRequest,
  CreatePaymentMethodRequest,
  CreatePayoutRequestPayload,
} from '@/lib/mentorEarningsApi'

export default function MentorPayouts() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [checkingAuth, setCheckingAuth] = useState(true)

  // Data states
  const [summary, setSummary] = useState<EarningsSummary | null>(null)
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])
  const [payoutRequests, setPayoutRequests] = useState<PayoutRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Payment method form states
  const [showMethodForm, setShowMethodForm] = useState(false)
  const [methodForm, setMethodForm] = useState({
    account_holder_name: '',
    bank_name: '',
    account_number: '',
    routing_number: '',
    is_default: false,
  })
  const [methodSubmitting, setMethodSubmitting] = useState(false)
  const [methodError, setMethodError] = useState('')
  const [methodSuccess, setMethodSuccess] = useState('')

  // Payout request form states
  const [showPayoutForm, setShowPayoutForm] = useState(false)
  const [payoutAmount, setPayoutAmount] = useState('')
  const [selectedPaymentMethodId, setSelectedPaymentMethodId] = useState<number | undefined>()
  const [payoutNotes, setPayoutNotes] = useState('')
  const [payoutSubmitting, setPayoutSubmitting] = useState(false)
  const [payoutError, setPayoutError] = useState('')
  const [payoutSuccess, setPayoutSuccess] = useState('')

  // Load all data
  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await mentorEarningsPageApi.loadAllData()
      setSummary(data.summary)
      setPaymentMethods(data.paymentMethods)
      setPayoutRequests(data.payoutRequests)
      setIsAuthenticated(true)
    } catch (err: any) {
      const errorMsg = err?.message || 'Failed to load earnings data'
      console.error('Error loading data:', err)
      
      // Check if it's an auth error
      if (err?.message?.includes('401') || err?.message?.includes('Unauthorized')) {
        setError('You need to be logged in to access this page.')
        // Redirect to login after 2 seconds
        setTimeout(() => {
          router.push('/auth/login')
        }, 2000)
      } else if (err?.message?.includes('Mentor profile')) {
        setError('You need to have a mentor profile to access earnings.')
      } else {
        setError(errorMsg)
      }
    } finally {
      setLoading(false)
      setCheckingAuth(false)
    }
  }, [router])

  useEffect(() => {
    loadData()
  }, [loadData])

  // Handle add payment method
  const handleAddPaymentMethod = async (e: React.FormEvent) => {
    e.preventDefault()

    if (
      !methodForm.account_holder_name ||
      !methodForm.bank_name ||
      !methodForm.account_number ||
      !methodForm.routing_number
    ) {
      setMethodError('Please fill in all fields')
      return
    }

    setMethodSubmitting(true)
    setMethodError('')
    setMethodSuccess('')

    try {
      const result = await mentorEarningsPageApi.paymentMethods.create(
        methodForm as CreatePaymentMethodRequest
      )

      setMethodSuccess('Payment method added successfully!')
      setMethodForm({
        account_holder_name: '',
        bank_name: '',
        account_number: '',
        routing_number: '',
        is_default: false,
      })
      setShowMethodForm(false)

      // Reload payment methods
      const methods = await mentorEarningsPageApi.paymentMethods.list()
      setPaymentMethods(methods)
    } catch (err: any) {
      setMethodError(err?.message || 'Failed to add payment method')
      console.error('Error adding payment method:', err)
    } finally {
      setMethodSubmitting(false)
    }
  }

  // Handle delete payment method
  const handleDeletePaymentMethod = async (id: number) => {
    if (!confirm('Are you sure you want to delete this payment method?')) return

    try {
      await mentorEarningsPageApi.paymentMethods.delete(id)
      setPaymentMethods(paymentMethods.filter((m) => m.id !== id))
    } catch (err: any) {
      setError(err?.message || 'Failed to delete payment method')
      console.error('Error deleting payment method:', err)
    }
  }

  // Handle set default payment method
  const handleSetDefault = async (id: number) => {
    try {
      await mentorEarningsPageApi.paymentMethods.setDefault(id)
      const methods = await mentorEarningsPageApi.paymentMethods.list()
      setPaymentMethods(methods)
    } catch (err: any) {
      setError(err?.message || 'Failed to set default payment method')
      console.error('Error setting default:', err)
    }
  }

  // Handle request payout
  const handleRequestPayout = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!payoutAmount) {
      setPayoutError('Please enter an amount')
      return
    }

    if (!selectedPaymentMethodId && paymentMethods.length > 0) {
      setPayoutError('Please select a payment method')
      return
    }

    setPayoutSubmitting(true)
    setPayoutError('')
    setPayoutSuccess('')

    try {
      const payload: CreatePayoutRequestPayload = {
        amount: parseFloat(payoutAmount),
        payment_method_id: selectedPaymentMethodId,
        notes: payoutNotes || undefined,
      }

      const result = await mentorEarningsPageApi.payoutRequests.create(payload)

      setPayoutSuccess(`Payout request submitted successfully! ID: #${result.id}`)
      setPayoutAmount('')
      setPayoutNotes('')
      setSelectedPaymentMethodId(undefined)
      setShowPayoutForm(false)

      // Reload payout requests
      const requests = await mentorEarningsPageApi.payoutRequests.history(0, 10)
      setPayoutRequests(requests)
    } catch (err: any) {
      setPayoutError(err?.message || 'Failed to request payout')
      console.error('Error requesting payout:', err)
    } finally {
      setPayoutSubmitting(false)
    }
  }

  if (loading || checkingAuth) {
    return (
      <DashboardLayout
        title="Payouts & Withdrawals"
        breadcrumbs={[
          { label: 'Dashboard', href: '/mentors/dashboard' },
          { label: 'Payouts' },
        ]}
      >
        <div className="space-y-8 animate-pulse">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-white/5 rounded-lg" />
            ))}
          </div>
          <div className="h-64 bg-white/5 rounded-lg" />
        </div>
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout
        title="Payouts & Withdrawals"
        breadcrumbs={[
          { label: 'Dashboard', href: '/mentors/dashboard' },
          { label: 'Payouts' },
        ]}
      >
        <div className="bg-red-500/20 border border-red-500/30 text-red-400 px-6 py-4 rounded-lg">
          <div className="font-semibold mb-2">⚠️ Error Loading Page</div>
          <div className="text-sm">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
          >
            Try Again
          </button>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout
      title="Payouts & Withdrawals"
      breadcrumbs={[
        { label: 'Dashboard', href: '/mentors/dashboard' },
        { label: 'Payouts' },
      ]}
    >
      <Head>
        <title>Payouts & Withdrawals – Mentor Dashboard</title>
      </Head>

      <div className="space-y-8">
        {/* Global Error */}
        {error && (
          <div className="bg-red-500/20 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Balance Summary */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <DashboardStatCard
              label="Available Balance"
              value={`$${summary.available_balance.toFixed(2)}`}
              color="green"
            />
            <DashboardStatCard
              label="Pending Payouts"
              value={`$${summary.pending_payouts.toFixed(2)}`}
              color="purple"
            />
            <DashboardStatCard
              label="Total Earned"
              value={`$${summary.total_earnings.toFixed(2)}`}
              color="blue"
            />
          </div>
        )}

        {/* Payment Methods Section */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Payment Methods</h2>
            <button
              onClick={() => setShowMethodForm(!showMethodForm)}
              className="px-4 py-2 bg-forgePurple hover:bg-forgePurple/80 text-white font-medium rounded-lg transition-colors"
            >
              {showMethodForm ? '✕ Close' : '+ Add Method'}
            </button>
          </div>

          {/* Add Payment Method Form */}
          {showMethodForm && (
            <form onSubmit={handleAddPaymentMethod} className="bg-white/5 p-6 rounded-lg mb-6 border border-white/10">
              {methodError && (
                <div className="mb-4 bg-red-500/20 border border-red-500/30 text-red-400 px-3 py-2 rounded text-sm">
                  {methodError}
                </div>
              )}

              {methodSuccess && (
                <div className="mb-4 bg-green-500/20 border border-green-500/30 text-green-400 px-3 py-2 rounded text-sm">
                  {methodSuccess}
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-techGray mb-2">Account Holder Name</label>
                  <input
                    type="text"
                    placeholder="John Doe"
                    value={methodForm.account_holder_name}
                    onChange={(e) =>
                      setMethodForm({
                        ...methodForm,
                        account_holder_name: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                  />
                </div>

                <div>
                  <label className="block text-sm text-techGray mb-2">Bank Name</label>
                  <input
                    type="text"
                    placeholder="Chase Bank"
                    value={methodForm.bank_name}
                    onChange={(e) =>
                      setMethodForm({ ...methodForm, bank_name: e.target.value })
                    }
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                  />
                </div>

                <div>
                  <label className="block text-sm text-techGray mb-2">Account Number</label>
                  <input
                    type="password"
                    placeholder="••••••••••••••••"
                    value={methodForm.account_number}
                    onChange={(e) =>
                      setMethodForm({
                        ...methodForm,
                        account_number: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                  />
                  <p className="text-xs text-techGray mt-1">Your account number is encrypted</p>
                </div>

                <div>
                  <label className="block text-sm text-techGray mb-2">Routing Number</label>
                  <input
                    type="password"
                    placeholder="•••••••••"
                    value={methodForm.routing_number}
                    onChange={(e) =>
                      setMethodForm({
                        ...methodForm,
                        routing_number: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                  />
                  <p className="text-xs text-techGray mt-1">Your routing number is encrypted</p>
                </div>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={methodForm.is_default}
                    onChange={(e) =>
                      setMethodForm({
                        ...methodForm,
                        is_default: e.target.checked,
                      })
                    }
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-white text-sm">Set as default payment method</span>
                </label>

                <button
                  type="submit"
                  disabled={methodSubmitting}
                  className="w-full px-4 py-2 bg-techBlue hover:bg-techBlue/80 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
                >
                  {methodSubmitting ? 'Adding...' : 'Add Payment Method'}
                </button>
              </div>
            </form>
          )}

          {/* Payment Methods List */}
          {paymentMethods.length === 0 ? (
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
              {paymentMethods.map((method) => (
                <div
                  key={method.id}
                  className="bg-white/5 p-4 rounded-lg border border-white/10 hover:border-techBlue/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-white font-medium">
                          {method.account_holder_name}
                        </h3>
                        {method.is_default && (
                          <span className="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded">
                            Default
                          </span>
                        )}
                        {method.status === 'PENDING' && (
                          <span className="text-xs bg-yellow-600/20 text-yellow-400 px-2 py-1 rounded">
                            Pending Verification
                          </span>
                        )}
                        {method.status === 'VERIFIED' && (
                          <span className="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded">
                            Verified
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-techGray">
                        {method.bank_name} • ••••{method.account_last_four}
                      </div>
                      <div className="text-xs text-techGray mt-1">
                        Added {new Date(method.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {!method.is_default && (
                        <button
                          onClick={() => handleSetDefault(method.id)}
                          className="px-3 py-1 text-xs bg-white/10 hover:bg-white/20 text-white rounded transition-colors"
                        >
                          Set Default
                        </button>
                      )}
                      <button
                        onClick={() => handleDeletePaymentMethod(method.id)}
                        className="px-3 py-1 text-xs bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Request Payout Section */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Request a Payout</h2>
            <button
              onClick={() => setShowPayoutForm(!showPayoutForm)}
              disabled={!summary || summary.available_balance < 10}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
            >
              {showPayoutForm ? '✕ Close' : '💰 Request Withdrawal'}
            </button>
          </div>

          {/* Request Payout Form */}
          {showPayoutForm && (
            <form onSubmit={handleRequestPayout} className="bg-white/5 p-6 rounded-lg border border-white/10 mb-6">
              {payoutError && (
                <div className="mb-4 bg-red-500/20 border border-red-500/30 text-red-400 px-3 py-2 rounded text-sm">
                  {payoutError}
                </div>
              )}

              {payoutSuccess && (
                <div className="mb-4 bg-green-500/20 border border-green-500/30 text-green-400 px-3 py-2 rounded text-sm">
                  {payoutSuccess}
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-techGray mb-2">Amount ($)</label>
                  <input
                    type="number"
                    min="10"
                    max={summary?.available_balance || 0}
                    step="0.01"
                    placeholder="100.00"
                    value={payoutAmount}
                    onChange={(e) => setPayoutAmount(e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                  />
                  {summary && (
                    <div className="text-xs text-techGray mt-2">
                      Available: ${summary.available_balance.toFixed(2)} | Minimum: $10
                    </div>
                  )}
                </div>

                {paymentMethods.length > 0 && (
                  <div>
                    <label className="block text-sm text-techGray mb-2">
                      Payment Method
                    </label>
                    <select
                      value={selectedPaymentMethodId || ''}
                      onChange={(e) =>
                        setSelectedPaymentMethodId(
                          e.target.value ? parseInt(e.target.value) : undefined
                        )
                      }
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-techBlue"
                    >
                      <option value="">
                        {paymentMethods.find((m) => m.is_default)
                          ? 'Select payment method...'
                          : 'Select payment method...'}
                      </option>
                      {paymentMethods.map((method) => (
                        <option key={method.id} value={method.id}>
                          {method.bank_name} • ••••{method.account_last_four}
                          {method.is_default ? ' (Default)' : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                <div>
                  <label className="block text-sm text-techGray mb-2">
                    Notes (Optional)
                  </label>
                  <textarea
                    placeholder="Add any notes about this payout..."
                    value={payoutNotes}
                    onChange={(e) => setPayoutNotes(e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue resize-none"
                    rows={3}
                  />
                </div>

                <button
                  type="submit"
                  disabled={payoutSubmitting || !payoutAmount}
                  className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
                >
                  {payoutSubmitting ? 'Processing...' : 'Submit Payout Request'}
                </button>
              </div>
            </form>
          )}

          {paymentMethods.length === 0 && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 text-yellow-300 p-4 rounded-lg text-sm mb-6">
              ⚠️ Add a payment method first to request payouts
            </div>
          )}
        </div>

        {/* Payout History */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Payout History</h2>

          {payoutRequests.length === 0 ? (
            <div className="text-center py-8 text-techGray">
              <p className="text-4xl mb-3">📋</p>
              <p>No payout requests yet. Request your first withdrawal above.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {payoutRequests.map((payout) => (
                <div
                  key={payout.id}
                  className="bg-white/5 p-4 rounded-lg border border-white/10"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <div className="text-white font-medium">Payout Request #{payout.id}</div>
                      <div className="text-sm text-techGray">
                        {new Date(payout.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-green-400">
                        ${(payout.amount / 100).toFixed(2)}
                      </div>
                      <span
                        className={`text-xs px-2 py-1 rounded inline-block ${
                          payout.status === 'COMPLETED'
                            ? 'bg-green-600/20 text-green-400'
                            : payout.status === 'PROCESSING'
                            ? 'bg-blue-600/20 text-blue-400'
                            : payout.status === 'REJECTED'
                            ? 'bg-red-600/20 text-red-400'
                            : 'bg-yellow-600/20 text-yellow-400'
                        }`}
                      >
                        {payout.status}
                      </span>
                    </div>
                  </div>
                  {payout.rejection_reason && (
                    <div className="text-sm text-red-400 mt-2">
                      Reason: {payout.rejection_reason}
                    </div>
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


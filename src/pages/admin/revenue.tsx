import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useState, useEffect } from 'react'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'

type RevenueOverview = {
  timeframe: string
  total_revenue: number
  session_revenue: number
  subscription_revenue: number
  session_count: number
  avg_transaction_value: number
  active_subscriptions: number
  monthly_recurring_revenue: number
  mentor_payouts: number
  platform_revenue: number
}

type Transaction = {
  id: number
  date: string
  amount: number
  mentor_email: string
  student_email: string
  duration_minutes: number
  payment_intent_id: string
  status: string
}

type MentorEarnings = {
  mentor_id: number
  email: string
  total_earnings: number
  mentor_payout: number
  platform_fee: number
  session_count: number
  avg_rating: number | null
}

export default function AdminRevenue({ me }: AdminSSRProps) {
  const [overview, setOverview] = useState<RevenueOverview | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [mentorEarnings, setMentorEarnings] = useState<MentorEarnings[]>([])
  const [timeframe, setTimeframe] = useState<'7d' | '30d' | '90d' | '1y' | 'all'>('30d')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRevenue()
  }, [timeframe])

  async function loadRevenue() {
    setLoading(true)
    try {
      const [overviewRes, transactionsRes, earningsRes] = await Promise.all([
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/revenue/overview?timeframe=${timeframe}`,
          { credentials: 'include' }
        ),
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/revenue/transactions?limit=20`,
          { credentials: 'include' }
        ),
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/revenue/mentor-earnings?timeframe=${timeframe}&limit=10`,
          { credentials: 'include' }
        )
      ])

      if (overviewRes.ok) {
        const data = await overviewRes.json()
        setOverview(data)
      }

      if (transactionsRes.ok) {
        const data = await transactionsRes.json()
        setTransactions(data.transactions || [])
      }

      if (earningsRes.ok) {
        const data = await earningsRes.json()
        setMentorEarnings(data.mentors || [])
      }
    } catch (err) {
      console.error('Failed to load revenue data:', err)
    } finally {
      setLoading(false)
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
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  function exportTransactionsCSV() {
    const headers = ['ID', 'Date', 'Amount', 'Mentor', 'Student', 'Duration (min)', 'Payment ID', 'Status']
    const rows = transactions.map(t => [
      t.id,
      t.date,
      t.amount,
      t.mentor_email,
      t.student_email,
      t.duration_minutes,
      t.payment_intent_id || 'N/A',
      t.status
    ])

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transactions_${timeframe}_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <Layout>
      <Head>
        <title>Revenue & Payments – Admin – SkillForge Global</title>
      </Head>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Revenue & Payments Dashboard</h1>
          <p className="text-techGray">Financial analytics and transaction management</p>
        </div>

        {/* Timeframe Selector */}
        <div className="mb-6 flex gap-2">
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
              {tf === '7d' && 'Last 7 Days'}
              {tf === '30d' && 'Last 30 Days'}
              {tf === '90d' && 'Last 90 Days'}
              {tf === '1y' && 'Last Year'}
              {tf === 'all' && 'All Time'}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400">
            Loading revenue data...
          </div>
        ) : !overview ? (
          <div className="text-center py-12">
            <div className="rounded-xl border border-yellow-500/30 p-6 bg-yellow-500/10 inline-block">
              <p className="text-yellow-300">Revenue data not available</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Revenue Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <MetricCard
                title="Total Revenue"
                value={formatCurrency(overview.total_revenue)}
                subtitle={`${timeframe.toUpperCase()}`}
                icon="💰"
              />
              <MetricCard
                title="Platform Revenue"
                value={formatCurrency(overview.platform_revenue)}
                subtitle="30% commission"
                icon="🏢"
              />
              <MetricCard
                title="Mentor Payouts"
                value={formatCurrency(overview.mentor_payouts)}
                subtitle="70% of session revenue"
                icon="👨‍🏫"
              />
              <MetricCard
                title="Session Count"
                value={overview.session_count.toString()}
                subtitle={`Avg: ${formatCurrency(overview.avg_transaction_value)}`}
                icon="📅"
              />
            </div>

            {/* Subscription Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <MetricCard
                title="Active Subscriptions"
                value={overview.active_subscriptions.toString()}
                subtitle="Current subscribers"
                icon="⭐"
              />
              <MetricCard
                title="Monthly Recurring Revenue"
                value={formatCurrency(overview.monthly_recurring_revenue)}
                subtitle="MRR"
                icon="📈"
              />
              <MetricCard
                title="Subscription Revenue"
                value={formatCurrency(overview.subscription_revenue)}
                subtitle={`${timeframe.toUpperCase()}`}
                icon="💳"
              />
            </div>

            {/* Top Earning Mentors */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Top Earning Mentors</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-400 border-b border-white/10">
                      <th className="pb-3">Rank</th>
                      <th className="pb-3">Mentor</th>
                      <th className="pb-3">Sessions</th>
                      <th className="pb-3">Total Revenue</th>
                      <th className="pb-3">Mentor Payout</th>
                      <th className="pb-3">Platform Fee</th>
                      <th className="pb-3">Rating</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mentorEarnings.map((mentor, idx) => (
                      <tr key={mentor.mentor_id} className="border-b border-white/5 last:border-0">
                        <td className="py-3 text-gray-300">#{idx + 1}</td>
                        <td className="py-3 text-white">{mentor.email}</td>
                        <td className="py-3 text-gray-300">{mentor.session_count}</td>
                        <td className="py-3 text-green-400 font-medium">
                          {formatCurrency(mentor.total_earnings)}
                        </td>
                        <td className="py-3 text-blue-400">
                          {formatCurrency(mentor.mentor_payout)}
                        </td>
                        <td className="py-3 text-purple-400">
                          {formatCurrency(mentor.platform_fee)}
                        </td>
                        <td className="py-3 text-yellow-400">
                          {mentor.avg_rating ? `⭐ ${mentor.avg_rating.toFixed(1)}` : 'N/A'}
                        </td>
                      </tr>
                    ))}
                    {mentorEarnings.length === 0 && (
                      <tr>
                        <td colSpan={7} className="py-6 text-center text-gray-400">
                          No mentor earnings data available
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Recent Transactions */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white">Recent Transactions</h2>
                <button
                  onClick={exportTransactionsCSV}
                  disabled={transactions.length === 0}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors"
                >
                  📥 Export CSV
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-400 border-b border-white/10">
                      <th className="pb-3">ID</th>
                      <th className="pb-3">Date</th>
                      <th className="pb-3">Amount</th>
                      <th className="pb-3">Mentor</th>
                      <th className="pb-3">Student</th>
                      <th className="pb-3">Duration</th>
                      <th className="pb-3">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((txn) => (
                      <tr key={txn.id} className="border-b border-white/5 last:border-0">
                        <td className="py-3 text-gray-400 font-mono text-sm">#{txn.id}</td>
                        <td className="py-3 text-gray-300 text-sm">
                          {txn.date ? formatDate(txn.date) : 'N/A'}
                        </td>
                        <td className="py-3 text-green-400 font-medium">
                          {formatCurrency(txn.amount)}
                        </td>
                        <td className="py-3 text-white text-sm">{txn.mentor_email}</td>
                        <td className="py-3 text-gray-300 text-sm">{txn.student_email}</td>
                        <td className="py-3 text-gray-400">{txn.duration_minutes} min</td>
                        <td className="py-3">
                          <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-300">
                            {txn.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {transactions.length === 0 && (
                      <tr>
                        <td colSpan={7} className="py-6 text-center text-gray-400">
                          No transactions found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Revenue Breakdown Chart Placeholder */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Revenue Breakdown</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-4 rounded-lg bg-white/5">
                    <div>
                      <p className="text-sm text-gray-400">Session Revenue</p>
                      <p className="text-2xl font-bold text-white">
                        {formatCurrency(overview.session_revenue)}
                      </p>
                    </div>
                    <div className="text-4xl">💼</div>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg bg-white/5">
                    <div>
                      <p className="text-sm text-gray-400">Subscription Revenue</p>
                      <p className="text-2xl font-bold text-white">
                        {formatCurrency(overview.subscription_revenue)}
                      </p>
                    </div>
                    <div className="text-4xl">🎫</div>
                  </div>
                </div>
                <div className="flex items-center justify-center border border-dashed border-white/20 rounded-lg">
                  <div className="text-center">
                    <p className="text-gray-400">📊 Revenue Chart</p>
                    <p className="text-sm text-gray-500 mt-2">Coming soon with charting library</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

function MetricCard({
  title,
  value,
  subtitle,
  icon
}: {
  title: string
  value: string
  subtitle?: string
  icon?: string
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-6">
      <div className="flex items-start justify-between mb-2">
        <p className="text-sm text-gray-400">{title}</p>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
      <p className="text-3xl font-bold text-white mb-1">{value}</p>
      {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
    </div>
  )
}

export const getServerSideProps = requireAdminSSR

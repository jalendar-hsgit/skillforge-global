import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'

type EarningsData = {
  total_earnings: number
  this_month: number
  last_month: number
  pending_payout: number
  monthly_breakdown: Array<{ month: string; amount: number }>
  top_students: Array<{ student_id: number; amount: number; session_count: number }>
}

export default function MentorEarnings() {
  const router = useRouter()
  const [data, setData] = useState<EarningsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadEarnings()
  }, [])

  async function loadEarnings() {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/mentor-portal/dashboard/earnings`,
        { credentials: 'include' }
      )

      if (res.status === 401) {
        router.push('/login?redirect=/mentors/dashboard/earnings')
        return
      }

      if (res.ok) {
        const earnings = await res.json()
        setData(earnings)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <Head><title>Earnings – Mentor Dashboard</title></Head>
        <AdminHeader title="My Earnings" backUrl="/mentors/dashboard" />
        <div className="container mx-auto px-4 py-8 text-center text-techGray">
          Loading earnings...
        </div>
      </Layout>
    )
  }

  if (!data) {
    return (
      <Layout>
        <Head><title>Earnings – Mentor Dashboard</title></Head>
        <AdminHeader title="My Earnings" backUrl="/mentors/dashboard" />
        <div className="container mx-auto px-4 py-8 text-center text-red-400">
          Failed to load earnings data
        </div>
      </Layout>
    )
  }

  const monthChange = data.last_month > 0
    ? ((data.this_month - data.last_month) / data.last_month) * 100
    : 0

  return (
    <Layout>
      <Head>
        <title>Earnings – Mentor Dashboard</title>
      </Head>

      <AdminHeader title="My Earnings" backUrl="/mentors/dashboard" />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 border border-green-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">Total Earnings</div>
            <div className="text-3xl font-bold text-white mb-1">
              ${data.total_earnings.toFixed(2)}
            </div>
            <div className="text-xs text-green-400">All time</div>
          </div>

          <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">This Month</div>
            <div className="text-3xl font-bold text-white mb-1">
              ${data.this_month.toFixed(2)}
            </div>
            <div className={`text-xs ${monthChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {monthChange >= 0 ? '↑' : '↓'} {Math.abs(monthChange).toFixed(1)}% vs last month
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 border border-purple-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">Last Month</div>
            <div className="text-3xl font-bold text-white mb-1">
              ${data.last_month.toFixed(2)}
            </div>
            <div className="text-xs text-techGray">Previous period</div>
          </div>

          <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 border border-yellow-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">Pending Payout</div>
            <div className="text-3xl font-bold text-white mb-1">
              ${data.pending_payout.toFixed(2)}
            </div>
            <div className="text-xs text-yellow-400">Available soon</div>
          </div>
        </div>

        {/* Monthly Chart */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-6">Monthly Breakdown</h2>
          {data.monthly_breakdown.length === 0 ? (
            <div className="text-center py-8 text-techGray">No monthly data yet</div>
          ) : (
            <div className="space-y-3">
              {data.monthly_breakdown.map((item, idx) => {
                const maxAmount = Math.max(...data.monthly_breakdown.map(d => d.amount))
                const widthPercent = maxAmount > 0 ? (item.amount / maxAmount) * 100 : 0

                return (
                  <div key={idx}>
                    <div className="flex justify-between mb-1 text-sm">
                      <span className="text-techGray">{item.month}</span>
                      <span className="text-white font-medium">${item.amount.toFixed(2)}</span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-techBlue to-forgePurple h-full transition-all duration-500"
                        style={{ width: `${widthPercent}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Top Students */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-6">Top Students by Revenue</h2>
          {data.top_students.length === 0 ? (
            <div className="text-center py-8 text-techGray">
              No student data yet
            </div>
          ) : (
            <div className="space-y-3">
              {data.top_students.map((student, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-lg hover:border-techBlue/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-techBlue to-forgePurple flex items-center justify-center text-white font-bold">
                      #{idx + 1}
                    </div>
                    <div>
                      <div className="text-white font-medium">Student #{student.student_id}</div>
                      <div className="text-sm text-techGray">
                        {student.session_count} session{student.session_count !== 1 ? 's' : ''}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold text-white">
                      ${student.amount.toFixed(2)}
                    </div>
                    <div className="text-xs text-techGray">Total revenue</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

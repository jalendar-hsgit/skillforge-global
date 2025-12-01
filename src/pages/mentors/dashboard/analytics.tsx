import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'

type AnalyticsData = {
  total_sessions: number
  sessions_by_status: { [key: string]: number }
  rating_distribution: { [key: string]: number }
  sessions_by_day: Array<{ day: string; count: number }>
}

export default function MentorAnalytics() {
  const router = useRouter()
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  async function loadAnalytics() {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/mentor-portal/dashboard/analytics`,
        { credentials: 'include' }
      )

      if (res.status === 401) {
        router.push('/login?redirect=/mentors/dashboard/analytics')
        return
      }

      if (res.ok) {
        const analytics = await res.json()
        setData(analytics)
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
        <Head><title>Analytics – Mentor Dashboard</title></Head>
        <AdminHeader title="Performance Analytics" backUrl="/mentors/dashboard" />
        <div className="container mx-auto px-4 py-8 text-center text-techGray">
          Loading analytics...
        </div>
      </Layout>
    )
  }

  if (!data) {
    return (
      <Layout>
        <Head><title>Analytics – Mentor Dashboard</title></Head>
        <AdminHeader title="Performance Analytics" backUrl="/mentors/dashboard" />
        <div className="container mx-auto px-4 py-8 text-center text-red-400">
          Failed to load analytics
        </div>
      </Layout>
    )
  }

  const statusColors: { [key: string]: string } = {
    pending: 'bg-yellow-500',
    confirmed: 'bg-green-500',
    completed: 'bg-blue-500',
    cancelled: 'bg-red-500',
  }

  return (
    <Layout>
      <Head>
        <title>Analytics – Mentor Dashboard</title>
      </Head>

      <AdminHeader title="Performance Analytics" backUrl="/mentors/dashboard" />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">Total Sessions</div>
            <div className="text-4xl font-bold text-white mb-1">{data.total_sessions}</div>
            <div className="text-xs text-techGray">All time</div>
          </div>

          <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 border border-green-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">Completed</div>
            <div className="text-4xl font-bold text-white mb-1">
              {data.sessions_by_status.completed || 0}
            </div>
            <div className="text-xs text-green-400">
              {data.total_sessions > 0
                ? ((data.sessions_by_status.completed / data.total_sessions) * 100).toFixed(0)
                : 0}% completion rate
            </div>
          </div>

          <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 border border-yellow-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">Pending</div>
            <div className="text-4xl font-bold text-white mb-1">
              {data.sessions_by_status.pending || 0}
            </div>
            <div className="text-xs text-techGray">Awaiting confirmation</div>
          </div>

          <div className="bg-gradient-to-br from-red-500/20 to-red-600/20 border border-red-500/30 rounded-xl p-6">
            <div className="text-techGray text-sm mb-2">Cancelled</div>
            <div className="text-4xl font-bold text-white mb-1">
              {data.sessions_by_status.cancelled || 0}
            </div>
            <div className="text-xs text-red-400">
              {data.total_sessions > 0
                ? ((data.sessions_by_status.cancelled / data.total_sessions) * 100).toFixed(0)
                : 0}% cancellation rate
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Session Status Breakdown */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-6">Sessions by Status</h2>
            <div className="space-y-4">
              {Object.entries(data.sessions_by_status).map(([status, count]) => {
                const percentage = data.total_sessions > 0 ? (count / data.total_sessions) * 100 : 0
                return (
                  <div key={status}>
                    <div className="flex justify-between mb-2">
                      <span className="text-white capitalize">{status}</span>
                      <span className="text-techGray">{count} ({percentage.toFixed(0)}%)</span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                      <div
                        className={`${statusColors[status] || 'bg-gray-500'} h-full transition-all duration-500`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Rating Distribution */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-6">Rating Distribution</h2>
            {Object.keys(data.rating_distribution).length === 0 ? (
              <div className="text-center py-8 text-techGray">No ratings yet</div>
            ) : (
              <div className="space-y-4">
                {Object.entries(data.rating_distribution)
                  .sort(([a], [b]) => Number(b) - Number(a))
                  .map(([rating, count]) => {
                    const totalRatings = Object.values(data.rating_distribution).reduce((a, b) => a + b, 0)
                    const percentage = totalRatings > 0 ? (count / totalRatings) * 100 : 0
                    return (
                      <div key={rating}>
                        <div className="flex justify-between mb-2">
                          <span className="text-white">{rating} ⭐</span>
                          <span className="text-techGray">{count} ({percentage.toFixed(0)}%)</span>
                        </div>
                        <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-yellow-500 to-yellow-600 h-full transition-all duration-500"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    )
                  })}
              </div>
            )}
          </div>
        </div>

        {/* Sessions by Day */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 mt-8">
          <h2 className="text-xl font-bold text-white mb-6">Sessions by Day (Last 7 Days)</h2>
          {data.sessions_by_day.length === 0 ? (
            <div className="text-center py-8 text-techGray">No session data yet</div>
          ) : (
            <div className="space-y-3">
              {data.sessions_by_day.map((item, idx) => {
                const maxCount = Math.max(...data.sessions_by_day.map(d => d.count))
                const widthPercent = maxCount > 0 ? (item.count / maxCount) * 100 : 0

                return (
                  <div key={idx}>
                    <div className="flex justify-between mb-1 text-sm">
                      <span className="text-techGray">{item.day}</span>
                      <span className="text-white font-medium">{item.count} sessions</span>
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
      </div>
    </Layout>
  )
}

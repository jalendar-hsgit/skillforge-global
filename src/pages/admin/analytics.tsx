import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useState, useEffect } from 'react'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'

type AnalyticsData = {
  user_growth: { date: string; count: number }[]
  revenue_trend: { date: string; amount: number }[]
  session_stats: {
    total: number
    completed: number
    cancelled: number
    completion_rate: number
  }
  top_mentors: {
    id: number
    email: string
    total_sessions: number
    avg_rating: number
    total_earnings: number
  }[]
  popular_courses: {
    slug: string
    title: string
    enrollments: number
    completion_rate: number
  }[]
}

export default function AdminAnalytics({ me }: AdminSSRProps) {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [timeframe, setTimeframe] = useState<'7d' | '30d' | '90d' | '1y'>('30d')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [timeframe])

  async function loadAnalytics() {
    setLoading(true)
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/analytics?timeframe=${timeframe}`,
        { credentials: 'include' }
      )

      if (res.ok) {
        const data = await res.json()
        setAnalytics(data)
      }
    } catch (err) {
      console.error('Failed to load analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <Head>
        <title>Analytics – Admin – SkillForge Global</title>
      </Head>

      <AdminHeader 
        title="Analytics" 
        backUrl="/admin"
        actions={
          <div className="flex gap-2">
            {(['7d', '30d', '90d', '1y'] as const).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  timeframe === tf
                    ? 'bg-forgePurple text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {tf === '7d' ? '7 Days' : tf === '30d' ? '30 Days' : tf === '90d' ? '90 Days' : '1 Year'}
              </button>
            ))}
          </div>
        }
      />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Timeframe Selector - Moved to header */}
        <div className="mb-6 flex gap-2">
          {(['7d', '30d', '90d', '1y'] as const).map((tf) => (
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
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400">
            Loading analytics...
          </div>
        ) : !analytics ? (
          <div className="text-center py-12">
            <div className="rounded-xl border border-yellow-500/30 p-6 bg-yellow-500/10 inline-block">
              <p className="text-yellow-300">Analytics data not available</p>
              <p className="text-sm text-yellow-200/60 mt-2">
                This feature is coming soon
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <MetricCard
                title="Session Completion"
                value={`${analytics.session_stats.completion_rate.toFixed(1)}%`}
                change="+5.2%"
                positive={true}
              />
              <MetricCard
                title="Total Sessions"
                value={analytics.session_stats.total.toString()}
                subtitle={`${analytics.session_stats.completed} completed`}
              />
              <MetricCard
                title="Active Mentors"
                value={analytics.top_mentors.length.toString()}
                subtitle="This period"
              />
              <MetricCard
                title="Total Revenue"
                value="Coming Soon"
                subtitle="Feature in progress"
              />
            </div>

            {/* Charts Placeholder */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ChartPlaceholder title="User Growth" />
              <ChartPlaceholder title="Revenue Trend" />
            </div>

            {/* Top Mentors Table */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Top Performing Mentors</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-400 border-b border-white/10">
                      <th className="pb-3">Mentor</th>
                      <th className="pb-3">Sessions</th>
                      <th className="pb-3">Avg Rating</th>
                      <th className="pb-3">Earnings</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.top_mentors.map((mentor, idx) => (
                      <tr key={mentor.id} className="border-b border-white/5 last:border-0">
                        <td className="py-3 text-white">{mentor.email}</td>
                        <td className="py-3 text-gray-300">{mentor.total_sessions}</td>
                        <td className="py-3 text-gray-300">
                          ⭐ {mentor.avg_rating?.toFixed(1) || 'N/A'}
                        </td>
                        <td className="py-3 text-green-400">
                          ${mentor.total_earnings?.toFixed(2) || '0.00'}
                        </td>
                      </tr>
                    ))}
                    {analytics.top_mentors.length === 0 && (
                      <tr>
                        <td colSpan={4} className="py-6 text-center text-gray-400">
                          No mentor data available
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Popular Courses */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Popular Courses</h2>
              <div className="space-y-3">
                {analytics.popular_courses.map((course, idx) => (
                  <div
                    key={course.slug}
                    className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                  >
                    <div>
                      <p className="text-white font-medium">{course.title}</p>
                      <p className="text-sm text-gray-400">
                        {course.enrollments} enrollments • {course.completion_rate}% completion
                      </p>
                    </div>
                    <span className="text-2xl">#{idx + 1}</span>
                  </div>
                ))}
                {analytics.popular_courses.length === 0 && (
                  <p className="text-center py-6 text-gray-400">
                    No course data available
                  </p>
                )}
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
  change,
  positive,
}: {
  title: string
  value: string
  subtitle?: string
  change?: string
  positive?: boolean
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-6">
      <p className="text-sm text-gray-400 mb-2">{title}</p>
      <p className="text-3xl font-bold text-white mb-1">{value}</p>
      {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
      {change && (
        <p className={`text-sm mt-2 ${positive ? 'text-green-400' : 'text-red-400'}`}>
          {change}
        </p>
      )}
    </div>
  )
}

function ChartPlaceholder({ title }: { title: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-6">
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      <div className="h-64 flex items-center justify-center border border-dashed border-white/20 rounded-lg">
        <div className="text-center">
          <p className="text-gray-400">📊 Chart Visualization</p>
          <p className="text-sm text-gray-500 mt-2">Coming soon with charting library</p>
        </div>
      </div>
    </div>
  )
}

export const getServerSideProps = requireAdminSSR

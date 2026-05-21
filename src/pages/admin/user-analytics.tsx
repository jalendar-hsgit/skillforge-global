import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'

type AnalyticsOverview = {
  timeframe: string
  total_users: number
  new_users: number
  growth_rate: number
  dau: number
  wau: number
  mau: number
  engagement_rate: number
  active_users_with_sessions: number
  role_distribution: Record<string, number>
}

type Cohort = {
  cohort_month: string
  cohort_size: number
  active_users: number
  retention_rate: number
}

type ActivityStats = {
  timeframe: string
  segments: {
    highly_active: number
    purchasers: number
    mentors: number
    inactive: number
  }
  total_users: number
}

type PopularContent = {
  timeframe: string
  popular_mentors: Array<{
    mentor_id: number
    email: string
    bookings: number
    avg_rating: number | null
  }>
  popular_courses: Array<{
    course_id: number
    title: string
    purchases: number
  }>
}

type ChurnRiskUser = {
  user_id: number
  email: string
  role: string
  days_since_signup: number
  last_activity: string
  risk_level: string
}

export default function AdminUserAnalytics({ me }: AdminSSRProps) {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null)
  const [cohorts, setCohorts] = useState<Cohort[]>([])
  const [activity, setActivity] = useState<ActivityStats | null>(null)
  const [popularContent, setPopularContent] = useState<PopularContent | null>(null)
  const [churnRisk, setChurnRisk] = useState<ChurnRiskUser[]>([])
  const [timeframe, setTimeframe] = useState<'7d' | '30d' | '90d' | '1y'>('30d')
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'cohorts' | 'activity' | 'churn'>('overview')

  useEffect(() => {
    loadAnalytics()
  }, [timeframe])

  async function loadAnalytics() {
    setLoading(true)
    try {
      const [overviewRes, cohortsRes, activityRes, contentRes, churnRes] = await Promise.all([
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/user-analytics/overview?timeframe=${timeframe}`,
          { credentials: 'include' }
        ),
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/user-analytics/cohorts`,
          { credentials: 'include' }
        ),
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/user-analytics/activity?timeframe=${timeframe}`,
          { credentials: 'include' }
        ),
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/user-analytics/popular-content?timeframe=${timeframe}`,
          { credentials: 'include' }
        ),
        fetch(
          `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/user-analytics/churn-risk`,
          { credentials: 'include' }
        )
      ])

      if (overviewRes.ok) {
        const data = await overviewRes.json()
        setOverview(data)
      }

      if (cohortsRes.ok) {
        const data = await cohortsRes.json()
        setCohorts(data.cohorts || [])
      }

      if (activityRes.ok) {
        const data = await activityRes.json()
        setActivity(data)
      }

      if (contentRes.ok) {
        const data = await contentRes.json()
        setPopularContent(data)
      }

      if (churnRes.ok) {
        const data = await churnRes.json()
        setChurnRisk(data.users || [])
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
        <title>User Analytics – Admin – SkillForge Global</title>
      </Head>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">User Analytics & Engagement</h1>
          <p className="text-techGray">Retention, activity patterns, and user behavior insights</p>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-2 border-b border-white/10">
          {(['overview', 'cohorts', 'activity', 'churn'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === tab
                  ? 'text-white border-b-2 border-forgePurple'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              {tab === 'overview' && 'Overview'}
              {tab === 'cohorts' && 'Cohorts'}
              {tab === 'activity' && 'Activity'}
              {tab === 'churn' && 'Churn Risk'}
            </button>
          ))}
        </div>

        {/* Timeframe Selector */}
        {activeTab !== 'cohorts' && activeTab !== 'churn' && (
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
        )}

        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading analytics...</div>
        ) : (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && overview && (
              <div className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <MetricCard
                    title="Total Users"
                    value={overview.total_users.toLocaleString()}
                    subtitle={`+${overview.new_users} new`}
                    icon="👥"
                  />
                  <MetricCard
                    title="Growth Rate"
                    value={`${overview.growth_rate > 0 ? '+' : ''}${overview.growth_rate.toFixed(1)}%`}
                    subtitle={timeframe.toUpperCase()}
                    icon="📈"
                    positive={overview.growth_rate > 0}
                  />
                  <MetricCard
                    title="Engagement Rate"
                    value={`${overview.engagement_rate.toFixed(1)}%`}
                    subtitle="Active users"
                    icon="⚡"
                  />
                  <MetricCard
                    title="Active Users"
                    value={overview.active_users_with_sessions.toString()}
                    subtitle="With sessions"
                    icon="🎯"
                  />
                </div>

                {/* DAU/WAU/MAU */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <MetricCard title="DAU" value={overview.dau.toString()} subtitle="Daily Active Users" icon="📅" />
                  <MetricCard title="WAU" value={overview.wau.toString()} subtitle="Weekly Active Users" icon="📊" />
                  <MetricCard title="MAU" value={overview.mau.toString()} subtitle="Monthly Active Users" icon="📈" />
                </div>

                {/* Role Distribution */}
                <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                  <h2 className="text-xl font-bold text-white mb-4">User Role Distribution</h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(overview.role_distribution).map(([role, count]) => (
                      <div key={role} className="p-4 rounded-lg bg-white/5">
                        <p className="text-sm text-gray-400 mb-1">{role}</p>
                        <p className="text-2xl font-bold text-white">{count}</p>
                        <p className="text-xs text-gray-500">
                          {((count / overview.total_users) * 100).toFixed(1)}%
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Popular Content */}
                {popularContent && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Popular Mentors */}
                    <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                      <h2 className="text-xl font-bold text-white mb-4">Most Booked Mentors</h2>
                      <div className="space-y-2">
                        {popularContent.popular_mentors.slice(0, 5).map((mentor, idx) => (
                          <div
                            key={mentor.mentor_id}
                            className="flex items-center justify-between p-3 rounded-lg bg-white/5"
                          >
                            <div className="flex items-center gap-3">
                              <span className="text-lg font-bold text-gray-400">#{idx + 1}</span>
                              <div>
                                <p className="text-white text-sm">{mentor.email}</p>
                                <p className="text-xs text-gray-400">
                                  {mentor.bookings} bookings
                                  {mentor.avg_rating && ` • ⭐ ${mentor.avg_rating.toFixed(1)}`}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Popular Courses */}
                    <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                      <h2 className="text-xl font-bold text-white mb-4">Most Purchased Courses</h2>
                      <div className="space-y-2">
                        {popularContent.popular_courses.length > 0 ? (
                          popularContent.popular_courses.slice(0, 5).map((course, idx) => (
                            <div
                              key={course.course_id}
                              className="flex items-center justify-between p-3 rounded-lg bg-white/5"
                            >
                              <div className="flex items-center gap-3">
                                <span className="text-lg font-bold text-gray-400">#{idx + 1}</span>
                                <div>
                                  <p className="text-white text-sm">{course.title}</p>
                                  <p className="text-xs text-gray-400">{course.purchases} purchases</p>
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-center py-4 text-gray-400">No purchase data available</p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Cohorts Tab */}
            {activeTab === 'cohorts' && (
              <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                <h2 className="text-xl font-bold text-white mb-4">Retention Cohort Analysis</h2>
                <p className="text-gray-400 mb-6">
                  Shows retention rates for users by signup month
                </p>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-sm text-gray-400 border-b border-white/10">
                        <th className="p-4">Cohort Month</th>
                        <th className="p-4">Cohort Size</th>
                        <th className="p-4">Active Users</th>
                        <th className="p-4">Retention Rate</th>
                        <th className="p-4">Visual</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cohorts.map((cohort) => (
                        <tr key={cohort.cohort_month} className="border-b border-white/5">
                          <td className="p-4 text-white font-medium">{cohort.cohort_month}</td>
                          <td className="p-4 text-gray-300">{cohort.cohort_size}</td>
                          <td className="p-4 text-blue-400">{cohort.active_users}</td>
                          <td className="p-4 text-green-400 font-bold">
                            {cohort.retention_rate.toFixed(1)}%
                          </td>
                          <td className="p-4">
                            <div className="w-full bg-white/10 rounded-full h-2">
                              <div
                                className="bg-forgePurple h-2 rounded-full"
                                style={{ width: `${cohort.retention_rate}%` }}
                              />
                            </div>
                          </td>
                        </tr>
                      ))}
                      {cohorts.length === 0 && (
                        <tr>
                          <td colSpan={5} className="py-12 text-center text-gray-400">
                            No cohort data available
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Activity Tab */}
            {activeTab === 'activity' && activity && (
              <div className="space-y-6">
                <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                  <h2 className="text-xl font-bold text-white mb-6">User Segmentation</h2>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <SegmentCard
                      title="Highly Active"
                      count={activity.segments.highly_active}
                      total={activity.total_users}
                      color="green"
                      icon="🔥"
                    />
                    <SegmentCard
                      title="Purchasers"
                      count={activity.segments.purchasers}
                      total={activity.total_users}
                      color="purple"
                      icon="💳"
                    />
                    <SegmentCard
                      title="Active Mentors"
                      count={activity.segments.mentors}
                      total={activity.total_users}
                      color="blue"
                      icon="🎓"
                    />
                    <SegmentCard
                      title="Inactive"
                      count={activity.segments.inactive}
                      total={activity.total_users}
                      color="gray"
                      icon="😴"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Churn Risk Tab */}
            {activeTab === 'churn' && (
              <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                <h2 className="text-xl font-bold text-white mb-4">
                  Users at Risk of Churning ({churnRisk.length})
                </h2>
                <p className="text-gray-400 mb-6">
                  Users who signed up 30+ days ago but have no activity in the last 14 days
                </p>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-sm text-gray-400 border-b border-white/10">
                        <th className="p-4">Email</th>
                        <th className="p-4">Role</th>
                        <th className="p-4">Days Since Signup</th>
                        <th className="p-4">Last Activity</th>
                        <th className="p-4">Risk Level</th>
                      </tr>
                    </thead>
                    <tbody>
                      {churnRisk.map((user) => (
                        <tr key={user.user_id} className="border-b border-white/5">
                          <td className="p-4 text-white">{user.email}</td>
                          <td className="p-4 text-gray-300">{user.role}</td>
                          <td className="p-4 text-gray-400">{user.days_since_signup} days</td>
                          <td className="p-4 text-gray-400">{user.last_activity}</td>
                          <td className="p-4">
                            <span
                              className={`text-xs px-2 py-1 rounded-full ${
                                user.risk_level === 'high'
                                  ? 'bg-red-500/20 text-red-300'
                                  : 'bg-yellow-500/20 text-yellow-300'
                              }`}
                            >
                              {user.risk_level}
                            </span>
                          </td>
                        </tr>
                      ))}
                      {churnRisk.length === 0 && (
                        <tr>
                          <td colSpan={5} className="py-12 text-center text-gray-400">
                            No at-risk users identified
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  )
}

function MetricCard({
  title,
  value,
  subtitle,
  icon,
  positive
}: {
  title: string
  value: string
  subtitle?: string
  icon?: string
  positive?: boolean
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-6">
      <div className="flex items-start justify-between mb-2">
        <p className="text-sm text-gray-400">{title}</p>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
      <p className={`text-3xl font-bold mb-1 ${
        positive !== undefined
          ? positive
            ? 'text-green-400'
            : 'text-red-400'
          : 'text-white'
      }`}>
        {value}
      </p>
      {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
    </div>
  )
}

function SegmentCard({
  title,
  count,
  total,
  color,
  icon
}: {
  title: string
  count: number
  total: number
  color: string
  icon: string
}) {
  const percentage = ((count / total) * 100).toFixed(1)
  
  const colorClasses = {
    green: 'border-green-500/30 bg-green-500/10',
    purple: 'border-purple-500/30 bg-purple-500/10',
    blue: 'border-blue-500/30 bg-blue-500/10',
    gray: 'border-gray-500/30 bg-gray-500/10'
  }

  return (
    <div className={`rounded-xl border p-6 ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="flex items-center gap-3 mb-3">
        <span className="text-3xl">{icon}</span>
        <div>
          <p className="text-sm text-gray-300">{title}</p>
          <p className="text-2xl font-bold text-white">{count}</p>
        </div>
      </div>
      <p className="text-sm text-gray-400">{percentage}% of total users</p>
    </div>
  )
}

export const getServerSideProps = requireAdminSSR

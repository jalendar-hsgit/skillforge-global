import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useState, useEffect } from 'react'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Users, TrendingUp, DollarSign, Award, ActivitySquare } from 'lucide-react'

type KPI = {
  total_users: number
  active_users_today: number
  new_users_today: number
  total_mentors: number
  active_sessions_today: number
  revenue_today: number
  revenue_month: number
  revenue_year: number
  new_mentors_this_week: number
  avg_session_rating: number
}

type DailyMetric = {
  date: string
  count: number
  percentage_change: number
}

type RevenueSource = {
  source: string
  amount: number
  percentage: number
}

type FeatureUsage = {
  feature: string
  active_users: number
  total_users: number
  adoption_rate: number
  trend: string
}

type MentorPerformance = {
  mentor_id: number
  name: string
  avatar_url?: string
  sessions: number
  rating: number
  earnings: number
}

type StudentEngagementMetric = {
  metric: string
  value: number
  change: number
  trend: string
}

export default function AdminAnalytics({ me }: AdminSSRProps) {
  const [kpi, setKpi] = useState<KPI | null>(null)
  const [dailyUsers, setDailyUsers] = useState<DailyMetric[]>([])
  const [revenue, setRevenue] = useState<RevenueSource[]>([])
  const [features, setFeatures] = useState<FeatureUsage[]>([])
  const [mentors, setMentors] = useState<MentorPerformance[]>([])
  const [engagement, setEngagement] = useState<StudentEngagementMetric[]>([])
  const [timeframe, setTimeframe] = useState<'7d' | '30d' | '90d' | '1y'>('30d')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAnalytics()
  }, [timeframe])

  async function loadAnalytics() {
    setLoading(true)
    setError(null)
    try {
      const days = timeframe === '7d' ? 7 : timeframe === '30d' ? 30 : timeframe === '90d' ? 90 : 365
      
      const [kpiRes, dauRes, revRes, featRes, mentRes, engRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/analytics/overview`, { credentials: 'include' }),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/analytics/daily-active-users?days=${days}`, { credentials: 'include' }),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/analytics/revenue-breakdown`, { credentials: 'include' }),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/analytics/feature-adoption`, { credentials: 'include' }),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/analytics/mentors-performance?limit=10`, { credentials: 'include' }),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/analytics/student-engagement`, { credentials: 'include' })
      ])

      if (!kpiRes.ok) throw new Error('Failed to load KPI data')
      if (!dauRes.ok) throw new Error('Failed to load user metrics')

      const [kpiData, dauData, revData, featData, mentData, engData] = await Promise.all([
        kpiRes.json(),
        dauRes.json(),
        revRes.ok ? revRes.json() : [],
        featRes.ok ? featRes.json() : [],
        mentRes.ok ? mentRes.json() : [],
        engRes.ok ? engRes.json() : []
      ])

      setKpi(kpiData)
      setDailyUsers(dauData)
      setRevenue(revData)
      setFeatures(featData)
      setMentors(mentData)
      setEngagement(engData)
    } catch (err: any) {
      console.error('Failed to load analytics:', err)
      setError(err.message || 'Failed to load analytics data')
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
        }
      />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {loading ? (
          <div className="text-center py-12 text-gray-400">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-forgePurple border-r-transparent"></div>
            <p className="mt-4">Loading analytics...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <div className="rounded-xl border border-red-500/30 p-6 bg-red-500/10 inline-block">
              <p className="text-red-300">{error}</p>
              <button
                onClick={loadAnalytics}
                className="mt-4 px-4 py-2 bg-forgePurple text-white rounded-lg hover:bg-forgePurple/90 transition"
              >
                Retry
              </button>
            </div>
          </div>
        ) : !kpi ? (
          <div className="text-center py-12">
            <div className="rounded-xl border border-yellow-500/30 p-6 bg-yellow-500/10 inline-block">
              <p className="text-yellow-300">No analytics data available</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <MetricCard
                title="Total Users"
                value={kpi.total_users.toLocaleString()}
                subtitle={`+${kpi.new_users_today} today`}
                icon={<Users className="w-6 h-6 text-blue-400" />}
                color="blue"
              />
              <MetricCard
                title="Active Today"
                value={kpi.active_users_today.toLocaleString()}
                subtitle={`${((kpi.active_users_today / kpi.total_users) * 100).toFixed(1)}% of total`}
                icon={<ActivitySquare className="w-6 h-6 text-emerald-400" />}
                color="emerald"
              />
              <MetricCard
                title="Mentors"
                value={kpi.total_mentors.toLocaleString()}
                subtitle={`+${kpi.new_mentors_this_week} this week`}
                icon={<Award className="w-6 h-6 text-purple-400" />}
                color="purple"
              />
              <MetricCard
                title="Sessions Today"
                value={kpi.active_sessions_today.toLocaleString()}
                subtitle={`⭐ ${kpi.avg_session_rating.toFixed(1)}/5.0`}
                icon={<TrendingUp className="w-6 h-6 text-cyan-400" />}
                color="cyan"
              />
              <MetricCard
                title="Revenue (30d)"
                value={`$${(kpi.revenue_month / 1000).toFixed(1)}k`}
                subtitle={`Today: $${kpi.revenue_today.toFixed(2)}`}
                icon={<DollarSign className="w-6 h-6 text-amber-400" />}
                color="amber"
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Daily Active Users */}
              <div className="lg:col-span-2 rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-lg font-bold text-white mb-4">Daily Active Users ({timeframe})</h3>
                {dailyUsers.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={dailyUsers}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" style={{ fontSize: '12px' }} />
                      <YAxis stroke="rgba(255,255,255,0.3)" style={{ fontSize: '12px' }} />
                      <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', border: '1px solid rgba(139,92,246,0.3)' }} />
                      <Line type="monotone" dataKey="count" stroke="#8B5CF6" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-400">
                    No user data available
                  </div>
                )}
              </div>

              {/* Revenue Breakdown */}
              <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-lg font-bold text-white mb-4">Revenue Sources</h3>
                {revenue.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={revenue}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ source, percentage }) => `${source} ${percentage}%`}
                        outerRadius={80}
                        fill="#8B5CF6"
                        dataKey="amount"
                      >
                        {['#8B5CF6', '#06B6D4', '#EC4899', '#F59E0B', '#10B981'].map((color, idx) => (
                          <Cell key={`cell-${idx}`} fill={color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `$${(value as number).toFixed(2)}`} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-400">
                    No revenue data
                  </div>
                )}
              </div>
            </div>

            {/* Feature Adoption & Top Mentors */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Feature Adoption */}
              <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-lg font-bold text-white mb-4">Feature Adoption</h3>
                {features.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={features}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="feature" stroke="rgba(255,255,255,0.3)" style={{ fontSize: '12px' }} angle={-45} textAnchor="end" height={80} />
                      <YAxis stroke="rgba(255,255,255,0.3)" style={{ fontSize: '12px' }} />
                      <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', border: '1px solid rgba(139,92,246,0.3)' }} />
                      <Bar dataKey="adoption_rate" fill="#8B5CF6" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-400">
                    No feature adoption data
                  </div>
                )}
              </div>

              {/* Top Mentors */}
              <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-lg font-bold text-white mb-4">Top Mentors</h3>
                {mentors.length > 0 ? (
                  <div className="space-y-3 max-h-[320px] overflow-y-auto">
                    {mentors.slice(0, 5).map((mentor) => (
                      <div key={mentor.mentor_id} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition">
                        <div className="flex-1">
                          <p className="text-sm font-bold text-white">{mentor.name}</p>
                          <p className="text-xs text-gray-400">{mentor.sessions} sessions</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-bold text-forgePurple">⭐ {mentor.rating.toFixed(1)}</p>
                          <p className="text-xs text-gray-400">${mentor.earnings}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-400">
                    No mentor data
                  </div>
                )}
              </div>
            </div>

            {/* Student Engagement */}
            {engagement.length > 0 && (
              <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-lg font-bold text-white mb-4">Student Engagement Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {engagement.map((metric) => (
                    <div key={metric.metric} className="p-4 rounded-lg bg-white/5">
                      <p className="text-sm text-gray-400 mb-2">{metric.metric}</p>
                      <p className="text-2xl font-bold text-white">{metric.value}</p>
                      <p className={`text-xs mt-2 ${metric.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {metric.change >= 0 ? '+' : ''}{metric.change}% {metric.trend}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Refresh Button */}
            <div className="flex justify-end">
              <button
                onClick={loadAnalytics}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition"
              >
                🔄 Refresh
              </button>
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
  icon,
  color,
}: {
  title: string
  value: string
  subtitle?: string
  icon?: React.ReactNode
  color?: string
}) {
  const colorMap = {
    blue: 'from-blue-500/10 to-blue-600/5 border-blue-500/30',
    emerald: 'from-emerald-500/10 to-emerald-600/5 border-emerald-500/30',
    purple: 'from-purple-500/10 to-purple-600/5 border-purple-500/30',
    cyan: 'from-cyan-500/10 to-cyan-600/5 border-cyan-500/30',
    amber: 'from-amber-500/10 to-amber-600/5 border-amber-500/30',
  }

  return (
    <div className={`rounded-xl bg-gradient-to-br ${colorMap[color as keyof typeof colorMap] || colorMap.blue} border p-6`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm text-gray-400 font-medium">{title}</p>
          <p className="text-3xl font-bold text-white mt-2">{value}</p>
        </div>
        {icon}
      </div>
      {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
    </div>
  )
}

export const getServerSideProps = requireAdminSSR

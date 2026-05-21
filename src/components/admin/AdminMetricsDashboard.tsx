/**
 * Admin Metrics Dashboard - Admin-only metrics and analytics
 * Shows KPIs, user growth, engagement, and system health
 */
import { useEffect, useState } from 'react'
import { Card } from '@/components/Card'
import { adminMetricsAPI } from '@/lib/newFeaturesAPI'

interface MetricCard {
  label: string
  value: string | number
  trend?: number
  icon: string
  color: 'blue' | 'green' | 'purple' | 'orange' | 'red'
}

interface AdminMetrics {
  summary: {
    active_users: number
    total_revenue: number
    engagement_rate: number
    system_status: 'healthy' | 'degraded' | 'critical'
  }
  growth?: {
    daily_registrations: number[]
    total_users: number
    growth_rate: number
  }
  engagement?: {
    quiz_attempts: number
    coding_submissions: number
    resume_views: number
    avg_session_duration: number
  }
  health?: {
    db_status: string
    active_sessions: number
    error_rate: number
    avg_response_time: number
  }
}

const getColorClasses = (color: string) => {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200',
    red: 'bg-red-50 text-red-600 border-red-200',
  }
  return colors[color] || colors.blue
}

const getStatusColor = (status: string) => {
  if (status.includes('healthy') || status === 'healthy') return 'text-green-600'
  if (status.includes('degraded')) return 'text-yellow-600'
  return 'text-red-600'
}

export default function AdminMetricsDashboard({ requiredRole = 'admin' }: { requiredRole?: string }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null)
  const [tab, setTab] = useState<'summary' | 'growth' | 'engagement' | 'health'>('summary')

  useEffect(() => {
    let mounted = true

    const fetchMetrics = async () => {
      try {
        setLoading(true)
        setError(null)

        const [summary, growth, engagement, health] = await Promise.all([
          adminMetricsAPI.getDashboardSummary(),
          adminMetricsAPI.getUserGrowth(),
          adminMetricsAPI.getEngagementMetrics(),
          adminMetricsAPI.getSystemHealth(),
        ])

        if (mounted) {
          setMetrics({
            summary,
            growth,
            engagement,
            health,
          })
        }
      } catch (err: any) {
        if (mounted) setError(err.message || 'Failed to load metrics')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    fetchMetrics()
    return () => {
      mounted = false
    }
  }, [])

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center gap-2 text-gray-600">
          <span className="animate-spin">⏳</span>
          <span>Loading metrics dashboard...</span>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="p-6 border-red-200 bg-red-50">
        <p className="text-sm text-red-600">{error}</p>
      </Card>
    )
  }

  if (!metrics) return null

  const cards: MetricCard[] = [
    {
      label: 'Active Users',
      value: metrics.summary.active_users?.toLocaleString() || '0',
      trend: 12,
      icon: '👥',
      color: 'blue',
    },
    {
      label: 'Total Revenue',
      value: `$${(metrics.summary.total_revenue || 0).toLocaleString()}`,
      trend: 8,
      icon: '💰',
      color: 'green',
    },
    {
      label: 'Engagement Rate',
      value: `${metrics.summary.engagement_rate || 0}%`,
      trend: -2,
      icon: '📈',
      color: 'purple',
    },
    {
      label: 'System Status',
      value: metrics.summary.system_status || 'unknown',
      icon: '🔧',
      color: metrics.summary.system_status === 'healthy' ? 'green' : 'red',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Admin Metrics Dashboard</h1>
        <p className="text-gray-600 mt-1">Real-time analytics and system monitoring</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card, idx) => (
          <Card key={idx} className={`p-4 border-2 ${getColorClasses(card.color)}`}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-gray-600 uppercase">{card.label}</p>
                <p className="text-2xl font-bold mt-2">{card.value}</p>
                {card.trend !== undefined && (
                  <p
                    className={`text-xs mt-2 ${
                      card.trend >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {card.trend >= 0 ? '↑' : '↓'} {Math.abs(card.trend)}% vs last period
                  </p>
                )}
              </div>
              <span className="text-3xl">{card.icon}</span>
            </div>
          </Card>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {(['summary', 'growth', 'engagement', 'health'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 font-medium border-b-2 transition-all ${
              tab === t
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'summary' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card className="p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Key Metrics</h3>
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-gray-600">Active Users</dt>
                <dd className="font-semibold text-gray-900">
                  {metrics.summary.active_users?.toLocaleString()}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Total Revenue</dt>
                <dd className="font-semibold text-gray-900">
                  ${(metrics.summary.total_revenue || 0).toLocaleString()}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Engagement Rate</dt>
                <dd className="font-semibold text-gray-900">
                  {metrics.summary.engagement_rate || 0}%
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">System Status</dt>
                <dd className={`font-semibold ${getStatusColor(metrics.summary.system_status || '')}`}>
                  {metrics.summary.system_status || 'Unknown'}
                </dd>
              </div>
            </dl>
          </Card>

          <Card className="p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Quick Stats</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Quiz Attempts</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">
                  {metrics.engagement?.quiz_attempts?.toLocaleString() || '0'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Coding Submissions</p>
                <p className="text-2xl font-bold text-purple-600 mt-1">
                  {metrics.engagement?.coding_submissions?.toLocaleString() || '0'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Avg Session Duration</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {metrics.engagement?.avg_session_duration || '0'} min
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {tab === 'growth' && (
        <Card className="p-6">
          <h3 className="font-semibold text-gray-900 mb-4">User Growth</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Total Users</p>
              <p className="text-3xl font-bold text-blue-600 mt-1">
                {metrics.growth?.total_users?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Growth Rate</p>
              <p className="text-3xl font-bold text-green-600 mt-1">
                {metrics.growth?.growth_rate || 0}%
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Daily Average</p>
              <p className="text-3xl font-bold text-purple-600 mt-1">
                {Math.round(
                  (metrics.growth?.daily_registrations || []).reduce((a, b) => a + b, 0) /
                    (metrics.growth?.daily_registrations || [1]).length
                )}
              </p>
            </div>
          </div>
        </Card>
      )}

      {tab === 'engagement' && (
        <Card className="p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Engagement Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <p className="text-sm text-gray-600 font-medium">Quiz Attempts</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">
                {metrics.engagement?.quiz_attempts?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="border rounded-lg p-4">
              <p className="text-sm text-gray-600 font-medium">Coding Submissions</p>
              <p className="text-3xl font-bold text-purple-600 mt-2">
                {metrics.engagement?.coding_submissions?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="border rounded-lg p-4">
              <p className="text-sm text-gray-600 font-medium">Resume Views</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {metrics.engagement?.resume_views?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="border rounded-lg p-4">
              <p className="text-sm text-gray-600 font-medium">Avg Session Duration</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">
                {metrics.engagement?.avg_session_duration || '0'} min
              </p>
            </div>
          </div>
        </Card>
      )}

      {tab === 'health' && (
        <Card className="p-6">
          <h3 className="font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className={`border-l-4 border-green-500 bg-green-50 p-4 rounded`}>
              <p className="text-sm text-gray-600 font-medium">Database Status</p>
              <p className="text-lg font-bold text-green-600 mt-2">
                {metrics.health?.db_status || 'Unknown'}
              </p>
            </div>
            <div className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded">
              <p className="text-sm text-gray-600 font-medium">Active Sessions</p>
              <p className="text-lg font-bold text-blue-600 mt-2">
                {metrics.health?.active_sessions || '0'}
              </p>
            </div>
            <div className="border-l-4 border-red-500 bg-red-50 p-4 rounded">
              <p className="text-sm text-gray-600 font-medium">Error Rate</p>
              <p className="text-lg font-bold text-red-600 mt-2">
                {metrics.health?.error_rate || '0'}%
              </p>
            </div>
            <div className="border-l-4 border-purple-500 bg-purple-50 p-4 rounded">
              <p className="text-sm text-gray-600 font-medium">Avg Response Time</p>
              <p className="text-lg font-bold text-purple-600 mt-2">
                {metrics.health?.avg_response_time || '0'} ms
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Last Updated */}
      <p className="text-xs text-gray-500 text-right">
        Last updated: {new Date().toLocaleTimeString()}
      </p>
    </div>
  )
}

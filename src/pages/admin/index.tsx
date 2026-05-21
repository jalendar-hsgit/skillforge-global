import Head from 'next/head'
import Link from 'next/link'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'

type DashboardStats = {
  total_users: number
  total_mentors: number
  pending_mentor_applications: number
  total_sessions: number
  scheduled_sessions: number
  completed_sessions: number
  total_revenue: number
  active_users_30d: number
}

type AuditLog = {
  id: number
  admin_email: string
  action: string
  resource_type: string
  details: string
  created_at: string
}

export default function AdminDashboard({ me }: AdminSSRProps) {
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentLogs, setRecentLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadDashboard()
  }, [])

  async function loadDashboard() {
    setLoading(true)
    try {
      const [statsRes, logsRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/dashboard/stats`, {
          credentials: 'include'
        }),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/logs?limit=10`, {
          credentials: 'include'
        })
      ])

      if (statsRes.status === 403 || logsRes.status === 403) {
        setError('Access denied. Admin privileges required.')
        return
      }

      if (statsRes.status === 401 || logsRes.status === 401) {
        router.push('/login?redirect=/admin')
        return
      }

      if (statsRes.ok) {
        const data = await statsRes.json()
        setStats(data)
      }

      if (logsRes.ok) {
        const data = await logsRes.json()
        setRecentLogs(data.logs || [])
      }
    } catch (err) {
      console.error(err)
      setError('Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  const quickLinks = [
    { title: 'Analytics', desc: 'Platform performance metrics', href: '/admin/analytics', icon: '📊' },
    { title: 'User Analytics', desc: 'Retention & engagement insights', href: '/admin/user-analytics', icon: '👤' },
    { title: 'Revenue', desc: 'Financial analytics & payments', href: '/admin/revenue', icon: '💰' },
    { title: 'Marketplace', desc: 'Orders, coupons & sales', href: '/admin/marketplace', icon: '🛒' },
    { title: 'Notifications', desc: 'Send broadcast emails & templates', href: '/admin/notifications', icon: '📧' },
    { title: 'Users', desc: 'Manage user accounts & roles', href: '/admin/users', icon: '👥' },
    { title: 'Mentors', desc: 'Approve & manage mentors', href: '/admin/mentors', icon: '🎓', badge: stats?.pending_mentor_applications },
    { title: 'Sessions', desc: 'Review & moderate sessions', href: '/admin/sessions', icon: '📅' },
    { title: 'Courses', desc: 'Manage course content', href: '/admin/courses-enhanced', icon: '📚' },
    { title: 'Audit Logs', desc: 'View admin activity logs', href: '/admin/logs', icon: '📋' },
    { title: 'Settings', desc: 'Platform configuration', href: '/admin/settings', icon: '⚙️' },
  ]

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-techGray">Loading admin dashboard...</div>
        </div>
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="rounded-xl border border-red-500/30 p-8 bg-red-500/10">
            <p className="text-red-300">{error}</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <Head><title>{`Admin Dashboard`}</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Admin Dashboard</h1>
            <p className="text-techGray">Platform management & analytics · Signed in as {me.email} ({me.role})</p>
          </div>
          <button
            onClick={loadDashboard}
            className="h-10 px-4 rounded-md bg-white/5 border border-white/10 hover:bg-white/10 transition"
          >
            🔄 Refresh
          </button>
        </div>

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="rounded-xl border border-white/10 p-6 bg-gradient-to-br from-forgePurple/20 to-transparent">
              <div className="text-sm text-techGray mb-1">Total Users</div>
              <div className="text-3xl font-bold">{stats.total_users.toLocaleString()}</div>
              <div className="text-xs text-green-400 mt-1">
                +{stats.active_users_30d} in last 30 days
              </div>
            </div>

            <div className="rounded-xl border border-white/10 p-6 bg-gradient-to-br from-neuralBlue/20 to-transparent">
              <div className="text-sm text-techGray mb-1">Mentors</div>
              <div className="text-3xl font-bold">{stats.total_mentors}</div>
              {stats.pending_mentor_applications > 0 && (
                <div className="text-xs text-yellow-400 mt-1">
                  {stats.pending_mentor_applications} pending approval
                </div>
              )}
            </div>

            <div className="rounded-xl border border-white/10 p-6 bg-gradient-to-br from-aiElectric/20 to-transparent">
              <div className="text-sm text-techGray mb-1">Sessions</div>
              <div className="text-3xl font-bold">{stats.total_sessions}</div>
              <div className="text-xs text-techGray mt-1">
                {stats.scheduled_sessions} scheduled · {stats.completed_sessions} completed
              </div>
            </div>

            <div className="rounded-xl border border-white/10 p-6 bg-gradient-to-br from-green-500/20 to-transparent">
              <div className="text-sm text-techGray mb-1">Total Revenue</div>
              <div className="text-3xl font-bold">${stats.total_revenue.toLocaleString()}</div>
              <div className="text-xs text-green-400 mt-1">
                From completed sessions
              </div>
            </div>
          </div>
        )}

        {/* Quick Links */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickLinks.map((link) => (
              <Link
                key={link.title}
                href={link.href}
                className="rounded-xl border border-white/10 p-6 bg-white/[0.06] hover:bg-white/[0.09] transition group relative"
              >
                <div className="flex items-start gap-4">
                  <div className="text-3xl">{link.icon}</div>
                  <div className="flex-1">
                    <div className="text-lg font-semibold group-hover:text-neuralBlue transition">
                      {link.title}
                      {link.badge !== undefined && link.badge > 0 && (
                        <span className="ml-2 text-xs px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">
                          {link.badge}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-techGray mt-1">{link.desc}</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold">Recent Admin Activity</h2>
            <Link href="/admin/logs" className="text-sm text-neuralBlue hover:underline">
              View All Logs →
            </Link>
          </div>
          {recentLogs.length === 0 ? (
            <div className="rounded-xl border border-white/10 p-8 bg-white/[0.06] text-center text-techGray">
              No recent activity
            </div>
          ) : (
            <div className="space-y-2">
              {recentLogs.map((log) => (
                <div
                  key={log.id}
                  className="rounded-lg border border-white/10 p-4 bg-white/[0.04] hover:bg-white/[0.06] transition"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="text-sm">
                        <span className="font-semibold text-neuralBlue">{log.admin_email}</span>
                        {' '}
                        <span className="text-techGray">{log.action.replace(/_/g, ' ')}</span>
                        {' '}
                        <span className="text-forgePurple">{log.resource_type}</span>
                      </div>
                      {log.details && (
                        <div className="text-xs text-techGray mt-1">{log.details}</div>
                      )}
                    </div>
                    <div className="text-xs text-techGray whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </Layout>
  )
}

export const getServerSideProps = requireAdminSSR

import { useSession } from 'next-auth/react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import AdminMetricsDashboard from '@/components/admin/AdminMetricsDashboard'
import PageLayout from '@/components/PageLayout'
import { useState } from 'react'

export default function AdminDashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [period, setPeriod] = useState<number>(30)

  // Loading state
  if (status === 'loading') {
    return (
      <PageLayout>
        <div className="flex justify-center items-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading admin dashboard...</p>
          </div>
        </div>
      </PageLayout>
    )
  }

  // Unauthorized state
  if (!session) {
    router.push('/auth/signin')
    return null
  }

  const userRole = (session?.user as any)?.role || ''
  const isAdmin = userRole === 'admin' || userRole === 'superadmin'

  if (!isAdmin) {
    return (
      <PageLayout>
        <div className="max-w-2xl mx-auto px-4 py-12">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h1 className="text-2xl font-bold text-red-600 mb-2">❌ Access Denied</h1>
            <p className="text-red-700">
              You don't have permission to access the admin dashboard. This area is restricted to administrators only.
            </p>
            <button
              onClick={() => router.push('/')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
            >
              Return to Home
            </button>
          </div>
        </div>
      </PageLayout>
    )
  }

  return (
    <>
      <Head>
        <title>Admin Dashboard - SkillForge Global</title>
        <meta name="description" content="Admin dashboard for SkillForge Global platform monitoring and management" />
        <meta name="robots" content="noindex, nofollow" />
      </Head>

      <PageLayout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Header Section */}
          <div className="mb-8 flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">⚙️ Admin Dashboard</h1>
              <p className="text-lg text-gray-600">
                Monitor system health, user growth, and platform metrics
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-sm text-gray-600 mb-2">Logged in as</p>
              <p className="font-semibold text-gray-900">{session?.user?.name || session?.user?.email}</p>
              <p className="text-xs text-gray-500 mt-1">Role: <span className="font-mono bg-blue-100 px-2 py-1 rounded">{userRole}</span></p>
            </div>
          </div>

          {/* Period Selector */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Dashboard Period</h2>
            <div className="flex gap-4">
              <button
                onClick={() => setPeriod(30)}
                className={`px-6 py-2 rounded-lg font-medium transition ${
                  period === 30
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Last 30 Days
              </button>
              <button
                onClick={() => setPeriod(90)}
                className={`px-6 py-2 rounded-lg font-medium transition ${
                  period === 90
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Last 90 Days
              </button>
              <button
                onClick={() => setPeriod(365)}
                className={`px-6 py-2 rounded-lg font-medium transition ${
                  period === 365
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Last Year
              </button>
            </div>
          </div>

          {/* Admin Metrics Dashboard Component */}
          <div className="space-y-8">
            <AdminMetricsDashboard
              userRole={userRole}
              period={period}
            />
          </div>

          {/* Admin Controls */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <AdminControlCard
              title="User Management"
              description="Manage user accounts and permissions"
              href="/admin/users"
              icon="👥"
            />
            <AdminControlCard
              title="Content Management"
              description="Manage courses, quizzes, and content"
              href="/admin/content"
              icon="📚"
            />
            <AdminControlCard
              title="Reports"
              description="Generate and view system reports"
              href="/admin/reports"
              icon="📊"
            />
            <AdminControlCard
              title="Settings"
              description="Configure system settings and policies"
              href="/admin/settings"
              icon="⚙️"
            />
          </div>

          {/* Quick Actions */}
          <div className="mt-8 bg-blue-50 rounded-lg p-6 border border-blue-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <QuickActionButton
                label="Export User Data"
                description="Export all user data as CSV"
                onClick={() => alert('Feature coming soon')}
              />
              <QuickActionButton
                label="View Logs"
                description="System activity and error logs"
                onClick={() => alert('Feature coming soon')}
              />
              <QuickActionButton
                label="Backup Database"
                description="Create database backup"
                onClick={() => alert('Feature coming soon')}
              />
              <QuickActionButton
                label="Send Announcement"
                description="Send platform-wide announcement"
                onClick={() => alert('Feature coming soon')}
              />
            </div>
          </div>

          {/* Footer Note */}
          <div className="mt-8 text-center text-sm text-gray-500 border-t pt-6">
            <p>Admin Dashboard • Real-time monitoring and analytics</p>
            <p>Last updated: {new Date().toLocaleString()}</p>
          </div>
        </div>
      </PageLayout>
    </>
  )
}

interface AdminControlCardProps {
  title: string
  description: string
  href: string
  icon: string
}

function AdminControlCard({ title, description, href, icon }: AdminControlCardProps) {
  return (
    <a
      href={href}
      className="bg-white rounded-lg shadow hover:shadow-lg transition p-6 group cursor-pointer"
    >
      <div className="text-3xl mb-3">{icon}</div>
      <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition">
        {title}
      </h4>
      <p className="text-sm text-gray-600 mt-2">{description}</p>
    </a>
  )
}

interface QuickActionButtonProps {
  label: string
  description: string
  onClick: () => void
}

function QuickActionButton({ label, description, onClick }: QuickActionButtonProps) {
  return (
    <button
      onClick={onClick}
      className="text-left p-4 bg-white rounded-lg hover:bg-blue-50 transition border border-transparent hover:border-blue-300"
    >
      <h4 className="font-semibold text-gray-900">{label}</h4>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
    </button>
  )
}

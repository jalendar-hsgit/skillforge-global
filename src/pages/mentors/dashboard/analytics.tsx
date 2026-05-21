import Head from 'next/head'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import DashboardLayout from '@/components/DashboardLayout'
import DashboardStatCard from '@/components/DashboardStatCard'
import { DashboardGridSkeleton } from '@/components/DashboardSkeletons'

type AnalyticsData = {
  total_sessions: number
  sessions_by_status: { [key: string]: number }
  rating_distribution: { [key: string]: number }
  sessions_by_day: Array<{ day: string; count: number }> | { [key: string]: number }
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
      <DashboardLayout
        title="Analytics"
        subtitle="Session performance and ratings"
        breadcrumbs={[{ label: 'Dashboard', href: '/mentors/dashboard' }, { label: 'Analytics' }]}
      >
        <DashboardGridSkeleton />
      </DashboardLayout>
    )
  }

  if (!data) {
    return (
      <DashboardLayout
        title="Analytics"
        subtitle="Session performance and ratings"
        breadcrumbs={[{ label: 'Dashboard', href: '/mentors/dashboard' }, { label: 'Analytics' }]}
      >
        <div className="text-center py-12 text-techGray-400">No analytics data available</div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout
      title="Analytics"
      subtitle="Session performance and ratings"
      breadcrumbs={[{ label: 'Dashboard', href: '/mentors/dashboard' }, { label: 'Analytics' }]}
    >
      <Head>
        <title>Analytics – Mentor Dashboard</title>
      </Head>

      <div className="space-y-6">
        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DashboardStatCard
            label="Total Sessions"
            value={data?.total_sessions?.toString() || '0'}
            color="blue"
          />
          <DashboardStatCard
            label="Average Rating"
            value="4.5 ⭐"
            color="green"
          />
        </div>

        {/* Sessions by Status */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4">Sessions by Status</h2>
          <div className="space-y-3">
            {Object.entries(data.sessions_by_status || {}).map(([status, count]) => {
              const statusColorMap: { [key: string]: { bg: string; text: string } } = {
                pending: { bg: 'bg-warning/20', text: 'text-warning' },
                confirmed: { bg: 'bg-success/20', text: 'text-success' },
                completed: { bg: 'bg-neuralBlue/20', text: 'text-neuralBlue-400' },
                cancelled: { bg: 'bg-error/20', text: 'text-error' }
              }
              const colors = statusColorMap[status] || { bg: 'bg-techGray/20', text: 'text-techGray-400' }
              return (
                <div key={status} className="flex justify-between items-center bg-white/5 border border-white/10 p-3 rounded-lg">
                  <span className="capitalize text-techGray-400">{status}</span>
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${colors.bg}`}></div>
                    <span className={`font-semibold ${colors.text}`}>{count}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Rating Distribution */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4">Rating Distribution</h2>
          <div className="space-y-3">
            {[5, 4, 3, 2, 1].map((rating) => {
              const count = data.rating_distribution?.[rating] || 0
              return (
                <div key={rating} className="flex items-center gap-4">
                  <span className="text-techGray-400 w-12">{rating} ⭐</span>
                  <div className="flex-1 bg-white/10 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-success to-success h-2 rounded-full transition-all"
                      style={{ width: `${count * 10}%` }}
                    ></div>
                  </div>
                  <span className="text-techGray-400 w-12 text-right">{count}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

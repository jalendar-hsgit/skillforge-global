import Head from 'next/head'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import DashboardLayout from '@/components/DashboardLayout'
import { DashboardGridSkeleton } from '@/components/DashboardSkeletons'
import DashboardStatCard from '@/components/DashboardStatCard'
import DashboardSectionHeader from '@/components/DashboardSectionHeader'
import DashboardListItem from '@/components/DashboardListItem'

type EarningsData = {
  total_earnings: number
  total_hours: number
  session_count: number
  average_per_session: number
  hourly_rate: number
  monthly_breakdown: Array<{ month: string; earnings: number; sessions: number }>
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

  const thisMonth = data?.monthly_breakdown?.[0]?.earnings ?? 0
  const lastMonth = data?.monthly_breakdown?.[1]?.earnings ?? 0
  const monthChange = lastMonth > 0
    ? ((thisMonth - lastMonth) / lastMonth) * 100
    : 0

  if (loading) {
    return (
      <DashboardLayout 
        title="Earnings"
        subtitle="Your earnings and payments"
        breadcrumbs={[{ label: 'Dashboard', href: '/mentors/dashboard' }, { label: 'Earnings' }]}
      >
        <DashboardGridSkeleton />
      </DashboardLayout>
    )
  }

  if (!data) {
    return (
      <DashboardLayout 
        title="Earnings"
        subtitle="Your earnings and payments"
        breadcrumbs={[{ label: 'Dashboard', href: '/mentors/dashboard' }, { label: 'Earnings' }]}
      >
        <div className="text-center py-12 text-techGray-400">No earnings data available</div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout
      title="Earnings"
      subtitle="Your earnings and payments"
      breadcrumbs={[{ label: 'Dashboard', href: '/mentors/dashboard' }, { label: 'Earnings' }]}
    >
      <Head>
        <title>Earnings – Mentor Dashboard</title>
      </Head>

      <div className="space-y-8">
        {/* Earnings Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <DashboardStatCard
            label="Total Earnings"
            value={`$${data.total_earnings.toFixed(2)}`}
            color="electric"
          />
          <DashboardStatCard
            label="Sessions Count"
            value={data.session_count}
            color="green"
          />
          <DashboardStatCard
            label="Average Per Session"
            value={`$${data.average_per_session.toFixed(2)}`}
            color="blue"
          />
        </div>

        {/* Monthly Breakdown */}
        <div>
          <DashboardSectionHeader title="Monthly Breakdown" subtitle={`${data.monthly_breakdown?.length || 0} months`} />
          <div className="space-y-2">
            {data.monthly_breakdown && data.monthly_breakdown.map((month, idx) => (
              <DashboardListItem key={idx} hoverColor="electric" className="p-3">
                <div className="flex justify-between items-center">
                  <span className="text-white font-medium">{month.month}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-techGray-400 text-sm">{month.sessions} sessions</span>
                    <span className="text-success font-semibold">${month.earnings.toFixed(2)}</span>
                  </div>
                </div>
              </DashboardListItem>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

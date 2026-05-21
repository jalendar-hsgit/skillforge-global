import Head from 'next/head'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import DashboardLayout from '@/components/DashboardLayout'
import { DashboardGridSkeleton } from '@/components/DashboardSkeletons'
import DashboardStatCard from '@/components/DashboardStatCard'
import DashboardSectionHeader from '@/components/DashboardSectionHeader'
import DashboardListItem from '@/components/DashboardListItem'

type MentorStats = {
  total_sessions: number
  month_sessions: number
  completed_sessions: number
  total_earnings: number
  month_earnings: number
  average_rating: number
  total_reviews: number
  unique_students: number
}

type UpcomingSession = {
  id: number
  student_id: number
  topic: string
  scheduled_at: string
  duration_minutes: number
  status: string
}

type Review = {
  id: number
  student_id: number
  rating: number
  review_text?: string
  comment?: string
  created_at: string
}

type MentorData = {
  mentor: {
    id: number
    user_id: number
    status: string
    bio: string
    expertise: string[]
    hourly_rate: number
  }
  stats: MentorStats
  upcoming_sessions: UpcomingSession[]
  recent_reviews: Review[]
}

export default function MentorDashboard() {
  const router = useRouter()
  const [data, setData] = useState<MentorData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadDashboard()
  }, [])

  async function loadDashboard() {
    setLoading(true)
    setError('')
    try {
      const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/mentor-portal/dashboard/overview`
      
      const res = await fetch(apiUrl, {
        credentials: 'include'
      })

      if (res.status === 401) {
        router.push('/login?redirect=/mentors/dashboard')
        return
      }

      if (res.status === 404) {
        setError('You are not registered as a mentor')
        return
      }

      if (res.status === 403) {
        try {
          const errorData = await res.json()
          setError(errorData.detail || 'Mentor account not approved')
        } catch {
          setError('Mentor account not approved')
        }
        return
      }

      if (res.ok) {
        const dashboardData = await res.json()
        
        if (dashboardData.mentor && typeof dashboardData.mentor.status !== 'string') {
          dashboardData.mentor.status = String(dashboardData.mentor.status)
        }
        setData(dashboardData)
      } else {
        setError('Failed to load dashboard')
      }
    } catch (err) {
      console.error('Error loading dashboard:', err)
      setError('Error loading dashboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout
        title="Dashboard"
        subtitle="Welcome back, mentor"
        breadcrumbs={[{ label: 'Dashboard', href: '/mentors/dashboard' }]}
      >
        <Head>
          <title>Mentor Dashboard</title>
        </Head>
        <DashboardGridSkeleton count={4} />
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout
        title="Dashboard"
        subtitle="Welcome back, mentor"
        breadcrumbs={[{ label: 'Dashboard', href: '/mentors/dashboard' }]}
      >
        <Head>
          <title>Mentor Dashboard</title>
        </Head>
        <div className="max-w-md mx-auto text-center">
          <div className="text-error mb-6 text-lg font-medium">{error}</div>
          <Link
            href="/mentors"
            className="inline-block px-6 py-3 bg-forgePurple hover:bg-forgePurple/80 text-white font-medium rounded-lg transition-colors"
          >
            Back to Mentors
          </Link>
        </div>
      </DashboardLayout>
    )
  }

  if (!data) {
    return null
  }

  const { mentor, stats, upcoming_sessions, recent_reviews } = data

  return (
    <DashboardLayout
      title="Dashboard"
      subtitle="Your performance overview"
      breadcrumbs={[{ label: 'Dashboard', href: '/mentors/dashboard' }]}
    >
      <Head>
        <title>Mentor Dashboard</title>
      </Head>

      <div className="space-y-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <DashboardStatCard
            label="Total Earnings"
            value={`$${stats.total_earnings.toFixed(2)}`}
            subtitle={`+$${stats.month_earnings.toFixed(2)} this month`}
            color="purple"
          />

          <DashboardStatCard
            label="Total Sessions"
            value={stats.total_sessions}
            subtitle={`${stats.completed_sessions} completed`}
            color="blue"
          />

          <DashboardStatCard
            label="Average Rating"
            value={`${stats.average_rating.toFixed(1)} ⭐`}
            subtitle={`${stats.total_reviews} reviews`}
            color="electric"
          />

          <DashboardStatCard
            label="Total Students"
            value={stats.unique_students}
            subtitle={`${stats.month_sessions} sessions this month`}
            color="green"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Upcoming Sessions */}
            <div>
              <DashboardSectionHeader title="Upcoming Sessions" />
              {upcoming_sessions.length === 0 ? (
                <DashboardListItem>
                  <p className="text-techGray-400 text-center">No upcoming sessions</p>
                </DashboardListItem>
              ) : (
                <div className="space-y-4">
                  {upcoming_sessions.map((session) => (
                    <DashboardListItem key={session.id} hoverColor="purple">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-semibold text-white">{session.topic}</h3>
                        <span className={`px-3 py-1 rounded text-xs font-medium ${
                          session.status === 'confirmed' 
                            ? 'bg-success/20 text-success' 
                            : 'bg-warning/20 text-warning'
                        }`}>
                          {session.status}
                        </span>
                      </div>
                      <div className="flex gap-4 text-sm text-techGray-400">
                        <span>📅 {new Date(session.scheduled_at).toLocaleDateString()}</span>
                        <span>⏱️ {session.duration_minutes} min</span>
                        <span>👤 Student #{session.student_id}</span>
                      </div>
                    </DashboardListItem>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Navigation */}
            <div>
              <DashboardSectionHeader title="Quick Navigation" />
              <div className="grid grid-cols-2 gap-4">
                <Link href="/mentors/dashboard/earnings" className="block">
                  <DashboardListItem hoverColor="purple">
                    <div className="text-3xl mb-3">💵</div>
                    <h3 className="font-semibold text-white mb-2">Earnings</h3>
                    <p className="text-sm text-techGray-400">Detailed breakdown</p>
                  </DashboardListItem>
                </Link>

                <Link href="/mentors/dashboard/analytics" className="block">
                  <DashboardListItem hoverColor="blue">
                    <div className="text-3xl mb-3">📊</div>
                    <h3 className="font-semibold text-white mb-2">Analytics</h3>
                    <p className="text-sm text-techGray-400">Performance insights</p>
                  </DashboardListItem>
                </Link>

                <Link href="/mentors/dashboard/payouts" className="block">
                  <DashboardListItem hoverColor="electric">
                    <div className="text-3xl mb-3">🏦</div>
                    <h3 className="font-semibold text-white mb-2">Payouts</h3>
                    <p className="text-sm text-techGray-400">Withdrawal options</p>
                  </DashboardListItem>
                </Link>

                <Link href="/" className="block">
                  <DashboardListItem hoverColor="purple">
                    <div className="text-3xl mb-3">🏠</div>
                    <h3 className="font-semibold text-white mb-2">Home</h3>
                    <p className="text-sm text-techGray-400">Back to main site</p>
                  </DashboardListItem>
                </Link>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Profile Card */}
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">Your Profile</h2>
                <Link
                  href="/mentors/dashboard/profile"
                  className="px-3 py-1 text-sm bg-forgePurple hover:bg-forgePurple/80 text-white rounded transition-colors font-medium"
                >
                  ✎ Edit
                </Link>
              </div>
              <DashboardListItem hoverColor="purple" className="space-y-4">
                <div>
                  <p className="text-sm text-techGray-400 mb-1">Hourly Rate</p>
                  <p className="text-2xl font-bold text-forgePurple">${mentor.hourly_rate}/hr</p>
                </div>
                <div>
                  <p className="text-sm text-techGray-400 mb-2">Expertise</p>
                  <div className="flex flex-wrap gap-2">
                    {Array.isArray(mentor.expertise) && mentor.expertise.length > 0
                      ? mentor.expertise.map((skill, i) => (
                          <span key={i} className="px-2 py-1 bg-forgePurple/20 text-forgePurple text-xs rounded">
                            {skill}
                          </span>
                        ))
                      : <span className="text-techGray-400 text-sm">Not set</span>
                    }
                  </div>
                </div>
                <div>
                  <p className="text-sm text-techGray-400 mb-1">Status</p>
                  <p className={`font-medium capitalize ${
                    mentor.status === 'approved' ? 'text-success' : 
                    mentor.status === 'pending' ? 'text-warning' : 
                    'text-error'
                  }`}>{mentor.status}</p>
                </div>
              </DashboardListItem>
            </div>

            {/* Recent Reviews */}
            <div>
              <DashboardSectionHeader title="Recent Reviews" subtitle={`${recent_reviews.length} reviews`} />
              {recent_reviews.length === 0 ? (
                <DashboardListItem>
                  <p className="text-techGray-400 text-sm text-center">No reviews yet</p>
                </DashboardListItem>
              ) : (
                <div className="space-y-3">
                  {recent_reviews.slice(0, 3).map((review) => (
                    <DashboardListItem key={review.id} className="p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex gap-0.5">
                          {[...Array(5)].map((_, i) => (
                            <span key={i} className={i < review.rating ? 'text-aiElectric' : 'text-techGray-600'}>
                              ⭐
                            </span>
                          ))}
                        </div>
                        <span className="text-xs text-techGray-500">
                          {new Date(review.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      {(review.review_text || review.comment) && (
                        <p className="text-sm text-techGray-400 italic">"{review.review_text || review.comment}"</p>
                      )}
                    </DashboardListItem>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

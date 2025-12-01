import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'

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
      console.log('Fetching mentor dashboard from:', apiUrl)
      
      const res = await fetch(apiUrl, {
        credentials: 'include'
      })

      console.log('Response status:', res.status)

      if (res.status === 401) {
        console.log('Unauthorized - redirecting to login')
        router.push('/login?redirect=/mentors/dashboard')
        return
      }

      if (res.status === 404) {
        console.log('Not a mentor')
        setError('You are not registered as a mentor')
        return
      }

      if (res.status === 403) {
        const errorData = await res.json()
        console.log('Forbidden:', errorData)
        setError(errorData.detail || 'Mentor account not approved')
        return
      }

      if (res.ok) {
        const dashboardData = await res.json()
        console.log('Dashboard data received:', dashboardData)
        
        // Ensure status is a string
        if (dashboardData.mentor && typeof dashboardData.mentor.status !== 'string') {
          dashboardData.mentor.status = String(dashboardData.mentor.status)
        }
        setData(dashboardData)
      } else {
        const errorText = await res.text()
        console.error('Dashboard error:', res.status, errorText)
        setError(`Failed to load dashboard (${res.status})`)
      }
    } catch (err: any) {
      console.error('Dashboard fetch error:', err)
      setError(err?.message || 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-techGray">Loading mentor dashboard...</div>
        </div>
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-400 mb-4">{error}</div>
            <Link
              href="/mentors"
              className="inline-block px-6 py-3 bg-forgePurple hover:bg-forgePurple/80 text-white font-medium rounded-lg transition-colors"
            >
              Back to Mentors
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  if (!data) {
    return null
  }

  const { mentor, stats, upcoming_sessions, recent_reviews } = data

  return (
    <Layout>
      <Head>
        <title>Mentor Dashboard – SkillForge Global</title>
      </Head>

      <AdminHeader 
        title="Mentor Dashboard" 
        showBackButton={true}
        backUrl="/mentors"
      />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-2">Welcome, Mentor! 👨‍🏫</h2>
          <p className="text-techGray">
            Status: <span className={`font-semibold ${
              (mentor?.status || '').toLowerCase() === 'approved' ? 'text-green-400' : 'text-yellow-400'
            }`}>{(mentor?.status || 'unknown').toUpperCase()}</span>
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Earnings */}
          <div className="bg-gradient-to-br from-green-500/20 to-green-500/5 border border-green-500/30 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-3xl">💰</span>
              <span className="text-green-400 text-sm font-medium">All Time</span>
            </div>
            <div className="text-3xl font-bold text-white mb-1">${stats.total_earnings.toFixed(2)}</div>
            <div className="text-sm text-techGray">Total Earnings</div>
            <div className="text-xs text-green-400 mt-2">
              +${stats.month_earnings.toFixed(2)} this month
            </div>
          </div>

          {/* Total Sessions */}
          <div className="bg-gradient-to-br from-techBlue/20 to-techBlue/5 border border-techBlue/30 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-3xl">📅</span>
              <span className="text-techBlue text-sm font-medium">Sessions</span>
            </div>
            <div className="text-3xl font-bold text-white mb-1">{stats.total_sessions}</div>
            <div className="text-sm text-techGray">Total Sessions</div>
            <div className="text-xs text-techBlue mt-2">
              {stats.completed_sessions} completed
            </div>
          </div>

          {/* Average Rating */}
          <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-500/5 border border-yellow-500/30 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-3xl">⭐</span>
              <span className="text-yellow-400 text-sm font-medium">Rating</span>
            </div>
            <div className="text-3xl font-bold text-white mb-1">{stats.average_rating.toFixed(1)}</div>
            <div className="text-sm text-techGray">Average Rating</div>
            <div className="text-xs text-yellow-400 mt-2">
              {stats.total_reviews} reviews
            </div>
          </div>

          {/* Unique Students */}
          <div className="bg-gradient-to-br from-forgePurple/20 to-forgePurple/5 border border-forgePurple/30 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-3xl">👥</span>
              <span className="text-forgePurple text-sm font-medium">Students</span>
            </div>
            <div className="text-3xl font-bold text-white mb-1">{stats.unique_students}</div>
            <div className="text-sm text-techGray">Total Students</div>
            <div className="text-xs text-forgePurple mt-2">
              {stats.month_sessions} sessions this month
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Upcoming Sessions */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Upcoming Sessions</h2>
              {upcoming_sessions.length === 0 ? (
                <div className="bg-white/5 border border-white/10 rounded-xl p-8 text-center">
                  <div className="text-4xl mb-4">📅</div>
                  <h3 className="text-xl font-semibold text-white mb-2">No upcoming sessions</h3>
                  <p className="text-techGray">Check back later for new session bookings</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {upcoming_sessions.map((session) => (
                    <div
                      key={session.id}
                      className="bg-white/5 border border-white/10 rounded-xl p-6 hover:border-techBlue/50 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-semibold text-white">{session.topic}</h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          session.status === 'confirmed' 
                            ? 'bg-green-500/20 text-green-400' 
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {session.status}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-techGray">
                        <span>📅 {new Date(session.scheduled_at).toLocaleDateString()}</span>
                        <span>⏱️ {session.duration_minutes} min</span>
                        <span>👤 Student #{session.student_id}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 gap-4">
                <Link
                  href="/mentors/dashboard/sessions"
                  className="bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl p-6 transition-colors"
                >
                  <div className="text-3xl mb-3">📋</div>
                  <h3 className="text-lg font-semibold text-white mb-2">All Sessions</h3>
                  <p className="text-sm text-techGray">View and manage all sessions</p>
                </Link>

                <Link
                  href="/mentors/dashboard/earnings"
                  className="bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl p-6 transition-colors"
                >
                  <div className="text-3xl mb-3">💵</div>
                  <h3 className="text-lg font-semibold text-white mb-2">Earnings</h3>
                  <p className="text-sm text-techGray">Detailed earnings breakdown</p>
                </Link>

                <Link
                  href="/mentors/dashboard/students"
                  className="bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl p-6 transition-colors"
                >
                  <div className="text-3xl mb-3">👨‍🎓</div>
                  <h3 className="text-lg font-semibold text-white mb-2">Students</h3>
                  <p className="text-sm text-techGray">View your student list</p>
                </Link>

                <Link
                  href="/mentors/dashboard/analytics"
                  className="bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl p-6 transition-colors"
                >
                  <div className="text-3xl mb-3">📊</div>
                  <h3 className="text-lg font-semibold text-white mb-2">Analytics</h3>
                  <p className="text-sm text-techGray">Performance insights</p>
                </Link>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Profile Summary */}
            <div>
              <h2 className="text-xl font-bold text-white mb-4">Your Profile</h2>
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <div className="mb-4">
                  <div className="text-sm text-techGray mb-1">Hourly Rate</div>
                  <div className="text-2xl font-bold text-white">${mentor.hourly_rate}/hr</div>
                </div>
                <div className="mb-4">
                  <div className="text-sm text-techGray mb-1">Expertise</div>
                  <div className="text-white">
                    {Array.isArray(mentor.expertise) 
                      ? mentor.expertise.join(', ') 
                      : (mentor.expertise || 'Not set')}
                  </div>
                </div>
                <Link
                  href="/mentors/dashboard/profile"
                  className="block w-full px-4 py-2 bg-forgePurple hover:bg-forgePurple/80 text-white text-center font-medium rounded-lg transition-colors"
                >
                  Edit Profile
                </Link>
              </div>
            </div>

            {/* Recent Reviews */}
            <div>
              <h2 className="text-xl font-bold text-white mb-4">Recent Reviews</h2>
              {recent_reviews.length === 0 ? (
                <div className="bg-white/5 border border-white/10 rounded-xl p-6 text-center">
                  <p className="text-techGray text-sm">No reviews yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {recent_reviews.slice(0, 3).map((review) => (
                    <div
                      key={review.id}
                      className="bg-white/5 border border-white/10 rounded-lg p-4"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-1">
                          {[...Array(5)].map((_, i) => (
                            <span key={i} className={i < review.rating ? 'text-yellow-400' : 'text-gray-600'}>
                              ⭐
                            </span>
                          ))}
                        </div>
                        <span className="text-xs text-techGray">
                          {new Date(review.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      {(review.review_text || review.comment) && (
                        <p className="text-sm text-techGray italic">"{review.review_text || review.comment}"</p>
                      )}
                    </div>
                  ))}
                  <Link
                    href="/mentors/dashboard/reviews"
                    className="block text-center text-sm text-techBlue hover:underline"
                  >
                    View all reviews →
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

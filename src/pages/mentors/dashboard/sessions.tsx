import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import DateRangePicker from '@/components/DateRangePicker'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'

type Session = {
  id: number
  student_id: number
  topic: string
  description: string
  scheduled_at: string
  duration_minutes: number
  status: string
  amount_paid: number
  meeting_link: string
  notes: string
  created_at: string
}

type SessionAction = 'confirm' | 'cancel' | 'complete'

export default function MentorSessions() {
  const router = useRouter()
  const [sessions, setSessions] = useState<Session[]>([])
  const [total, setTotal] = useState(0)
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  useEffect(() => {
    loadSessions()
  }, [filter, startDate, endDate])

  async function loadSessions() {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filter !== 'all') params.set('status', filter)
      if (startDate) params.set('start_date', startDate)
      if (endDate) params.set('end_date', endDate)
      
      const url = `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/mentor-portal/dashboard/sessions?${params.toString()}`
      
      const res = await fetch(url, { credentials: 'include' })

      if (res.status === 401) {
        router.push('/login?redirect=/mentors/dashboard/sessions')
        return
      }

      if (res.ok) {
        const data = await res.json()
        setSessions(data.sessions || [])
        setTotal(data.total || 0)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'completed': return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'cancelled': return 'bg-red-500/20 text-red-400 border-red-500/30'
      case 'pending': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  async function handleSessionAction(sessionId: number, action: SessionAction) {
    if (actionLoading) return
    
    const statusMap: Record<SessionAction, string> = {
      confirm: 'confirmed',
      cancel: 'cancelled',
      complete: 'completed'
    }
    
    setActionLoading(sessionId)
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/mentors/sessions/${sessionId}`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ status: statusMap[action] })
        }
      )

      if (res.status === 401) {
        router.push('/login?redirect=/mentors/dashboard/sessions')
        return
      }

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || 'Failed to update session')
      }

      // Reload sessions
      await loadSessions()
    } catch (err: any) {
      alert(err?.message || 'Failed to update session')
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <Layout>
      <Head>
        <title>My Sessions – Mentor Dashboard</title>
      </Head>

      <AdminHeader title="My Sessions" backUrl="/mentors/dashboard" />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Filter Tabs */}
        <div className="mb-6 flex gap-2 flex-wrap">
          {['all', 'pending', 'confirmed', 'completed', 'cancelled'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === status
                  ? 'bg-forgePurple text-white'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>

        {/* Date Range Filter */}
        <div className="mb-6">
          <DateRangePicker
            startDate={startDate}
            endDate={endDate}
            onStartChange={setStartDate}
            onEndChange={setEndDate}
            onClear={() => { setStartDate(''); setEndDate('') }}
          />
        </div>

        {/* Sessions List */}
        {loading ? (
          <div className="text-center py-12 text-techGray">Loading sessions...</div>
        ) : sessions.length === 0 ? (
          <div className="bg-white/5 border border-white/10 rounded-xl p-12 text-center">
            <div className="text-6xl mb-4">📅</div>
            <h3 className="text-xl font-semibold text-white mb-2">No sessions found</h3>
            <p className="text-techGray">
              {filter === 'all' ? 'You have no sessions yet' : `No ${filter} sessions`}
            </p>
          </div>
        ) : (
          <>
            <div className="mb-4 text-techGray">
              Showing {sessions.length} of {total} sessions
            </div>
            <div className="space-y-4">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className="bg-white/5 border border-white/10 rounded-xl p-6 hover:border-techBlue/50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">{session.topic}</h3>
                      {session.description && (
                        <p className="text-techGray mb-3">{session.description}</p>
                      )}
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(session.status)}`}>
                      {session.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <div className="text-xs text-techGray mb-1">Scheduled</div>
                      <div className="text-white font-medium">
                        {new Date(session.scheduled_at).toLocaleDateString()}
                      </div>
                      <div className="text-sm text-techGray">
                        {new Date(session.scheduled_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </div>
                    </div>

                    <div>
                      <div className="text-xs text-techGray mb-1">Duration</div>
                      <div className="text-white font-medium">{session.duration_minutes} min</div>
                    </div>

                    <div>
                      <div className="text-xs text-techGray mb-1">Student</div>
                      <div className="text-white font-medium">ID #{session.student_id}</div>
                    </div>

                    <div>
                      <div className="text-xs text-techGray mb-1">Amount</div>
                      <div className="text-white font-medium">${session.amount_paid.toFixed(2)}</div>
                    </div>
                  </div>

                  {session.meeting_link && (
                    <div className="mb-3">
                      <a
                        href={session.meeting_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-techBlue hover:underline text-sm"
                      >
                        🔗 Join Meeting
                      </a>
                    </div>
                  )}

                  {session.notes && (
                    <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                      <div className="text-xs text-techGray mb-1">Notes:</div>
                      <div className="text-sm text-white">{session.notes}</div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2 mt-4">
                    {session.status === 'pending' && (
                      <>
                        <button
                          onClick={() => handleSessionAction(session.id, 'confirm')}
                          disabled={actionLoading === session.id}
                          className="px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 border border-green-500/30 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                        >
                          {actionLoading === session.id ? 'Processing...' : '✓ Confirm'}
                        </button>
                        <button
                          onClick={() => handleSessionAction(session.id, 'cancel')}
                          disabled={actionLoading === session.id}
                          className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                        >
                          {actionLoading === session.id ? 'Processing...' : '✗ Cancel'}
                        </button>
                      </>
                    )}
                    {session.status === 'confirmed' && (
                      <>
                        <button
                          onClick={() => handleSessionAction(session.id, 'complete')}
                          disabled={actionLoading === session.id}
                          className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 border border-blue-500/30 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                        >
                          {actionLoading === session.id ? 'Processing...' : '✓ Mark Complete'}
                        </button>
                        <button
                          onClick={() => handleSessionAction(session.id, 'cancel')}
                          disabled={actionLoading === session.id}
                          className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                        >
                          {actionLoading === session.id ? 'Processing...' : '✗ Cancel'}
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </Layout>
  )
}

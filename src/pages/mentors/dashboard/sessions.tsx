import Head from 'next/head'
import DashboardLayout from '@/components/DashboardLayout'
import DashboardListItem from '@/components/DashboardListItem'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { DashboardListSkeleton } from '@/components/DashboardSkeletons'

type Session = {
  id: number
  student_id: number
  topic: string
  description?: string
  scheduled_at: string
  duration_minutes: number
  price: number
  payment_status?: string
  status: string
  meeting_link?: string
  notes?: string
  created_at: string
}

type SessionAction = 'confirm' | 'cancel' | 'complete'

type PaginatedResponse = {
  sessions: Session[]
  total: number
  completed: number
}

export default function MentorSessions() {
  const router = useRouter()
  const [data, setData] = useState<PaginatedResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState<'all' | 'pending' | 'confirmed' | 'completed' | 'cancelled'>('all')
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [showCancelModal, setShowCancelModal] = useState(false)
  const [cancelReason, setCancelReason] = useState('')
  const [cancelingSession, setCancelingSession] = useState<Session | null>(null)

  useEffect(() => {
    loadSessions()
  }, [filter])

  async function loadSessions() {
    setLoading(true)
    setError('')
    try {
      const url = new URL(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/mentor-portal/dashboard/sessions`)
      if (filter !== 'all') url.searchParams.append('status', filter)
      
      const res = await fetch(url.toString(), {
        credentials: 'include'
      })

      if (res.status === 401) {
        router.push('/login?redirect=/mentors/dashboard/sessions')
        return
      }

      if (res.status === 404 || res.status === 403) {
        setError('Not authorized to view sessions')
        return
      }

      if (res.ok) {
        const sessionsData = await res.json()
        setData(sessionsData)
      } else {
        setError('Failed to load sessions')
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load sessions')
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

  async function handleSessionAction(sessionId: number, action: SessionAction, notes?: string) {
    if (actionLoading) return
    
    const statusMap: Record<SessionAction, string> = {
      confirm: 'confirmed',
      cancel: 'cancelled',
      complete: 'completed'
    }
    
    setActionLoading(sessionId)
    try {
      const payload: any = { status: statusMap[action] }
      if (notes) {
        payload.mentor_notes = notes
      }
      
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/mentors/sessions/${sessionId}`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload)
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

      await loadSessions()
      setShowCancelModal(false)
      setCancelReason('')
      setCancelingSession(null)
    } catch (err: any) {
      alert(err?.message || 'Failed to update session')
    } finally {
      setActionLoading(null)
    }
  }

  function handleCancelClick(session: Session) {
    setCancelingSession(session)
    setShowCancelModal(true)
  }

  function handleCancelConfirm() {
    if (cancelingSession) {
      handleSessionAction(cancelingSession.id, 'cancel', cancelReason)
    }
  }

  if (loading) {
    return (
      <DashboardLayout
        title="My Sessions"
        breadcrumbs={[
          { label: 'Dashboard', href: '/mentors/dashboard' },
          { label: 'Sessions' }
        ]}
      >
        <DashboardListSkeleton count={5} />
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout
        title="My Sessions"
        breadcrumbs={[
          { label: 'Dashboard', href: '/mentors/dashboard' },
          { label: 'Sessions' }
        ]}
      >
        <div className="text-center text-red-400 py-12">
          {error}
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout
      title="My Sessions"
      subtitle={`Total: ${data?.total || 0} sessions | Completed: ${data?.completed || 0}`}
      breadcrumbs={[
        { label: 'Dashboard', href: '/mentors/dashboard' },
        { label: 'Sessions' }
      ]}
    >
      <Head>
        <title>My Sessions – Mentor Dashboard</title>
      </Head>

      <div className="space-y-6">
        {/* Filter Tabs */}
        <div className="mb-6 flex gap-2 flex-wrap">
          {(['all', 'pending', 'confirmed', 'completed', 'cancelled'] as const).map((status) => (
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

        {/* Sessions List */}
        {(data?.sessions && data.sessions.length === 0) ? (
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
              Showing {data?.sessions?.length || 0} of {data?.total || 0} sessions
            </div>
            <div className="space-y-4">
              {data?.sessions?.map((session) => (
                <div
                  key={session.id}
                  data-testid="session-row"
                  data-status={session.status}
                  className="bg-white/5 border border-white/10 rounded-xl p-6 hover:border-techBlue/50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 data-testid="session-topic" className="text-xl font-bold text-white mb-2">{session.topic}</h3>
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
                      <div className="text-white font-medium">${session.price?.toFixed(2) || '$0.00'}</div>
                      {session.payment_status && (
                        <div className="text-xs text-techGray mt-1">
                          Status: {session.payment_status}
                        </div>
                      )}
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
                    <div className="bg-white/5 border border-white/10 rounded-lg p-3 mb-4">
                      <div className="text-xs text-techGray mb-1">Notes:</div>
                      <div className="text-sm text-white">{session.notes}</div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2 mt-4 flex-wrap">
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
                          onClick={() => handleCancelClick(session)}
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
                          onClick={() => handleCancelClick(session)}
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

      {/* Cancel Modal */}
      {showCancelModal && cancelingSession && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div
            role="dialog"
            className="bg-deepNavy border border-white/10 rounded-xl p-6 max-w-md w-full"
          >
            <h3 className="text-xl font-bold text-white mb-4">Cancel Session</h3>
            <p className="text-techGray mb-4">
              Please provide a reason for cancelling this session:
            </p>
            <textarea
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              placeholder="Reason for cancellation..."
              aria-label="reason"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-techGray focus:outline-none focus:border-techBlue resize-none"
              rows={4}
            />
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setShowCancelModal(false)
                  setCancelReason('')
                  setCancelingSession(null)
                }}
                disabled={actionLoading !== null}
                className="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                Nevermind
              </button>
              <button
                onClick={handleCancelConfirm}
                disabled={actionLoading !== null || !cancelReason.trim()}
                className="flex-1 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {actionLoading !== null ? 'Cancelling...' : 'Confirm Cancel'}
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  )
}

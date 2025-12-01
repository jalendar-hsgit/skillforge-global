import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth'

type Session = {
  id: number
  mentor_id: number
  student_id: number
  topic: string
  scheduled_at: string
  duration_minutes: number
  status: 'scheduled' | 'completed' | 'cancelled' | 'no_show'
  price: number
  meeting_url?: string
  mentor_notes?: string
  student_feedback?: string
  rating?: number
  created_at: string
}

export default function AdminSessions({ me }: AdminSSRProps) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [filter, setFilter] = useState<'all' | 'scheduled' | 'completed' | 'cancelled' | 'no_show'>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSessions()
  }, [filter])

  async function loadSessions() {
    setLoading(true)
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/sessions?status=${filter === 'all' ? '' : filter}`, {
        credentials: 'include'
      })
      if (!res.ok) throw new Error('Failed to fetch sessions')
      const data = await res.json()
      setSessions(data.sessions || [])
    } catch (err) {
      console.error(err)
      setSessions([])
    } finally {
      setLoading(false)
    }
  }

  async function updateSessionStatus(sessionId: number, newStatus: 'cancelled' | 'no_show') {
    if (!confirm(`Are you sure you want to mark this session as ${newStatus}?`)) {
      return
    }
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/admin/sessions/${sessionId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status: newStatus })
      })
      
      if (!res.ok) {
        const err = await res.text()
        alert(`Failed to update session: ${err}`)
        return
      }
      
      alert(`Session status updated to ${newStatus}`)
      loadSessions()
    } catch (err) {
      console.error(err)
      alert('Error updating session')
    }
  }

  const statusColors = {
    scheduled: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    completed: 'bg-green-500/20 text-green-300 border-green-500/30',
    cancelled: 'bg-red-500/20 text-red-300 border-red-500/30',
    no_show: 'bg-orange-500/20 text-orange-300 border-orange-500/30'
  }

  return (
    <Layout>
      <Head><title>{`Admin – Sessions`}</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        <h1 className="text-3xl font-semibold mb-2">Session Management</h1>
        <p className="text-techGray mb-6">Review and moderate all mentoring sessions · Signed in as {me.email}</p>

        <div className="mb-6 flex flex-col md:flex-row gap-4">
          <select 
            className="h-12 rounded-md bg-white/5 border border-white/10 px-4" 
            value={filter} 
            onChange={(e)=>setFilter(e.target.value as any)}
          >
            <option value="all">All Sessions</option>
            <option value="scheduled">Scheduled</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
            <option value="no_show">No Show</option>
          </select>
        </div>

        {loading ? (
          <div className="text-techGray">Loading sessions...</div>
        ) : sessions.length === 0 ? (
          <div className="rounded-xl border border-white/10 p-8 bg-white/[0.06] text-center text-techGray">
            No sessions found for filter: {filter}
          </div>
        ) : (
          <div className="space-y-4">
            {sessions.map((s) => (
              <div key={s.id} className="rounded-xl border border-white/10 p-6 bg-white/[0.06] hover:bg-white/[0.08] transition">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">Session #{s.id}</h3>
                      <span className={`text-xs px-3 py-1 rounded-full border ${statusColors[s.status]}`}>
                        {s.status}
                      </span>
                    </div>
                    <p className="text-sm mb-2"><strong>Topic:</strong> {s.topic}</p>
                    <p className="text-sm text-techGray mb-1">
                      <strong>Scheduled:</strong> {new Date(s.scheduled_at).toLocaleString()} ({s.duration_minutes} min)
                    </p>
                    <p className="text-sm text-techGray mb-1">
                      <strong>Mentor ID:</strong> {s.mentor_id} | <strong>Student ID:</strong> {s.student_id}
                    </p>
                    <p className="text-sm text-techGray mb-2">
                      <strong>Price:</strong> ${s.price}
                    </p>
                    {s.meeting_url && (
                      <p className="text-sm mb-2">
                        <strong>Meeting:</strong> <a href={s.meeting_url} target="_blank" rel="noopener noreferrer" className="text-neuralBlue hover:underline">{s.meeting_url}</a>
                      </p>
                    )}
                    {s.mentor_notes && (
                      <p className="text-sm mb-2"><strong>Mentor Notes:</strong> {s.mentor_notes}</p>
                    )}
                    {s.student_feedback && (
                      <p className="text-sm mb-2"><strong>Student Feedback:</strong> {s.student_feedback}</p>
                    )}
                    {s.rating && (
                      <p className="text-sm mb-2"><strong>Rating:</strong> ⭐ {s.rating}</p>
                    )}
                  </div>

                  <div className="flex flex-col gap-2 min-w-[140px]">
                    <Link
                      href={`/mentors/sessions/${s.id}`}
                      className="h-10 rounded-md bg-neuralBlue hover:bg-neuralBlue/80 px-4 text-sm font-semibold transition flex items-center justify-center"
                    >
                      View Details
                    </Link>
                    {s.status === 'scheduled' && (
                      <>
                        <button
                          onClick={() => updateSessionStatus(s.id, 'cancelled')}
                          className="h-10 rounded-md bg-red-600 hover:bg-red-700 px-4 text-sm font-semibold transition"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => updateSessionStatus(s.id, 'no_show')}
                          className="h-10 rounded-md bg-orange-600 hover:bg-orange-700 px-4 text-sm font-semibold transition"
                        >
                          Mark No Show
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </Layout>
  )
}

export const getServerSideProps = requireAdminSSR

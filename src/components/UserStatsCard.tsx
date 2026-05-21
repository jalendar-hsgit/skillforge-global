// src/components/UserStatsCard.tsx
import { useState, useEffect } from 'react'
import { BookOpen, Star, Clock, AlertCircle } from 'lucide-react'

interface UserStats {
  sessions_completed: number
  avg_rating: number
  total_hours: number
  recent_sessions?: Array<{
    id: number
    title: string
    date: string
  }>
}

export default function UserStatsCard() {
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/v1x/account/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        setStats(await res.json())
      } else {
        setError('Failed to load statistics')
      }
    } catch (err) {
      setError('Error fetching statistics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-lg border border-white/10 p-8 text-center backdrop-blur-sm">
        <div className="text-white/60">Loading statistics...</div>
      </div>
    )
  }
  if (!stats) {
    return (
      <div className="bg-gradient-to-br from-red-500/10 to-red-600/5 rounded-lg border border-red-500/20 px-4 py-3 backdrop-blur-sm flex items-center gap-2">
        <AlertCircle className="w-5 h-5 text-red-400" />
        <div className="text-red-300">Failed to load statistics</div>
      </div>
    )
  }

  const StatItem = ({ icon: Icon, label, value, unit = '' }: any) => (
    <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-lg border border-white/10 p-4 backdrop-blur-sm">
      <div className="flex items-center gap-3 mb-2">
        <Icon className="w-5 h-5 text-blue-400" />
        <span className="text-xs text-white/60 font-medium uppercase tracking-wider">{label}</span>
      </div>
      <p className="text-3xl font-bold text-white">
        {value}
        <span className="text-lg text-white/50 ml-1">{unit}</span>
      </p>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatItem
          icon={BookOpen}
          label="Sessions Completed"
          value={stats.sessions_completed}
        />
        <StatItem
          icon={Star}
          label="Average Rating"
          value={stats.avg_rating.toFixed(1)}
          unit="★"
        />
        <StatItem
          icon={Clock}
          label="Total Hours"
          value={stats.total_hours}
          unit="hrs"
        />
        <StatItem
          icon={BookOpen}
          label="Courses"
          value={stats.sessions_completed > 0 ? Math.ceil(stats.sessions_completed / 3) : 0}
        />
      </div>

      {/* Recent Sessions */}
      {stats.recent_sessions && stats.recent_sessions.length > 0 && (
        <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-lg border border-white/10 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">Recent Sessions</h3>
          <div className="space-y-3">
            {stats.recent_sessions.map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors"
              >
                <div>
                  <p className="font-medium text-white">{session.title}</p>
                  <p className="text-sm text-white/60">{session.date}</p>
                </div>
                <button className="text-blue-400 hover:text-blue-300 font-medium text-sm">
                  View Details →
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {(!stats.recent_sessions || stats.recent_sessions.length === 0) && (
        <div className="bg-gradient-to-br from-white/10 to-white/5 rounded-lg border border-white/10 p-6 text-center backdrop-blur-sm">
          <BookOpen className="w-12 h-12 text-white/30 mx-auto mb-3" />
          <p className="text-white/60">No sessions yet. Start learning to build your stats!</p>
        </div>
      )}
    </div>
  )
}

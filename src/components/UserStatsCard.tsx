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
    return <div className="text-center py-8">Loading statistics...</div>
  }

  if (!stats) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
        <AlertCircle className="w-5 h-5" />
        {error}
      </div>
    )
  }

  const StatItem = ({ icon: Icon, label, value, unit = '' }: any) => (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center gap-3 mb-2">
        <Icon className="w-5 h-5 text-blue-600" />
        <span className="text-sm text-gray-600">{label}</span>
      </div>
      <p className="text-2xl font-bold">
        {value}
        <span className="text-lg text-gray-500 ml-1">{unit}</span>
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
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-bold mb-4">Recent Sessions</h3>
          <div className="space-y-3">
            {stats.recent_sessions.map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900">{session.title}</p>
                  <p className="text-sm text-gray-500">{session.date}</p>
                </div>
                <button className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                  View Details →
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {(!stats.recent_sessions || stats.recent_sessions.length === 0) && (
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-6 text-center">
          <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600">No sessions yet. Start learning to build your stats!</p>
        </div>
      )}
    </div>
  )
}

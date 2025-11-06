import Head from 'next/head'
import Layout from '@/components/Layout'
import { useEffect, useState } from 'react'

type Stats = {
  total_generated: number
  last_24h: number
  total_sessions: number
  completed_sessions: number
  avg_score_pct: number
  top_topics: { topic: string; count: number }[]
  providers: { provider: string; count: number }[]
  difficulties: { difficulty: string; count: number }[]
}

type RecentQuiz = {
  id: number
  user_id: number
  topic: string
  difficulty: string
  num_questions: number
  provider: string | null
  model: string | null
  times_taken: number
  created_at: string | null
  is_favorite: boolean
}

export default function AdminQuizzesPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [recent, setRecent] = useState<RecentQuiz[]>([])
  const [err, setErr] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('/api/session/v1x/admin/quizzes/stats', { credentials: 'include' })
        .then(r => r.ok ? r.json() : Promise.reject(r.statusText)),
      fetch('/api/session/v1x/admin/quizzes/recent?limit=15', { credentials: 'include' })
        .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
    ])
      .then(([statsData, recentData]) => {
        setStats(statsData)
        setRecent(recentData)
        setLoading(false)
      })
      .catch(e => {
        setErr(String(e))
        setLoading(false)
      })
  }, [])

  return (
    <Layout>
      <Head><title>Admin - AI Quiz Analytics</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-forgePurple to-neuralBlue bg-clip-text text-transparent">
          AI Quiz Analytics
        </h1>
        <p className="mt-2 text-techGray">Real-time monitoring of quiz generation activity</p>

        {err && (
          <div className="mt-6 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-red-300">
            {err}
          </div>
        )}

        {loading && <div className="mt-8 text-techGray">Loading analytics...</div>}

        {stats && (
          <>
            {/* Overview Stats */}
            <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard label="Total Generated" value={stats.total_generated.toLocaleString()} />
              <StatCard label="Last 24 Hours" value={stats.last_24h.toLocaleString()} />
              <StatCard label="Quiz Sessions" value={stats.total_sessions.toLocaleString()} />
              <StatCard label="Avg Score" value={`${stats.avg_score_pct}%`} />
            </div>

            {/* Charts Grid */}
            <div className="mt-8 grid gap-6 lg:grid-cols-2">
              {/* Top Topics */}
              <div className="rounded-xl border border-white/10 p-6 bg-white/[0.03]">
                <h2 className="text-xl font-semibold">Top Topics</h2>
                <div className="mt-4 space-y-2">
                  {stats.top_topics.map((t, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <span className="text-white/90">{t.topic}</span>
                      <span className="font-mono text-techGray">{t.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Provider Distribution */}
              <div className="rounded-xl border border-white/10 p-6 bg-white/[0.03]">
                <h2 className="text-xl font-semibold">Providers</h2>
                <div className="mt-4 space-y-2">
                  {stats.providers.map((p, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <span className="text-white/90">{p.provider}</span>
                      <span className="font-mono text-techGray">{p.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Difficulty Distribution */}
              <div className="rounded-xl border border-white/10 p-6 bg-white/[0.03]">
                <h2 className="text-xl font-semibold">Difficulty Levels</h2>
                <div className="mt-4 space-y-2">
                  {stats.difficulties.map((d, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <span className="text-white/90 capitalize">{d.difficulty}</span>
                      <span className="font-mono text-techGray">{d.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Session Completion */}
              <div className="rounded-xl border border-white/10 p-6 bg-white/[0.03]">
                <h2 className="text-xl font-semibold">Session Completion</h2>
                <div className="mt-4">
                  <div className="text-3xl font-bold">
                    {stats.total_sessions > 0 
                      ? Math.round((stats.completed_sessions / stats.total_sessions) * 100)
                      : 0}%
                  </div>
                  <div className="mt-1 text-sm text-techGray">
                    {stats.completed_sessions} / {stats.total_sessions} completed
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Quizzes Table */}
            <div className="mt-8 rounded-xl border border-white/10 overflow-hidden bg-white/[0.03]">
              <div className="px-6 py-4 border-b border-white/10">
                <h2 className="text-xl font-semibold">Recent Generations</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-white/[0.03] text-techGray">
                    <tr>
                      <th className="px-4 py-3 text-left">ID</th>
                      <th className="px-4 py-3 text-left">Topic</th>
                      <th className="px-4 py-3 text-left">Difficulty</th>
                      <th className="px-4 py-3 text-left">Questions</th>
                      <th className="px-4 py-3 text-left">Provider</th>
                      <th className="px-4 py-3 text-left">Times Taken</th>
                      <th className="px-4 py-3 text-left">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recent.map((q) => (
                      <tr key={q.id} className="border-t border-white/5 hover:bg-white/[0.02]">
                        <td className="px-4 py-3 font-mono text-techGray">#{q.id}</td>
                        <td className="px-4 py-3 text-white/90">{q.topic}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                            q.difficulty === 'easy' ? 'bg-green-500/20 text-green-300' :
                            q.difficulty === 'hard' ? 'bg-red-500/20 text-red-300' :
                            'bg-yellow-500/20 text-yellow-300'
                          }`}>
                            {q.difficulty}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-techGray">{q.num_questions}</td>
                        <td className="px-4 py-3 text-techGray">{q.provider || 'N/A'}</td>
                        <td className="px-4 py-3 text-techGray">{q.times_taken}</td>
                        <td className="px-4 py-3 text-techGray">
                          {q.created_at ? new Date(q.created_at).toLocaleString() : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </section>
    </Layout>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 p-6 bg-white/[0.03]">
      <div className="text-sm text-techGray">{label}</div>
      <div className="mt-2 text-3xl font-bold">{value}</div>
    </div>
  )
}

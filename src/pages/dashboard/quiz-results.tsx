import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'

type QuizAttempt = {
  id: number
  quiz_id: number
  quiz_title: string
  score: number
  passed: boolean
  created_at: string
  answers?: any
}

export default function QuizResultsPage() {
  const router = useRouter()
  const [attempts, setAttempts] = useState<QuizAttempt[]>([])
  const [stats, setStats] = useState({
    total: 0,
    passed: 0,
    avgScore: 0,
    bestScore: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadQuizResults()
  }, [])

  async function loadQuizResults() {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/student/dashboard/quiz-results`, {
        credentials: 'include'
      })

      if (res.status === 401) {
        router.push('/login?redirect=/dashboard/quiz-results')
        return
      }

      if (res.ok) {
        const data = await res.json()
        const quizAttempts = data.quiz_attempts || []
        setAttempts(quizAttempts)

        // Calculate stats
        if (quizAttempts.length > 0) {
          const scores = quizAttempts.map((a: QuizAttempt) => a.score)
          setStats({
            total: quizAttempts.length,
            passed: quizAttempts.filter((a: QuizAttempt) => a.passed).length,
            avgScore: Math.round(scores.reduce((a: number, b: number) => a + b, 0) / scores.length),
            bestScore: Math.max(...scores)
          })
        }
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-techGray">Loading quiz results...</div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <Head>
        <title>Quiz Results – SkillForge Global</title>
      </Head>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <Link href="/dashboard" className="text-techBlue hover:underline mb-4 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-white mb-2">Quiz Results</h1>
          <p className="text-techGray">Your complete quiz history and performance</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <div className="text-3xl mb-2">📝</div>
            <div className="text-2xl font-bold text-white">{stats.total}</div>
            <div className="text-sm text-techGray">Total Attempts</div>
          </div>

          <div className="bg-gradient-to-br from-green-500/20 to-green-500/5 border border-green-500/30 rounded-xl p-6">
            <div className="text-3xl mb-2">✅</div>
            <div className="text-2xl font-bold text-white">{stats.passed}</div>
            <div className="text-sm text-techGray">Passed</div>
          </div>

          <div className="bg-gradient-to-br from-techBlue/20 to-techBlue/5 border border-techBlue/30 rounded-xl p-6">
            <div className="text-3xl mb-2">📊</div>
            <div className="text-2xl font-bold text-white">{stats.avgScore}%</div>
            <div className="text-sm text-techGray">Average Score</div>
          </div>

          <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-500/5 border border-yellow-500/30 rounded-xl p-6">
            <div className="text-3xl mb-2">🏆</div>
            <div className="text-2xl font-bold text-white">{stats.bestScore}%</div>
            <div className="text-sm text-techGray">Best Score</div>
          </div>
        </div>

        {/* Quiz Attempts List */}
        {attempts.length === 0 ? (
          <div className="bg-white/5 border border-white/10 rounded-xl p-12 text-center">
            <div className="text-6xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold text-white mb-2">No quiz attempts yet</h3>
            <p className="text-techGray mb-6">Test your knowledge by taking a quiz!</p>
            <Link
              href="/paths"
              className="inline-block px-6 py-3 bg-forgePurple hover:bg-forgePurple/80 text-white font-medium rounded-lg transition-colors"
            >
              Browse Quizzes
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-white mb-4">All Attempts ({attempts.length})</h2>
            {attempts.map((attempt) => (
              <div
                key={attempt.id}
                className={`bg-white/5 border rounded-xl p-6 ${
                  attempt.passed 
                    ? 'border-green-500/30 hover:border-green-500/50' 
                    : 'border-red-500/30 hover:border-red-500/50'
                } transition-colors`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-2">
                      {attempt.quiz_title}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-techGray">
                      <span>
                        {new Date(attempt.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    {/* Score */}
                    <div className="text-center">
                      <div className={`text-3xl font-bold ${
                        attempt.score >= 70 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {attempt.score}%
                      </div>
                      <div className="text-xs text-techGray">Score</div>
                    </div>

                    {/* Status Badge */}
                    <div>
                      {attempt.passed ? (
                        <span className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/20 border border-green-500/30 rounded-lg text-green-400 font-medium">
                          <span className="text-xl">✅</span>
                          Passed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 font-medium">
                          <span className="text-xl">❌</span>
                          Failed
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Score Visualization */}
                <div className="mt-4">
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        attempt.score >= 70 
                          ? 'bg-gradient-to-r from-green-500 to-green-400'
                          : 'bg-gradient-to-r from-red-500 to-red-400'
                      }`}
                      style={{ width: `${attempt.score}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}

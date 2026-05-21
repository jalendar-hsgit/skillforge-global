import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { PageHeader, PageContainer, PageSection } from '@/components/PageLayout'
import { CheckCircle, XCircle, Clock, Code, Trophy, TrendingUp, Calendar, Filter } from 'lucide-react'
import Link from 'next/link'
import type { GetServerSideProps } from 'next'

type Submission = {
  id: number
  challenge_id: number
  challenge_title: string
  challenge_slug: string
  language: string
  status: string
  score: number
  passed_tests: number
  total_tests: number
  execution_time_ms: number
  coins_earned: number
  submitted_at: string
}

export const getServerSideProps: GetServerSideProps = async (ctx) => {
  const base = `http://${ctx.req.headers.host}`
  const r = await fetch(`${base}/api/session/me`, {
    headers: { cookie: ctx.req.headers.cookie || '' }
  })
  if (!r.ok) {
    return { redirect: { destination: '/login', permanent: false } }
  }
  return { props: {} }
}

const statusColors = {
  success: 'bg-green-500/20 text-green-400 border-green-500/30',
  failed: 'bg-red-500/20 text-red-400 border-red-500/30',
  running: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  error: 'bg-orange-500/20 text-orange-400 border-orange-500/30'
}

export default function Submissions() {
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'success' | 'failed'>('all')

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

  useEffect(() => {
    fetchSubmissions()
  }, [])

  const fetchSubmissions = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1x/coding-practice/my-submissions?limit=50`, {
        credentials: 'include'
      })
      if (res.ok) {
        const data = await res.json()
        setSubmissions(data)
      }
    } catch (error) {
      console.error('Failed to fetch submissions:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredSubmissions = submissions.filter(s => {
    if (filter === 'all') return true
    return s.status === filter
  })

  const totalSubmissions = submissions.length
  const successfulSubmissions = submissions.filter(s => s.score >= 100).length
  const averageScore = submissions.length > 0 
    ? submissions.reduce((sum, s) => sum + s.score, 0) / submissions.length 
    : 0
  const totalCoins = submissions.reduce((sum, s) => sum + s.coins_earned, 0)

  return (
    <Layout maxWidth="7xl">
      <Head>
        <title>My Submissions – SkillForge Global</title>
      </Head>

      <PageHeader
        icon="📊"
        title="My Submissions"
        subtitle="Track your coding practice progress and performance"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Practice', href: '/practice' },
          { label: 'Submissions' }
        ]}
      />

      {/* Stats Overview */}
      <PageSection>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-6 rounded-2xl bg-gradient-to-br from-forgePurple/20 to-neuralBlue/20 border border-forgePurple/30">
            <div className="flex items-center justify-between mb-4">
              <Code className="w-8 h-8 text-forgePurple" />
            </div>
            <div className="text-3xl font-bold text-white mb-1">{totalSubmissions}</div>
            <div className="text-sm text-gray-400">Total Submissions</div>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30">
            <div className="flex items-center justify-between mb-4">
              <CheckCircle className="w-8 h-8 text-green-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-1">{successfulSubmissions}</div>
            <div className="text-sm text-gray-400">Perfect Scores</div>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/30">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="w-8 h-8 text-blue-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-1">{averageScore.toFixed(1)}%</div>
            <div className="text-sm text-gray-400">Average Score</div>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/30">
            <div className="flex items-center justify-between mb-4">
              <Trophy className="w-8 h-8 text-yellow-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-1">{totalCoins}</div>
            <div className="text-sm text-gray-400">Coins Earned</div>
          </div>
        </div>
      </PageSection>

      {/* Submissions List */}
      <PageSection>
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white">Recent Submissions</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-forgePurple text-white'
                  : 'bg-darkNavy text-gray-400 hover:text-white'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('success')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'success'
                  ? 'bg-green-600 text-white'
                  : 'bg-darkNavy text-gray-400 hover:text-white'
              }`}
            >
              Success
            </button>
            <button
              onClick={() => setFilter('failed')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'failed'
                  ? 'bg-red-600 text-white'
                  : 'bg-darkNavy text-gray-400 hover:text-white'
              }`}
            >
              Failed
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-forgePurple mx-auto"></div>
            <p className="text-gray-400 mt-4">Loading submissions...</p>
          </div>
        ) : filteredSubmissions.length === 0 ? (
          <div className="text-center py-12 border border-techBlue/20 rounded-2xl">
            <Code className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No submissions yet</h3>
            <p className="text-gray-400 mb-6">Start solving challenges to see your progress here</p>
            <Link
              href="/practice"
              className="inline-block px-6 py-3 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue text-white font-medium hover:shadow-lg hover:shadow-forgePurple/50 transition-all"
            >
              Browse Challenges
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredSubmissions.map((submission) => (
              <div
                key={submission.id}
                className="p-6 rounded-2xl bg-darkNavy/50 border border-techBlue/20 hover:border-techBlue/40 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Link
                        href={`/practice/${submission.challenge_slug}`}
                        className="text-lg font-semibold text-white hover:text-forgePurple transition-colors"
                      >
                        {submission.challenge_title}
                      </Link>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${statusColors[submission.status as keyof typeof statusColors]}`}>
                        {submission.status}
                      </span>
                    </div>

                    <div className="flex items-center gap-6 text-sm text-gray-400">
                      <div className="flex items-center gap-2">
                        <Code className="w-4 h-4" />
                        <span>{submission.language}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        <span>{submission.passed_tests}/{submission.total_tests} tests</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        <span>{submission.execution_time_ms}ms</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        <span>{new Date(submission.submitted_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-2xl font-bold text-white mb-1">
                      {submission.score}%
                    </div>
                    {submission.coins_earned > 0 && (
                      <div className="flex items-center gap-1 text-sm text-yellow-400">
                        <Trophy className="w-4 h-4" />
                        <span>+{submission.coins_earned} coins</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </PageSection>
    </Layout>
  )
}

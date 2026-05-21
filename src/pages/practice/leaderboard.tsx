import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { PageHeader, PageContainer, PageSection } from '@/components/PageLayout'
import { Trophy, Medal, Award, TrendingUp, Star, Code, Zap } from 'lucide-react'
import type { GetServerSideProps } from 'next'

type LeaderboardEntry = {
  rank: number
  user_id: number
  username: string
  avatar?: string
  total_score: number
  challenges_completed: number
  perfect_solutions: number
  coins_earned: number
  success_rate: number
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

export default function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [timeframe, setTimeframe] = useState<'all' | 'month' | 'week'>('all')

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true)
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/coding-practice/leaderboard?timeframe=${timeframe}&limit=50`)
        if (!res.ok) {
          console.error('Failed to fetch leaderboard:', res.status)
          // Fallback to empty
          setLeaderboard([])
          return
        }
        const data = await res.json()
        setLeaderboard(data || [])
      } catch (error) {
        console.error('Error fetching leaderboard:', error)
        setLeaderboard([])
      } finally {
        setLoading(false)
      }
    }
    
    fetchLeaderboard()
  }, [timeframe])

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="w-6 h-6 text-yellow-400" />
    if (rank === 2) return <Medal className="w-6 h-6 text-gray-400" />
    if (rank === 3) return <Medal className="w-6 h-6 text-orange-400" />
    return <span className="text-lg font-bold text-gray-400">#{rank}</span>
  }

  const getRankBg = (rank: number) => {
    if (rank === 1) return 'from-yellow-500/20 to-orange-500/20 border-yellow-500/30'
    if (rank === 2) return 'from-gray-400/20 to-gray-500/20 border-gray-400/30'
    if (rank === 3) return 'from-orange-500/20 to-red-500/20 border-orange-500/30'
    return 'from-forgePurple/10 to-neuralBlue/10 border-techBlue/20'
  }

  return (
    <Layout maxWidth="7xl">
      <Head>
        <title>Leaderboard – SkillForge Global</title>
      </Head>

      <PageHeader
        icon="🏆"
        title="Coding Practice Leaderboard"
        subtitle="Compete with the best coders and climb the ranks"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Practice', href: '/practice' },
          { label: 'Leaderboard' }
        ]}
      />

      {/* Timeframe Selector */}
      <PageSection>
        <div className="flex justify-center gap-2 mb-8">
          <button
            onClick={() => setTimeframe('week')}
            className={`px-6 py-3 rounded-lg text-sm font-medium transition-all ${
              timeframe === 'week'
                ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white shadow-lg'
                : 'bg-darkNavy text-gray-400 hover:text-white'
            }`}
          >
            This Week
          </button>
          <button
            onClick={() => setTimeframe('month')}
            className={`px-6 py-3 rounded-lg text-sm font-medium transition-all ${
              timeframe === 'month'
                ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white shadow-lg'
                : 'bg-darkNavy text-gray-400 hover:text-white'
            }`}
          >
            This Month
          </button>
          <button
            onClick={() => setTimeframe('all')}
            className={`px-6 py-3 rounded-lg text-sm font-medium transition-all ${
              timeframe === 'all'
                ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white shadow-lg'
                : 'bg-darkNavy text-gray-400 hover:text-white'
            }`}
          >
            All Time
          </button>
        </div>

        {/* Top 3 Podium */}
        {!loading && leaderboard.length >= 3 && (
          <div className="grid grid-cols-3 gap-4 mb-8 max-w-4xl mx-auto">
            {/* 2nd Place */}
            <div className="pt-12">
              <div className="p-6 rounded-2xl bg-gradient-to-br from-gray-400/20 to-gray-500/20 border border-gray-400/30 text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-gray-400 to-gray-500 flex items-center justify-center mx-auto mb-4">
                  <Medal className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-1">{leaderboard[1].username}</h3>
                <div className="text-3xl font-bold text-gray-400 mb-2">#2</div>
                <div className="text-sm text-gray-400">{leaderboard[1].total_score.toLocaleString()} points</div>
              </div>
            </div>

            {/* 1st Place */}
            <div>
              <div className="p-6 rounded-2xl bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 text-center">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center mx-auto mb-4">
                  <Trophy className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-1">{leaderboard[0].username}</h3>
                <div className="text-4xl font-bold text-yellow-400 mb-2">#1</div>
                <div className="text-sm text-gray-400">{leaderboard[0].total_score.toLocaleString()} points</div>
                <div className="mt-4 flex justify-center gap-4 text-xs text-gray-300">
                  <div>
                    <Star className="w-4 h-4 inline mr-1" />
                    {leaderboard[0].perfect_solutions} perfect
                  </div>
                  <div>
                    <TrendingUp className="w-4 h-4 inline mr-1" />
                    {leaderboard[0].success_rate}%
                  </div>
                </div>
              </div>
            </div>

            {/* 3rd Place */}
            <div className="pt-12">
              <div className="p-6 rounded-2xl bg-gradient-to-br from-orange-500/20 to-red-500/20 border border-orange-500/30 text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center mx-auto mb-4">
                  <Medal className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-1">{leaderboard[2].username}</h3>
                <div className="text-3xl font-bold text-orange-400 mb-2">#3</div>
                <div className="text-sm text-gray-400">{leaderboard[2].total_score.toLocaleString()} points</div>
              </div>
            </div>
          </div>
        )}

        {/* Full Leaderboard */}
        <div className="space-y-3">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-forgePurple mx-auto"></div>
              <p className="text-gray-400 mt-4">Loading leaderboard...</p>
            </div>
          ) : (
            leaderboard.map((entry, idx) => (
              <div
                key={entry.user_id}
                className={`p-6 rounded-2xl bg-gradient-to-br border hover:scale-[1.02] transition-all ${getRankBg(entry.rank)}`}
              >
                <div className="flex items-center gap-6">
                  <div className="w-12 h-12 flex items-center justify-center">
                    {getRankIcon(entry.rank)}
                  </div>

                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-white mb-1">{entry.username}</h3>
                    <div className="flex gap-6 text-sm text-gray-400">
                      <div className="flex items-center gap-1">
                        <Trophy className="w-4 h-4 text-yellow-400" />
                        <span>{entry.total_score.toLocaleString()} pts</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Code className="w-4 h-4" />
                        <span>{entry.challenges_completed} solved</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-green-400" />
                        <span>{entry.perfect_solutions} perfect</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <TrendingUp className="w-4 h-4 text-blue-400" />
                        <span>{entry.success_rate}% success</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Zap className="w-4 h-4 text-yellow-400" />
                        <span>{entry.coins_earned} coins</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </PageSection>
    </Layout>
  )
}

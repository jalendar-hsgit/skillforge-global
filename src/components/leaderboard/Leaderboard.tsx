/**
 * Leaderboard Component - Interactive leaderboard with multiple views
 * Shows global, weekly, category-based, and friend rankings
 */
import { useEffect, useState } from 'react'
import { Card } from '@/components/Card'
import { leaderboardAPI } from '@/lib/newFeaturesAPI'

type LeaderboardType = 'global' | 'weekly' | 'coding' | 'quizzes' | 'friends'

interface LeaderboardEntry {
  rank: number
  user_id: number
  user_name: string
  user_email: string
  avatar_url?: string
  coins?: number
  achievements?: number
  coding_solved?: number
  quiz_score?: number
  streak?: number
  badges?: string[]
}

interface MyRankData {
  rank: number
  total_users: number
  coins: number
  achievements: number
  percentile: number
}

const typeLabels: Record<LeaderboardType, string> = {
  global: '🌍 Global Rankings',
  weekly: '📅 This Week',
  coding: '💻 Coding Masters',
  quizzes: '📚 Quiz Champions',
  friends: '👥 Friends',
}

const getBadgeEmoji = (rank: number) => {
  if (rank === 1) return '🥇'
  if (rank === 2) return '🥈'
  if (rank === 3) return '🥉'
  if (rank <= 10) return '⭐'
  if (rank <= 50) return '✨'
  return '•'
}

export default function Leaderboard() {
  const [type, setType] = useState<LeaderboardType>('global')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])
  const [myRank, setMyRank] = useState<MyRankData | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  useEffect(() => {
    let mounted = true

    const fetchLeaderboard = async () => {
      try {
        setLoading(true)
        setError(null)

        let data
        const offset = (currentPage - 1) * itemsPerPage

        switch (type) {
          case 'global':
            data = await leaderboardAPI.getGlobalCoins({ limit: itemsPerPage, offset })
            break
          case 'weekly':
            data = await leaderboardAPI.getWeeklyCoins({ limit: itemsPerPage, offset })
            break
          case 'coding':
            data = await leaderboardAPI.getCodingLeaderboard({ limit: itemsPerPage, offset })
            break
          case 'quizzes':
            data = await leaderboardAPI.getQuizzesLeaderboard({ limit: itemsPerPage, offset })
            break
          case 'friends':
            data = await leaderboardAPI.getFriendLeaderboard({ limit: itemsPerPage, offset })
            break
        }

        if (mounted) {
          setEntries(data.entries || data)
        }
      } catch (err: any) {
        if (mounted) setError(err.message || 'Failed to load leaderboard')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    const fetchMyRank = async () => {
      try {
        const rank = await leaderboardAPI.getMyRank()
        if (mounted) setMyRank(rank)
      } catch (err) {
        // Silently fail for my rank
      }
    }

    fetchLeaderboard()
    fetchMyRank()

    return () => {
      mounted = false
    }
  }, [type, currentPage])

  const getMetricValue = (entry: LeaderboardEntry): number => {
    switch (type) {
      case 'global':
      case 'weekly':
        return entry.coins || 0
      case 'coding':
        return entry.coding_solved || 0
      case 'quizzes':
        return entry.quiz_score || 0
      case 'friends':
        return entry.coins || 0
      default:
        return 0
    }
  }

  const getMetricLabel = (): string => {
    switch (type) {
      case 'global':
      case 'weekly':
        return 'Coins'
      case 'coding':
        return 'Challenges'
      case 'quizzes':
        return 'Score'
      case 'friends':
        return 'Coins'
      default:
        return 'Points'
    }
  }

  return (
    <div className="space-y-4">
      {/* Leaderboard Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {(Object.keys(typeLabels) as LeaderboardType[]).map((t) => (
          <button
            key={t}
            onClick={() => {
              setType(t)
              setCurrentPage(1)
            }}
            className={`whitespace-nowrap px-4 py-2 rounded-lg font-medium transition-all ${
              type === t
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {typeLabels[t]}
          </button>
        ))}
      </div>

      {/* My Rank Card */}
      {myRank && (
        <Card className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-gray-700">Your Rank</p>
              <p className="text-3xl font-bold text-blue-600 mt-1">
                #{myRank.rank}
              </p>
            </div>
            <div className="text-right space-y-2">
              <div>
                <p className="text-xs text-gray-600">Percentile</p>
                <p className="text-lg font-semibold text-purple-600">
                  Top {myRank.percentile}%
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Coins</p>
                <p className="text-lg font-semibold text-green-600">
                  {myRank.coins}
                </p>
              </div>
            </div>
          </div>
          <div className="mt-3 w-full bg-white rounded-lg h-2">
            <div
              className="bg-blue-600 rounded-lg h-2"
              style={{
                width: `${Math.min((myRank.rank / (myRank.total_users / 100)) * 100, 100)}%`,
              }}
            />
          </div>
        </Card>
      )}

      {/* Leaderboard Table */}
      <Card className="overflow-hidden">
        {loading ? (
          <div className="p-6 flex items-center gap-2 text-gray-600">
            <span className="animate-spin">⏳</span>
            <span>Loading leaderboard...</span>
          </div>
        ) : error ? (
          <div className="p-6 bg-red-50 border-t border-red-200">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        ) : entries.length === 0 ? (
          <div className="p-6 text-center text-gray-600">
            <p>No entries found for this leaderboard</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">Rank</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">User</th>
                    <th className="px-4 py-3 text-right font-semibold text-gray-700">
                      {getMetricLabel()}
                    </th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Badge</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.map((entry, idx) => (
                    <tr
                      key={entry.user_id}
                      className={`border-b transition-colors ${
                        idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                      } hover:bg-blue-50`}
                    >
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getBadgeEmoji(entry.rank)}</span>
                          <span className="font-bold text-gray-900">#{entry.rank}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          {entry.avatar_url && (
                            <img
                              src={entry.avatar_url}
                              alt={entry.user_name}
                              className="w-8 h-8 rounded-full"
                            />
                          )}
                          <div>
                            <p className="font-medium text-gray-900">
                              {entry.user_name || 'Anonymous'}
                            </p>
                            <p className="text-xs text-gray-600">
                              {entry.user_email?.split('@')[0]}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="font-bold text-lg text-blue-600">
                          {getMetricValue(entry).toLocaleString()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center gap-1">
                          {(entry.badges || []).slice(0, 3).map((badge) => (
                            <span key={badge} title={badge} className="text-lg">
                              {badge}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-4 border-t bg-gray-50 flex items-center justify-between">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 rounded bg-white border border-gray-300 text-sm font-medium text-gray-700 disabled:opacity-50 hover:bg-gray-100"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {currentPage}
              </span>
              <button
                onClick={() => setCurrentPage((p) => p + 1)}
                disabled={entries.length < itemsPerPage}
                className="px-4 py-2 rounded bg-white border border-gray-300 text-sm font-medium text-gray-700 disabled:opacity-50 hover:bg-gray-100"
              >
                Next
              </button>
            </div>
          </>
        )}
      </Card>
    </div>
  )
}

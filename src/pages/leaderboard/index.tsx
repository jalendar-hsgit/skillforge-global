import { useSession } from 'next-auth/react'
import Head from 'next/head'
import Leaderboard from '@/components/leaderboard/Leaderboard'
import PageLayout from '@/components/PageLayout'
import { useState } from 'react'

export default function LeaderboardPage() {
  const { data: session, status } = useSession()
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [friendsOnly, setFriendsOnly] = useState(false)

  if (status === 'loading') {
    return (
      <PageLayout>
        <div className="flex justify-center items-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading leaderboard...</p>
          </div>
        </div>
      </PageLayout>
    )
  }

  return (
    <>
      <Head>
        <title>Community Leaderboard - SkillForge Global</title>
        <meta name="description" content="View community rankings, achievements, and compete with other learners on SkillForge Global" />
        <meta name="og:title" content="Community Leaderboard" />
        <meta name="og:description" content="Climb the ranks and showcase your skills" />
      </Head>

      <PageLayout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Header Section */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">🏆 Community Leaderboard</h1>
            <p className="text-lg text-gray-600">
              Compete with other learners and climb the ranks. {session?.user?.name && `Welcome, ${session.user.name}!`}
            </p>
          </div>

          {/* Filters Section */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Filter Rankings</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Categories</option>
                  <option value="coding">Coding Challenges</option>
                  <option value="quizzes">Quizzes</option>
                  <option value="resume">Resume Builder</option>
                  <option value="general">General</option>
                </select>
              </div>

              {/* Friends Filter */}
              <div className="flex items-end">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={friendsOnly}
                    onChange={(e) => setFriendsOnly(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">Show Friends Only</span>
                </label>
              </div>
            </div>
          </div>

          {/* Leaderboard Component */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <Leaderboard
              categoryFilter={categoryFilter || undefined}
              friendsOnly={friendsOnly}
            />
          </div>

          {/* Stats Section */}
          {session?.user && (
            <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Stats</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded p-4">
                  <p className="text-sm text-gray-600">Your Rank</p>
                  <p className="text-2xl font-bold text-blue-600">#--</p>
                </div>
                <div className="bg-white rounded p-4">
                  <p className="text-sm text-gray-600">Total Points</p>
                  <p className="text-2xl font-bold text-green-600">--</p>
                </div>
                <div className="bg-white rounded p-4">
                  <p className="text-sm text-gray-600">Achievements</p>
                  <p className="text-2xl font-bold text-purple-600">--</p>
                </div>
              </div>
            </div>
          )}

          {/* Info Section */}
          <div className="mt-8 bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">📊 How Rankings Work</h3>
            <ul className="text-gray-700 space-y-2 text-sm">
              <li>• <strong>Global Coins:</strong> Earn coins by completing challenges and quizzes</li>
              <li>• <strong>Achievements:</strong> Unlock badges by reaching milestones</li>
              <li>• <strong>Weekly:</strong> Fresh rankings based on activity in the last 7 days</li>
              <li>• <strong>Categories:</strong> Compete in specific skill areas</li>
              <li>• <strong>Friends:</strong> Challenge your network and see how you stack up</li>
            </ul>
          </div>
        </div>
      </PageLayout>
    </>
  )
}

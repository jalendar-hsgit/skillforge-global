import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'

type Achievement = {
  id: string
  title: string
  description: string
  icon: string
  earned: boolean
  earnedDate?: string
}

export default function AchievementsPage() {
  const router = useRouter()
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAchievements()
  }, [])

  async function loadAchievements() {
    try {
      // Use Next.js proxy to properly handle authentication
      const res = await fetch(`/api/session/v1x/student/dashboard/achievements`, {
        credentials: 'include'
      })

      if (res.status === 401) {
        router.push('/login?redirect=/dashboard/achievements')
        return
      }

      if (res.ok) {
        const data = await res.json()
        setAchievements(data.achievements || [])
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
          <div className="text-techGray">Loading achievements...</div>
        </div>
      </Layout>
    )
  }

  const earned = achievements.filter(a => a.earned)
  const locked = achievements.filter(a => !a.earned)

  return (
    <Layout>
      <Head>
        <title>My Achievements – SkillForge Global</title>
      </Head>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <Link href="/dashboard" className="text-techBlue hover:underline mb-4 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-white mb-2">Your Achievements</h1>
          <p className="text-techGray">
            {earned.length} of {achievements.length} earned
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="bg-gray-700 rounded-full h-4 overflow-hidden">
            <div
              className="bg-gradient-to-r from-yellow-500 to-orange-500 h-4 transition-all"
              style={{ width: `${(earned.length / achievements.length) * 100}%` }}
            />
          </div>
          <div className="text-center mt-2 text-sm text-techGray">
            {Math.round((earned.length / achievements.length) * 100)}% Complete
          </div>
        </div>

        {/* Earned Achievements */}
        {earned.length > 0 && (
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-white mb-4">🏆 Earned ({earned.length})</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {earned.map((achievement) => (
                <div
                  key={achievement.id}
                  className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border-2 border-yellow-500/50 rounded-xl p-6 transform hover:scale-105 transition-transform"
                >
                  <div className="text-center mb-4">
                    <div className="text-6xl mb-3">{achievement.icon}</div>
                    <h3 className="text-xl font-bold text-white mb-2">{achievement.title}</h3>
                    <p className="text-sm text-techGray">{achievement.description}</p>
                  </div>
                  <div className="text-center">
                    <span className="inline-block px-3 py-1 bg-yellow-500/20 rounded-full text-xs text-yellow-400">
                      ✓ Unlocked
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Locked Achievements */}
        {locked.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-4">🔒 Locked ({locked.length})</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {locked.map((achievement) => (
                <div
                  key={achievement.id}
                  className="bg-white/5 border border-white/10 rounded-xl p-6 opacity-60"
                >
                  <div className="text-center mb-4">
                    <div className="text-6xl mb-3 grayscale">{achievement.icon}</div>
                    <h3 className="text-xl font-bold text-white mb-2">{achievement.title}</h3>
                    <p className="text-sm text-techGray">{achievement.description}</p>
                  </div>
                  <div className="text-center">
                    <span className="inline-block px-3 py-1 bg-gray-700 rounded-full text-xs text-gray-400">
                      🔒 Locked
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {achievements.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🏆</div>
            <h3 className="text-xl font-semibold text-white mb-2">No achievements yet</h3>
            <p className="text-techGray mb-6">Start learning to earn your first achievement!</p>
            <Link
              href="/paths"
              className="inline-block px-6 py-3 bg-forgePurple hover:bg-forgePurple/80 text-white font-medium rounded-lg transition-colors"
            >
              Start Learning
            </Link>
          </div>
        )}
      </div>
    </Layout>
  )
}

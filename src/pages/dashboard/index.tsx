import Head from 'next/head'
import Layout from '@/components/Layout'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { BookOpen, Award, TrendingUp, Target, Clock } from 'lucide-react'
import type { GetServerSideProps } from 'next'

type Me = { id:number; email:string; created_at:string } | null

type PathProgress = {
  path: string
  title: string
  totalVideos: number
  completedVideos: number
  percentage: number
  lastWatched?: string
}

type DashboardStats = {
  totalVideosCompleted: number
  totalQuizzesTaken: number
  forgeCredits: number
  streakDays: number
  pathsInProgress: PathProgress[]
}

export const getServerSideProps: GetServerSideProps = async (ctx) => {
  const base = `http://${ctx.req.headers.host}`
  const r = await fetch(`${base}/api/session/me`, {
    headers: { cookie: ctx.req.headers.cookie || '' }
  })
  if (!r.ok) {
    return { redirect: { destination: '/login', permanent: false } }
  }
  const me = await r.json()
  return { props: { me } }
}

export default function Dashboard({ me }: { me: Me }) {
  const [stats, setStats] = useState<DashboardStats>({
    totalVideosCompleted: 0,
    totalQuizzesTaken: 0,
    forgeCredits: 10, // Default starting credits
    streakDays: 1,
    pathsInProgress: []
  })
  const [loading, setLoading] = useState(true)

  const pathTitles: Record<string, string> = {
    'python-ai': 'Python AI Mastery',
    'fullstack': 'Full Stack Development',
    'aws-devops': 'AWS DevOps Professional',
    'cybersec': 'Cybersecurity Expert',
    'flutter': 'Flutter Mobile Dev'
  }

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const paths = ['python-ai', 'fullstack', 'aws-devops', 'cybersec', 'flutter']
        const pathProgress: PathProgress[] = []
        let totalCompleted = 0

        for (const path of paths) {
          try {
            // Fetch all videos for path
            const videosRes = await fetch(`/api/v1x/courses-db/${path}/videos`)
            if (!videosRes.ok) continue
            const videos = await videosRes.json()
            
            // Fetch user progress for path
            const progressRes = await fetch(`/api/progress/get?path=${path}`)
            const progressData = progressRes.ok ? await progressRes.json() : { completed: [] }
            
            const completed = progressData.completed?.length || 0
            const total = videos.length || 0
            
            if (completed > 0 || total > 0) {
              pathProgress.push({
                path,
                title: pathTitles[path] || path,
                totalVideos: total,
                completedVideos: completed,
                percentage: total > 0 ? Math.round((completed / total) * 100) : 0
              })
              totalCompleted += completed
            }
          } catch (err) {
            console.error(`Failed to fetch progress for ${path}`, err)
          }
        }

        // Sort by progress percentage (most progress first)
        pathProgress.sort((a, b) => b.percentage - a.percentage)

        setStats({
          totalVideosCompleted: totalCompleted,
          totalQuizzesTaken: 0, // TODO: Fetch from quiz attempts
          forgeCredits: 10, // TODO: Fetch from coins API
          streakDays: 1,
          pathsInProgress: pathProgress
        })
      } catch (error) {
        console.error('Failed to fetch dashboard data', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])
  if (loading) {
    return (
      <Layout>
        <Head><title>Dashboard – SkillForge Global</title></Head>
        <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
          <div className="text-center py-20">
            <p className="text-techGray">Loading your dashboard...</p>
          </div>
        </section>
      </Layout>
    )
  }

  const nextPath = stats.pathsInProgress.find(p => p.percentage > 0 && p.percentage < 100) || stats.pathsInProgress[0]

  return (
    <Layout>
      <Head><title>Dashboard – SkillForge Global</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-semibold">
              Welcome back{me ? `, ${me.email.split('@')[0]}` : ''}! 👋
            </h1>
            <p className="text-techGray mt-2">Track your learning journey and career growth</p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-forgePurple/20 to-neuralBlue/20 border border-forgePurple/30">
            <Award className="w-5 h-5 text-yellow-400" />
            <span className="font-semibold">{stats.forgeCredits} Forge Credits</span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
          <div className="rounded-xl border border-white/10 bg-white/[0.06] p-4">
            <div className="flex items-center gap-2 text-techGray text-sm mb-1">
              <BookOpen className="w-4 h-4" />
              Videos Completed
            </div>
            <div className="text-2xl font-bold">{stats.totalVideosCompleted}</div>
          </div>
          
          <div className="rounded-xl border border-white/10 bg-white/[0.06] p-4">
            <div className="flex items-center gap-2 text-techGray text-sm mb-1">
              <Target className="w-4 h-4" />
              Quizzes Taken
            </div>
            <div className="text-2xl font-bold">{stats.totalQuizzesTaken}</div>
          </div>
          
          <div className="rounded-xl border border-white/10 bg-white/[0.06] p-4">
            <div className="flex items-center gap-2 text-techGray text-sm mb-1">
              <TrendingUp className="w-4 h-4" />
              Paths Started
            </div>
            <div className="text-2xl font-bold">{stats.pathsInProgress.length}</div>
          </div>
          
          <div className="rounded-xl border border-white/10 bg-white/[0.06] p-4">
            <div className="flex items-center gap-2 text-techGray text-sm mb-1">
              <Clock className="w-4 h-4" />
              Day Streak
            </div>
            <div className="text-2xl font-bold">{stats.streakDays}</div>
          </div>
        </div>

        {/* Continue Learning */}
        {nextPath && (
          <div className="mt-8 rounded-2xl border border-white/10 bg-gradient-to-br from-forgePurple/10 to-neuralBlue/10 p-6">
            <h2 className="text-xl font-semibold mb-2">Continue Learning</h2>
            <p className="text-sm text-techGray mb-4">Pick up where you left off</p>
            
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div className="flex-1 min-w-[200px]">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{nextPath.title}</span>
                  <span className="text-sm text-techGray">{nextPath.percentage}%</span>
                </div>
                <div className="h-3 rounded-full bg-white/10 overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue"
                    style={{ width: `${nextPath.percentage}%` }}
                  />
                </div>
                <p className="text-xs text-techGray mt-2">
                  {nextPath.completedVideos} of {nextPath.totalVideos} videos completed
                </p>
              </div>
              
              <Link 
                href={`/paths/${nextPath.path}`}
                className="px-6 py-3 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue font-semibold hover:opacity-90 transition whitespace-nowrap"
              >
                Continue →
              </Link>
            </div>
          </div>
        )}

        {/* All Paths Progress */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Your Learning Paths</h2>
          
          {stats.pathsInProgress.length === 0 ? (
            <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-8 text-center">
              <p className="text-techGray mb-4">You haven't started any paths yet</p>
              <Link 
                href="/paths"
                className="inline-block px-6 py-3 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue font-semibold"
              >
                Browse Paths
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {stats.pathsInProgress.map(path => (
                <Link 
                  key={path.path}
                  href={`/paths/${path.path}`}
                  className="rounded-xl border border-white/10 bg-white/[0.06] hover:bg-white/[0.08] p-5 transition"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold">{path.title}</h3>
                    <span className={`text-sm px-2 py-1 rounded ${
                      path.percentage === 100 ? 'bg-green-500/20 text-green-400' :
                      path.percentage > 50 ? 'bg-blue-500/20 text-blue-400' :
                      path.percentage > 0 ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {path.percentage === 100 ? 'Completed' : 
                       path.percentage > 0 ? 'In Progress' : 'Not Started'}
                    </span>
                  </div>
                  
                  <div className="mb-2">
                    <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue"
                        style={{ width: `${path.percentage}%` }}
                      />
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-techGray">
                    <span>{path.completedVideos}/{path.totalVideos} videos</span>
                    <span>{path.percentage}% complete</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-6">
            <h3 className="font-semibold mb-2">Take a Quiz</h3>
            <p className="text-sm text-techGray mb-4">Test your knowledge and earn credits</p>
            <Link 
              href="/paths"
              className="inline-block px-4 py-2 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue font-semibold text-sm"
            >
              Browse Quizzes
            </Link>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-6">
            <h3 className="font-semibold mb-2">Explore All Paths</h3>
            <p className="text-sm text-techGray mb-4">Discover new learning opportunities</p>
            <Link 
              href="/paths"
              className="inline-block px-4 py-2 rounded-lg bg-white/10 border border-white/10 font-semibold text-sm"
            >
              View All Paths
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  )
}

import Head from 'next/head'
import Layout from '@/components/Layout'
import { PageHeader, PageContainer, PageSection, PageGrid, LoadingState, EmptyState } from '@/components/PageLayout'
import { StatCard, ProgressCard, AlertCard, ActionCard } from '@/components/Cards'
import { useEffect, useState } from 'react'
import { BookOpen, Award, TrendingUp, Target, Clock } from 'lucide-react'
import type { GetServerSideProps } from 'next'
import { usePlanFeatures } from '@/hooks/usePlanFeatures'
import { Button } from '@/components/Button'

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
  const { plan, loading: planLoading } = usePlanFeatures()
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

        // Fetch coin balance
        let coinBalance = 0
        try {
          const coinRes = await fetch('/api/coins/balance', {
            credentials: 'include'
          })
          if (coinRes.ok) {
            const coinData = await coinRes.json()
            coinBalance = coinData.balance || coinData.coins || 0
          }
        } catch (err) {
          console.error('Failed to fetch coin balance', err)
        }

        setStats({
          totalVideosCompleted: totalCompleted,
          totalQuizzesTaken: 0, // TODO: Fetch from quiz attempts
          forgeCredits: coinBalance,
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
      <Layout maxWidth="7xl">
        <Head><title>Dashboard – SkillForge Global</title></Head>
        <LoadingState message="Loading your dashboard..." />
      </Layout>
    )
  }

  const nextPath = stats.pathsInProgress.find(p => p.percentage > 0 && p.percentage < 100) || stats.pathsInProgress[0]

  return (
    <Layout maxWidth="7xl">
      <Head><title>Dashboard – SkillForge Global</title></Head>

      {/* Page Header */}
      <PageHeader
        icon="📊"
        title={`Welcome back${me ? `, ${me.email.split('@')[0]}` : ''}! 👋`}
        subtitle="Track your learning journey and career growth"
        breadcrumbs={[
          { label: 'Home', href: '/' },
          { label: 'Dashboard' }
        ]}
        actions={
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-forgePurple/20 to-neuralBlue/20 border border-forgePurple/30">
            <Award className="w-5 h-5 text-yellow-400" />
            <span className="font-semibold">{stats.forgeCredits} Forge Credits</span>
          </div>
        }
      />

      {/* Subscription banner */}
      {!planLoading && plan && (
        <div className="mb-6">
          <AlertCard
            variant={plan === 'PRO' ? 'success' : 'info'}
            title={`Current Plan: ${plan}`}
            message={plan === 'PRO' ? 
              'You have unlimited access to all features.' : 
              'Upgrade to Pro for unlimited access and longer sessions.'
            }
            action={
              <a href="/pricing">
                <Button variant={plan === 'PRO' ? 'secondary' : 'primary'} size="sm">
                  {plan === 'PRO' ? 'Manage Plan' : 'Upgrade to Pro'}
                </Button>
              </a>
            }
          />
        </div>
      )}

      {/* Stats Grid */}
      <PageSection icon="📈" title="Your Progress">
        <PageGrid cols={4} gap="md">
          <StatCard
            icon="📚"
            label="Videos Completed"
            value={stats.totalVideosCompleted.toString()}
            color="purple"
          />
          <StatCard
            icon="🎯"
            label="Quizzes Taken"
            value={stats.totalQuizzesTaken.toString()}
            color="blue"
          />
          <StatCard
            icon="📖"
            label="Paths Started"
            value={stats.pathsInProgress.length.toString()}
            color="green"
            href="/paths"
          />
          <StatCard
            icon="🔥"
            label="Day Streak"
            value={stats.streakDays.toString()}
            color="orange"
          />
        </PageGrid>
      </PageSection>

      {/* Continue Learning */}
      {nextPath && (
        <PageSection 
          icon="▶️" 
          title="Continue Learning" 
          subtitle="Pick up where you left off"
        >
          <ProgressCard
            icon="🎓"
            title={nextPath.title}
            subtitle={`${nextPath.completedVideos} of ${nextPath.totalVideos} videos completed`}
            progress={nextPath.percentage}
            href={`/paths/${nextPath.path}`}
            stats={[
              { label: 'Progress', value: `${nextPath.percentage}%` },
              { label: 'Videos', value: `${nextPath.completedVideos}/${nextPath.totalVideos}` }
            ]}
          />
        </PageSection>
      )}

      {/* All Paths Progress */}
      <PageSection 
        icon="📚" 
        title="Your Learning Paths"
        subtitle={stats.pathsInProgress.length > 0 ? 
          `${stats.pathsInProgress.length} path${stats.pathsInProgress.length > 1 ? 's' : ''} in progress` : 
          undefined
        }
      >
        {stats.pathsInProgress.length === 0 ? (
          <EmptyState
            icon="📚"
            title="No paths started yet"
            description="Start your learning journey by choosing a career path that matches your goals."
            action={
              <a href="/paths">
                <Button variant="primary" size="lg">Browse Paths</Button>
              </a>
            }
          />
        ) : (
          <PageGrid cols={2} gap="md">
            {stats.pathsInProgress.map(path => (
              <ProgressCard
                key={path.path}
                icon="🎓"
                title={path.title}
                subtitle={`${path.completedVideos} of ${path.totalVideos} videos`}
                progress={path.percentage}
                href={`/paths/${path.path}`}
                stats={[
                  { label: 'Complete', value: `${path.percentage}%` },
                  { label: 'Status', value: path.percentage === 100 ? '✅ Done' : '🔄 Active' }
                ]}
              />
            ))}
          </PageGrid>
        )}
      </PageSection>

      {/* Quick Actions */}
      <PageSection icon="⚡" title="Quick Actions">
        <PageGrid cols={2} gap="md">
          <ActionCard
            icon="🎯"
            title="Take a Quiz"
            description="Test your knowledge and earn Forge Credits."
            buttonText="Browse Quizzes"
            buttonHref="/paths"
            variant="gradient"
          />
          <ActionCard
            icon="🗺️"
            title="Explore All Paths"
            description="Discover new learning opportunities and expand your skills."
            buttonText="View All Paths"
            buttonHref="/paths"
            variant="default"
          />
        </PageGrid>
      </PageSection>
    </Layout>
  )
}

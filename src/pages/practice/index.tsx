import Head from 'next/head'
import Layout from '@/components/Layout'
import { PageHeader, PageContainer, PageSection, PageGrid } from '@/components/PageLayout'
import { useState, useEffect } from 'react'
import { Code, Zap, Trophy, Target, Clock, TrendingUp, Award, Play, CheckCircle, XCircle, Brain, Cloud, Database, Shield, Layers, Terminal } from 'lucide-react'
import Link from 'next/link'
import type { GetServerSideProps } from 'next'

type CodingStats = {
  total_submissions: number
  perfect_solutions: number
  challenges_attempted: number
  coins_earned: number
  avg_score: number
  active_sessions: number
  success_rate: number
}

type Challenge = {
  id: number
  title: string
  slug: string
  category: string
  difficulty: string
  points: number
  is_premium: boolean
  success_rate: number
}

type Submission = {
  id: number
  challenge_id: number
  status: string
  score: number
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

const difficultyColors = {
  beginner: 'bg-green-500/20 text-green-400 border-green-500/30',
  easy: 'bg-green-500/20 text-green-400 border-green-500/30',
  medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  hard: 'bg-red-500/20 text-red-400 border-red-500/30',
  expert: 'bg-purple-500/20 text-purple-400 border-purple-500/30'
}

const categoryIcons = {
  algorithms: Brain,
  data_structures: Layers,
  cloud_aws: Cloud,
  cloud_azure: Cloud,
  cloud_gcp: Cloud,
  devops: Shield,
  database: Database,
  web_development: Code,
  security: Shield
}

export default function CodingPractice() {
  const [stats, setStats] = useState<CodingStats | null>(null)
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [recentSubmissions, setRecentSubmissions] = useState<Submission[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all')

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch stats
        const statsRes = await fetch(`${API_BASE}/api/v1x/coding-practice/my-stats`, {
          credentials: 'include'
        })
        if (statsRes.ok) {
          setStats(await statsRes.json())
        } else {
          console.warn('Stats response not ok:', statsRes.status, statsRes.statusText)
        }

        // Fetch challenges
        const challengesRes = await fetch(`${API_BASE}/api/v1x/coding-practice/challenges?limit=100`, {
          credentials: 'include'
        })
        if (challengesRes.ok) {
          const data = await challengesRes.json()
          console.log('Challenges fetched:', data.length, 'challenges')
          setChallenges(data)
        } else {
          console.warn('Challenges response not ok:', challengesRes.status, challengesRes.statusText)
        }

        // Fetch recent submissions
        const submissionsRes = await fetch(`${API_BASE}/api/v1x/coding-practice/my-submissions?limit=10`, {
          credentials: 'include'
        })
        if (submissionsRes.ok) {
          setRecentSubmissions(await submissionsRes.json())
        } else {
          console.warn('Submissions response not ok:', submissionsRes.status, submissionsRes.statusText)
        }
      } catch (error) {
        console.error('Failed to fetch coding practice data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [API_BASE])

  const filteredChallenges = challenges.filter(c => {
    if (selectedCategory !== 'all' && c.category !== selectedCategory) return false
    if (selectedDifficulty !== 'all' && c.difficulty !== selectedDifficulty) return false
    return true
  })

  return (
    <Layout maxWidth="7xl">
      <Head>
        <title>Coding Practice – SkillForge Global</title>
      </Head>

      {/* Header */}
      <PageHeader
        icon="💻"
        title="Coding Practice Arena"
        subtitle="Master your programming skills with hands-on challenges"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Coding Practice' }
        ]}
      />

      {/* Stats Overview */}
      {stats && (
        <PageSection>
          <PageGrid cols={4}>
            <div className="p-6 rounded-2xl bg-gradient-to-br from-forgePurple/20 to-neuralBlue/20 border border-forgePurple/30">
              <div className="flex items-center justify-between mb-4">
                <Code className="w-8 h-8 text-forgePurple" />
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-forgePurple/20 text-forgePurple">
                  Total
                </span>
              </div>
              <div className="text-3xl font-bold text-white mb-1">{stats.total_submissions}</div>
              <div className="text-sm text-gray-400">Submissions</div>
            </div>

            <div className="p-6 rounded-2xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30">
              <div className="flex items-center justify-between mb-4">
                <CheckCircle className="w-8 h-8 text-green-400" />
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-500/20 text-green-400">
                  Perfect
                </span>
              </div>
              <div className="text-3xl font-bold text-white mb-1">{stats.perfect_solutions}</div>
              <div className="text-sm text-gray-400">Perfect Solutions</div>
            </div>

            <div className="p-6 rounded-2xl bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/30">
              <div className="flex items-center justify-between mb-4">
                <Trophy className="w-8 h-8 text-yellow-400" />
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-yellow-500/20 text-yellow-400">
                  {stats.success_rate}%
                </span>
              </div>
              <div className="text-3xl font-bold text-white mb-1">{stats.challenges_attempted}</div>
              <div className="text-sm text-gray-400">Challenges Attempted</div>
            </div>

            <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/30">
              <div className="flex items-center justify-between mb-4">
                <Award className="w-8 h-8 text-blue-400" />
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-500/20 text-blue-400">
                  Avg {stats.avg_score}%
                </span>
              </div>
              <div className="text-3xl font-bold text-white mb-1">{stats.coins_earned}</div>
              <div className="text-sm text-gray-400">Coins Earned</div>
            </div>
          </PageGrid>
        </PageSection>
      )}

      {/* Quick Actions */}
      <PageSection>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Link href="#challenges" className="p-6 rounded-2xl bg-gradient-to-br from-forgePurple/10 to-neuralBlue/10 border border-forgePurple/20 hover:border-forgePurple/40 transition-all group">
            <Play className="w-10 h-10 text-forgePurple mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-semibold text-white mb-2">Start Challenge</h3>
            <p className="text-sm text-gray-400">Choose from 100+ coding challenges</p>
          </Link>

          <Link href="/practice/submissions" className="p-6 rounded-2xl bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20 hover:border-blue-500/40 transition-all group">
            <CheckCircle className="w-10 h-10 text-blue-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-semibold text-white mb-2">My Submissions</h3>
            <p className="text-sm text-gray-400">View your solution history</p>
          </Link>

          <Link href="/practice/leaderboard" className="p-6 rounded-2xl bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border border-yellow-500/20 hover:border-yellow-500/40 transition-all group">
            <Trophy className="w-10 h-10 text-yellow-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-semibold text-white mb-2">Leaderboard</h3>
            <p className="text-sm text-gray-400">Compete with top coders</p>
          </Link>

          <Link href="#simulators" className="p-6 rounded-2xl bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20 hover:border-green-500/40 transition-all group">
            <Code className="w-10 h-10 text-green-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-semibold text-white mb-2">Code Simulators</h3>
            <p className="text-sm text-gray-400">Real-time IDE & terminal practice</p>
          </Link>
        </div>
      </PageSection>

      {/* Filters */}
      <PageSection id="challenges">
        <div className="flex flex-wrap items-center gap-4 mb-6">
          <div>
            <label className="text-sm text-gray-400 mb-2 block">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 rounded-lg bg-darkNavy border border-techBlue/30 text-white focus:outline-none focus:border-techBlue"
            >
              <option value="all">All Categories</option>
              <option value="algorithms">Algorithms</option>
              <option value="data_structures">Data Structures</option>
              <option value="cloud_aws">Cloud - AWS</option>
              <option value="cloud_azure">Cloud - Azure</option>
              <option value="devops">DevOps</option>
              <option value="database">Database</option>
              <option value="web_development">Web Development</option>
              <option value="security">Security</option>
            </select>
          </div>

          <div>
            <label className="text-sm text-gray-400 mb-2 block">Difficulty</label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="px-4 py-2 rounded-lg bg-darkNavy border border-techBlue/30 text-white focus:outline-none focus:border-techBlue"
            >
              <option value="all">All Levels</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
              <option value="expert">Expert</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-forgePurple"></div>
            </div>
            <p className="text-gray-400 mt-4">Loading challenges...</p>
          </div>
        ) : (
          <>
            {/* Challenges Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredChallenges.map((challenge) => {
                const Icon = categoryIcons[challenge.category as keyof typeof categoryIcons] || Code
                return (
                  <div
                    key={challenge.id}
                    className="p-6 rounded-2xl bg-darkNavy border border-techBlue/20 hover:border-techBlue/40 transition-all group cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <Icon className="w-8 h-8 text-techBlue group-hover:text-forgePurple transition-colors" />
                      {challenge.is_premium && (
                        <span className="px-2 py-1 rounded-md text-xs font-medium bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
                          Premium
                        </span>
                      )}
                    </div>

                    <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-forgePurple transition-colors">
                      {challenge.title}
                    </h3>

                    <div className="flex items-center gap-2 mb-4">
                      <span className={`px-2 py-1 rounded-md text-xs font-medium border ${difficultyColors[challenge.difficulty as keyof typeof difficultyColors]}`}>
                        {challenge.difficulty}
                      </span>
                      <span className="px-2 py-1 rounded-md text-xs font-medium bg-forgePurple/20 text-forgePurple border border-forgePurple/30">
                        {challenge.category.replace('_', ' ')}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-sm text-gray-400">
                      <span className="flex items-center gap-1">
                        <Trophy className="w-4 h-4" />
                        {challenge.points} points
                      </span>
                      <span className="flex items-center gap-1">
                        <Target className="w-4 h-4" />
                        {(challenge.success_rate || 0).toFixed(0)}% success
                      </span>
                    </div>

                    <Link
                      href={`/practice/${challenge.slug}`}
                      className="mt-4 block w-full py-2 px-4 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue text-white text-center font-medium hover:shadow-lg hover:shadow-forgePurple/50 transition-all"
                    >
                      Start Challenge
                    </Link>
                  </div>
                )
              })}
            </div>

            {filteredChallenges.length === 0 && (
              <div className="text-center py-12">
                <Code className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No challenges found. Try different filters.</p>
              </div>
            )}
          </>
        )}
      </PageSection>

      {/* Code Simulators Section */}
      <PageSection id="simulators">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white mb-2">Code Simulators</h2>
          <p className="text-gray-400">Practice coding in real-time environments similar to KodeKloud and W3Schools</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link href="/practice/simulator/code-editor" className="p-6 rounded-2xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 hover:border-purple-500/40 transition-all group">
            <Code className="w-10 h-10 text-purple-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-semibold text-white mb-2">Code Editor</h3>
            <p className="text-sm text-gray-400 mb-3">Multi-language IDE with syntax highlighting</p>
            <div className="flex flex-wrap gap-1">
              <span className="px-2 py-0.5 rounded text-xs bg-purple-500/20 text-purple-300">Python</span>
              <span className="px-2 py-0.5 rounded text-xs bg-purple-500/20 text-purple-300">JS</span>
              <span className="px-2 py-0.5 rounded text-xs bg-purple-500/20 text-purple-300">Java</span>
            </div>
          </Link>

          <Link href="/practice/simulator/terminal" className="p-6 rounded-2xl bg-gradient-to-br from-green-500/10 to-teal-500/10 border border-green-500/20 hover:border-green-500/40 transition-all group">
            <Terminal className="w-10 h-10 text-green-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-semibold text-white mb-2">Terminal</h3>
            <p className="text-sm text-gray-400 mb-3">Linux/Bash command line practice</p>
            <div className="flex flex-wrap gap-1">
              <span className="px-2 py-0.5 rounded text-xs bg-green-500/20 text-green-300">Bash</span>
              <span className="px-2 py-0.5 rounded text-xs bg-green-500/20 text-green-300">Shell</span>
            </div>
          </Link>

          <Link href="/practice/simulator/database" className="p-6 rounded-2xl bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border border-blue-500/20 hover:border-blue-500/40 transition-all group">
            <Database className="w-10 h-10 text-blue-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-semibold text-white mb-2">SQL Playground</h3>
            <p className="text-sm text-gray-400 mb-3">Practice SQL queries live</p>
            <div className="flex flex-wrap gap-1">
              <span className="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-300">MySQL</span>
              <span className="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-300">PostgreSQL</span>
            </div>
          </Link>

          <Link href="/practice/simulator/cloud-console" className="p-6 rounded-2xl bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/20 hover:border-orange-500/40 transition-all group">
            <Cloud className="w-10 h-10 text-orange-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-semibold text-white mb-2">Cloud Console</h3>
            <p className="text-sm text-gray-400 mb-3">AWS/Azure CLI practice</p>
            <div className="flex flex-wrap gap-1">
              <span className="px-2 py-0.5 rounded text-xs bg-orange-500/20 text-orange-300">AWS</span>
              <span className="px-2 py-0.5 rounded text-xs bg-orange-500/20 text-orange-300">Azure</span>
            </div>
          </Link>

          <Link href="/practice/simulator/kubernetes" className="p-6 rounded-2xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 hover:border-cyan-500/40 transition-all group">
            <Layers className="w-10 h-10 text-cyan-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-semibold text-white mb-2">Kubernetes Cluster</h3>
            <p className="text-sm text-gray-400 mb-3">Deploy and manage K8s resources</p>
            <div className="flex flex-wrap gap-1">
              <span className="px-2 py-0.5 rounded text-xs bg-cyan-500/20 text-cyan-300">kubectl</span>
              <span className="px-2 py-0.5 rounded text-xs bg-cyan-500/20 text-cyan-300">helm</span>
            </div>
          </Link>

          <Link href="/practice/simulator/docker" className="p-6 rounded-2xl bg-gradient-to-br from-blue-600/10 to-sky-500/10 border border-blue-600/20 hover:border-blue-600/40 transition-all group">
            <Layers className="w-10 h-10 text-blue-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-semibold text-white mb-2">Docker Lab</h3>
            <p className="text-sm text-gray-400 mb-3">Container management practice</p>
            <div className="flex flex-wrap gap-1">
              <span className="px-2 py-0.5 rounded text-xs bg-blue-600/20 text-blue-300">Docker</span>
              <span className="px-2 py-0.5 rounded text-xs bg-blue-600/20 text-blue-300">Compose</span>
            </div>
          </Link>

          <Link href="/practice/simulator/api-playground" className="p-6 rounded-2xl bg-gradient-to-br from-pink-500/10 to-rose-500/10 border border-pink-500/20 hover:border-pink-500/40 transition-all group">
            <Zap className="w-10 h-10 text-pink-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-semibold text-white mb-2">API Playground</h3>
            <p className="text-sm text-gray-400 mb-3">Test REST APIs interactively</p>
            <div className="flex flex-wrap gap-1">
              <span className="px-2 py-0.5 rounded text-xs bg-pink-500/20 text-pink-300">REST</span>
              <span className="px-2 py-0.5 rounded text-xs bg-pink-500/20 text-pink-300">GraphQL</span>
            </div>
          </Link>

          <Link href="/practice/simulator/web-editor" className="p-6 rounded-2xl bg-gradient-to-br from-yellow-500/10 to-amber-500/10 border border-yellow-500/20 hover:border-yellow-500/40 transition-all group">
            <Code className="w-10 h-10 text-yellow-400 mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-semibold text-white mb-2">Web Editor</h3>
            <p className="text-sm text-gray-400 mb-3">HTML/CSS/JS live preview</p>
            <div className="flex flex-wrap gap-1">
              <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-300">HTML</span>
              <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-300">CSS</span>
              <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-300">JS</span>
            </div>
          </Link>
        </div>
      </PageSection>

      {/* Cloud Labs Section */}
      <PageSection id="cloud-labs">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white mb-2">Cloud Labs</h2>
          <p className="text-gray-400">Hands-on practice with real cloud environments</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-6 rounded-2xl bg-gradient-to-br from-orange-500/10 to-yellow-500/10 border border-orange-500/20 hover:border-orange-500/40 transition-all group cursor-pointer">
            <div className="flex items-center justify-between mb-4">
              <Cloud className="w-10 h-10 text-orange-400 group-hover:scale-110 transition-transform" />
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-orange-500/20 text-orange-400">AWS</span>
            </div>
            <h3 className="font-semibold text-white mb-2">AWS Solutions Architect</h3>
            <p className="text-sm text-gray-400 mb-4">Practice EC2, S3, Lambda, and more in live AWS environment</p>
            <div className="flex items-center justify-between text-sm text-gray-400">
              <span>12 scenarios</span>
              <span className="text-yellow-400">★ Premium</span>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20 hover:border-blue-500/40 transition-all group cursor-pointer">
            <div className="flex items-center justify-between mb-4">
              <Cloud className="w-10 h-10 text-blue-400 group-hover:scale-110 transition-transform" />
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400">Azure</span>
            </div>
            <h3 className="font-semibold text-white mb-2">Azure Administrator</h3>
            <p className="text-sm text-gray-400 mb-4">Master Azure VMs, Storage, and Networking</p>
            <div className="flex items-center justify-between text-sm text-gray-400">
              <span>8 scenarios</span>
              <span className="text-yellow-400">★ Premium</span>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-br from-red-500/10 to-pink-500/10 border border-red-500/20 hover:border-red-500/40 transition-all group cursor-pointer">
            <div className="flex items-center justify-between mb-4">
              <Cloud className="w-10 h-10 text-red-400 group-hover:scale-110 transition-transform" />
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-400">GCP</span>
            </div>
            <h3 className="font-semibold text-white mb-2">Google Cloud Engineer</h3>
            <p className="text-sm text-gray-400 mb-4">Practice Compute Engine, Cloud Storage, and GKE</p>
            <div className="flex items-center justify-between text-sm text-gray-400">
              <span>6 scenarios</span>
              <span className="text-yellow-400">★ Premium</span>
            </div>
          </div>
        </div>
      </PageSection>

      {/* Recent Submissions */}
      {recentSubmissions.length > 0 && (
        <PageSection>
          <h2 className="text-2xl font-bold text-white mb-6">Recent Submissions</h2>
          <div className="space-y-3">
            {recentSubmissions.map((submission) => (
              <div
                key={submission.id}
                className="p-4 rounded-xl bg-darkNavy border border-techBlue/20 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  {submission.status === 'success' ? (
                    <CheckCircle className="w-6 h-6 text-green-400" />
                  ) : (
                    <XCircle className="w-6 h-6 text-red-400" />
                  )}
                  <div>
                    <div className="font-medium text-white">Challenge #{submission.challenge_id}</div>
                    <div className="text-sm text-gray-400">
                      {new Date(submission.submitted_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-white">{submission.score}%</div>
                  <div className="text-xs text-gray-400">{submission.status}</div>
                </div>
              </div>
            ))}
          </div>
        </PageSection>
      )}
    </Layout>
  )
}

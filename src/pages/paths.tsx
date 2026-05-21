import Head from 'next/head'
import Layout from '@/components/Layout'
import { SectionHeading } from '@/components/SectionHeading'
import { InfoCard } from '@/components/InfoCard'
import { Brain, Code2, CloudCog, ShieldCheck, Smartphone } from "lucide-react"
import Link from 'next/link'
import { useMe } from '@/hooks/useMe'
import { useEffect, useState } from 'react'
import { apiGet } from '@/lib/api'

const pathIcons = {
  'python-ai': <Brain />,
  'fullstack': <Code2 />,
  'aws-devops': <CloudCog />,
  'cybersec': <ShieldCheck />,
  'flutter': <Smartphone />
}

interface Path {
  slug: string;
  title: string;
  subtitle: string;
}

interface PathStats {
  slug: string;
  totalVideos: number;
  completedVideos: number;
  percentage: number;
}

export default function PathsPage() {
  const { me, loading: userLoading } = useMe()
  const [paths, setPaths] = useState<Path[]>([])
  const [pathStats, setPathStats] = useState<Record<string, PathStats>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    if (userLoading) return

    const fetchPaths = async () => {
      try {
        const data = await apiGet('/api/v1/paths/list')
        setPaths(data)
        
        // Fetch stats for each path if user is logged in
        if (me) {
          const stats: Record<string, PathStats> = {}
          
          for (const path of data) {
            try {
              // Fetch total videos (DB-backed first, fallback to file-backed)
              let videos: any[] = []
              const videosRes = await fetch(`/api/v1x/courses-db/${path.slug}/videos`)
              if (videosRes.ok) {
                const dbVideos = await videosRes.json()
                if (Array.isArray(dbVideos) && dbVideos.length > 0) {
                  videos = dbVideos
                }
              }
              if (videos.length === 0) {
                const fbRes = await fetch(`/api/v1/courses?path=${path.slug}`)
                if (fbRes.ok) {
                  const fb = await fbRes.json()
                  videos = Array.isArray(fb) ? fb : []
                }
              }
              
              // Fetch user progress
              const progressRes = await fetch(`/api/progress/get?path=${path.slug}`)
              const progressData = progressRes.ok ? await progressRes.json() : { completed: [] }
              
              const completed = progressData.completed?.length || 0
              const total = videos.length || 0
              
              stats[path.slug] = {
                slug: path.slug,
                totalVideos: total,
                completedVideos: completed,
                percentage: total > 0 ? Math.round((completed / total) * 100) : 0
              }
            } catch (err) {
              console.error(`Failed to fetch stats for ${path.slug}`, err)
            }
          }
          
          setPathStats(stats)
        }
      } catch (err) {
        setError('Failed to load paths')
      } finally {
        setLoading(false)
      }
    }

    fetchPaths()
  }, [userLoading, me])

  // Filter paths by search query
  const filteredPaths = paths.filter(p =>
    p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.subtitle.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (!me && !userLoading) {
    return (
      <Layout>
        <Head><title>Career Paths – SkillForge Global</title></Head>
        <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Content unavailable</h2>
            <p className="text-gray-600 mb-6">
              Watch videos, complete projects, take quizzes. Your progress is saved when logged in.
            </p>
            <div className="space-x-4">
              <Link
                href="/signup"
                className="inline-block px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Create free account
              </Link>
              <Link
                href="/login"
                className="inline-block px-6 py-3 border border-indigo-300 text-base font-medium rounded-md text-indigo-600 hover:border-indigo-400"
              >
                Sign in
              </Link>
            </div>
          </div>
        </section>
      </Layout>
    )
  }

  return (
    <Layout>
      <Head><title>Career Paths – SkillForge Global</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        <SectionHeading
          title="Choose your Career Path"
          subtitle="Each path includes curated video lessons, projects, quizzes, and interview prep."
        />
        
        {/* Search bar */}
        <div className="mt-8 mb-6 max-w-xl mx-auto">
          <input
            type="text"
            placeholder="🔍 Search career paths..."
            className="w-full h-12 rounded-xl bg-white/[0.06] border border-white/10 px-5 text-sm text-white placeholder:text-techGray focus:outline-none focus:ring-2 focus:ring-forgePurple transition"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <p className="text-xs text-techGray mt-2 text-center">
              Found {filteredPaths.length} of {paths.length} paths
            </p>
          )}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Loading paths...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-500">{error}</p>
          </div>
        ) : filteredPaths.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-techGray mb-4">No paths found matching "{searchQuery}"</p>
            <button
              onClick={() => setSearchQuery('')}
              className="text-forgePurple hover:underline"
            >
              Clear search
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {filteredPaths.map(p => {
              const stats = pathStats[p.slug]
              const hasProgress = stats && stats.completedVideos > 0
              
              return (
                <Link key={p.slug} href={`/paths/${p.slug}`}>
                  <div className="rounded-2xl border border-white/10 bg-white/[0.06] hover:bg-white/[0.08] transition p-5 group">
                    <div className="flex items-start gap-4">
                      <div className="shrink-0 h-12 w-12 rounded-xl bg-gradient-to-br from-forgePurple/40 to-neuralBlue/40 grid place-items-center group-hover:scale-110 transition">
                        <div className="text-aiElectric">{pathIcons[p.slug as keyof typeof pathIcons]}</div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between gap-2">
                          <h3 className="text-base font-semibold">{p.title}</h3>
                          {stats && (
                            <span className={`text-xs px-2 py-1 rounded whitespace-nowrap ${
                              stats.percentage === 100 ? 'bg-green-500/20 text-green-400' :
                              hasProgress ? 'bg-blue-500/20 text-blue-400' :
                              'bg-gray-500/20 text-gray-400'
                            }`}>
                              {stats.percentage === 100 ? 'Completed' : 
                               hasProgress ? 'In Progress' : 'Not Started'}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-techGray mt-1">{p.subtitle}</p>
                        
                        {/* Progress bar and stats */}
                        {stats && (
                          <div className="mt-3 space-y-2">
                            <div className="flex items-center justify-between text-xs text-techGray">
                              <span>{stats.totalVideos} videos</span>
                              {hasProgress && (
                                <span>{stats.completedVideos}/{stats.totalVideos} complete</span>
                              )}
                            </div>
                            
                            {hasProgress && (
                              <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
                                <div 
                                  className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue transition-all duration-500"
                                  style={{ width: `${stats.percentage}%` }}
                                />
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </section>
    </Layout>
  )
}

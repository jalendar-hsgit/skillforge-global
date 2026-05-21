import Head from 'next/head'
import Layout from '@/components/Layout'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'
import { YouTubeCard } from '@/components/YouTubeCard'
import { useMe } from '@/hooks/useMe'
import { ROUTES } from '@/lib/routes'

type CourseItem = { id:string; title:string; youtubeId:string; duration?:string }

export default function PathPage() {
  const router = useRouter()
  const { query } = router
  const slug = Array.isArray(query.slug) ? query.slug[0] : query.slug
  const [items, setItems] = useState<CourseItem[]>([])
  const [completed, setCompleted] = useState<string[]>([])
  const [err, setErr] = useState<string|null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterCompleted, setFilterCompleted] = useState<'all' | 'completed' | 'incomplete'>('all')
  const [sortBy, setSortBy] = useState<'default' | 'title' | 'duration'>('default')
  const { me } = useMe()

  // Helper to format duration seconds to HH:MM:SS or MM:SS
  function formatDuration(seconds: string | number): string {
    const sec = typeof seconds === 'string' ? parseInt(seconds) : seconds
    if (!sec || sec === 0) return '0:00'
    const h = Math.floor(sec / 3600)
    const m = Math.floor((sec % 3600) / 60)
    const s = sec % 60
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
    }
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  useEffect(() => {
    if (!slug && router.isReady) {
      router.push(ROUTES.paths)
    }
  }, [slug, router])

  async function loadProgress() {
    if (!me || !slug) return
    const r = await fetch(`/api/progress/get?path=${slug}`)
    if (r.ok) {
      const d = await r.json()
      setCompleted(d.completed || [])
    }
  }

  useEffect(() => {
    if (!slug) return
    let cancelled = false
    setErr(null)

    const load = async () => {
      // Try DB-backed API first (v1x)
      try {
        const r = await fetch(`/api/v1x/courses-db/${slug}/videos`, { credentials: 'include' })
        if (r.ok) {
          const data = await r.json()
          if (Array.isArray(data) && data.length > 0) {
            const transformed = data.map((v: any) => ({
              id: v.id.toString(),
              title: v.title,
              youtubeId: v.youtube_id,
              duration: formatDuration(v.duration)
            }))
            if (!cancelled) setItems(transformed)
            return
          }
        }
      } catch {}

      // Fallback to file-backed API (v1)
      try {
        const r2 = await fetch(`/api/v1/courses?path=${slug}`, { credentials: 'include' })
        if (r2.ok) {
          const data2 = await r2.json()
          if (Array.isArray(data2) && data2.length > 0) {
            const transformed = data2.map((c: any) => ({
              id: c.id,
              title: c.title,
              youtubeId: c.youtubeId,
              duration: c.duration || undefined
            }))
            if (!cancelled) setItems(transformed)
            return
          }
        }
        if (!cancelled) setErr('Content unavailable')
      } catch {
        if (!cancelled) setErr('Content unavailable')
      }
    }

    load()
    return () => { cancelled = true }
  }, [slug])


  useEffect(() => { loadProgress() }, [slug, me])

  // Filter and sort videos
  const filteredItems = items
    .filter(v => {
      // Search filter
      if (searchQuery && !v.title.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false
      }
      // Completion filter
      if (filterCompleted === 'completed' && !completed.includes(v.id)) return false
      if (filterCompleted === 'incomplete' && completed.includes(v.id)) return false
      return true
    })
    .sort((a, b) => {
      if (sortBy === 'title') return a.title.localeCompare(b.title)
      if (sortBy === 'duration') {
        const durA = parseDuration(a.duration)
        const durB = parseDuration(b.duration)
        return durA - durB
      }
      return 0 // default order
    })

  function parseDuration(dur?: string): number {
    if (!dur) return 0
    const parts = dur.split(':').map(Number)
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if (parts.length === 2) return parts[0] * 60 + parts[1]
    return 0
  }

  const total = items.length || 1
  const done = completed.length
  const pct = Math.round((done / total) * 100)

  async function mark(id: string) {
    if (!me) { alert('Log in to track progress.'); return }
    const r = await fetch('/api/progress/mark', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ path: slug, module_id: id })
    })
    if (r.ok) {
      const d = await r.json()
      setCompleted(d.completed || [])
    } else {
      alert('Could not mark complete')
    }
  }

  return (
    <Layout>
      <Head><title>{`Path – ${slug}`}</title></Head>
      <section className="mx-auto max-w-6xl px-6 pt-36 pb-20">
        <Link href={ROUTES.paths} className="text-techGray hover:text-white text-sm">← Back to paths</Link>

        <div className="mt-4">
          <h1 className="text-3xl font-semibold">Learning path: {slug}</h1>
          <div className="mt-3 flex items-center gap-3">
            <div className="h-2 w-56 rounded bg-white/10 overflow-hidden">
              <div className="h-2 bg-gradient-to-r from-forgePurple to-neuralBlue" style={{width:`${pct}%`}}/>
            </div>
            <div className="text-xs text-techGray">{done}/{total} complete ({pct}%)</div>
          </div>
        </div>

        {err && <div className="mt-6 text-red-400">{err}</div>}

        {/* Search and Filters */}
        <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.06] p-4">
          <div className="grid gap-4 md:grid-cols-3">
            {/* Search */}
            <div className="md:col-span-2">
              <input
                type="text"
                placeholder="🔍 Search videos by title..."
                className="w-full h-11 rounded-lg bg-black/30 border border-white/10 px-4 text-sm text-white placeholder:text-techGray focus:outline-none focus:ring-2 focus:ring-forgePurple"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Filter by completion */}
            <div>
              <select
                className="w-full h-11 rounded-lg bg-black/30 border border-white/10 px-4 text-sm text-white focus:outline-none focus:ring-2 focus:ring-forgePurple"
                value={filterCompleted}
                onChange={(e) => setFilterCompleted(e.target.value as any)}
              >
                <option value="all">All videos ({items.length})</option>
                <option value="completed">Completed ({done})</option>
                <option value="incomplete">Incomplete ({items.length - done})</option>
              </select>
            </div>
          </div>

          {/* Sort options */}
          <div className="flex items-center gap-2 mt-3 text-sm">
            <span className="text-techGray">Sort by:</span>
            <button
              onClick={() => setSortBy('default')}
              className={`px-3 py-1.5 rounded-md transition ${sortBy === 'default' ? 'bg-forgePurple text-white' : 'bg-white/5 text-techGray hover:text-white'}`}
            >
              Default
            </button>
            <button
              onClick={() => setSortBy('title')}
              className={`px-3 py-1.5 rounded-md transition ${sortBy === 'title' ? 'bg-forgePurple text-white' : 'bg-white/5 text-techGray hover:text-white'}`}
            >
              Title A-Z
            </button>
            <button
              onClick={() => setSortBy('duration')}
              className={`px-3 py-1.5 rounded-md transition ${sortBy === 'duration' ? 'bg-forgePurple text-white' : 'bg-white/5 text-techGray hover:text-white'}`}
            >
              Duration
            </button>
          </div>

          {/* Results count */}
          {searchQuery && (
            <div className="mt-3 text-xs text-techGray">
              Found {filteredItems.length} of {items.length} videos
            </div>
          )}
        </div>

        <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.06] p-6">
          <h2 className="font-semibold text-xl mb-3">Overview</h2>
          <p className="text-sm text-techGray mb-4">Watch videos, complete projects, take quizzes. Your progress is saved when logged in.</p>
          <div className="flex flex-wrap gap-3">
            <Link href={ROUTES.signup} className="inline-flex h-12 items-center justify-center rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue px-6 font-semibold">
              Create free account
            </Link>
            <Link href={ROUTES.quiz(slug)} className="inline-flex h-12 items-center justify-center rounded-md bg-white/10 border border-white/10 px-6 font-semibold">
              Take quiz
            </Link>
          </div>
        </div>

        <h2 className="text-xl font-semibold mt-10">Module Videos</h2>
        
        {filteredItems.length === 0 ? (
          <div className="mt-6 text-center py-12 text-techGray">
            <p>No videos found matching your filters.</p>
            <button
              onClick={() => {
                setSearchQuery('')
                setFilterCompleted('all')
                setSortBy('default')
              }}
              className="mt-4 text-forgePurple hover:underline"
            >
              Clear all filters
            </button>
          </div>
        ) : (
          <div className="grid gap-6 mt-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {filteredItems.map(v => (
            <div key={v.id} className="rounded-2xl border border-white/10 bg-white/[0.06] overflow-hidden flex flex-col group">
              <Link href={`/watch/${v.id}`} className="aspect-video relative overflow-hidden">
                <img
                  src={`https://i.ytimg.com/vi/${v.youtubeId}/hqdefault.jpg`}
                  alt={v.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
                  <div className="w-16 h-16 rounded-full bg-forgePurple/90 flex items-center justify-center">
                    <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                    </svg>
                  </div>
                </div>
                {v.duration && (
                  <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
                    {v.duration}
                  </div>
                )}
                {completed.includes(v.id) && (
                  <div className="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Done
                  </div>
                )}
              </Link>
              <div className="flex items-start justify-between px-4 py-3 gap-3">
                <div className="flex-1">
                  <Link href={`/watch/${v.id}`} className="text-sm font-medium line-clamp-2 hover:text-forgePurple transition">{v.title}</Link>
                  <div className="text-xs text-techGray mt-1">{completed.includes(v.id) ? 'Completed' : 'Not completed'}</div>
                </div>
                <button onClick={()=>mark(v.id)} className={`h-9 px-3 rounded-md whitespace-nowrap text-sm ${completed.includes(v.id) ? 'bg-white/10 border border-white/10' : 'bg-gradient-to-r from-forgePurple to-neuralBlue'}`}>
                  {completed.includes(v.id) ? '✓' : 'Mark'}
                </button>
              </div>
            </div>
            ))}
          </div>
        )}
      </section>
    </Layout>
  )
}

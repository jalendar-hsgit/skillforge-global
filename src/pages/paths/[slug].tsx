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
  const { query } = useRouter()
  const slug = String(query.slug || '')
  const [items, setItems] = useState<CourseItem[]>([])
  const [completed, setCompleted] = useState<string[]>([])
  const [err, setErr] = useState<string|null>(null)
  const { me } = useMe()

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
    setErr(null)
    fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1/courses?path=${slug}`)
      .then(r => r.ok ? r.json() : Promise.reject('error'))
      .then(setItems)
      .catch(()=>setErr('Content unavailable'))
  }, [slug])

  useEffect(() => { loadProgress() }, [slug, me])

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
        <div className="grid gap-6 mt-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {items.map(v => (
            <div key={v.id} className="rounded-2xl border border-white/10 bg-white/[0.06] overflow-hidden flex flex-col">
              <div className="aspect-video">
                <YouTubeCard title={v.title} youtubeId={v.youtubeId} duration={v.duration} />
              </div>
              <div className="flex items-start justify-between px-4 py-3 gap-3">
                <div>
                  <div className="text-sm font-medium line-clamp-2">{v.title}</div>
                  <div className="text-xs text-techGray">{completed.includes(v.id) ? 'Completed' : 'Not completed'}</div>
                </div>
                <button onClick={()=>mark(v.id)} className={`h-9 px-3 rounded-md whitespace-nowrap ${completed.includes(v.id) ? 'bg-white/10 border border-white/10' : 'bg-gradient-to-r from-forgePurple to-neuralBlue'}`}>
                  {completed.includes(v.id) ? 'Completed' : 'Mark'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </Layout>
  )
}

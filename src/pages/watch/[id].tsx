import { useRouter } from 'next/router'
import { useEffect, useState, useRef } from 'react'
import Head from 'next/head'
import Layout from '@/components/Layout'
import Link from 'next/link'
import { useMe } from '@/hooks/useMe'
import { Play, CheckCircle2, Clock } from 'lucide-react'

interface VideoData {
  id: string
  title: string
  youtubeId: string
  duration: string
  path?: string
  description?: string
}

interface RelatedVideo {
  id: string
  title: string
  youtubeId: string
  duration: string
}

export default function WatchPage() {
  const router = useRouter()
  const { id } = router.query
  const { me } = useMe()
  
  const [video, setVideo] = useState<VideoData | null>(null)
  const [relatedVideos, setRelatedVideos] = useState<RelatedVideo[]>([])
  const [progress, setProgress] = useState(0)
  const [isCompleted, setIsCompleted] = useState(false)
  const [loading, setLoading] = useState(true)
  const playerRef = useRef<HTMLIFrameElement>(null)

  useEffect(() => {
    if (!id) return
    
    // Fetch video details from DB-backed API first, then fallback to file-backed courses
    const fetchVideo = async () => {
      try {
        const paths = ['python-ai', 'fullstack', 'aws-devops', 'cybersec', 'flutter']
        let foundAny = false
        
        for (const path of paths) {
          const response = await fetch(`/api/v1x/courses-db/${path}/videos`, {
            credentials: 'include'
          })
          
          if (response.ok) {
            const videos = await response.json()
            const found = videos.find((v: any) => v.id.toString() === id)
            
            if (found) {
              setVideo({
                id: found.id.toString(),
                title: found.title,
                youtubeId: found.youtube_id,
                duration: formatDuration(found.duration),
                path: path
              })
              
              // Get related videos from same path
              setRelatedVideos(
                videos
                  .filter((v: any) => v.id.toString() !== id)
                  .slice(0, 5)
                  .map((v: any) => ({
                    id: v.id.toString(),
                    title: v.title,
                    youtubeId: v.youtube_id,
                    duration: formatDuration(v.duration)
                  }))
              )
              foundAny = true
              break
            }
          }
        }

        if (!foundAny) {
          // Fallback: search in file-backed courses list (v1)
          const r = await fetch('/api/v1/courses', { credentials: 'include' })
          if (r.ok) {
            const all = await r.json()
            const found = all.find((c: any) => c.id.toString() === id)
            if (found) {
              setVideo({
                id: found.id.toString(),
                title: found.title,
                youtubeId: found.youtubeId,
                duration: found.duration || '—',
                path: found.path
              })
              const related = all
                .filter((c: any) => c.path === found.path && c.id.toString() !== id)
                .slice(0, 5)
                .map((c: any) => ({
                  id: c.id.toString(),
                  title: c.title,
                  youtubeId: c.youtubeId,
                  duration: c.duration || '—'
                }))
              setRelatedVideos(related)
              foundAny = true
            }
          }
        }
      } catch (err) {
        console.error('Failed to load video', err)
      } finally {
        setLoading(false)
      }
    }

    fetchVideo()
  }, [id])

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
    if (!me || !id) return
    
    // Fetch current progress
    const fetchProgress = async () => {
      try {
        const response = await fetch(`/api/v1/progress/videos/${id}`, {
          credentials: 'include'
        })
        if (response.ok) {
          const data = await response.json()
          setProgress(data.progress_percent || 0)
          setIsCompleted(data.progress_percent >= 95)
        }
      } catch (err) {
        console.error('Failed to load progress', err)
      }
    }

    fetchProgress()
  }, [id, me])

  const markAsComplete = async () => {
    if (!me || !id) {
      alert('Please log in to track progress')
      return
    }

    try {
      const response = await fetch(`/api/v1/progress/videos/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          progress_percent: 100,
          last_position_sec: 0
        })
      })

      if (response.ok) {
        setProgress(100)
        setIsCompleted(true)
      } else {
        alert('Failed to mark as complete')
      }
    } catch (err) {
      console.error('Failed to mark complete', err)
      alert('Failed to mark as complete')
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <p className="text-techGray">Loading video...</p>
        </div>
      </Layout>
    )
  }

  if (!video) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <p className="text-techGray mb-4">Video not found</p>
            <Link href="/paths" className="text-forgePurple hover:underline">
              Browse all paths
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <Head>
        <title>{video.title} – SkillForge Global</title>
      </Head>
      
      <div className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        {/* Back button */}
        {video.path && (
          <Link 
            href={`/paths/${video.path}`}
            className="text-techGray hover:text-white text-sm mb-4 inline-block"
          >
            ← Back to {video.path} path
          </Link>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main video player */}
          <div className="lg:col-span-2">
            <div className="rounded-2xl overflow-hidden border border-white/10 bg-white/[0.06]">
              <div className="aspect-video">
                <iframe
                  ref={playerRef}
                  className="w-full h-full"
                  src={`https://www.youtube.com/embed/${video.youtubeId}?autoplay=1&rel=0`}
                  title={video.title}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  referrerPolicy="strict-origin-when-cross-origin"
                  allowFullScreen
                />
              </div>
            </div>

            {/* Video info */}
            <div className="mt-6">
              <h1 className="text-2xl font-bold">{video.title}</h1>
              
              <div className="flex items-center gap-4 mt-4 text-sm">
                <div className="flex items-center gap-2 text-techGray">
                  <Clock className="w-4 h-4" />
                  {video.duration}
                </div>
                
                {me && (
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-32 rounded-full bg-white/10 overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-techGray">{progress}%</span>
                  </div>
                )}
              </div>

              {/* Action buttons */}
              {me && (
                <div className="flex gap-3 mt-6">
                  <button
                    onClick={markAsComplete}
                    disabled={isCompleted}
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition ${
                      isCompleted
                        ? 'bg-white/10 border border-white/10 text-techGray cursor-not-allowed'
                        : 'bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90'
                    }`}
                  >
                    <CheckCircle2 className="w-5 h-5" />
                    {isCompleted ? 'Completed' : 'Mark as Complete'}
                  </button>
                </div>
              )}

              {!me && (
                <div className="mt-6 p-4 rounded-xl bg-white/[0.06] border border-white/10">
                  <p className="text-sm text-techGray mb-3">
                    Sign in to track your progress and earn certificates
                  </p>
                  <div className="flex gap-3">
                    <Link
                      href="/signup"
                      className="px-4 py-2 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue font-semibold text-sm"
                    >
                      Create Account
                    </Link>
                    <Link
                      href="/login"
                      className="px-4 py-2 rounded-lg bg-white/10 border border-white/10 font-semibold text-sm"
                    >
                      Sign In
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar - Related videos */}
          <div className="lg:col-span-1">
            <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-5">
              <h2 className="font-semibold mb-4">Related Videos</h2>
              
              {relatedVideos.length === 0 ? (
                <p className="text-sm text-techGray">No related videos</p>
              ) : (
                <div className="space-y-3">
                  {relatedVideos.map(v => (
                    <Link
                      key={v.id}
                      href={`/watch/${v.id}`}
                      className="block rounded-lg overflow-hidden border border-white/10 bg-white/[0.03] hover:bg-white/[0.06] transition"
                    >
                      <div className="aspect-video relative">
                        <img
                          src={`https://i.ytimg.com/vi/${v.youtubeId}/hqdefault.jpg`}
                          alt={v.title}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 hover:opacity-100 transition">
                          <Play className="w-10 h-10 text-white" />
                        </div>
                      </div>
                      <div className="p-3">
                        <p className="text-sm font-medium line-clamp-2">{v.title}</p>
                        <p className="text-xs text-techGray mt-1">{v.duration}</p>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

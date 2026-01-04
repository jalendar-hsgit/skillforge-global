import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Layout from '@/components/Layout'
import ResumeImportModal from '@/components/resume/ResumeImportModal'
import { FileText, Plus, Upload, Edit, Eye, Trash2, Copy } from 'lucide-react'
import type { GetServerSideProps } from 'next'

interface Resume {
  id: number
  title: string
  template_id: string
  full_name?: string
  updated_at: string
  views: number
}

export const getServerSideProps: GetServerSideProps = async (ctx) => {
  const base = `http://${ctx.req.headers.host}`
  const r = await fetch(`${base}/api/session/me`, {
    headers: { cookie: ctx.req.headers.cookie || '' }
  })
  if (!r.ok) {
    return { redirect: { destination: `/login?redirect=${encodeURIComponent('/resumes')}`, permanent: false } }
  }
  const me = await r.json()
  return { props: { me } }
}

export default function ResumesPage({ me }: { me: any }) {
  const router = useRouter()
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(true)
  const [showImportModal, setShowImportModal] = useState(false)

  useEffect(() => {
    fetchResumes()
  }, [])

  const fetchResumes = async () => {
    try {
      const res = await fetch('/api/session/resumes', {
        credentials: 'include',
      })

      if (res.ok) {
        const data = await res.json()
        setResumes(data)
      }
    } catch (e) {
      console.error('Failed to fetch resumes:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateNew = async () => {
    router.push('/resumes/new')
  }

  const handleImportSuccess = (resumeId: number) => {
    // After importing, open the resume editor so user can make edits immediately
    router.push(`/resumes/${resumeId}/edit`)
  }

  const handleEdit = (resumeId: number) => {
    router.push(`/resumes/${resumeId}`)
  }

  const handlePreview = (resumeId: number) => {
    router.push(`/resumes/${resumeId}/preview`)
  }

  const handleDuplicate = async (resumeId: number) => {
    try {
      const res = await fetch(`/api/session/resumes?id=${resumeId}&action=duplicate`, {
        method: 'POST',
        credentials: 'include',
      })

      if (res.ok) {
        const newResume = await res.json()
        setResumes([...resumes, newResume])
        alert('Resume duplicated successfully!')
        router.push(`/resumes/${newResume.id}/edit`)
      } else {
        const error = await res.json().catch(() => ({}))
        alert(`Failed to duplicate: ${error.detail || 'Unknown error'}`)
      }
    } catch (e) {
      console.error('Failed to duplicate resume:', e)
      alert('Failed to duplicate resume.')
    }
  }

  const handleDelete = async (resumeId: number) => {
    if (!confirm('Are you sure you want to delete this resume?')) return

    try {
      const res = await fetch(`/api/session/resumes?id=${resumeId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      if (res.ok) {
        setResumes(resumes.filter(r => r.id !== resumeId))
      }
    } catch (e) {
      console.error('Failed to delete resume:', e)
    }
  }

  return (
    <Layout>
      <Head>
        <title>My Resumes - SkillForge Global</title>
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech/95 to-deepTech/90 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">My Resumes</h1>
              <p className="text-white/60">Create, manage, and export your professional resumes</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => router.push('/resumes/templates')}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/10 border border-white/20 text-white hover:bg-white/20 transition-all"
              >
                🎨 Templates
              </button>
              <button
                onClick={() => router.push('/resumes/compare')}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/10 border border-white/20 text-white hover:bg-white/20 transition-all"
              >
                ⚖️ Compare
              </button>
              <button
                onClick={() => setShowImportModal(true)}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/10 border border-white/20 text-white hover:bg-white/20 transition-all"
              >
                <Upload className="w-5 h-5" />
                Import Resume
              </button>
              <button
                onClick={handleCreateNew}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-forgePurple to-neuralBlue text-white font-semibold hover:shadow-lg transition-all"
              >
                <Plus className="w-5 h-5" />
                Create New
              </button>
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-forgePurple/20 border-t-forgePurple"></div>
            </div>
          )}

          {/* Empty State */}
          {!loading && resumes.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-20 h-20 rounded-2xl bg-white/5 flex items-center justify-center mb-6">
                <FileText className="w-10 h-10 text-white/40" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">No resumes yet</h2>
              <p className="text-white/60 mb-8 max-w-md">
                Start creating your professional resume or import an existing one to get started.
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => setShowImportModal(true)}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/10 border border-white/20 text-white hover:bg-white/20 transition-all"
                >
                  <Upload className="w-5 h-5" />
                  Import Resume
                </button>
                <button
                  onClick={handleCreateNew}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-forgePurple to-neuralBlue text-white font-semibold hover:shadow-lg transition-all"
                >
                  <Plus className="w-5 h-5" />
                  Create New Resume
                </button>
              </div>
            </div>
          )}

          {/* Resumes Grid */}
          {!loading && resumes.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {resumes.map((resume, index) => (
                <div
                  key={resume.id}
                  className="group relative bg-gradient-to-br from-white/10 via-white/5 to-transparent backdrop-blur-xl border border-white/20 rounded-2xl p-6 hover:border-forgePurple/50 hover:shadow-2xl hover:shadow-forgePurple/20 transition-all duration-300 hover:scale-[1.02] animate-fade-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {/* Gradient Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-br from-forgePurple/5 to-neuralBlue/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  
                  {/* Resume Card Content */}
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-xl font-bold text-white mb-2 line-clamp-2 group-hover:text-forgePurple transition-colors">
                          {resume.title}
                        </h3>
                        <p className="text-sm text-white/70 font-medium flex items-center gap-2">
                          <span className="truncate">{resume.full_name || 'Untitled'}</span>
                        </p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-forgePurple to-neuralBlue flex items-center justify-center flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform duration-300">
                        <FileText className="w-6 h-6 text-white" />
                      </div>
                    </div>

                    {/* Stats Bar */}
                    <div className="flex items-center gap-3 mb-4 p-3 rounded-lg bg-white/5 border border-white/10">
                      <div className="flex items-center gap-2 text-xs text-white/60">
                        <div className="w-2 h-2 rounded-full bg-forgePurple animate-pulse" />
                        <span className="font-semibold capitalize">{resume.template_id}</span>
                      </div>
                      <span className="text-white/30">•</span>
                      <div className="flex items-center gap-1 text-xs text-white/60">
                        <Eye className="w-3 h-3" />
                        <span className="font-semibold">{resume.views}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-white/50 mb-5 font-medium">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>Updated {new Date(resume.updated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 mb-3">
                      <button
                        onClick={() => handleEdit(resume.id)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-forgePurple to-neuralBlue text-white font-semibold hover:shadow-lg hover:shadow-forgePurple/30 transition-all duration-300 hover:scale-[1.02]"
                      >
                        <Edit className="w-4 h-4" />
                        <span>Edit</span>
                      </button>
                      <button
                        onClick={() => handlePreview(resume.id)}
                        className="flex items-center justify-center p-3 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 hover:border-white/30 transition-all duration-200"
                        title="Preview"
                      >
                        <Eye className="w-4 h-4 text-white" />
                      </button>
                      <button
                        onClick={() => handleDuplicate(resume.id)}
                        className="flex items-center justify-center p-3 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 hover:border-white/30 transition-all duration-200"
                        title="Duplicate"
                      >
                        <Copy className="w-4 h-4 text-white" />
                      </button>
                      <button
                        onClick={() => handleDelete(resume.id)}
                        className="flex items-center justify-center p-3 rounded-xl bg-white/10 hover:bg-red-500/30 border border-white/20 hover:border-red-500/50 transition-all duration-200 group/delete"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4 text-white/70 group-hover/delete:text-red-400 transition-colors" />
                      </button>
                    </div>

                    {/* Quick Links */}
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <button
                        onClick={() => router.push(`/resumes/${resume.id}/ats-score`)}
                        className="px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 hover:text-white border border-white/10 transition"
                      >
                        🤖 ATS Score
                      </button>
                      <button
                        onClick={() => router.push(`/resumes/${resume.id}/export`)}
                        className="px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 hover:text-white border border-white/10 transition"
                      >
                        📥 Export
                      </button>
                      <button
                        onClick={() => router.push(`/resumes/${resume.id}/versions`)}
                        className="px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 hover:text-white border border-white/10 transition"
                      >
                        ⏱️ Versions
                      </button>
                      <button
                        onClick={() => router.push(`/resumes/${resume.id}/sharing`)}
                        className="px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 hover:text-white border border-white/10 transition"
                      >
                        🔗 Share
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Import Modal */}
      <ResumeImportModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onImportSuccess={handleImportSuccess}
      />
    </Layout>
  )
}

import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Layout from '@/components/Layout'
import { PageHeader, PageSection, PageContainer } from '@/components/PageLayout'
import { Button } from '@/components/Button'
import { AlertCard } from '@/components/Cards'
import { Copy, Globe, Lock, Eye, EyeOff, Share2 } from 'lucide-react'

interface Resume {
  id: number
  title: string
  is_public: boolean
  full_name?: string
}

interface ShareSettings {
  is_public: boolean
  public_link: string
  view_only: boolean
  download_allowed: boolean
  expiration_date?: string
}

export default function SharingPage() {
  const router = useRouter()
  const { id } = router.query
  const [resume, setResume] = useState<Resume | null>(null)
  const [shareSettings, setShareSettings] = useState<ShareSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (id) {
      fetchResume()
      fetchShareSettings()
    }
  }, [id])

  const fetchResume = async () => {
    try {
      const res = await fetch(`/api/session/resumes/${id}`, {
        credentials: 'include',
      })
      if (res.ok) {
        const data = await res.json()
        setResume(data)
      }
    } catch (e) {
      console.error('Error fetching resume:', e)
    }
  }

  const fetchShareSettings = async () => {
    try {
      setLoading(true)
      // This endpoint might not exist yet, so we'll create default settings
      const res = await fetch(`/api/v1x/resumes/${id}/share-settings`, {
        credentials: 'include',
      })
      
      if (res.ok) {
        const data = await res.json()
        setShareSettings(data)
      } else {
        // Create default settings
        setShareSettings({
          is_public: false,
          public_link: `${window.location.origin}/public/resumes/${id}`,
          view_only: true,
          download_allowed: false,
        })
      }
    } catch (e) {
      console.error('Error fetching share settings:', e)
      // Set default
      setShareSettings({
        is_public: false,
        public_link: `${typeof window !== 'undefined' ? window.location.origin : ''}/public/resumes/${id}`,
        view_only: true,
        download_allowed: false,
      })
    } finally {
      setLoading(false)
    }
  }

  const togglePublic = async () => {
    if (!shareSettings) return

    try {
      setUpdating(true)
      const res = await fetch(`/api/v1x/resumes/${id}/share-settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          is_public: !shareSettings.is_public,
          view_only: shareSettings.view_only,
          download_allowed: shareSettings.download_allowed,
        }),
      })

      if (res.ok) {
        const data = await res.json()
        setShareSettings(data)
        setError(null)
      } else {
        setError('Failed to update sharing settings')
      }
    } catch (e) {
      console.error('Error updating settings:', e)
      setError('Error updating settings')
    } finally {
      setUpdating(false)
    }
  }

  const toggleDownload = async () => {
    if (!shareSettings) return

    try {
      setUpdating(true)
      const res = await fetch(`/api/v1x/resumes/${id}/share-settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          is_public: shareSettings.is_public,
          view_only: shareSettings.view_only,
          download_allowed: !shareSettings.download_allowed,
        }),
      })

      if (res.ok) {
        const data = await res.json()
        setShareSettings(data)
        setError(null)
      } else {
        setError('Failed to update sharing settings')
      }
    } catch (e) {
      console.error('Error updating settings:', e)
      setError('Error updating settings')
    } finally {
      setUpdating(false)
    }
  }

  const copyLink = () => {
    if (shareSettings?.public_link) {
      navigator.clipboard.writeText(shareSettings.public_link)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (loading) {
    return (
      <Layout maxWidth="7xl">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Loading sharing settings...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <>
      <Head>
        <title>Sharing - {resume?.title || 'Resume'} - SkillForge</title>
      </Head>

      <Layout maxWidth="7xl">
        <PageHeader
          icon="🔗"
          title="Sharing & Privacy"
          subtitle="Control who can view and download your resume"
          breadcrumbs={[
            { label: 'Resumes', href: '/resumes' },
            { label: resume?.title || 'Resume', href: `/resumes/${id}` },
            { label: 'Sharing' },
          ]}
        />

        {error && (
          <div className="mb-8">
            <AlertCard
              variant="error"
              title="Error"
              message={error}
              action={
                <Button variant="secondary" size="sm" onClick={() => setError(null)}>
                  Dismiss
                </Button>
              }
            />
          </div>
        )}

        {/* Public/Private Toggle */}
        <PageSection icon="🔐" title="Resume Visibility">
          <div className="space-y-4">
            {/* Current Status */}
            <div className="bg-white rounded-lg border-2 p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="font-semibold text-gray-900 mb-1">
                    {shareSettings?.is_public ? '🌐 Public' : '🔒 Private'}
                  </p>
                  <p className="text-sm text-gray-600">
                    {shareSettings?.is_public
                      ? 'Your resume is visible to anyone with the link'
                      : 'Only you can view this resume'}
                  </p>
                </div>
              </div>

              <Button
                onClick={togglePublic}
                disabled={updating}
                className={
                  shareSettings?.is_public
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }
              >
                {shareSettings?.is_public ? 'Make Private' : 'Make Public'}
              </Button>
            </div>

            {/* Public Link (only show if public) */}
            {shareSettings?.is_public && (
              <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
                <p className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Globe className="w-5 h-5 text-blue-600" />
                  Public Link
                </p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={shareSettings?.public_link || ''}
                    readOnly
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-white font-mono text-sm"
                  />
                  <Button
                    onClick={copyLink}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {copied ? '✓ Copied' : 'Copy'}
                  </Button>
                </div>
                <p className="text-xs text-gray-600 mt-2">
                  Share this link with recruiters, employers, or anyone you want to see your resume.
                </p>
              </div>
            )}
          </div>
        </PageSection>

        {/* Access Permissions */}
        {shareSettings?.is_public && (
          <PageSection icon="👥" title="Access Permissions">
            <div className="space-y-4">
              {/* Download Permission */}
              <div className="bg-white rounded-lg border p-6 flex items-start justify-between">
                <div>
                  <p className="font-semibold text-gray-900 mb-1">
                    {shareSettings?.download_allowed ? '📥 Downloads Enabled' : '🚫 Downloads Disabled'}
                  </p>
                  <p className="text-sm text-gray-600">
                    {shareSettings?.download_allowed
                      ? 'Anyone with the link can download your resume'
                      : 'People can only view, not download'}
                  </p>
                </div>
                <Button
                  onClick={toggleDownload}
                  disabled={updating}
                  className={
                    shareSettings?.download_allowed
                      ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                      : 'bg-gray-600 hover:bg-gray-700 text-white'
                  }
                  size="sm"
                >
                  {shareSettings?.download_allowed ? 'Disable' : 'Enable'}
                </Button>
              </div>

              {/* View Only Info */}
              <AlertCard
                variant="info"
                title="View-Only by Default"
                message="Viewers cannot modify your resume. They can only see it in the format you've shared."
              />
            </div>
          </PageSection>
        )}

        {/* Sharing Methods */}
        {shareSettings?.is_public && (
          <PageSection icon="📤" title="How to Share">
            <div className="grid grid-cols-2 gap-4">
              {/* Email */}
              <div className="bg-white rounded-lg border p-4">
                <p className="font-semibold text-gray-900 mb-2">✉️ Email</p>
                <p className="text-sm text-gray-600 mb-3">
                  Send the link directly to recruiters or hiring managers.
                </p>
                <Button
                  onClick={() => {
                    const subject = `Resume: ${resume?.full_name || resume?.title}`
                    const body = `Check out my resume: ${shareSettings?.public_link}`
                    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
                  }}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm"
                  size="sm"
                >
                  Email Link
                </Button>
              </div>

              {/* LinkedIn */}
              <div className="bg-white rounded-lg border p-4">
                <p className="font-semibold text-gray-900 mb-2">💼 LinkedIn</p>
                <p className="text-sm text-gray-600 mb-3">
                  Share on your LinkedIn profile or in messages.
                </p>
                <Button
                  onClick={() => {
                    const text = `Check out my resume: ${shareSettings?.public_link}`
                    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareSettings?.public_link || '')}`, '_blank')
                  }}
                  className="w-full bg-blue-700 hover:bg-blue-800 text-white text-sm"
                  size="sm"
                >
                  Share on LinkedIn
                </Button>
              </div>

              {/* Twitter */}
              <div className="bg-white rounded-lg border p-4">
                <p className="font-semibold text-gray-900 mb-2">𝕏 Twitter</p>
                <p className="text-sm text-gray-600 mb-3">
                  Share your resume on social media.
                </p>
                <Button
                  onClick={() => {
                    const text = `Check out my resume: ${shareSettings?.public_link}`
                    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank')
                  }}
                  className="w-full bg-black hover:bg-gray-800 text-white text-sm"
                  size="sm"
                >
                  Tweet
                </Button>
              </div>

              {/* Copy Link */}
              <div className="bg-white rounded-lg border p-4">
                <p className="font-semibold text-gray-900 mb-2">🔗 Copy Link</p>
                <p className="text-sm text-gray-600 mb-3">
                  Copy and paste anywhere you need.
                </p>
                <Button
                  onClick={copyLink}
                  className="w-full bg-gray-600 hover:bg-gray-700 text-white text-sm"
                  size="sm"
                >
                  {copied ? '✓ Copied' : 'Copy Link'}
                </Button>
              </div>
            </div>
          </PageSection>
        )}

        {/* Privacy Tips */}
        <PageSection icon="💡" title="Privacy & Security Tips">
          <div className="space-y-3 bg-gray-50 rounded-lg p-6">
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold flex-shrink-0">1.</span>
              <p className="text-gray-700 text-sm">
                <strong>Only make public when necessary:</strong> Share your resume only with trusted recruiters and employers.
              </p>
            </div>
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold flex-shrink-0">2.</span>
              <p className="text-gray-700 text-sm">
                <strong>Disable downloads for sensitive versions:</strong> Keep sensitive information safe by disabling downloads.
              </p>
            </div>
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold flex-shrink-0">3.</span>
              <p className="text-gray-700 text-sm">
                <strong>Review before sharing:</strong> Always check your resume content before making it public.
              </p>
            </div>
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold flex-shrink-0">4.</span>
              <p className="text-gray-700 text-sm">
                <strong>Use a separate email:</strong> Consider using a professional email address for public links.
              </p>
            </div>
          </div>
        </PageSection>

        {/* Back Button */}
        <div className="flex gap-3 mt-8">
          <Button
            onClick={() => router.push(`/resumes/${id}/edit`)}
            className="bg-gray-600 hover:bg-gray-700 text-white"
          >
            Back to Edit
          </Button>
          <Button
            onClick={() => router.push('/resumes')}
            variant="secondary"
          >
            Back to Resumes
          </Button>
        </div>
      </Layout>
    </>
  )
}

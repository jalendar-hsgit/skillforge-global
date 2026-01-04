import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Layout from '@/components/Layout'
import { PageHeader, PageSection, PageContainer } from '@/components/PageLayout'
import { Button } from '@/components/Button'
import { AlertCard } from '@/components/Cards'
import { ChevronRight, Clock, Download, Eye, Trash2, Copy } from 'lucide-react'

interface ResumeVersion {
  id: number
  version_number: number
  created_at: string
  updated_at: string
  changes: string
  is_current: boolean
}

interface Resume {
  id: number
  title: string
  version: number
  updated_at: string
}

export default function VersionHistoryPage() {
  const router = useRouter()
  const { id } = router.query
  const [resume, setResume] = useState<Resume | null>(null)
  const [versions, setVersions] = useState<ResumeVersion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedVersion, setExpandedVersion] = useState<number | null>(null)

  useEffect(() => {
    if (id) {
      fetchResume()
      fetchVersions()
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

  const fetchVersions = async () => {
    try {
      setLoading(true)
      const res = await fetch(`/api/v1x/resumes/${id}/versions`, {
        credentials: 'include',
      })
      if (res.ok) {
        const data = await res.json()
        setVersions(data)
      } else {
        setError('Failed to load version history')
      }
    } catch (e) {
      console.error('Error fetching versions:', e)
      setError('Error loading versions')
    } finally {
      setLoading(false)
    }
  }

  const restoreVersion = async (versionId: number) => {
    try {
      const res = await fetch(`/api/v1x/resumes/${id}/restore/${versionId}`, {
        method: 'POST',
        credentials: 'include',
      })
      if (res.ok) {
        setError(null)
        // Refresh versions
        fetchVersions()
        fetchResume()
        // Show success message
        alert('Version restored successfully!')
      } else {
        setError('Failed to restore version')
      }
    } catch (e) {
      console.error('Error restoring version:', e)
      setError('Error restoring version')
    }
  }

  const deleteVersion = async (versionId: number) => {
    if (!confirm('Are you sure you want to delete this version?')) return

    try {
      const res = await fetch(`/api/v1x/resumes/${id}/versions/${versionId}`, {
        method: 'DELETE',
        credentials: 'include',
      })
      if (res.ok) {
        setError(null)
        fetchVersions()
        alert('Version deleted successfully')
      } else {
        setError('Failed to delete version')
      }
    } catch (e) {
      console.error('Error deleting version:', e)
      setError('Error deleting version')
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString()
  }

  if (loading) {
    return (
      <Layout maxWidth="7xl">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Loading version history...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <>
      <Head>
        <title>Version History - {resume?.title || 'Resume'} - SkillForge</title>
      </Head>

      <Layout maxWidth="7xl">
        <PageHeader
          icon="⏱️"
          title="Version History"
          subtitle="Track and manage all versions of your resume"
          breadcrumbs={[
            { label: 'Resumes', href: '/resumes' },
            { label: resume?.title || 'Resume', href: `/resumes/${id}` },
            { label: 'Versions' },
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

        {versions.length === 0 ? (
          <PageSection icon="📋" title="No Versions">
            <PageContainer variant="glass" className="text-center py-12">
              <p className="text-gray-600">No version history yet. Start editing your resume to create versions.</p>
            </PageContainer>
          </PageSection>
        ) : (
          <PageSection icon="📜" title={`All Versions (${versions.length})`}>
            <div className="space-y-3">
              {versions.map((version) => (
                <div
                  key={version.id}
                  className="bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition"
                >
                  {/* Version Header */}
                  <button
                    onClick={() => setExpandedVersion(expandedVersion === version.id ? null : version.id)}
                    className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 cursor-pointer"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <Clock className="w-5 h-5 text-blue-600 flex-shrink-0" />
                      <div className="text-left">
                        <p className="font-semibold text-gray-900">
                          Version {version.version_number}
                          {version.is_current && <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded ml-2">Current</span>}
                        </p>
                        <p className="text-sm text-gray-500">
                          {formatDate(version.updated_at || version.created_at)}
                        </p>
                      </div>
                    </div>
                    <ChevronRight
                      className={`w-5 h-5 text-gray-400 transition ${expandedVersion === version.id ? 'rotate-90' : ''}`}
                    />
                  </button>

                  {/* Version Details */}
                  {expandedVersion === version.id && (
                    <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
                      {version.changes && (
                        <div className="mb-4">
                          <p className="text-sm font-semibold text-gray-700 mb-2">Changes:</p>
                          <p className="text-sm text-gray-600 whitespace-pre-wrap">{version.changes}</p>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex gap-2">
                        <Button
                          onClick={() => restoreVersion(version.id)}
                          disabled={version.is_current}
                          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
                          size="sm"
                        >
                          <Copy className="w-4 h-4" />
                          {version.is_current ? 'Current Version' : 'Restore'}
                        </Button>
                        <Button
                          onClick={() => {
                            // Open preview of this version
                            window.open(`/api/v1x/resumes/${id}/versions/${version.id}/preview`, '_blank')
                          }}
                          className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white"
                          size="sm"
                        >
                          <Eye className="w-4 h-4" />
                          Preview
                        </Button>
                        <Button
                          onClick={() => deleteVersion(version.id)}
                          disabled={version.is_current}
                          className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
                          size="sm"
                        >
                          <Trash2 className="w-4 h-4" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </PageSection>
        )}

        {/* Info Box */}
        <PageSection icon="ℹ️" title="About Versions">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 space-y-3">
            <p className="text-sm text-gray-700">
              ✅ <strong>Automatic Versioning:</strong> A new version is created each time you save significant changes to your resume.
            </p>
            <p className="text-sm text-gray-700">
              ✅ <strong>Version Recovery:</strong> Restore any previous version of your resume in one click.
            </p>
            <p className="text-sm text-gray-700">
              ✅ <strong>Version Preview:</strong> See exactly what changes were made in each version before restoring.
            </p>
            <p className="text-sm text-gray-700">
              ✅ <strong>Space Management:</strong> Delete old versions to save storage space (keep at least one backup version).
            </p>
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

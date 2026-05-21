import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Layout from '@/components/Layout'
import { PageHeader, PageSection, PageGrid, PageContainer } from '@/components/PageLayout'
import { Button } from '@/components/Button'
import { AlertCard, ActionCard } from '@/components/Cards'
import { Download, FileText, FileCode, Image as ImageIcon, Printer } from 'lucide-react'

interface ExportOption {
  format: string
  name: string
  description: string
  icon: React.ReactNode
  endpoint: string
  mimeType: string
}

interface Resume {
  id: number
  title: string
  full_name?: string
}

export default function ExportPage() {
  const router = useRouter()
  const { id } = router.query
  const [resume, setResume] = useState<Resume | null>(null)
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const exportOptions: ExportOption[] = [
    {
      format: 'pdf',
      name: 'PDF Document',
      description: 'Universal format, perfect for email and printing',
      icon: <FileText className="w-6 h-6" />,
      endpoint: `/api/v1x/resumes/${id}/export?format=pdf`,
      mimeType: 'application/pdf',
    },
    {
      format: 'docx',
      name: 'Microsoft Word',
      description: 'Editable document for future modifications',
      icon: <FileCode className="w-6 h-6" />,
      endpoint: `/api/v1x/resumes/${id}/export?format=docx`,
      mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    },
    {
      format: 'html',
      name: 'HTML File',
      description: 'Web-friendly format for online viewing',
      icon: <FileCode className="w-6 h-6" />,
      endpoint: `/api/v1x/resumes/${id}/export?format=html`,
      mimeType: 'text/html',
    },
    {
      format: 'png',
      name: 'PNG Image',
      description: 'Single image file, good for social media',
      icon: <ImageIcon className="w-6 h-6" />,
      endpoint: `/api/v1x/resumes/${id}/export?format=png`,
      mimeType: 'image/png',
    },
  ]

  useEffect(() => {
    if (id) {
      fetchResume()
    }
  }, [id])

  const fetchResume = async () => {
    try {
      setLoading(false)
      const res = await fetch(`/api/session/resumes/${id}`, {
        credentials: 'include',
      })
      if (res.ok) {
        const data = await res.json()
        setResume(data)
      }
    } catch (e) {
      console.error('Error fetching resume:', e)
      setError('Failed to load resume')
    }
  }

  const handleExport = async (option: ExportOption) => {
    try {
      setExporting(option.format)
      setError(null)

      const response = await fetch(option.endpoint, {
        credentials: 'include',
      })

      if (!response.ok) {
        throw new Error('Export failed')
      }

      // Create a blob from the response
      const blob = await response.blob()

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      // Set filename
      const filename = `${resume?.title || 'resume'}.${option.format}`
      link.setAttribute('download', filename)

      // Trigger download
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      // Show success
      alert(`Resume exported as ${option.format.toUpperCase()}`)
    } catch (e) {
      console.error('Error exporting resume:', e)
      setError(`Failed to export as ${option.format.toUpperCase()}`)
    } finally {
      setExporting(null)
    }
  }

  if (loading) {
    return (
      <Layout maxWidth="7xl">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <>
      <Head>
        <title>Export - {resume?.title || 'Resume'} - SkillForge</title>
      </Head>

      <Layout maxWidth="7xl">
        <PageHeader
          icon="📥"
          title="Export Resume"
          subtitle="Download your resume in multiple formats"
          breadcrumbs={[
            { label: 'Resumes', href: '/resumes' },
            { label: resume?.title || 'Resume', href: `/resumes/${id}` },
            { label: 'Export' },
          ]}
        />

        {error && (
          <div className="mb-8">
            <AlertCard
              variant="error"
              title="Export Error"
              message={error}
              action={
                <Button variant="secondary" size="sm" onClick={() => setError(null)}>
                  Dismiss
                </Button>
              }
            />
          </div>
        )}

        {/* Export Options */}
        <PageSection icon="💾" title="Choose Format">
          <PageGrid cols={2} gap="md">
            {exportOptions.map((option) => (
              <div
                key={option.format}
                className="bg-white rounded-lg border border-gray-200 p-6 hover:border-blue-300 hover:shadow-md transition"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="text-blue-600">{option.icon}</div>
                  <h3 className="font-semibold text-gray-900">{option.name}</h3>
                </div>
                <p className="text-sm text-gray-600 mb-4">{option.description}</p>
                <Button
                  onClick={() => handleExport(option)}
                  disabled={exporting === option.format}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
                >
                  {exporting === option.format ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2" />
                      Exporting...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 inline-block mr-2" />
                      Export as {option.format.toUpperCase()}
                    </>
                  )}
                </Button>
              </div>
            ))}
          </PageGrid>
        </PageSection>

        {/* Format Recommendations */}
        <PageSection icon="💡" title="Format Recommendations">
          <div className="space-y-4">
            <AlertCard
              variant="info"
              title="PDF"
              message="Best for: Email submissions, official applications, and ensuring consistent formatting across all devices."
            />
            <AlertCard
              variant="info"
              title="Microsoft Word (DOCX)"
              message="Best for: Customizing the resume further, making edits, or submitting to systems that request Word format."
            />
            <AlertCard
              variant="info"
              title="HTML"
              message="Best for: Creating an online portfolio, embedding on your website, or sharing interactive resumes."
            />
            <AlertCard
              variant="info"
              title="PNG Image"
              message="Best for: Sharing on social media, quick previews, or when recipients can't open other formats."
            />
          </div>
        </PageSection>

        {/* Tips */}
        <PageSection icon="🎯" title="Export Tips">
          <PageContainer variant="glass" className="space-y-3">
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold">1.</span>
              <p className="text-gray-700">Always export a PDF for official applications - it preserves all formatting.</p>
            </div>
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold">2.</span>
              <p className="text-gray-700">Export as Word if you need to customize the resume for specific companies.</p>
            </div>
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold">3.</span>
              <p className="text-gray-700">Check the file size and readability before submitting to online applications.</p>
            </div>
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold">4.</span>
              <p className="text-gray-700">Use consistent naming: "FirstName_LastName_Resume.pdf" is professional.</p>
            </div>
          </PageContainer>
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
            onClick={() => router.push(`/resumes/${id}/preview`)}
            variant="secondary"
          >
            Preview
          </Button>
        </div>
      </Layout>
    </>
  )
}

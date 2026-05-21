import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Layout from '@/components/Layout'
import { PageHeader, PageSection, PageGrid, PageContainer } from '@/components/PageLayout'
import { Button } from '@/components/Button'
import { AlertCard, FeatureCard } from '@/components/Cards'
import { Eye, Download, Star } from 'lucide-react'

interface ResumeTemplate {
  id: string
  name: string
  description: string
  category: string
  preview_image?: string
  features: string[]
  popularity?: number
  color_theme?: string
}

export default function TemplatesPage() {
  const router = useRouter()
  const { id } = router.query
  const [templates, setTemplates] = useState<ResumeTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [filter, setFilter] = useState('all')

  const categories = [
    { id: 'all', label: 'All Templates' },
    { id: 'modern', label: 'Modern' },
    { id: 'classic', label: 'Classic' },
    { id: 'creative', label: 'Creative' },
    { id: 'minimal', label: 'Minimal' },
  ]

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      setLoading(true)
      const res = await fetch('/api/v1x/resume-templates', {
        credentials: 'include',
      })

      if (res.ok) {
        const data = await res.json()
        setTemplates(data)
        if (data.length > 0) {
          setSelectedTemplate(data[0].id)
        }
      } else {
        setError('Failed to load templates')
        // Set default templates
        setTemplates([
          {
            id: 'modern',
            name: 'Modern',
            description: 'Clean, contemporary design with accent colors',
            category: 'modern',
            features: ['Accent colors', 'Icons', 'Two-column layout'],
          },
          {
            id: 'classic',
            name: 'Classic',
            description: 'Traditional format, ATS-friendly',
            category: 'classic',
            features: ['ATS-optimized', 'Single column', 'Minimal styling'],
          },
          {
            id: 'creative',
            name: 'Creative',
            description: 'Visual design with graphics and creative elements',
            category: 'creative',
            features: ['Graphics', 'Timeline', 'Color blocks'],
          },
          {
            id: 'minimal',
            name: 'Minimal',
            description: 'Simple, elegant, and distraction-free',
            category: 'minimal',
            features: ['Clean layout', 'Typography-focused', 'Whitespace'],
          },
          {
            id: 'executive',
            name: 'Executive',
            description: 'Professional layout for senior roles',
            category: 'modern',
            features: ['Executive summary', 'Key achievements', 'Premium fonts'],
          },
          {
            id: 'timeline',
            name: 'Timeline',
            description: 'Visual timeline design for easy scanning',
            category: 'creative',
            features: ['Timeline layout', 'Visual timeline', 'Dates highlighted'],
          },
        ])
      }
    } catch (e) {
      console.error('Error fetching templates:', e)
      setError('Error loading templates')
    } finally {
      setLoading(false)
    }
  }

  const applyTemplate = async (templateId: string) => {
    if (!id) return

    try {
      // Call dedicated apply-template endpoint
      const res = await fetch(`/api/session/resumes?id=${id}&action=apply-template&template=${templateId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      })

      if (res.ok) {
        const updated = await res.json()
        alert('Template applied successfully!')
        router.push(`/resumes/${id}/edit`)
      } else {
        const error = await res.json().catch(() => ({}))
        setError(`Failed to apply template: ${error.detail || 'Unknown error'}`)
      }
    } catch (e) {
      console.error('Error applying template:', e)
      setError('Error applying template')
    }
  }

  const filteredTemplates =
    filter === 'all' ? templates : templates.filter((t) => t.category === filter)

  if (loading) {
    return (
      <Layout maxWidth="7xl">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Loading templates...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <>
      <Head>
        <title>Resume Templates - SkillForge</title>
      </Head>

      <Layout maxWidth="7xl">
        <PageHeader
          icon="🎨"
          title="Resume Templates"
          subtitle="Choose from professionally designed templates for your resume"
          breadcrumbs={[
            { label: 'Resumes', href: '/resumes' },
            { label: id ? 'Templates' : 'New Resume' },
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

        {/* Category Filter */}
        <PageSection icon="🏷️" title="Filter by Category">
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setFilter(category.id)}
                className={`px-4 py-2 rounded-full font-medium transition ${
                  filter === category.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category.label}
              </button>
            ))}
          </div>
        </PageSection>

        {/* Template Grid */}
        <PageSection
          icon="📋"
          title={`${filteredTemplates.length} Templates Available`}
        >
          <PageGrid cols={3} gap="md">
            {filteredTemplates.map((template) => (
              <div
                key={template.id}
                className={`rounded-lg border-2 overflow-hidden transition cursor-pointer hover:shadow-lg ${
                  selectedTemplate === template.id
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
                onClick={() => setSelectedTemplate(template.id)}
              >
                {/* Preview Image */}
                {template.preview_image ? (
                  <img
                    src={template.preview_image}
                    alt={template.name}
                    className="w-full h-48 object-cover"
                  />
                ) : (
                  <div className="w-full h-48 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                    <FileText className="w-12 h-12 text-gray-400" />
                  </div>
                )}

                {/* Template Info */}
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{template.name}</h3>
                    {template.popularity && (
                      <div className="flex items-center gap-1 text-sm text-yellow-600">
                        <Star className="w-4 h-4 fill-current" />
                        {template.popularity}
                      </div>
                    )}
                  </div>

                  <p className="text-sm text-gray-600 mb-3">{template.description}</p>

                  {/* Features */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {template.features?.slice(0, 2).map((feature) => (
                      <span
                        key={feature}
                        className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                      >
                        {feature}
                      </span>
                    ))}
                    {(template.features?.length || 0) > 2 && (
                      <span className="text-xs text-gray-500 px-2 py-1">
                        +{(template.features?.length || 0) - 2}
                      </span>
                    )}
                  </div>

                  {/* Actions */}
                  {id ? (
                    <Button
                      onClick={() => applyTemplate(template.id)}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm"
                      size="sm"
                    >
                      Apply to Resume
                    </Button>
                  ) : (
                    <Button
                      onClick={() => router.push(`/resumes/new?template=${template.id}`)}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm"
                      size="sm"
                    >
                      Create with This
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </PageGrid>
        </PageSection>

        {/* Template Details */}
        {selectedTemplate && (
          <PageSection icon="📄" title="Template Details">
            {(() => {
              const template = templates.find((t) => t.id === selectedTemplate)
              return (
                template && (
                  <PageContainer variant="glass" className="space-y-4">
                    <div>
                      <p className="font-semibold text-gray-900 mb-2">{template.name}</p>
                      <p className="text-gray-700">{template.description}</p>
                    </div>

                    {template.features && template.features.length > 0 && (
                      <div>
                        <p className="font-semibold text-gray-900 mb-2">Features:</p>
                        <ul className="space-y-1">
                          {template.features.map((feature) => (
                            <li key={feature} className="text-sm text-gray-700 flex items-center gap-2">
                              <span className="text-blue-600">✓</span> {feature}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {template.category && (
                      <div>
                        <p className="text-sm text-gray-600">
                          <strong>Category:</strong> {template.category}
                        </p>
                      </div>
                    )}
                  </PageContainer>
                )
              )
            })()}
          </PageSection>
        )}

        {/* Tips */}
        <PageSection icon="💡" title="Template Tips">
          <div className="space-y-3 bg-blue-50 rounded-lg p-6">
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold flex-shrink-0">1.</span>
              <p className="text-gray-700 text-sm">
                <strong>Modern templates</strong> work best for tech and creative roles.
              </p>
            </div>
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold flex-shrink-0">2.</span>
              <p className="text-gray-700 text-sm">
                <strong>Classic templates</strong> are ATS-friendly and great for traditional industries.
              </p>
            </div>
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold flex-shrink-0">3.</span>
              <p className="text-gray-700 text-sm">
                <strong>Creative templates</strong> showcase personality for design, marketing, and creative roles.
              </p>
            </div>
            <div className="flex gap-3">
              <span className="text-blue-600 font-bold flex-shrink-0">4.</span>
              <p className="text-gray-700 text-sm">
                You can change templates anytime - your content stays the same!
              </p>
            </div>
          </div>
        </PageSection>

        {/* Back Button */}
        <div className="flex gap-3 mt-8">
          {id ? (
            <>
              <Button
                onClick={() => router.push(`/resumes/${id}/edit`)}
                className="bg-gray-600 hover:bg-gray-700 text-white"
              >
                Back to Edit
              </Button>
            </>
          ) : (
            <>
              <Button
                onClick={() => router.push('/resumes')}
                variant="secondary"
              >
                Back to Resumes
              </Button>
            </>
          )}
        </div>
      </Layout>
    </>
  )
}

// Import lucide icon
import { FileText } from 'lucide-react'

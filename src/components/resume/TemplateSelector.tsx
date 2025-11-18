import { useState, useEffect, useMemo, useCallback } from 'react'
import { Button } from '@/components/Button'
import ResumePreview from './ResumePreview'

interface Template {
  id: number
  name: string
  description: string
  category: string
  thumbnail_url: string | null
  config: {
    layout?: string
    font?: string
    font_family?: string
    accent?: string
    accent_color?: string
    picture?: string
    picture_style?: string
    icons?: boolean
    show_icons?: boolean
    color_theme?: string
  }
  is_ats_friendly: boolean
  popularity: number
  is_active: boolean
}

interface TemplateSelectorProps {
  currentTemplate?: number
  onSelect: (template: Template) => void
  onClose: () => void
  resumeData?: any // Pass current resume data for live preview
}

export default function TemplateSelector({ currentTemplate, onSelect, onClose, resumeData }: TemplateSelectorProps) {
  const [templates, setTemplates] = useState<Template[]>([])
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([])
  const [categories, setCategories] = useState<string[]>(['All'])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Fallback curated templates (trending styles)
  const FALLBACK_TEMPLATES: Template[] = [
    {
      id: 1001,
      name: 'Modern ATS',
      description: 'Clean, recruiter-friendly layout optimized for ATS parsing',
      category: 'Modern',
      thumbnail_url: null,
      config: { layout: 'modern', font: 'Inter', accent: '#2563eb', icons: true, picture: 'none', color_theme: 'light' },
      is_ats_friendly: true,
      popularity: 96,
      is_active: true,
    },
    {
      id: 1002,
      name: 'Minimal Swiss',
      description: 'Elegant whitespace, tight typography, Swiss-inspired minimalism',
      category: 'Minimal',
      thumbnail_url: null,
      config: { layout: 'minimal', font: 'Inter', accent: '#0ea5e9', icons: false, picture: 'none', color_theme: 'light' },
      is_ats_friendly: true,
      popularity: 92,
      is_active: true,
    },
    {
      id: 1003,
      name: 'Executive Two-Column',
      description: 'Polished two-column layout for senior and leadership roles',
      category: 'Executive',
      thumbnail_url: null,
      config: { layout: 'executive-two', font: 'Georgia', accent: '#111827', icons: false, picture: 'none', color_theme: 'neutral' },
      is_ats_friendly: true,
      popularity: 89,
      is_active: true,
    },
    {
      id: 1004,
      name: 'Creative Gradient',
      description: 'Bold gradient header and expressive accent elements',
      category: 'Creative',
      thumbnail_url: null,
      config: { layout: 'creative', font: 'Poppins', accent: '#8b5cf6', icons: true, picture: 'circle', color_theme: 'vibrant' },
      is_ats_friendly: false,
      popularity: 84,
      is_active: true,
    },
    {
      id: 1005,
      name: 'Tech Neon',
      description: 'Modern tech aesthetic with subtle neon accents',
      category: 'Tech',
      thumbnail_url: null,
      config: { layout: 'tech-two', font: 'Inter', accent: '#22d3ee', icons: true, picture: 'rounded', color_theme: 'dark' },
      is_ats_friendly: true,
      popularity: 87,
      is_active: true,
    },
    {
      id: 1008,
      name: 'Timeline Progress',
      description: 'Vertical timeline emphasizing chronological career growth',
      category: 'Timeline',
      thumbnail_url: null,
      config: { layout: 'timeline', font: 'Inter', accent: '#0ea5e9', icons: false, picture: 'none', color_theme: 'light' },
      is_ats_friendly: true,
      popularity: 77,
      is_active: true,
    },
    {
      id: 1009,
      name: 'Elegant Blue',
      description: 'Refined blue header with balanced information density',
      category: 'Classic',
      thumbnail_url: null,
      config: { layout: 'elegant-blue', font: 'Georgia', accent: '#1e3a8a', icons: false, picture: 'none', color_theme: 'classic' },
      is_ats_friendly: true,
      popularity: 80,
      is_active: true,
    },
    {
      id: 1006,
      name: 'Academic Serif',
      description: 'Research-oriented structure with serif typography',
      category: 'Academic',
      thumbnail_url: null,
      config: { layout: 'academic-two', font: 'Georgia', accent: '#334155', icons: false, picture: 'none', color_theme: 'classic' },
      is_ats_friendly: true,
      popularity: 81,
      is_active: true,
    },
    {
      id: 1007,
      name: 'Elegant Classic',
      description: 'Timeless single-column with accent underline headers',
      category: 'Classic',
      thumbnail_url: null,
      config: { layout: 'classic', font: 'Georgia', accent: '#475569', icons: false, picture: 'none', color_theme: 'classic' },
      is_ats_friendly: true,
      popularity: 78,
      is_active: true,
    },
  ]
  
  // Filters
  const [selectedCategory, setSelectedCategory] = useState<string>('All')
  const [atsOnly, setAtsOnly] = useState(false)
  const [sortBy, setSortBy] = useState<'popularity' | 'name'>('popularity')
  
  // Preview
  const [previewTemplate, setPreviewTemplate] = useState<Template | null>(null)

  const fetchTemplates = useCallback(async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/session/v1x/resume-templates')
      
      if (!response.ok) throw new Error('Failed to fetch templates')
      const data = await response.json()
      if (Array.isArray(data) && data.length > 0) {
        setTemplates(data)
      } else {
        // Use curated fallback when API returns no templates
        setTemplates(FALLBACK_TEMPLATES)
      }
      setError(null)
    } catch (err) {
      console.error('Error fetching templates:', err)
      // Provide graceful fallback templates when API unavailable
      setTemplates(FALLBACK_TEMPLATES)
      setError(null)
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchCategories = useCallback(async () => {
    try {
      const response = await fetch('/api/session/v1x/resume-templates/categories')
      const data = await response.json()
      setCategories(['All', ...data.categories])
    } catch (err) {
      console.error('Error fetching categories:', err)
    }
  }, [])

  // Memoize filtered templates to avoid unnecessary recalculations
  const filteredTemplatesMemo = useMemo(() => {
    let filtered = [...templates]

    if (selectedCategory !== 'All') {
      filtered = filtered.filter(t => t.category === selectedCategory)
    }

    if (atsOnly) {
      filtered = filtered.filter(t => t.is_ats_friendly)
    }

    filtered.sort((a, b) => {
      if (sortBy === 'popularity') return b.popularity - a.popularity
      return a.name.localeCompare(b.name)
    })

    return filtered
  }, [templates, selectedCategory, atsOnly, sortBy])

  useEffect(() => {
    fetchTemplates()
    fetchCategories()
  }, [fetchTemplates, fetchCategories])

  // Update filteredTemplates when memoized value changes
  useEffect(() => {
    setFilteredTemplates(filteredTemplatesMemo)
  }, [filteredTemplatesMemo])

  const handleTemplateSelect = useCallback(async (template: Template) => {
    try {
      await fetch(`/api/session/v1x/resume-templates/${template.id}/popularity`, {
        method: 'POST',
      })
    } catch (err) {
      console.error('Failed to track popularity:', err)
    }

    onSelect(template)
  }, [onSelect])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="w-full max-w-7xl bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-2xl p-8 my-8 border border-gray-200">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h3 className="text-3xl font-extrabold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
              Choose Your Perfect Template
            </h3>
            <p className="text-sm text-gray-600 flex items-center gap-2">
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {filteredTemplates.length} templates
              </span>
              Professional designs ready to use
            </p>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full p-2 transition-all"
            aria-label="Close"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Filters */}
        {!loading && !error && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              {/* ATS Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filter
                </label>
                <label className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={atsOnly}
                    onChange={(e) => setAtsOnly(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded"
                  />
                  <span className="text-sm text-gray-700">ATS-Friendly Only</span>
                </label>
              </div>

              {/* Sort */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sort By
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'popularity' | 'name')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="popularity">Most Popular</option>
                  <option value="name">Name (A-Z)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Loading State with Skeleton */}
        {loading && (
          <div className="mb-6 max-h-[65vh] overflow-y-auto pr-1">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {[...Array(8)].map((_, idx) => (
                <div key={idx} className="p-3 border-2 border-gray-200 rounded-lg animate-pulse">
                  <div className="aspect-[3/4] bg-gradient-to-br from-gray-200 to-gray-300 rounded-md mb-3"></div>
                  <div className="h-4 bg-gray-200 rounded mb-2 w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded mb-2"></div>
                  <div className="flex justify-between">
                    <div className="h-3 bg-gray-200 rounded w-12"></div>
                    <div className="h-3 bg-gray-200 rounded w-16"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchTemplates} variant="primary">Retry</Button>
          </div>
        )}

        {/* Templates Grid */}
        {!loading && !error && (
          <div className="mb-6 max-h-[65vh] overflow-y-auto pr-1">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredTemplates.map((template) => (
              <button
                key={template.id}
                onClick={() => handleTemplateSelect(template)}
                className={`text-left p-3 border-2 rounded-lg hover:shadow-lg transition-all ${
                  currentTemplate === template.id
                    ? 'border-blue-600 ring-2 ring-blue-200 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-400'
                }`}
              >
                {/* Thumbnail */}
                <div className="aspect-[3/4] bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-md mb-3 relative overflow-hidden">
                  {template.thumbnail_url && (
                    <img
                      src={template.thumbnail_url}
                      alt={template.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none'
                      }}
                    />
                  )}
                  
                  {/* Template Name Overlay (shown when no image or image fails) */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-white p-3">
                    <div className="bg-black/30 backdrop-blur-sm rounded-lg px-3 py-2 text-center w-full">
                      <div className="text-sm font-bold mb-0.5 truncate">{template.name}</div>
                      <div className="text-xs opacity-90">{template.category}</div>
                    </div>
                  </div>
                  
                  {/* Preview Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setPreviewTemplate(template)
                    }}
                    className="absolute top-2 right-2 p-1.5 bg-white/90 hover:bg-white rounded-full shadow-sm"
                    title="Preview"
                  >
                    <svg className="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>

                  {/* Badges */}
                  <div className="absolute bottom-2 left-2 flex gap-1">
                    {template.is_ats_friendly && (
                      <span className="px-2 py-0.5 bg-green-500 text-white text-xs font-medium rounded">
                        ATS
                      </span>
                    )}
                    {currentTemplate === template.id && (
                      <span className="px-2 py-0.5 bg-blue-600 text-white text-xs font-medium rounded">
                        Selected
                      </span>
                    )}
                  </div>
                </div>

                {/* Info */}
                <div className="font-semibold text-gray-900 text-sm mb-1">{template.name}</div>
                <div className="text-xs text-gray-600 mb-2 line-clamp-2">{template.description}</div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500 flex items-center">
                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    {template.popularity}
                  </span>
                  <span className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                    {template.category}
                  </span>
                </div>
              </button>
            ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && filteredTemplates.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg mb-2">No templates found</p>
            <p className="text-gray-500 text-sm">Try adjusting your filters</p>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end border-t border-gray-200 pt-4">
          <Button onClick={onClose} variant="secondary">Close</Button>
        </div>

        {/* Preview Modal */}
        {previewTemplate && (
          <div
            className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
            onClick={() => setPreviewTemplate(null)}
          >
            <div
              className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Preview Header */}
              <div className="flex items-center justify-between p-6 border-b">
                <div>
                  <h4 className="text-xl font-bold text-gray-900">{previewTemplate.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">{previewTemplate.description}</p>
                </div>
                <button
                  onClick={() => setPreviewTemplate(null)}
                  className="text-gray-500 hover:text-gray-700 text-xl"
                >
                  ✕
                </button>
              </div>

              {/* Live Resume Preview with Template */}
              <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)] flex flex-col md:flex-row gap-8">
                <div className="flex-1 min-w-[320px] max-w-[500px] mx-auto">
                  {resumeData ? (
                    <div className="transform scale-90 origin-top">
                      <ResumePreview resume={{
                        ...resumeData,
                        template: previewTemplate.id.toString(),
                        font_family: (previewTemplate.config as any).font_family || (previewTemplate.config as any).font || resumeData.font_family,
                        layout: (previewTemplate.config as any).layout || resumeData.layout,
                        accent_color: (previewTemplate.config as any).accent_color || (previewTemplate.config as any).accent || resumeData.accent_color,
                        picture_style: (previewTemplate.config as any).picture_style || (previewTemplate.config as any).picture || resumeData.picture_style,
                        show_icons: (previewTemplate.config as any).show_icons !== undefined ? (previewTemplate.config as any).show_icons : ((previewTemplate.config as any).icons !== undefined ? (previewTemplate.config as any).icons : resumeData.show_icons),
                        color_theme: (previewTemplate.config as any).color_theme || resumeData.color_theme,
                        background_type: (previewTemplate.config as any).background_type || resumeData.background_type,
                        section_divider: (previewTemplate.config as any).section_divider || resumeData.section_divider,
                        header_shape: (previewTemplate.config as any).header_shape || resumeData.header_shape,
                        icon_style: (previewTemplate.config as any).icon_style || resumeData.icon_style,
                      }} />
                    </div>
                  ) : (
                    <div className="aspect-[3/4] bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">
                      <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-[220px] space-y-6">
                  <div>
                    <h5 className="text-xs font-black uppercase tracking-wider text-gray-500 mb-3">Template Details</h5>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h6 className="text-xs font-medium text-gray-600 mb-1">Category</h6>
                        <p className="text-sm text-gray-900 font-semibold">{previewTemplate.category}</p>
                      </div>
                      <div>
                        <h6 className="text-xs font-medium text-gray-600 mb-1">Layout</h6>
                        <p className="text-sm text-gray-900 font-semibold capitalize">{previewTemplate.config.layout}</p>
                      </div>
                      <div>
                        <h6 className="text-xs font-medium text-gray-600 mb-1">Font</h6>
                        <p className="text-sm text-gray-900 font-semibold">{previewTemplate.config.font}</p>
                      </div>
                      <div>
                        <h6 className="text-xs font-medium text-gray-600 mb-1">ATS-Friendly</h6>
                        <p className={`text-sm font-semibold ${previewTemplate.is_ats_friendly ? 'text-green-600' : 'text-gray-500'}`}>
                          {previewTemplate.is_ats_friendly ? '✓ Yes' : 'No'}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h6 className="text-xs font-medium text-gray-600 mb-2">Accent Color</h6>
                    <div className="flex items-center space-x-3">
                      <div
                        className="w-12 h-12 rounded-lg border-2 shadow-sm"
                        style={{ backgroundColor: previewTemplate.config.accent }}
                      ></div>
                      <span className="text-xs font-mono text-gray-700 font-semibold">{previewTemplate.config.accent}</span>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-gray-200">
                    <p className="text-xs text-gray-600 leading-relaxed">
                      {previewTemplate.description}
                    </p>
                  </div>
                </div>
              </div>

              {/* Preview Footer */}
              <div className="flex items-center justify-end gap-3 p-4 border-t bg-gray-50">
                <Button onClick={() => setPreviewTemplate(null)} variant="secondary">
                  Close
                </Button>
                <Button
                  onClick={() => {
                    handleTemplateSelect(previewTemplate)
                    setPreviewTemplate(null)
                  }}
                  variant="primary"
                >
                  Use This Template
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

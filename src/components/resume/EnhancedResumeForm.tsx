/**
 * Enhanced Resume Form with Extra Content & Skills Field
 * Integrated with Style Settings tracking
 */

import React, { useState, useEffect } from 'react'
import { ChevronDown, Plus, Trash2, Settings, RotateCcw } from 'lucide-react'

interface ResumeFormProps {
  resumeId: number
  initialData?: any
  onSave: (data: any) => Promise<void>
  onStyleUpdate?: (styles: any) => Promise<void>
}

export const EnhancedResumeForm: React.FC<ResumeFormProps> = ({
  resumeId,
  initialData,
  onSave,
  onStyleUpdate
}) => {
  const [formData, setFormData] = useState(initialData || {})
  const [expandedSections, setExpandedSections] = useState<string[]>([])
  const [showStyleSettings, setShowStyleSettings] = useState(false)
  const [styleSettings, setStyleSettings] = useState(initialData?.styleSettings || {})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  // Toggle section expansion
  const toggleSection = (section: string) => {
    setExpandedSections(prev =>
      prev.includes(section)
        ? prev.filter(s => s !== section)
        : [...prev, section]
    )
  }

  // Update form data
  const updateField = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // Update style setting
  const updateStyleSetting = (field: string, value: any) => {
    setStyleSettings(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // Save resume data
  const handleSaveResume = async () => {
    try {
      setLoading(true)
      setError(null)
      
      await onSave(formData)
      
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save')
    } finally {
      setLoading(false)
    }
  }

  // Save style settings
  const handleSaveStyles = async () => {
    try {
      setLoading(true)
      setError(null)
      
      if (onStyleUpdate) {
        await onStyleUpdate(styleSettings)
      }
      
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save styles')
    } finally {
      setLoading(false)
    }
  }

  // Reset styles to defaults
  const handleResetStyles = async () => {
    if (!confirm('Reset all styles to defaults?')) return
    
    setStyleSettings({
      font_family: 'Roboto',
      color_theme: 'blue',
      picture_style: 'circle',
      layout: 'single-column',
      accent_color: '#2563eb',
      text_color: '#000000',
      heading_color: '#1f2937',
      line_spacing: 1.2,
      font_size: 11,
      heading_size: 14,
      show_icons: true,
      background_type: 'none'
    })
    
    handleSaveStyles()
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Resume Editor</h1>
        <button
          onClick={() => setShowStyleSettings(!showStyleSettings)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Settings size={20} />
          Style Settings
        </button>
      </div>

      {/* Status Messages */}
      {error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}
      
      {success && (
        <div className="p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
          ✅ Changes saved successfully!
        </div>
      )}

      {/* Style Settings Panel */}
      {showStyleSettings && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6 space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Style Settings</h2>
            <button
              onClick={handleResetStyles}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-white border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition"
            >
              <RotateCcw size={16} />
              Reset to Defaults
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Typography Settings */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-800">Typography</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Font Family
                </label>
                <select
                  value={styleSettings.font_family || 'Roboto'}
                  onChange={(e) => updateStyleSetting('font_family', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Roboto">Roboto</option>
                  <option value="Open Sans">Open Sans</option>
                  <option value="Lato">Lato</option>
                  <option value="Montserrat">Montserrat</option>
                  <option value="Inter">Inter</option>
                  <option value="Poppins">Poppins</option>
                  <option value="Georgia">Georgia (Serif)</option>
                  <option value="Garamond">Garamond (Serif)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Body Font Size: {styleSettings.font_size || 11}pt
                </label>
                <input
                  type="range"
                  min="8"
                  max="16"
                  step="1"
                  value={styleSettings.font_size || 11}
                  onChange={(e) => updateStyleSetting('font_size', parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Heading Font Size: {styleSettings.heading_size || 14}pt
                </label>
                <input
                  type="range"
                  min="9"
                  max="24"
                  step="1"
                  value={styleSettings.heading_size || 14}
                  onChange={(e) => updateStyleSetting('heading_size', parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Line Spacing: {(styleSettings.line_spacing || 1.2).toFixed(1)}
                </label>
                <input
                  type="range"
                  min="1.0"
                  max="2.0"
                  step="0.1"
                  value={styleSettings.line_spacing || 1.2}
                  onChange={(e) => updateStyleSetting('line_spacing', parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>

            {/* Color Settings */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-800">Colors</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Accent Color
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={styleSettings.accent_color || '#2563eb'}
                    onChange={(e) => updateStyleSetting('accent_color', e.target.value)}
                    className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={styleSettings.accent_color || '#2563eb'}
                    onChange={(e) => updateStyleSetting('accent_color', e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="#2563eb"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Text Color
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={styleSettings.text_color || '#000000'}
                    onChange={(e) => updateStyleSetting('text_color', e.target.value)}
                    className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={styleSettings.text_color || '#000000'}
                    onChange={(e) => updateStyleSetting('text_color', e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="#000000"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Heading Color
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={styleSettings.heading_color || '#1f2937'}
                    onChange={(e) => updateStyleSetting('heading_color', e.target.value)}
                    className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={styleSettings.heading_color || '#1f2937'}
                    onChange={(e) => updateStyleSetting('heading_color', e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="#1f2937"
                  />
                </div>
              </div>
            </div>

            {/* Layout Settings */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-800">Layout</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Layout Type
                </label>
                <select
                  value={styleSettings.layout || 'single-column'}
                  onChange={(e) => updateStyleSetting('layout', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="single-column">Single Column</option>
                  <option value="two-column">Two Column</option>
                  <option value="sidebar">Sidebar</option>
                  <option value="centered">Centered</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Picture Style
                </label>
                <select
                  value={styleSettings.picture_style || 'circle'}
                  onChange={(e) => updateStyleSetting('picture_style', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="circle">Circle</option>
                  <option value="square">Square</option>
                  <option value="rounded">Rounded</option>
                  <option value="none">None</option>
                </select>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="show_icons"
                  checked={styleSettings.show_icons !== false}
                  onChange={(e) => updateStyleSetting('show_icons', e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="show_icons" className="text-sm font-medium text-gray-700">
                  Show Icons
                </label>
              </div>
            </div>
          </div>

          <div className="flex gap-3 justify-end">
            <button
              onClick={() => setShowStyleSettings(false)}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
            >
              Close
            </button>
            <button
              onClick={handleSaveStyles}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save Styles'}
            </button>
          </div>
        </div>
      )}

      {/* Main Form Sections */}
      <div className="space-y-4">
        {/* Extra Content Section */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('extra-content')}
            className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between font-semibold text-gray-900 transition"
          >
            <span>📝 Additional Content</span>
            <ChevronDown
              size={20}
              className={`transform transition ${expandedSections.includes('extra-content') ? 'rotate-180' : ''}`}
            />
          </button>
          
          {expandedSections.includes('extra-content') && (
            <div className="p-4 space-y-4">
              <p className="text-sm text-gray-600">
                Add any additional content such as languages, volunteer work, publications, or other information not covered by standard sections.
              </p>
              <textarea
                value={formData.extra_content || ''}
                onChange={(e) => updateField('extra_content', e.target.value)}
                placeholder="Add extra content here... (languages, volunteer work, publications, awards, etc.)"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[120px] font-mono text-sm"
              />
              <p className="text-xs text-gray-500">
                Tip: Organize your content with headers like "Languages:", "Volunteer Work:", "Publications:" for better readability
              </p>
            </div>
          )}
        </div>

        {/* Skills Section */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('skills')}
            className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between font-semibold text-gray-900 transition"
          >
            <span>🎯 Skills</span>
            <ChevronDown
              size={20}
              className={`transform transition ${expandedSections.includes('skills') ? 'rotate-180' : ''}`}
            />
          </button>
          
          {expandedSections.includes('skills') && (
            <div className="p-4 space-y-4">
              <p className="text-sm text-gray-600">
                Manage your professional skills and competencies.
              </p>
              
              {/* Skills will be managed via the main skills component */}
              <p className="text-sm text-blue-600 italic">
                Skills are managed in the Skills section of the resume editor.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Save Button */}
      <div className="flex gap-3 justify-end">
        <button
          onClick={() => window.history.back()}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
        >
          Cancel
        </button>
        <button
          onClick={handleSaveResume}
          disabled={loading}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 font-medium"
        >
          {loading ? 'Saving Resume...' : 'Save Resume'}
        </button>
      </div>
    </div>
  )
}

export default EnhancedResumeForm

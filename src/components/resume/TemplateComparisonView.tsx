import { useState } from 'react'
import { X, Check, ArrowLeftRight } from 'lucide-react'
import ResumePreview from './ResumePreview'
import { Button } from '../Button'

interface TemplateComparisonViewProps {
  isOpen: boolean
  onClose: () => void
  currentTemplate: any
  compareTemplate: any
  resumeData: any
  onSelect: (template: any) => void
}

export default function TemplateComparisonView({
  isOpen,
  onClose,
  currentTemplate,
  compareTemplate,
  resumeData,
  onSelect
}: TemplateComparisonViewProps) {
  const [selectedSide, setSelectedSide] = useState<'current' | 'compare'>('compare')

  if (!isOpen) return null

  const applyTemplateConfig = (template: any) => ({
    ...resumeData,
    template: template.id.toString(),
    font_family: template.config.font_family || template.config.font || resumeData.font_family,
    layout: template.config.layout || resumeData.layout,
    accent_color: template.config.accent_color || template.config.accent || resumeData.accent_color,
    picture_style: template.config.picture_style || template.config.picture || resumeData.picture_style,
    show_icons: template.config.show_icons !== undefined ? template.config.show_icons : 
                (template.config.icons !== undefined ? template.config.icons : resumeData.show_icons),
    color_theme: template.config.color_theme || resumeData.color_theme,
  })

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-md"
      onClick={onClose}
    >
      <div
        className="bg-gradient-to-br from-deepTech to-deepTech/95 rounded-2xl shadow-2xl border border-white/20 max-w-7xl w-full mx-4 h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-forgePurple to-neuralBlue rounded-lg">
              <ArrowLeftRight className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-black text-white">Template Comparison</h3>
              <p className="text-xs text-white/60 mt-0.5">Compare side-by-side before switching</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-all text-white/70 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Comparison Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-2 gap-6 h-full">
            {/* Current Template */}
            <div className="flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="text-lg font-bold text-white flex items-center gap-2">
                    {currentTemplate.name}
                    <span className="px-2 py-0.5 bg-blue-500/20 border border-blue-500/30 rounded text-xs text-blue-200">
                      Current
                    </span>
                  </h4>
                  <p className="text-xs text-white/60 mt-1">{currentTemplate.description}</p>
                </div>
                <button
                  onClick={() => setSelectedSide('current')}
                  className={`p-2 rounded-lg transition-all ${
                    selectedSide === 'current' 
                      ? 'bg-blue-500/30 text-blue-200 ring-2 ring-blue-500/50' 
                      : 'bg-white/5 text-white/40 hover:bg-white/10'
                  }`}
                >
                  <Check className="w-5 h-5" />
                </button>
              </div>
              
              <div className="flex-1 bg-white/5 rounded-xl p-4 border border-white/10 overflow-auto">
                <div className="transform scale-75 origin-top">
                  <div className="bg-white rounded-lg shadow-2xl">
                    <ResumePreview resume={applyTemplateConfig(currentTemplate)} />
                  </div>
                </div>
              </div>

              {/* Template Info */}
              <div className="mt-4 p-4 bg-white/5 rounded-lg border border-white/10 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-white/60">Category</span>
                  <span className="text-white font-medium">{currentTemplate.category}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-white/60">ATS Friendly</span>
                  <span className={currentTemplate.is_ats_friendly ? 'text-green-400' : 'text-yellow-400'}>
                    {currentTemplate.is_ats_friendly ? '✓ Yes' : '⚠ No'}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-white/60">Font</span>
                  <span className="text-white font-medium">{currentTemplate.config.font || 'Inter'}</span>
                </div>
                <div className="flex justify-between text-xs items-center">
                  <span className="text-white/60">Accent Color</span>
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-4 h-4 rounded border border-white/20"
                      style={{ backgroundColor: currentTemplate.config.accent }}
                    />
                    <span className="text-white font-mono text-[10px]">{currentTemplate.config.accent}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Compare Template */}
            <div className="flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="text-lg font-bold text-white flex items-center gap-2">
                    {compareTemplate.name}
                    <span className="px-2 py-0.5 bg-purple-500/20 border border-purple-500/30 rounded text-xs text-purple-200">
                      Preview
                    </span>
                  </h4>
                  <p className="text-xs text-white/60 mt-1">{compareTemplate.description}</p>
                </div>
                <button
                  onClick={() => setSelectedSide('compare')}
                  className={`p-2 rounded-lg transition-all ${
                    selectedSide === 'compare' 
                      ? 'bg-purple-500/30 text-purple-200 ring-2 ring-purple-500/50' 
                      : 'bg-white/5 text-white/40 hover:bg-white/10'
                  }`}
                >
                  <Check className="w-5 h-5" />
                </button>
              </div>
              
              <div className="flex-1 bg-white/5 rounded-xl p-4 border border-white/10 overflow-auto">
                <div className="transform scale-75 origin-top">
                  <div className="bg-white rounded-lg shadow-2xl">
                    <ResumePreview resume={applyTemplateConfig(compareTemplate)} />
                  </div>
                </div>
              </div>

              {/* Template Info */}
              <div className="mt-4 p-4 bg-white/5 rounded-lg border border-white/10 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-white/60">Category</span>
                  <span className="text-white font-medium">{compareTemplate.category}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-white/60">ATS Friendly</span>
                  <span className={compareTemplate.is_ats_friendly ? 'text-green-400' : 'text-yellow-400'}>
                    {compareTemplate.is_ats_friendly ? '✓ Yes' : '⚠ No'}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-white/60">Font</span>
                  <span className="text-white font-medium">{compareTemplate.config.font || 'Inter'}</span>
                </div>
                <div className="flex justify-between text-xs items-center">
                  <span className="text-white/60">Accent Color</span>
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-4 h-4 rounded border border-white/20"
                      style={{ backgroundColor: compareTemplate.config.accent }}
                    />
                    <span className="text-white font-mono text-[10px]">{compareTemplate.config.accent}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t border-white/10 bg-white/5 flex items-center justify-between">
          <div className="text-sm text-white/60">
            Selected: <span className="text-white font-medium">
              {selectedSide === 'current' ? currentTemplate.name : compareTemplate.name}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={onClose} variant="secondary">
              Cancel
            </Button>
            <Button
              onClick={() => {
                const selected = selectedSide === 'current' ? currentTemplate : compareTemplate
                onSelect(selected)
                onClose()
              }}
              variant="primary"
              className="font-bold"
            >
              {selectedSide === 'current' ? 'Keep Current' : 'Switch Template'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

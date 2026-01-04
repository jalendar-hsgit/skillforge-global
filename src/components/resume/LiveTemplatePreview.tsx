import { useState, useEffect, useRef } from 'react'
import { Eye, EyeOff, Maximize2, Minimize2, RotateCcw, ZoomIn, ZoomOut } from 'lucide-react'
import ResumePreview from './ResumePreview'
import useResizeObserver from '@/hooks/useResizeObserver'
import useAutoScale from '@/hooks/useAutoScale'

interface LiveTemplatePreviewProps {
  resume: any
  isVisible?: boolean
  onToggle?: () => void
  className?: string
}

export default function LiveTemplatePreview({ 
  resume, 
  isVisible = true, 
  onToggle,
  className = '' 
}: LiveTemplatePreviewProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [scale, setScale] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('resume-preview-zoom')
      return saved ? parseFloat(saved) : 0.72
    }
    return 0.72
  })
  // detect whether user explicitly set a zoom
  const [hasManualZoom] = useState(() => {
    if (typeof window === 'undefined') return false
    return !!localStorage.getItem('resume-preview-zoom')
  })
  const [isAnimating, setIsAnimating] = useState(false)
  const previewRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const containerWidth = useResizeObserver(containerRef)
  const autoScale = useAutoScale(containerWidth, { targetWidth: 794, min: 0.45, max: 1 })

  // Trigger subtle animation when resume data changes
  useEffect(() => {
    if (!resume) return
    
    setIsAnimating(true)
    const timer = setTimeout(() => setIsAnimating(false), 300)
    return () => clearTimeout(timer)
  }, [
    resume?.full_name,
    resume?.professional_summary,
    resume?.work_experiences,
    resume?.education,
    resume?.skills,
    resume?.projects,
    resume?.template,
    resume?.accent_color,
    resume?.font_family
  ])

  const handleZoomIn = () => {
    setScale(prev => {
      const newScale = Math.min(prev + 0.1, 1.2)
      localStorage.setItem('resume-preview-zoom', newScale.toString())
      return newScale
    })
  }

  const handleZoomOut = () => {
    setScale(prev => {
      const newScale = Math.max(prev - 0.1, 0.4)
      localStorage.setItem('resume-preview-zoom', newScale.toString())
      return newScale
    })
  }

  const handleResetZoom = () => {
    setScale(0.72)
    localStorage.setItem('resume-preview-zoom', '0.72')
  }

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded)
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only listen when expanded (fullscreen)
      if (!isExpanded) return

      switch(e.key) {
        case 'Escape':
          setIsExpanded(false)
          break
        case 'f':
        case 'F':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault()
            setIsExpanded(!isExpanded)
          }
          break
        case '+':
        case '=':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault()
            handleZoomIn()
          }
          break
        case '-':
        case '_':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault()
            handleZoomOut()
          }
          break
        case '0':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault()
            handleResetZoom()
          }
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isExpanded])

  if (!isVisible) {
    return (
      <div className={`${className} flex items-center justify-center h-full`}>
        <button
          onClick={onToggle}
          className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg border border-white/20 text-white transition-all"
        >
          <Eye className="w-4 h-4" />
          <span>Show Live Preview</span>
        </button>
      </div>
    )
  }

  // Choose display scale: if user manually set zoom, respect it; otherwise use autoScale when not expanded
  const displayScale = isExpanded ? scale : (hasManualZoom ? scale : autoScale)

  return (
    <div 
      ref={containerRef}
      className={`${className} ${isExpanded ? 'fixed inset-0 z-50 bg-black/90 backdrop-blur-lg' : 'relative'} transition-all duration-300`}
    >
      {/* Preview Controls */}
      <div className={`${isExpanded ? 'sticky top-0 z-10' : ''} flex items-center justify-between p-3 bg-gradient-to-r from-gray-900 to-gray-800 border-b border-white/10`}>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 px-2 py-1 bg-white/10 rounded-lg">
            <button
              onClick={handleZoomOut}
              className="p-1 hover:bg-white/10 rounded text-white/70 hover:text-white transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-3 h-3" />
            </button>
            <span className="text-xs text-white/70 px-2 min-w-[3rem] text-center">
              {Math.round(scale * 100)}%
            </span>
            <button
              onClick={handleZoomIn}
              className="p-1 hover:bg-white/10 rounded text-white/70 hover:text-white transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-3 h-3" />
            </button>
          </div>
          <button
            onClick={handleResetZoom}
            className="p-1.5 hover:bg-white/10 rounded text-white/70 hover:text-white transition-colors"
            title="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="flex items-center gap-2">
          {isAnimating && (
            <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded-lg">
              <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
              <span className="text-xs text-blue-200">Updating...</span>
            </div>
          )}
          
          <button
            onClick={toggleExpanded}
            className="p-1.5 hover:bg-white/10 rounded text-white/70 hover:text-white transition-colors"
            title={isExpanded ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>

          {onToggle && !isExpanded && (
            <button
              onClick={onToggle}
              className="p-1.5 hover:bg-white/10 rounded text-white/70 hover:text-white transition-colors"
              title="Hide Preview"
            >
              <EyeOff className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Preview Content */}
      <div 
        className={`${isExpanded ? 'overflow-auto h-[calc(100vh-56px)]' : 'overflow-y-auto'} bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6`}
        style={{ maxHeight: isExpanded ? 'calc(100vh - 56px)' : '100%' }}
      >
        <div className="bg-gradient-to-br from-white/5 to-white/10 rounded-2xl p-4 border border-white/20 shadow-2xl flex justify-center w-full overflow-x-auto">
          <div 
            ref={previewRef}
            className={`bg-white rounded-xl shadow-2xl overflow-hidden transition-all duration-300 flex-shrink-0 ${
              isAnimating ? 'ring-2 ring-blue-400/50' : ''
            }`}
            style={{ 
              transform: `scale(${displayScale})`, 
              transformOrigin: 'top center',
              width: '8.5in',
              height: 'auto',
              minHeight: '11in',
              margin: '0 auto'
            }}
          >
            <ResumePreview resume={resume} />
          </div>
        </div>

        {/* Template Info Footer (Expanded mode only) */}
        {isExpanded && resume && (
          <div className="mt-6 max-w-3xl mx-auto">
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                  <p className="text-xs text-white/50 mb-1">Template</p>
                  <p className="text-sm text-white font-medium capitalize">{resume.template || 'Modern'}</p>
                </div>
                <div>
                  <p className="text-xs text-white/50 mb-1">Font</p>
                  <p className="text-sm text-white font-medium">{resume.font_family || 'Inter'}</p>
                </div>
                <div>
                  <p className="text-xs text-white/50 mb-1">Layout</p>
                  <p className="text-sm text-white font-medium capitalize">{resume.layout || 'Single Column'}</p>
                </div>
                <div>
                  <p className="text-xs text-white/50 mb-1">Accent Color</p>
                  <div className="flex items-center justify-center gap-2">
                    <div 
                      className="w-4 h-4 rounded border border-white/20"
                      style={{ backgroundColor: resume.accent_color || '#2563eb' }}
                    />
                    <p className="text-xs text-white/70 font-mono">{resume.accent_color || '#2563eb'}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Keyboard shortcuts hint */}
      {isExpanded && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/80 backdrop-blur-sm px-4 py-2 rounded-full border border-white/10">
          <p className="text-xs text-white/60 flex items-center gap-3">
            <span className="flex items-center gap-1">
              <kbd className="px-2 py-0.5 bg-white/10 rounded text-white/80 font-mono text-[10px]">ESC</kbd> to exit
            </span>
            <span className="text-white/30">•</span>
            <span className="flex items-center gap-1">
              <kbd className="px-2 py-0.5 bg-white/10 rounded text-white/80 font-mono text-[10px]">Ctrl</kbd>
              <span className="text-white/40">+</span>
              <kbd className="px-2 py-0.5 bg-white/10 rounded text-white/80 font-mono text-[10px]">+/-</kbd> zoom
            </span>
            <span className="text-white/30">•</span>
            <span className="flex items-center gap-1">
              <kbd className="px-2 py-0.5 bg-white/10 rounded text-white/80 font-mono text-[10px]">Ctrl</kbd>
              <span className="text-white/40">+</span>
              <kbd className="px-2 py-0.5 bg-white/10 rounded text-white/80 font-mono text-[10px]">0</kbd> reset
            </span>
          </p>
        </div>
      )}
    </div>
  )
}

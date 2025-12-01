import React from 'react'
import { Download, FileText, FileJson, FileCode, FileDown } from 'lucide-react'
import { exportResumePDFFromPreview } from '@/lib/pdf'

interface ExportOptionsModalProps {
  isOpen: boolean
  onClose: () => void
  resume: any
  resumeId: number
}

export default function ExportOptionsModal({ isOpen, onClose, resume, resumeId }: ExportOptionsModalProps) {
  const [dpi, setDpi] = React.useState<number>(300)
  const [marginMM, setMarginMM] = React.useState<number>(10)

  if (!isOpen) return null

  const loaded = !!resume && !!resumeId

  const exportAsJSON = () => {
    const dataStr = JSON.stringify(resume, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${resume.title || 'resume'}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const exportAsPDF = async () => {
    try {
      console.log(`[PDF Export] Attempting export for resume ${resumeId} with DPI=${dpi}, margin=${marginMM}mm`)
      
      // Use client-side export with custom DPI/margin settings
      await exportResumePDFFromPreview(
        resumeId, 
        `${resume.title || 'resume'}.pdf`,
        { dpi, marginMM }
      )
      console.log(`[PDF Export] Successfully exported with custom settings`)
    } catch (error) {
      console.error('[PDF Export] Exception:', error)
      alert('PDF export failed. Please try again later.')
    }
  }

  const exportAsText = () => {
    let text = ''
    
    // Header
    if (resume.full_name) text += `${resume.full_name}\n`
    if (resume.email) text += `${resume.email}`
    if (resume.phone) text += ` | ${resume.phone}`
    if (resume.location) text += ` | ${resume.location}`
    text += '\n' + '='.repeat(60) + '\n\n'

    // Summary
    if (resume.professional_summary) {
      text += 'PROFESSIONAL SUMMARY\n'
      text += resume.professional_summary + '\n\n'
    }

    // Work Experience
    if (resume.work_experiences?.length > 0) {
      text += 'WORK EXPERIENCE\n' + '-'.repeat(60) + '\n'
      resume.work_experiences.forEach((exp: any) => {
        text += `\n${exp.title} at ${exp.company}\n`
        if (exp.start_date || exp.end_date) {
          text += `${exp.start_date || ''} - ${exp.end_date || 'Present'}\n`
        }
        if (exp.description) text += `${exp.description}\n`
        if (exp.achievements?.length) {
          exp.achievements.forEach((ach: string) => text += `  • ${ach}\n`)
        }
      })
      text += '\n'
    }

    // Education
    if (resume.education?.length > 0) {
      text += 'EDUCATION\n' + '-'.repeat(60) + '\n'
      resume.education.forEach((edu: any) => {
        text += `\n${edu.degree} - ${edu.institution}\n`
        if (edu.graduation_date) text += `Graduated: ${edu.graduation_date}\n`
        if (edu.gpa) text += `GPA: ${edu.gpa}\n`
      })
      text += '\n'
    }

    // Skills
    if (resume.skills?.length > 0) {
      text += 'SKILLS\n' + '-'.repeat(60) + '\n'
      const skillsByCategory = resume.skills.reduce((acc: any, skill: any) => {
        const cat = skill.category || 'General'
        if (!acc[cat]) acc[cat] = []
        acc[cat].push(skill.name)
        return acc
      }, {})
      Object.entries(skillsByCategory).forEach(([category, skills]: [string, any]) => {
        text += `\n${category}: ${skills.join(', ')}\n`
      })
      text += '\n'
    }

    // Projects
    if (resume.projects?.length > 0) {
      text += 'PROJECTS\n' + '-'.repeat(60) + '\n'
      resume.projects.forEach((proj: any) => {
        text += `\n${proj.name}\n`
        if (proj.description) text += `${proj.description}\n`
        if (proj.technologies) text += `Technologies: ${proj.technologies}\n`
        if (proj.url) text += `URL: ${proj.url}\n`
      })
      text += '\n'
    }

    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${resume.title || 'resume'}.txt`
    link.click()
    URL.revokeObjectURL(url)
  }

  const exportAsWord = async () => {
    try {
      // Preflight: verify the resume exists and belongs to the current user
      try {
        const check = await fetch(`/api/session/resumes?id=${resumeId}`, {
          method: 'GET',
          credentials: 'include',
        })
        if (check.status === 401) {
          alert('You need to be logged in to export this resume.');
          return;
        }
        if (check.status === 404) {
          alert('This resume was not found or you do not have access. Open one of your resumes and try again.');
          return;
        }
      } catch (e) {
        console.warn('[DOCX Export] Preflight check failed:', e)
      }
       console.log(`[DOCX Export] Attempting export for resume ${resumeId} (type: ${typeof resumeId})`)
      // Use dedicated export endpoint that's reliable for demo
      const response = await fetch(`/api/session/export?resumeId=${resumeId}&format=docx`, {
        method: 'GET',
        credentials: 'include',
      })
      
      console.log(`[DOCX Export] Response status: ${response.status}`)
      console.log(`[DOCX Export] Response headers:`, {
        'content-type': response.headers.get('content-type'),
        'content-disposition': response.headers.get('content-disposition'),
        'x-debug-target': response.headers.get('x-debug-target')
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        // Prefer backend-provided filename when available
        const disposition = response.headers.get('content-disposition') || ''
        const match = disposition.match(/filename="?([^";]+)"?/i)
        const filename = match?.[1] || `${resume.title || 'resume'}.docx`
        link.download = filename
        link.click()
        URL.revokeObjectURL(url)
      } else {
        let msg = ''
        const ct = response.headers.get('content-type') || ''
        try {
          if (ct.includes('application/json')) {
            const j = await response.json()
            msg = j?.detail || JSON.stringify(j)
          } else {
            msg = await response.text()
          }
        } catch {}
        if (response.status === 401) {
          msg = msg || 'You need to be logged in to export this resume.'
        } else if (response.status === 404) {
          msg = msg || 'This resume was not found or you do not have access.'
        }
        console.error(`[DOCX Export] Failed with ${response.status}: ${msg}`)
        alert(`Word export failed (${response.status})${msg ? `: ${msg}` : ''}`)
      }
    } catch (error) {
      console.error('Word export failed:', error)
      alert('Word export failed. Please try PDF export instead.')
    }
  }

  const exportFormats = [
    {
      name: 'PDF (.pdf)',
      description: 'Print-ready professional PDF document',
      icon: FileDown,
      color: 'from-red-500 to-pink-600',
      action: exportAsPDF,
    },
    {
      name: 'JSON',
      description: 'Machine-readable format for data portability',
      icon: FileJson,
      color: 'from-yellow-500 to-orange-500',
      action: exportAsJSON,
    },
    {
      name: 'Plain Text',
      description: 'Simple text format for ATS systems',
      icon: FileCode,
      color: 'from-gray-500 to-gray-600',
      action: exportAsText,
    },
    {
      name: 'Word (.docx)',
      description: 'Editable Microsoft Word document',
      icon: FileText,
      color: 'from-blue-500 to-blue-600',
      action: exportAsWord,
      beta: true,
    },
  ]

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-gradient-to-br from-deepTech to-deepTech/90 rounded-2xl shadow-2xl border border-white/20 max-w-2xl w-full mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-forgePurple to-neuralBlue rounded-lg">
              <Download className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-black text-white">Export Resume</h3>
              <p className="text-xs text-white/60 mt-0.5">Choose your preferred export format</p>
            </div>
          </div>
        </div>

        {/* PDF Export Settings */}
        <div className="p-6 pb-4 border-b border-white/10 space-y-4">
          <h4 className="text-sm font-bold text-white/80 uppercase tracking-wide">PDF Export Settings</h4>
          
          {/* DPI Selection */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-white/70">Quality (DPI)</label>
            <div className="flex gap-2">
              {[150, 300, 600].map((dpiOption) => (
                <button
                  key={dpiOption}
                  onClick={() => setDpi(dpiOption)}
                  className={`flex-1 px-3 py-2 rounded-lg text-xs font-bold transition-all ${
                    dpi === dpiOption
                      ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white border-2 border-white/20'
                      : 'bg-white/5 text-white/60 border border-white/10 hover:bg-white/10'
                  }`}
                >
                  {dpiOption} DPI
                  {dpiOption === 150 && <div className="text-[9px] opacity-70">Fast</div>}
                  {dpiOption === 300 && <div className="text-[9px] opacity-70">Recommended</div>}
                  {dpiOption === 600 && <div className="text-[9px] opacity-70">High Quality</div>}
                </button>
              ))}
            </div>
          </div>

          {/* Margin Selection */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-white/70">Margins (mm)</label>
            <div className="flex gap-2">
              {[0, 5, 10, 15].map((margin) => (
                <button
                  key={margin}
                  onClick={() => setMarginMM(margin)}
                  className={`flex-1 px-3 py-2 rounded-lg text-xs font-bold transition-all ${
                    marginMM === margin
                      ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white border-2 border-white/20'
                      : 'bg-white/5 text-white/60 border border-white/10 hover:bg-white/10'
                  }`}
                >
                  {margin}mm
                  {margin === 0 && <div className="text-[9px] opacity-70">No margins</div>}
                  {margin === 10 && <div className="text-[9px] opacity-70">Standard</div>}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Export Options */}
        <div className="p-6 space-y-3">
          {exportFormats.map((format) => (
            <button
              key={format.name}
              onClick={() => {
                if (!loaded) {
                  alert('Resume data not loaded yet. Please wait a moment and try again.')
                  return
                }
                format.action()
                onClose()
              }}
              className="w-full flex items-center gap-4 p-4 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 hover:border-white/20 transition-all group"
              disabled={!loaded}
            >
              <div className={`p-3 bg-gradient-to-br ${format.color} rounded-lg group-hover:scale-110 transition-transform`}>
                <format.icon className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1 text-left">
                <div className="flex items-center gap-2">
                  <h4 className="text-lg font-bold text-white">{format.name}</h4>
                  {format.beta && (
                    <span className="px-2 py-0.5 bg-purple-500/20 border border-purple-500/30 rounded text-[10px] text-purple-200 font-bold uppercase">
                      Beta
                    </span>
                  )}
                </div>
                <p className="text-xs text-white/60 mt-0.5">{format.description}</p>
                {!loaded && (
                  <p className="text-[10px] text-yellow-300/70 mt-1">Resume not loaded yet</p>
                )}
              </div>
              <Download className="w-5 h-5 text-white/40 group-hover:text-white transition-colors" />
            </button>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/10 bg-white/5 text-center">
          <div className="text-xs text-white/60 space-y-1">
            <p>💡 <strong>Tip:</strong> Use PDF for job portals; DOCX if you plan to keep editing.</p>
            <p className="opacity-70">Debug: resumeId={resumeId} loaded={String(loaded)}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

import { Download, FileText, FileJson, FileCode } from 'lucide-react'

interface ExportOptionsModalProps {
  isOpen: boolean
  onClose: () => void
  resume: any
  resumeId: number
}

export default function ExportOptionsModal({ isOpen, onClose, resume, resumeId }: ExportOptionsModalProps) {
  if (!isOpen) return null

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
      const response = await fetch(`/api/session/resumes/${resumeId}/export/docx`, {
        method: 'GET',
        credentials: 'include',
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${resume.title || 'resume'}.docx`
        link.click()
        URL.revokeObjectURL(url)
      } else {
        alert('Word export not yet available. Please use PDF export.')
      }
    } catch (error) {
      console.error('Word export failed:', error)
      alert('Word export failed. Please try PDF export instead.')
    }
  }

  const exportFormats = [
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

        {/* Export Options */}
        <div className="p-6 space-y-3">
          {exportFormats.map((format) => (
            <button
              key={format.name}
              onClick={() => {
                format.action()
                onClose()
              }}
              className="w-full flex items-center gap-4 p-4 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 hover:border-white/20 transition-all group"
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
              </div>
              <Download className="w-5 h-5 text-white/40 group-hover:text-white transition-colors" />
            </button>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/10 bg-white/5 text-center">
          <p className="text-xs text-white/50">
            💡 <strong>Tip:</strong> Use PDF export for best compatibility with job applications
          </p>
        </div>
      </div>
    </div>
  )
}

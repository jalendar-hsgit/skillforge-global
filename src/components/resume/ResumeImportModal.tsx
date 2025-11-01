import { useEffect, useRef, useState } from 'react'
import { Upload, FileText, Loader2, CheckCircle2, AlertCircle, X } from 'lucide-react'
import ModalShell from './ModalShell'
// Lazy import jsPDF only when needed
let jsPDF: any = null

interface ParsedData {
  full_name?: string
  email?: string
  phone?: string
  professional_summary?: string
  raw_text?: string
  error?: string
  note?: string
  work_experience?: Array<{
    position?: string
    company?: string
    description?: string
  }>
  education?: Array<{
    institution?: string
    degree?: string
    field?: string
  }>
  skills?: string[]
}

interface ResumeImportModalProps {
  isOpen: boolean
  onClose: () => void
  onImportSuccess: (resumeId: number) => void
}

export default function ResumeImportModal({ isOpen, onClose, onImportSuccess }: ResumeImportModalProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [previewData, setPreviewData] = useState<ParsedData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [step, setStep] = useState<'upload' | 'preview' | 'importing'>('upload')
  const [isDragging, setIsDragging] = useState(false)
  const [showRaw, setShowRaw] = useState(false)
  const [nameInput, setNameInput] = useState('')
  const [emailInput, setEmailInput] = useState('')
  const [phoneInput, setPhoneInput] = useState('')
  const [summaryInput, setSummaryInput] = useState('')
  const [progress, setProgress] = useState(0)
  const progressTimer = useRef<NodeJS.Timeout | null>(null)
  const [filesQueue, setFilesQueue] = useState<File[]>([])
  const [useAI, setUseAI] = useState(false)
  const [toast, setToast] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null)

  useEffect(() => {
    if (uploading) {
      // Simulate a smooth progress bar while uploading/parsing
      setProgress(10)
      progressTimer.current = setInterval(() => {
        setProgress(p => (p < 90 ? p + Math.max(1, Math.floor((100 - p) / 10)) : p))
      }, 200)
    } else {
      if (progressTimer.current) clearInterval(progressTimer.current)
      setProgress(0)
    }
    return () => {
      if (progressTimer.current) clearInterval(progressTimer.current)
    }
  }, [uploading])

  const validateAndSetFile = (selectedFile: File) => {
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Please upload a PDF or DOCX file')
      return
    }
    
    // Validate file size (10MB max)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }
    
    setFile(selectedFile)
    setError(null)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files
    if (!fileList || fileList.length === 0) return
    const selectedFile = fileList[0]
    validateAndSetFile(selectedFile)
    if (fileList.length > 1) {
      setFilesQueue(Array.from(fileList))
    } else {
      setFilesQueue([])
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const droppedFile = e.dataTransfer.files?.[0]
    if (droppedFile) {
      validateAndSetFile(droppedFile)
    }
  }

  const handlePreview = async () => {
    if (!file) return

    setUploading(true)
    setError(null)

    try {
  const formData = new FormData()
  formData.append('file', file)
  if (useAI) formData.append('ai', '1')

      const res = await fetch('/api/session/v1x/resume-import/parse-preview', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      })

      if (!res.ok) {
        let detail = 'Failed to parse resume'
        try {
          const data = await res.json()
          if (typeof data?.detail === 'string') detail = data.detail
        } catch {}
        if (res.status === 401) detail = 'Please log in to import your resume.'
        if (res.status === 404) detail = 'Import service not found. Ensure backend is running on 8001.'
        throw new Error(detail)
      }

  const data = await res.json()
  setPreviewData(data.parsed_data)
  // seed editable inputs from parsed data
  setNameInput(data.parsed_data?.full_name || '')
  setEmailInput(data.parsed_data?.email || '')
  setPhoneInput(data.parsed_data?.phone || '')
  setSummaryInput(data.parsed_data?.professional_summary || '')
      setShowRaw(false)
      setStep('preview')
    } catch (e: any) {
      setError(e.message || 'Failed to parse resume')
    } finally {
      setUploading(false)
      setProgress(100)
    }
  }

  const handleImport = async () => {
    if (!file) return

    setStep('importing')
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      if (nameInput) formData.append('full_name', nameInput)
      if (emailInput) formData.append('email', emailInput)
      if (phoneInput) formData.append('phone', phoneInput)
      if (summaryInput) formData.append('summary', summaryInput)

      const res = await fetch('/api/session/v1x/resume-import/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      })

      if (!res.ok) {
        let detail = 'Failed to import resume'
        try {
          const data = await res.json()
          if (typeof data?.detail === 'string') detail = data.detail
        } catch {}
        if (res.status === 401) detail = 'Please log in to import your resume.'
        if (res.status === 404) detail = 'Import service not found. Ensure backend is running on 8001.'
        throw new Error(detail)
      }

      const resume = await res.json()
      setToast({ type: 'success', message: 'Resume imported successfully' })
      setTimeout(() => {
        onImportSuccess(resume.id)
        onClose()
      }, 800)
    } catch (e: any) {
      setError(e.message || 'Failed to import resume')
      setStep('preview')
    }
  }

  const reset = () => {
    setFile(null)
    setPreviewData(null)
    setError(null)
    setStep('upload')
    setFilesQueue([])
    setUseAI(false)
  }

  const fileBadge = (f?: File | null) => {
    if (!f) return null
    const isPdf = f.type === 'application/pdf' || (f.name || '').toLowerCase().endsWith('.pdf')
    const isDocx = f.type.includes('word') || (f.name || '').toLowerCase().endsWith('.docx')
    const label = isPdf ? 'PDF' : isDocx ? 'DOCX' : 'FILE'
    const color = isPdf ? 'bg-red-500/20 text-red-200 border-red-500/30' : isDocx ? 'bg-blue-500/20 text-blue-200 border-blue-500/30' : 'bg-white/10 text-white/70 border-white/20'
    return (
      <span className={`text-2xs px-2 py-0.5 rounded-full border ${color}`}>{label}</span>
    )
  }

  const trySample = async () => {
    try {
      if (!jsPDF) {
        const mod = await import('jspdf')
        jsPDF = mod.jsPDF || (mod as any).default
      }
      const doc = new jsPDF({ unit: 'pt' })
      const lines = [
        'John Doe',
        'john@example.com',
        '+1 555-555-1234',
        'Professional Summary',
        'Experienced developer with focus on robust web applications.',
        '',
        'Work Experience',
        'Senior Software Engineer',
        'Acme Corp',
        'Built scalable systems and led a team of 5 engineers.',
        '',
        'Education',
        'Bachelor of Science in Computer Science',
        'State University',
        '',
        'Skills',
        'JavaScript, TypeScript, React, Node.js, AWS, SQL'
      ]
      let y = 40
      doc.setFontSize(12)
      for (const ln of lines) {
        doc.text(ln, 40, y)
        y += 18
      }
      const blob = doc.output('blob') as Blob
      const sample = new File([blob], 'sample-resume.pdf', { type: 'application/pdf' })
      validateAndSetFile(sample)
      // Auto-run preview
      setTimeout(() => handlePreview(), 50)
    } catch (e) {
      setError('Failed to generate sample. Please upload your own file.')
    }
  }

  if (!isOpen) return null

  const footer = (
    <>
      {step === 'upload' && (
        <>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-xs text-white/70">
              <input type="checkbox" className="accent-forgePurple" checked={useAI} onChange={e => setUseAI(e.target.checked)} />
              Use AI assist
            </label>
            <button
              onClick={trySample}
              className="px-4 py-2 rounded-xl text-white/80 hover:text-white hover:bg-white/5 border border-white/10 text-sm transition-all"
            >
              Try sample resume
            </button>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-6 py-3 rounded-xl text-white/70 hover:text-white hover:bg-white/5 transition-all"
            >
              Cancel
            </button>
            <button
              onClick={handlePreview}
              disabled={!file || uploading}
              className="px-8 py-3 rounded-xl bg-gradient-to-r from-forgePurple to-neuralBlue text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-xl hover:shadow-forgePurple/30 hover:scale-105 transition-all duration-300 flex items-center gap-2 relative overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-neuralBlue to-forgePurple opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              {uploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin relative z-10" />
                  <span className="relative z-10">Parsing...</span>
                </>
              ) : (
                <>
                  <FileText className="w-5 h-5 relative z-10" />
                  <span className="relative z-10">Parse Resume</span>
                </>
              )}
            </button>
          </div>
        </>
      )}
      {step === 'preview' && (
        <>
          <button
            onClick={reset}
            className="px-6 py-3 rounded-xl text-white/70 hover:text-white hover:bg-white/5 transition-all"
          >
            Try Another File
          </button>
          <button
            onClick={handleImport}
            className="px-8 py-3 rounded-xl bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold hover:shadow-xl hover:shadow-green-500/30 hover:scale-105 transition-all duration-300 flex items-center gap-2 relative overflow-hidden group"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-green-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <CheckCircle2 className="w-5 h-5 relative z-10" />
            <span className="relative z-10">Import Resume</span>
          </button>
        </>
      )}
    </>
  )

  return (
    <>
      <ModalShell
        isOpen={isOpen}
        onClose={onClose}
        title="Import Resume"
        icon={<FileText className="w-6 h-6" />}
        accent="purple"
        size="lg"
        footer={footer}
      >
        <div onKeyDown={(e) => {
          if (e.key === 'Escape') onClose()
        }}>
          {step === 'upload' && (
            <div className="space-y-6">
              <p className="text-white/70 text-sm">
                Upload your existing resume (PDF or DOCX) and we'll automatically extract your information to create a new resume.
              </p>

              {/* File Upload Area */}
              <div className="relative">
                <input
                  type="file"
                  id="resume-file"
                  accept=".pdf,.docx"
                  multiple
                  onChange={handleFileChange}
                  className="sr-only"
                />
                <label
                  htmlFor="resume-file"
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`flex flex-col items-center justify-center w-full h-56 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-300 group relative overflow-hidden ${
                    isDragging 
                      ? 'border-forgePurple bg-forgePurple/10 scale-[1.02]' 
                      : 'border-white/20 hover:border-forgePurple/50 hover:bg-white/5'
                  }`}
                >
                  {/* Animated gradient on hover */}
                  <div className="absolute inset-0 bg-gradient-to-br from-forgePurple/0 via-neuralBlue/0 to-forgePurple/0 group-hover:from-forgePurple/5 group-hover:via-neuralBlue/5 group-hover:to-forgePurple/5 transition-all duration-500" />
                  
                  <div className="flex flex-col items-center justify-center pt-5 pb-6 relative z-10">
                    <div className="relative mb-4">
                      <Upload className="w-14 h-14 text-white/40 group-hover:text-forgePurple group-hover:scale-110 transition-all duration-300" />
                      <div className="absolute -inset-2 bg-forgePurple/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </div>
                    <p className="mb-2 text-base text-white/70 group-hover:text-white transition-colors">
                      <span className="font-semibold text-forgePurple group-hover:text-neuralBlue transition-colors">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-sm text-white/50 group-hover:text-white/60 transition-colors">PDF or DOCX (MAX. 10MB)</p>
                    <p className="text-xs text-white/30 mt-2">We'll extract your info automatically</p>
                  </div>
                </label>
              </div>

              {/* Selected File */}
              {file && (
                <div className="flex items-center gap-4 p-5 rounded-xl bg-gradient-to-r from-forgePurple/10 to-neuralBlue/10 border border-forgePurple/30 shadow-lg animate-in slide-in-from-bottom-4 duration-300">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-forgePurple/40 to-neuralBlue/40 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-white truncate mb-1">{file.name}</p>
                    <div className="flex items-center gap-3 text-xs text-white/60">
                      {fileBadge(file)}
                      <span>{(file.size / 1024).toFixed(1)} KB</span>
                      <span>•</span>
                      <span className="text-green-400 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        Ready to parse
                      </span>
                      {filesQueue.length > 1 && (
                        <span className="ml-2 text-white/70 bg-white/10 px-2 py-0.5 rounded-full border border-white/20">{filesQueue.length} files selected</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => setFile(null)}
                    className="p-2 rounded-lg hover:bg-white/20 transition-all hover:scale-110"
                    aria-label="Remove file"
                  >
                    <X className="w-5 h-5 text-white/70" />
                  </button>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="flex items-start gap-3 p-4 rounded-xl bg-gradient-to-r from-red-500/10 to-rose-500/10 border border-red-500/30 animate-in slide-in-from-top-4 duration-300">
                  <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0">
                    <AlertCircle className="w-4 h-4 text-red-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-red-200 mb-1">Upload Error</p>
                    <p className="text-xs text-red-300/80">{error}</p>
                  </div>
                  <button
                    onClick={() => setError(null)}
                    className="p-1 rounded-lg hover:bg-white/10 transition-colors"
                    aria-label="Dismiss error"
                  >
                    <X className="w-4 h-4 text-red-300/60" />
                  </button>
                </div>
              )}
            </div>
          )}

          {step === 'preview' && previewData && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* Success Banner */}
              <div className="flex items-center gap-3 p-4 rounded-xl bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/40">
                <div className="w-10 h-10 rounded-full bg-green-500/30 flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5 text-green-300 animate-in zoom-in duration-300" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-green-200">Resume parsed successfully!</p>
                  <p className="text-xs text-green-300/70 mt-0.5">Review the extracted information below</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-white font-semibold text-lg">Extracted Information</h3>
                  <span className="text-xs text-white/50 bg-white/5 px-3 py-1 rounded-full">
                    {[previewData.full_name, previewData.email, previewData.phone, previewData.professional_summary].filter(Boolean).length} fields found
                  </span>
                </div>
                
                <div className="p-4 rounded-xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 hover:border-forgePurple/30 transition-all duration-300 group">
                  <label className="flex items-center gap-2 text-xs text-white/50 uppercase tracking-wide font-semibold mb-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-forgePurple group-hover:bg-neuralBlue transition-colors" />
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={nameInput}
                    onChange={e => setNameInput(e.target.value)}
                    placeholder="e.g., Jane Doe"
                    className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-forgePurple/50"
                  />
                </div>

                <div className="p-4 rounded-xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 hover:border-forgePurple/30 transition-all duration-300 group">
                  <label className="flex items-center gap-2 text-xs text-white/50 uppercase tracking-wide font-semibold mb-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-forgePurple group-hover:bg-neuralBlue transition-colors" />
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={emailInput}
                    onChange={e => setEmailInput(e.target.value)}
                    placeholder="e.g., jane@example.com"
                    className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-forgePurple/50"
                  />
                </div>

                <div className="p-4 rounded-xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 hover:border-forgePurple/30 transition-all duration-300 group">
                  <label className="flex items-center gap-2 text-xs text-white/50 uppercase tracking-wide font-semibold mb-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-forgePurple group-hover:bg-neuralBlue transition-colors" />
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={phoneInput}
                    onChange={e => setPhoneInput(e.target.value)}
                    placeholder="e.g., +1 555-555-1234"
                    className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-forgePurple/50"
                  />
                </div>

                <div className="p-4 rounded-xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 hover:border-forgePurple/30 transition-all duration-300 group">
                  <label className="flex items-center gap-2 text-xs text-white/50 uppercase tracking-wide font-semibold mb-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-forgePurple group-hover:bg-neuralBlue transition-colors" />
                    Professional Summary
                  </label>
                  <textarea
                    value={summaryInput}
                    onChange={e => setSummaryInput(e.target.value)}
                    rows={4}
                    placeholder="Brief, compelling summary of experience and impact."
                    className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-forgePurple/50"
                  />
                </div>

                {/* Work Experience */}
                {previewData.work_experience && previewData.work_experience.length > 0 && (
                  <div className="p-4 rounded-xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10">
                    <label className="flex items-center gap-2 text-xs text-white/50 uppercase tracking-wide font-semibold mb-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-forgePurple" />
                      Work Experience ({previewData.work_experience.length})
                    </label>
                    <div className="space-y-3">
                      {previewData.work_experience.map((exp, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-white/5 border border-white/10">
                          <p className="text-sm text-white font-medium">{exp.position || 'Position'}</p>
                          {exp.company && <p className="text-xs text-white/70 mt-1">{exp.company}</p>}
                          {exp.description && <p className="text-xs text-white/50 mt-2 line-clamp-2">{exp.description}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Education */}
                {previewData.education && previewData.education.length > 0 && (
                  <div className="p-4 rounded-xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10">
                    <label className="flex items-center gap-2 text-xs text-white/50 uppercase tracking-wide font-semibold mb-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-forgePurple" />
                      Education ({previewData.education.length})
                    </label>
                    <div className="space-y-3">
                      {previewData.education.map((edu, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-white/5 border border-white/10">
                          <p className="text-sm text-white font-medium">{edu.degree || 'Degree'}</p>
                          {edu.institution && <p className="text-xs text-white/70 mt-1">{edu.institution}</p>}
                          {edu.field && <p className="text-xs text-white/50 mt-1">{edu.field}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Skills */}
                {previewData.skills && previewData.skills.length > 0 && (
                  <div className="p-4 rounded-xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10">
                    <label className="flex items-center gap-2 text-xs text-white/50 uppercase tracking-wide font-semibold mb-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-forgePurple" />
                      Skills ({previewData.skills.length})
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {previewData.skills.slice(0, 15).map((skill, idx) => (
                        <span key={idx} className="text-xs px-3 py-1 rounded-full bg-forgePurple/20 text-white/90 border border-forgePurple/30">
                          {skill}
                        </span>
                      ))}
                      {previewData.skills.length > 15 && (
                        <span className="text-xs px-3 py-1 rounded-full bg-white/10 text-white/60 border border-white/20">
                          +{previewData.skills.length - 15} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Template recommendations stub */}
                <div className="p-4 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between">
                  <div>
                    <p className="text-sm text-white/80 font-medium">Recommended templates</p>
                    <p className="text-xs text-white/60">Based on parsed content and skills</p>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-2xs px-2 py-0.5 rounded-full border bg-white/10 text-white/80 border-white/20">ATS-Friendly</span>
                    <span className="text-2xs px-2 py-0.5 rounded-full border bg-white/10 text-white/80 border-white/20">Modern</span>
                  </div>
                </div>

                {/* Raw text toggle */}
                {previewData.raw_text && (
                  <div className="rounded-xl border border-white/10 bg-white/5">
                    <button
                      onClick={() => setShowRaw(v => !v)}
                      className="w-full flex items-center justify-between px-4 py-3 text-sm text-white/80 hover:bg-white/10 rounded-t-xl"
                    >
                      <span>Extracted Raw Text</span>
                      <span className="text-white/50">{showRaw ? 'Hide' : 'Show'}</span>
                    </button>
                    {showRaw && (
                      <div className="max-h-60 overflow-auto p-4 text-xs text-white/70 whitespace-pre-wrap">
                        {previewData.raw_text}
                      </div>
                    )}
                  </div>
                )}

                {previewData.error && (
                  <div className="flex items-start gap-3 p-4 rounded-xl bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/30">
                    <div className="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center flex-shrink-0">
                      <AlertCircle className="w-4 h-4 text-yellow-400" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-yellow-200 mb-1">{previewData.error}</p>
                      {previewData.note && <p className="text-xs text-yellow-300/70">{previewData.note}</p>}
                    </div>
                  </div>
                )}

                {!previewData.full_name && !previewData.email && !previewData.phone && !previewData.professional_summary && !previewData.error && (
                  <div className="flex items-center gap-3 p-4 rounded-xl bg-white/5 border border-white/10">
                    <AlertCircle className="w-5 h-5 text-white/40" />
                    <p className="text-sm text-white/60">No structured data found. You can still import and add details manually.</p>
                  </div>
                )}
              </div>

              <div className="flex items-start gap-2 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
                <div className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs text-blue-300">ℹ</span>
                </div>
                <p className="text-xs text-blue-200 leading-relaxed">
                  You can edit all information after importing. Additional sections like work experience and education can be added in the resume editor.
                </p>
              </div>
            </div>
          )}

          {step === 'importing' && (
            <div className="flex flex-col items-center justify-center py-16 animate-in fade-in duration-300">
              <div className="relative">
                <Loader2 className="w-16 h-16 text-forgePurple animate-spin" />
                <div className="absolute inset-0 w-16 h-16 bg-forgePurple/20 rounded-full blur-xl animate-pulse" />
              </div>
              <p className="text-white font-semibold text-lg mt-6">Creating your resume...</p>
              <p className="text-white/60 text-sm mt-2 max-w-xs text-center">
                We're importing your information and setting up your new resume
              </p>
              <div className="flex items-center gap-2 mt-6">
                <div className="w-2 h-2 bg-forgePurple rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-neuralBlue rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-forgePurple rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
        </div>

        {/* Progress bar */}
        {uploading && (
          <div className="mt-4">
            <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue transition-all" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}
      </ModalShell>

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-[70]">
          <div
            className={`min-w-[220px] max-w-sm px-4 py-3 rounded-xl shadow-2xl border backdrop-blur-sm transition-all ${
              toast.type === 'success'
                ? 'bg-green-500/20 border-green-400/40 text-green-100'
                : toast.type === 'error'
                ? 'bg-red-500/20 border-red-400/40 text-red-100'
                : 'bg-blue-500/20 border-blue-400/40 text-blue-100'
            }`}
            role="status"
            aria-live="polite"
          >
            <p className="text-sm font-semibold tracking-wide">{toast.message}</p>
          </div>
        </div>
      )}
    </>
  )
}

import { useState } from 'react'
import { Card } from '@/components/Card'
import { Button } from '@/components/Button'
import { Target, AlertCircle, CheckCircle, TrendingUp, Lightbulb } from 'lucide-react'

interface ATSInsightsPanelProps {
  resumeId: string
  resumeContent: any
  onClose: () => void
}

interface KeywordGap {
  keyword: string
  inResume: boolean
  frequency: number
}

export default function ATSInsightsPanel({ resumeId, resumeContent, onClose }: ATSInsightsPanelProps) {
  const [jobDescription, setJobDescription] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [keywordGaps, setKeywordGaps] = useState<KeywordGap[]>([])
  const [atsBreakdown, setAtsBreakdown] = useState<any>(null)

  const extractKeywords = (text: string): string[] => {
    // Simple keyword extraction - remove common words and punctuation
    const commonWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'])
    
    const words = text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 2 && !commonWords.has(w))
    
    // Count frequency
    const freq: Record<string, number> = {}
    words.forEach(w => {
      freq[w] = (freq[w] || 0) + 1
    })
    
    // Return sorted by frequency
    return Object.entries(freq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 30)
      .map(([word]) => word)
  }

  const analyzeGaps = async () => {
    if (!jobDescription.trim()) {
      alert('Please paste a job description first')
      return
    }

    setAnalyzing(true)
    
    try {
      // Extract keywords from JD
      const jdKeywords = extractKeywords(jobDescription)
      
      // Build resume text from content
      const resumeText = [
        resumeContent.professional_summary || '',
        ...(resumeContent.work_experiences || []).map((exp: any) => 
          `${exp.position} ${exp.company} ${exp.description || ''} ${(exp.bullet_points || []).join(' ')}`
        ),
        ...(resumeContent.skills || []).map((s: any) => s.name || s.skill_name || ''),
        ...(resumeContent.projects || []).map((p: any) => `${p.name || p.title || ''} ${p.description || ''}`),
      ].join(' ').toLowerCase()
      
      // Check which JD keywords are in resume
      const gaps: KeywordGap[] = jdKeywords.map(kw => ({
        keyword: kw,
        inResume: resumeText.includes(kw),
        frequency: (jobDescription.toLowerCase().match(new RegExp(kw, 'g')) || []).length
      }))
      
      setKeywordGaps(gaps)
      
      // Fetch ATS breakdown if available
      try {
        const res = await fetch(`/api/session/v1x/resume-ai/ats-score/${resumeId}`, {
          credentials: 'include'
        })
        if (res.ok) {
          const data = await res.json()
          setAtsBreakdown(data)
        }
      } catch (e) {
        console.warn('ATS breakdown not available:', e)
      }
    } catch (error) {
      console.error('Analysis failed:', error)
      alert('Analysis failed. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  const missingKeywords = keywordGaps.filter(k => !k.inResume)
  const matchedKeywords = keywordGaps.filter(k => k.inResume)
  const matchRate = keywordGaps.length > 0 ? (matchedKeywords.length / keywordGaps.length) * 100 : 0

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
        <h3 className="text-xl font-black flex items-center gap-3" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
          <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
            <Target className="w-5 h-5 text-white" />
          </div>
          <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
            ATS Insights
          </span>
        </h3>
        <button
          onClick={onClose}
          className="p-2 hover:bg-white/10 rounded-lg transition-all duration-200 group"
        >
          <span className="text-2xl text-techGray group-hover:text-white transition-colors">×</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4">
        {/* Job Description Input */}
        <Card className="p-4 bg-white/5 border-white/10">
          <label className="block text-sm font-bold text-white mb-2">Job Description</label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here to analyze keyword gaps..."
            rows={8}
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500/40 text-sm"
          />
          <Button
            onClick={analyzeGaps}
            disabled={analyzing || !jobDescription.trim()}
            className="mt-3 w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 font-semibold"
          >
            {analyzing ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Analyzing...
              </>
            ) : (
              <>
                <Target className="w-4 h-4 mr-2" />
                Analyze Keywords
              </>
            )}
          </Button>
        </Card>

        {/* Results */}
        {keywordGaps.length > 0 && (
          <>
            {/* Match Rate */}
            <Card className="p-4 bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-400/30">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-bold text-white">Keyword Match Rate</h4>
                <TrendingUp className={`w-4 h-4 ${matchRate >= 70 ? 'text-green-400' : matchRate >= 50 ? 'text-yellow-400' : 'text-red-400'}`} />
              </div>
              <div className="text-3xl font-black text-white mb-2">{matchRate.toFixed(0)}%</div>
              <div className="w-full bg-white/10 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${matchRate >= 70 ? 'bg-green-400' : matchRate >= 50 ? 'bg-yellow-400' : 'bg-red-400'}`}
                  style={{ width: `${matchRate}%` }}
                />
              </div>
              <p className="text-xs text-white/60 mt-2">
                {matchedKeywords.length} of {keywordGaps.length} key terms found in your resume
              </p>
            </Card>

            {/* Missing Keywords */}
            {missingKeywords.length > 0 && (
              <Card className="p-4 bg-red-500/10 border-red-400/30">
                <div className="flex items-center gap-2 mb-3">
                  <AlertCircle className="w-4 h-4 text-red-400" />
                  <h4 className="text-sm font-bold text-red-200">Missing Keywords ({missingKeywords.length})</h4>
                </div>
                <div className="flex flex-wrap gap-2">
                  {missingKeywords.slice(0, 15).map((kw, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-red-500/20 border border-red-400/40 rounded text-xs font-semibold text-red-200"
                      title={`Appears ${kw.frequency} time(s) in JD`}
                    >
                      {kw.keyword}
                    </span>
                  ))}
                  {missingKeywords.length > 15 && (
                    <span className="text-xs text-red-200/60">+{missingKeywords.length - 15} more</span>
                  )}
                </div>
                <div className="mt-3 p-3 bg-red-500/10 rounded-lg border border-red-400/20">
                  <div className="flex items-start gap-2">
                    <Lightbulb className="w-4 h-4 text-yellow-300 mt-0.5" />
                    <p className="text-xs text-white/80">
                      <strong>Tip:</strong> Add these keywords naturally to your experience bullets, skills, or summary to improve ATS matching.
                    </p>
                  </div>
                </div>
              </Card>
            )}

            {/* Matched Keywords */}
            {matchedKeywords.length > 0 && (
              <Card className="p-4 bg-green-500/10 border-green-400/30">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  <h4 className="text-sm font-bold text-green-200">Matched Keywords ({matchedKeywords.length})</h4>
                </div>
                <div className="flex flex-wrap gap-2">
                  {matchedKeywords.slice(0, 15).map((kw, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-green-500/20 border border-green-400/40 rounded text-xs font-semibold text-green-200"
                      title={`Appears ${kw.frequency} time(s) in JD`}
                    >
                      {kw.keyword}
                    </span>
                  ))}
                  {matchedKeywords.length > 15 && (
                    <span className="text-xs text-green-200/60">+{matchedKeywords.length - 15} more</span>
                  )}
                </div>
              </Card>
            )}

            {/* ATS Breakdown if available */}
            {atsBreakdown && (
              <Card className="p-4 bg-blue-500/10 border-blue-400/30">
                <h4 className="text-sm font-bold text-blue-200 mb-3">ATS Score Breakdown</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-white/70">Overall Score:</span>
                    <span className="font-bold text-white">{atsBreakdown.score || 0}%</span>
                  </div>
                  {atsBreakdown.breakdown && Object.entries(atsBreakdown.breakdown).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex justify-between text-xs">
                      <span className="text-white/70 capitalize">{key.replace(/_/g, ' ')}:</span>
                      <span className="text-white/90">{value}</span>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </>
        )}

        {keywordGaps.length === 0 && (
          <div className="text-center py-10">
            <Target className="w-12 h-12 text-white/20 mx-auto mb-3" />
            <p className="text-white/60 text-sm">Paste a job description above to get started</p>
          </div>
        )}
      </div>
    </div>
  )
}

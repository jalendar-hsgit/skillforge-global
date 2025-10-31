import { useEffect, useState } from 'react'
import { Card } from '@/components/Card'

interface ATSReport {
  score: number
  missing_keywords: string[]
  issues: { message: string; severity: 'low' | 'medium' | 'high' }[]
  recommendations: string[]
}

export default function ATSScoreCard({ resumeId }: { resumeId: number }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [report, setReport] = useState<ATSReport | null>(null)

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

  useEffect(() => {
    let mounted = true
    const fetchReport = async () => {
      try {
        setLoading(true)
        setError(null)
        const token = document.cookie
          .split('; ')
          .find(row => row.startsWith('token='))
          ?.split('=')[1]
        const res = await fetch(`${API_BASE}/api/v1x/resume-ai/ats-analysis/${resumeId}`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (!res.ok) throw new Error('Failed to fetch ATS report')
        const data = await res.json()
        if (mounted) setReport(data)
      } catch (e: any) {
        if (mounted) setError(e.message || 'Error fetching ATS report')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    fetchReport()
    return () => { mounted = false }
  }, [resumeId])

  const score = report?.score ?? 0
  const zone = score < 50 ? 'red' : score < 75 ? 'yellow' : 'green'
  const ringColor = zone === 'red' ? '#ef4444' : zone === 'yellow' ? '#eab308' : '#22c55e'

  return (
    <Card className="p-4">
      <h3 className="font-semibold text-gray-900 mb-3">ATS Score</h3>
      {loading ? (
        <div className="flex items-center gap-2 text-gray-600">
          <span className="animate-spin">⏳</span>
          <span>Analyzing…</span>
        </div>
      ) : error ? (
        <p className="text-sm text-red-600">{error}</p>
      ) : report ? (
        <div className="space-y-4">
          {/* Score donut */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <svg width="80" height="80" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="16" fill="none" stroke="#e5e7eb" strokeWidth="4" />
                <circle
                  cx="18"
                  cy="18"
                  r="16"
                  fill="none"
                  stroke={ringColor}
                  strokeWidth="4"
                  strokeDasharray={`${(score/100)*100} 100`}
                  transform="rotate(-90 18 18)"
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center font-bold text-gray-900">
                {score}
              </div>
            </div>
            <div className="text-sm text-gray-700">
              <p>
                Status:{' '}
                <span className={zone === 'red' ? 'text-red-600' : zone === 'yellow' ? 'text-yellow-600' : 'text-green-600'}>
                  {zone === 'red' ? 'Needs work' : zone === 'yellow' ? 'Good' : 'Strong'}
                </span>
              </p>
              <p className="text-gray-500">Aim for 75+ for best results</p>
            </div>
          </div>

          {/* Missing keywords */}
          {report.missing_keywords?.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Missing Keywords</h4>
              <div className="flex flex-wrap gap-2">
                {report.missing_keywords.map((kw, i) => (
                  <span key={i} className="px-2 py-1 text-xs rounded-full bg-orange-100 text-orange-700">
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Issues */}
          {report.issues?.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Issues</h4>
              <ul className="space-y-1 text-sm">
                {report.issues.map((it, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className={
                      it.severity === 'high' ? 'text-red-600' : it.severity === 'medium' ? 'text-yellow-600' : 'text-gray-600'
                    }>•</span>
                    <span className="text-gray-700">{it.message}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {report.recommendations?.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Recommendations</h4>
              <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                {report.recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <p className="text-sm text-gray-600">No report available.</p>
      )}
    </Card>
  )
}

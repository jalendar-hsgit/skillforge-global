import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Layout from '@/components/Layout'
import { PageHeader, PageSection, PageGrid, PageContainer } from '@/components/PageLayout'
import { StatCard, AlertCard, ActionCard } from '@/components/Cards'
import { Button } from '@/components/Button'
import { AlertCircle, TrendingUp, Zap, BookOpen, RefreshCw, Download } from 'lucide-react'

interface ATSScore {
  overall_score: number
  section_scores: {
    [key: string]: number
  }
  missing_keywords: string[]
  found_keywords: string[]
  improvements: string[]
  analysis: string
  timestamp: string
}

interface Resume {
  id: number
  title: string
  full_name?: string
  ats_score: number
}

export default function ATSScorePage() {
  const router = useRouter()
  const { id } = router.query
  const [resume, setResume] = useState<Resume | null>(null)
  const [atsScore, setATSScore] = useState<ATSScore | null>(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      fetchResume()
      fetchATSScore()
    }
  }, [id])

  const fetchResume = async () => {
    try {
      const res = await fetch(`/api/session/resumes/${id}`, {
        credentials: 'include',
      })
      if (res.ok) {
        const data = await res.json()
        setResume(data)
      }
    } catch (e) {
      console.error('Error fetching resume:', e)
      setError('Failed to load resume')
    }
  }

  const fetchATSScore = async () => {
    try {
      setLoading(true)
      const res = await fetch(`/api/v1x/resume-scoring/score-by-resume/${id}`, {
        credentials: 'include',
      })
      if (res.ok) {
        const data = await res.json()
        setATSScore(data)
      } else if (res.status === 404) {
        // No score yet - this is fine, we'll show a message to analyze
        setATSScore(null)
      }
    } catch (e) {
      console.error('Error fetching ATS score:', e)
      setError('Failed to load ATS score')
    } finally {
      setLoading(false)
    }
  }

  const analyzeATS = async () => {
    if (!id) return
    try {
      setAnalyzing(true)
      const res = await fetch('/api/v1x/resume-ai/ats-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ resume_id: parseInt(id as string) }),
      })
      if (res.ok) {
        const data = await res.json()
        setATSScore(data)
      } else {
        setError('Failed to analyze ATS score')
      }
    } catch (e) {
      console.error('Error analyzing ATS:', e)
      setError('Error analyzing resume')
    } finally {
      setAnalyzing(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'green'
    if (score >= 70) return 'yellow'
    return 'red'
  }

  if (loading) {
    return (
      <Layout maxWidth="7xl">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Loading ATS analysis...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <>
      <Head>
        <title>ATS Score - {resume?.title || 'Resume'} - SkillForge</title>
      </Head>

      <Layout maxWidth="7xl">
        <PageHeader
          icon="🤖"
          title="ATS Score Analysis"
          subtitle="Optimize your resume for Applicant Tracking Systems"
          breadcrumbs={[
            { label: 'Resumes', href: '/resumes' },
            { label: resume?.title || 'Resume', href: `/resumes/${id}` },
            { label: 'ATS Score' },
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

        {!atsScore ? (
          <PageSection icon="🔍" title="No Analysis Yet">
            <PageContainer variant="glass" className="text-center py-12">
              <p className="text-gray-600 mb-6">
                Run an ATS analysis to see how your resume scores with Applicant Tracking Systems.
              </p>
              <Button
                onClick={analyzeATS}
                disabled={analyzing}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                {analyzing ? 'Analyzing...' : 'Analyze My Resume'}
              </Button>
            </PageContainer>
          </PageSection>
        ) : (
          <>
            {/* Overall Score */}
            <PageSection icon="📊" title="Overall Score">
              <PageGrid cols={1} gap="md">
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8 border border-blue-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-600 text-sm mb-2">ATS SCORE</p>
                      <div className="flex items-baseline gap-2">
                        <span className={`text-6xl font-bold text-${getScoreColor(atsScore.overall_score)}-600`}>
                          {Math.round(atsScore.overall_score)}
                        </span>
                        <span className="text-gray-500">/100</span>
                      </div>
                    </div>
                    <div className="text-right">
                      {atsScore.overall_score >= 85 ? (
                        <p className="text-green-600 font-semibold mb-2">✅ Excellent</p>
                      ) : atsScore.overall_score >= 70 ? (
                        <p className="text-yellow-600 font-semibold mb-2">⚠️ Good</p>
                      ) : (
                        <p className="text-red-600 font-semibold mb-2">❌ Needs Improvement</p>
                      )}
                      <p className="text-sm text-gray-500">Updated: {new Date(atsScore.timestamp).toLocaleDateString()}</p>
                    </div>
                  </div>
                </div>
              </PageGrid>
            </PageSection>

            {/* Section Scores */}
            {atsScore?.section_scores && Object.keys(atsScore.section_scores).length > 0 && (
              <PageSection icon="📈" title="Section Scores">
                <PageGrid cols={2} gap="md">
                  {Object.entries(atsScore.section_scores).map(([section, score]) => (
                    <ActionCard
                      key={section}
                      icon="📝"
                      label={section.replace(/_/g, ' ').toUpperCase()}
                      value={`${Math.round(score as number)}/100`}
                      color={getScoreColor(score as number)}
                      onClick={() => {}}
                    />
                  ))}
                </PageGrid>
              </PageSection>
            )}

            {/* Keywords Found */}
            {atsScore?.found_keywords && atsScore.found_keywords.length > 0 && (
              <PageSection icon="✅" title="Keywords Found">
                <PageContainer variant="card">
                  <div className="flex flex-wrap gap-2">
                    {atsScore.found_keywords.slice(0, 20).map((keyword, idx) => (
                      <span
                        key={idx}
                        className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium"
                      >
                        {keyword}
                      </span>
                    ))}
                    {atsScore.found_keywords.length > 20 && (
                      <span className="text-gray-500 text-sm px-2 py-1">
                        +{atsScore.found_keywords.length - 20} more
                      </span>
                    )}
                  </div>
                </PageContainer>
              </PageSection>
            )}

            {/* Missing Keywords */}
            {atsScore?.missing_keywords && atsScore.missing_keywords.length > 0 && (
              <PageSection icon="⚠️" title="Missing Keywords">
                <PageContainer variant="card">
                  <p className="text-gray-600 text-sm mb-4">
                    Adding these keywords could improve your ATS score:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {atsScore.missing_keywords.slice(0, 20).map((keyword, idx) => (
                      <span
                        key={idx}
                        className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium"
                      >
                        {keyword}
                      </span>
                    ))}
                    {atsScore.missing_keywords.length > 20 && (
                      <span className="text-gray-500 text-sm px-2 py-1">
                        +{atsScore.missing_keywords.length - 20} more
                      </span>
                    )}
                  </div>
                </PageContainer>
              </PageSection>
            )}

            {/* Improvements */}
            {atsScore?.improvements && atsScore.improvements.length > 0 && (
              <PageSection icon="💡" title="Recommendations">
                <div className="space-y-3">
                  {atsScore.improvements.map((improvement, idx) => (
                    <AlertCard
                      key={idx}
                      variant="info"
                      title={`Tip ${idx + 1}`}
                      message={improvement}
                    />
                  ))}
                </div>
              </PageSection>
            )}

            {/* Analysis */}
            {atsScore.analysis && (
              <PageSection icon="📋" title="Detailed Analysis">
                <PageContainer variant="card" className="prose prose-sm max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap">{atsScore.analysis}</p>
                </PageContainer>
              </PageSection>
            )}

            {/* Actions */}
            <PageSection icon="🚀" title="Next Steps">
              <PageGrid cols={3} gap="md">
                <Button
                  onClick={analyzeATS}
                  disabled={analyzing}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {analyzing ? 'Re-analyzing...' : 'Re-analyze'}
                </Button>
                <Button
                  onClick={() => router.push(`/resumes/${id}/edit`)}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                >
                  Edit Resume
                </Button>
                <Button
                  onClick={() => router.push(`/resumes/${id}/export`)}
                  className="w-full bg-green-600 hover:bg-green-700 text-white"
                >
                  Export
                </Button>
              </PageGrid>
            </PageSection>
          </>
        )}
      </Layout>
    </>
  )
}

import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Layout from '@/components/Layout'
import { PageHeader, PageSection, PageContainer } from '@/components/PageLayout'
import { Button } from '@/components/Button'
import { AlertCard } from '@/components/Cards'
import { ChevronDown, RotateCw } from 'lucide-react'

interface Resume {
  id: number
  title: string
  full_name?: string
  email?: string
  phone?: string
  location?: string
  summary?: string
  ats_score?: number
  views?: number
  downloads?: number
  updated_at?: string
}

interface ComparisonField {
  label: string
  key: string
}

export default function ComparePage() {
  const router = useRouter()
  const { id } = router.query
  const [resumeA, setResumeA] = useState<Resume | null>(null)
  const [resumeB, setResumeB] = useState<Resume | null>(null)
  const [allResumes, setAllResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedResumeB, setSelectedResumeB] = useState<number | null>(null)

  const comparisonFields: ComparisonField[] = [
    { label: 'Title', key: 'title' },
    { label: 'Full Name', key: 'full_name' },
    { label: 'Email', key: 'email' },
    { label: 'Phone', key: 'phone' },
    { label: 'Location', key: 'location' },
    { label: 'Professional Summary', key: 'summary' },
    { label: 'ATS Score', key: 'ats_score' },
    { label: 'Views', key: 'views' },
    { label: 'Downloads', key: 'downloads' },
  ]

  useEffect(() => {
    if (id) {
      fetchResumes()
    }
  }, [id])

  const fetchResumes = async () => {
    try {
      setLoading(true)
      
      // Fetch all resumes
      const res = await fetch('/api/session/resumes', {
        credentials: 'include',
      })
      
      if (res.ok) {
        const data = await res.json()
        setAllResumes(data)
        
        // Set Resume A as the one from URL
        const resume = data.find((r: Resume) => r.id === parseInt(id as string))
        if (resume) {
          setResumeA(resume)
        }
        
        // Set Resume B as the first other resume (if exists)
        const other = data.find((r: Resume) => r.id !== parseInt(id as string))
        if (other) {
          setResumeB(other)
          setSelectedResumeB(other.id)
        }
      } else {
        setError('Failed to load resumes')
      }
    } catch (e) {
      console.error('Error fetching resumes:', e)
      setError('Error loading resumes')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectResumeB = async (resumeId: number) => {
    try {
      const res = await fetch(`/api/session/resumes/${resumeId}`, {
        credentials: 'include',
      })
      if (res.ok) {
        const data = await res.json()
        setResumeB(data)
        setSelectedResumeB(resumeId)
      }
    } catch (e) {
      console.error('Error loading resume:', e)
    }
  }

  const swapResumes = () => {
    const temp = resumeA
    setResumeA(resumeB)
    setResumeB(temp)
  }

  const getFieldValue = (resume: Resume | null, key: string): string => {
    if (!resume) return '-'
    const value = (resume as any)[key]
    if (value === null || value === undefined) return '-'
    if (key === 'summary') return value.substring(0, 100) + (value.length > 100 ? '...' : '')
    return String(value)
  }

  const isSame = (val1: string, val2: string) => {
    return val1 !== '-' && val2 !== '-' && val1 === val2
  }

  const isDifferent = (val1: string, val2: string) => {
    return val1 !== '-' && val2 !== '-' && val1 !== val2
  }

  if (loading) {
    return (
      <Layout maxWidth="7xl">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Loading resumes...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <>
      <Head>
        <title>Compare Resumes - SkillForge</title>
      </Head>

      <Layout maxWidth="7xl">
        <PageHeader
          icon="⚖️"
          title="Compare Resumes"
          subtitle="Side-by-side comparison of your resumes"
          breadcrumbs={[
            { label: 'Resumes', href: '/resumes' },
            { label: 'Compare' },
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

        {allResumes.length < 2 ? (
          <PageSection icon="📋" title="Need Multiple Resumes">
            <PageContainer variant="glass" className="text-center py-12">
              <p className="text-gray-600 mb-6">
                You need at least 2 resumes to compare them side-by-side.
              </p>
              <div className="flex gap-3 justify-center">
                <Button
                  onClick={() => router.push('/resumes/new')}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Create New Resume
                </Button>
                <Button
                  onClick={() => router.push('/resumes')}
                  variant="secondary"
                >
                  Back to Resumes
                </Button>
              </div>
            </PageContainer>
          </PageSection>
        ) : (
          <>
            {/* Resume Selection */}
            <PageSection icon="📝" title="Select Resumes to Compare">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-start">
                {/* Resume A */}
                <div className="bg-white rounded-lg border-2 border-blue-300 p-4">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Resume A</p>
                  <p className="font-semibold text-gray-900 mb-1">{resumeA?.title}</p>
                  <p className="text-xs text-gray-500">
                    {resumeA?.full_name && `${resumeA.full_name}`}
                  </p>
                </div>

                {/* Swap Button */}
                <div className="flex items-center justify-center">
                  <Button
                    onClick={swapResumes}
                    className="bg-purple-600 hover:bg-purple-700 text-white rounded-full p-3"
                    title="Swap resumes"
                  >
                    <RotateCw className="w-5 h-5" />
                  </Button>
                </div>

                {/* Resume B Selection */}
                <div className="bg-white rounded-lg border-2 border-orange-300 p-4">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Resume B</p>
                  <select
                    value={selectedResumeB || ''}
                    onChange={(e) => handleSelectResumeB(parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-sm"
                  >
                    <option value="">Select a resume...</option>
                    {allResumes
                      .filter((r) => r.id !== parseInt(id as string))
                      .map((resume) => (
                        <option key={resume.id} value={resume.id}>
                          {resume.title}
                        </option>
                      ))}
                  </select>
                  {resumeB && (
                    <p className="text-xs text-gray-500 mt-2">
                      {resumeB.full_name && `${resumeB.full_name}`}
                    </p>
                  )}
                </div>
              </div>
            </PageSection>

            {/* Comparison Table */}
            {resumeB && (
              <PageSection icon="📊" title="Detailed Comparison">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-gray-100 border-b-2 border-gray-300">
                        <th className="px-4 py-3 text-left font-semibold text-gray-900">Field</th>
                        <th className="px-4 py-3 text-left font-semibold text-blue-700">
                          Resume A: {resumeA?.title}
                        </th>
                        <th className="px-4 py-3 text-left font-semibold text-orange-700">
                          Resume B: {resumeB?.title}
                        </th>
                        <th className="px-4 py-3 text-center font-semibold text-gray-700">Match</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparisonFields.map((field) => {
                        const valA = getFieldValue(resumeA, field.key)
                        const valB = getFieldValue(resumeB, field.key)
                        const same = isSame(valA, valB)
                        const different = isDifferent(valA, valB)

                        return (
                          <tr key={field.key} className="border-b border-gray-200 hover:bg-gray-50">
                            <td className="px-4 py-3 font-semibold text-gray-900">{field.label}</td>
                            <td className={`px-4 py-3 text-sm ${same ? 'bg-green-50' : different ? 'bg-yellow-50' : ''}`}>
                              {valA}
                            </td>
                            <td className={`px-4 py-3 text-sm ${same ? 'bg-green-50' : different ? 'bg-yellow-50' : ''}`}>
                              {valB}
                            </td>
                            <td className="px-4 py-3 text-center">
                              {same ? (
                                <span className="text-green-600 font-semibold">✓</span>
                              ) : different ? (
                                <span className="text-yellow-600 font-semibold">≠</span>
                              ) : (
                                <span className="text-gray-400">-</span>
                              )}
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </PageSection>
            )}

            {/* Legend */}
            <PageSection icon="🔍" title="Legend">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm font-semibold text-green-900">✓ Same</p>
                  <p className="text-xs text-green-700">Both resumes have identical values</p>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm font-semibold text-yellow-900">≠ Different</p>
                  <p className="text-xs text-yellow-700">Resumes have different values</p>
                </div>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p className="text-sm font-semibold text-gray-900">- Missing</p>
                  <p className="text-xs text-gray-700">At least one resume is missing data</p>
                </div>
              </div>
            </PageSection>

            {/* Actions */}
            <div className="flex gap-3 mt-8">
              <Button
                onClick={() => router.push(`/resumes/${resumeA?.id}/edit`)}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                Edit Resume A
              </Button>
              {resumeB && (
                <Button
                  onClick={() => router.push(`/resumes/${resumeB?.id}/edit`)}
                  className="bg-orange-600 hover:bg-orange-700 text-white"
                >
                  Edit Resume B
                </Button>
              )}
              <Button
                onClick={() => router.push('/resumes')}
                variant="secondary"
              >
                Back to Resumes
              </Button>
            </div>
          </>
        )}
      </Layout>
    </>
  )
}

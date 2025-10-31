import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'

interface Resume {
  id: number
  title: string
  template: string
  full_name?: string
  email?: string
  phone?: string
  location?: string
  linkedin?: string
  github?: string
  website?: string
  professional_summary?: string
  work_experiences: any[]
  education: any[]
  skills: any[]
  projects: any[]
  certificates: any[]
  achievements: any[]
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

export default function ResumePreviewPage() {
  const router = useRouter()
  const { id } = router.query
  const [resume, setResume] = useState<Resume | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return

    const fetchResume = async () => {
      try {
        const token = document.cookie
          .split('; ')
          .find(row => row.startsWith('token='))
          ?.split('=')[1]

        const res = await fetch(`${API_BASE}/api/v1x/resumes/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        if (res.ok) {
          const data = await res.json()
          setResume(data)
        } else {
          console.error('Failed to load resume')
        }
      } catch (e) {
        console.error('Error loading resume:', e)
      } finally {
        setLoading(false)
      }
    }

    fetchResume()
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <p className="text-gray-600">Loading resume...</p>
      </div>
    )
  }

  if (!resume) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <p className="text-gray-600">Resume not found</p>
      </div>
    )
  }

  const template = resume.template || 'modern'

  return (
    <>
      <Head>
        <title>{resume.full_name || 'Resume'} - Preview</title>
      </Head>
      <div className="min-h-screen bg-gray-100 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Print Controls */}
          <div className="mb-4 flex justify-end gap-3 print:hidden">
            <button
              onClick={() => router.back()}
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              ← Back to Editor
            </button>
            <button
              onClick={() => window.print()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              🖨️ Print / Save as PDF
            </button>
          </div>

          {/* Resume Container - Print optimized */}
          <div
            id="resume-content"
            className="bg-white shadow-lg print:shadow-none"
            style={{ minHeight: '297mm' }}
          >
            {template === 'modern' && <ModernTemplate resume={resume} />}
            {template === 'classic' && <ClassicTemplate resume={resume} />}
            {template === 'minimal' && <MinimalTemplate resume={resume} />}
            {template === 'creative' && <CreativeTemplate resume={resume} />}
          </div>
        </div>
      </div>

      <style jsx global>{`
        @media print {
          body {
            margin: 0;
            padding: 0;
          }
          @page {
            size: A4;
            margin: 0;
          }
          #resume-content {
            width: 210mm;
            min-height: 297mm;
            margin: 0 auto;
            box-shadow: none !important;
          }
        }
      `}</style>
    </>
  )
}

// Modern Template
function ModernTemplate({ resume }: { resume: Resume }) {
  return (
    <div className="p-12 text-gray-900">
      {/* Header */}
      <header className="border-b-2 border-blue-600 pb-6 mb-6">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          {resume.full_name || 'Your Name'}
        </h1>
        <div className="flex flex-wrap gap-4 text-sm text-gray-600">
          {resume.email && <span>📧 {resume.email}</span>}
          {resume.phone && <span>📱 {resume.phone}</span>}
          {resume.location && <span>📍 {resume.location}</span>}
        </div>
        <div className="flex flex-wrap gap-4 text-sm text-blue-600 mt-2">
          {resume.linkedin && (
            <a href={resume.linkedin} className="hover:underline">
              LinkedIn
            </a>
          )}
          {resume.github && (
            <a href={resume.github} className="hover:underline">
              GitHub
            </a>
          )}
          {resume.website && (
            <a href={resume.website} className="hover:underline">
              Website
            </a>
          )}
        </div>
      </header>

      {/* Professional Summary */}
      {resume.professional_summary && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide">
            Professional Summary
          </h2>
          <p className="text-gray-700 leading-relaxed">{resume.professional_summary}</p>
        </section>
      )}

      {/* Work Experience */}
      {resume.work_experiences?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide">
            Work Experience
          </h2>
          {resume.work_experiences.map((exp: any, idx: number) => (
            <div key={idx} className="mb-4">
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="text-lg font-semibold text-gray-900">{exp.position}</h3>
                <span className="text-sm text-gray-600">
                  {exp.start_date} - {exp.is_current ? 'Present' : exp.end_date}
                </span>
              </div>
              <p className="text-md font-medium text-gray-700 mb-2">
                {exp.company} {exp.location && `• ${exp.location}`}
              </p>
              {exp.responsibilities?.length > 0 && (
                <ul className="list-disc pl-5 space-y-1">
                  {exp.responsibilities.map((resp: string, i: number) => (
                    <li key={i} className="text-gray-700">
                      {resp}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Education */}
      {resume.education?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide">
            Education
          </h2>
          {resume.education.map((edu: any, idx: number) => (
            <div key={idx} className="mb-3">
              <div className="flex justify-between items-baseline">
                <h3 className="text-lg font-semibold text-gray-900">
                  {edu.degree} in {edu.field_of_study}
                </h3>
                <span className="text-sm text-gray-600">
                  {edu.start_date} - {edu.is_current ? 'Present' : edu.end_date}
                </span>
              </div>
              <p className="text-md font-medium text-gray-700">{edu.school}</p>
              {edu.gpa && <p className="text-sm text-gray-600">GPA: {edu.gpa}</p>}
              {edu.achievements?.length > 0 && (
                <ul className="list-disc pl-5 mt-1">
                  {edu.achievements.map((ach: string, i: number) => (
                    <li key={i} className="text-sm text-gray-700">
                      {ach}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Skills */}
      {resume.skills?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide">
            Skills
          </h2>
          <div className="flex flex-wrap gap-2">
            {resume.skills.map((skill: any, idx: number) => (
              <span
                key={idx}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
              >
                {skill.name}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Projects */}
      {resume.projects?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide">
            Projects
          </h2>
          {resume.projects.map((proj: any, idx: number) => (
            <div key={idx} className="mb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">{proj.name}</h3>
              <p className="text-gray-700 mb-2">{proj.description}</p>
              {proj.tech_stack?.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {proj.tech_stack.map((tech: string, i: number) => (
                    <span key={i} className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs">
                      {tech}
                    </span>
                  ))}
                </div>
              )}
              <div className="flex gap-3 text-sm text-blue-600">
                {proj.github_url && <a href={proj.github_url}>GitHub</a>}
                {proj.live_url && <a href={proj.live_url}>Live Demo</a>}
              </div>
            </div>
          ))}
        </section>
      )}

      {/* Certificates */}
      {resume.certificates?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide">
            Certificates
          </h2>
          {resume.certificates.map((cert: any, idx: number) => (
            <div key={idx} className="mb-2">
              <h3 className="font-semibold text-gray-900">{cert.name}</h3>
              <p className="text-sm text-gray-700">
                {cert.issuer} • {cert.issue_date}
              </p>
            </div>
          ))}
        </section>
      )}

      {/* Achievements */}
      {resume.achievements?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide">
            Achievements
          </h2>
          <ul className="list-disc pl-5 space-y-1">
            {resume.achievements.map((ach: any, idx: number) => (
              <li key={idx} className="text-gray-700">
                <strong>{ach.title}</strong>: {ach.description}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}

// Classic Template
function ClassicTemplate({ resume }: { resume: Resume }) {
  return (
    <div className="p-12 font-serif text-gray-900">
      <header className="text-center border-b-2 border-gray-800 pb-4 mb-6">
        <h1 className="text-4xl font-bold mb-2">{resume.full_name || 'Your Name'}</h1>
        <div className="text-sm text-gray-600 space-x-3">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>•</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.location && <span>•</span>}
          {resume.location && <span>{resume.location}</span>}
        </div>
      </header>
      {/* Reuse similar sections as Modern but with serif font and centered header */}
      <ModernTemplate resume={resume} />
    </div>
  )
}

// Minimal Template
function MinimalTemplate({ resume }: { resume: Resume }) {
  return (
    <div className="p-16 text-gray-900">
      <header className="mb-8">
        <h1 className="text-5xl font-light tracking-tight mb-4">
          {resume.full_name || 'Your Name'}
        </h1>
        <div className="text-sm text-gray-600 space-x-4">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.location && <span>{resume.location}</span>}
        </div>
      </header>
      <ModernTemplate resume={resume} />
    </div>
  )
}

// Creative Template
function CreativeTemplate({ resume }: { resume: Resume }) {
  return (
    <div className="text-gray-900">
      <header className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-12">
        <h1 className="text-4xl font-bold mb-2">{resume.full_name || 'Your Name'}</h1>
        <div className="text-sm space-x-3">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>• {resume.phone}</span>}
          {resume.location && <span>• {resume.location}</span>}
        </div>
      </header>
      <div className="p-12">
        <ModernTemplate resume={resume} />
      </div>
    </div>
  )
}

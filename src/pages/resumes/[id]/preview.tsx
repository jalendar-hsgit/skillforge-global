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
        // Use Next.js proxy so HttpOnly cookie is forwarded automatically
        const res = await fetch(`/api/session/resumes?id=${id}`, {
          credentials: 'include',
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
        {/* Professional fonts for screen and print */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap"
          rel="stylesheet"
        />
      </Head>
      <div className="min-h-screen bg-gray-100 py-8 print:p-0 print:bg-white">
        <div className="max-w-4xl mx-auto print:max-w-none">
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
            className="bg-white shadow-xl print:shadow-none rounded-lg print:rounded-none overflow-hidden"
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
          * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            color-adjust: exact !important;
          }
          
          html, body {
            margin: 0 !important;
            padding: 0 !important;
            background: white !important;
            width: 210mm;
            height: 297mm;
          }
          
          @page {
            size: A4 portrait;
            margin: 0mm;
          }
          
          body > div:first-child {
            margin: 0 !important;
            padding: 0 !important;
            background: white !important;
          }
          
          #resume-content {
            width: 210mm !important;
            max-width: 210mm !important;
            min-height: auto !important;
            margin: 0 !important;
            padding: 0 !important;
            box-shadow: none !important;
            border-radius: 0 !important;
            background: white !important;
          }
          
          /* Allow natural page breaks for multi-page content */
          #resume-content > div {
            page-break-after: auto;
          }
          
          /* Avoid breaking inside important elements */
          #resume-content section {
            page-break-inside: avoid;
            break-inside: avoid;
          }
          
          #resume-content h2 {
            page-break-after: avoid;
            break-after: avoid;
          }
          
          #resume-content ul, #resume-content ol {
            page-break-inside: avoid;
            break-inside: avoid;
          }
          
          /* Ensure links are visible in print */
          #resume-content a {
            text-decoration: underline;
            color: #2563eb !important;
          }
          
          /* Hide screen-only elements */
          .print\\:hidden {
            display: none !important;
          }
        }
        
        /* Screen + Print: base typography */
        #resume-content { 
          font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
          line-height: 1.6;
        }
        
        #resume-content .font-serif { 
          font-family: "Source Serif 4", ui-serif, Georgia, Cambria, "Times New Roman", Times, serif; 
        }
        
        /* Ensure gradient backgrounds render crisply */
        #resume-content .bg-gradient-to-r, 
        #resume-content .bg-gradient-to-br,
        #resume-content header,
        #resume-content [style*="printColorAdjust"] {
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
          color-adjust: exact;
        }
        
        /* Better text rendering */
        #resume-content {
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
          text-rendering: optimizeLegibility;
        }
        
        /* Section headers with subtle shadow */
        #resume-content h2 {
          filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.05));
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
      <header className="border-b-4 border-blue-600 pb-6 mb-8 bg-gradient-to-r from-blue-50 via-blue-50 to-transparent" style={{ printColorAdjust: 'exact', WebkitPrintColorAdjust: 'exact' }}>
        <h1 className="text-5xl font-bold text-gray-900 mb-3 tracking-tight" style={{ textShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
          {resume.full_name || 'Your Name'}
        </h1>
        <div className="flex flex-wrap gap-x-5 gap-y-2 text-sm text-gray-700 font-medium">
          {resume.email && (
            <span className="flex items-center gap-1.5">
              <span className="text-blue-600">📧</span> {resume.email}
            </span>
          )}
          {resume.phone && (
            <span className="flex items-center gap-1.5">
              <span className="text-blue-600">📱</span> {resume.phone}
            </span>
          )}
          {resume.location && (
            <span className="flex items-center gap-1.5">
              <span className="text-blue-600">📍</span> {resume.location}
            </span>
          )}
        </div>
        {(resume.linkedin || resume.github || resume.website) && (
          <div className="flex flex-wrap gap-4 text-sm text-blue-600 mt-3 font-medium">
            {resume.linkedin && (
              <a href={resume.linkedin} className="hover:underline flex items-center gap-1">
                <span>🔗</span> LinkedIn
              </a>
            )}
            {resume.github && (
              <a href={resume.github} className="hover:underline flex items-center gap-1">
                <span>💻</span> GitHub
              </a>
            )}
            {resume.website && (
              <a href={resume.website} className="hover:underline flex items-center gap-1">
                <span>🌐</span> Website
              </a>
            )}
          </div>
        )}
      </header>

      {/* Professional Summary */}
      {resume.professional_summary && (
        <section className="mb-8">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide border-b-2 border-blue-600 pb-1" style={{ textShadow: '0 1px 2px rgba(37,99,235,0.1)' }}>
            Professional Summary
          </h2>
          <p className="text-gray-800 leading-relaxed text-base">{resume.professional_summary}</p>
        </section>
      )}

      {/* Work Experience */}
      {resume.work_experiences?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide border-b-2 border-blue-600 pb-1">
            Work Experience
          </h2>
          {resume.work_experiences.map((exp: any, idx: number) => (
            <div key={idx} className="mb-4 last:mb-0">
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="text-lg font-semibold text-gray-900">{exp.position || 'Position'}</h3>
                <span className="text-sm text-gray-600 whitespace-nowrap ml-4">
                  {exp.start_date || ''} {exp.start_date && '-'} {exp.is_current ? 'Present' : (exp.end_date || '')}
                </span>
              </div>
              <p className="text-md font-medium text-gray-700 mb-2">
                {exp.company || 'Company'} {exp.location && `• ${exp.location}`}
              </p>
              {(exp.responsibilities?.length || exp.bullet_points?.length) && (
                <ul className="list-disc pl-5 space-y-1 text-sm">
                  {(exp.bullet_points || exp.responsibilities || []).map((resp: string, i: number) => (
                    <li key={i} className="text-gray-700 leading-relaxed">
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
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide border-b-2 border-blue-600 pb-1">
            Education
          </h2>
          {resume.education.map((edu: any, idx: number) => (
            <div key={idx} className="mb-3 last:mb-0">
              <div className="flex justify-between items-baseline">
                <h3 className="text-lg font-semibold text-gray-900">
                  {edu.degree || 'Degree'} {edu.field_of_study && `in ${edu.field_of_study}`}
                </h3>
                <span className="text-sm text-gray-600 whitespace-nowrap ml-4">
                  {edu.start_date || ''} {edu.start_date && '-'} {edu.is_current ? 'Present' : (edu.end_date || '')}
                </span>
              </div>
              <p className="text-md font-medium text-gray-700">{edu.institution || edu.school || 'Institution'}</p>
              {edu.gpa && <p className="text-sm text-gray-600">GPA: {edu.gpa}</p>}
              {edu.achievements?.length > 0 && (
                <ul className="list-disc pl-5 mt-1 space-y-0.5">
                  {edu.achievements.filter((a: string) => a && a.trim()).map((ach: string, i: number) => (
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
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide border-b-2 border-blue-600 pb-1">
            Skills
          </h2>
          <div className="flex flex-wrap gap-2">
            {resume.skills.map((skill: any, idx: number) => (
              <span
                key={idx}
                className="px-3 py-1.5 bg-blue-100 text-blue-900 rounded-md text-sm font-medium shadow-sm"
                style={{ printColorAdjust: 'exact', WebkitPrintColorAdjust: 'exact' }}
              >
                {skill.name || 'Skill'}
                {skill.proficiency && (
                  <span className="ml-1.5 text-xs opacity-75">• {skill.proficiency}</span>
                )}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Projects */}
      {resume.projects?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide border-b-2 border-blue-600 pb-1">
            Projects
          </h2>
          {resume.projects.map((proj: any, idx: number) => (
            <div key={idx} className="mb-4 last:mb-0">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">{proj.title || proj.name || 'Project'}</h3>
              {proj.description && <p className="text-gray-700 mb-2 text-sm leading-relaxed">{proj.description}</p>}
              {proj.tech_stack?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {proj.tech_stack.filter((t: string) => t && t.trim()).map((tech: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-200 text-gray-800 rounded text-xs font-medium">
                      {tech}
                    </span>
                  ))}
                </div>
              )}
              {(proj.github_url || proj.demo_url || proj.live_url) && (
                <div className="flex gap-3 text-sm text-blue-600 font-medium">
                  {proj.github_url && <a href={proj.github_url} className="hover:underline">🔗 GitHub</a>}
                  {(proj.demo_url || proj.live_url) && <a href={proj.demo_url || proj.live_url} className="hover:underline">🌐 Live Demo</a>}
                </div>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Certificates */}
      {resume.certificates?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide border-b-2 border-blue-600 pb-1">
            Certificates
          </h2>
          {resume.certificates.map((cert: any, idx: number) => (
            <div key={idx} className="mb-2 last:mb-0">
              <h3 className="font-semibold text-gray-900">{cert.name || 'Certificate'}</h3>
              <p className="text-sm text-gray-700">
                {(cert.issuing_organization || cert.issuer) ? `${cert.issuing_organization || cert.issuer}` : 'Issuer'}
                {(cert.issue_date || cert.date) ? ` • ${cert.issue_date || cert.date}` : ''}
              </p>
              {cert.credential_id && <p className="text-xs text-gray-500 mt-0.5">ID: {cert.credential_id}</p>}
              {cert.credential_url && (
                <a href={cert.credential_url} className="text-xs text-blue-600 hover:underline">
                  View Credential →
                </a>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Achievements */}
      {resume.achievements?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold text-blue-600 mb-3 uppercase tracking-wide border-b-2 border-blue-600 pb-1">
            Achievements
          </h2>
          <ul className="list-disc pl-5 space-y-1.5">
            {resume.achievements.map((ach: any, idx: number) => (
              <li key={idx} className="text-gray-700 text-sm leading-relaxed">
                <strong className="text-gray-900">{ach.title || 'Achievement'}</strong>
                {ach.date && <span className="text-gray-600"> ({ach.date})</span>}
                {ach.issuer && <span className="text-gray-600"> • {ach.issuer}</span>}
                {ach.description && <span>: {ach.description}</span>}
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
    <div className="p-16 font-serif text-gray-900">
      <header className="text-center border-b-2 border-gray-800 pb-6 mb-8">
        <h1 className="text-5xl font-bold mb-3 tracking-tight">{resume.full_name || 'Your Name'}</h1>
        <div className="text-sm text-gray-700 space-x-2 font-sans">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && resume.email && <span>•</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.location && (resume.email || resume.phone) && <span>•</span>}
          {resume.location && <span>{resume.location}</span>}
        </div>
        {(resume.linkedin || resume.github || resume.website) && (
          <div className="text-sm text-gray-600 mt-2 space-x-2 font-sans">
            {resume.linkedin && <a href={resume.linkedin} className="hover:underline">LinkedIn</a>}
            {resume.github && (resume.linkedin && <span>•</span>)}
            {resume.github && <a href={resume.github} className="hover:underline">GitHub</a>}
            {resume.website && ((resume.linkedin || resume.github) && <span>•</span>)}
            {resume.website && <a href={resume.website} className="hover:underline">Website</a>}
          </div>
        )}
      </header>

      {resume.professional_summary && (
        <section className="mb-6 text-center">
          <h2 className="text-lg font-bold text-gray-800 mb-3 uppercase tracking-widest">Summary</h2>
          <p className="text-gray-700 leading-relaxed max-w-3xl mx-auto">{resume.professional_summary}</p>
        </section>
      )}

      {resume.work_experiences?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4 uppercase tracking-widest text-center border-b border-gray-300 pb-2">Experience</h2>
          {resume.work_experiences.map((exp: any, idx: number) => (
            <div key={idx} className="mb-4 last:mb-0">
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="text-base font-bold text-gray-900">{exp.position || 'Position'}</h3>
                <span className="text-sm text-gray-600 font-sans whitespace-nowrap ml-4">
                  {exp.start_date || ''} {exp.start_date && '—'} {exp.is_current ? 'Present' : (exp.end_date || '')}
                </span>
              </div>
              <p className="text-sm italic text-gray-700 mb-2">
                {exp.company || 'Company'}{exp.location && `, ${exp.location}`}
              </p>
              {(exp.bullet_points?.length || exp.responsibilities?.length) && (
                <ul className="list-disc pl-6 space-y-1 text-sm font-sans">
                  {(exp.bullet_points || exp.responsibilities || []).map((resp: string, i: number) => (
                    <li key={i} className="text-gray-700 leading-relaxed">{resp}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </section>
      )}

      {resume.education?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4 uppercase tracking-widest text-center border-b border-gray-300 pb-2">Education</h2>
          {resume.education.map((edu: any, idx: number) => (
            <div key={idx} className="mb-3 last:mb-0">
              <div className="flex justify-between items-baseline">
                <h3 className="text-base font-bold text-gray-900">
                  {edu.degree || 'Degree'} {edu.field_of_study && `in ${edu.field_of_study}`}
                </h3>
                <span className="text-sm text-gray-600 font-sans whitespace-nowrap ml-4">
                  {edu.start_date || ''} {edu.start_date && '—'} {edu.is_current ? 'Present' : (edu.end_date || '')}
                </span>
              </div>
              <p className="text-sm italic text-gray-700">{edu.institution || edu.school || 'Institution'}</p>
              {edu.gpa && <p className="text-sm text-gray-600 font-sans">GPA: {edu.gpa}</p>}
              {edu.achievements?.length > 0 && (
                <ul className="list-disc pl-6 mt-1 text-sm font-sans">
                  {edu.achievements.filter((a: string) => a && a.trim()).map((ach: string, i: number) => (
                    <li key={i} className="text-gray-700">{ach}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </section>
      )}

      {resume.skills?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4 uppercase tracking-widest text-center border-b border-gray-300 pb-2">Skills</h2>
          <div className="text-center font-sans text-sm text-gray-800 leading-relaxed">
            {resume.skills.map((skill: any, idx: number) => (
              <span key={idx}>
                {skill.name || 'Skill'}
                {skill.proficiency && ` (${skill.proficiency})`}
                {idx < resume.skills.length - 1 && ' • '}
              </span>
            ))}
          </div>
        </section>
      )}

      {resume.projects?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4 uppercase tracking-widest text-center border-b border-gray-300 pb-2">Projects</h2>
          {resume.projects.map((proj: any, idx: number) => (
            <div key={idx} className="mb-3 last:mb-0">
              <h3 className="text-base font-bold text-gray-900 mb-1">{proj.title || proj.name || 'Project'}</h3>
              {proj.description && <p className="text-sm text-gray-700 leading-relaxed mb-1 font-sans">{proj.description}</p>}
              {proj.tech_stack?.length > 0 && (
                <p className="text-xs text-gray-600 italic font-sans">
                  Technologies: {proj.tech_stack.filter((t: string) => t && t.trim()).join(', ')}
                </p>
              )}
            </div>
          ))}
        </section>
      )}

      {resume.certificates?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4 uppercase tracking-widest text-center border-b border-gray-300 pb-2">Certificates</h2>
          {resume.certificates.map((cert: any, idx: number) => (
            <div key={idx} className="mb-2 last:mb-0">
              <h3 className="font-bold text-gray-900 text-sm">{cert.name || 'Certificate'}</h3>
              <p className="text-sm text-gray-700 font-sans">
                {(cert.issuing_organization || cert.issuer) || 'Issuer'}
                {(cert.issue_date || cert.date) ? ` • ${cert.issue_date || cert.date}` : ''}
              </p>
            </div>
          ))}
        </section>
      )}

      {resume.achievements?.length > 0 && (
        <section className="mb-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4 uppercase tracking-widest text-center border-b border-gray-300 pb-2">Achievements</h2>
          <ul className="list-disc pl-6 space-y-1 text-sm font-sans">
            {resume.achievements.map((ach: any, idx: number) => (
              <li key={idx} className="text-gray-700 leading-relaxed">
                <strong>{ach.title || 'Achievement'}</strong>
                {ach.date && ` (${ach.date})`}
                {ach.issuer && ` • ${ach.issuer}`}
                {ach.description && `: ${ach.description}`}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}

// Minimal Template
function MinimalTemplate({ resume }: { resume: Resume }) {
  return (
    <div className="p-16 text-gray-900">
      <header className="mb-10">
        <h1 className="text-6xl font-light tracking-tight mb-4 text-gray-900">
          {resume.full_name || 'Your Name'}
        </h1>
        <div className="text-sm text-gray-600 space-x-4 font-light">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && resume.email && <span>•</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.location && (resume.email || resume.phone) && <span>•</span>}
          {resume.location && <span>{resume.location}</span>}
        </div>
        {(resume.linkedin || resume.github || resume.website) && (
          <div className="text-sm text-gray-500 mt-2 space-x-3 font-light">
            {resume.linkedin && <a href={resume.linkedin} className="hover:underline">LinkedIn</a>}
            {resume.github && <a href={resume.github} className="hover:underline">GitHub</a>}
            {resume.website && <a href={resume.website} className="hover:underline">Website</a>}
          </div>
        )}
      </header>

      {resume.professional_summary && (
        <section className="mb-8">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Summary</h2>
          <p className="text-gray-800 leading-relaxed font-light">{resume.professional_summary}</p>
        </section>
      )}

      {resume.work_experiences?.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">Experience</h2>
          {resume.work_experiences.map((exp: any, idx: number) => (
            <div key={idx} className="mb-5 last:mb-0">
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="text-lg font-medium text-gray-900">{exp.position || 'Position'}</h3>
                <span className="text-xs text-gray-500 whitespace-nowrap ml-4 font-light">
                  {exp.start_date || ''} {exp.start_date && '—'} {exp.is_current ? 'Present' : (exp.end_date || '')}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2 font-light">
                {exp.company || 'Company'}{exp.location && ` • ${exp.location}`}
              </p>
              {(exp.bullet_points?.length || exp.responsibilities?.length) && (
                <ul className="space-y-1 text-sm font-light">
                  {(exp.bullet_points || exp.responsibilities || []).map((resp: string, i: number) => (
                    <li key={i} className="text-gray-700 leading-relaxed pl-4 relative before:content-['—'] before:absolute before:left-0">{resp}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </section>
      )}

      {resume.education?.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">Education</h2>
          {resume.education.map((edu: any, idx: number) => (
            <div key={idx} className="mb-4 last:mb-0">
              <div className="flex justify-between items-baseline">
                <h3 className="text-base font-medium text-gray-900">
                  {edu.degree || 'Degree'} {edu.field_of_study && `in ${edu.field_of_study}`}
                </h3>
                <span className="text-xs text-gray-500 whitespace-nowrap ml-4 font-light">
                  {edu.start_date || ''} {edu.start_date && '—'} {edu.is_current ? 'Present' : (edu.end_date || '')}
                </span>
              </div>
              <p className="text-sm text-gray-600 font-light">{edu.institution || edu.school || 'Institution'}</p>
            </div>
          ))}
        </section>
      )}

      {resume.skills?.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Skills</h2>
          <div className="text-sm text-gray-700 font-light">
            {resume.skills.map((s: any, idx: number) => s.name || 'Skill').join(' • ')}
          </div>
        </section>
      )}

      {resume.projects?.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">Projects</h2>
          {resume.projects.map((proj: any, idx: number) => (
            <div key={idx} className="mb-3 last:mb-0">
              <h3 className="text-base font-medium text-gray-900 mb-1">{proj.title || proj.name || 'Project'}</h3>
              {proj.description && <p className="text-sm text-gray-700 font-light leading-relaxed">{proj.description}</p>}
            </div>
          ))}
        </section>
      )}

      {resume.certificates?.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Certificates</h2>
          {resume.certificates.map((cert: any, idx: number) => (
            <div key={idx} className="mb-2 last:mb-0 text-sm">
              <span className="font-medium text-gray-900">{cert.name || 'Certificate'}</span>
              <span className="text-gray-600 font-light">
                {' • '}{(cert.issuing_organization || cert.issuer) || 'Issuer'}
                {(cert.issue_date || cert.date) ? ` • ${cert.issue_date || cert.date}` : ''}
              </span>
            </div>
          ))}
        </section>
      )}

      {resume.achievements?.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Achievements</h2>
          <ul className="space-y-1 text-sm font-light">
            {resume.achievements.map((ach: any, idx: number) => (
              <li key={idx} className="text-gray-700 pl-4 relative before:content-['—'] before:absolute before:left-0">
                <strong className="font-medium">{ach.title || 'Achievement'}</strong>
                {ach.date && ` (${ach.date})`}
                {ach.description && `: ${ach.description}`}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}

// Creative Template
function CreativeTemplate({ resume }: { resume: Resume }) {
  return (
    <div className="text-gray-900">
      <header 
        className="bg-gradient-to-r from-purple-600 via-pink-500 to-blue-600 text-white p-12" 
        style={{ printColorAdjust: 'exact', WebkitPrintColorAdjust: 'exact' }}
      >
        <h1 className="text-5xl font-bold mb-3 tracking-tight" style={{ textShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>
          {resume.full_name || 'Your Name'}
        </h1>
        <div className="text-sm space-x-4 opacity-95 font-medium">
          {resume.email && <span>📧 {resume.email}</span>}
          {resume.phone && <span>📱 {resume.phone}</span>}
          {resume.location && <span>📍 {resume.location}</span>}
        </div>
        {(resume.linkedin || resume.github || resume.website) && (
          <div className="text-sm mt-3 space-x-3 opacity-90">
            {resume.linkedin && <a href={resume.linkedin} className="hover:underline">🔗 LinkedIn</a>}
            {resume.github && <a href={resume.github} className="hover:underline">💻 GitHub</a>}
            {resume.website && <a href={resume.website} className="hover:underline">🌐 Website</a>}
          </div>
        )}
      </header>
      <div className="p-12">
        {resume.professional_summary && (
          <section className="mb-6">
            <h2 className="text-xl font-bold text-purple-600 mb-3 uppercase tracking-wide border-l-4 border-purple-600 pl-3">
              Professional Summary
            </h2>
            <p className="text-gray-800 leading-relaxed">{resume.professional_summary}</p>
          </section>
        )}

        {resume.work_experiences?.length > 0 && (
          <section className="mb-6">
            <h2 className="text-xl font-bold text-purple-600 mb-3 uppercase tracking-wide border-l-4 border-purple-600 pl-3">
              Work Experience
            </h2>
            {resume.work_experiences.map((exp: any, idx: number) => (
              <div key={idx} className="mb-4 last:mb-0 pl-4 border-l-2 border-gray-200">
                <div className="flex justify-between items-baseline mb-1">
                  <h3 className="text-lg font-semibold text-gray-900">{exp.position || 'Position'}</h3>
                  <span className="text-sm text-gray-600 whitespace-nowrap ml-4">
                    {exp.start_date || ''} {exp.start_date && '—'} {exp.is_current ? 'Present' : (exp.end_date || '')}
                  </span>
                </div>
                <p className="text-md font-medium text-gray-700 mb-2">
                  {exp.company || 'Company'}{exp.location && ` • ${exp.location}`}
                </p>
                {(exp.bullet_points?.length || exp.responsibilities?.length) && (
                  <ul className="list-disc pl-5 space-y-1 text-sm">
                    {(exp.bullet_points || exp.responsibilities || []).map((resp: string, i: number) => (
                      <li key={i} className="text-gray-700 leading-relaxed">{resp}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </section>
        )}

        {resume.education?.length > 0 && (
          <section className="mb-6">
            <h2 className="text-xl font-bold text-purple-600 mb-3 uppercase tracking-wide border-l-4 border-purple-600 pl-3">
              Education
            </h2>
            {resume.education.map((edu: any, idx: number) => (
              <div key={idx} className="mb-3 last:mb-0 pl-4">
                <div className="flex justify-between items-baseline">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {edu.degree || 'Degree'} {edu.field_of_study && `in ${edu.field_of_study}`}
                  </h3>
                  <span className="text-sm text-gray-600 whitespace-nowrap ml-4">
                    {edu.start_date || ''} {edu.start_date && '—'} {edu.is_current ? 'Present' : (edu.end_date || '')}
                  </span>
                </div>
                <p className="text-md font-medium text-gray-700">{edu.institution || edu.school || 'Institution'}</p>
              </div>
            ))}
          </section>
        )}

        {resume.skills?.length > 0 && (
          <section className="mb-6">
            <h2 className="text-xl font-bold text-purple-600 mb-3 uppercase tracking-wide border-l-4 border-purple-600 pl-3">
              Skills
            </h2>
            <div className="flex flex-wrap gap-2 pl-4">
              {resume.skills.map((skill: any, idx: number) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 bg-gradient-to-r from-purple-100 to-blue-100 text-purple-900 rounded-full text-sm font-medium shadow-sm"
                  style={{ printColorAdjust: 'exact', WebkitPrintColorAdjust: 'exact' }}
                >
                  {skill.name || 'Skill'}
                </span>
              ))}
            </div>
          </section>
        )}

        {resume.projects?.length > 0 && (
          <section className="mb-6">
            <h2 className="text-xl font-bold text-purple-600 mb-3 uppercase tracking-wide border-l-4 border-purple-600 pl-3">
              Projects
            </h2>
            {resume.projects.map((proj: any, idx: number) => (
              <div key={idx} className="mb-4 last:mb-0 pl-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{proj.title || proj.name || 'Project'}</h3>
                {proj.description && <p className="text-gray-700 mb-2 text-sm leading-relaxed">{proj.description}</p>}
                {proj.tech_stack?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    {proj.tech_stack.filter((t: string) => t && t.trim()).map((tech: string, i: number) => (
                      <span key={i} className="px-2 py-0.5 bg-gray-200 text-gray-800 rounded text-xs">{tech}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </section>
        )}

        {resume.certificates?.length > 0 && (
          <section className="mb-6">
            <h2 className="text-xl font-bold text-purple-600 mb-3 uppercase tracking-wide border-l-4 border-purple-600 pl-3">
              Certificates
            </h2>
            {resume.certificates.map((cert: any, idx: number) => (
              <div key={idx} className="mb-2 last:mb-0 pl-4">
                <h3 className="font-semibold text-gray-900">{cert.name || 'Certificate'}</h3>
                <p className="text-sm text-gray-700">
                  {(cert.issuing_organization || cert.issuer) || 'Issuer'}
                  {(cert.issue_date || cert.date) ? ` • ${cert.issue_date || cert.date}` : ''}
                </p>
              </div>
            ))}
          </section>
        )}

        {resume.achievements?.length > 0 && (
          <section className="mb-6">
            <h2 className="text-xl font-bold text-purple-600 mb-3 uppercase tracking-wide border-l-4 border-purple-600 pl-3">
              Achievements
            </h2>
            <ul className="list-disc pl-9 space-y-1.5">
              {resume.achievements.map((ach: any, idx: number) => (
                <li key={idx} className="text-gray-700 text-sm leading-relaxed">
                  <strong className="text-gray-900">{ach.title || 'Achievement'}</strong>
                  {ach.date && ` (${ach.date})`}
                  {ach.description && `: ${ach.description}`}
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  )
}

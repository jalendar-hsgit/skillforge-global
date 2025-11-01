import { Card } from '@/components/Card'

interface ResumePreviewProps {
  resume: {
    full_name?: string
    email?: string
    phone?: string
    location?: string
    linkedin?: string
    github?: string
    website?: string
    professional_summary?: string
    template: string
    work_experiences: any[]
    education: any[]
    skills: any[]
    projects: any[]
    certificates: any[]
    achievements: any[]
  }
}

export default function ResumePreview({ resume }: ResumePreviewProps) {
  // Simple preview that adapts lightly by template; full templates can be expanded later
  const template = resume.template || 'modern'

  return (
    <div className="bg-white text-gray-900 rounded-lg overflow-hidden border shadow">
      {/* Header */}
      <div className={
        template === 'classic'
          ? 'px-4 py-3 border-b bg-gray-50'
          : template === 'creative'
          ? 'px-4 py-3 border-b bg-gradient-to-r from-indigo-600 to-purple-600 text-white'
          : 'px-4 py-3 border-b bg-white'
      }>
        <h2 className={
          template === 'classic' ? 'text-xl font-serif font-bold' : 'text-xl font-bold'
        }>
          {resume.full_name || 'Your Name'}
        </h2>
        <p className="text-xs opacity-80">
          {(resume.email || 'email@example.com') + ' • ' + (resume.phone || '000-000-0000')}
        </p>
      </div>

      {/* Body */}
      <div className="p-4 space-y-3 text-xs">
        {resume.professional_summary && (
          <section>
            <h3 className="font-semibold mb-1">Summary</h3>
            <p className="leading-relaxed">{resume.professional_summary}</p>
          </section>
        )}

        {Array.isArray(resume.work_experiences) && resume.work_experiences.length > 0 && (
          <section>
            <h3 className="font-semibold mb-1">Experience</h3>
            <ul className="space-y-1">
              {resume.work_experiences.slice(0, 2).map((exp: any, idx: number) => (
                <li key={idx}>
                  <div className="font-medium">{exp.position || 'Role'} • {exp.company || 'Company'}</div>
                  {((exp.responsibilities && exp.responsibilities.length) || (exp.bullet_points && exp.bullet_points.length)) && (
                    <ul className="list-disc pl-5">
                      {(exp.responsibilities || exp.bullet_points || []).slice(0, 2).map((r: string, i: number) => (
                        <li key={i}>{r}</li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}

        {Array.isArray(resume.education) && resume.education.length > 0 && (
          <section>
            <h3 className="font-semibold mb-1">Education</h3>
            <ul className="space-y-1">
              {resume.education.slice(0, 2).map((edu: any, idx: number) => (
                <li key={idx}>
                  <div className="font-medium">{edu.degree || 'Degree'} in {edu.field_of_study || 'Field'} • {edu.institution || edu.school || 'Institution'}</div>
                </li>
              ))}
            </ul>
          </section>
        )}

        {Array.isArray(resume.skills) && resume.skills.length > 0 && (
          <section>
            <h3 className="font-semibold mb-1">Skills</h3>
            <div className="flex flex-wrap gap-1">
              {resume.skills.slice(0, 8).map((s: any, idx: number) => (
                <span key={idx} className="px-2 py-0.5 bg-gray-100 rounded-full">{s.name || 'Skill'}</span>
              ))}
            </div>
          </section>
        )}

        {Array.isArray(resume.projects) && resume.projects.length > 0 && (
          <section>
            <h3 className="font-semibold mb-1">Projects</h3>
            <ul className="space-y-1">
              {resume.projects.slice(0, 2).map((p: any, idx: number) => (
                <li key={idx}>
                  <div className="font-medium">{p.title || p.name || 'Project'}</div>
                  {p.description && <p className="text-[11px] text-gray-600">{p.description}</p>}
                </li>
              ))}
            </ul>
          </section>
        )}

        {Array.isArray(resume.certificates) && resume.certificates.length > 0 && (
          <section>
            <h3 className="font-semibold mb-1">Certificates</h3>
            <ul className="space-y-1">
              {resume.certificates.slice(0, 2).map((c: any, idx: number) => (
                <li key={idx}>
                  <div className="font-medium">{c.name || 'Certificate'}</div>
                  <div className="text-[11px] text-gray-600">{c.issuing_organization || c.issuer || 'Issuer'}{(c.issue_date || c.date) ? ` • ${c.issue_date || c.date}` : ''}</div>
                </li>
              ))}
            </ul>
          </section>
        )}

        {Array.isArray(resume.achievements) && resume.achievements.length > 0 && (
          <section>
            <h3 className="font-semibold mb-1">Achievements</h3>
            <ul className="list-disc pl-5 space-y-1">
              {resume.achievements.slice(0, 3).map((a: any, idx: number) => (
                <li key={idx} className="text-[11px]">
                  <strong>{a.title}</strong>{a.date ? ` (${a.date})` : ''}{a.issuer ? ` • ${a.issuer}` : ''}{a.description ? `: ${a.description}` : ''}
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  )
}

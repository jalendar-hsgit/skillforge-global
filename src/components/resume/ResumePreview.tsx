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
    <div className="bg-white text-gray-900 rounded-lg overflow-hidden border">
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
                  {Array.isArray(exp.responsibilities) && exp.responsibilities.length > 0 && (
                    <ul className="list-disc pl-5">
                      {exp.responsibilities.slice(0, 2).map((r: string, i: number) => (
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
                  <div className="font-medium">{edu.degree || 'Degree'} in {edu.field_of_study || 'Field'} • {edu.school || 'School'}</div>
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
      </div>
    </div>
  )
}

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
    template?: string
    work_experiences?: any[]
    education?: any[]
    skills?: any[]
    projects?: any[]
    certificates?: any[]
    achievements?: any[]
    // Customization
    font_family?: string
    color_theme?: string
    layout?: string
    accent_color?: string
    picture_style?: string
    show_icons?: boolean
    // Optional typography controls
    font_size?: number
    heading_size?: number
  }
}

export default function ResumePreview({ resume }: ResumePreviewProps) {
  // Derive style config from resume fields (coming from selected template)
  const layout = (resume.layout || resume.template || 'modern').toString().toLowerCase()
  const accent = resume.accent_color || '#2563eb' // default blue-600
  const fontFamily = resume.font_family
    ? (resume.font_family.toLowerCase() === 'century gothic' ? 'Century Gothic, CenturyGothic, AppleGothic, sans-serif' : resume.font_family)
    : (layout.includes('classic') ? 'Georgia, serif' : 'Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif')
  const baseFontSize = Math.max(9, Math.min(16, resume.font_size || 12))
  const headingFontSize = Math.max(9, Math.min(24, resume.heading_size || baseFontSize + 2))
  const showIcons = resume.show_icons ?? true

  const headerBase = 'px-4 py-3 border-b'
  const headerClass = layout.includes('classic')
    ? `${headerBase} bg-gray-50`
    : layout.includes('creative')
    ? `${headerBase} text-white`
    : layout.includes('beginner') || layout.includes('center')
    ? 'px-6 py-5'
    : `${headerBase} bg-white`

  const isTwoCol = layout.includes('two') || layout.includes('sidebar')
  const showPhoto = (resume.picture_style || '').toLowerCase() !== 'none'

  // Simple inline SVG icons to avoid extra imports
  const MailIcon = () => (
    <svg className="w-3.5 h-3.5 inline-block mr-1 align-[-2px]" viewBox="0 0 24 24" fill="currentColor"><path d="M20 4H4c-1.1 0-2 .9-2 2v12a2 2 0 002 2h16a2 2 0 002-2V6c0-1.1-.9-2-2-2Zm0 4-8 5L4 8V6l8 5 8-5v2Z"/></svg>
  )
  const PhoneIcon = () => (
    <svg className="w-3.5 h-3.5 inline-block mr-1 align-[-2px]" viewBox="0 0 24 24" fill="currentColor"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24 11.36 11.36 0 003.56.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1 11.36 11.36 0 00.57 3.56 1 1 0 01-.24 1.01l-2.2 2.2Z"/></svg>
  )
  const LinkIcon = () => (
    <svg className="w-3.5 h-3.5 inline-block mr-1 align-[-2px]" viewBox="0 0 24 24" fill="currentColor"><path d="M3.9 12a5 5 0 015-5h3v2h-3a3 3 0 100 6h3v2h-3a5 5 0 01-5-5Zm6.1 1h4v-2h-4v2Zm5-6h3a5 5 0 010 10h-3v-2h3a3 3 0 100-6h-3V7Z"/></svg>
  )

  const headerContent = (
    <div className={`flex ${layout.includes('beginner') || layout.includes('center') ? 'flex-col items-center text-center' : 'items-center justify-between'} gap-4`}>
      <div className={`flex ${layout.includes('beginner') || layout.includes('center') ? 'flex-col items-center' : 'items-center'} gap-3`}>
        {showPhoto && (
          <div className={`shrink-0 ${layout.includes('beginner') || layout.includes('center') ? 'mb-1' : ''}`}>
            <div
              className={`w-12 h-12 ${
                (resume.picture_style || '').includes('circle') ? 'rounded-full' : 'rounded-md'
              } bg-gray-200 border`}>
            </div>
          </div>
        )}
        <div>
          <h2 className={`font-bold`} style={{ fontFamily, fontSize: headingFontSize }}>
            {resume.full_name || 'Your Name'}
          </h2>
          <p className={`${layout.includes('creative') ? 'opacity-90' : 'opacity-80'}`} style={{ fontFamily, fontSize: baseFontSize - 2 }}>
            {showIcons && <MailIcon />}{resume.email || 'email@example.com'}
            <span className="mx-1.5">•</span>
            {showIcons && <PhoneIcon />}{resume.phone || '000-000-0000'}
            {resume.linkedin && (
              <>
                <span className="mx-1.5">•</span>
                {showIcons && <LinkIcon />}{resume.linkedin}
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  )

  return (
    <div className="bg-white text-gray-900 rounded-lg overflow-hidden border shadow" style={{ fontFamily }}>
      {/* Header */}
      {layout.includes('creative') ? (
        <div className={headerClass} style={{ background: `linear-gradient(90deg, ${accent}, ${accent}aa)` }}>
          {headerContent}
        </div>
      ) : layout.includes('beginner') || layout.includes('center') ? (
        <div className="px-6 pt-6">
          <div className="rounded-xl border-2 px-6 py-5 shadow-md" style={{ borderColor: accent, backgroundColor: `${accent}05` }}>
            {headerContent}
          </div>
        </div>
      ) : (
        <div className={headerClass}>
          <div className="border-b-2" style={{ borderColor: accent }} />
          {headerContent}
        </div>
      )}

      {/* Body */}
  <div className={`p-4 ${isTwoCol ? 'grid grid-cols-3 gap-4' : 'space-y-3'}`} style={{ fontSize: baseFontSize }}>
        {/* Left/Main column */}
        <div className={isTwoCol ? 'col-span-2 space-y-3' : ''}>
          {resume.professional_summary && (
            <section>
              <h3 className={`font-semibold mb-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('beginner') || layout.includes('center') ? accent : 'transparent' }}>Summary</h3>
              <p className={`leading-relaxed ${layout.includes('beginner') || layout.includes('center') ? 'text-center' : ''}`}>{resume.professional_summary}</p>
            </section>
          )}

          {Array.isArray(resume.work_experiences) && resume.work_experiences.length > 0 && (
            <section>
              <h3 className={`font-semibold mb-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('beginner') || layout.includes('center') ? accent : 'transparent' }}>Experience</h3>
              <ul className={`space-y-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center' : ''}`}>
                {resume.work_experiences.slice(0, 2).map((exp: any, idx: number) => (
                  <li key={idx}>
                    <div className="font-medium">{exp.position || 'Role'} • {exp.company || 'Company'}</div>
                    {((exp.responsibilities && exp.responsibilities.length) || (exp.bullet_points && exp.bullet_points.length)) && (
                      <ul className={`list-disc ${layout.includes('beginner') || layout.includes('center') ? 'list-none' : 'pl-5'}`}>
                        {(exp.responsibilities || exp.bullet_points || []).slice(0, 2).map((r: string, i: number) => (
                          <li key={i} className="text-[11px]">{r}</li>
                        ))}
                      </ul>
                    )}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {Array.isArray(resume.projects) && resume.projects.length > 0 && (
            <section>
              <h3 className={`font-semibold mb-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('beginner') || layout.includes('center') ? accent : 'transparent' }}>Projects</h3>
              <ul className={`space-y-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center' : ''}`}>
                {resume.projects.slice(0, 2).map((p: any, idx: number) => (
                  <li key={idx}>
                    <div className="font-medium">{p.title || p.name || 'Project'}</div>
                    {p.description && <p className="text-[11px] text-gray-600">{p.description}</p>}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        {/* Right/Sidebar column */}
        <div className={isTwoCol ? 'space-y-3' : ''}>
          {Array.isArray(resume.skills) && resume.skills.length > 0 && (
            <section>
              <h3 className={`font-semibold mb-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('beginner') || layout.includes('center') ? accent : 'transparent' }}>Skills</h3>
              <div className={`flex flex-wrap gap-1 ${layout.includes('beginner') || layout.includes('center') ? 'justify-center' : ''}`}>
                {resume.skills.slice(0, 8).map((s: any, idx: number) => (
                  <span key={idx} className="px-2 py-0.5 rounded-full border text-xs" style={{ borderColor: `${accent}55`, backgroundColor: `${accent}0d` }}>{s.name || 'Skill'}</span>
                ))}
              </div>
            </section>
          )}

          {Array.isArray(resume.education) && resume.education.length > 0 && (
            <section>
              <h3 className={`font-semibold mb-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('beginner') || layout.includes('center') ? accent : 'transparent' }}>Education</h3>
              <ul className={`space-y-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center' : ''}`}>
                {resume.education.slice(0, 2).map((edu: any, idx: number) => (
                  <li key={idx}>
                    <div className="font-medium text-[11px]">{edu.degree || 'Degree'} in {edu.field_of_study || 'Field'} • {edu.institution || edu.school || 'Institution'}</div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {Array.isArray(resume.certificates) && resume.certificates.length > 0 && (
            <section>
              <h3 className={`font-semibold mb-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('beginner') || layout.includes('center') ? accent : 'transparent' }}>Certificates</h3>
              <ul className={`space-y-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center' : ''}`}>
                {resume.certificates.slice(0, 2).map((c: any, idx: number) => (
                  <li key={idx}>
                    <div className="font-medium text-[11px]">{c.name || 'Certificate'}</div>
                    <div className="text-[10px] text-gray-600">{c.issuing_organization || c.issuer || 'Issuer'}{(c.issue_date || c.date) ? ` • ${c.issue_date || c.date}` : ''}</div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {Array.isArray(resume.achievements) && resume.achievements.length > 0 && (
            <section>
              <h3 className={`font-semibold mb-1 ${layout.includes('beginner') || layout.includes('center') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('beginner') || layout.includes('center') ? accent : 'transparent' }}>Achievements</h3>
              <ul className={`space-y-1 ${layout.includes('beginner') || layout.includes('center') ? 'list-none text-center' : 'list-disc pl-5'}`}>
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
    </div>
  )
}

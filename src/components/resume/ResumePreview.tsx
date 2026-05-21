import React from 'react';
import { Resume } from './types';
import ModernTemplate from './templates/ModernTemplate';
import MinimalTemplate from './templates/MinimalTemplate';
import ExecutiveTemplate from './templates/ExecutiveTemplate';
import CreativeTemplate from './templates/CreativeTemplate';
import TimelineTemplate from './templates/TimelineTemplate';
import ElegantBlueTemplate from './templates/ElegantBlueTemplate';

interface ResumePreviewProps {
  resume: Resume;
}

// ResumePreview component
const ResumePreview = (props: ResumePreviewProps) => {
  const { resume } = props;
  // Derive effective layout: prefer explicit layout, else map template/template_id
  const templateValue = (resume as any).template_id || resume.template;
  let layout = resume.layout || '';
  // If layout is missing OR looks like a numeric id (e.g., "1001"), derive from template/template_id
  if (!layout || /^\d+$/.test(layout.trim())) {
    const tpl = typeof templateValue === 'number' ? String(templateValue) : (templateValue || '').toString();
    const templateIdMap: Record<string,string> = {
      '1001': 'modern',
      '1002': 'minimal',
      '1003': 'executive-two',
      '1004': 'creative',
      '1005': 'tech-two',
      '1008': 'timeline',
      '1009': 'elegant-blue'
    };
    if (templateIdMap[tpl]) layout = templateIdMap[tpl];
    // Fallback: if template string contains known keyword
    else if (/modern/i.test(tpl)) layout = 'modern';
    else if (/minimal/i.test(tpl)) layout = 'minimal';
    else if (/executive/i.test(tpl)) layout = 'executive-two';
    else if (/creative/i.test(tpl)) layout = 'creative';
    else if (/timeline/i.test(tpl)) layout = 'timeline';
    else if (/elegant/i.test(tpl)) layout = 'elegant-blue';
  }
  
  // Use dedicated template components when layout matches
  if (layout === 'modern' || layout.includes('modern')) {
    return <ModernTemplate resume={resume} />;
  }
  if (layout === 'minimal' || layout.includes('minimal')) {
    return <MinimalTemplate resume={resume} />;
  }
  if (layout === 'executive' || layout.includes('executive')) {
    return <ExecutiveTemplate resume={resume} />;
  }
  if (layout === 'creative' || layout.includes('creative')) {
    return <CreativeTemplate resume={resume} />;
  }
  if (layout === 'timeline' || layout.includes('timeline')) {
    return <TimelineTemplate resume={resume} />;
  }
  if (layout === 'elegant-blue' || layout.includes('elegant')) {
    return <ElegantBlueTemplate resume={resume} />;
  }
  
  // Fallback to generic rendering for other layouts
  const accent = resume.accent_color || resume.accent || '#007bff';
  const sectionDivider = resume.section_divider || 'line';
  const headerShape = resume.header_shape || 'default';
  const iconStyle = resume.icon_style || 'default';
  const fontFamily = resume.font_family
    ? (resume.font_family.toLowerCase() === 'century gothic' ? 'Century Gothic, CenturyGothic, AppleGothic, sans-serif' : resume.font_family)
    : (layout.includes('classic') || layout.includes('academic') ? 'Georgia, serif' : layout.includes('creative') ? 'Poppins, Inter, system-ui, sans-serif' : 'Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif');
  const baseFontSize = Math.max(9, Math.min(16, resume.font_size || 12));
  const headingFontSize = Math.max(9, Math.min(24, resume.heading_size || baseFontSize + 2));
  const showIcons = resume.show_icons ?? true;
  // Place debugConfig here, after all variable declarations and logic

  // ...existing code...
  // ...existing code...

  // ...existing code...


  // Advanced header and background logic
  let headerClass = 'px-4 py-3';
  let headerStyle: React.CSSProperties = {};
  // Advanced header styling by layout, accent, background_type, header_shape, icon_style
  if (layout.includes('creative')) {
    headerClass += ' text-white shadow-lg';
    headerStyle = { background: `linear-gradient(90deg, ${accent}, ${accent}aa)`, borderRadius: headerShape === 'rounded' ? '2rem' : undefined };
    if (resume.background_type === 'pattern') headerStyle.backgroundImage = 'repeating-linear-gradient(135deg, #fff2 0px, #fff2 8px, transparent 8px, transparent 16px)';
  } else if (layout.includes('minimal')) {
    headerClass = 'px-6 pt-6';
    headerStyle = { backgroundColor: `${accent}08`, borderRadius: headerShape === 'pill' ? '999px' : undefined };
  } else if (layout.includes('executive')) {
    headerClass += ' bg-white/80 backdrop-blur border-b';
    headerStyle = { borderBottom: `4px solid ${accent}`, boxShadow: '0 2px 8px #0001', borderRadius: headerShape === 'cut' ? '0 0 2rem 2rem' : undefined };
  } else if (layout.includes('tech')) {
    headerClass += ' bg-gray-900 text-white';
    headerStyle = { borderBottom: `3px solid ${accent}`, background: resume.background_type === 'gradient' ? `linear-gradient(90deg, ${accent}, #222)` : undefined };
  } else if (layout.includes('academic')) {
    headerClass += ' bg-gray-50 border-b';
    headerStyle = { borderBottom: `2px solid ${accent}`, borderRadius: headerShape === 'notch' ? '0 0 1rem 1rem' : undefined };
  } else if (layout.includes('classic')) {
    headerClass += ' bg-gray-100 border-b';
    headerStyle = { borderBottom: `2px solid ${accent}` };
  } else if (layout.includes('center') || layout.includes('beginner')) {
    headerClass = 'px-6 pt-6';
    headerStyle = { border: `2px solid ${accent}`, backgroundColor: `${accent}05`, borderRadius: headerShape === 'circle' ? '50%' : undefined };
  } else if (layout.includes('modern')) {
    headerClass += ' bg-gradient-to-r from-white to-gray-100';
    headerStyle = { borderBottom: `2px solid ${accent}`, boxShadow: '0 1px 6px #0001', borderRadius: headerShape === 'wave' ? '2rem 0 2rem 0' : undefined };
  } else {
    headerClass += ' bg-white border-b';
    headerStyle = { borderBottom: `2px solid ${accent}` };
  }

  // Icon style logic (for future use)
  const iconClass = iconStyle === 'outline' ? 'stroke-2' : iconStyle === 'filled' ? 'fill-current' : '';

  // Unique layout logic
  const isTwoCol = layout.includes('two') || layout.includes('sidebar') || layout.includes('executive') || layout.includes('tech') || layout.includes('academic');
  const isSidebar = layout.includes('sidebar');
  const isTimeline = layout.includes('timeline');
  const isCard = layout.includes('card');
  const isGrid = layout.includes('grid');
  const showPhoto = (resume.picture_style || '').toLowerCase() !== 'none';

  // Section divider logic
  const divider = sectionDivider === 'gradient' ? <div style={{ height: 4, background: `linear-gradient(90deg, ${accent}, #fff)` }} /> : sectionDivider === 'dashed' ? <hr style={{ borderTop: `2px dashed ${accent}` }} /> : <hr style={{ borderTop: `2px solid ${accent}` }} />;

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
    );

  return (
    <div className="bg-white text-gray-900 overflow-hidden" style={{ fontFamily, maxWidth: '100%', width: '100%' }}>
      {/* Header */}
      <div className={headerClass} style={headerStyle}>
        {headerContent}
      </div>
      {/* Divider */}
      {divider}
      {/* Body */}
      {/* Unique layouts */}
      {isSidebar ? (
        <div className="flex">
          <aside className="w-1/3 bg-gray-50 p-4 border-r overflow-y-auto" style={{ borderColor: accent, maxHeight: '100%' }}>
            {/* Sidebar: skills, contact, certificates */}
            {Array.isArray(resume.skills) && resume.skills.length > 0 && (
              <section>
                <h3 className="font-semibold mb-1" style={{ color: accent }}>Skills</h3>
                <div className="flex flex-wrap gap-1">
                  {resume.skills.map((s: any, idx: number) => (
                    <span key={idx} className="px-2 py-0.5 rounded-full text-xs border" style={{ borderColor: `${accent}55`, backgroundColor: `${accent}0d` }}>{s.name || 'Skill'}</span>
                  ))}
                </div>
              </section>
            )}
            {Array.isArray(resume.certificates) && resume.certificates.length > 0 && (
              <section>
                <h3 className="font-semibold mb-1" style={{ color: accent }}>Certificates</h3>
                <ul className="space-y-1">
                  {resume.certificates.map((c: any, idx: number) => (
                    <li key={idx}><div className="font-medium text-[11px]">{c.name || 'Certificate'}</div></li>
                  ))}
                </ul>
              </section>
            )}
          </aside>
          <main className="flex-1 p-4 overflow-y-auto" style={{ maxHeight: '100%', boxSizing: 'border-box' }}>
            {/* Main: summary, experience, projects, education */}
            {resume.professional_summary && (
              <section>
                <h3 className="font-semibold mb-1" style={{ color: accent }}>Summary</h3>
                <p className="leading-relaxed">{resume.professional_summary}</p>
              </section>
            )}
            {Array.isArray(resume.work_experiences) && resume.work_experiences.length > 0 && (
              <section>
                <h3 className="font-semibold mb-1" style={{ color: accent }}>Experience</h3>
                <ul className="space-y-2">
                  {resume.work_experiences.map((exp: any, idx: number) => (
                    <li key={idx} className="break-inside-avoid">
                      <div className="font-medium text-sm">{exp.position || 'Role'} • {exp.company || 'Company'}</div>
                      {exp.start_date && <div className="text-xs text-gray-600 mb-1">{exp.start_date}{exp.end_date ? ` - ${exp.end_date}` : ''}</div>}
                      {exp.description && <p className="text-xs text-gray-700">{exp.description}</p>}
                    </li>
                  ))}
                </ul>
              </section>
            )}
            {Array.isArray(resume.projects) && resume.projects.length > 0 && (
              <section>
                <h3 className="font-semibold mb-1" style={{ color: accent }}>Projects</h3>
                <ul className="space-y-1">
                  {resume.projects.slice(0, 2).map((p: any, idx: number) => (
                    <li key={idx}><div className="font-medium">{p.title || p.name || 'Project'}</div></li>
                  ))}
                </ul>
              </section>
            )}
            {Array.isArray(resume.education) && resume.education.length > 0 && (
              <section>
                <h3 className="font-semibold mb-1" style={{ color: accent }}>Education</h3>
                <ul className="space-y-1">
                  {resume.education.slice(0, 2).map((edu: any, idx: number) => (
                    <li key={idx}><div className="font-medium text-[11px]">{edu.degree || 'Degree'} in {edu.field_of_study || 'Field'} • {edu.institution || edu.school || 'Institution'}</div></li>
                  ))}
                </ul>
              </section>
            )}
          </main>
        </div>
      ) : isTimeline ? (
        <div className="p-4">
          {/* Timeline layout for experience */}
          {resume.work_experiences && resume.work_experiences.length > 0 && (
            <section>
              <h3 className="font-semibold mb-1" style={{ color: accent }}>Experience Timeline</h3>
              <ul className="border-l-4 pl-4" style={{ borderColor: accent }}>
                {resume.work_experiences.slice(0, 4).map((exp: any, idx: number) => (
                  <li key={idx} className="mb-4">
                    <div className="font-medium">{exp.position || 'Role'} • {exp.company || 'Company'}</div>
                    <div className="text-xs text-gray-500">{exp.start_date || ''} - {exp.end_date || ''}</div>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      ) : isCard ? (
        <div className="p-4 grid grid-cols-2 gap-4">
          {/* Card layout for sections */}
          {resume.skills && resume.skills.length > 0 && (
            <div className="bg-white border rounded-lg p-3 shadow" style={{ borderColor: accent }}>
              <h3 className="font-semibold mb-1" style={{ color: accent }}>Skills</h3>
              <div className="flex flex-wrap gap-1">
                {resume.skills.slice(0, 8).map((s: any, idx: number) => (
                  <span key={idx} className="px-2 py-0.5 rounded-full text-xs border" style={{ borderColor: `${accent}55`, backgroundColor: `${accent}0d` }}>{s.name || 'Skill'}</span>
                ))}
              </div>
            </div>
          )}
          {resume.projects && resume.projects.length > 0 && (
            <div className="bg-white border rounded-lg p-3 shadow" style={{ borderColor: accent }}>
              <h3 className="font-semibold mb-1" style={{ color: accent }}>Projects</h3>
              <ul className="space-y-1">
                {resume.projects.slice(0, 2).map((p: any, idx: number) => (
                  <li key={idx}><div className="font-medium">{p.title || p.name || 'Project'}</div></li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : isGrid ? (
        <div className="p-4 grid grid-cols-3 gap-4">
          {/* Grid layout for all sections */}
          {resume.skills && resume.skills.length > 0 && (
            <div className="bg-white border rounded-lg p-3 shadow" style={{ borderColor: accent }}>
              <h3 className="font-semibold mb-1" style={{ color: accent }}>Skills</h3>
              <div className="flex flex-wrap gap-1">
                {resume.skills.slice(0, 8).map((s: any, idx: number) => (
                  <span key={idx} className="px-2 py-0.5 rounded-full text-xs border" style={{ borderColor: `${accent}55`, backgroundColor: `${accent}0d` }}>{s.name || 'Skill'}</span>
                ))}
              </div>
            </div>
          )}
          {resume.projects && resume.projects.length > 0 && (
            <div className="bg-white border rounded-lg p-3 shadow" style={{ borderColor: accent }}>
              <h3 className="font-semibold mb-1" style={{ color: accent }}>Projects</h3>
              <ul className="space-y-1">
                {resume.projects.slice(0, 2).map((p: any, idx: number) => (
                  <li key={idx}><div className="font-medium">{p.title || p.name || 'Project'}</div></li>
                ))}
              </ul>
            </div>
          )}
          {resume.education && resume.education.length > 0 && (
            <div className="bg-white border rounded-lg p-3 shadow" style={{ borderColor: accent }}>
              <h3 className="font-semibold mb-1" style={{ color: accent }}>Education</h3>
              <ul className="space-y-1">
                {resume.education.slice(0, 2).map((edu: any, idx: number) => (
                  <li key={idx}><div className="font-medium text-[11px]">{edu.degree || 'Degree'} in {edu.field_of_study || 'Field'} • {edu.institution || edu.school || 'Institution'}</div></li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        // Default: two-column or single-column
        <div className={`p-4 ${isTwoCol ? 'grid grid-cols-3 gap-4' : 'space-y-3'}`} style={{ fontSize: baseFontSize, width: '100%', boxSizing: 'border-box' }}>
          {/* Left/Main column */}
          <div className={isTwoCol ? 'col-span-2 space-y-3' : ''} style={{ width: '100%', boxSizing: 'border-box' }}>
            {resume.professional_summary && (
              <section>
                <h3 className={`font-semibold mb-1 ${layout.includes('center') || layout.includes('beginner') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('center') || layout.includes('beginner') ? accent : 'transparent' }}>Summary</h3>
                <p className={`leading-relaxed ${layout.includes('center') || layout.includes('beginner') ? 'text-center' : ''}`}>{resume.professional_summary}</p>
              </section>
            )}
            {Array.isArray(resume.work_experiences) && resume.work_experiences.length > 0 && (
              <section>
                <h3 className={`font-semibold mb-1 ${layout.includes('center') || layout.includes('beginner') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('center') || layout.includes('beginner') ? accent : 'transparent' }}>Experience</h3>
                <ul className={`space-y-2 ${layout.includes('center') || layout.includes('beginner') ? 'text-center' : ''}`}>
                  {resume.work_experiences.map((exp: any, idx: number) => (
                    <li key={idx} className="break-inside-avoid">
                      <div className="font-medium text-sm">{exp.position || 'Role'} • {exp.company || 'Company'}</div>
                      {exp.start_date && <div className="text-xs text-gray-600 mb-1">{exp.start_date}{exp.end_date ? ` - ${exp.end_date}` : ''}</div>}
                      {((exp.responsibilities && exp.responsibilities.length) || (exp.bullet_points && exp.bullet_points.length)) && (
                        <ul className={`list-disc ${layout.includes('center') || layout.includes('beginner') ? 'list-none' : 'pl-5'}`}>
                          {(exp.responsibilities || exp.bullet_points || []).map((r: string, i: number) => (
                            <li key={i} className="text-[11px] text-gray-700">{r}</li>
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
                <h3 className={`font-semibold mb-1 ${layout.includes('center') || layout.includes('beginner') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('center') || layout.includes('beginner') ? accent : 'transparent' }}>Projects</h3>
                <ul className={`space-y-1 ${layout.includes('center') || layout.includes('beginner') ? 'text-center' : ''}`}>
                  {resume.projects.map((p: any, idx: number) => (
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
          <div className={isTwoCol ? 'space-y-3' : ''} style={{ width: '100%', boxSizing: 'border-box' }}>
            {Array.isArray(resume.skills) && resume.skills.length > 0 && (
              <section>
                <h3 className={`font-semibold mb-1 ${layout.includes('center') || layout.includes('beginner') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('center') || layout.includes('beginner') ? accent : 'transparent' }}>Skills</h3>
                <div className={`flex flex-wrap gap-1 ${layout.includes('center') || layout.includes('beginner') ? 'justify-center' : ''}`}>
                  {resume.skills.map((s: any, idx: number) => (
                    <span key={idx} className={`px-2 py-0.5 rounded-full text-xs border`} style={{ borderColor: `${accent}55`, backgroundColor: `${accent}0d` }}>{s.name || 'Skill'}</span>
                  ))}
                </div>
              </section>
            )}
            {Array.isArray(resume.education) && resume.education.length > 0 && (
              <section>
                <h3 className={`font-semibold mb-1 ${layout.includes('center') || layout.includes('beginner') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('center') || layout.includes('beginner') ? accent : 'transparent' }}>Education</h3>
                <ul className={`space-y-1 ${layout.includes('center') || layout.includes('beginner') ? 'text-center' : ''}`}>
                  {resume.education.map((edu: any, idx: number) => (
                    <li key={idx}>
                      <div className="font-medium text-[11px]">{edu.degree || 'Degree'} in {edu.field_of_study || 'Field'} • {edu.institution || edu.school || 'Institution'}</div>
                    </li>
                  ))}
                </ul>
              </section>
            )}
            {Array.isArray(resume.certificates) && resume.certificates.length > 0 && (
              <section>
                <h3 className={`font-semibold mb-1 ${layout.includes('center') || layout.includes('beginner') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('center') || layout.includes('beginner') ? accent : 'transparent' }}>Certificates</h3>
                <ul className={`space-y-1 ${layout.includes('center') || layout.includes('beginner') ? 'text-center' : ''}`}>
                  {resume.certificates.map((c: any, idx: number) => (
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
                <h3 className={`font-semibold mb-1 ${layout.includes('center') || layout.includes('beginner') ? 'text-center pb-1 border-b-2' : ''}`} style={{ color: accent, borderColor: layout.includes('center') || layout.includes('beginner') ? accent : 'transparent' }}>Achievements</h3>
                <ul className={`space-y-1 ${layout.includes('center') || layout.includes('beginner') ? 'list-none text-center' : 'list-disc pl-5'}`}>
                  {resume.achievements.map((a: any, idx: number) => (
                    <li key={idx} className="text-[11px]">
                      <strong>{a.title}</strong>{a.date ? ` (${a.date})` : ''}{a.issuer ? ` • ${a.issuer}` : ''}{a.description ? `: ${a.description}` : ''}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ResumePreview;

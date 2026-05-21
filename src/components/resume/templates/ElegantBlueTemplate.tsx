import React from 'react';
import { Resume } from '../types';

export default function ElegantBlueTemplate({ resume }: { resume: Resume }) {
  const primaryBlue = '#1e3a8a'; // Blue-900
  const accentBlue = resume.accent_color || '#3b82f6'; // Blue-500
  return (
    <div className="elegant-blue-template bg-white mx-auto" style={{ minHeight: '297mm', width: '210mm', maxWidth: '100%', boxSizing: 'border-box', overflow: 'hidden' }}>
      <div className="text-white relative" style={{ background: `linear-gradient(135deg, ${primaryBlue} 0%, ${accentBlue} 100%)`, padding: '32px 28px', boxSizing: 'border-box' }}>
        <div className="absolute inset-0 opacity-5" style={{
          backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
          backgroundSize: '32px 32px'
        }}></div>
        <div className="relative z-10">
          <h1 className="text-5xl font-bold tracking-tight mb-3">{resume.full_name || 'Your Name'}</h1>
          {resume.title && <p className="text-2xl opacity-95 font-light tracking-wide">{resume.title}</p>}
          <div className="flex flex-wrap gap-6 mt-6 text-sm opacity-90">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.location && <span>{resume.location}</span>}
          {resume.linkedin && <span>{resume.linkedin}</span>}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-0" style={{ padding: '28px', boxSizing: 'border-box' }}>
        <div className="col-span-2 space-y-8" style={{ paddingRight: '16px', boxSizing: 'border-box' }}>
          {resume.professional_summary && (
            <section>
              <h3 className="font-bold text-2xl uppercase tracking-wide pb-3 mb-4 border-b-4" style={{ color: primaryBlue, borderColor: accentBlue }}>
                Professional Summary
              </h3>
              <p className="leading-relaxed text-gray-700 text-sm">{resume.professional_summary}</p>
            </section>
          )}
          {resume.work_experiences?.length ? (
            <section>
              <h3 className="font-bold text-2xl uppercase tracking-wide pb-3 mb-4 border-b-4" style={{ color: primaryBlue, borderColor: accentBlue }}>
                Experience
              </h3>
              {resume.work_experiences.map((exp, i) => (
                <div key={i} className="mb-6 pl-6 relative">
                  <div className="absolute left-0 top-1 w-3 h-3 rounded-full" style={{ backgroundColor: accentBlue }}></div>
                  <div className="font-bold text-lg" style={{ color: primaryBlue }}>{exp.position}</div>
                  <div className="font-semibold text-base" style={{ color: accentBlue }}>{exp.company}</div>
                  <div className="text-xs text-gray-500 mt-1">{exp.start_date} - {exp.end_date || 'Present'}</div>
                  {exp.description && <p className="text-sm mt-2 text-gray-700 leading-relaxed">{exp.description}</p>}
                </div>
              ))}
            </section>
          ) : null}
          {resume.education?.length ? (
            <section>
              <h3 className="font-bold text-2xl uppercase tracking-wide pb-3 mb-4 border-b-4" style={{ color: primaryBlue, borderColor: accentBlue }}>
                Education
              </h3>
              {resume.education.map((edu, i) => (
                <div key={i} className="mb-5">
                  <div className="font-semibold text-base" style={{ color: primaryBlue }}>{edu.degree}</div>
                  <div className="text-sm text-gray-700">{edu.institution}</div>
                  {edu.graduation_date && <div className="text-xs text-gray-500 mt-1">{edu.graduation_date}</div>}
                </div>
              ))}
            </section>
          ) : null}
        </div>
        <aside className="space-y-8">
          {resume.skills?.length ? (
            <section>
              <h3 className="font-bold text-lg uppercase tracking-wide pb-2 mb-3 border-b-2" style={{ color: primaryBlue, borderColor: accentBlue }}>
                Skills
              </h3>
              <div className="space-y-3">
                {resume.skills.slice(0, 30).map((s, i) => (
                  <div key={i}>
                    <div className="text-sm font-medium mb-1" style={{ color: primaryBlue }}>{s.name}</div>
                    {s.level && (
                      <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div 
                          className="h-1.5 rounded-full" 
                          style={{ 
                            width: s.level === 'Expert' ? '100%' : s.level === 'Advanced' ? '80%' : s.level === 'Intermediate' ? '60%' : '40%',
                            backgroundColor: accentBlue
                          }}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          ) : null}
          {resume.certificates?.length ? (
            <section>
              <h3 className="font-bold text-lg uppercase tracking-wide pb-2 mb-3 border-b-2" style={{ color: primaryBlue, borderColor: accentBlue }}>
                Certifications
              </h3>
              <ul className="space-y-2 text-xs">
                {resume.certificates.slice(0, 8).map((c, i) => (
                  <li key={i}>
                    <div className="font-semibold" style={{ color: primaryBlue }}>{c.name}</div>
                    {c.issuer && <div className="text-gray-600 mt-0.5">{c.issuer}</div>}
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
          {resume.achievements?.length ? (
            <section>
              <h3 className="font-bold text-lg uppercase tracking-wide pb-2 mb-3 border-b-2" style={{ color: primaryBlue, borderColor: accentBlue }}>
                Achievements
              </h3>
              <ul className="space-y-2 text-xs">
                {resume.achievements.slice(0, 8).map((a: any, i: number) => (
                  <li key={i} className="flex items-start gap-2">
                    <span style={{ color: accentBlue }}>▸</span>
                    <div>
                      <div className="font-semibold">{a.title}</div>
                      {a.description && <div className="text-gray-600 text-xs mt-0.5">{a.description}</div>}
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </aside>
      </div>
    </div>
  );
}

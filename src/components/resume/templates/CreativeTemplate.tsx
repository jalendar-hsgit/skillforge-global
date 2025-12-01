import React from 'react';
import { Resume } from '../types';

export default function CreativeTemplate({ resume }: { resume: Resume }) {
  const accent = resume.accent_color || '#8b5cf6';
  return (
    <div className="creative-template bg-white overflow-hidden" style={{ minHeight: '297mm', width: '210mm' }}>
      <div className="p-12 bg-gradient-to-r from-purple-600 via-indigo-500 to-pink-500 text-white relative overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10" style={{ 
          backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,.1) 10px, rgba(255,255,255,.1) 20px)' 
        }}></div>
        <div className="relative z-10">
          <h1 className="text-5xl font-extrabold tracking-tight drop-shadow-lg mb-2">{resume.full_name || 'Your Name'}</h1>
          {resume.title && <p className="text-2xl opacity-95 mt-2 font-semibold">{resume.title}</p>}
          <div className="w-24 h-1 bg-white/50 mt-4 mb-6"></div>
        <p className="text-sm opacity-90 flex flex-wrap gap-x-6 gap-y-2">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.location && <span>{resume.location}</span>}
          {resume.website && <span>{resume.website}</span>}
        </p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-10 p-10">
        <div className="col-span-2 space-y-8">
          {resume.professional_summary && (
            <section>
              <h3 className="font-bold text-2xl mb-3 uppercase tracking-wide relative inline-block" style={{ color: accent }}>
                Profile
                <div className="absolute -bottom-1 left-0 w-full h-1 bg-gradient-to-r from-purple-500 to-pink-500"></div>
              </h3>
              <p className="leading-relaxed text-gray-700 mt-4 text-sm">{resume.professional_summary}</p>
            </section>
          )}
          {resume.work_experiences?.length ? (
            <section>
              <h3 className="font-bold text-2xl mb-4 uppercase tracking-wide relative inline-block" style={{ color: accent }}>
                Experience
                <div className="absolute -bottom-1 left-0 w-full h-1 bg-gradient-to-r from-purple-500 to-pink-500"></div>
              </h3>
              {resume.work_experiences.map((exp, i) => (
                <div key={i} className="mb-6 pl-6 border-l-4 border-gradient" style={{ borderColor: `${accent}40` }}>
                  <div className="font-bold text-base">{exp.position}</div>
                  <div className="font-semibold text-gray-600 text-sm">{exp.company}</div>
                  <div className="text-xs text-gray-500 mt-1">{exp.start_date} - {exp.end_date || 'Present'}</div>
                  {exp.description && <p className="text-sm mt-2 text-gray-700">{exp.description}</p>}
                </div>
              ))}
            </section>
          ) : null}
          {resume.projects?.length ? (
            <section>
              <h3 className="font-bold text-2xl mb-4 uppercase tracking-wide relative inline-block" style={{ color: accent }}>
                Projects
                <div className="absolute -bottom-1 left-0 w-full h-1 bg-gradient-to-r from-purple-500 to-pink-500"></div>
              </h3>
              {resume.projects.map((p, i) => (
                <div key={i} className="mb-5">
                  <div className="font-bold text-base flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500"></span>
                    {p.title || p.name}
                  </div>
                  {p.description && <p className="text-sm text-gray-700 mt-1">{p.description}</p>}
                </div>
              ))}
            </section>
          ) : null}
        </div>
        <aside className="space-y-6">
          {resume.skills?.length ? (
            <section>
              <h3 className="font-bold text-lg uppercase tracking-wide mb-4 pb-2 border-b-2" style={{ color: accent, borderColor: `${accent}40` }}>
                Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {resume.skills.slice(0, 24).map((s, i) => (
                  <span key={i} className="px-3 py-1.5 rounded-full text-xs font-medium shadow-sm" style={{ 
                    background: `linear-gradient(135deg, ${accent}20, ${accent}10)`,
                    color: accent,
                    border: `1px solid ${accent}40`
                  }}>{s.name}</span>
                ))}
              </div>
            </section>
          ) : null}
          {resume.education?.length ? (
            <section>
              <h3 className="font-bold text-lg uppercase tracking-wide mb-4 pb-2 border-b-2" style={{ color: accent, borderColor: `${accent}40` }}>
                Education
              </h3>
              {resume.education.map((edu, i) => (
                <div key={i} className="mb-4">
                  <div className="font-semibold text-sm">{edu.degree}</div>
                  <div className="text-xs text-gray-600 mt-1">{edu.institution}</div>
                  {edu.graduation_date && <div className="text-xs text-gray-500 mt-1">{edu.graduation_date}</div>}
                </div>
              ))}
            </section>
          ) : null}
          {resume.achievements?.length ? (
            <section>
              <h3 className="font-bold text-lg uppercase tracking-wide mb-4 pb-2 border-b-2" style={{ color: accent, borderColor: `${accent}40` }}>
                Achievements
              </h3>
              <ul className="space-y-2 text-xs">
                {resume.achievements.slice(0, 8).map((a: any, i: number) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-purple-500 mt-0.5">✦</span>
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

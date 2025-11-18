import React from 'react';
import { Resume } from '../types';

export default function CreativeTemplate({ resume }: { resume: Resume }) {
  const accent = resume.accent_color || '#8b5cf6';
  return (
    <div className="creative-template bg-white rounded-xl shadow-xl overflow-hidden">
      <div className="p-8 bg-gradient-to-r from-purple-600 via-indigo-500 to-pink-500 text-white">
        <h1 className="text-4xl font-extrabold tracking-tight drop-shadow-sm">{resume.full_name}</h1>
        {resume.title && <p className="text-lg opacity-90 mt-1">{resume.title}</p>}
        <p className="text-sm opacity-80 mt-3 flex flex-wrap gap-x-4 gap-y-1">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.location && <span>{resume.location}</span>}
          {resume.website && <span>{resume.website}</span>}
        </p>
      </div>
      <div className="grid md:grid-cols-3 gap-8 p-8">
        <div className="md:col-span-2 space-y-8">
          {resume.professional_summary && (
            <section>
              <h3 className="font-bold text-xl mb-2" style={{ color: accent }}>Profile</h3>
              <p className="leading-relaxed text-gray-700">{resume.professional_summary}</p>
            </section>
          )}
          {resume.work_experiences?.length ? (
            <section>
              <h3 className="font-bold text-xl mb-2" style={{ color: accent }}>Experience</h3>
              {resume.work_experiences.map((exp, i) => (
                <div key={i} className="mb-5">
                  <div className="font-semibold flex items-center gap-2"><span className="w-2 h-2 rounded-full" style={{ background: accent }} />{exp.position} • {exp.company}</div>
                  <div className="text-xs text-gray-500">{exp.start_date} - {exp.end_date}</div>
                  {exp.description && <p className="text-sm mt-1">{exp.description}</p>}
                </div>
              ))}
            </section>
          ) : null}
          {resume.projects?.length ? (
            <section>
              <h3 className="font-bold text-xl mb-2" style={{ color: accent }}>Projects</h3>
              {resume.projects.map((p, i) => (
                <div key={i} className="mb-4">
                  <div className="font-semibold">{p.title || p.name}</div>
                  {p.description && <p className="text-sm text-gray-600">{p.description}</p>}
                </div>
              ))}
            </section>
          ) : null}
        </div>
        <aside className="space-y-8">
          {resume.skills?.length ? (
            <section>
              <h3 className="font-semibold text-sm uppercase tracking-wide mb-3" style={{ color: accent }}>Skills</h3>
              <div className="flex flex-wrap gap-2">
                {resume.skills.slice(0, 24).map((s, i) => (
                  <span key={i} className="px-2 py-1 rounded-full text-xs border" style={{ borderColor: accent, color: accent }}>{s.name}</span>
                ))}
              </div>
            </section>
          ) : null}
          {resume.education?.length ? (
            <section>
              <h3 className="font-semibold text-sm uppercase tracking-wide mb-3" style={{ color: accent }}>Education</h3>
              {resume.education.map((edu, i) => (
                <div key={i} className="mb-3">
                  <div className="font-medium text-sm">{edu.degree}</div>
                  <div className="text-xs text-gray-500">{edu.institution}</div>
                </div>
              ))}
            </section>
          ) : null}
          {resume.achievements?.length ? (
            <section>
              <h3 className="font-semibold text-sm uppercase tracking-wide mb-3" style={{ color: accent }}>Achievements</h3>
              <ul className="space-y-1 text-xs">
                {resume.achievements.slice(0, 8).map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            </section>
          ) : null}
        </aside>
      </div>
    </div>
  );
}

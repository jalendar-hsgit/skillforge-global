import React from 'react';
import { Resume } from '../types';

export default function ElegantBlueTemplate({ resume }: { resume: Resume }) {
  const accent = resume.accent_color || '#1e3a8a';
  return (
    <div className="elegant-blue-template bg-white rounded-xl shadow border overflow-hidden">
      <div className="p-8 bg-blue-900 text-blue-50">
        <h1 className="text-4xl font-bold tracking-tight">{resume.full_name}</h1>
        {resume.title && <p className="text-lg opacity-90 mt-1">{resume.title}</p>}
        <p className="text-xs opacity-75 mt-3 flex flex-wrap gap-x-4 gap-y-1">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.location && <span>{resume.location}</span>}
        </p>
      </div>
      <div className="p-8 grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-8">
          {resume.professional_summary && (
            <section>
              <h3 className="font-semibold text-sm uppercase tracking-wide mb-2" style={{ color: accent }}>Professional Summary</h3>
              <p className="leading-relaxed text-gray-700">{resume.professional_summary}</p>
            </section>
          )}
          {resume.work_experiences?.length ? (
            <section>
              <h3 className="font-semibold text-sm uppercase tracking-wide mb-2" style={{ color: accent }}>Experience</h3>
              {resume.work_experiences.map((exp, i) => (
                <div key={i} className="mb-5">
                  <div className="font-medium">{exp.position} • {exp.company}</div>
                  <div className="text-xs text-gray-500">{exp.start_date} - {exp.end_date}</div>
                  {exp.description && <p className="text-sm mt-1 text-gray-600">{exp.description}</p>}
                </div>
              ))}
            </section>
          ) : null}
          {resume.education?.length ? (
            <section>
              <h3 className="font-semibold text-sm uppercase tracking-wide mb-2" style={{ color: accent }}>Education</h3>
              {resume.education.map((edu, i) => (
                <div key={i} className="mb-3">
                  <div className="font-medium text-sm">{edu.degree}</div>
                  <div className="text-xs text-gray-500">{edu.institution}</div>
                </div>
              ))}
            </section>
          ) : null}
        </div>
        <aside className="space-y-8">
          {resume.skills?.length ? (
            <section>
              <h3 className="font-semibold text-sm uppercase tracking-wide mb-2" style={{ color: accent }}>Skills</h3>
              <div className="flex flex-wrap gap-2">
                {resume.skills.slice(0, 30).map((s, i) => <span key={i} className="px-2 py-1 rounded text-xs border" style={{ borderColor: accent }}>{s.name}</span>)}
              </div>
            </section>
          ) : null}
          {resume.certificates?.length ? (
            <section>
              <h3 className="font-semibold text-sm uppercase tracking-wide mb-2" style={{ color: accent }}>Certifications</h3>
              <ul className="space-y-1 text-xs">
                {resume.certificates.slice(0, 8).map((c, i) => <li key={i}>{c.name}</li>)}
              </ul>
            </section>
          ) : null}
          {resume.achievements?.length ? (
            <section>
              <h3 className="font-semibold text-sm uppercase tracking-wide mb-2" style={{ color: accent }}>Achievements</h3>
              <ul className="space-y-1 text-xs list-disc pl-5">
                {resume.achievements.slice(0, 8).map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            </section>
          ) : null}
        </aside>
      </div>
    </div>
  );
}

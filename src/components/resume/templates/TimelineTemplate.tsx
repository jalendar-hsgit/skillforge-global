import React from 'react';
import { Resume } from '../types';

export default function TimelineTemplate({ resume }: { resume: Resume }) {
  const accent = resume.accent_color || '#0ea5e9';
  return (
    <div className="timeline-template bg-white mx-auto" style={{ minHeight: '297mm', width: '210mm', maxWidth: '100%', boxSizing: 'border-box', overflow: 'hidden', padding: '32px' }}>
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold" style={{ color: accent }}>{resume.full_name}</h1>
        {resume.title && <p className="text-sm text-gray-600 mt-1">{resume.title}</p>}
        <p className="text-xs text-gray-500 mt-2 flex flex-wrap justify-center gap-x-3 gap-y-1">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.location && <span>{resume.location}</span>}
        </p>
      </header>
      {resume.work_experiences?.length ? (
        <section className="mb-8">
          <h3 className="font-semibold text-sm mb-3 uppercase tracking-wide" style={{ color: accent }}>Experience Timeline</h3>
          <ul className="relative border-l-2 pl-6" style={{ borderColor: accent }}>
            {resume.work_experiences.map((exp, i) => (
              <li key={i} className="mb-6">
                <div className="absolute -left-2 w-4 h-4 rounded-full" style={{ background: accent }} />
                <div className="font-medium">{exp.position} • {exp.company}</div>
                <div className="text-xs text-gray-500">{exp.start_date} - {exp.end_date}</div>
                {exp.description && <p className="text-xs mt-1 text-gray-600">{exp.description}</p>}
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      <div className="grid md:grid-cols-3 gap-6">
        {resume.skills?.length ? (
          <section className="md:col-span-1">
            <h3 className="font-semibold text-sm mb-2 uppercase tracking-wide" style={{ color: accent }}>Skills</h3>
            <div className="flex flex-wrap gap-2">
              {resume.skills.slice(0, 30).map((s, i) => <span key={i} className="px-2 py-1 rounded text-xs border" style={{ borderColor: accent }}>{s.name}</span>)}
            </div>
          </section>
        ) : null}
        {resume.projects?.length ? (
          <section className="md:col-span-2">
            <h3 className="font-semibold text-sm mb-2 uppercase tracking-wide" style={{ color: accent }}>Projects</h3>
            {resume.projects.map((p, i) => (
              <div key={i} className="mb-4">
                <div className="font-medium text-sm">{p.title || p.name}</div>
                {p.description && <p className="text-xs text-gray-600">{p.description}</p>}
              </div>
            ))}
          </section>
        ) : null}
      </div>
    </div>
  );
}

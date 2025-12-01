import React from 'react';
import { Resume } from '../types';

export default function ExecutiveTemplate({ resume }: { resume: Resume }) {
  return (
    <div className="executive-template bg-white rounded-xl shadow border p-8 grid grid-cols-3 gap-8">
      <div className="col-span-2">
        <header className="mb-6 pb-4 border-b-4" style={{ borderColor: resume.accent_color || '#111827' }}>
          <h1 className="text-4xl font-extrabold tracking-tight" style={{ color: resume.accent_color || '#111827' }}>{resume.full_name}</h1>
          {resume.title && <p className="text-lg font-medium text-gray-600 mt-1">{resume.title}</p>}
          <p className="text-sm text-gray-500 mt-2 flex flex-wrap gap-x-3 gap-y-1">
            {resume.email && <span>{resume.email}</span>}
            {resume.phone && <span>{resume.phone}</span>}
            {resume.location && <span>{resume.location}</span>}
            {resume.linkedin && <span>{resume.linkedin}</span>}
          </p>
        </header>
        {resume.professional_summary && (
          <section className="mb-6">
            <h3 className="font-bold text-lg mb-2" style={{ color: resume.accent_color || '#111827' }}>Executive Summary</h3>
            <p className="leading-relaxed text-gray-700">{resume.professional_summary}</p>
          </section>
        )}
        {resume.work_experiences?.length ? (
          <section className="mb-6">
            <h3 className="font-bold text-lg mb-2" style={{ color: resume.accent_color || '#111827' }}>Leadership Experience</h3>
            {resume.work_experiences.map((exp, i) => (
              <div key={i} className="mb-4">
                <div className="font-semibold">{exp.position} • {exp.company}</div>
                <div className="text-xs text-gray-500">{exp.start_date} - {exp.end_date}</div>
                {exp.description && <p className="text-sm mt-1">{exp.description}</p>}
              </div>
            ))}
          </section>
        ) : null}
        {resume.achievements?.length ? (
          <section className="mb-6">
            <h3 className="font-bold text-lg mb-2" style={{ color: resume.accent_color || '#111827' }}>Key Achievements</h3>
            <ul className="list-disc pl-5 text-sm space-y-1">
              {resume.achievements.map((a: any, i: number) => (
                <li key={i}>
                  <span className="font-semibold">{a.title}</span>
                  {a.description && <span className="text-gray-600 text-xs block mt-0.5">{a.description}</span>}
                </li>
              ))}
            </ul>
          </section>
        ) : null}
        {resume.projects?.length ? (
          <section>
            <h3 className="font-bold text-lg mb-2" style={{ color: resume.accent_color || '#111827' }}>Strategic Projects</h3>
            {resume.projects.map((p, i) => (
              <div key={i} className="mb-3">
                <div className="font-semibold">{p.title || p.name}</div>
                {p.description && <p className="text-sm text-gray-600">{p.description}</p>}
              </div>
            ))}
          </section>
        ) : null}
      </div>
      <aside className="col-span-1 space-y-6">
        {resume.skills?.length ? (
          <section>
            <h3 className="font-semibold text-sm mb-2 uppercase tracking-wide" style={{ color: resume.accent_color || '#111827' }}>Core Competencies</h3>
            <div className="flex flex-wrap gap-2">
              {resume.skills.slice(0, 20).map((s, i) => (
                <span key={i} className="px-2 py-1 rounded border text-xs" style={{ borderColor: (resume.accent_color || '#111827') + '55' }}>{s.name}</span>
              ))}
            </div>
          </section>
        ) : null}
        {resume.education?.length ? (
          <section>
            <h3 className="font-semibold text-sm mb-2 uppercase tracking-wide" style={{ color: resume.accent_color || '#111827' }}>Education</h3>
            {resume.education.map((edu, i) => (
              <div key={i} className="mb-3">
                <div className="font-medium text-sm">{edu.degree}</div>
                <div className="text-xs text-gray-500">{edu.institution}</div>
              </div>
            ))}
          </section>
        ) : null}
        {resume.certificates?.length ? (
          <section>
            <h3 className="font-semibold text-sm mb-2 uppercase tracking-wide" style={{ color: resume.accent_color || '#111827' }}>Certifications</h3>
            <ul className="space-y-1 text-xs">
              {resume.certificates.slice(0, 6).map((c, i) => (
                <li key={i}>{c.name}</li>
              ))}
            </ul>
          </section>
        ) : null}
      </aside>
    </div>
  );
}

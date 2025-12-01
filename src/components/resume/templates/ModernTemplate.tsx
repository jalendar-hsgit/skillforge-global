import React from 'react';
import { Resume } from '../types';

export default function ModernTemplate({ resume }: { resume: Resume }) {
  const accent = resume.accent_color || '#1e40af'; // Blue-700
  return (
    <div className="modern-template bg-white grid grid-cols-3 gap-0" style={{ minHeight: '297mm', width: '210mm' }}>
      {/* Left Column */}
      <div
        className="col-span-1 flex flex-col bg-gradient-to-b from-gray-800 to-gray-600 text-white p-8"
        style={{ background: `linear-gradient(180deg, ${accent} 0%, ${accent}cc 100%)` }}
      >
        {/* Profile Photo */}
        {resume.photo_url && (
          <div className="w-32 h-32 rounded-full overflow-hidden mb-6 border-4 border-white shadow-xl mx-auto">
            <img src={resume.photo_url} alt="Profile" className="object-cover w-full h-full" />
          </div>
        )}

        {/* Contact Info */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center mr-3">
              <span className="text-lg">📧</span>
            </div>
            <h3 className="font-bold text-lg uppercase tracking-wider">Contact</h3>
          </div>
          {resume.email && <p className="text-sm mb-2 opacity-90">📧 {resume.email}</p>}
          {resume.phone && <p className="text-sm mb-2 opacity-90">📱 {resume.phone}</p>}
          {resume.location && <p className="text-sm mb-2 opacity-90">📍 {resume.location}</p>}
          {resume.linkedin && <p className="text-sm mb-2 opacity-90">💼 {resume.linkedin}</p>}
          {resume.website && <p className="text-sm opacity-90">🌐 {resume.website}</p>}
        </div>

        {/* Education */}
        {resume.education && resume.education.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center mr-3">
                <span className="text-lg">🎓</span>
              </div>
              <h3 className="font-bold text-lg uppercase tracking-wider">Education</h3>
            </div>
            {resume.education.map((edu: any, idx: number) => (
              <div key={idx} className="mb-4">
                <div className="font-semibold text-sm">{edu.degree}</div>
                <div className="text-xs opacity-80">{edu.institution}</div>
                {edu.graduation_date && (
                  <div className="text-xs opacity-70 mt-1">{edu.graduation_date}</div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Languages */}
        {resume.languages && resume.languages.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center mr-3">
                <span className="text-lg">🌍</span>
              </div>
              <h3 className="font-bold text-lg uppercase tracking-wider">Languages</h3>
            </div>
            {resume.languages.map((lang: any, idx: number) => (
              <div key={idx} className="flex justify-between text-sm mb-2">
                <span>{lang.name}</span>
                {lang.proficiency && <span className="opacity-80">{lang.proficiency}</span>}
              </div>
            ))}
          </div>
        )}

        {/* Skills */}
        {resume.skills && resume.skills.length > 0 && (
          <div>
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center mr-3">
                <span className="text-lg">⚡</span>
              </div>
              <h3 className="font-bold text-lg uppercase tracking-wider">Skills</h3>
            </div>
            {resume.skills.map((skill: any, idx: number) => (
              <div key={idx} className="mb-3">
                <div className="text-sm font-medium mb-1">{skill.name}</div>
                {skill.level && (
                  <div className="w-full bg-white/20 rounded-full h-1.5">
                    <div
                      className="bg-white h-1.5 rounded-full"
                      style={{
                        width:
                          skill.level === 'Expert'
                            ? '100%'
                            : skill.level === 'Advanced'
                            ? '80%'
                            : skill.level === 'Intermediate'
                            ? '60%'
                            : '40%',
                      }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right Column */}
      <div className="col-span-2 p-10">
        <div className="mb-8">
          <h1 className="text-5xl font-extrabold mb-2" style={{ color: accent }}>
            {resume.full_name || 'Your Name'}
          </h1>
          <h2 className="text-2xl font-semibold text-gray-600">
            {resume.title || 'Professional Title'}
          </h2>
          <div className="w-20 h-1 mt-3" style={{ backgroundColor: accent }}></div>
        </div>

        {/* Summary */}
        {resume.professional_summary && (
          <section className="mb-8">
            <h3
              className="font-bold text-xl mb-3 pb-2 border-b-2"
              style={{ color: accent, borderColor: accent }}
            >
              PROFESSIONAL SUMMARY
            </h3>
            <p className="text-gray-700 leading-relaxed text-sm">
              {resume.professional_summary}
            </p>
          </section>
        )}

        {/* Work Experience */}
        {resume.work_experiences && resume.work_experiences.length > 0 && (
          <section className="mb-8">
            <h3
              className="font-bold text-xl mb-3 pb-2 border-b-2"
              style={{ color: accent, borderColor: accent }}
            >
              WORK EXPERIENCE
            </h3>
            {resume.work_experiences.map((exp: any, idx: number) => (
              <div key={idx} className="mb-5 relative pl-6">
                <div
                  className="absolute left-0 top-2 w-2 h-2 rounded-full"
                  style={{ backgroundColor: accent }}
                ></div>
                <div className="font-bold text-base">{exp.position}</div>
                <div className="font-semibold text-gray-700 text-sm">{exp.company}</div>
                <div className="text-xs text-gray-500 mb-2">
                  {exp.start_date} - {exp.end_date || 'Present'}
                </div>
                <p className="text-sm text-gray-700 leading-relaxed">{exp.description}</p>
                {exp.achievements && exp.achievements.length > 0 && (
                  <ul className="list-disc list-inside mt-2 text-sm text-gray-600">
                    {exp.achievements.map((ach: any, i: number) => (
                      <li key={i}>{typeof ach === 'string' ? ach : (ach.title || ach.description || '')}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </section>
        )}

        {/* Projects */}
        {resume.projects && resume.projects.length > 0 && (
          <section className="mb-8">
            <h3
              className="font-bold text-xl mb-3 pb-2 border-b-2"
              style={{ color: accent, borderColor: accent }}
            >
              PROJECTS
            </h3>
            {resume.projects.map((proj: any, idx: number) => (
              <div key={idx} className="mb-4">
                <div className="font-bold text-base">{proj.name}</div>
                <p className="text-sm text-gray-700 mt-1">{proj.description}</p>
                {proj.technologies && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {proj.technologies.split(',').map((tech: string, i: number) => (
                      <span
                        key={i}
                        className="px-2 py-1 text-xs rounded"
                        style={{ backgroundColor: `${accent}20`, color: accent }}
                      >
                        {tech.trim()}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </section>
        )}

        {/* Achievements */}
        {resume.achievements && resume.achievements.length > 0 && (
          <section className="mb-8">
            <h3
              className="font-bold text-xl mb-3 pb-2 border-b-2"
              style={{ color: accent, borderColor: accent }}
            >
              ACHIEVEMENTS
            </h3>
            <ul className="list-disc pl-5 space-y-2">
              {resume.achievements.map((ach: any, idx: number) => (
                <li key={idx} className="text-sm text-gray-700">
                  <span className="font-semibold">{ach.title}</span>
                  {ach.description && <p className="text-xs text-gray-600 mt-0.5">{ach.description}</p>}
                  {ach.date && <p className="text-xs text-gray-500">{ach.date}</p>}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Certificates */}
        {resume.certificates && resume.certificates.length > 0 && (
          <section>
            <h3
              className="font-bold text-xl mb-3 pb-2 border-b-2"
              style={{ color: accent, borderColor: accent }}
            >
              CERTIFICATIONS
            </h3>
            {resume.certificates.map((cert: any, idx: number) => (
              <div key={idx} className="mb-3">
                <div className="font-semibold text-sm">{cert.name}</div>
                <div className="text-xs text-gray-600">
                  {cert.issuer} • {cert.date}
                </div>
              </div>
            ))}
          </section>
        )}
      </div>
    </div>
  );
}

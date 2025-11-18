import React from 'react';
import { Resume } from '../types';

export default function ModernTemplate({ resume }: { resume: Resume }) {
  return (
    <div className="modern-template p-8 bg-white rounded-xl shadow-lg grid grid-cols-3 gap-8">
      {/* Left Column */}
      <div className="col-span-1 flex flex-col items-center bg-gradient-to-b from-blue-700 to-blue-400 text-white rounded-xl p-6">
        {/* Profile Photo */}
        {resume.photo_url && (
          <div className="w-28 h-28 rounded-full overflow-hidden mb-4 border-4 border-white">
            <img src={resume.photo_url} alt="Profile" className="object-cover w-full h-full" />
          </div>
        )}
        {/* Contact Info */}
        <div className="mb-6">
          <h3 className="font-bold text-lg mb-2">Contact</h3>
          <p>{resume.email}</p>
          <p>{resume.phone}</p>
          <p>{resume.location}</p>
        </div>
        {/* Education */}
        <div className="mb-6">
          <h3 className="font-bold text-lg mb-2">Education</h3>
          {resume.education?.map((edu, idx) => (
            <div key={idx} className="mb-2">
              <div className="font-semibold">{edu.degree}</div>
              <div className="text-sm">{edu.institution}</div>
            </div>
          ))}
        </div>
        {/* Languages */}
        <div className="mb-6">
          <h3 className="font-bold text-lg mb-2">Languages</h3>
          {resume.languages?.map((lang, idx) => (
            <div key={idx} className="text-sm">{lang.name} {lang.level && `- ${lang.level}`}</div>
          ))}
        </div>
        {/* Skills */}
        <div>
          <h3 className="font-bold text-lg mb-2">Skills</h3>
          {resume.skills?.map((skill, idx) => (
            <div key={idx} className="text-sm mb-1">{skill.name}</div>
          ))}
        </div>
      </div>
      {/* Right Column */}
      <div className="col-span-2 p-6">
        <h1 className="text-4xl font-extrabold text-blue-700 mb-2">{resume.full_name}</h1>
        <h2 className="text-xl font-semibold text-blue-400 mb-4">{resume.title}</h2>
        {/* Summary */}
        {resume.professional_summary && (
          <section className="mb-6">
            <h3 className="font-bold text-lg text-blue-700 mb-2 border-b-2 pb-1" style={{ borderColor: '#14b8a6' }}>About Me</h3>
            <p className="text-gray-700 leading-relaxed">{resume.professional_summary}</p>
          </section>
        )}
        {/* Work Experience */}
        <section className="mb-6">
          <h3 className="font-bold text-lg text-blue-700 mb-2 border-b-2 pb-1" style={{ borderColor: '#14b8a6' }}>Work Experience</h3>
          {resume.work_experiences?.map((exp, idx) => (
            <div key={idx} className="mb-4">
              <div className="font-semibold">{exp.position} - {exp.company}</div>
              <div className="text-sm text-gray-500">{exp.start_date} - {exp.end_date}</div>
              <div className="text-sm">{exp.description}</div>
            </div>
          ))}
        </section>
        {/* Achievements */}
        {resume.achievements?.length > 0 && (
          <section className="mb-6">
            <h3 className="font-bold text-lg text-blue-700 mb-2 border-b-2 pb-1" style={{ borderColor: '#14b8a6' }}>Achievements</h3>
            <ul className="list-disc pl-5">
              {resume.achievements.map((ach, idx) => (
                <li key={idx}>{ach}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  );
}

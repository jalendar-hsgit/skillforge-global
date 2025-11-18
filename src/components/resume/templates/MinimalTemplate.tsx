import React from 'react';
import { Resume } from '../types';

export default function MinimalTemplate({ resume }: { resume: Resume }) {
  return (
    <div className="minimal-template p-8 bg-white rounded-xl shadow grid grid-cols-3 gap-8">
      {/* Sidebar */}
      <div className="col-span-1 flex flex-col items-center bg-gray-900 text-white rounded-xl p-6">
        <h1 className="text-3xl font-bold mb-2">{resume.full_name}</h1>
        <h2 className="text-lg font-semibold mb-4">{resume.title}</h2>
        <div className="mb-6">
          <h3 className="font-bold text-base mb-2">Contact</h3>
          <p>{resume.email}</p>
          <p>{resume.phone}</p>
          <p>{resume.location}</p>
        </div>
        <div className="mb-6">
          <h3 className="font-bold text-base mb-2">Languages</h3>
          {resume.languages?.map((lang, idx) => (
            <div key={idx} className="text-sm">{lang.name} {lang.level && `- ${lang.level}`}</div>
          ))}
        </div>
        <div>
          <h3 className="font-bold text-base mb-2">References</h3>
          {resume.references?.map((ref, idx) => (
            <div key={idx} className="text-sm mb-1">{ref.name} - {ref.position}</div>
          ))}
        </div>
      </div>
      {/* Main Content */}
      <div className="col-span-2 p-6">
        {resume.professional_summary && (
          <section className="mb-6">
            <h3 className="font-bold text-lg text-gray-900 mb-2">Profile</h3>
            <p className="text-gray-700 leading-relaxed">{resume.professional_summary}</p>
          </section>
        )}
        <section className="mb-6">
          <h3 className="font-bold text-lg text-gray-900 mb-2">Experience</h3>
          {resume.work_experiences?.map((exp, idx) => (
            <div key={idx} className="mb-4">
              <div className="font-semibold">{exp.position} - {exp.company}</div>
              <div className="text-sm text-gray-500">{exp.start_date} - {exp.end_date}</div>
              <div className="text-sm">{exp.description}</div>
            </div>
          ))}
        </section>
        <section className="mb-6">
          <h3 className="font-bold text-lg text-gray-900 mb-2">Education</h3>
          {resume.education?.map((edu, idx) => (
            <div key={idx} className="mb-2">
              <div className="font-semibold">{edu.degree}</div>
              <div className="text-sm">{edu.institution}</div>
            </div>
          ))}
        </section>
        <section>
          <h3 className="font-bold text-lg text-gray-900 mb-2">Expertise</h3>
          {resume.skills?.map((skill, idx) => (
            <div key={idx} className="text-sm mb-1">{skill.name}</div>
          ))}
        </section>
      </div>
    </div>
  );
}

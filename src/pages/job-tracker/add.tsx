'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/router';
import Head from 'next/head';
import Layout from '@/components/Layout';
import { API_BASE } from '@/lib/apiBase';
import { Save, ArrowLeft, Plus, Trash2, Calendar, X } from 'lucide-react';

// Force this page to be SSR to avoid static export errors for dynamic routes
export async function getServerSideProps() {
  return { props: {} };
}

interface Interview {
  date: string;
  type: string;
  interviewer?: string;
  notes?: string;
  status?: string;
}

interface Contact {
  name: string;
  role?: string;
  email?: string;
  phone?: string;
  linkedin?: string;
}

interface JobApplicationForm {
  company_name: string;
  position_title: string;
  job_type: string;
  location: string;
  work_mode: string;
  job_url: string;
  description: string;
  status: string;
  priority: number;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  resume_id?: number;
  cover_letter_url: string;
  portfolio_url: string;
  application_date: string;
  deadline: string;
  response_date: string;
  skills_required: string[];
  skills_matched: string[];
  notes: string;
  follow_up_date: string;
  source: string;
  referral_name: string;
  interviews: Interview[];
  contacts: Contact[];
}

export default function JobApplicationForm() {
  const router = useRouter();
  const { id } = useParams();
  const isEditing = !!id;

  const [form, setForm] = useState<JobApplicationForm>({
    company_name: '',
    position_title: '',
    job_type: 'full_time',
    location: '',
    work_mode: 'remote',
    job_url: '',
    description: '',
    status: 'applied',
    priority: 3,
    salary_min: undefined,
    salary_max: undefined,
    salary_currency: 'USD',
    resume_id: undefined,
    cover_letter_url: '',
    portfolio_url: '',
    application_date: new Date().toISOString().split('T')[0],
    deadline: '',
    response_date: '',
    skills_required: [],
    skills_matched: [],
    notes: '',
    follow_up_date: '',
    source: '',
    referral_name: '',
    interviews: [],
    contacts: [],
  });

  const [skillInput, setSkillInput] = useState('');
  const [interviewInput, setInterviewInput] = useState<Interview>({
    date: '',
    type: 'phone',
    interviewer: '',
    notes: '',
  });
  const [contactInput, setContactInput] = useState<Contact>({
    name: '',
    role: '',
    email: '',
    phone: '',
    linkedin: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isEditing) {
      fetchApplication();
    }
  }, [id, isEditing]);

  const fetchApplication = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1x/job-applications/${id}`, {
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        setForm({
          ...data,
          application_date: data.application_date?.split('T')[0] || '',
          deadline: data.deadline?.split('T')[0] || '',
          response_date: data.response_date?.split('T')[0] || '',
          follow_up_date: data.follow_up_date?.split('T')[0] || '',
        });
      }
    } catch (err) {
      console.error('Error fetching application:', err);
      setError('Failed to load application');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: name === 'priority' || name === 'salary_min' || name === 'salary_max' ? 
        (value ? Number(value) : undefined) : value
    }));
  };

  const handleAddSkill = () => {
    if (skillInput.trim()) {
      setForm(prev => ({
        ...prev,
        skills_required: [...prev.skills_required, skillInput.trim()]
      }));
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skill: string) => {
    setForm(prev => ({
      ...prev,
      skills_required: prev.skills_required.filter(s => s !== skill)
    }));
  };

  const handleAddInterview = () => {
    if (interviewInput.date) {
      setForm(prev => ({
        ...prev,
        interviews: [...prev.interviews, interviewInput]
      }));
      setInterviewInput({ date: '', type: 'phone', interviewer: '', notes: '' });
    }
  };

  const handleRemoveInterview = (index: number) => {
    setForm(prev => ({
      ...prev,
      interviews: prev.interviews.filter((_, i) => i !== index)
    }));
  };

  const handleAddContact = () => {
    if (contactInput.name) {
      setForm(prev => ({
        ...prev,
        contacts: [...prev.contacts, contactInput]
      }));
      setContactInput({ name: '', role: '', email: '', phone: '', linkedin: '' });
    }
  };

  const handleRemoveContact = (index: number) => {
    setForm(prev => ({
      ...prev,
      contacts: prev.contacts.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const method = isEditing ? 'PATCH' : 'POST';
      const url = isEditing 
        ? `${API_BASE}/api/v1x/job-applications/${id}`
        : `${API_BASE}/api/v1x/job-applications`;

      const payload = {
        ...form,
        application_date: form.application_date ? new Date(form.application_date + 'T00:00:00Z').toISOString() : undefined,
        deadline: form.deadline ? new Date(form.deadline + 'T00:00:00Z').toISOString() : undefined,
        response_date: form.response_date ? new Date(form.response_date + 'T00:00:00Z').toISOString() : undefined,
        follow_up_date: form.follow_up_date ? new Date(form.follow_up_date + 'T00:00:00Z').toISOString() : undefined,
      };

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        router.push(`/job-tracker/${data.id}`);
      } else {
        const errorData = await res.json();
        setError(errorData.detail || 'Failed to save application');
      }
    } catch (err) {
      console.error('Error saving application:', err);
      setError('An error occurred while saving');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>{isEditing ? 'Edit' : 'Add'} Job Application | SkillForge Global</title>
      </Head>

      <Layout>
        <div className="max-w-4xl mx-auto px-4 py-8">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </button>

          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            {isEditing ? 'Edit Job Application' : 'Add New Job Application'}
          </h1>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Information */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📋 Basic Information</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Company Name *</label>
                  <input
                    type="text"
                    name="company_name"
                    value={form.company_name}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Google, Microsoft, Startup Inc"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Position Title *</label>
                  <input
                    type="text"
                    name="position_title"
                    value={form.position_title}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Senior Software Engineer"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Job Type</label>
                  <select
                    name="job_type"
                    value={form.job_type}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="full_time">Full Time</option>
                    <option value="part_time">Part Time</option>
                    <option value="contract">Contract</option>
                    <option value="internship">Internship</option>
                    <option value="freelance">Freelance</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Location</label>
                  <input
                    type="text"
                    name="location"
                    value={form.location}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., San Francisco, CA"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Work Mode</label>
                  <select
                    name="work_mode"
                    value={form.work_mode}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="remote">Remote</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="onsite">Onsite</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Priority</label>
                  <select
                    name="priority"
                    value={form.priority}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {[1, 2, 3, 4, 5].map(p => (
                      <option key={p} value={p}>{p}/5 - {
                        p === 5 ? 'Critical' : p === 4 ? 'High' : p === 3 ? 'Medium' : p === 2 ? 'Low' : 'Very Low'
                      }</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">Job URL</label>
                <input
                  type="url"
                  name="job_url"
                  value={form.job_url}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://..."
                />
              </div>

              <div className="mt-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">Job Description</label>
                <textarea
                  name="description"
                  value={form.description}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Paste the job description here..."
                />
              </div>
            </div>

            {/* Status and Dates */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📅 Status & Dates</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Status</label>
                  <select
                    name="status"
                    value={form.status}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="wishlist">Wishlist</option>
                    <option value="applied">Applied</option>
                    <option value="screening">Screening</option>
                    <option value="interview">Interview</option>
                    <option value="assessment">Assessment</option>
                    <option value="offer">Offer</option>
                    <option value="accepted">Accepted</option>
                    <option value="rejected">Rejected</option>
                    <option value="withdrawn">Withdrawn</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Application Date</label>
                  <input
                    type="date"
                    name="application_date"
                    value={form.application_date}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Deadline</label>
                  <input
                    type="date"
                    name="deadline"
                    value={form.deadline}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Response Date</label>
                  <input
                    type="date"
                    name="response_date"
                    value={form.response_date}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Follow-up Date</label>
                  <input
                    type="date"
                    name="follow_up_date"
                    value={form.follow_up_date}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Source</label>
                  <input
                    type="text"
                    name="source"
                    value={form.source}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="LinkedIn, Indeed, Company Website, etc."
                  />
                </div>
              </div>
            </div>

            {/* Salary Information */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">💰 Salary Information</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Min Salary</label>
                  <input
                    type="number"
                    name="salary_min"
                    value={form.salary_min || ''}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 100000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Max Salary</label>
                  <input
                    type="number"
                    name="salary_max"
                    value={form.salary_max || ''}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 150000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Currency</label>
                  <input
                    type="text"
                    name="salary_currency"
                    value={form.salary_currency}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Skills */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🛠️ Skills Required</h2>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSkill())}
                  placeholder="Add skill and press Enter"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="button"
                  onClick={handleAddSkill}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>

              <div className="flex flex-wrap gap-2">
                {form.skills_required.map((skill, i) => (
                  <div key={i} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full flex items-center gap-2">
                    {skill}
                    <button
                      type="button"
                      onClick={() => handleRemoveSkill(skill)}
                      className="ml-1"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Interviews */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🎯 Interviews</h2>

              <div className="space-y-3 mb-4">
                <input
                  type="datetime-local"
                  value={interviewInput.date}
                  onChange={(e) => setInterviewInput({...interviewInput, date: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <select
                  value={interviewInput.type}
                  onChange={(e) => setInterviewInput({...interviewInput, type: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="phone">Phone</option>
                  <option value="video">Video</option>
                  <option value="in-person">In-Person</option>
                  <option value="technical">Technical</option>
                </select>

                <input
                  type="text"
                  value={interviewInput.interviewer}
                  onChange={(e) => setInterviewInput({...interviewInput, interviewer: e.target.value})}
                  placeholder="Interviewer name"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <textarea
                  value={interviewInput.notes}
                  onChange={(e) => setInterviewInput({...interviewInput, notes: e.target.value})}
                  placeholder="Interview notes"
                  rows={2}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <button
                  type="button"
                  onClick={handleAddInterview}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <Plus className="w-5 h-5" />
                  Add Interview
                </button>
              </div>

              {form.interviews.map((interview, i) => (
                <div key={i} className="bg-gray-50 p-3 rounded-lg mb-2 flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{interview.type} - {new Date(interview.date).toLocaleString()}</p>
                    {interview.interviewer && <p className="text-sm text-gray-600">Interviewer: {interview.interviewer}</p>}
                    {interview.notes && <p className="text-sm text-gray-600">Notes: {interview.notes}</p>}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveInterview(i)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>

            {/* Contacts */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">👥 Contacts</h2>

              <div className="space-y-3 mb-4">
                <input
                  type="text"
                  value={contactInput.name}
                  onChange={(e) => setContactInput({...contactInput, name: e.target.value})}
                  placeholder="Contact name"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <input
                  type="text"
                  value={contactInput.role}
                  onChange={(e) => setContactInput({...contactInput, role: e.target.value})}
                  placeholder="Role (e.g., Hiring Manager)"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <input
                  type="email"
                  value={contactInput.email}
                  onChange={(e) => setContactInput({...contactInput, email: e.target.value})}
                  placeholder="Email"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <input
                  type="tel"
                  value={contactInput.phone}
                  onChange={(e) => setContactInput({...contactInput, phone: e.target.value})}
                  placeholder="Phone"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <input
                  type="url"
                  value={contactInput.linkedin}
                  onChange={(e) => setContactInput({...contactInput, linkedin: e.target.value})}
                  placeholder="LinkedIn URL"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <button
                  type="button"
                  onClick={handleAddContact}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <Plus className="w-5 h-5" />
                  Add Contact
                </button>
              </div>

              {form.contacts.map((contact, i) => (
                <div key={i} className="bg-gray-50 p-3 rounded-lg mb-2 flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{contact.name}</p>
                    {contact.role && <p className="text-sm text-gray-600">{contact.role}</p>}
                    {contact.email && <p className="text-sm text-gray-600">{contact.email}</p>}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveContact(i)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>

            {/* Notes */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📝 Notes</h2>
              <textarea
                name="notes"
                value={form.notes}
                onChange={handleChange}
                rows={4}
                placeholder="Add any additional notes..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Submit */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
              >
                <Save className="w-5 h-5" />
                {loading ? 'Saving...' : isEditing ? 'Update Application' : 'Create Application'}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </Layout>
    </>
  );
}

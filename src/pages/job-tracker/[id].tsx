'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/router';
import Head from 'next/head';
import Layout from '@/components/Layout';
import { API_BASE } from '@/lib/apiBase';
import { ArrowLeft, Edit, Trash2, Download, Share2, MessageSquare, Calendar, MapPin, DollarSign, Briefcase, Clock, TrendingUp } from 'lucide-react';

interface JobApplication {
  id: number;
  company_name: string;
  position_title: string;
  job_type: string;
  location?: string;
  work_mode?: string;
  job_url?: string;
  description?: string;
  status: string;
  priority: number;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  resume_id?: number;
  cover_letter_url?: string;
  portfolio_url?: string;
  application_date: string;
  deadline?: string;
  response_date?: string;
  follow_up_date?: string;
  interviews: Array<{date: string; type: string; interviewer?: string; notes?: string; status?: string}>;
  contacts: Array<{name: string; role?: string; email?: string; phone?: string; linkedin?: string}>;
  skills_required: string[];
  skills_matched: string[];
  notes?: string;
  source?: string;
  created_at: string;
  updated_at: string;
  days_since_applied?: number;
  is_overdue: boolean;
  response_time_days?: number;
}

const statusColors: Record<string, string> = {
  wishlist: 'bg-gray-100 text-gray-800 border-gray-300',
  applied: 'bg-blue-100 text-blue-800 border-blue-300',
  screening: 'bg-purple-100 text-purple-800 border-purple-300',
  interview: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  assessment: 'bg-indigo-100 text-indigo-800 border-indigo-300',
  offer: 'bg-green-100 text-green-800 border-green-300',
  accepted: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  rejected: 'bg-red-100 text-red-800 border-red-300',
  withdrawn: 'bg-slate-100 text-slate-800 border-slate-300',
};

const statusEmojis: Record<string, string> = {
  wishlist: '⭐',
  applied: '📨',
  screening: '👀',
  interview: '🎯',
  assessment: '✍️',
  offer: '🎉',
  accepted: '✅',
  rejected: '❌',
  withdrawn: '🚫',
};

export default function JobApplicationDetail() {
  const router = useRouter();
  const { id } = useParams();

  const [application, setApplication] = useState<JobApplication | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (id) {
      fetchApplication();
    }
  }, [id]);

  const fetchApplication = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1x/job-applications/${id}`, {
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        setApplication(data);
      }
    } catch (error) {
      console.error('Error fetching application:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this application?')) return;

    try {
      setDeleting(true);
      const res = await fetch(`${API_BASE}/api/v1x/job-applications/${id}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (res.ok) {
        router.push('/job-tracker');
      }
    } catch (error) {
      console.error('Error deleting application:', error);
      alert('Failed to delete application');
    } finally {
      setDeleting(false);
    }
  };

  const exportToCSV = () => {
    if (!application) return;

    const headers = ['Field', 'Value'];
    const rows = [
      ['Company', application.company_name],
      ['Position', application.position_title],
      ['Status', application.status],
      ['Priority', application.priority],
      ['Location', application.location || 'N/A'],
      ['Work Mode', application.work_mode || 'N/A'],
      ['Job Type', application.job_type],
      ['Salary', `$${application.salary_min}k - $${application.salary_max}k (${application.salary_currency})`],
      ['Application Date', new Date(application.application_date).toLocaleDateString()],
      ['Days Since Applied', application.days_since_applied || 'N/A'],
      ['Response Time', application.response_time_days ? `${application.response_time_days} days` : 'No response'],
      ['Source', application.source || 'N/A'],
      ['Skills Required', application.skills_required.join(', ')],
      ['Interviews', application.interviews.length],
      ['Contacts', application.contacts.length],
    ];

    let csv = headers.join(',') + '\n';
    rows.forEach(row => {
      csv += row.map(field => `"${field}"`).join(',') + '\n';
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${application.company_name}-${application.position_title}-${Date.now()}.csv`;
    a.click();
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading application...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!application) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto px-4 py-8 text-center">
          <p className="text-gray-600 text-lg">Application not found</p>
          <button
            onClick={() => router.push('/job-tracker')}
            className="mt-4 text-blue-600 hover:text-blue-700 font-semibold"
          >
            Back to Job Tracker
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <>
      <Head>
        <title>{application.position_title} at {application.company_name} | Job Tracker</title>
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

          {/* Header */}
          <div className="bg-white rounded-lg border border-gray-200 p-8 mb-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-4xl">{statusEmojis[application.status]}</span>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">{application.position_title}</h1>
                    <p className="text-xl text-gray-600">{application.company_name}</p>
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => router.push(`/job-tracker/${application.id}/edit`)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <Edit className="w-5 h-5" />
                  Edit
                </button>
                <button
                  onClick={handleDelete}
                  disabled={deleting}
                  className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  <Trash2 className="w-5 h-5" />
                  Delete
                </button>
                <button
                  onClick={exportToCSV}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  <Download className="w-5 h-5" />
                  Export
                </button>
              </div>
            </div>

            <div className="flex flex-wrap gap-4 items-center">
              <span className={`px-4 py-2 rounded-full font-semibold border ${statusColors[application.status]}`}>
                {application.status.charAt(0).toUpperCase() + application.status.slice(1)}
              </span>
              <span className="text-sm bg-gray-100 text-gray-800 px-3 py-1 rounded-full font-semibold">
                Priority: {application.priority}/5
              </span>
              {application.is_overdue && (
                <span className="text-sm bg-red-100 text-red-800 px-3 py-1 rounded-full font-semibold">
                  ⚠️ Overdue Follow-up
                </span>
              )}
            </div>
          </div>

          {/* Key Information Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {application.location && (
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center gap-3">
                  <MapPin className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">Location</p>
                    <p className="font-semibold text-gray-900">{application.location}</p>
                  </div>
                </div>
              </div>
            )}

            {application.salary_min && application.salary_max && (
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center gap-3">
                  <DollarSign className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">Salary</p>
                    <p className="font-semibold text-gray-900">${application.salary_min}k - ${application.salary_max}k</p>
                  </div>
                </div>
              </div>
            )}

            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="text-sm text-gray-600">Applied</p>
                  <p className="font-semibold text-gray-900">{new Date(application.application_date).toLocaleDateString()}</p>
                </div>
              </div>
            </div>

            {application.response_time_days !== undefined && application.response_date && (
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-orange-600" />
                  <div>
                    <p className="text-sm text-gray-600">Response Time</p>
                    <p className="font-semibold text-gray-900">{application.response_time_days} days</p>
                  </div>
                </div>
              </div>
            )}

            {application.deadline && (
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center gap-3">
                  <TrendingUp className="w-5 h-5 text-red-600" />
                  <div>
                    <p className="text-sm text-gray-600">Deadline</p>
                    <p className="font-semibold text-gray-900">{new Date(application.deadline).toLocaleDateString()}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <Briefcase className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-sm text-gray-600">Job Type</p>
                  <p className="font-semibold text-gray-900">{application.job_type.replace(/_/g, ' ')}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Job Description */}
          {application.description && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📄 Job Description</h2>
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{application.description}</p>
              </div>
            </div>
          )}

          {/* Skills */}
          {application.skills_required.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🛠️ Required Skills</h2>
              <div className="flex flex-wrap gap-2">
                {application.skills_required.map((skill, i) => (
                  <span
                    key={i}
                    className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Interviews */}
          {application.interviews.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🎯 Interviews ({application.interviews.length})</h2>
              <div className="space-y-3">
                {application.interviews.map((interview, i) => (
                  <div key={i} className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                    <p className="font-semibold text-gray-900">{interview.type.toUpperCase()}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(interview.date).toLocaleString()}
                    </p>
                    {interview.interviewer && (
                      <p className="text-sm text-gray-600">Interviewer: {interview.interviewer}</p>
                    )}
                    {interview.notes && (
                      <p className="text-sm text-gray-700 mt-2">{interview.notes}</p>
                    )}
                    {interview.status && (
                      <p className="text-sm font-semibold text-gray-700 mt-2">Status: {interview.status}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Contacts */}
          {application.contacts.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">👥 Contacts ({application.contacts.length})</h2>
              <div className="space-y-3">
                {application.contacts.map((contact, i) => (
                  <div key={i} className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                    <p className="font-semibold text-gray-900">{contact.name}</p>
                    {contact.role && (
                      <p className="text-sm text-gray-600">{contact.role}</p>
                    )}
                    {contact.email && (
                      <p className="text-sm text-blue-600">
                        <a href={`mailto:${contact.email}`}>{contact.email}</a>
                      </p>
                    )}
                    {contact.phone && (
                      <p className="text-sm text-gray-600">{contact.phone}</p>
                    )}
                    {contact.linkedin && (
                      <p className="text-sm text-blue-600">
                        <a href={contact.linkedin} target="_blank" rel="noopener noreferrer">
                          LinkedIn Profile
                        </a>
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Notes */}
          {application.notes && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📝 Notes</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{application.notes}</p>
            </div>
          )}

          {/* Links */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">🔗 Links</h2>
            <div className="space-y-2">
              {application.job_url && (
                <a
                  href={application.job_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-blue-600 hover:text-blue-700 truncate"
                >
                  Job Posting
                </a>
              )}
              {application.portfolio_url && (
                <a
                  href={application.portfolio_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-blue-600 hover:text-blue-700 truncate"
                >
                  Portfolio/Project Link
                </a>
              )}
              {!application.job_url && !application.portfolio_url && (
                <p className="text-gray-500">No links added</p>
              )}
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}

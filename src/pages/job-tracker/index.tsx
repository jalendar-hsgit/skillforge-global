'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Layout from '@/components/Layout';
import { API_BASE } from '@/lib/apiBase';
import { Briefcase, Plus, Filter, Calendar, TrendingUp, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface JobApplication {
  id: number;
  company_name: string;
  position_title: string;
  status: string;
  priority: number;
  salary_min?: number;
  salary_max?: number;
  location?: string;
  application_date: string;
  response_date?: string;
  deadline?: string;
  follow_up_date?: string;
  is_overdue: boolean;
  days_since_applied?: number;
  response_time_days?: number;
}

interface Stats {
  total_applications: number;
  response_rate: number;
  applications_this_month: number;
  offers_received: number;
  interviews_scheduled: number;
  overdue_follow_ups: number;
  avg_response_time_days?: number;
}

type ViewMode = 'kanban' | 'list' | 'calendar';
type StatusFilter = 'all' | 'wishlist' | 'applied' | 'screening' | 'interview' | 'assessment' | 'offer' | 'accepted' | 'rejected' | 'withdrawn';

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

export default function JobTrackerDashboard() {
  const router = useRouter();
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [priorityFilter, setPriorityFilter] = useState<number | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchData();
  }, [statusFilter, priorityFilter, searchTerm]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch applications
      const params = new URLSearchParams();
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (priorityFilter !== 'all') params.append('priority', String(priorityFilter));
      if (searchTerm) params.append('search', searchTerm);
      
      const appRes = await fetch(`${API_BASE}/api/v1x/job-applications?${params}`, {
        credentials: 'include'
      });
      
      if (appRes.ok) {
        const data = await appRes.json();
        setApplications(Array.isArray(data) ? data : []);
      }
      
      // Fetch stats
      const statsRes = await fetch(`${API_BASE}/api/v1x/job-applications/stats`, {
        credentials: 'include'
      });
      
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (error) {
      console.error('Error fetching job applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddApplication = () => {
    router.push('/job-tracker/add');
  };

  const handleEditApplication = (id: number) => {
    router.push(`/job-tracker/${id}/edit`);
  };

  const handleViewApplication = (id: number) => {
    router.push(`/job-tracker/${id}`);
  };

  const filteredApplications = applications.filter(app => {
    if (statusFilter !== 'all' && app.status !== statusFilter) return false;
    if (priorityFilter !== 'all' && app.priority !== priorityFilter) return false;
    if (searchTerm && !app.company_name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !app.position_title.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  // Group applications by status for Kanban view
  const groupedByStatus = {
    wishlist: filteredApplications.filter(a => a.status === 'wishlist'),
    applied: filteredApplications.filter(a => a.status === 'applied'),
    screening: filteredApplications.filter(a => a.status === 'screening'),
    interview: filteredApplications.filter(a => a.status === 'interview'),
    assessment: filteredApplications.filter(a => a.status === 'assessment'),
    offer: filteredApplications.filter(a => a.status === 'offer'),
    accepted: filteredApplications.filter(a => a.status === 'accepted'),
    rejected: filteredApplications.filter(a => a.status === 'rejected'),
  };

  return (
    <>
      <Head>
        <title>Job Application Tracker | SkillForge Global</title>
        <meta name="description" content="Track and manage your job applications" />
      </Head>
      
      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-3">
                <Briefcase className="w-10 h-10 text-blue-600" />
                Job Application Tracker
              </h1>
              <p className="text-gray-600 mt-2">Track, manage, and optimize your job search</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => router.push('/job-tracker/settings')}
                className="flex items-center gap-2 bg-white border border-gray-300 text-gray-800 px-4 py-3 rounded-lg hover:bg-gray-50 transition"
              >
                <Calendar className="w-5 h-5 text-gray-600" />
                Settings
              </button>
              <button
                onClick={handleAddApplication}
                className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="w-5 h-5" />
                Add Application
              </button>
            </div>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Total Applications</p>
                    <p className="text-2xl font-bold text-blue-600">{stats.total_applications}</p>
                  </div>
                  <Briefcase className="w-8 h-8 text-blue-300" />
                </div>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Response Rate</p>
                    <p className="text-2xl font-bold text-green-600">{Math.round(stats.response_rate * 100)}%</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-300" />
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">This Month</p>
                    <p className="text-2xl font-bold text-purple-600">{stats.applications_this_month}</p>
                  </div>
                  <Calendar className="w-8 h-8 text-purple-300" />
                </div>
              </div>

              <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 p-4 rounded-lg border border-emerald-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Offers</p>
                    <p className="text-2xl font-bold text-emerald-600">{stats.offers_received}</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-emerald-300" />
                </div>
              </div>

              <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-4 rounded-lg border border-yellow-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Interviews</p>
                    <p className="text-2xl font-bold text-yellow-600">{stats.interviews_scheduled}</p>
                  </div>
                  <Clock className="w-8 h-8 text-yellow-300" />
                </div>
              </div>

              <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Overdue Follow-ups</p>
                    <p className="text-2xl font-bold text-red-600">{stats.overdue_follow_ups}</p>
                  </div>
                  <AlertCircle className="w-8 h-8 text-red-300" />
                </div>
              </div>
            </div>
          )}

          {/* Filters and Controls */}
          <div className="bg-white p-4 rounded-lg border border-gray-200 mb-8">
            <div className="flex items-center gap-4 flex-wrap">
              <Filter className="w-5 h-5 text-gray-600" />
              
              <input
                type="text"
                placeholder="Search company or position..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Statuses</option>
                <option value="wishlist">Wishlist</option>
                <option value="applied">Applied</option>
                <option value="screening">Screening</option>
                <option value="interview">Interview</option>
                <option value="assessment">Assessment</option>
                <option value="offer">Offer</option>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
              </select>

              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value === 'all' ? 'all' : Number(e.target.value))}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Priorities</option>
                <option value="5">Priority 5 (Critical)</option>
                <option value="4">Priority 4 (High)</option>
                <option value="3">Priority 3 (Medium)</option>
                <option value="2">Priority 2 (Low)</option>
                <option value="1">Priority 1 (Very Low)</option>
              </select>

              <div className="flex gap-2 ml-auto">
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-4 py-2 rounded-lg transition ${
                    viewMode === 'list'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  }`}
                >
                  List
                </button>
                <button
                  onClick={() => setViewMode('kanban')}
                  className={`px-4 py-2 rounded-lg transition ${
                    viewMode === 'kanban'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  }`}
                >
                  Kanban
                </button>
              </div>
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Loading applications...</p>
              </div>
            </div>
          )}

          {/* List View */}
          {!loading && viewMode === 'list' && (
            <div className="space-y-3">
              {filteredApplications.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
                  <Briefcase className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No applications found</p>
                  <button
                    onClick={handleAddApplication}
                    className="mt-4 text-blue-600 hover:text-blue-700 font-semibold"
                  >
                    Add your first application
                  </button>
                </div>
              ) : (
                filteredApplications.map((app) => (
                  <div
                    key={app.id}
                    onClick={() => handleViewApplication(app.id)}
                    className="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition cursor-pointer"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{statusEmojis[app.status] || '📋'}</span>
                          <div>
                            <h3 className="font-bold text-lg text-gray-900">{app.position_title}</h3>
                            <p className="text-gray-600">{app.company_name}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold border ${statusColors[app.status]}`}>
                            {app.status.charAt(0).toUpperCase() + app.status.slice(1)}
                          </span>
                          {app.is_overdue && (
                            <p className="text-red-600 text-sm font-semibold mt-1">⚠️ Overdue Follow-up</p>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      {app.location && (
                        <div>
                          <p className="text-gray-600">📍 Location</p>
                          <p className="font-semibold text-gray-900">{app.location}</p>
                        </div>
                      )}
                      {app.salary_min && app.salary_max && (
                        <div>
                          <p className="text-gray-600">💰 Salary</p>
                          <p className="font-semibold text-gray-900">${app.salary_min}k - ${app.salary_max}k</p>
                        </div>
                      )}
                      <div>
                        <p className="text-gray-600">📅 Applied</p>
                        <p className="font-semibold text-gray-900">
                          {app.days_since_applied} day{app.days_since_applied !== 1 ? 's' : ''} ago
                        </p>
                      </div>
                      {app.response_date && app.response_time_days !== undefined && (
                        <div>
                          <p className="text-gray-600">⏱️ Response Time</p>
                          <p className="font-semibold text-gray-900">{app.response_time_days} days</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Kanban View */}
          {!loading && viewMode === 'kanban' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(groupedByStatus).map(([status, apps]) => (
                <div key={status} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <span>{statusEmojis[status]}</span>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                    <span className="bg-gray-300 text-gray-800 text-xs rounded-full w-6 h-6 flex items-center justify-center ml-auto">
                      {apps.length}
                    </span>
                  </h3>
                  
                  <div className="space-y-3">
                    {apps.map((app) => (
                      <div
                        key={app.id}
                        onClick={() => handleViewApplication(app.id)}
                        className="bg-white p-3 rounded-lg border border-gray-300 hover:shadow-md transition cursor-pointer"
                      >
                        <p className="font-semibold text-gray-900 text-sm line-clamp-2">{app.position_title}</p>
                        <p className="text-gray-600 text-xs">{app.company_name}</p>
                        {app.priority && (
                          <div className="mt-2 pt-2 border-t border-gray-200">
                            <span className="text-xs font-semibold">Priority: {app.priority}/5</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { API_BASE } from '@/lib/apiBase';
import { useMe } from '@/hooks/useMe';

interface JobApplication {
  id: number;
  company_name: string;
  position_title: string;
  application_date: string;
  status: string;
  priority: number;
  job_url: string | null;
  description: string | null;
  salary_min: number | null;
  salary_max: number | null;
  location: string | null;
  job_type: string | null;
  notes: string | null;
  next_followup_date: string | null;
  interview_date: string | null;
  created_at: string;
  updated_at: string;
}

interface Stats {
  total: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  response_rate: number;
  avg_response_time: number | null;
}

const statusColors = {
  applied: 'bg-blue-100 text-blue-800',
  screening: 'bg-yellow-100 text-yellow-800',
  interviewing: 'bg-purple-100 text-purple-800',
  offered: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  accepted: 'bg-emerald-100 text-emerald-800',
  withdrawn: 'bg-gray-100 text-gray-800'
};

const priorityLabels = {
  1: { label: 'Low', color: 'text-gray-600' },
  2: { label: 'Medium', color: 'text-blue-600' },
  3: { label: 'High', color: 'text-orange-600' },
  4: { label: 'Urgent', color: 'text-red-600' }
};

export default function JobTrackerPage() {
  const router = useRouter();
  const { me, loading: meLoading } = useMe();
  
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('application_date');
  const [sortOrder, setSortOrder] = useState('desc');
  
  // View mode
  const [viewMode, setViewMode] = useState<'board' | 'list'>('board');

  useEffect(() => {
    if (me) {
      fetchApplications();
      fetchStats();
    }
  }, [me, statusFilter, priorityFilter, searchQuery, sortBy, sortOrder]);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);
      if (priorityFilter) params.append('priority', priorityFilter);
      if (searchQuery) params.append('search', searchQuery);
      params.append('sort_by', sortBy);
      params.append('order', sortOrder);

      const response = await fetch(
        `${API_BASE}/api/v1x/job-applications?${params.toString()}`,
        { credentials: 'include' }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch applications');
      }

      const data = await response.json();
      setApplications(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1x/job-applications/stats`,
        { credentials: 'include' }
      );

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getStatusBadge = (status: string) => {
    const colorClass = statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800';
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colorClass}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  const getPriorityIndicator = (priority: number) => {
    const { label, color } = priorityLabels[priority as keyof typeof priorityLabels] || priorityLabels[2];
    return (
      <span className={`text-sm font-medium ${color}`}>
        {'★'.repeat(priority)}{'☆'.repeat(4 - priority)} {label}
      </span>
    );
  };

  const groupByStatus = () => {
    const groups: Record<string, JobApplication[]> = {
      applied: [],
      screening: [],
      interviewing: [],
      offered: [],
      rejected: [],
      accepted: [],
      withdrawn: []
    };

    applications.forEach(app => {
      if (groups[app.status]) {
        groups[app.status].push(app);
      }
    });

    return groups;
  };

  if (meLoading || !me) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  const groupedApplications = viewMode === 'board' ? groupByStatus() : {};

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Job Application Tracker
              </h1>
              <p className="text-xl text-gray-600">
                Manage and track your job search
              </p>
            </div>
            <Button
              onClick={() => router.push('/jobs/new')}
              variant="primary"
            >
              + Add Application
            </Button>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">Total Applications</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
                </div>
              </Card>
              <Card>
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">In Progress</p>
                  <p className="text-3xl font-bold text-blue-600">
                    {(stats.by_status.screening || 0) + (stats.by_status.interviewing || 0)}
                  </p>
                </div>
              </Card>
              <Card>
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">Offers</p>
                  <p className="text-3xl font-bold text-green-600">
                    {stats.by_status.offered || 0}
                  </p>
                </div>
              </Card>
              <Card>
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">Response Rate</p>
                  <p className="text-3xl font-bold text-purple-600">
                    {stats.response_rate.toFixed(1)}%
                  </p>
                </div>
              </Card>
            </div>
          )}

          {/* Filters & View Toggle */}
          <Card className="mb-6">
            <div className="flex flex-wrap items-center gap-4">
              {/* Search */}
              <div className="flex-1 min-w-[200px]">
                <Input
                  type="text"
                  placeholder="Search companies or positions..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full"
                />
              </div>

              {/* Status Filter */}
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="applied">Applied</option>
                <option value="screening">Screening</option>
                <option value="interviewing">Interviewing</option>
                <option value="offered">Offered</option>
                <option value="rejected">Rejected</option>
                <option value="accepted">Accepted</option>
                <option value="withdrawn">Withdrawn</option>
              </select>

              {/* Priority Filter */}
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Priorities</option>
                <option value="1">Low</option>
                <option value="2">Medium</option>
                <option value="3">High</option>
                <option value="4">Urgent</option>
              </select>

              {/* View Mode Toggle */}
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('board')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    viewMode === 'board'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  Board
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    viewMode === 'list'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  List
                </button>
              </div>
            </div>
          </Card>

          {error && (
            <Card className="mb-6 bg-red-50 border-red-200">
              <p className="text-red-700">{error}</p>
            </Card>
          )}

          {/* Board View */}
          {viewMode === 'board' && (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {Object.entries(groupedApplications).map(([status, apps]) => (
                <div key={status} className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-gray-900 capitalize">
                      {status.replace('_', ' ')}
                    </h3>
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-semibold">
                      {apps.length}
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    {apps.map(app => (
                      <Card
                        key={app.id}
                        className="cursor-pointer hover:shadow-lg transition-shadow"
                        onClick={() => router.push(`/jobs/${app.id}`)}
                      >
                        <div className="space-y-2">
                          <h4 className="font-semibold text-gray-900 line-clamp-1">
                            {app.company_name}
                          </h4>
                          <p className="text-sm text-gray-600 line-clamp-2">
                            {app.position_title}
                          </p>
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>{formatDate(app.application_date)}</span>
                            {getPriorityIndicator(app.priority)}
                          </div>
                        </div>
                      </Card>
                    ))}
                    
                    {apps.length === 0 && (
                      <div className="text-center py-8 text-gray-400 text-sm">
                        No applications
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* List View */}
          {viewMode === 'list' && (
            <div className="space-y-4">
              {loading ? (
                <Card>
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                  </div>
                </Card>
              ) : applications.length === 0 ? (
                <Card className="text-center py-12">
                  <svg
                    className="w-16 h-16 text-gray-400 mx-auto mb-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                  </svg>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    No applications yet
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Start tracking your job applications
                  </p>
                  <Button
                    onClick={() => router.push('/jobs/new')}
                    variant="primary"
                  >
                    Add Your First Application
                  </Button>
                </Card>
              ) : (
                applications.map(app => (
                  <Card
                    key={app.id}
                    className="cursor-pointer hover:shadow-lg transition-shadow"
                    onClick={() => router.push(`/jobs/${app.id}`)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-4 mb-2">
                          <h3 className="text-xl font-bold text-gray-900">
                            {app.company_name}
                          </h3>
                          {getStatusBadge(app.status)}
                        </div>
                        <p className="text-lg text-gray-700 mb-2">
                          {app.position_title}
                        </p>
                        <div className="flex items-center gap-6 text-sm text-gray-600">
                          <span>📅 Applied: {formatDate(app.application_date)}</span>
                          {app.location && <span>📍 {app.location}</span>}
                          {app.job_type && <span>💼 {app.job_type}</span>}
                          {app.salary_min && app.salary_max && (
                            <span>💰 ${app.salary_min.toLocaleString()} - ${app.salary_max.toLocaleString()}</span>
                          )}
                        </div>
                      </div>
                      <div className="ml-4">
                        {getPriorityIndicator(app.priority)}
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

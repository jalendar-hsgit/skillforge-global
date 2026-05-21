import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import AdminHeader from '@/components/AdminHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/apiBase';
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth';
import { ChevronDown, User, Mail, DollarSign, CheckCircle, XCircle, Clock } from 'lucide-react';

interface MentorApplication {
  id: number;
  user_id: number;
  bio: string;
  expertise: string;
  hourly_rate: number;
  status: string;
  created_at: string;
  approved_at?: string;
  total_sessions?: number;
  average_rating?: number;
  user?: {
    email: string;
    full_name?: string;
  };
}

interface MentorStats {
  total: number;
  pending: number;
  approved: number;
  rejected: number;
  suspended: number;
  avg_rating: number;
  total_earnings: number;
}

export default function MentorAdminPage({ me }: AdminSSRProps) {
  const router = useRouter();
  const [applications, setApplications] = useState<MentorApplication[]>([]);
  const [stats, setStats] = useState<MentorStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected' | 'suspended'>('pending');
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    fetchData();
  }, [filter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      // Fetch both applications and stats in parallel
      const [appRes, statsRes] = await Promise.all([
        fetch(
          `${API_BASE}/api/v1x/admin/mentors/applications?status_filter=${filter === 'all' ? '' : filter}`,
          { credentials: 'include' }
        ),
        fetch(
          `${API_BASE}/api/v1x/admin/analytics?timeframe=30d`,
          { credentials: 'include' }
        )
      ]);

      if (appRes.status === 401 || statsRes.status === 401) {
        router.push('/login?redirect=/admin/mentors');
        return;
      }

      if (appRes.status === 403 || statsRes.status === 403) {
        setError('Access denied. Admin privileges required.');
        return;
      }

      if (!appRes.ok) {
        throw new Error('Failed to fetch applications');
      }

      const appData = await appRes.json();
      setApplications(appData.applications || appData || []);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateApplicationStatus = async (mentorId: number, status: 'approved' | 'rejected' | 'suspended') => {
    try {
      setProcessingId(mentorId);
      setError('');
      setSuccess('');

      const response = await fetch(
        `${API_BASE}/api/v1x/admin/mentors/${mentorId}/status`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ status })
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update status');
      }

      // Refresh applications
      await fetchData();
      setSuccess(`Mentor ${status === 'approved' ? 'approved' : status === 'rejected' ? 'rejected' : 'suspended'} successfully`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setProcessingId(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'suspended':
        return <XCircle className="w-5 h-5 text-orange-600" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      suspended: 'bg-orange-100 text-orange-800'
    };
    return (
      <div className="flex items-center gap-2">
        {getStatusIcon(status)}
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading && applications.length === 0) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading mentor data...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                🎓 Mentor Management
              </h1>
              <p className="text-xl text-gray-600">
                Review applications · Manage mentors · Signed in as {me.email}
              </p>
            </div>
            <Button
              onClick={() => router.push('/admin')}
              variant="outline"
            >
              ← Back to Admin
            </Button>
          </div>

          {error && (
            <Card className="mb-8 bg-red-50 border-red-200">
              <p className="text-red-700 font-medium">❌ {error}</p>
            </Card>
          )}

          {success && (
            <Card className="mb-8 bg-green-50 border-green-200">
              <p className="text-green-700 font-medium">✅ {success}</p>
            </Card>
          )}

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
              <Card className="bg-gradient-to-br from-blue-50 to-blue-100">
                <p className="text-sm text-blue-600 font-semibold mb-1">Total Mentors</p>
                <p className="text-3xl font-bold text-blue-900">{stats.total}</p>
              </Card>
              <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100">
                <p className="text-sm text-yellow-600 font-semibold mb-1">Pending</p>
                <p className="text-3xl font-bold text-yellow-900">{stats.pending}</p>
              </Card>
              <Card className="bg-gradient-to-br from-green-50 to-green-100">
                <p className="text-sm text-green-600 font-semibold mb-1">Approved</p>
                <p className="text-3xl font-bold text-green-900">{stats.approved}</p>
              </Card>
              <Card className="bg-gradient-to-br from-red-50 to-red-100">
                <p className="text-sm text-red-600 font-semibold mb-1">Rejected</p>
                <p className="text-3xl font-bold text-red-900">{stats.rejected}</p>
              </Card>
              <Card className="bg-gradient-to-br from-purple-50 to-purple-100">
                <p className="text-sm text-purple-600 font-semibold mb-1">Avg Rating</p>
                <p className="text-3xl font-bold text-purple-900">{(stats.avg_rating || 0).toFixed(1)}⭐</p>
              </Card>
            </div>
          )}

          {/* Filters */}
          <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
            {(['all', 'pending', 'approved', 'rejected', 'suspended'] as const).map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-6 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                  filter === f
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>

          {/* Applications List */}
          {applications.length === 0 ? (
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
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No applications found
              </h3>
              <p className="text-gray-600">
                {filter === 'pending' 
                  ? 'No pending applications to review' 
                  : `No ${filter} applications`}
              </p>
            </Card>
          ) : (
            <div className="space-y-4">
              {applications.map((app) => (
                <Card key={app.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                  <div
                    className="flex items-start justify-between p-4 cursor-pointer hover:bg-gray-50"
                    onClick={() => setExpandedId(expandedId === app.id ? null : app.id)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <User className="w-5 h-5 text-gray-400" />
                        <h3 className="text-lg font-bold text-gray-900">
                          {app.user?.full_name || 'Unknown User'}
                        </h3>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600 mb-2">
                        <Mail className="w-4 h-4" />
                        <p>{app.user?.email}</p>
                      </div>
                      <div className="flex items-center gap-3 text-sm text-gray-500">
                        <span>Applied: {formatDate(app.created_at)}</span>
                        {app.total_sessions !== undefined && (
                          <span>• {app.total_sessions} sessions</span>
                        )}
                        {app.average_rating !== undefined && (
                          <span>• {app.average_rating.toFixed(1)}★ rating</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {getStatusBadge(app.status)}
                      <ChevronDown
                        className={`w-5 h-5 text-gray-400 transition-transform ${
                          expandedId === app.id ? 'rotate-180' : ''
                        }`}
                      />
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {expandedId === app.id && (
                    <div className="border-t border-gray-200 p-4 bg-gray-50">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        {/* Bio */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-2">
                            Professional Bio
                          </h4>
                          <p className="text-gray-700 leading-relaxed text-sm">
                            {app.bio}
                          </p>
                        </div>

                        {/* Details */}
                        <div className="space-y-4">
                          <div>
                            <h4 className="text-sm font-semibold text-gray-700 mb-2">
                              Areas of Expertise
                            </h4>
                            <div className="flex flex-wrap gap-2">
                              {app.expertise.split(',').map((skill, idx) => (
                                <span
                                  key={idx}
                                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium"
                                >
                                  {skill.trim()}
                                </span>
                              ))}
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <DollarSign className="w-4 h-4 text-green-600" />
                            <div>
                              <h4 className="text-sm font-semibold text-gray-700">
                                Hourly Rate
                              </h4>
                              <p className="text-2xl font-bold text-green-600">
                                ${app.hourly_rate.toFixed(2)}/hr
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      {app.status === 'pending' && (
                        <div className="flex gap-3 pt-4 border-t border-gray-200">
                          <Button
                            onClick={() => updateApplicationStatus(app.id, 'approved')}
                            disabled={processingId === app.id}
                            className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium"
                          >
                            {processingId === app.id ? '⏳ Processing...' : '✓ Approve Mentor'}
                          </Button>
                          <Button
                            onClick={() => {
                              if (confirm('Reject this application? This action cannot be undone.')) {
                                updateApplicationStatus(app.id, 'rejected');
                              }
                            }}
                            disabled={processingId === app.id}
                            className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium"
                          >
                            ✗ Reject
                          </Button>
                        </div>
                      )}

                      {app.status === 'approved' && (
                        <div className="flex gap-3 pt-4 border-t border-gray-200">
                          <Button
                            onClick={() => {
                              if (confirm('Suspend this mentor? They will not be able to accept new sessions.')) {
                                updateApplicationStatus(app.id, 'suspended');
                              }
                            }}
                            disabled={processingId === app.id}
                            className="flex-1 bg-orange-600 hover:bg-orange-700 text-white font-medium"
                          >
                            ⚠️ Suspend
                          </Button>
                        </div>
                      )}

                      {app.status === 'suspended' && (
                        <div className="pt-4 border-t border-gray-200">
                          <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                            <p className="text-sm text-orange-700">
                              ⚠️ This mentor is currently suspended and cannot accept new sessions.
                            </p>
                          </div>
                        </div>
                      )}

                      {['rejected', 'approved'].includes(app.status) && app.status !== 'pending' && (
                        <div className="pt-4 border-t border-gray-200">
                          <p className="text-sm text-gray-600">
                            {app.status === 'approved' 
                              ? '✅ This mentor is approved and can accept sessions.'
                              : '❌ This mentor was rejected and cannot use the platform.'}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

export const getServerSideProps = requireAdminSSR

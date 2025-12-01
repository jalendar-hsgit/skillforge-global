import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import AdminHeader from '@/components/AdminHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/apiBase';
import { requireAdminSSR, AdminSSRProps } from '@/lib/adminAuth';

interface MentorApplication {
  id: number;
  user_id: number;
  bio: string;
  expertise: string;
  hourly_rate: number;
  status: string;
  created_at: string;
  user?: {
    email: string;
    full_name: string;
  };
}

export default function MentorAdminPage({ me }: AdminSSRProps) {
  const router = useRouter();
  const [applications, setApplications] = useState<MentorApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('pending');
  const [processingId, setProcessingId] = useState<number | null>(null);

  useEffect(() => {
    fetchApplications();
  }, [filter]);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(
        `${API_BASE}/api/v1x/admin/mentors/applications?status=${filter === 'all' ? '' : filter}`,
        { credentials: 'include' }
      );

      if (response.status === 401) {
        router.push('/login?redirect=/admin/mentors');
        return;
      }

      if (response.status === 403) {
        setError('Access denied. Admin privileges required.');
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to fetch applications');
      }

      const data = await response.json();
      setApplications(data.applications || data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateApplicationStatus = async (mentorId: number, status: 'approved' | 'rejected') => {
    try {
      setProcessingId(mentorId);
      setError('');

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
      await fetchApplications();
      alert(`Application ${status} successfully`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setProcessingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {status.toUpperCase()}
      </span>
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
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
                Mentor Applications
              </h1>
              <p className="text-xl text-gray-600">
                Review and approve mentor applications · Signed in as {me.email}
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
              <p className="text-red-700">{error}</p>
            </Card>
          )}

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="text-center">
              <p className="text-sm text-gray-600 mb-1">Total Applications</p>
              <p className="text-3xl font-bold text-gray-900">
                {applications.length}
              </p>
            </Card>
            <Card className="text-center">
              <p className="text-sm text-gray-600 mb-1">Pending</p>
              <p className="text-3xl font-bold text-yellow-600">
                {applications.filter(a => a.status === 'pending').length}
              </p>
            </Card>
            <Card className="text-center">
              <p className="text-sm text-gray-600 mb-1">Approved</p>
              <p className="text-3xl font-bold text-green-600">
                {applications.filter(a => a.status === 'approved').length}
              </p>
            </Card>
            <Card className="text-center">
              <p className="text-sm text-gray-600 mb-1">Rejected</p>
              <p className="text-3xl font-bold text-red-600">
                {applications.filter(a => a.status === 'rejected').length}
              </p>
            </Card>
          </div>

          {/* Filters */}
          <div className="flex gap-4 mb-6">
            {(['all', 'pending', 'approved', 'rejected'] as const).map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  filter === f
                    ? 'bg-blue-600 text-white'
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
            <div className="space-y-6">
              {applications.map((app) => (
                <Card key={app.id}>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">
                        {app.user?.full_name || 'Unknown User'}
                      </h3>
                      <p className="text-gray-600">{app.user?.email}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        Applied on {formatDate(app.created_at)}
                      </p>
                    </div>
                    {getStatusBadge(app.status)}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    {/* Bio */}
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-2">
                        Bio
                      </h4>
                      <p className="text-gray-700 whitespace-pre-wrap">
                        {app.bio}
                      </p>
                    </div>

                    {/* Details */}
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">
                          Expertise
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {app.expertise.split(',').map((skill, idx) => (
                            <span
                              key={idx}
                              className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                            >
                              {skill.trim()}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-1">
                          Hourly Rate
                        </h4>
                        <p className="text-2xl font-bold text-green-600">
                          ${app.hourly_rate}/hour
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  {app.status === 'pending' && (
                    <div className="flex gap-4 pt-4 border-t border-gray-200">
                      <Button
                        onClick={() => updateApplicationStatus(app.id, 'approved')}
                        variant="primary"
                        disabled={processingId === app.id}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                      >
                        {processingId === app.id ? 'Processing...' : '✓ Approve'}
                      </Button>
                      <Button
                        onClick={() => {
                          if (confirm('Are you sure you want to reject this application?')) {
                            updateApplicationStatus(app.id, 'rejected');
                          }
                        }}
                        variant="secondary"
                        disabled={processingId === app.id}
                        className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                      >
                        ✗ Reject
                      </Button>
                    </div>
                  )}

                  {app.status !== 'pending' && (
                    <div className="pt-4 border-t border-gray-200">
                      <p className="text-sm text-gray-600">
                        This application has been {app.status}.
                      </p>
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

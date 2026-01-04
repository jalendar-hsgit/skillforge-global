import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { getMyMentorSessions, cancelMentorSession } from '@/lib/api';

interface MentorSession {
  id: number;
  mentor_id: number;
  mentor?: {
    user?: {
      full_name: string;
    };
    hourly_rate?: number;
  };
  topic: string;
  scheduled_at: string;
  status: string;
  duration_minutes: number;
  price: number;
  description?: string;
}

const MySessionsPage = () => {
  const router = useRouter();
  const [sessions, setSessions] = useState<MentorSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancelling, setCancelling] = useState<number | null>(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getMyMentorSessions();
      const sessionsList = Array.isArray(data) ? data : data.sessions || [];
      setSessions(sessionsList);
    } catch (err: any) {
      setError(err.message || 'Failed to load sessions');
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (sessionId: number) => {
    if (!window.confirm('Are you sure you want to cancel this session?')) {
      return;
    }

    try {
      setCancelling(sessionId);
      await cancelMentorSession(sessionId);
      setSessions(sessions.map(s => 
        s.id === sessionId ? { ...s, status: 'cancelled' } : s
      ));
    } catch (err: any) {
      setError(err.message || 'Failed to cancel session');
    } finally {
      setCancelling(null);
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    const s = status.toLowerCase();
    switch (s) {
      case 'confirmed':
        return 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300';
      case 'pending':
        return 'bg-yellow-500/20 border-yellow-500/50 text-yellow-300';
      case 'completed':
        return 'bg-blue-500/20 border-blue-500/50 text-blue-300';
      case 'cancelled':
        return 'bg-red-500/20 border-red-500/50 text-red-300';
      default:
        return 'bg-gray-500/20 border-gray-500/50 text-gray-300';
    }
  };

  const getStatusBadgeColor = (status: string) => {
    const s = status.toLowerCase();
    switch (s) {
      case 'confirmed':
        return 'bg-emerald-500';
      case 'pending':
        return 'bg-yellow-500';
      case 'completed':
        return 'bg-blue-500';
      case 'cancelled':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const upcomingSessions = sessions.filter(s => {
    const sessionDate = new Date(s.scheduled_at);
    const statusLower = s.status.toLowerCase();
    return sessionDate > new Date() && (statusLower === 'confirmed' || statusLower === 'pending');
  });

  const pastSessions = sessions.filter(s => {
    const sessionDate = new Date(s.scheduled_at);
    const statusLower = s.status.toLowerCase();
    return sessionDate <= new Date() || statusLower === 'completed' || statusLower === 'cancelled';
  });

  if (loading) {
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
      <div className="min-h-screen bg-deepTech-950 bg-neural py-12 md:py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-display font-black text-transparent bg-clip-text bg-gradient-to-r from-forgePurple-400 via-neuralBlue-400 to-aiElectric-400 mb-4">
              My Mentor Sessions
            </h1>
            <p className="text-xl text-techGray-300">
              View and manage your booked sessions
            </p>
          </div>

          {error && (
            <Card className="mb-8 bg-red-500/20 border border-red-500/50">
              <p className="text-red-300">{error}</p>
            </Card>
          )}

          {sessions.length === 0 ? (
            <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass text-center py-16">
              <svg
                className="w-20 h-20 mx-auto text-techGray-500 mb-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <h3 className="text-2xl font-bold text-white mb-3">
                No Sessions Yet
              </h3>
              <p className="text-techGray-400 mb-8 max-w-md mx-auto">
                You haven't booked any mentor sessions yet. Start by browsing our mentors and booking a session!
              </p>
              <Button
                onClick={() => router.push('/mentors')}
                variant="primary"
              >
                Browse Mentors
              </Button>
            </Card>
          ) : (
            <div className="space-y-8">
              {/* Upcoming Sessions */}
              {upcomingSessions.length > 0 && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                    <div className="w-2 h-8 bg-emerald-500 rounded"></div>
                    Upcoming Sessions
                  </h2>
                  <div className="space-y-4">
                    {upcomingSessions.map(session => (
                      <Card
                        key={session.id}
                        className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass hover:border-emerald-500/30 transition-colors"
                      >
                        <div className="p-6 md:p-8">
                          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                            <div className="flex-1">
                              <div className="flex items-start gap-4 mb-4">
                                <div>
                                  <h3 className="text-2xl font-bold text-white mb-2">
                                    {session.topic}
                                  </h3>
                                  <p className="text-techGray-400">
                                    with {session.mentor?.user?.full_name || 'Mentor'}
                                  </p>
                                </div>
                              </div>

                              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
                                <div>
                                  <p className="text-xs text-techGray-400 uppercase font-semibold mb-1">
                                    Date & Time
                                  </p>
                                  <p className="text-white font-semibold">
                                    {formatDateTime(session.scheduled_at)}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-techGray-400 uppercase font-semibold mb-1">
                                    Duration
                                  </p>
                                  <p className="text-white font-semibold">
                                    {session.duration_minutes} minutes
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-techGray-400 uppercase font-semibold mb-1">
                                    Price
                                  </p>
                                  <p className="text-aiElectric-400 font-bold text-lg">
                                    ${session.price.toFixed(2)}
                                  </p>
                                </div>
                              </div>

                              {session.description && (
                                <div className="mt-4 p-3 bg-deepTech-900/50 rounded-lg">
                                  <p className="text-sm text-techGray-300">
                                    <span className="font-semibold text-white">Notes:</span> {session.description}
                                  </p>
                                </div>
                              )}
                            </div>

                            <div className="flex flex-col gap-3 md:w-auto">
                              <div className={`px-4 py-2 rounded-lg border text-center font-semibold text-sm ${getStatusColor(session.status)}`}>
                                {session.status}
                              </div>
                              {session.status.toLowerCase() === 'pending' && (
                                <Button
                                  variant="outline"
                                  onClick={() => handleCancel(session.id)}
                                  disabled={cancelling === session.id}
                                  className="text-red-400 border-red-500/50 hover:border-red-500 hover:bg-red-500/10"
                                >
                                  {cancelling === session.id ? 'Cancelling...' : 'Cancel'}
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Past Sessions */}
              {pastSessions.length > 0 && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                    <div className="w-2 h-8 bg-techGray-500 rounded"></div>
                    Past Sessions
                  </h2>
                  <div className="space-y-4">
                    {pastSessions.map(session => (
                      <Card
                        key={session.id}
                        className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass opacity-75 hover:opacity-100 transition-opacity"
                      >
                        <div className="p-6 md:p-8">
                          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                            <div className="flex-1">
                              <h3 className="text-xl font-bold text-white mb-1">
                                {session.topic}
                              </h3>
                              <p className="text-techGray-400 text-sm">
                                with {session.mentor?.user?.full_name || 'Mentor'} • {formatDateTime(session.scheduled_at)}
                              </p>
                            </div>
                            <div className={`px-4 py-2 rounded-lg border text-center font-semibold text-sm ${getStatusColor(session.status)}`}>
                              {session.status}
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* CTA Button */}
          {sessions.length > 0 && (
            <div className="mt-12 text-center">
              <p className="text-techGray-400 mb-6">Want to book another session?</p>
              <Button
                onClick={() => router.push('/mentors')}
                variant="primary"
              >
                Browse More Mentors
              </Button>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default MySessionsPage;

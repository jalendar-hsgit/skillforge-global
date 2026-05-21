import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useProtectedPage } from '@/lib/useProtectedPage';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import Link from 'next/link';
import { Calendar, Clock, Users, MessageCircle, Video, BookOpen, Timer, DollarSign, CreditCard, AlertCircle } from 'lucide-react';

interface MentorSession {
  id: number;
  mentor_id: number;
  mentor_name?: string;
  mentor_rating?: number;
  topic: string;
  description?: string;
  scheduled_at: string;
  status: string;
  duration_minutes: number;
  price?: number;
  payment_status?: string;
  meeting_link?: string;
}

export default function MyBookings() {
  const router = useRouter();
  const { user, loading: authLoading, isAuthorized } = useProtectedPage('user');
  const [sessions, setSessions] = useState<MentorSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authLoading && isAuthorized) {
      loadBookings();
    }
  }, [authLoading, isAuthorized]);

  const loadBookings = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

      console.log('Fetching sessions for user from:', apiBase);
      // Call backend directly - it will validate auth from HttpOnly cookie
      const response = await fetch(`${apiBase}/api/v1x/mentors/sessions/my`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Send HttpOnly cookies
      });

      console.log('Session fetch response status:', response.status);

      if (response.status === 401 || response.status === 403) {
        console.log('Unauthorized, redirecting to login');
        router.push('/login');
        return;
      }

      if (response.ok) {
        const data = await response.json();
        console.log('Sessions response data:', data);
        
        // Handle both array and {sessions} format
        const sessionsList = Array.isArray(data) ? data : (data.sessions || []);
        console.log('Parsed sessions:', sessionsList);
        
        setSessions(sessionsList);
        if (sessionsList.length === 0) {
          console.log('No sessions found for user');
        }
      } else {
        const errorText = await response.text();
        console.error('API error:', response.status, errorText);
        
        // Try to parse as JSON for better error message
        try {
          const errorData = JSON.parse(errorText);
          setError(`Failed to load bookings (Status: ${response.status}) - ${errorData.detail || 'Unknown error'}`);
        } catch {
          setError(`Failed to load bookings (Status: ${response.status}) - ${errorText}`);
        }
      }
    } catch (err) {
      console.error('Error loading bookings:', err);
      setError('Failed to load bookings. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status: string) => {
    const statusLower = status?.toLowerCase() || '';
    switch (statusLower) {
      case 'confirmed':
        return 'bg-green-500/20 text-green-300 border border-green-500/50';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/50';
      case 'completed':
        return 'bg-blue-500/20 text-blue-300 border border-blue-500/50';
      case 'cancelled':
        return 'bg-red-500/20 text-red-300 border border-red-500/50';
      default:
        return 'bg-techGray-500/20 text-techGray-300 border border-techGray-500/50';
    }
  };

  if (authLoading || loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-deepTech-950 bg-neural">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="flex items-center justify-center">
              <div className="w-8 h-8 border-4 border-forgePurple-400/30 border-t-forgePurple-400 rounded-full animate-spin"></div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (loading || authLoading) {
    return (
      <Layout>
        <div className="min-h-screen bg-deepTech-950 bg-neural flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-forgePurple-500"></div>
        </div>
      </Layout>
    );
  }

  if (!isAuthorized) {
    return (
      <Layout>
        <div className="min-h-screen bg-deepTech-950 bg-neural flex items-center justify-center">
          <div className="text-center">
            <p className="text-techGray-300 mb-4">Please log in to view your bookings.</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-deepTech-950 bg-neural py-12 md:py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-10">
            <h1 className="text-4xl md:text-5xl font-display font-black text-transparent bg-clip-text bg-gradient-to-r from-forgePurple-400 via-neuralBlue-400 to-aiElectric-400 mb-3 leading-tight">
              My Mentor Sessions
            </h1>
            <p className="text-lg text-techGray-300">
              View and manage all your booked mentor sessions
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 mb-10 flex-wrap">
            <Link href="/mentors">
              <Button variant="primary">
                Book New Session
              </Button>
            </Link>
          </div>

        {/* Error Message */}
        {error && (
          <Card className="mb-6 bg-red-500/20 border border-red-500/50 backdrop-blur-xl shadow-glass">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-300">{error}</p>
            </div>
          </Card>
        )}

        {/* Sessions List */}
        {sessions.length === 0 ? (
          <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass p-12 text-center">
            <Calendar className="mx-auto mb-4 w-12 h-12 text-forgePurple-400" />
            <h3 className="text-xl font-bold text-white mb-2">
              No Sessions Booked
            </h3>
            <p className="text-techGray-300 mb-6">
              You haven't booked any mentor sessions yet. Start by browsing mentors and scheduling your first session!
            </p>
            <Link href="/mentors">
              <Button variant="primary">
                Browse Mentors
              </Button>
            </Link>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sessions.map((session) => (
              <Card key={session.id} className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass hover:shadow-lg hover:shadow-forgePurple-500/20 transition-all">
                <div className="flex flex-col h-full">
                  {/* Mentor Info */}
                  <div className="mb-4 pb-4 border-b border-white/10">
                    <div className="flex items-center justify-between mb-2 gap-2">
                      <h3 className="text-lg font-bold text-white">
                        {session.mentor_name || 'Mentor'}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${getStatusColor(session.status)}`}>
                        {session.status?.toUpperCase()}
                      </span>
                    </div>
                    {session.mentor_rating && (
                      <div className="flex items-center gap-1 text-aiElectric-300">
                        <span>⭐</span>
                        <span className="text-sm font-medium">{session.mentor_rating.toFixed(1)}</span>
                        </div>
                      )}
                    </div>

                    {/* Topic & Details */}
                    <div className="space-y-3 pb-4 border-b border-white/10">
                      <div className="flex items-start gap-2">
                        <BookOpen className="w-4 h-4 text-forgePurple-400 mt-1 flex-shrink-0" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-techGray-400">Topic</p>
                          <p className="text-sm font-medium text-white">{session.topic}</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-2">
                        <Calendar className="w-4 h-4 text-aiElectric-400 mt-1 flex-shrink-0" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-techGray-400">Scheduled</p>
                          <p className="text-sm font-medium text-white">
                            {new Date(session.scheduled_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-2">
                        <Clock className="w-4 h-4 text-neuralBlue-400 mt-1 flex-shrink-0" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-techGray-400">Time</p>
                          <p className="text-sm font-medium text-white">
                            {new Date(session.scheduled_at).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-2">
                        <Timer className="w-4 h-4 text-neuralBlue-400 mt-1 flex-shrink-0" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-techGray-400">Duration</p>
                          <p className="text-sm font-medium text-white">{session.duration_minutes} minutes</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-2">
                        <DollarSign className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-techGray-400">Price</p>
                          <p className="text-sm font-bold text-white">${session.price?.toFixed(2) || '0.00'}</p>
                        </div>
                      </div>
                      {session.payment_status && (
                        <div className="flex items-start gap-2">
                          <CreditCard className="w-4 h-4 text-neuralBlue-300 mt-1 flex-shrink-0" />
                          <div>
                            <p className="text-xs uppercase tracking-wide text-techGray-400">Payment</p>
                            <p className={`text-sm font-semibold ${
                              session.payment_status === 'completed' 
                                ? 'text-green-400' 
                                : 'text-yellow-400'
                            }`}>
                              {session.payment_status.charAt(0).toUpperCase() + session.payment_status.slice(1)}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>

                  {/* Description */}
                    {session.description && (
                      <p className="text-techGray-300 text-sm mt-4 mb-4">
                        {session.description}
                      </p>
                    )}

                  {/* Right: Actions */}
                  <div className="flex flex-col gap-2 pt-4">
                    {session.status === 'CONFIRMED' && session.meeting_link && (
                      <a
                        href={session.meeting_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-green-500 text-white rounded-lg hover:shadow-lg hover:shadow-green-500/30 transition-all"
                      >
                        <Video size={16} />
                        Join Meeting
                      </a>
                    )}
                    <Link href={`/my-bookings/${session.id}`}>
                      <Button variant="outline" className="w-full">
                        View Details
                      </Button>
                    </Link>
                    {session.status === 'COMPLETED' && (
                      <Button variant="outline" className="w-full flex items-center justify-center gap-2">
                        <MessageCircle size={16} />
                        Leave Feedback
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
        </div>
      </div>
    </Layout>
  );
}

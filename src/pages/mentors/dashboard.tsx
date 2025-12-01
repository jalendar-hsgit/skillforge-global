import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/apiBase';
import AvailabilityCalendar from '@/components/AvailabilityCalendar';

interface Mentor {
  id: number;
  bio: string;
  expertise: string[];
  hourly_rate: number;
  average_rating: number;
  total_sessions: number;
  status: string;
}

interface Session {
  id: number;
  mentor_id: number;
  student_id: number;
  scheduled_at: string; // backend field
  duration_minutes: number;
  status: string;
  topic: string;
  meeting_url?: string;
  mentor_notes?: string;
  student_feedback?: string;
}

interface Availability {
  id: number;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export default function MentorDashboard() {
  const router = useRouter();
  
  const [mentorProfile, setMentorProfile] = useState<Mentor | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [availability, setAvailability] = useState<Availability[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [activeTab, setActiveTab] = useState<'overview' | 'sessions' | 'availability'>('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch mentor profile
      const profileResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/me`,
        { credentials: 'include' }
      );

      if (profileResponse.status === 401) {
        router.push('/login?redirect=/mentors/dashboard');
        return;
      }

      if (profileResponse.status === 404) {
        // Not a mentor yet
        router.push('/mentors/become');
        return;
      }

      if (!profileResponse.ok) throw new Error('Failed to fetch profile');
      const profileData = await profileResponse.json();
      setMentorProfile(profileData);

      // Fetch sessions
      const sessionsResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/sessions/my`,
        { credentials: 'include' }
      );
      if (sessionsResponse.ok) {
        const sessionsData = await sessionsResponse.json();
        // Backend returns { sessions: [...], total: n }
        const list = Array.isArray(sessionsData) ? sessionsData : sessionsData.sessions;
        setSessions(Array.isArray(list) ? list : []);
      }

      // Fetch availability (if mentor is approved)
      if (profileData.status === 'approved') {
        const availabilityResponse = await fetch(
          `${API_BASE}/api/v1x/mentors/availability/${profileData.id}`,
          { credentials: 'include' }
        );
        if (availabilityResponse.ok) {
          const availabilityData = await availabilityResponse.json();
          setAvailability(availabilityData);
        }
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      confirmed: 'bg-blue-100 text-blue-800',
      completed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    };
  };

  const safeSessions = Array.isArray(sessions) ? sessions : [];
  const upcomingSessions = safeSessions
    .filter(s => new Date(s.scheduled_at) > new Date() && s.status !== 'cancelled')
    .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime());

  const completedSessions = safeSessions
    .filter(s => s.status === 'completed')
    .sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime());

  const pendingSessions = safeSessions.filter(s => s.status === 'pending');

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  if (error || !mentorProfile) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <Card className="bg-red-50 border-red-200">
            <p className="text-red-700">{error || 'Failed to load dashboard'}</p>
          </Card>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-deepTech-950 bg-neural py-12 md:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-10">
            <h1 className="text-4xl md:text-5xl font-display font-black text-transparent bg-clip-text bg-gradient-to-r from-forgePurple-400 via-neuralBlue-400 to-aiElectric-400 mb-4 leading-tight">
              Mentor Dashboard
            </h1>
            <p className="text-xl md:text-2xl text-techGray-300">
              Manage your sessions and availability
            </p>
          </div>

          {/* Status Banner */}
          {mentorProfile.status === 'pending' && (
            <Card className="mb-8 bg-warning-dark/20 border border-warning/30 backdrop-blur-xl">
              <div className="flex items-center gap-4">
                <svg className="w-10 h-10 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="text-xl font-bold text-white">
                    Application Under Review
                  </h3>
                  <p className="text-warning-light">
                    Your mentor application is being reviewed. You'll be notified once approved.
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
            <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass hover:border-forgePurple-500/50 hover:shadow-glow-sm transition-all duration-300">
              <div className="p-6">
                <div className="text-center">
                  <p className="text-sm text-techGray-400 mb-2">Total Sessions</p>
                  <p className="text-4xl font-bold text-white">
                    {mentorProfile.total_sessions}
                  </p>
                </div>
              </div>
            </Card>
            <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass hover:border-warning/50 hover:shadow-glow-sm transition-all duration-300">
              <div className="p-6">
                <div className="text-center">
                  <p className="text-sm text-techGray-400 mb-2">Pending Requests</p>
                  <p className="text-4xl font-bold text-warning">
                    {pendingSessions.length}
                  </p>
                </div>
              </div>
            </Card>
            <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass hover:border-neuralBlue-500/50 hover:shadow-glow-sm transition-all duration-300">
              <div className="p-6">
                <div className="text-center">
                  <p className="text-sm text-techGray-400 mb-2">Average Rating</p>
                  <p className="text-4xl font-bold text-neuralBlue-400">
                    {mentorProfile.average_rating.toFixed(1)}
                  </p>
                </div>
              </div>
            </Card>
            <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass hover:border-success/50 hover:shadow-glow-sm transition-all duration-300">
              <div className="p-6">
                <div className="text-center">
                  <p className="text-sm text-techGray-400 mb-2">Hourly Rate</p>
                  <p className="text-4xl font-bold text-success">
                    ${mentorProfile.hourly_rate}
                  </p>
                </div>
              </div>
            </Card>
          </div>

          {/* Tabs */}
          <div className="border-b border-white/10 mb-8">
            <nav className="flex space-x-8">
              {(['overview', 'sessions', 'availability'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 border-b-2 font-semibold text-sm transition-all ${
                    activeTab === tab
                      ? 'border-forgePurple-500 text-white'
                      : 'border-transparent text-techGray-400 hover:text-techGray-200 hover:border-techGray-600'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Upcoming Sessions */}
              <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
                <div className="p-6 md:p-8">
                  <h2 className="text-2xl md:text-3xl font-bold text-white mb-6">
                    Upcoming Sessions ({upcomingSessions.length})
                  </h2>
                  {upcomingSessions.length === 0 ? (
                    <p className="text-techGray-400 text-lg">No upcoming sessions</p>
                  ) : (
                    <div className="space-y-4">
                      {upcomingSessions.slice(0, 5).map(session => {
                        const { date, time } = formatDateTime(session.scheduled_at);
                        return (
                          <div 
                            key={session.id} 
                            className="p-5 bg-deepTech-900/30 border border-white/10 rounded-lg hover:border-forgePurple-500/50 hover:shadow-glow-sm transition-all duration-300 cursor-pointer"
                            onClick={() => router.push(`/mentors/sessions/${session.id}`)}
                          >
                            <div className="flex justify-between items-start mb-3">
                              <div>
                                <h3 className="font-bold text-white text-lg">{session.topic}</h3>
                                <p className="text-sm text-techGray-400 mt-1">
                                  with {session.student?.full_name || 'Student'}
                                </p>
                              </div>
                              {getStatusBadge(session.status)}
                            </div>
                            <div className="flex items-center gap-4 text-sm text-techGray-400">
                              <span>📅 {date}</span>
                              <span>🕐 {time}</span>
                              <span>⏱️ {session.duration_minutes} min</span>
                            </div>
                            <div className="flex gap-2 mt-3">
                              {session.meeting_url && (
                                <Button
                                  variant="primary"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    window.open(session.meeting_url, '_blank');
                                  }}
                                >
                                  Join Meeting
                                </Button>
                              )}
                              <Button
                                variant="outline"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  router.push(`/mentors/sessions/${session.id}`);
                                }}
                              >
                                View Details
                              </Button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </Card>

              {/* Profile Summary */}
              <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
                <div className="p-6 md:p-8">
                  <h2 className="text-2xl md:text-3xl font-bold text-white mb-6">Profile</h2>
                  <div className="space-y-4">
                  <div>
                    <p className="text-sm text-techGray-400 mb-2">Status</p>
                    {getStatusBadge(mentorProfile.status)}
                  </div>
                  <div>
                    <p className="text-sm text-techGray-400 mb-2">Expertise</p>
                    <div className="flex flex-wrap gap-2">
                      {(() => {
                        const skills = Array.isArray(mentorProfile.expertise)
                          ? mentorProfile.expertise
                          : String(mentorProfile.expertise || '')
                              .split(',')
                              .map(s => s.trim())
                              .filter(Boolean);
                        return skills.map((skill, index) => (
                          <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                            {skill}
                          </span>
                        ));
                      })()}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-techGray-400 mb-2">Bio</p>
                    <p className="text-techGray-300 leading-relaxed">{mentorProfile.bio}</p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => router.push('/mentors/edit')}
                  >
                    Edit Profile
                  </Button>
                </div>
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'sessions' && (
            <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
              <div className="p-6 md:p-8">
                <h2 className="text-2xl md:text-3xl font-bold text-white mb-8">All Sessions</h2>
                {sessions.length === 0 ? (
                  <p className="text-techGray-400 text-lg">No sessions yet</p>
                ) : (
                  <div className="space-y-4">
                    {sessions.map(session => {
                      const { date, time } = formatDateTime(session.start_time);
                      return (
                        <div key={session.id} className="p-5 bg-deepTech-900/30 border border-white/10 rounded-lg">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h3 className="font-bold text-white text-lg">{session.topic}</h3>
                              <p className="text-sm text-techGray-400 mt-1">
                                with {session.student?.full_name || 'Student'}
                              </p>
                            </div>
                            {getStatusBadge(session.status)}
                          </div>
                          <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                            <span>📅 {date}</span>
                            <span>🕐 {time}</span>
                            <span>⏱️ {session.duration_minutes} min</span>
                          </div>
                          {session.notes && (
                            <p className="text-sm text-techGray-300 mt-3 p-3 bg-deepTech-800/50 rounded border border-white/5">
                              {session.notes}
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </Card>
          )}

          {activeTab === 'availability' && mentorProfile && (
            <AvailabilityCalendar
              mentorId={mentorProfile.id}
              editable={true}
            />
          )}
        </div>
      </div>
    </Layout>
  );
}

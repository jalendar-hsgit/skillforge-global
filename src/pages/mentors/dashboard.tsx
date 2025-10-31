import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/apiBase';

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
  start_time: string;
  end_time: string;
  duration_minutes: number;
  status: string;
  topic: string;
  notes?: string;
  meeting_url?: string;
  student?: {
    full_name: string;
    email: string;
  };
  mentor?: {
    user: {
      full_name: string;
    };
  };
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
        setSessions(sessionsData);
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

  const upcomingSessions = sessions
    .filter(s => new Date(s.start_time) > new Date() && s.status !== 'cancelled')
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());

  const completedSessions = sessions
    .filter(s => s.status === 'completed')
    .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());

  const pendingSessions = sessions.filter(s => s.status === 'pending');

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
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Mentor Dashboard
            </h1>
            <p className="text-xl text-gray-600">
              Manage your sessions and availability
            </p>
          </div>

          {/* Status Banner */}
          {mentorProfile.status === 'pending' && (
            <Card className="mb-8 bg-yellow-50 border-yellow-200">
              <div className="flex items-center gap-4">
                <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="text-lg font-semibold text-yellow-900">
                    Application Under Review
                  </h3>
                  <p className="text-yellow-800">
                    Your mentor application is being reviewed. You'll be notified once approved.
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Total Sessions</p>
                <p className="text-3xl font-bold text-gray-900">
                  {mentorProfile.total_sessions}
                </p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Pending Requests</p>
                <p className="text-3xl font-bold text-yellow-600">
                  {pendingSessions.length}
                </p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Average Rating</p>
                <p className="text-3xl font-bold text-blue-600">
                  {mentorProfile.average_rating.toFixed(1)}
                </p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Hourly Rate</p>
                <p className="text-3xl font-bold text-green-600">
                  ${mentorProfile.hourly_rate}
                </p>
              </div>
            </Card>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="flex space-x-8">
              {(['overview', 'sessions', 'availability'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
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
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  Upcoming Sessions ({upcomingSessions.length})
                </h2>
                {upcomingSessions.length === 0 ? (
                  <p className="text-gray-600">No upcoming sessions</p>
                ) : (
                  <div className="space-y-4">
                    {upcomingSessions.slice(0, 5).map(session => {
                      const { date, time } = formatDateTime(session.start_time);
                      return (
                        <div key={session.id} className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h3 className="font-semibold text-gray-900">{session.topic}</h3>
                              <p className="text-sm text-gray-600">
                                with {session.student?.full_name || 'Student'}
                              </p>
                            </div>
                            {getStatusBadge(session.status)}
                          </div>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span>📅 {date}</span>
                            <span>🕐 {time}</span>
                            <span>⏱️ {session.duration_minutes} min</span>
                          </div>
                          {session.meeting_url && (
                            <Button
                              variant="primary"
                              onClick={() => window.open(session.meeting_url, '_blank')}
                              className="mt-3"
                            >
                              Join Meeting
                            </Button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </Card>

              {/* Profile Summary */}
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Profile</h2>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Status</p>
                    {getStatusBadge(mentorProfile.status)}
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Expertise</p>
                    <div className="flex flex-wrap gap-2">
                      {mentorProfile.expertise.map((skill, index) => (
                        <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Bio</p>
                    <p className="text-gray-700">{mentorProfile.bio}</p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => router.push('/mentors/edit')}
                  >
                    Edit Profile
                  </Button>
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'sessions' && (
            <Card>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">All Sessions</h2>
              {sessions.length === 0 ? (
                <p className="text-gray-600">No sessions yet</p>
              ) : (
                <div className="space-y-4">
                  {sessions.map(session => {
                    const { date, time } = formatDateTime(session.start_time);
                    return (
                      <div key={session.id} className="p-4 border border-gray-200 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="font-semibold text-gray-900">{session.topic}</h3>
                            <p className="text-sm text-gray-600">
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
                          <p className="text-sm text-gray-700 mt-2 p-3 bg-gray-50 rounded">
                            {session.notes}
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>
          )}

          {activeTab === 'availability' && (
            <Card>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  Availability Schedule
                </h2>
                <Button variant="primary">
                  Add Time Slot
                </Button>
              </div>
              {availability.length === 0 ? (
                <p className="text-gray-600">No availability set yet</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {availability.map(slot => {
                    const start = formatDateTime(slot.start_time);
                    const end = formatDateTime(slot.end_time);
                    return (
                      <div key={slot.id} className="p-4 border border-gray-200 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <p className="font-medium text-gray-900">{start.date}</p>
                            <p className="text-sm text-gray-600">
                              {start.time} - {end.time}
                            </p>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs ${
                            slot.is_available
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {slot.is_available ? 'Available' : 'Booked'}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
}

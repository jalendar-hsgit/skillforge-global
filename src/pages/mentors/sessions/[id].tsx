import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import MentorChat from '@/components/MentorChat';
import { API_BASE } from '@/lib/apiBase';
import { useMe } from '@/hooks/useMe';
import { Avatar } from '@/components/Avatar';
import { Chip } from '@/components/Chip';

interface Session {
  id: number;
  mentor_id: number;
  student_id: number;
  topic: string;
  description: string;
  scheduled_at: string;
  duration_minutes: number;
  status: string;
  meeting_url: string | null;
  price: number;
  payment_status: string;
  mentor_notes: string | null;
  student_feedback: string | null;
  created_at: string;
}

interface MentorInfo {
  id: number;
  user_id: number;
  bio: string;
  expertise: string[] | string;
  hourly_rate: number;
  average_rating: number;
  user?: {
    full_name?: string;
    email?: string;
  };
}

interface StudentInfo {
  id: number;
  email: string;
  full_name: string;
}

export default function SessionDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const { me, loading: meLoading } = useMe();
  
  const [session, setSession] = useState<Session | null>(null);
  const [mentor, setMentor] = useState<MentorInfo | null>(null);
  const [student, setStudent] = useState<StudentInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);
  
  const [showChat, setShowChat] = useState(false);
  const [meetingUrl, setMeetingUrl] = useState('');
  const [mentorNotes, setMentorNotes] = useState('');

  useEffect(() => {
    if (id && me) {
      fetchSessionDetails();
    }
  }, [id, me]);

  const fetchSessionDetails = async () => {
    try {
      setLoading(true);

      // Fetch all sessions to find this one
      const response = await fetch(
        `${API_BASE}/api/v1x/mentors/sessions/my`,
        { credentials: 'include' }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch session');
      }

      const data = await response.json();
      const foundSession = data.sessions?.find((s: Session) => s.id === Number(id)) || null;

      if (!foundSession) {
        throw new Error('Session not found');
      }

      setSession(foundSession);
      setMentorNotes(foundSession.mentor_notes || '');
      setMeetingUrl(foundSession.meeting_url || '');

      // Fetch mentor info
      const mentorResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/${foundSession.mentor_id}`,
        { credentials: 'include' }
      );
      if (mentorResponse.ok) {
        const mentorData = await mentorResponse.json();
        // Normalize mentor shape (expertise array + presence of user object)
        const normalizedExpertise = Array.isArray(mentorData.expertise)
          ? mentorData.expertise
          : String(mentorData.expertise || '')
              .split(',')
              .map((s: string) => s.trim())
              .filter(Boolean);
        const normalizedMentor: MentorInfo = {
          ...mentorData,
          expertise: normalizedExpertise,
          user: mentorData.user || {
            full_name: mentorData.full_name || 'Mentor',
            email: mentorData.email || ''
          }
        };
        setMentor(normalizedMentor);
      }

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateSession = async (updates: { status?: string; meeting_url?: string; mentor_notes?: string }) => {
    if (!session) return;

    try {
      setUpdating(true);
      setError('');

      const response = await fetch(
        `${API_BASE}/api/v1x/mentors/sessions/${session.id}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(updates)
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update session');
      }

      const updatedSession = await response.json();
      setSession(updatedSession);
      
      // Show success message
      alert('Session updated successfully');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUpdating(false);
    }
  };

  const confirmSession = () => {
    if (!meetingUrl.trim()) {
      setError('Please provide a meeting URL');
      return;
    }
    updateSession({
      status: 'confirmed',
      meeting_url: meetingUrl,
      mentor_notes: mentorNotes || undefined
    });
  };

  const completeSession = () => {
    updateSession({ status: 'completed' });
  };

  const cancelSession = () => {
    if (confirm('Are you sure you want to cancel this session?')) {
      updateSession({ status: 'cancelled' });
    }
  };

  const saveMentorNotes = () => {
    updateSession({ mentor_notes: mentorNotes });
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }),
      time: date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit' 
      })
    };
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
      no_show: 'bg-gray-100 text-gray-800'
    };
    return (
      <span className={`px-4 py-2 rounded-full text-sm font-semibold ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  if (meLoading || loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  if (error || !session || !me) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <Card className="bg-red-50 border-red-200">
            <p className="text-red-700">{error || 'Session not found'}</p>
            <Button
              onClick={() => router.push('/mentors/dashboard')}
              variant="outline"
              className="mt-4"
            >
              Back to Dashboard
            </Button>
          </Card>
        </div>
      </Layout>
    );
  }

  const { date, time } = formatDateTime(session.scheduled_at);
  const isMentor = mentor?.user_id === me.id;

  return (
    <Layout>
      <div className="min-h-screen bg-deepTech-950 bg-neural py-12 md:py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Back Button */}
          <Button
            onClick={() => router.push('/mentors/dashboard')}
            variant="outline"
            className="mb-6"
          >
            ← Back to Dashboard
          </Button>

          {/* Header */}
          <div className="flex items-start justify-between mb-8">
            <div>
              <h1 className="text-4xl md:text-5xl font-display font-black text-transparent bg-clip-text bg-gradient-to-r from-forgePurple-400 via-neuralBlue-400 to-aiElectric-400 mb-3 leading-tight">
                {session.topic}
              </h1>
              <p className="text-xl md:text-2xl text-techGray-300">
                {isMentor ? 'Mentoring Session' : 'Learning Session'}
              </p>
            </div>
            {getStatusBadge(session.status)}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Session Details */}
              <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
                <div className="p-6 md:p-8">
                  <h2 className="text-2xl md:text-3xl font-bold text-white mb-6">
                    Session Details
                  </h2>
                  <div className="space-y-4">
                  <div>
                    <p className="text-sm text-techGray-400">Date & Time</p>
                    <p className="text-lg font-semibold text-white">
                      {date} at {time}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-techGray-400">Duration</p>
                    <p className="text-lg font-semibold text-white">
                      {session.duration_minutes} minutes
                    </p>
                  </div>
                  {session.description && (
                    <div>
                      <p className="text-sm text-techGray-400 mb-2">Description</p>
                      <p className="text-techGray-300 whitespace-pre-wrap leading-relaxed">
                        {session.description}
                      </p>
                    </div>
                  )}
                  {mentor && (
                    <div>
                      <p className="text-sm text-techGray-400 mb-2">
                        {isMentor ? 'Student' : 'Mentor'}
                      </p>
                      <div className="flex items-center gap-3">
                        <Avatar name={isMentor ? student?.full_name : mentor.user?.full_name} size="md" />
                        <p className="text-lg font-semibold text-gray-900">
                          {isMentor
                            ? (student?.full_name || 'Student Name')
                            : (mentor.user?.full_name || mentor.user?.email || 'Mentor')}
                        </p>
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {!isMentor && (() => {
                          const skills = Array.isArray(mentor.expertise)
                            ? mentor.expertise
                            : String(mentor.expertise || '')
                                .split(',')
                                .map(s => s.trim())
                                .filter(Boolean);
                          return skills.map((skill, idx) => (
                            <Chip key={idx}>{skill}</Chip>
                          ));
                        })()}
                      </div>
                    </div>
                  )}
                </div>
                </div>
              </Card>

              {/* Meeting Link */}
              {isMentor && session.status === 'pending' && (
                <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
                  <div className="p-6 md:p-8">
                    <h2 className="text-2xl md:text-3xl font-bold text-white mb-6">
                      Confirm Session
                    </h2>
                    <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-techGray-300 mb-2">
                        Meeting URL *
                      </label>
                      <input
                        type="url"
                        value={meetingUrl}
                        onChange={(e) => setMeetingUrl(e.target.value)}
                        placeholder="https://zoom.us/j/... or https://meet.google.com/..."
                        className="w-full px-4 py-3 bg-deepTech-900/50 border border-white/10 rounded-lg text-white placeholder-techGray-600 focus:ring-2 focus:ring-forgePurple-500 focus:border-forgePurple-500 transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-techGray-300 mb-2">
                        Notes for Student (Optional)
                      </label>
                      <textarea
                        value={mentorNotes}
                        onChange={(e) => setMentorNotes(e.target.value)}
                        rows={3}
                        className="w-full px-4 py-3 bg-deepTech-900/50 border border-white/10 rounded-lg text-white placeholder-techGray-600 focus:ring-2 focus:ring-forgePurple-500 focus:border-forgePurple-500 transition-all"
                        placeholder="Any preparation instructions or materials to review..."
                      />
                    </div>
                    <Button
                      onClick={confirmSession}
                      variant="primary"
                      disabled={updating || !meetingUrl.trim()}
                      className="w-full"
                    >
                      {updating ? 'Confirming...' : 'Confirm Session'}
                    </Button>
                  </div>
                  </div>
                </Card>
              )}

              {/* Meeting Info */}
              {session.meeting_url && (
                <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
                  <div className="p-6 md:p-8">
                    <h2 className="text-2xl md:text-3xl font-bold text-white mb-6">
                      Meeting Information
                    </h2>
                    <div className="space-y-4">
                    <div>
                      <p className="text-sm text-techGray-400 mb-2">Meeting Link</p>
                      <a
                        href={session.meeting_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-neuralBlue-400 hover:text-neuralBlue-300 break-all transition-colors"
                      >
                        {session.meeting_url}
                      </a>
                    </div>
                    <Button
                      onClick={() => window.open(session.meeting_url!, '_blank')}
                      variant="primary"
                      className="w-full"
                    >
                      Join Meeting
                    </Button>
                  </div>
                  </div>
                </Card>
              )}

              {/* Chat Section */}
              {(session.status === 'confirmed' || session.status === 'completed') && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl md:text-3xl font-bold text-white">
                      Session Chat
                    </h2>
                    <Button
                      onClick={() => setShowChat(!showChat)}
                      variant="outline"
                    >
                      {showChat ? 'Hide Chat' : 'Show Chat'}
                    </Button>
                  </div>
                  {showChat && (
                    <MentorChat
                      sessionId={session.id}
                      currentUserId={me.id}
                      otherUserId={isMentor ? session.student_id : mentor!.user_id}
                      token={''} // TODO: Get from auth context
                    />
                  )}
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1 space-y-6">
              {/* Payment Info */}
              <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
                <div className="p-6">
                  <h3 className="text-lg md:text-xl font-bold text-white mb-4">
                    Payment
                  </h3>
                  <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-techGray-400">Amount</span>
                    <span className="font-semibold text-white">
                      ${session.price.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-techGray-400">Status</span>
                    <span className={`font-semibold ${
                      session.payment_status === 'paid' 
                        ? 'text-success' 
                        : 'text-warning'
                    }`}>
                      {session.payment_status.toUpperCase()}
                    </span>
                  </div>
                </div>
                </div>
              </Card>

              {/* Actions */}
              <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
                <div className="p-6">
                  <h3 className="text-lg md:text-xl font-bold text-white mb-4">
                    Actions
                  </h3>
                  <div className="space-y-3">
                  {isMentor && session.status === 'confirmed' && (
                    <Button
                      onClick={completeSession}
                      variant="primary"
                      disabled={updating}
                      className="w-full"
                    >
                      Mark as Completed
                    </Button>
                  )}
                  {session.status === 'pending' && (
                    <Button
                      onClick={cancelSession}
                      variant="secondary"
                      disabled={updating}
                      className="w-full bg-red-600 hover:bg-red-700 text-white"
                    >
                      Cancel Session
                    </Button>
                  )}
                </div>
                </div>
              </Card>

              {/* Mentor Notes */}
              {isMentor && session.status !== 'cancelled' && (
                <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
                  <div className="p-6">
                    <h3 className="text-lg md:text-xl font-bold text-white mb-4">
                      Private Notes
                    </h3>
                    <textarea
                    value={mentorNotes}
                    onChange={(e) => setMentorNotes(e.target.value)}
                    rows={4}
                    className="w-full px-4 py-3 bg-deepTech-900/50 border border-white/10 rounded-lg text-white placeholder-techGray-600 focus:ring-2 focus:ring-forgePurple-500 focus:border-forgePurple-500 transition-all mb-3"
                    placeholder="Your private notes about this session..."
                  />
                    <Button
                      onClick={saveMentorNotes}
                      variant="outline"
                      disabled={updating}
                      className="w-full"
                    >
                      Save Notes
                    </Button>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

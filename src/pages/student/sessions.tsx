'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useProtectedPage } from '@/lib/useProtectedPage';
import { useToast } from '@/components/Toast';
import Layout from '@/components/Layout';
import Button from '@/components/Button';
import Card from '@/components/Card';
import { Calendar, Clock, MapPin, Star, MessageSquare, X } from 'lucide-react';

interface MentorSession {
  id: number;
  mentor_id: number;
  student_id: number;
  mentor_name?: string;
  mentor_rating?: number;
  topic: string;
  description?: string;
  scheduled_at: string;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  duration_minutes: number;
  price?: number;
  meeting_link?: string;
  feedback_submitted?: boolean;
}

interface SessionFeedback {
  session_id: number;
  rating: number;
  feedback_text: string;
  submitted_at: string;
}

export default function StudentSessions() {
  const router = useRouter();
  const { user, loading: authLoading, isAuthorized } = useProtectedPage('user');
  const [sessions, setSessions] = useState<MentorSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed'>('upcoming');
  const [selectedSession, setSelectedSession] = useState<MentorSession | null>(null);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackData, setFeedbackData] = useState({ rating: 5, text: '' });
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token') || '';
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      
      if (!token) {
        throw new Error('No authentication token found. Please log in.');
      }
      
      const response = await fetch(`${apiBase}/api/v1x/mentors/sessions/my`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.error('Response status:', response.status);
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`Failed to load sessions: ${response.status}`);
      }
      
      const data = await response.json();
      // Response has 'sessions' array and 'total' count
      const sessionsList = data.sessions || data.data || data || [];
      setSessions(Array.isArray(sessionsList) ? sessionsList : []);
      setError(null);
    } catch (err) {
      console.error('Error loading sessions:', err);
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  const getFilteredSessions = () => {
    const now = new Date();
    return sessions.filter((session) => {
      const sessionDate = new Date(session.scheduled_at);
      if (filter === 'upcoming') {
        return (session.status === 'confirmed' || session.status === 'pending') && sessionDate > now;
      } else if (filter === 'completed') {
        return session.status === 'completed';
      }
      return true;
    });
  };

  const handleSubmitFeedback = async () => {
    if (!selectedSession) return;

    try {
      setSubmittingFeedback(true);
      const response = await fetch(
        `/api/v1x/mentors/sessions/${selectedSession.id}/feedback`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            rating: feedbackData.rating,
            feedback_text: feedbackData.text,
          }),
        }
      );

      if (response.ok) {
        setShowFeedbackModal(false);
        setFeedbackData({ rating: 5, text: '' });
        loadSessions(); // Reload to show feedback
      }
    } catch (err) {
      alert('Error submitting feedback');
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const handleCancelSession = async (sessionId: number) => {
    if (!confirm('Are you sure you want to cancel this session?')) return;

    try {
      const response = await fetch(
        `/api/v1x/mentors/sessions/${sessionId}/cancel`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ reason: 'Student requested cancellation' }),
        }
      );

      if (response.ok) {
        loadSessions();
      }
    } catch (err) {
      alert('Error cancelling session');
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

  if (loading) {
    return (
      <Layout maxWidth="2xl">
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  const filteredSessions = getFilteredSessions();
  const upcomingCount = sessions.filter((s) => s.status === 'confirmed' || s.status === 'pending').length;
  const completedCount = sessions.filter((s) => s.status === 'completed').length;

  return (
    <Layout maxWidth="2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Mentor Sessions</h1>
        <p className="text-gray-600">View and manage your booked sessions</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-blue-600">{sessions.length}</p>
            <p className="text-sm text-gray-600">Total Sessions</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">{upcomingCount}</p>
            <p className="text-sm text-gray-600">Upcoming</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-purple-600">{completedCount}</p>
            <p className="text-sm text-gray-600">Completed</p>
          </div>
        </Card>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        {(['all', 'upcoming', 'completed'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              filter === tab
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">Error: {error}</p>
        </div>
      )}

      {filteredSessions.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <Calendar size={48} className="mx-auto mb-4 text-gray-400" />
            <p className="text-gray-600 mb-4">No sessions found</p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredSessions.map((session) => (
            <Card key={session.id} className="hover:shadow-lg transition-shadow">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                {/* Left: Session details */}
                <div className="flex-1">
                  <div className="flex items-start gap-4">
                    {/* Mentor Avatar Placeholder */}
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="font-bold text-blue-600">
                        {session.mentor_name?.[0] || 'M'}
                      </span>
                    </div>

                    {/* Session Info */}
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 mb-1">
                        {session.mentor_name || 'Mentor'}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">{session.topic}</p>

                      <div className="flex flex-wrap gap-3 text-sm text-gray-600 mb-2">
                        <div className="flex items-center gap-1">
                          <Calendar size={16} />
                          {formatDate(session.scheduled_at)}
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock size={16} />
                          {formatTime(session.scheduled_at)}
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock size={16} />
                          {session.duration_minutes} min
                        </div>
                      </div>

                      {/* Status Badge */}
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            session.status === 'completed'
                              ? 'bg-green-100 text-green-700'
                              : session.status === 'confirmed'
                              ? 'bg-blue-100 text-blue-700'
                              : session.status === 'pending'
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-red-100 text-red-700'
                          }`}
                        >
                          {session.status?.charAt(0).toUpperCase() + session.status?.slice(1)}
                        </span>
                        {session.mentor_rating && (
                          <div className="flex items-center gap-1 text-yellow-500">
                            <Star size={14} fill="currentColor" />
                            <span className="text-xs font-medium">{session.mentor_rating}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right: Actions */}
                <div className="flex gap-2 md:flex-col">
                  {session.status === 'confirmed' && (
                    <>
                      {session.meeting_link && (
                        <a
                          href={session.meeting_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors text-center"
                        >
                          Join Meeting
                        </a>
                      )}
                      <button
                        onClick={() => handleCancelSession(session.id)}
                        className="px-4 py-2 border border-red-300 text-red-600 text-sm font-medium rounded-lg hover:bg-red-50 transition-colors"
                      >
                        Cancel
                      </button>
                    </>
                  )}

                  {session.status === 'completed' && !session.feedback_submitted && (
                    <button
                      onClick={() => {
                        setSelectedSession(session);
                        setShowFeedbackModal(true);
                      }}
                      className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                    >
                      <MessageSquare size={16} />
                      Add Feedback
                    </button>
                  )}

                  {session.feedback_submitted && session.status === 'completed' && (
                    <span className="px-4 py-2 bg-green-100 text-green-700 text-sm font-medium rounded-lg">
                      Feedback Given
                    </span>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Feedback Modal */}
      {showFeedbackModal && selectedSession && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Add Feedback</h2>
              <button
                onClick={() => setShowFeedbackModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X size={20} />
              </button>
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-3">
                How would you rate this session with {selectedSession.mentor_name}?
              </p>
              <div className="flex gap-2 justify-center mb-4">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setFeedbackData({ ...feedbackData, rating: star })}
                    className="transition-transform hover:scale-125"
                  >
                    <Star
                      size={28}
                      className={
                        star <= feedbackData.rating
                          ? 'text-yellow-400 fill-yellow-400'
                          : 'text-gray-300'
                      }
                    />
                  </button>
                ))}
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your feedback (optional)
              </label>
              <textarea
                value={feedbackData.text}
                onChange={(e) => setFeedbackData({ ...feedbackData, text: e.target.value })}
                placeholder="Tell us about your experience..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 resize-none"
                rows={3}
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowFeedbackModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitFeedback}
                disabled={submittingFeedback}
                className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {submittingFeedback ? 'Submitting...' : 'Submit'}
              </button>
            </div>
          </Card>
        </div>
      )}
    </Layout>
  );
}

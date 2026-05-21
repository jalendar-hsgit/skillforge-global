'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useProtectedPage } from '@/lib/useProtectedPage';
import { useToast } from '@/components/Toast';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import Layout from '@/components/Layout';
import Button from '@/components/Button';
import Card from '@/components/Card';
import {
  getMySessions,
  confirmSession,
  cancelSession,
  getSessionDetails,
  MentorSessionDetail,
  SessionListResponse,
  SESSION_STATUSES,
} from '@/lib/api/mentorSessionApi';

export default function MentorSessionsPage() {
  const router = useRouter();
  const { user, loading: authLoading, isAuthorized } = useProtectedPage('mentor');
  const { addToast } = useToast();

  const [sessions, setSessions] = useState<MentorSessionDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed' | 'cancelled'>('upcoming');
  const [selectedSession, setSelectedSession] = useState<MentorSessionDetail | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [cancellationReason, setCancellationReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [modalAction, setModalAction] = useState<'confirm' | 'cancel' | 'details'>('details');

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthorized) return;
    loadSessions();
  }, [isAuthorized, authLoading]);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      const data = await getMySessions(token);
      setSessions(data.sessions || []);
    } catch (error: any) {
      addToast({
        type: 'error',
        message: 'Failed to load sessions: ' + (error.message || 'Unknown error'),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!selectedSession) return;

    try {
      setIsSubmitting(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      await confirmSession(selectedSession.id, token);
      addToast({ type: 'success', message: 'Session confirmed' });
      setShowModal(false);
      await loadSessions();
    } catch (error: any) {
      addToast({ type: 'error', message: error.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = async () => {
    if (!selectedSession || !cancellationReason.trim()) {
      addToast({ type: 'error', message: 'Please provide a cancellation reason' });
      return;
    }

    try {
      setIsSubmitting(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      await cancelSession(selectedSession.id, cancellationReason, token);
      addToast({ type: 'success', message: 'Session cancelled' });
      setShowModal(false);
      setCancellationReason('');
      await loadSessions();
    } catch (error: any) {
      addToast({ type: 'error', message: error.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const config = SESSION_STATUSES.find(s => s.value === status);
    return (
      <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${config?.color || 'bg-gray-100'}`}>
        {config?.label || status}
      </span>
    );
  };

  const filteredSessions = sessions.filter(session => {
    if (filter === 'all') return true;
    if (filter === 'upcoming') {
      return ['pending', 'confirmed'].includes(session.status) && 
             new Date(session.scheduled_at) > new Date();
    }
    if (filter === 'completed') return session.status === 'completed';
    if (filter === 'cancelled') return ['cancelled', 'no_show'].includes(session.status);
    return true;
  });

  const stats = {
    total: sessions.length,
    upcoming: sessions.filter(s => ['pending', 'confirmed'].includes(s.status) && new Date(s.scheduled_at) > new Date()).length,
    completed: sessions.filter(s => s.status === 'completed').length,
    cancelled: sessions.filter(s => ['cancelled', 'no_show'].includes(s.status)).length,
  };

  if (authLoading) {
    return <LoadingSpinner message="Loading..." />;
  }

  if (!isAuthorized) {
    return null;
  }

  if (loading) {
    return <LoadingSpinner message="Loading your sessions..." />;
  }

  return (
    <Layout maxWidth="2xl">
      <div className="px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Mentor Sessions</h1>
          <p className="text-gray-600">Manage your mentoring sessions and confirmations.</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total', value: stats.total, color: 'text-primary-500' },
            { label: 'Upcoming', value: stats.upcoming, color: 'text-blue-500' },
            { label: 'Completed', value: stats.completed, color: 'text-green-500' },
            { label: 'Cancelled', value: stats.cancelled, color: 'text-red-500' },
          ].map(stat => (
            <Card key={stat.label} className="p-4">
              <div className="text-center">
                <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            </Card>
          ))}
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6">
          {(['all', 'upcoming', 'completed', 'cancelled'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === tab
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Sessions List */}
        {filteredSessions.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-gray-600 mb-4">No sessions in this category</p>
            {filter === 'upcoming' && (
              <p className="text-sm text-gray-500">Students will book sessions once you set your availability</p>
            )}
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredSessions.map(session => {
              const sessionDate = new Date(session.scheduled_at);
              const isUpcoming = sessionDate > new Date() && ['pending', 'confirmed'].includes(session.status);
              const isPending = session.status === 'pending' && sessionDate > new Date();

              return (
                <Card key={session.id} className={`p-6 ${isPending ? 'border-2 border-yellow-300 bg-yellow-50' : ''}`}>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold mb-2">{session.topic}</h3>
                      <div className="space-y-1 text-sm text-gray-600">
                        <p>
                          <span className="font-medium">Date & Time:</span>{' '}
                          {sessionDate.toLocaleDateString()} at {sessionDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                        <p>
                          <span className="font-medium">Duration:</span> {session.duration_minutes} minutes
                        </p>
                        <p>
                          <span className="font-medium">Price:</span> ${session.price.toFixed(2)}
                        </p>
                        {session.description && (
                          <p>
                            <span className="font-medium">Details:</span> {session.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="ml-4">{getStatusBadge(session.status)}</div>
                  </div>

                  {/* Meeting Link */}
                  {session.meeting_url && (
                    <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-sm font-medium mb-2">Meeting Link:</p>
                      <a
                        href={session.meeting_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-500 underline break-all"
                      >
                        {session.meeting_url}
                      </a>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        setSelectedSession(session);
                        setModalAction('details');
                        setShowModal(true);
                      }}
                    >
                      View Details
                    </Button>

                    {isPending && (
                      <>
                        <Button
                          size="sm"
                          onClick={() => {
                            setSelectedSession(session);
                            setModalAction('confirm');
                            setShowModal(true);
                          }}
                        >
                          Confirm
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => {
                            setSelectedSession(session);
                            setModalAction('cancel');
                            setCancellationReason('');
                            setShowModal(true);
                          }}
                        >
                          Decline
                        </Button>
                      </>
                    )}

                    {isUpcoming && !isPending && (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setSelectedSession(session);
                          setModalAction('cancel');
                          setCancellationReason('');
                          setShowModal(true);
                        }}
                      >
                        Cancel
                      </Button>
                    )}

                    {session.status === 'completed' && (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => router.push(`/mentor/sessions/${session.id}/feedback`)}
                      >
                        Leave Feedback
                      </Button>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        )}

        {/* Modal */}
        {showModal && selectedSession && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="absolute inset-0" onClick={() => setShowModal(false)} />
            <Card className="relative p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
              {modalAction === 'details' && (
                <>
                  <h3 className="text-xl font-bold mb-4">Session Details</h3>
                  <div className="space-y-3 mb-6">
                    <div>
                      <p className="text-sm text-gray-600">Topic</p>
                      <p className="font-medium">{selectedSession.topic}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Date & Time</p>
                      <p className="font-medium">
                        {new Date(selectedSession.scheduled_at).toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Duration</p>
                      <p className="font-medium">{selectedSession.duration_minutes} minutes</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Price</p>
                      <p className="font-medium">${selectedSession.price.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Status</p>
                      <p className="font-medium">{getStatusBadge(selectedSession.status)}</p>
                    </div>
                    {selectedSession.description && (
                      <div>
                        <p className="text-sm text-gray-600">Description</p>
                        <p>{selectedSession.description}</p>
                      </div>
                    )}
                    {selectedSession.meeting_url && (
                      <div>
                        <p className="text-sm text-gray-600">Meeting Link</p>
                        <a
                          href={selectedSession.meeting_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary-500 underline text-sm"
                        >
                          {selectedSession.meeting_url}
                        </a>
                      </div>
                    )}
                  </div>
                  <Button className="w-full" onClick={() => setShowModal(false)}>
                    Close
                  </Button>
                </>
              )}

              {modalAction === 'confirm' && (
                <>
                  <h3 className="text-xl font-bold mb-4">Confirm Session?</h3>
                  <p className="text-gray-600 mb-6">
                    This will notify the student that you've confirmed the session.
                  </p>
                  <div className="flex gap-3">
                    <Button
                      variant="secondary"
                      className="flex-1"
                      onClick={() => setShowModal(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      className="flex-1"
                      onClick={handleConfirm}
                      loading={isSubmitting}
                    >
                      Confirm
                    </Button>
                  </div>
                </>
              )}

              {modalAction === 'cancel' && (
                <>
                  <h3 className="text-xl font-bold mb-4">Cancel Session</h3>
                  <p className="text-gray-600 mb-4">
                    Provide a reason for cancellation (shown to student).
                  </p>
                  <textarea
                    value={cancellationReason}
                    onChange={(e) => setCancellationReason(e.target.value)}
                    placeholder="Reason for cancellation..."
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500 mb-4"
                    rows={4}
                  />
                  <div className="flex gap-3">
                    <Button
                      variant="secondary"
                      className="flex-1"
                      onClick={() => setShowModal(false)}
                    >
                      Keep
                    </Button>
                    <Button
                      variant="secondary"
                      className="flex-1"
                      onClick={handleCancel}
                      loading={isSubmitting}
                    >
                      Cancel Session
                    </Button>
                  </div>
                </>
              )}
            </Card>
          </div>
        )}

        {/* Help Info */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="font-bold mb-2">Quick Tips:</h3>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• Confirm pending sessions within 24 hours</li>
            <li>• Always set a meeting link before the session starts</li>
            <li>• Leave feedback after each completed session</li>
            <li>• Students can see when you confirm their booking</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}

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
  getAvailableSlots,
  bookSession,
  getMentorRatings,
  AvailabilitySlot,
  BookSessionRequest,
  SESSION_DURATIONS,
  MentorRating,
} from '@/lib/api/mentorSessionApi';

export default function BookSessionPage() {
  const router = useRouter();
  const { mentorId } = router.query;
  const { user, loading: authLoading, isAuthorized } = useProtectedPage('user');
  const { addToast } = useToast();

  const [availableSlots, setAvailableSlots] = useState<AvailabilitySlot[]>([]);
  const [mentorRating, setMentorRating] = useState<MentorRating | null>(null);
  const [loading, setLoading] = useState(true);

  // Form state
  const [selectedSlot, setSelectedSlot] = useState<AvailabilitySlot | null>(null);
  const [duration, setDuration] = useState(60);
  const [topic, setTopic] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!mentorId) return;
    loadData();
  }, [mentorId]);

  const loadData = async () => {
    if (!mentorId || typeof mentorId !== 'string') return;

    try {
      setLoading(true);
      const [slots, rating] = await Promise.all([
        getAvailableSlots(mentorId),
        getMentorRatings(mentorId).catch(() => null),
      ]);

      setAvailableSlots(slots || []);
      if (rating) setMentorRating(rating);
    } catch (error: any) {
      addToast({
        type: 'error',
        message: 'Failed to load availability: ' + (error.message || 'Unknown error'),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBookSession = async () => {
    if (!selectedSlot) {
      addToast({ type: 'error', message: 'Please select a date and time' });
      return;
    }

    if (!topic.trim()) {
      addToast({ type: 'error', message: 'Please enter a session topic' });
      return;
    }

    if (duration <= 0) {
      addToast({ type: 'error', message: 'Please select a session duration' });
      return;
    }

    try {
      setIsSubmitting(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('Not authenticated');

      // Calculate scheduled time
      const [year, month, day] = selectedSlot.date?.split('-').map(Number) || [
        new Date().getFullYear(),
        new Date().getMonth() + 1,
        new Date().getDate(),
      ];
      const [startHour, startMin] = selectedSlot.start_time.split(':').map(Number);
      const scheduledAt = new Date(year, month - 1, day, startHour, startMin).toISOString();

      const booking: BookSessionRequest = {
        mentor_id: mentorId as string,
        topic,
        description: description || undefined,
        scheduled_at: scheduledAt,
        duration_minutes: duration,
      };

      await bookSession(booking, token);
      addToast({ type: 'success', message: 'Session booked successfully!' });

      // Redirect to student sessions page
      router.push('/student/sessions');
    } catch (error: any) {
      addToast({ type: 'error', message: error.message || 'Booking failed' });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (authLoading) {
    return <LoadingSpinner message="Loading..." />;
  }

  if (!isAuthorized) {
    return null;
  }

  if (loading) {
    return <LoadingSpinner message="Loading mentor availability..." />;
  }

  // Group slots by date
  const slotsByDate = availableSlots.reduce((acc, slot) => {
    const date = slot.date || new Date().toISOString().split('T')[0];
    if (!acc[date]) acc[date] = [];
    acc[date].push(slot);
    return acc;
  }, {} as Record<string, AvailabilitySlot[]>);

  const sortedDates = Object.keys(slotsByDate).sort();

  return (
    <Layout maxWidth="2xl">
      <div className="px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Book a Session</h1>
          <p className="text-gray-600">Schedule a mentoring session with this mentor.</p>
        </div>

        {/* Mentor Info */}
        {mentorRating && (
          <Card className="p-6 mb-8 bg-primary-50 border border-primary-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Mentor Rating</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="text-2xl font-bold text-primary-500">
                    {mentorRating.average_rating.toFixed(1)}
                  </div>
                  <div>
                    <div className="flex gap-0.5">
                      {[...Array(5)].map((_, i) => (
                        <span key={i} className={i < Math.round(mentorRating.average_rating) ? 'text-yellow-400' : 'text-gray-300'}>
                          ★
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-gray-600 mt-1">{mentorRating.total_reviews} reviews</p>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Available Times */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <h2 className="text-xl font-bold mb-4">Select Date & Time</h2>

              {sortedDates.length === 0 ? (
                <p className="text-gray-600 text-center py-8">No available slots currently</p>
              ) : (
                <div className="space-y-4">
                  {sortedDates.map(date => (
                    <div key={date}>
                      <h3 className="font-medium text-gray-700 mb-2">
                        {new Date(date).toLocaleDateString('en-US', {
                          weekday: 'long',
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })}
                      </h3>
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        {slotsByDate[date].map(slot => (
                          <button
                            key={slot.id}
                            onClick={() => setSelectedSlot(slot)}
                            className={`p-3 rounded-lg border-2 transition-all ${
                              selectedSlot?.id === slot.id
                                ? 'border-primary-500 bg-primary-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            <div className="font-medium text-sm">{slot.start_time}</div>
                            <div className="text-xs text-gray-600">{slot.end_time}</div>
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          {/* Booking Form */}
          <div>
            <Card className="p-6 sticky top-4">
              <h2 className="text-xl font-bold mb-4">Session Details</h2>

              <div className="space-y-4">
                {/* Selected Time */}
                {selectedSlot && (
                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-xs text-gray-600">Selected Time</p>
                    <p className="font-medium">
                      {new Date(selectedSlot.date || '').toLocaleDateString()} {selectedSlot.start_time}
                    </p>
                  </div>
                )}

                {/* Duration */}
                <div>
                  <label className="block text-sm font-medium mb-2">Duration</label>
                  <select
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    {SESSION_DURATIONS.map(d => (
                      <option key={d.value} value={d.value}>{d.label}</option>
                    ))}
                  </select>
                </div>

                {/* Topic */}
                <div>
                  <label className="block text-sm font-medium mb-2">Topic *</label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="What do you want to discuss?"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium mb-2">Details</label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Any additional details..."
                    rows={3}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                {/* Book Button */}
                <Button
                  className="w-full"
                  onClick={handleBookSession}
                  disabled={!selectedSlot || !topic.trim()}
                  loading={isSubmitting}
                >
                  Book Session
                </Button>

                <p className="text-xs text-gray-600 text-center">
                  The mentor will confirm within 24 hours
                </p>
              </div>
            </Card>
          </div>
        </div>

        {/* Info */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="font-bold mb-2">Booking Information:</h3>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• Select a date/time from the available slots</li>
            <li>• Enter a session topic (what you want to learn)</li>
            <li>• Click "Book Session" to send your request</li>
            <li>• The mentor will confirm within 24 hours</li>
            <li>• You'll receive a meeting link once confirmed</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}

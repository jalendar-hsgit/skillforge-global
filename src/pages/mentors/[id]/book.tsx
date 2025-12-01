import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { API_BASE } from '@/lib/apiBase';
import SessionPayment from '@/components/SessionPayment';

interface Mentor {
  id: number;
  bio: string;
  expertise: string[];
  hourly_rate: number;
  average_rating: number;
  user?: {
    full_name: string;
  };
}

interface Availability {
  id: number;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export default function BookSessionPage() {
  const router = useRouter();
  const { id } = router.query;
  
  const [mentor, setMentor] = useState<Mentor | null>(null);
  const [availability, setAvailability] = useState<Availability[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<Availability | null>(null);
  
  const [topic, setTopic] = useState('');
  const [notes, setNotes] = useState('');
  const [duration, setDuration] = useState(60);
  
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  // Payment state
  const [showPayment, setShowPayment] = useState(false);
  const [bookedSessionId, setBookedSessionId] = useState<number | null>(null);

  useEffect(() => {
    if (id) {
      fetchMentorAndAvailability();
    }
  }, [id]);

  const fetchMentorAndAvailability = async () => {
    try {
      setLoading(true);

      // Fetch mentor
      const mentorResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/${id}`,
        { credentials: 'include' }
      );
      if (!mentorResponse.ok) throw new Error('Failed to fetch mentor');
      const mentorData = await mentorResponse.json();
      setMentor(mentorData);

      // Fetch availability
      const availabilityResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/availability/${id}`,
        { credentials: 'include' }
      );
      if (availabilityResponse.ok) {
        const availabilityData = await availabilityResponse.json();
        const slots = availabilityData.slots || availabilityData;
        const dataArray = Array.isArray(slots) ? slots : [];
        // Filter to future available slots only
        const futureSlots = dataArray.filter(
          (slot: Availability) => 
            slot.is_available && 
            new Date(slot.start_time) > new Date()
        );
        setAvailability(futureSlots);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBooking = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedSlot) {
      setError('Please select a time slot');
      return;
    }

    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }
    
    if (topic.trim().length < 5) {
      setError('Topic must be at least 5 characters');
      return;
    }

    try {
      setBooking(true);
      setError('');

      const scheduledAt = selectedSlot?.start_time || (() => {
        const now = new Date();
        const fallbackStart = new Date(now.getTime());
        fallbackStart.setDate(now.getDate() + 1);
        fallbackStart.setHours(10, 0, 0, 0);
        return fallbackStart.toISOString();
      })();

      const response = await fetch(`${API_BASE}/api/v1x/mentors/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          mentor_id: Number(id),
          scheduled_at: scheduledAt,
          duration_minutes: duration,
          topic,
          description: notes || undefined
        })
      });

      if (response.status === 401) {
        router.push(`/login?redirect=/mentors/${id}/book`);
        return;
      }

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to book session');
      }

      const sessionData = await response.json();
      setBookedSessionId(sessionData.id);
      
      // Show payment modal if session has a price
      if (sessionData.price > 0) {
        setShowPayment(true);
      } else {
        // Free session, redirect to dashboard
        setSuccess(true);
        setTimeout(() => {
          router.push('/dashboard');
        }, 2000);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBooking(false);
    }
  };
  
  const handlePaymentSuccess = () => {
    setShowPayment(false);
    setSuccess(true);
    setTimeout(() => {
      router.push('/dashboard');
    }, 2000);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const calculateCost = () => {
    if (!mentor) return 0;
    return (mentor.hourly_rate * duration) / 60;
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  if (error && !mentor) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <Card className="bg-red-50 border-red-200">
            <p className="text-red-700">{error}</p>
          </Card>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-deepTech-950 bg-neural py-12 md:py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Back Button */}
          <Button
            onClick={() => router.push(`/mentors/${id}`)}
            variant="outline"
            className="mb-6"
          >
            ← Back to Profile
          </Button>

          {/* Header */}
          <div className="text-center mb-10">
            <h1 className="text-4xl md:text-5xl font-display font-black text-transparent bg-clip-text bg-gradient-to-r from-forgePurple-400 via-neuralBlue-400 to-aiElectric-400 mb-4 leading-tight">
              Book a Session
            </h1>
            <p className="text-xl md:text-2xl text-techGray-300">
              with {mentor?.user?.full_name || 'Mentor'}
            </p>
          </div>

          {/* Payment Modal */}
          {showPayment && bookedSessionId && mentor && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
              <div className="max-w-2xl w-full">
                <div className="flex justify-end mb-2">
                  <button
                    onClick={() => {
                      setShowPayment(false);
                      router.push('/dashboard');
                    }}
                    className="text-white hover:text-gray-300 text-2xl"
                  >
                    ×
                  </button>
                </div>
                <SessionPayment
                  sessionId={bookedSessionId}
                  amount={calculateCost()}
                  onPaymentSuccess={handlePaymentSuccess}
                />
              </div>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <Card className="mb-8 bg-success-dark/20 border border-success/30 backdrop-blur-xl">
              <div className="flex items-center gap-4">
                <svg className="w-10 h-10 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="text-xl font-bold text-white">
                    Session Booked!
                  </h3>
                  <p className="text-success-light">
                    Your booking request has been sent. Redirecting to dashboard...
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Error Message */}
          {error && !success && (
            <Card className="mb-8 bg-error-dark/20 border border-error/30 backdrop-blur-xl">
              <p className="text-error-light">{error}</p>
            </Card>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Booking Form */}
            <div className="lg:col-span-2">
              <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
                <div className="p-6 md:p-8">
                  <h2 className="text-2xl md:text-3xl font-bold text-white mb-8">
                    Session Details
                  </h2>
                
                <form onSubmit={handleBooking} className="space-y-7">
                  {/* Select Time Slot */}
                  <div>
                    <label className="block text-sm font-semibold text-techGray-300 mb-4 tracking-wide">
                      Select Time Slot *
                    </label>
                    {availability.length === 0 ? (
                      <div className="space-y-3">
                        <Card className="bg-neuralBlue-500/10 border border-neuralBlue-500/30 backdrop-blur-xl">
                          <div className="p-4">
                            <p className="text-neuralBlue-200 text-sm">
                              <span className="font-semibold">Demo Mode:</span> No availability slots found.
                              You can still book a session — the system will use a fallback time (tomorrow at 10:00 AM).
                            </p>
                          </div>
                        </Card>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {availability.slice(0, 8).map(slot => (
                          <button
                            key={slot.id}
                            type="button"
                            onClick={() => setSelectedSlot(slot)}
                            className={`p-5 border-2 rounded-lg text-left transition-all duration-300 ${
                              selectedSlot?.id === slot.id
                                ? 'border-forgePurple-500 bg-forgePurple-500/10 shadow-glow-sm'
                                : 'border-white/10 bg-deepTech-900/30 hover:border-neuralBlue-500/50 hover:shadow-glow-sm'
                            }`}
                          >
                            <p className="font-semibold text-white text-lg">
                              {formatDate(slot.start_time)}
                            </p>
                            <p className="text-sm text-techGray-400 mt-1">
                              {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                            </p>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Duration */}
                  <div>
                    <label className="block text-sm font-semibold text-techGray-300 mb-2">
                      Duration (minutes) *
                    </label>
                    <select
                      value={duration}
                      onChange={(e) => setDuration(Number(e.target.value))}
                      className="w-full px-4 py-3 bg-deepTech-900/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-forgePurple-500 focus:border-forgePurple-500 transition-all"
                      required
                    >
                      <option value={30} className="bg-deepTech-900">30 minutes</option>
                      <option value={60} className="bg-deepTech-900">1 hour</option>
                      <option value={90} className="bg-deepTech-900">1.5 hours</option>
                      <option value={120} className="bg-deepTech-900">2 hours</option>
                    </select>
                  </div>

                  {/* Topic */}
                  <div>
                    <label className="block text-sm font-semibold text-techGray-300 mb-2">
                      Session Topic * (min 5 characters)
                    </label>
                    <Input
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="e.g., Learn FastAPI authentication"
                      required
                      minLength={5}
                      className="w-full"
                    />
                  </div>

                  {/* Notes */}
                  <div>
                    <label className="block text-sm font-semibold text-techGray-300 mb-2">
                      Additional Notes
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      rows={4}
                      className="w-full px-4 py-3 bg-deepTech-900/50 border border-white/10 rounded-lg text-white placeholder-techGray-600 focus:ring-2 focus:ring-forgePurple-500 focus:border-forgePurple-500 transition-all"
                      placeholder="What would you like help with? Any specific goals?"
                    />
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={booking || !topic.trim() || (!selectedSlot && availability.length > 0)}
                    className="w-full"
                  >
                    {booking ? 'Booking...' : (mentor && mentor.hourly_rate > 0 ? 'Book & Pay' : 'Book Session')}
                  </Button>
                </form>
                </div>
              </Card>
            </div>

            {/* Booking Summary */}
            <div className="lg:col-span-1">
              <Card className="sticky top-6 bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
                <div className="p-6">
                  <h3 className="text-xl md:text-2xl font-bold text-white mb-6">
                    Booking Summary
                  </h3>
                
                <div className="space-y-5">
                  {/* Mentor Info */}
                  <div className="pb-5 border-b border-white/10">
                    <p className="text-sm text-techGray-400 mb-1">Mentor</p>
                    <p className="font-semibold text-white">
                      {mentor?.user?.full_name || 'Loading...'}
                    </p>
                  </div>

                  {/* Selected Time */}
                  {selectedSlot ? (
                    <div className="pb-5 border-b border-white/10">
                      <p className="text-sm text-techGray-400 mb-1">Date & Time</p>
                      <p className="font-semibold text-white">
                        {formatDate(selectedSlot.start_time)}
                      </p>
                      <p className="text-sm text-techGray-300">
                        {formatTime(selectedSlot.start_time)}
                      </p>
                    </div>
                  ) : availability.length === 0 ? (
                    <div className="pb-5 border-b border-white/10">
                      <p className="text-sm text-techGray-400 mb-1">Date & Time</p>
                      <p className="font-semibold text-neuralBlue-400 text-sm">
                        Demo: Tomorrow at 10:00 AM
                      </p>
                    </div>
                  ) : null}

                  {/* Duration */}
                  <div className="pb-5 border-b border-white/10">
                    <p className="text-sm text-techGray-400 mb-1">Duration</p>
                    <p className="font-semibold text-white">
                      {duration} minutes
                    </p>
                  </div>

                  {/* Cost */}
                  <div>
                    <p className="text-sm text-techGray-400 mb-2">Total Cost</p>
                    <p className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-aiElectric-400 to-neuralBlue-400">
                      ${calculateCost().toFixed(2)}
                    </p>
                    <p className="text-xs text-techGray-500 mt-2">
                      ${mentor?.hourly_rate}/hour
                    </p>
                  </div>
                </div>

                  {/* Info Box */}
                  <div className="mt-6 p-4 bg-neuralBlue-500/10 border border-neuralBlue-500/30 rounded-lg backdrop-blur-sm">
                    <p className="text-sm text-neuralBlue-200">
                      <span className="font-semibold">Note:</span> Your booking will be
                      pending until the mentor confirms. You'll receive an email once confirmed.
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

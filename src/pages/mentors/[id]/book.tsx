import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { API_BASE } from '@/lib/apiBase';

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
        // Filter to future available slots only
        const futureSlots = availabilityData.filter(
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

    try {
      setBooking(true);
      setError('');

      const response = await fetch(`${API_BASE}/api/v1x/mentors/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          mentor_id: Number(id),
          start_time: selectedSlot.start_time,
          duration_minutes: duration,
          topic,
          notes: notes || undefined
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

      setSuccess(true);
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBooking(false);
    }
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
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12">
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
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Book a Session
            </h1>
            <p className="text-xl text-gray-600">
              with {mentor?.user?.full_name || 'Mentor'}
            </p>
          </div>

          {/* Success Message */}
          {success && (
            <Card className="mb-8 bg-green-50 border-green-200">
              <div className="flex items-center gap-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="text-lg font-semibold text-green-900">
                    Session Booked!
                  </h3>
                  <p className="text-green-800">
                    Your booking request has been sent. Redirecting to dashboard...
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Error Message */}
          {error && !success && (
            <Card className="mb-8 bg-red-50 border-red-200">
              <p className="text-red-700">{error}</p>
            </Card>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Booking Form */}
            <div className="lg:col-span-2">
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  Session Details
                </h2>
                
                <form onSubmit={handleBooking} className="space-y-6">
                  {/* Select Time Slot */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Select Time Slot *
                    </label>
                    {availability.length === 0 ? (
                      <Card className="bg-yellow-50 border-yellow-200">
                        <p className="text-yellow-800">
                          No availability slots found. Please check back later or contact the mentor.
                        </p>
                      </Card>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {availability.slice(0, 8).map(slot => (
                          <button
                            key={slot.id}
                            type="button"
                            onClick={() => setSelectedSlot(slot)}
                            className={`p-4 border-2 rounded-lg text-left transition-all ${
                              selectedSlot?.id === slot.id
                                ? 'border-blue-600 bg-blue-50'
                                : 'border-gray-200 hover:border-blue-300'
                            }`}
                          >
                            <p className="font-medium text-gray-900">
                              {formatDate(slot.start_time)}
                            </p>
                            <p className="text-sm text-gray-600">
                              {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                            </p>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Duration */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Duration (minutes) *
                    </label>
                    <select
                      value={duration}
                      onChange={(e) => setDuration(Number(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value={30}>30 minutes</option>
                      <option value={60}>1 hour</option>
                      <option value={90}>1.5 hours</option>
                      <option value={120}>2 hours</option>
                    </select>
                  </div>

                  {/* Topic */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Session Topic *
                    </label>
                    <Input
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="e.g., Learn FastAPI authentication"
                      required
                      className="w-full"
                    />
                  </div>

                  {/* Notes */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Notes
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      rows={4}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="What would you like help with? Any specific goals?"
                    />
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={booking || !selectedSlot || !topic.trim() || availability.length === 0}
                    className="w-full"
                  >
                    {booking ? 'Booking...' : 'Book Session'}
                  </Button>
                </form>
              </Card>
            </div>

            {/* Booking Summary */}
            <div className="lg:col-span-1">
              <Card className="sticky top-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  Booking Summary
                </h3>
                
                <div className="space-y-4">
                  {/* Mentor Info */}
                  <div className="pb-4 border-b border-gray-200">
                    <p className="text-sm text-gray-600 mb-1">Mentor</p>
                    <p className="font-semibold text-gray-900">
                      {mentor?.user?.full_name || 'Loading...'}
                    </p>
                  </div>

                  {/* Selected Time */}
                  {selectedSlot && (
                    <div className="pb-4 border-b border-gray-200">
                      <p className="text-sm text-gray-600 mb-1">Date & Time</p>
                      <p className="font-semibold text-gray-900">
                        {formatDate(selectedSlot.start_time)}
                      </p>
                      <p className="text-sm text-gray-700">
                        {formatTime(selectedSlot.start_time)}
                      </p>
                    </div>
                  )}

                  {/* Duration */}
                  <div className="pb-4 border-b border-gray-200">
                    <p className="text-sm text-gray-600 mb-1">Duration</p>
                    <p className="font-semibold text-gray-900">
                      {duration} minutes
                    </p>
                  </div>

                  {/* Cost */}
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Cost</p>
                    <p className="text-3xl font-bold text-blue-600">
                      ${calculateCost().toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      ${mentor?.hourly_rate}/hour
                    </p>
                  </div>
                </div>

                {/* Info Box */}
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-900">
                    <span className="font-semibold">Note:</span> Your booking will be
                    pending until the mentor confirms. You'll receive an email once confirmed.
                  </p>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

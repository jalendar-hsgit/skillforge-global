import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/apiBase';

interface Mentor {
  id: number;
  user_id: number;
  bio: string;
  expertise: string[];
  hourly_rate: number;
  average_rating: number;
  total_sessions: number;
  status: string;
  created_at: string;
  user?: {
    full_name: string;
    email: string;
  };
}

interface Review {
  id: number;
  rating: number;
  comment: string;
  created_at: string;
  student: {
    full_name: string;
  };
}

interface Availability {
  id: number;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export default function MentorProfilePage() {
  const router = useRouter();
  const { id } = router.query;
  
  const [mentor, setMentor] = useState<Mentor | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [availability, setAvailability] = useState<Availability[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      fetchMentorData();
    }
  }, [id]);

  const fetchMentorData = async () => {
    try {
      setLoading(true);

      // Fetch mentor profile
      const mentorResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/${id}`,
        { credentials: 'include' }
      );
      if (!mentorResponse.ok) throw new Error('Failed to fetch mentor');
      const mentorData = await mentorResponse.json();
      setMentor(mentorData);

      // Fetch reviews
      const reviewsResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/reviews/${id}`,
        { credentials: 'include' }
      );
      if (reviewsResponse.ok) {
        const reviewsData = await reviewsResponse.json();
        setReviews(reviewsData);
      }

      // Fetch availability
      const availabilityResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/availability/${id}`,
        { credentials: 'include' }
      );
      if (availabilityResponse.ok) {
        const availabilityData = await availabilityResponse.json();
        setAvailability(availabilityData);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map(star => (
          <svg
            key={star}
            className={`w-6 h-6 ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
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

  if (error || !mentor) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <Card className="bg-red-50 border-red-200">
            <p className="text-red-700">{error || 'Mentor not found'}</p>
          </Card>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Back Button */}
          <Button
            onClick={() => router.push('/mentors')}
            variant="outline"
            className="mb-6"
          >
            ← Back to Mentors
          </Button>

          {/* Profile Header */}
          <Card className="mb-8">
            <div className="flex flex-col md:flex-row gap-8">
              {/* Avatar */}
              <div className="flex-shrink-0">
                <div className="w-32 h-32 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-5xl font-bold">
                  {mentor.user?.full_name?.charAt(0) || 'M'}
                </div>
              </div>

              {/* Info */}
              <div className="flex-grow">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {mentor.user?.full_name || 'Anonymous Mentor'}
                </h1>
                
                <div className="flex items-center gap-4 mb-4">
                  {renderStars(mentor.average_rating)}
                  <span className="text-gray-600">
                    ({reviews.length} reviews)
                  </span>
                </div>

                <div className="flex items-center gap-6 mb-6">
                  <div>
                    <p className="text-3xl font-bold text-blue-600">
                      ${mentor.hourly_rate}
                    </p>
                    <p className="text-sm text-gray-600">per hour</p>
                  </div>
                  <div className="border-l border-gray-300 pl-6">
                    <p className="text-2xl font-bold text-gray-900">
                      {mentor.total_sessions}
                    </p>
                    <p className="text-sm text-gray-600">sessions completed</p>
                  </div>
                </div>

                <Button
                  variant="primary"
                  onClick={() => router.push(`/mentors/${mentor.id}/book`)}
                  className="px-8"
                >
                  Book a Session
                </Button>
              </div>
            </div>
          </Card>

          {/* About */}
          <Card className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">About</h2>
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {mentor.bio}
            </p>
          </Card>

          {/* Expertise */}
          <Card className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Expertise</h2>
            <div className="flex flex-wrap gap-3">
              {mentor.expertise.map((skill, index) => (
                <span
                  key={index}
                  className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg text-base font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </Card>

          {/* Availability */}
          {availability.length > 0 && (
            <Card className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Available Time Slots
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availability
                  .filter(slot => slot.is_available)
                  .slice(0, 6)
                  .map(slot => (
                    <div
                      key={slot.id}
                      className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors"
                    >
                      <p className="font-medium text-gray-900">
                        {formatDate(slot.start_time)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(slot.start_time).toLocaleTimeString('en-US', {
                          hour: 'numeric',
                          minute: '2-digit'
                        })}
                        {' - '}
                        {new Date(slot.end_time).toLocaleTimeString('en-US', {
                          hour: 'numeric',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  ))}
              </div>
            </Card>
          )}

          {/* Reviews */}
          <Card>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Student Reviews
            </h2>
            {reviews.length === 0 ? (
              <p className="text-gray-600">No reviews yet</p>
            ) : (
              <div className="space-y-6">
                {reviews.map(review => (
                  <div key={review.id} className="border-b border-gray-200 pb-6 last:border-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center text-white font-bold">
                          {review.student.full_name.charAt(0)}
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900">
                            {review.student.full_name}
                          </p>
                          <p className="text-sm text-gray-600">
                            {formatDate(review.created_at)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        {renderStars(review.rating)}
                      </div>
                    </div>
                    <p className="text-gray-700 ml-13">
                      {review.comment}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </Layout>
  );
}

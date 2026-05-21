import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Avatar } from '@/components/Avatar';
import { RatingStars } from '@/components/RatingStars';
import { Chip } from '@/components/Chip';
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
        const reviews = reviewsData.reviews || reviewsData;
        setReviews(Array.isArray(reviews) ? reviews : []);
      }

      // Fetch availability
      const availabilityResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/availability/${id}`,
        { credentials: 'include' }
      );
      if (availabilityResponse.ok) {
        const availabilityData = await availabilityResponse.json();
        const slots = availabilityData.slots || availabilityData;
        setAvailability(Array.isArray(slots) ? slots : []);
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
      <div className="min-h-screen bg-deepTech-950 bg-neural py-12 md:py-16">
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
          <Card className="mb-8 bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
            <div className="p-6 md:p-8">
              <div className="flex flex-col md:flex-row gap-8 md:gap-10">
              {/* Avatar */}
              <div className="flex-shrink-0">
                <Avatar name={mentor.user?.full_name} size="xl" />
              </div>

              {/* Info */}
              <div className="flex-grow">
                <h1 className="text-3xl md:text-4xl font-display font-black text-transparent bg-clip-text bg-gradient-to-r from-forgePurple-400 via-neuralBlue-400 to-aiElectric-400 mb-4">
                  {mentor.user?.full_name || 'Anonymous Mentor'}
                </h1>
                
                <div className="flex items-center gap-4 mb-4">
                  <RatingStars rating={mentor.average_rating} label={`(${reviews.length} reviews)`} />
                </div>

                <div className="flex items-center gap-8 mb-6">
                  <div>
                    <p className="text-4xl font-bold text-aiElectric-400">
                      ${mentor.hourly_rate}
                    </p>
                    <p className="text-sm text-techGray-400">per hour</p>
                  </div>
                  <div className="border-l border-white/20 pl-8">
                    <p className="text-3xl font-bold text-neuralBlue-400">
                      {mentor.total_sessions}
                    </p>
                    <p className="text-sm text-techGray-400">sessions completed</p>
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
            </div>
          </Card>

          {/* About */}
          <Card className="mb-8 bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
            <div className="p-6 md:p-8">
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-6">About</h2>
              <p className="text-techGray-300 leading-relaxed whitespace-pre-wrap text-lg">
                {mentor.bio}
              </p>
            </div>
          </Card>

          {/* Expertise */}
          <Card className="mb-8 bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
            <div className="p-6 md:p-8">
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-6">Expertise</h2>
              <div className="flex flex-wrap gap-3">
              {(() => {
                const skills = Array.isArray(mentor.expertise)
                  ? mentor.expertise
                  : String(mentor.expertise || '')
                      .split(',')
                      .map(s => s.trim())
                      .filter(Boolean);
                return skills.map((skill, index) => (
                  <Chip key={index} className="text-base px-4 py-2 rounded-lg">{skill}</Chip>
                ));
              })()}
            </div>
            </div>
          </Card>

          {/* Availability */}
          {availability.length > 0 && (
            <Card className="mb-8 bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
              <div className="p-6 md:p-8">
                <h2 className="text-2xl md:text-3xl font-bold text-white mb-6">
                  Available Time Slots
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {availability
                  .filter(slot => slot.is_available)
                  .slice(0, 6)
                  .map(slot => (
                    <div
                      key={slot.id}
                      className="p-5 bg-deepTech-900/30 border border-white/10 rounded-lg hover:border-forgePurple-500/50 hover:shadow-glow-sm transition-all duration-300"
                    >
                      <p className="font-semibold text-white text-lg">
                        {formatDate(slot.start_time)}
                      </p>
                      <p className="text-sm text-techGray-400 mt-1">
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
              </div>
            </Card>
          )}

          {/* Reviews */}
          <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
            <div className="p-6 md:p-8">
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-8">
                Student Reviews
              </h2>
            {reviews.length === 0 ? (
              <p className="text-techGray-400 text-lg">No reviews yet</p>
            ) : (
              <div className="space-y-6">
                {reviews.map(review => {
                  const studentName = review.student?.full_name || 'Student';
                  return (
                    <div key={review.id} className="border-b border-white/10 pb-6 last:border-0">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center text-white font-bold">
                            {studentName.charAt(0)}
                          </div>
                          <div>
                            <p className="font-semibold text-white">
                              {studentName}
                            </p>
                            <p className="text-sm text-techGray-400">
                              {formatDate(review.created_at)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          {renderStars(review.rating)}
                        </div>
                      </div>
                      <p className="text-techGray-300 ml-13 leading-relaxed">
                        {review.comment}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  );
}

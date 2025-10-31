import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
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

export default function MentorsPage() {
  const router = useRouter();
  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [expertiseFilter, setExpertiseFilter] = useState('');
  const [minRating, setMinRating] = useState<number | undefined>();
  const [maxPrice, setMaxPrice] = useState<number | undefined>();

  useEffect(() => {
    fetchMentors();
  }, [expertiseFilter, minRating, maxPrice]);

  const fetchMentors = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (expertiseFilter) params.append('expertise', expertiseFilter);
      if (minRating) params.append('min_rating', minRating.toString());
      if (maxPrice) params.append('max_price', maxPrice.toString());

      const response = await fetch(
        `${API_BASE}/api/v1x/mentors/search?${params.toString()}`,
        { credentials: 'include' }
      );

      if (!response.ok) throw new Error('Failed to fetch mentors');

      const data = await response.json();
      setMentors(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredMentors = mentors.filter(mentor =>
    mentor.user?.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    mentor.bio.toLowerCase().includes(searchQuery.toLowerCase()) ||
    mentor.expertise.some(e => e.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map(star => (
          <svg
            key={star}
            className={`w-5 h-5 ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
        <span className="ml-2 text-sm text-gray-600">
          {rating.toFixed(1)} ({mentors.find(m => m.average_rating === rating)?.total_sessions || 0} sessions)
        </span>
      </div>
    );
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Find Your Perfect Mentor
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Learn from experienced developers who completed their learning journey
            </p>
            <Button
              onClick={() => router.push('/mentors/become')}
              variant="primary"
            >
              Become a Mentor
            </Button>
          </div>

          {/* Search and Filters */}
          <Card className="mb-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-2">
                <Input
                  type="text"
                  placeholder="Search by name, expertise, or bio..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full"
                />
              </div>
              <div>
                <select
                  value={expertiseFilter}
                  onChange={(e) => setExpertiseFilter(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Expertise</option>
                  <option value="Python">Python</option>
                  <option value="JavaScript">JavaScript</option>
                  <option value="React">React</option>
                  <option value="FastAPI">FastAPI</option>
                  <option value="Node.js">Node.js</option>
                  <option value="TypeScript">TypeScript</option>
                </select>
              </div>
              <div>
                <select
                  value={minRating || ''}
                  onChange={(e) => setMinRating(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Ratings</option>
                  <option value="4">4+ Stars</option>
                  <option value="4.5">4.5+ Stars</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Loading/Error States */}
          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading mentors...</p>
            </div>
          )}

          {error && (
            <Card className="bg-red-50 border-red-200">
              <p className="text-red-700">{error}</p>
            </Card>
          )}

          {/* Mentors Grid */}
          {!loading && !error && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredMentors.map((mentor) => (
                <Card
                  key={mentor.id}
                  className="hover:shadow-xl transition-shadow cursor-pointer"
                  onClick={() => router.push(`/mentors/${mentor.id}`)}
                >
                  <div className="space-y-4">
                    {/* Avatar & Name */}
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                        {mentor.user?.full_name?.charAt(0) || 'M'}
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">
                          {mentor.user?.full_name || 'Anonymous Mentor'}
                        </h3>
                        <p className="text-sm text-gray-500">
                          ${mentor.hourly_rate}/hour
                        </p>
                      </div>
                    </div>

                    {/* Rating */}
                    {renderStars(mentor.average_rating)}

                    {/* Bio */}
                    <p className="text-gray-700 line-clamp-3">
                      {mentor.bio}
                    </p>

                    {/* Expertise Tags */}
                    <div className="flex flex-wrap gap-2">
                      {mentor.expertise.slice(0, 4).map((skill, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                      {mentor.expertise.length > 4 && (
                        <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                          +{mentor.expertise.length - 4} more
                        </span>
                      )}
                    </div>

                    {/* Sessions Count */}
                    <div className="pt-4 border-t border-gray-200">
                      <p className="text-sm text-gray-600">
                        <span className="font-semibold">{mentor.total_sessions}</span> sessions completed
                      </p>
                    </div>

                    {/* Book Button */}
                    <Button
                      variant="primary"
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/mentors/${mentor.id}/book`);
                      }}
                      className="w-full"
                    >
                      Book Session
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Empty State */}
          {!loading && !error && filteredMentors.length === 0 && (
            <Card className="text-center py-12">
              <svg
                className="w-16 h-16 text-gray-400 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No mentors found
              </h3>
              <p className="text-gray-600">
                Try adjusting your filters or search query
              </p>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
}

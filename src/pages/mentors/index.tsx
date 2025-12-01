import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { API_BASE } from '@/lib/apiBase';
import { Avatar } from '@/components/Avatar';
import { RatingStars } from '@/components/RatingStars';
import { Chip } from '@/components/Chip';
import { MentorCardSkeleton } from '@/components/MentorCardSkeleton';

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



  return (
    <Layout>
      <div className="min-h-screen bg-deepTech-950 bg-neural py-12 md:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-12 md:mb-16">
            <h1 className="text-4xl md:text-6xl font-display font-black text-transparent bg-clip-text bg-gradient-to-r from-forgePurple-400 via-neuralBlue-400 to-aiElectric-400 mb-6 leading-tight tracking-tight">
              Find Your Perfect Mentor
            </h1>
            <p className="text-lg md:text-xl text-techGray-300 mb-8 leading-relaxed max-w-3xl mx-auto">
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
          <Card className="mb-8 bg-glass backdrop-blur-xl border border-white/10 shadow-glass">
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
                  className="w-full px-4 py-3 bg-deepTech-900/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-forgePurple-500 focus:border-forgePurple-500 transition-all"
                >
                  <option value="" className="bg-deepTech-900">All Expertise</option>
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
                  className="w-full px-4 py-3 bg-deepTech-900/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-forgePurple-500 focus:border-forgePurple-500 transition-all"
                >
                  <option value="" className="bg-deepTech-900">All Ratings</option>
                  <option value="4">4+ Stars</option>
                  <option value="4.5">4.5+ Stars</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Loading/Error States */}
          {loading && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <MentorCardSkeleton key={i} />
              ))}
            </div>
          )}

          {error && (
            <Card className="bg-error-dark/20 border border-error/30 backdrop-blur-xl">
              <p className="text-error-light">{error}</p>
            </Card>
          )}

          {/* Mentors Grid */}
          {!loading && !error && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredMentors.map((mentor) => (
                <Card
                  key={mentor.id}
                  className="bg-glass backdrop-blur-xl border border-white/10 hover:border-forgePurple-500/50 hover:shadow-glow transition-all duration-300 cursor-pointer group"
                  onClick={() => router.push(`/mentors/${mentor.id}`)}
                >
                  <div className="p-6 space-y-5">
                    {/* Avatar & Name */}
                    <div className="flex items-center gap-4">
                      <Avatar name={mentor.user?.full_name} size="lg" />
                      <div>
                        <h3 className="text-xl font-bold text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-forgePurple-400 group-hover:to-neuralBlue-400 transition-all">
                          {mentor.user?.full_name || 'Anonymous Mentor'}
                        </h3>
                        <p className="text-sm text-aiElectric-400 font-semibold">
                          ${mentor.hourly_rate}/hour
                        </p>
                      </div>
                    </div>

                    {/* Rating */}
                    <RatingStars rating={mentor.average_rating} />

                    {/* Bio */}
                    <p className="text-techGray-300 line-clamp-3 leading-relaxed">
                      {mentor.bio}
                    </p>

                    {/* Expertise Tags */}
                    <div className="flex flex-wrap gap-2">
                      {(() => {
                        const skills = Array.isArray(mentor.expertise)
                          ? mentor.expertise
                          : String(mentor.expertise || '')
                              .split(',')
                              .map(s => s.trim())
                              .filter(Boolean);
                        return skills.slice(0, 4).map((skill, index) => (
                          <Chip key={index}>{skill}</Chip>
                        ));
                      })()}
                      {(() => {
                        const skills = Array.isArray(mentor.expertise)
                          ? mentor.expertise
                          : String(mentor.expertise || '')
                              .split(',')
                              .map(s => s.trim())
                              .filter(Boolean);
                        return skills.length > 4 ? (
                          <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                            +{skills.length - 4} more
                          </span>
                        ) : null;
                      })()}
                    </div>

                    {/* Sessions Count */}
                    <div className="pt-4 border-t border-white/10">
                      <p className="text-sm text-techGray-400">
                        <span className="font-bold text-neuralBlue-400">{mentor.total_sessions}</span> sessions completed
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
            <Card className="bg-glass backdrop-blur-xl border border-white/10 text-center py-16">
              <svg
                className="w-20 h-20 text-techGray-600 mx-auto mb-6 opacity-50"
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
              <h3 className="text-2xl font-bold text-white mb-3">
                No mentors found
              </h3>
              <p className="text-techGray-400 text-lg">
                Try adjusting your filters or search query
              </p>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
}

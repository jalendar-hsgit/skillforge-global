import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { apiCall } from '@/lib/api';

interface TrendingItem {
  id: number;
  content_type: string;
  content_id: number;
  trend_score: number;
  rank: number;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  velocity: number;
  extra_data: {
    [key: string]: any;
  };
  started_trending: string;
}

type TrendingCategory = 'challenges' | 'solutions' | 'users';

const TrendingPage: React.FC = () => {
  const [trending, setTrending] = useState<TrendingItem[]>([]);
  const [category, setCategory] = useState<TrendingCategory>('challenges');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrending();
  }, [category]);

  const loadTrending = async () => {
    try {
      setLoading(true);
      const endpoint = `/activity/trending/${category}?limit=50`;
      const response = await apiCall('GET', endpoint);
      setTrending(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Failed to load trending:', error);
      setTrending([]);
    } finally {
      setLoading(false);
    }
  };

  const getTrendingIcon = (contentType: string) => {
    switch (contentType) {
      case 'challenge':
        return '⚡';
      case 'solution':
        return '✅';
      case 'user':
        return '⭐';
      default:
        return '🔥';
    }
  };

  const getMedalIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return `#${rank}`;
    }
  };

  const getVelocityLabel = (velocity: number) => {
    if (velocity > 100) return '🚀 Skyrocketing';
    if (velocity > 50) return '📈 Rising Fast';
    if (velocity > 10) return '📊 Rising';
    return '→ Stable';
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
              <span className="text-3xl">🔥</span>
              Trending Now
            </h1>
            <p className="text-gray-400">Discover what's hot in the community</p>
          </div>

          {/* Category Selector */}
          <div className="flex gap-4 mb-8 flex-wrap">
            {(['challenges', 'solutions', 'users'] as TrendingCategory[]).map((cat) => (
              <button
                key={cat}
                onClick={() => {
                  setCategory(cat);
                }}
                className={`px-6 py-2 rounded-lg font-semibold transition capitalize ${
                  category === cat
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Trending List */}
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin">
                <div className="w-8 h-8 border-4 border-gray-600 border-t-orange-500 rounded-full"></div>
              </div>
              <p className="text-gray-400 mt-4">Loading trending...</p>
            </div>
          ) : trending.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">No trending items yet</p>
            </div>
          ) : (
            <div className="space-y-4">
              {trending.map((item) => (
                <div
                  key={item.id}
                  className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition border border-gray-700 hover:border-orange-500"
                >
                  <div className="flex items-start justify-between gap-4">
                    {/* Rank and Content */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl font-bold">
                          {getMedalIcon(item.rank)}
                        </span>
                        <div>
                          <h3 className="text-xl font-bold text-white">
                            {getTrendingIcon(item.content_type)}{' '}
                            {item.extra_data?.title || item.extra_data?.name || `${item.content_type} #${item.content_id}`}
                          </h3>
                          {item.extra_data?.difficulty && (
                            <p className="text-sm text-gray-400">
                              Difficulty: <span className="text-orange-400">{item.extra_data.difficulty}</span>
                            </p>
                          )}
                          {item.extra_data?.category && (
                            <p className="text-sm text-gray-400">
                              Category: <span className="text-purple-400">{item.extra_data.category}</span>
                            </p>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-400">
                        {getVelocityLabel(item.velocity)}
                      </p>
                    </div>

                    {/* Metrics */}
                    <div className="flex gap-6 text-right">
                      <div>
                        <p className="text-2xl font-bold text-blue-400">{item.views}</p>
                        <p className="text-xs text-gray-400">Views</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-red-400">{item.likes}</p>
                        <p className="text-xs text-gray-400">Likes</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-green-400">{item.comments}</p>
                        <p className="text-xs text-gray-400">Comments</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-yellow-400">
                          {item.trend_score.toFixed(0)}
                        </p>
                        <p className="text-xs text-gray-400">Score</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default TrendingPage;

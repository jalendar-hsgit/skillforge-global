import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import ActivityCard from '@/components/ActivityCard';
import { apiGet, apiPost, apiDelete } from '@/lib/api';

interface Activity {
  id: number;
  user_id: number;
  user: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  activity_type: string;
  title: string;
  description?: string;
  points_earned: number;
  like_count: number;
  comment_count: number;
  view_count: number;
  created_at: string;
}

interface FeedResponse {
  total: number;
  activities: Activity[];
}

const FeedPage: React.FC = () => {
  const router = useRouter();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const [feedType, setFeedType] = useState<'personal' | 'global'>('personal');
  const LIMIT = 20;

  useEffect(() => {
    loadFeed();
  }, [feedType, skip]);

  const loadFeed = async () => {
    try {
      setLoading(true);
      const endpoint = feedType === 'personal' 
        ? `/activity/feed/personal?skip=${skip}&limit=${LIMIT}`
        : `/activity/feed/global?skip=${skip}&limit=${LIMIT}`;
      
      const response = await apiGet(endpoint);
      setActivities(response.activities || []);
      setTotal(response.total || 0);
    } catch (error) {
      console.error('Failed to load feed:', error);
      setActivities([]);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (activityId: number) => {
    try {
      await apiPost(`/activity/${activityId}/like`, {});
      // Refresh the activity
      const updated = activities.map(a => 
        a.id === activityId ? { ...a, like_count: a.like_count + 1 } : a
      );
      setActivities(updated);
    } catch (error) {
      console.error('Failed to like activity:', error);
    }
  };

  const handleUnlike = async (activityId: number) => {
    try {
      await apiDelete(`/activity/${activityId}/like`);
      const updated = activities.map(a => 
        a.id === activityId ? { ...a, like_count: Math.max(0, a.like_count - 1) } : a
      );
      setActivities(updated);
    } catch (error) {
      console.error('Failed to unlike activity:', error);
    }
  };

  const handleLoadMore = () => {
    setSkip(skip + LIMIT);
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-2xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">Activity Feed</h1>
            <p className="text-gray-400">Discover what's happening in the community</p>
          </div>

          {/* Feed Type Selector */}
          <div className="flex gap-4 mb-8">
            <button
              onClick={() => {
                setFeedType('personal');
                setSkip(0);
              }}
              className={`px-6 py-2 rounded-lg font-semibold transition ${
                feedType === 'personal'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Personal Feed
            </button>
            <button
              onClick={() => {
                setFeedType('global');
                setSkip(0);
              }}
              className={`px-6 py-2 rounded-lg font-semibold transition ${
                feedType === 'global'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Global Feed
            </button>
          </div>

          {/* Activities List */}
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin">
                <div className="w-8 h-8 border-4 border-gray-600 border-t-blue-500 rounded-full"></div>
              </div>
              <p className="text-gray-400 mt-4">Loading activities...</p>
            </div>
          ) : activities.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">
                {feedType === 'personal'
                  ? 'Start following users to see their activities!'
                  : 'No activities yet. Be the first to make a move!'}
              </p>
            </div>
          ) : (
            <>
              <div className="space-y-6">
                {activities.map((activity) => (
                  <ActivityCard
                    key={activity.id}
                    activity={activity}
                    onLike={() => handleLike(activity.id)}
                    onUnlike={() => handleUnlike(activity.id)}
                  />
                ))}
              </div>

              {/* Load More Button */}
              {skip + LIMIT < total && (
                <div className="mt-8 text-center">
                  <button
                    onClick={handleLoadMore}
                    className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
                  >
                    Load More Activities
                  </button>
                </div>
              )}

              {/* Pagination Info */}
              <div className="mt-8 text-center text-gray-400">
                Showing {Math.min(skip + LIMIT, total)} of {total} activities
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default FeedPage;

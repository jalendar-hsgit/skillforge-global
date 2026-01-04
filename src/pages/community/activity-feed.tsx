import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Heart, MessageCircle, Share2, User, Clock, Award } from 'lucide-react';
import Link from 'next/link';

interface ActivityItem {
  id: number;
  user_id: number;
  user_name: string;
  user_avatar: string;
  activity_type: string;
  title: string;
  description: string;
  timestamp: string;
  likes: number;
  comments: number;
  shares: number;
  is_liked: boolean;
  related_id?: number;
  related_title?: string;
}

export default function ActivityFeedPage() {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchActivities();
  }, [filter]);

  const fetchActivities = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const url = new URL(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/feed`);
      if (filter !== 'all') {
        url.searchParams.append('activity_type', filter);
      }

      const res = await fetch(url.toString(), {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const data = await res.json();
        setActivities(data.activities || []);
      }
    } catch (err) {
      console.error('Failed to fetch activities:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleLike = async (activityId: number) => {
    try {
      const token = localStorage.getItem('token');
      const activity = activities.find(a => a.id === activityId);
      if (!activity) return;

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'}/api/v1x/feed/${activityId}/like`,
        {
          method: activity.is_liked ? 'DELETE' : 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (res.ok) {
        setActivities(activities.map(a =>
          a.id === activityId
            ? {
                ...a,
                is_liked: !a.is_liked,
                likes: a.is_liked ? a.likes - 1 : a.likes + 1,
              }
            : a
        ));
      }
    } catch (err) {
      console.error('Failed to like activity:', err);
    }
  };

  const timeAgo = (date: string) => {
    const now = new Date();
    const then = new Date(date);
    const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'challenge_solved':
        return '🎯';
      case 'course_completed':
        return '🎓';
      case 'quiz_passed':
        return '✅';
      case 'solution_shared':
        return '💡';
      case 'achievement_earned':
        return '🏆';
      case 'follower_joined':
        return '👥';
      default:
        return '⭐';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Activity Feed</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">See what your network is doing</p>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {[
            { value: 'all', label: 'All Activity' },
            { value: 'challenge_solved', label: 'Challenges' },
            { value: 'course_completed', label: 'Courses' },
            { value: 'achievement_earned', label: 'Achievements' },
            { value: 'solution_shared', label: 'Solutions' },
          ].map(tab => (
            <button
              key={tab.value}
              onClick={() => setFilter(tab.value)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition ${
                filter === tab.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Activity Feed */}
        <div className="space-y-4">
          {activities.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                No activities yet. Follow users to see their updates!
              </p>
              <Link href="/social/following" className="text-blue-600 dark:text-blue-400 hover:underline mt-2 block">
                Find users to follow
              </Link>
            </div>
          ) : (
            activities.map(activity => (
              <div
                key={activity.id}
                className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition"
              >
                {/* Activity Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center text-xl">
                      {getActivityIcon(activity.activity_type)}
                    </div>
                    <div>
                      <Link href={`/profile/${activity.user_id}`} className="font-semibold text-gray-900 dark:text-white hover:text-blue-600">
                        {activity.user_name}
                      </Link>
                      <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                        <Clock className="w-3 h-3" />
                        {timeAgo(activity.timestamp)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Activity Content */}
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {activity.title}
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300">{activity.description}</p>

                  {/* Related Item */}
                  {activity.related_title && (
                    <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded border border-gray-200 dark:border-gray-600">
                      <p className="text-sm text-gray-600 dark:text-gray-400">Related to:</p>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {activity.related_title}
                      </p>
                    </div>
                  )}
                </div>

                {/* Activity Actions */}
                <div className="flex items-center gap-6 pt-4 border-t border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400">
                  <button
                    onClick={() => toggleLike(activity.id)}
                    className={`flex items-center gap-2 hover:text-blue-600 dark:hover:text-blue-400 transition ${
                      activity.is_liked ? 'text-red-600 dark:text-red-400' : ''
                    }`}
                  >
                    <Heart
                      className="w-5 h-5"
                      fill={activity.is_liked ? 'currentColor' : 'none'}
                    />
                    <span>{activity.likes}</span>
                  </button>

                  <button className="flex items-center gap-2 hover:text-blue-600 dark:hover:text-blue-400 transition">
                    <MessageCircle className="w-5 h-5" />
                    <span>{activity.comments}</span>
                  </button>

                  <button className="flex items-center gap-2 hover:text-blue-600 dark:hover:text-blue-400 transition">
                    <Share2 className="w-5 h-5" />
                    <span>{activity.shares}</span>
                  </button>

                  <button className="ml-auto px-4 py-2 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/50 transition">
                    View Details
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </Layout>
  );
}

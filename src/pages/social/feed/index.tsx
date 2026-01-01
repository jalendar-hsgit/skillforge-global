import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import SocialFeedItem from '@/components/social/SocialFeedItem';

interface FeedItem {
  id: number;
  type: 'post' | 'achievement' | 'course-completed' | 'skill-added';
  author: {
    id: number;
    name: string;
    avatar?: string;
  };
  content: string;
  timestamp: string;
  likes: number;
  comments: number;
  isLiked: boolean;
  image?: string;
  metadata?: {
    courseTitle?: string;
    skillName?: string;
    achievementName?: string;
  };
}

export default function SocialFeedPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [postContent, setPostContent] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    fetchFeed();
  }, [isAuthenticated]);

  const fetchFeed = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/social/feed`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch feed');
      const data = await response.json();
      setFeed(data.feed || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading feed');
      console.error('Feed fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePostSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!postContent.trim()) return;

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/social/posts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: postContent })
      });

      if (!response.ok) throw new Error('Failed to create post');
      setPostContent('');
      await fetchFeed();
    } catch (err) {
      console.error('Post creation error:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading feed...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Social Feed - SkillForge</title>
        <meta name="description" content="Connect with learners and celebrate achievements" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
        <div className="max-w-2xl mx-auto px-4">
          {/* Header */}
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            🌟 Social Feed
          </h1>

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-8">
              {error}
            </div>
          )}

          {/* Post Creator */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-8">
            <div className="flex gap-4 mb-4">
              <img
                src={user?.avatar || `https://ui-avatars.com/api/?name=${user?.name}&background=random`}
                alt={user?.name}
                className="w-12 h-12 rounded-full flex-shrink-0"
              />
              <form onSubmit={handlePostSubmit} className="flex-1">
                <textarea
                  value={postContent}
                  onChange={(e) => setPostContent(e.target.value)}
                  placeholder="Share your learning journey, achievements, or ask a question..."
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
                <div className="flex justify-between items-center mt-4">
                  <div className="flex gap-2">
                    <button type="button" className="text-xl hover:bg-gray-100 dark:hover:bg-gray-700 p-2 rounded">
                      📷
                    </button>
                    <button type="button" className="text-xl hover:bg-gray-100 dark:hover:bg-gray-700 p-2 rounded">
                      😊
                    </button>
                  </div>
                  <button
                    type="submit"
                    disabled={!postContent.trim()}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors"
                  >
                    Post
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Feed Items */}
          {feed.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                No posts yet. Be the first to share! 🚀
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {feed.map((item) => (
                <SocialFeedItem
                  key={item.id}
                  id={item.id}
                  type={item.type}
                  author={item.author}
                  content={item.content}
                  timestamp={item.timestamp}
                  likes={item.likes}
                  comments={item.comments}
                  isLiked={item.isLiked}
                  image={item.image}
                  metadata={item.metadata}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

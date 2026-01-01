import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import ForumTopicCard from '@/components/forum/ForumTopicCard';

interface ForumTopic {
  id: number;
  title: string;
  description: string;
  threadCount: number;
  replyCount: number;
  latestActivity: string;
  category: string;
  icon: string;
}

export default function CommunityForumsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [topics, setTopics] = useState<ForumTopic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    fetchTopics();
  }, [isAuthenticated, selectedCategory]);

  const fetchTopics = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(
        `${apiBase}/api/v1x/community/forums${selectedCategory !== 'all' ? `?category=${selectedCategory}` : ''}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!response.ok) throw new Error('Failed to fetch forums');
      const data = await response.json();
      setTopics(data.topics || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading forums');
      console.error('Forum fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { id: 'all', label: 'All Topics', icon: '📋' },
    { id: 'general', label: 'General Discussion', icon: '💬' },
    { id: 'courses', label: 'Course Help', icon: '📚' },
    { id: 'projects', label: 'Project Showcase', icon: '🚀' },
    { id: 'jobs', label: 'Job Market', icon: '💼' },
    { id: 'mentorship', label: 'Mentorship', icon: '👨‍🏫' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading forums...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Community Forums - SkillForge</title>
        <meta name="description" content="Join community discussions and forums" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="mb-12">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              💬 Community Forums
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Join discussions, ask questions, and help others learn
            </p>
          </div>

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-8">
              {error}
            </div>
          )}

          {/* Action Button */}
          <div className="mb-8">
            <Link href="/community/forums/new-topic">
              <button className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
                ➕ Start New Topic
              </button>
            </Link>
          </div>

          {/* Category Tabs */}
          <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
                  selectedCategory === cat.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:border-blue-600 dark:hover:border-blue-400'
                }`}
              >
                {cat.icon} {cat.label}
              </button>
            ))}
          </div>

          {/* Topics List */}
          {topics.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                No topics found in this category
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {topics.map((topic) => (
                <ForumTopicCard
                  key={topic.id}
                  id={topic.id}
                  title={topic.title}
                  description={topic.description}
                  threadCount={topic.threadCount}
                  replyCount={topic.replyCount}
                  latestActivity={topic.latestActivity}
                  category={topic.category}
                  icon={topic.icon}
                />
              ))}
            </div>
          )}

          {/* Stats */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {topics.length}
              </div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">
                Active Topics
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                {topics.reduce((sum, t) => sum + t.threadCount, 0)}
              </div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">
                Total Discussions
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                {topics.reduce((sum, t) => sum + t.replyCount, 0)}
              </div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">
                Total Replies
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

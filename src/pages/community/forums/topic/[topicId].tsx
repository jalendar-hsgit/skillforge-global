import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import ForumThreadCard from '@/components/forum/ForumThreadCard';

interface ForumThread {
  id: number;
  title: string;
  author: {
    id: number;
    name: string;
    avatar?: string;
  };
  preview: string;
  views: number;
  replyCount: number;
  createdAt: string;
  isPinned: boolean;
  isSolved: boolean;
  topicId: number;
  topicTitle: string;
}

export default function ForumTopicPage() {
  const router = useRouter();
  const { topicId } = router.query;
  const { user, isAuthenticated } = useAuth();
  const [threads, setThreads] = useState<ForumThread[]>([]);
  const [topic, setTopic] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('latest');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (topicId) {
      fetchTopic();
    }
  }, [isAuthenticated, topicId]);

  const fetchTopic = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(
        `${apiBase}/api/v1x/community/forums/topic/${topicId}?sort=${sortBy}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!response.ok) throw new Error('Failed to fetch topic');
      const data = await response.json();
      setTopic(data.topic);
      setThreads(data.threads || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading topic');
      console.error('Topic fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading topic...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{topic?.title} - SkillForge Forums</title>
        <meta name="description" content={topic?.description} />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
        <div className="max-w-4xl mx-auto px-4">
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2 text-sm">
            <Link href="/community/forums" className="text-blue-600 dark:text-blue-400 hover:underline">
              Forums
            </Link>
            <span className="text-gray-400">›</span>
            <span className="text-gray-600 dark:text-gray-400">{topic?.title}</span>
          </div>

          {/* Header */}
          {topic && (
            <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg p-8 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-4xl">{topic.icon}</span>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                    {topic.title}
                  </h1>
                  <p className="text-gray-600 dark:text-gray-400 mt-2">
                    {topic.description}
                  </p>
                </div>
              </div>

              <div className="flex gap-6 text-sm text-gray-600 dark:text-gray-400">
                <span>📌 {topic.threadCount} discussions</span>
                <span>💬 {topic.replyCount} replies</span>
                <span>🕐 {topic.latestActivity}</span>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-8">
              {error}
            </div>
          )}

          {/* Action and Sort */}
          <div className="mb-8 flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
            <Link href={`/community/forums/topic/${topicId}/new-thread`}>
              <button className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
                ➕ Create Thread
              </button>
            </Link>

            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value);
                fetchTopic();
              }}
              className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="latest">Latest Replies</option>
              <option value="popular">Most Popular</option>
              <option value="unanswered">Unanswered</option>
              <option value="solved">Solved</option>
            </select>
          </div>

          {/* Threads List */}
          {threads.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                No threads in this topic yet
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {threads.map((thread) => (
                <ForumThreadCard
                  key={thread.id}
                  id={thread.id}
                  title={thread.title}
                  author={thread.author}
                  preview={thread.preview}
                  views={thread.views}
                  replyCount={thread.replyCount}
                  createdAt={thread.createdAt}
                  isPinned={thread.isPinned}
                  isSolved={thread.isSolved}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

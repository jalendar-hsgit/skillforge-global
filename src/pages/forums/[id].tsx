import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { apiCall } from '@/lib/api';

interface Thread {
  id: number;
  title: string;
  content: string;
  creator: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  thread_type: string;
  status: string;
  view_count: number;
  reply_count: number;
  vote_count: number;
  created_at: string;
  updated_at: string;
  tags?: string[];
}

interface Reply {
  id: number;
  content: string;
  author: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  vote_count: number;
  is_accepted_answer: boolean;
  created_at: string;
  edited_count: number;
}

interface ThreadDetailResponse {
  id: number;
  title: string;
  content: string;
  creator: any;
  thread_type: string;
  status: string;
  view_count: number;
  reply_count: number;
  vote_count: number;
  created_at: string;
  replies?: Reply[];
  [key: string]: any;
}

const ForumThreadPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const [thread, setThread] = useState<ThreadDetailResponse | null>(null);
  const [replies, setReplies] = useState<Reply[]>([]);
  const [loading, setLoading] = useState(true);
  const [replyContent, setReplyContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (id) {
      loadThread();
    }
  }, [id]);

  const loadThread = async () => {
    try {
      setLoading(true);
      const threadData = await apiCall('GET', `/forums/threads/${id}`);
      setThread(threadData);

      const repliesData = await apiCall('GET', `/forums/threads/${id}/replies?limit=50`);
      setReplies(Array.isArray(repliesData) ? repliesData : []);
    } catch (error) {
      console.error('Failed to load thread:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReply = async () => {
    if (!replyContent.trim()) return;

    try {
      setSubmitting(true);
      const newReply = await apiCall('POST', `/forums/threads/${id}/replies`, {
        content: replyContent,
      });

      setReplies([...replies, newReply]);
      setReplyContent('');
    } catch (error) {
      console.error('Failed to submit reply:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleVote = async (replyId: number) => {
    try {
      await apiCall('POST', `/forums/replies/${replyId}/vote?vote_type=upvote`, {});
      // Refresh replies
      await loadThread();
    } catch (error) {
      console.error('Failed to vote:', error);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin mb-4">
              <div className="w-8 h-8 border-4 border-gray-600 border-t-blue-500 rounded-full"></div>
            </div>
            <p className="text-gray-400">Loading thread...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!thread) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
          <p className="text-gray-400 text-lg">Thread not found</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Thread Header */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
            <div className="flex items-start justify-between gap-4 mb-4">
              <h1 className="text-3xl font-bold text-white flex-1">{thread.title}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                thread.status === 'answered' ? 'bg-green-900 text-green-200' : 'bg-blue-900 text-blue-200'
              }`}>
                {thread.status}
              </span>
            </div>

            <div className="flex items-center gap-3 mb-4 pb-4 border-b border-gray-700">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">
                  {thread.creator.username.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <p className="font-semibold text-white">{thread.creator.username}</p>
                <p className="text-xs text-gray-400">Asked {formatDate(thread.created_at)}</p>
              </div>
            </div>

            <div className="prose prose-invert max-w-none">
              <p className="text-gray-300 whitespace-pre-wrap">{thread.content}</p>
            </div>

            {thread.tags && thread.tags.length > 0 && (
              <div className="mt-4 flex gap-2 flex-wrap">
                {thread.tags.map((tag) => (
                  <span key={tag} className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-sm">
                    {tag}
                  </span>
                ))}
              </div>
            )}

            <div className="mt-6 flex gap-8 text-gray-400 text-sm">
              <div>👁️ {thread.view_count} views</div>
              <div>💬 {thread.reply_count} replies</div>
              <div>👍 {thread.vote_count} votes</div>
            </div>
          </div>

          {/* Replies */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white mb-6">
              Answers ({replies.length})
            </h2>

            {replies.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-400">No replies yet. Be the first to answer!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {replies.map((reply) => (
                  <div key={reply.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-start justify-between gap-4 mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-blue-600 flex items-center justify-center">
                          <span className="text-white font-bold text-sm">
                            {reply.author.username.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="font-semibold text-white">{reply.author.username}</p>
                          <p className="text-xs text-gray-400">{formatDate(reply.created_at)}</p>
                        </div>
                      </div>
                      {reply.is_accepted_answer && (
                        <span className="px-3 py-1 bg-green-900 text-green-200 rounded-full text-sm font-semibold">
                          ✓ Accepted
                        </span>
                      )}
                    </div>

                    <p className="text-gray-300 whitespace-pre-wrap mb-4">{reply.content}</p>

                    <div className="flex gap-4">
                      <button
                        onClick={() => handleVote(reply.id)}
                        className="flex items-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition text-sm"
                      >
                        👍 {reply.vote_count}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Reply Form */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-4">Your Answer</h3>
            <textarea
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
              placeholder="Share your thoughts, solution, or answer..."
              rows={6}
              className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
            />
            <button
              onClick={handleSubmitReply}
              disabled={submitting || !replyContent.trim()}
              className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-semibold transition"
            >
              {submitting ? 'Posting...' : 'Post Reply'}
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ForumThreadPage;

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { PageContainer, LoadingState, EmptyState } from '@/components/PageLayout';
import { apiCall, apiPost } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

interface Thread {
  id: number;
  title: string;
  content: string;
  creator: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  category?: {
    id: number;
    name: string;
    icon_emoji?: string;
  };
  thread_type: string;
  status: string;
  view_count: number;
  reply_count: number;
  vote_count: number;
  created_at: string;
  updated_at: string;
  tags?: string[];
  is_pinned?: boolean;
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

const ForumThreadPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const { user } = useAuth();
  const [thread, setThread] = useState<Thread | null>(null);
  const [replies, setReplies] = useState<Reply[]>([]);
  const [loading, setLoading] = useState(true);
  const [replyContent, setReplyContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [votingReply, setVotingReply] = useState<number | null>(null);

  useEffect(() => {
    if (id) {
      loadThread();
    }
  }, [id]);

  const loadThread = async () => {
    try {
      setLoading(true);
      const threadData = await apiCall(`/api/v1x/forums/threads/${id}`);
      setThread(threadData);

      const repliesData = await apiCall(`/api/v1x/forums/threads/${id}/replies?limit=50`);
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
      const newReply = await apiPost(`/api/v1x/forums/threads/${id}/replies`, {
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
      setVotingReply(replyId);
      await apiPost(`/api/v1x/forums/replies/${replyId}/vote?vote_type=upvote`, {});
      setReplies(replies.map(r => 
        r.id === replyId ? { ...r, vote_count: r.vote_count + 1 } : r
      ));
    } catch (error) {
      console.error('Failed to vote:', error);
    } finally {
      setVotingReply(null);
    }
  };

  const formatRelativeDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    const days = Math.floor(diff / 86400);
    if (days === 1) return 'yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getThreadTypeIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      question: '❓',
      discussion: '💬',
      announcement: '📢',
      resource: '📚',
      bug_report: '🐛',
    };
    return icons[type] || '📌';
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
          <LoadingState message="Loading thread..." />
        </div>
      </Layout>
    );
  }

  if (!thread) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
          <EmptyState
            icon="🔍"
            title="Thread not found"
            description="This thread may have been deleted or moved."
            action={
              <Link href="/forums" className="px-6 py-3 bg-gradient-to-r from-forgePurple to-neuralBlue text-white rounded-xl font-semibold hover:opacity-90 transition">
                  Back to Forums
              </Link>
            }
          />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <Head>
        <title>{thread.title} - Forums - SkillForge</title>
        <meta name="description" content={thread.content.slice(0, 160)} />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-white/60 mb-6">
            <Link href="/forums" className="hover:text-white transition">Forums</Link>
            <span>›</span>
            {thread.category && (
              <>
                <span className="text-white/80">{thread.category.icon_emoji} {thread.category.name}</span>
                <span>›</span>
              </>
            )}
            <span className="text-white/40 truncate max-w-[200px]">{thread.title}</span>
          </nav>

          {/* Thread Header */}
          <PageContainer variant="glass" className="mb-8">
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <span className="text-2xl">{getThreadTypeIcon(thread.thread_type)}</span>
              {thread.is_pinned && (
                <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm font-semibold">📌 Pinned</span>
              )}
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                thread.status === 'answered' || thread.status === 'resolved'
                  ? 'bg-green-500/20 text-green-400' 
                  : thread.status === 'closed'
                  ? 'bg-gray-500/20 text-gray-400'
                  : 'bg-blue-500/20 text-blue-400'
              }`}>
                {thread.status === 'answered' || thread.status === 'resolved' ? '✓ ' : ''}{thread.status}
              </span>
            </div>

            <h1 className="text-3xl md:text-4xl font-bold text-white mb-6 leading-tight">{thread.title}</h1>

            <div className="flex items-center gap-4 mb-6 pb-6 border-b border-white/10">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-xl font-bold shadow-lg">
                {thread.creator.avatar_url ? (
                  <img src={thread.creator.avatar_url} alt={thread.creator.username} className="w-full h-full rounded-xl object-cover" />
                ) : (
                  thread.creator.username.charAt(0).toUpperCase()
                )}
              </div>
              <div>
                <p className="font-bold text-white text-lg">{thread.creator.username}</p>
                <p className="text-sm text-white/60">Asked {formatRelativeDate(thread.created_at)}</p>
              </div>
            </div>

            <div className="prose prose-invert max-w-none mb-6">
              <p className="text-white/90 whitespace-pre-wrap leading-relaxed text-lg">{thread.content}</p>
            </div>

            {thread.tags && thread.tags.length > 0 && (
              <div className="flex gap-2 flex-wrap mb-6">
                {thread.tags.map((tag) => (
                  <span key={tag} className="px-3 py-1 bg-white/10 text-white/70 rounded-full text-sm border border-white/10">#{tag}</span>
                ))}
              </div>
            )}

            <div className="flex gap-6 text-white/60 text-sm pt-6 border-t border-white/10">
              <div className="flex items-center gap-2"><span className="text-lg">👁️</span><span>{thread.view_count} views</span></div>
              <div className="flex items-center gap-2"><span className="text-lg">💬</span><span>{thread.reply_count} replies</span></div>
              <div className="flex items-center gap-2"><span className="text-lg">👍</span><span>{thread.vote_count} votes</span></div>
            </div>
          </PageContainer>

          {/* Replies */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2 mb-6">
              <span>💬</span> Answers ({replies.length})
            </h2>

            {replies.length === 0 ? (
              <PageContainer variant="card" className="text-center py-12">
                <div className="text-5xl mb-4">🤔</div>
                <p className="text-white/70 text-lg mb-2">No answers yet</p>
                <p className="text-white/50">Be the first to share your knowledge!</p>
              </PageContainer>
            ) : (
              <div className="space-y-4">
                {replies.filter(r => r.is_accepted_answer).map((reply) => (
                  <ReplyCard key={reply.id} reply={reply} formatRelativeDate={formatRelativeDate} onVote={() => handleVote(reply.id)} isVoting={votingReply === reply.id} isAccepted />
                ))}
                {replies.filter(r => !r.is_accepted_answer).map((reply) => (
                  <ReplyCard key={reply.id} reply={reply} formatRelativeDate={formatRelativeDate} onVote={() => handleVote(reply.id)} isVoting={votingReply === reply.id} />
                ))}
              </div>
            )}
          </div>

          {/* Reply Form */}
          <PageContainer variant="glass">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><span>✏️</span> Your Answer</h3>
            <textarea
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
              placeholder="Share your thoughts, solution, or answer..."
              rows={5}
              className="w-full px-4 py-3 bg-white/10 text-white rounded-xl border border-white/20 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none resize-none placeholder-white/40"
            />
            <div className="flex items-center justify-between mt-4">
              <p className="text-sm text-white/50">Be kind and constructive</p>
              <button
                onClick={handleSubmitReply}
                disabled={submitting || !replyContent.trim()}
                className="px-6 py-3 bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 disabled:opacity-50 text-white rounded-xl font-semibold transition-all shadow-lg shadow-purple-500/25 flex items-center gap-2"
              >
                {submitting ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Posting...
                  </>
                ) : (
                  <>📤 Post Answer</>
                )}
              </button>
            </div>
          </PageContainer>
        </div>
      </div>
    </Layout>
  );
};

interface ReplyCardProps {
  reply: Reply;
  formatRelativeDate: (date: string) => string;
  onVote: () => void;
  isVoting: boolean;
  isAccepted?: boolean;
}

const ReplyCard: React.FC<ReplyCardProps> = ({ reply, formatRelativeDate, onVote, isVoting, isAccepted }) => (
  <div className={`bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-xl p-6 border transition-all ${
    isAccepted ? 'border-green-500/30 shadow-lg shadow-green-500/10' : 'border-white/10 hover:border-white/20'
  }`}>
    <div className="flex items-start justify-between gap-4 mb-4">
      <div className="flex items-center gap-3">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold shadow-lg ${
          isAccepted ? 'bg-gradient-to-br from-green-500 to-emerald-600' : 'bg-gradient-to-br from-purple-500 to-blue-600'
        }`}>
          {reply.author.avatar_url ? (
            <img src={reply.author.avatar_url} alt={reply.author.username} className="w-full h-full rounded-xl object-cover" />
          ) : (
            reply.author.username.charAt(0).toUpperCase()
          )}
        </div>
        <div>
          <p className="font-bold text-white">{reply.author.username}</p>
          <p className="text-sm text-white/60">{formatRelativeDate(reply.created_at)}{reply.edited_count > 0 && <span className="text-white/40"> · edited</span>}</p>
        </div>
      </div>
      {isAccepted && <span className="px-3 py-1.5 bg-green-500/20 text-green-400 rounded-full text-sm font-bold flex items-center gap-1.5"><span>✓</span> Accepted Answer</span>}
    </div>
    <div className="prose prose-invert max-w-none mb-4">
      <p className="text-white/90 whitespace-pre-wrap leading-relaxed">{reply.content}</p>
    </div>
    <div className="flex items-center gap-4 pt-4 border-t border-white/10">
      <button onClick={onVote} disabled={isVoting} className={`flex items-center gap-2 px-4 py-2 rounded-lg transition font-medium ${
        reply.vote_count > 0 ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' : 'bg-white/10 text-white/70 hover:bg-white/20'
      } disabled:opacity-50`}>
        {isVoting ? <div className="w-4 h-4 border-2 border-current/30 border-t-current rounded-full animate-spin" /> : <span>👍</span>}
        <span>{reply.vote_count}</span>
      </button>
      <button className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white/70 hover:bg-white/20 rounded-lg transition"><span>💬</span><span>Reply</span></button>
      <button className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white/70 hover:bg-white/20 rounded-lg transition"><span>🔗</span><span>Share</span></button>
    </div>
  </div>
);

export default ForumThreadPage;

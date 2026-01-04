import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { PageHeader, PageContainer, LoadingState } from '@/components/PageLayout';
import { apiCall, apiPost } from '@/lib/api';
import Link from 'next/link';

interface Category {
  id: number;
  name: string;
  slug: string;
  icon_emoji?: string;
}

const CreateThreadPage: React.FC = () => {
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [categoryId, setCategoryId] = useState<number | ''>('');
  const [threadType, setThreadType] = useState('question');
  const [tags, setTags] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await apiCall('/api/v1x/forums/categories');
      setCategories(response || []);
      if (response && response.length > 0) {
        setCategoryId(response[0].id);
      }
    } catch (err) {
      console.error('Failed to load categories:', err);
      setError('Failed to load categories');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!title.trim() || !content.trim() || !categoryId) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setSubmitting(true);
      const tagsArray = tags
        .split(',')
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0);

      const thread = await apiPost('/api/v1x/forums/threads', {
        title,
        content,
        category_id: Number(categoryId),
        thread_type: threadType,
        tags: tagsArray,
      });

      router.push(`/forums/${thread.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create thread');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
          <LoadingState message="Loading..." />
        </div>
      </Layout>
    );
  }

  const threadTypes = [
    { value: 'question', label: 'Question', icon: '❓', desc: 'Ask for help or clarification' },
    { value: 'discussion', label: 'Discussion', icon: '💬', desc: 'Start a conversation' },
    { value: 'resource', label: 'Resource', icon: '📚', desc: 'Share useful content' },
    { value: 'bug_report', label: 'Bug Report', icon: '🐛', desc: 'Report an issue' },
  ];

  return (
    <Layout>
      <Head>
        <title>Create Thread - Forums - SkillForge</title>
        <meta name="description" content="Create a new forum thread" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-white/60 mb-6">
            <Link href="/forums" className="hover:text-white transition">Forums</Link>
            <span>›</span>
            <span className="text-white/40">Create Thread</span>
          </nav>

          {/* Header */}
          <PageHeader
            title="Create New Thread"
            subtitle="Ask a question or start a discussion with the community"
            icon="✏️"
          />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
            {/* Main Form */}
            <div className="lg:col-span-2">
              <PageContainer variant="glass">
                <form onSubmit={handleSubmit}>
                  {error && (
                    <div className="mb-6 p-4 bg-red-500/20 border border-red-500/30 text-red-200 rounded-xl flex items-center gap-3">
                      <span className="text-xl">⚠️</span>
                      {error}
                    </div>
                  )}

                  {/* Thread Type Selection */}
                  <div className="mb-6">
                    <label className="block text-white font-semibold mb-3">What type of thread?</label>
                    <div className="grid grid-cols-2 gap-3">
                      {threadTypes.map((type) => (
                        <button
                          key={type.value}
                          type="button"
                          onClick={() => setThreadType(type.value)}
                          className={`p-4 rounded-xl text-left transition-all ${
                            threadType === type.value
                              ? 'bg-gradient-to-r from-forgePurple to-neuralBlue border-transparent shadow-lg shadow-purple-500/20'
                              : 'bg-white/5 border-white/10 hover:bg-white/10'
                          } border`}
                        >
                          <div className="flex items-center gap-3 mb-1">
                            <span className="text-2xl">{type.icon}</span>
                            <span className="font-semibold text-white">{type.label}</span>
                          </div>
                          <p className="text-sm text-white/60 ml-9">{type.desc}</p>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Category Selection */}
                  <div className="mb-6">
                    <label className="block text-white font-semibold mb-2">Category *</label>
                    <select
                      value={categoryId}
                      onChange={(e) => setCategoryId(Number(e.target.value))}
                      className="w-full px-4 py-3 bg-white/10 text-white rounded-xl border border-white/20 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none"
                      required
                    >
                      <option value="" className="bg-gray-800">Select a category</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id} className="bg-gray-800">
                          {cat.icon_emoji} {cat.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Title */}
                  <div className="mb-6">
                    <label className="block text-white font-semibold mb-2">Title *</label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="What is your question or topic?"
                      maxLength={300}
                      className="w-full px-4 py-3 bg-white/10 text-white rounded-xl border border-white/20 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none placeholder-white/40"
                      required
                    />
                    <p className="text-xs text-white/50 mt-1.5">{title.length}/300 characters</p>
                  </div>

                  {/* Content */}
                  <div className="mb-6">
                    <label className="block text-white font-semibold mb-2">Content *</label>
                    <textarea
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      placeholder="Provide more details about your question or discussion..."
                      rows={10}
                      className="w-full px-4 py-3 bg-white/10 text-white rounded-xl border border-white/20 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none placeholder-white/40 resize-vertical"
                      required
                    />
                  </div>

                  {/* Tags */}
                  <div className="mb-8">
                    <label className="block text-white font-semibold mb-2">Tags</label>
                    <input
                      type="text"
                      value={tags}
                      onChange={(e) => setTags(e.target.value)}
                      placeholder="python, javascript, algorithms (comma-separated)"
                      className="w-full px-4 py-3 bg-white/10 text-white rounded-xl border border-white/20 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none placeholder-white/40"
                    />
                    <p className="text-xs text-white/50 mt-1.5">Add up to 5 tags to help others find your post</p>
                  </div>

                  {/* Submit Buttons */}
                  <div className="flex gap-4">
                    <button
                      type="submit"
                      disabled={submitting}
                      className="flex-1 px-8 py-4 bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 disabled:opacity-50 text-white rounded-xl font-semibold transition-all shadow-lg shadow-purple-500/25 flex items-center justify-center gap-2"
                    >
                      {submitting ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Creating...
                        </>
                      ) : (
                        <>
                          <span>🚀</span>
                          Create Thread
                        </>
                      )}
                    </button>
                    <button
                      type="button"
                      onClick={() => router.back()}
                      className="px-6 py-4 bg-white/10 hover:bg-white/20 text-white rounded-xl font-semibold transition border border-white/10"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </PageContainer>
            </div>

            {/* Sidebar - Guidelines */}
            <div className="lg:col-span-1 space-y-6">
              <PageContainer variant="card">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <span>📋</span> Posting Guidelines
                </h3>
                <ul className="text-white/70 space-y-3 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Search existing threads before posting</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Be respectful and constructive</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Include error messages and code snippets</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Use clear language and proper grammar</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-400">✗</span>
                    <span>No spam, self-promotion, or inappropriate content</span>
                  </li>
                </ul>
              </PageContainer>

              <PageContainer variant="card">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <span>💡</span> Tips for Good Questions
                </h3>
                <ul className="text-white/70 space-y-3 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-400">•</span>
                    <span>Be specific about what you're trying to achieve</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-400">•</span>
                    <span>Explain what you've already tried</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-400">•</span>
                    <span>Share relevant code or error messages</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-400">•</span>
                    <span>Include your environment details if relevant</span>
                  </li>
                </ul>
              </PageContainer>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CreateThreadPage;

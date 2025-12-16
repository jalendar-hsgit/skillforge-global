import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { apiCall } from '@/lib/api';

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
      const response = await apiCall('GET', '/forums/categories');
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

      const thread = await apiCall('POST', '/forums/threads', {
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
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin mb-4">
              <div className="w-8 h-8 border-4 border-gray-600 border-t-blue-500 rounded-full"></div>
            </div>
            <p className="text-gray-400">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">Create a New Thread</h1>
            <p className="text-gray-400">Ask a question or start a discussion with the community</p>
          </div>

          <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg p-8 border border-gray-700">
            {error && (
              <div className="mb-6 p-4 bg-red-900 border border-red-700 text-red-200 rounded-lg">
                {error}
              </div>
            )}

            {/* Category Selection */}
            <div className="mb-6">
              <label className="block text-white font-semibold mb-2">Category *</label>
              <select
                value={categoryId}
                onChange={(e) => setCategoryId(Number(e.target.value))}
                className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                required
              >
                <option value="">Select a category</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.icon_emoji} {cat.name}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-400 mt-1">Choose the most relevant category</p>
            </div>

            {/* Thread Type */}
            <div className="mb-6">
              <label className="block text-white font-semibold mb-2">Thread Type</label>
              <div className="flex gap-4">
                {[
                  { value: 'question', label: '❓ Question' },
                  { value: 'discussion', label: '💬 Discussion' },
                  { value: 'resource', label: '📚 Resource' },
                  { value: 'bug_report', label: '🐛 Bug Report' },
                ].map((type) => (
                  <label key={type.value} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="threadType"
                      value={type.value}
                      checked={threadType === type.value}
                      onChange={(e) => setThreadType(e.target.value)}
                      className="w-4 h-4"
                    />
                    <span className="text-white">{type.label}</span>
                  </label>
                ))}
              </div>
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
                className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none placeholder-gray-500"
                required
              />
              <p className="text-xs text-gray-400 mt-1">Be specific and descriptive</p>
            </div>

            {/* Content */}
            <div className="mb-6">
              <label className="block text-white font-semibold mb-2">Content *</label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Provide more details about your question or discussion..."
                rows={10}
                className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none placeholder-gray-500 resize-vertical"
                required
              />
              <p className="text-xs text-gray-400 mt-1">Include code examples if relevant</p>
            </div>

            {/* Tags */}
            <div className="mb-6">
              <label className="block text-white font-semibold mb-2">Tags</label>
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="python, javascript, algorithms (comma-separated)"
                className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none placeholder-gray-500"
              />
              <p className="text-xs text-gray-400 mt-1">Add up to 5 tags to help others find your post</p>
            </div>

            {/* Submit Button */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={submitting}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-semibold transition"
              >
                {submitting ? 'Creating...' : 'Create Thread'}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="px-8 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold transition"
              >
                Cancel
              </button>
            </div>
          </form>

          {/* Guidelines */}
          <div className="mt-8 bg-blue-900 border border-blue-700 rounded-lg p-6">
            <h3 className="text-lg font-bold text-blue-200 mb-3">📋 Community Guidelines</h3>
            <ul className="text-blue-100 space-y-2 text-sm">
              <li>✓ Search existing threads before posting to avoid duplicates</li>
              <li>✓ Be respectful and constructive in discussions</li>
              <li>✓ Include error messages, code snippets, and relevant context</li>
              <li>✓ Use clear language and proper grammar</li>
              <li>✓ No spam, self-promotion, or inappropriate content</li>
            </ul>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CreateThreadPage;

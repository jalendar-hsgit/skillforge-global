/**
 * Share Solution Dialog
 * Allow users to share their solutions with the community
 */

'use client';

import React, { useState } from 'react';
import solutionAPI from '@/lib/solutions';

interface ShareSolutionDialogProps {
  challengeId: number;
  code: string;
  language: string;
  onSuccess?: () => void;
}

export default function ShareSolutionDialog({
  challengeId,
  code,
  language,
  onSuccess,
}: ShareSolutionDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    explanation: '',
    complexity_explanation: '',
    approach_tags: '',
    difficulty_for_user: 'medium' as const,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);

      const tags = formData.approach_tags
        .split(',')
        .map(tag => tag.trim())
        .filter(Boolean);

      await solutionAPI.shareSolution(challengeId, {
        code,
        language,
        explanation: formData.explanation || undefined,
        complexity_explanation: formData.complexity_explanation || undefined,
        approach_tags: tags.length > 0 ? tags : undefined,
        difficulty_for_user: formData.difficulty_for_user,
      });

      setIsOpen(false);
      setFormData({
        explanation: '',
        complexity_explanation: '',
        approach_tags: '',
        difficulty_for_user: 'medium',
      });

      if (onSuccess) onSuccess();
      alert('Solution shared successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to share solution');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Trigger button */}
      <button
        onClick={() => setIsOpen(true)}
        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
      >
        📤 Share Solution
      </button>

      {/* Modal overlay */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">Share Your Solution</h2>
              <button
                onClick={() => setIsOpen(false)}
                disabled={loading}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ✕
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                  {error}
                </div>
              )}

              {/* Code display */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Solution ({language})
                </label>
                <pre className="bg-gray-50 border border-gray-300 rounded-lg p-4 text-xs overflow-x-auto max-h-48">
                  <code className="font-mono text-gray-900">{code}</code>
                </pre>
              </div>

              {/* Explanation */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Explanation (Optional)
                </label>
                <textarea
                  value={formData.explanation}
                  onChange={e =>
                    setFormData({ ...formData, explanation: e.target.value })
                  }
                  placeholder="Explain your approach and any key insights..."
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Complexity Analysis */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time & Space Complexity (Optional)
                </label>
                <input
                  type="text"
                  value={formData.complexity_explanation}
                  onChange={e =>
                    setFormData({ ...formData, complexity_explanation: e.target.value })
                  }
                  placeholder="e.g., O(n log n) time, O(n) space"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Approach Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Approach Tags (Optional)
                </label>
                <input
                  type="text"
                  value={formData.approach_tags}
                  onChange={e =>
                    setFormData({ ...formData, approach_tags: e.target.value })
                  }
                  placeholder="e.g., two-pointer, sorting, dynamic-programming (comma-separated)"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Help others find your solution by tagging the key algorithms/techniques used
                </p>
              </div>

              {/* Difficulty */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  How difficult was this for you?
                </label>
                <div className="flex gap-3">
                  {['easy', 'medium', 'hard'].map(level => (
                    <label
                      key={level}
                      className="flex items-center cursor-pointer"
                    >
                      <input
                        type="radio"
                        name="difficulty"
                        value={level}
                        checked={formData.difficulty_for_user === level}
                        onChange={e =>
                          setFormData({
                            ...formData,
                            difficulty_for_user: e.target.value as 'easy' | 'medium' | 'hard',
                          })
                        }
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700 capitalize">{level}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Info box */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
                <p className="font-medium mb-2">💡 Tips for better solutions:</p>
                <ul className="space-y-1 text-xs">
                  <li>✓ Add a clear explanation of your approach</li>
                  <li>✓ Include time and space complexity analysis</li>
                  <li>✓ Tag the key algorithms/techniques used</li>
                  <li>✓ Help others learn from your solution!</li>
                </ul>
              </div>

              {/* Actions */}
              <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  disabled={loading}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 font-medium"
                >
                  {loading ? 'Sharing...' : '📤 Share Solution'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

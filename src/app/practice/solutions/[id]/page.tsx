/**
 * Solution Details Page
 * View full code, discussion, and voting
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import solutionAPI, { DetailedSolution } from '@/lib/solutions';

interface SolutionDetailsProps {
  params: {
    id: string;
  };
}

export default function SolutionDetails({ params }: SolutionDetailsProps) {
  const router = useRouter();
  const [solution, setSolution] = useState<DetailedSolution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userVote, setUserVote] = useState<string | null>(null);

  useEffect(() => {
    loadSolution();
  }, [params.id]);

  const loadSolution = async () => {
    try {
      setLoading(true);
      const data = await solutionAPI.getSolution(parseInt(params.id));
      setSolution(data);
      setUserVote(data.user_vote || null);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load solution');
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (voteType: 'helpful' | 'unhelpful') => {
    if (!solution) return;
    try {
      await solutionAPI.voteSolution(solution.id, voteType);
      setUserVote(voteType);
      loadSolution(); // Reload to get updated counts
    } catch (err) {
      console.error('Failed to vote:', err);
    }
  };

  const handleBookmark = async () => {
    if (!solution) return;
    try {
      await solutionAPI.bookmarkSolution(solution.id);
      alert('Solution bookmarked!');
    } catch (err) {
      console.error('Failed to bookmark:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !solution) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Solution Not Found</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <button
                onClick={() => router.back()}
                className="text-blue-600 hover:underline mb-4"
              >
                ← Back
              </button>
              <h1 className="text-3xl font-bold text-gray-900">Community Solution</h1>
            </div>
            <button
              onClick={handleBookmark}
              className="text-3xl hover:opacity-70 transition-opacity"
              title="Bookmark solution"
            >
              ⭐
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
            <div>
              <strong>Author:</strong> {solution.user.username}
            </div>
            <div>
              <strong>Language:</strong>{' '}
              <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded">
                {solution.language}
              </span>
            </div>
            <div>
              <strong>Score:</strong> {solution.score}/100
            </div>
            <div>
              <strong>Tests Passed:</strong> {solution.test_cases_passed}
            </div>
            <div>
              <strong>Views:</strong> {solution.view_count}
            </div>
          </div>

          {solution.execution_time_ms && (
            <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-600">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <strong>Execution Time:</strong> {solution.execution_time_ms}ms
                </div>
                {solution.memory_used_mb && (
                  <div>
                    <strong>Memory:</strong> {solution.memory_used_mb.toFixed(2)} MB
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Main content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Code section - takes up 2 columns */}
          <div className="lg:col-span-2">
            {/* Code block */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
              <div className="bg-gray-900 p-4">
                <h2 className="text-white font-mono text-sm">
                  Solution ({solution.language})
                </h2>
              </div>
              <pre className="bg-gray-50 p-6 overflow-x-auto text-sm">
                <code className="font-mono text-gray-900">{solution.code}</code>
              </pre>
            </div>

            {/* Explanation */}
            {solution.explanation && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Explanation</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{solution.explanation}</p>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Complexity */}
            {solution.complexity_explanation && (
              <div className="bg-white rounded-lg shadow-md p-4">
                <h3 className="font-bold text-gray-900 mb-2">Complexity Analysis</h3>
                <p className="text-gray-700 text-sm">{solution.complexity_explanation}</p>
              </div>
            )}

            {/* Tags */}
            {solution.approach_tags && solution.approach_tags.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-4">
                <h3 className="font-bold text-gray-900 mb-3">Approach Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {solution.approach_tags.map((tag, i) => (
                    <span
                      key={i}
                      className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Difficulty assessment */}
            {solution.difficulty_for_user && (
              <div className="bg-white rounded-lg shadow-md p-4">
                <h3 className="font-bold text-gray-900 mb-2">Difficulty Level</h3>
                <p className="text-gray-700 text-sm capitalize">{solution.difficulty_for_user}</p>
              </div>
            )}

            {/* Voting */}
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="font-bold text-gray-900 mb-4">Rate This Solution</h3>
              <div className="space-y-2">
                <button
                  onClick={() => handleVote('helpful')}
                  className={`w-full flex items-center justify-between px-4 py-2 rounded border transition-colors ${
                    userVote === 'helpful'
                      ? 'bg-green-50 border-green-200 text-green-700'
                      : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-green-50'
                  }`}
                >
                  <span>👍 Helpful</span>
                  <span className="font-bold">{solution.helpful_votes}</span>
                </button>
                <button
                  onClick={() => handleVote('unhelpful')}
                  className={`w-full flex items-center justify-between px-4 py-2 rounded border transition-colors ${
                    userVote === 'unhelpful'
                      ? 'bg-red-50 border-red-200 text-red-700'
                      : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-red-50'
                  }`}
                >
                  <span>👎 Not Helpful</span>
                  <span className="font-bold">{solution.unhelpful_votes}</span>
                </button>
              </div>
            </div>

            {/* Helpful tips */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
              <p className="font-medium mb-2">💡 Tips:</p>
              <ul className="space-y-1 text-xs">
                <li>• Vote to help others find useful solutions</li>
                <li>• Bookmark to save for later reference</li>
                <li>• Compare with other approaches</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

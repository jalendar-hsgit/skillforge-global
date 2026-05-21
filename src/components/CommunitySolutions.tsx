/**
 * Community Solutions Component
 * Display community-shared solutions with voting and filtering
 */

'use client';

import React, { useState, useEffect } from 'react';
import solutionAPI, { SolutionSummary } from '@/lib/solutions';

interface CommunitySolutionsProps {
  challengeId: number;
}

export default function CommunitySolutions({ challengeId }: CommunitySolutionsProps) {
  const [solutions, setSolutions] = useState<SolutionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'votes' | 'recent' | 'helpful'>('votes');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('');
  const [expandedSolutionId, setExpandedSolutionId] = useState<number | null>(null);

  useEffect(() => {
    loadSolutions();
  }, [challengeId, sortBy, selectedLanguage]);

  const loadSolutions = async () => {
    try {
      setLoading(true);
      const response = await solutionAPI.getChallengeSolutions(
        challengeId,
        sortBy,
        selectedLanguage || undefined,
        20,
        0
      );
      setSolutions(response.solutions);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load solutions');
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (solutionId: number, voteType: 'helpful' | 'unhelpful') => {
    try {
      await solutionAPI.voteSolution(solutionId, voteType);
      // Reload solutions to get updated vote counts
      loadSolutions();
    } catch (err) {
      console.error('Failed to vote:', err);
    }
  };

  const handleBookmark = async (solutionId: number) => {
    try {
      await solutionAPI.bookmarkSolution(solutionId);
      alert('Solution bookmarked!');
    } catch (err) {
      console.error('Failed to bookmark:', err);
    }
  };

  const languages = [...new Set(solutions.map(s => s.language))];

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Community Solutions</h2>
        <span className="text-sm text-gray-600">{solutions.length} solutions</span>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6 flex-wrap">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Sort by:</label>
          <select
            value={sortBy}
            onChange={e => setSortBy(e.target.value as 'votes' | 'recent' | 'helpful')}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="votes">Most Helpful</option>
            <option value="recent">Most Recent</option>
            <option value="helpful">Most Upvotes</option>
          </select>
        </div>

        {languages.length > 0 && (
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Language:</label>
            <select
              value={selectedLanguage}
              onChange={e => setSelectedLanguage(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="">All Languages</option>
              {languages.map(lang => (
                <option key={lang} value={lang}>
                  {lang}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 text-red-800">
          {error}
        </div>
      ) : solutions.length === 0 ? (
        <div className="text-center py-8 text-gray-600">
          <p className="mb-2">No community solutions shared yet.</p>
          <p className="text-sm">Be the first to share your solution!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {solutions.map(solution => (
            <div
              key={solution.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                      {solution.language}
                    </span>
                    <span className="text-sm text-gray-600">
                      by <strong>{solution.user.username}</strong>
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
                    Score: {solution.score}/100 • {solution.test_cases_passed} test cases passed
                  </p>
                </div>
                <button
                  onClick={() => handleBookmark(solution.id)}
                  className="text-gray-400 hover:text-yellow-500 transition-colors"
                  title="Bookmark solution"
                >
                  ⭐
                </button>
              </div>

              {/* Solution metadata */}
              {solution.complexity_explanation && (
                <p className="text-sm text-gray-700 mb-3">
                  <strong>Complexity:</strong> {solution.complexity_explanation}
                </p>
              )}

              {solution.approach_tags && solution.approach_tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {solution.approach_tags.map((tag, i) => (
                    <span
                      key={i}
                      className="inline-block px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Voting buttons */}
              <div className="flex items-center gap-4 pt-3 border-t border-gray-200">
                <button
                  onClick={() => handleVote(solution.id, 'helpful')}
                  className="flex items-center gap-2 text-sm text-green-600 hover:bg-green-50 px-3 py-1 rounded transition-colors"
                >
                  👍 {solution.helpful_votes > 0 && solution.helpful_votes}
                </button>
                <button
                  onClick={() => handleVote(solution.id, 'unhelpful')}
                  className="flex items-center gap-2 text-sm text-red-600 hover:bg-red-50 px-3 py-1 rounded transition-colors"
                >
                  👎 {solution.unhelpful_votes > 0 && solution.unhelpful_votes}
                </button>
                <button
                  onClick={() =>
                    setExpandedSolutionId(expandedSolutionId === solution.id ? null : solution.id)
                  }
                  className="flex items-center gap-2 text-sm text-blue-600 hover:bg-blue-50 px-3 py-1 rounded transition-colors ml-auto"
                >
                  {expandedSolutionId === solution.id ? '▼' : '▶'} View Code
                </button>
                <span className="text-xs text-gray-500">{solution.view_count} views</span>
              </div>

              {/* Expanded code view */}
              {expandedSolutionId === solution.id && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <a
                    href={`/practice/solutions/${solution.id}`}
                    className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  >
                    View Full Solution →
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

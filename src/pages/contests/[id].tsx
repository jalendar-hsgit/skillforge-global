import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { useMe } from '@/hooks/useMe';
import { Trophy, Users, Clock, CheckCircle, TrendingUp } from 'lucide-react';

interface ContestDetail {
  id: number;
  title: string;
  description: string;
  rules: string;
  category: string;
  difficulty: string;
  contest_type: string;
  status: string;
  start_time: string;
  end_time: string;
  registration_deadline: string;
  total_participants: number;
  total_prize_pool: number;
  banner_image: string | null;
  is_participant: boolean;
  participant_rank: number | null;
  participant_score: number;
}

interface LeaderboardEntry {
  user_id: number;
  rank: number;
  score: number;
  challenges_solved: number;
  accuracy: number;
  last_accepted_time: string | null;
}

interface Submission {
  id: number;
  challenge_id: number;
  status: string;
  test_cases_passed: number;
  test_cases_total: number;
  points_earned: number;
  submitted_at: string;
}

const ContestDetailPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const { me: user } = useMe();

  const [contest, setContest] = useState<ContestDetail | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [joining, setJoining] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'leaderboard' | 'submissions'>('overview');

  // Fetch contest details
  useEffect(() => {
    if (!id) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');

        const [contestRes, leaderboardRes] = await Promise.all([
          apiCall(`/api/v1x/contests/${id}`, { method: 'GET' }),
          apiCall(`/api/v1x/contests/${id}/leaderboard`, { method: 'GET' }),
        ]);

        setContest(contestRes);
        setLeaderboard(leaderboardRes || []);

        // Fetch submissions if participant
        if (contestRes?.is_participant) {
          const submissionsRes = await apiCall(`/api/v1x/contests/${id}/submissions`, { method: 'GET' });
          setSubmissions(submissionsRes || []);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load contest');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleJoinContest = async () => {
    try {
      setJoining(true);
      setError('');

      await apiCall(`/api/v1x/contests/${id}/join`, {
        method: 'POST',
      });

      // Refresh contest data
      const updatedContest = await apiCall(`/api/v1x/contests/${id}`, { method: 'GET' });
      setContest(updatedContest);
    } catch (err: any) {
      setError(err.message || 'Failed to join contest');
    } finally {
      setJoining(false);
    }
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'hard':
        return 'text-red-600';
      case 'expert':
        return 'text-purple-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'upcoming':
        return 'bg-blue-100 text-blue-800';
      case 'finished':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="max-w-6xl mx-auto py-12 text-center">Loading contest...</div>
      </Layout>
    );
  }

  if (!contest) {
    return (
      <Layout>
        <div className="max-w-6xl mx-auto py-12 text-center text-red-600">
          Contest not found
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto py-12">
        {/* Banner */}
        {contest.banner_image && (
          <div className="mb-6 -mx-6">
            <img
              src={contest.banner_image}
              alt={contest.title}
              className="w-full h-64 object-cover rounded-t-lg"
            />
          </div>
        )}

        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-4xl font-bold mb-2">{contest.title}</h1>
            <div className="flex gap-2 flex-wrap">
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(contest.status)}`}>
                {contest.status.charAt(0).toUpperCase() + contest.status.slice(1)}
              </span>
              <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-semibold">
                {contest.category}
              </span>
              <span className={`px-3 py-1 bg-gray-100 rounded-full text-sm font-semibold ${getDifficultyColor(contest.difficulty)}`}>
                {contest.difficulty.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Action Button */}
          {!contest.is_participant ? (
            <Button
              onClick={handleJoinContest}
              disabled={joining || contest.status === 'finished'}
              className="bg-blue-600 text-white px-6"
            >
              {joining ? 'Joining...' : 'Join Contest'}
            </Button>
          ) : (
            <div className="text-center">
              <p className="text-gray-600 mb-2">Your Rank</p>
              <p className="text-4xl font-bold text-blue-600">
                {contest.participant_rank || 'N/A'}
              </p>
              <p className="text-sm text-gray-600 mt-2">{contest.participant_score} points</p>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Key Info */}
        <Card className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <p className="text-gray-600 text-sm mb-1">Starts At</p>
              <p className="font-semibold">{formatDate(contest.start_time)}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm mb-1">Ends At</p>
              <p className="font-semibold">{formatDate(contest.end_time)}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm mb-1">Registration Deadline</p>
              <p className="font-semibold">{formatDate(contest.registration_deadline)}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm mb-1">Prize Pool</p>
              <p className="font-bold text-green-600 text-lg">💰 {contest.total_prize_pool.toLocaleString()}</p>
            </div>
          </div>
        </Card>

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <div className="flex gap-8">
            {(['overview', 'leaderboard', 'submissions'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-3 px-2 font-semibold border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab === 'overview' && '📋 Overview'}
                {tab === 'leaderboard' && '🏆 Leaderboard'}
                {tab === 'submissions' && '📤 My Submissions'}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <Card>
            <div className="prose max-w-none">
              <h2 className="text-2xl font-bold mb-4">About This Contest</h2>
              <p className="text-gray-700 whitespace-pre-wrap mb-6">{contest.description}</p>

              {contest.rules && (
                <>
                  <h3 className="text-xl font-bold mb-3">Rules</h3>
                  <p className="text-gray-700 whitespace-pre-wrap mb-6">{contest.rules}</p>
                </>
              )}

              <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                <div>
                  <p className="text-sm text-gray-600">Type</p>
                  <p className="font-semibold">{contest.contest_type}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Participants</p>
                  <p className="font-semibold text-blue-600">{contest.total_participants}</p>
                </div>
              </div>
            </div>
          </Card>
        )}

        {activeTab === 'leaderboard' && (
          <Card>
            <h2 className="text-2xl font-bold mb-6">🏆 Live Leaderboard</h2>

            {leaderboard.length === 0 ? (
              <p className="text-gray-600 text-center py-8">No submissions yet</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold">Rank</th>
                      <th className="px-4 py-3 text-left font-semibold">Score</th>
                      <th className="px-4 py-3 text-left font-semibold">Solved</th>
                      <th className="px-4 py-3 text-left font-semibold">Accuracy</th>
                      <th className="px-4 py-3 text-left font-semibold">Last Submit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboard.map((entry) => (
                      <tr
                        key={entry.user_id}
                        className={`border-b border-gray-200 ${
                          contest.is_participant && entry.user_id === user?.id
                            ? 'bg-blue-50'
                            : ''
                        }`}
                      >
                        <td className="px-4 py-3">
                          <span className="font-bold text-lg">
                            {entry.rank === 1 && '🥇'}
                            {entry.rank === 2 && '🥈'}
                            {entry.rank === 3 && '🥉'}
                            {entry.rank > 3 && `#${entry.rank}`}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="font-bold text-blue-600">{entry.score}</span>
                        </td>
                        <td className="px-4 py-3">{entry.challenges_solved}</td>
                        <td className="px-4 py-3">
                          <span className="text-green-600 font-semibold">
                            {entry.accuracy.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {entry.last_accepted_time
                            ? formatDate(entry.last_accepted_time)
                            : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        )}

        {activeTab === 'submissions' && (
          <Card>
            <h2 className="text-2xl font-bold mb-6">📤 My Submissions</h2>

            {!contest.is_participant ? (
              <p className="text-gray-600 text-center py-8">Join the contest to view submissions</p>
            ) : submissions.length === 0 ? (
              <p className="text-gray-600 text-center py-8">No submissions yet</p>
            ) : (
              <div className="space-y-4">
                {submissions.map((submission) => (
                  <div
                    key={submission.id}
                    className={`p-4 border rounded-lg ${
                      submission.status === 'passed'
                        ? 'border-green-200 bg-green-50'
                        : submission.status === 'failed'
                        ? 'border-red-200 bg-red-50'
                        : 'border-gray-200'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-semibold">Challenge #{submission.challenge_id}</p>
                        <p className="text-sm text-gray-600">
                          {formatDate(submission.submitted_at)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className={`font-bold text-lg ${
                          submission.status === 'passed'
                            ? 'text-green-600'
                            : submission.status === 'failed'
                            ? 'text-red-600'
                            : 'text-gray-600'
                        }`}>
                          {submission.status.toUpperCase()}
                        </p>
                        <p className="text-2xl font-bold text-blue-600">+{submission.points_earned}</p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600">
                      {submission.test_cases_passed}/{submission.test_cases_total} test cases passed
                    </p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default ContestDetailPage;

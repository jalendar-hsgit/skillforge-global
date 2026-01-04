export const dynamic = 'force-dynamic'

import { useRouter } from 'next/router'
import Head from 'next/head'
import { useState, useEffect } from 'react'
import QuizTimingBreakdown from '@/components/quiz/QuizTimingBreakdown'
import { PageLayout } from '@/components/PageLayout'
import { newFeaturesAPI } from '@/lib/newFeaturesAPI'

interface QuizResultsState {
  score?: number
  totalQuestions?: number
  correctAnswers?: number
  timeSpent?: number
  passedScore?: number
}

export default function QuizResultsPage() {
  const router = useRouter()
  const { id, attemptId } = router.query
  const [results, setResults] = useState<QuizResultsState>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'summary' | 'timing'>('summary')

  useEffect(() => {
    if (!id || !attemptId) return

    const loadResults = async () => {
      try {
        setLoading(true)
        setError(null)

        // Try to fetch from session/quiz endpoint
        const response = await fetch(
          `/api/session/quiz/${id}/attempt/${attemptId}`,
          { credentials: 'include' }
        )

        if (!response.ok) {
          throw new Error('Failed to load quiz results')
        }

        const data = await response.json()
        setResults({
          score: data.score,
          totalQuestions: data.totalQuestions,
          correctAnswers: data.correctAnswers,
          timeSpent: data.timeSpent,
          passedScore: data.passedScore,
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error loading results')
      } finally {
        setLoading(false)
      }
    }

    loadResults()
  }, [id, attemptId])

  if (!router.isReady) {
    return (
      <PageLayout>
        <div className="flex justify-center items-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading quiz results...</p>
          </div>
        </div>
      </PageLayout>
    )
  }

  if (!id || !attemptId) {
    return (
      <PageLayout>
        <div className="max-w-2xl mx-auto px-4 py-12">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h1 className="text-2xl font-bold text-red-600 mb-2">❌ Invalid Results</h1>
            <p className="text-red-700">Could not load quiz results. Please try again.</p>
          </div>
        </div>
      </PageLayout>
    )
  }

  const score = results.score || 0
  const passed = score >= (results.passedScore || 70)
  const percentage = results.totalQuestions
    ? Math.round((results.correctAnswers || 0) / results.totalQuestions * 100)
    : 0

  return (
    <>
      <Head>
        <title>Quiz Results - SkillForge Global</title>
        <meta name="description" content="View your quiz results and detailed performance analysis" />
      </Head>

      <PageLayout>
        <div className="max-w-4xl mx-auto px-4 py-8">
          {/* Results Card */}
          <div className={`rounded-lg shadow-lg p-8 mb-8 ${
            passed ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200' : 'bg-gradient-to-br from-red-50 to-rose-50 border-2 border-red-200'
          }`}>
            <div className="text-center mb-6">
              <div className="text-6xl font-bold mb-4">
                {passed ? '🎉' : '📝'}
              </div>
              <h1 className={`text-4xl font-bold mb-2 ${passed ? 'text-green-600' : 'text-red-600'}`}>
                {passed ? 'Great Job!' : 'Quiz Completed'}
              </h1>
              <p className="text-lg text-gray-700">
                {passed ? 'You passed the quiz!' : 'Review your performance below'}
              </p>
            </div>

            {/* Score Display */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Score</p>
                <p className="text-3xl font-bold text-blue-600">{score}%</p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Correct Answers</p>
                <p className="text-3xl font-bold text-green-600">
                  {results.correctAnswers || 0}/{results.totalQuestions || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Percentage</p>
                <p className="text-3xl font-bold text-purple-600">{percentage}%</p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Time Spent</p>
                <p className="text-3xl font-bold text-orange-600">
                  {results.timeSpent ? `${Math.round(results.timeSpent / 60)}m` : '--'}
                </p>
              </div>
            </div>

            {/* Pass/Fail Status */}
            <div className="mt-6 flex justify-center">
              <span className={`px-6 py-2 rounded-full font-semibold text-white ${
                passed ? 'bg-green-600' : 'bg-red-600'
              }`}>
                {passed ? '✓ PASSED' : '✗ FAILED'}
              </span>
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="border-b border-gray-200 bg-gray-50 px-6 flex">
              <button
                onClick={() => setActiveTab('summary')}
                className={`py-4 px-6 font-semibold border-b-2 transition ${
                  activeTab === 'summary'
                    ? 'text-blue-600 border-blue-600'
                    : 'text-gray-600 border-transparent hover:text-gray-900'
                }`}
              >
                📊 Summary
              </button>
              <button
                onClick={() => setActiveTab('timing')}
                className={`py-4 px-6 font-semibold border-b-2 transition ${
                  activeTab === 'timing'
                    ? 'text-blue-600 border-blue-600'
                    : 'text-gray-600 border-transparent hover:text-gray-900'
                }`}
              >
                ⏱️ Timing Analysis
              </button>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {activeTab === 'summary' && (
                <div>
                  <h2 className="text-2xl font-bold mb-6 text-gray-900">Performance Summary</h2>

                  {/* Performance Insights */}
                  <div className="space-y-4 mb-8">
                    <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                      <h3 className="font-semibold text-blue-900 mb-2">💡 Your Performance</h3>
                      <ul className="text-blue-800 space-y-1 text-sm">
                        <li>• You answered {results.correctAnswers} out of {results.totalQuestions} questions correctly</li>
                        <li>• Your accuracy rate was {percentage}%</li>
                        <li>• Passing score required: {results.passedScore || 70}%</li>
                      </ul>
                    </div>

                    {!passed && (
                      <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
                        <h3 className="font-semibold text-yellow-900 mb-2">📚 How to Improve</h3>
                        <ul className="text-yellow-800 space-y-1 text-sm">
                          <li>• Review the topics covered in this quiz</li>
                          <li>• Practice with similar questions</li>
                          <li>• Take the quiz again to improve your score</li>
                          <li>• Check your timing analysis below</li>
                        </ul>
                      </div>
                    )}

                    {passed && (
                      <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                        <h3 className="font-semibold text-green-900 mb-2">🏆 Next Steps</h3>
                        <ul className="text-green-800 space-y-1 text-sm">
                          <li>• 🎖️ Achievement unlocked! Check your profile</li>
                          <li>• 💰 Coins earned: <span className="font-bold">+50 coins</span></li>
                          <li>• Try more challenging quizzes</li>
                          <li>• Share your achievement with friends</li>
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-4 pt-6 border-t">
                    <button
                      onClick={() => router.push('/quizzes')}
                      className="flex-1 px-4 py-3 bg-gray-100 text-gray-900 rounded-lg font-semibold hover:bg-gray-200 transition"
                    >
                      Back to Quizzes
                    </button>
                    <button
                      onClick={() => router.reload()}
                      className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                    >
                      Retake Quiz
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'timing' && (
                <div>
                  <h2 className="text-2xl font-bold mb-6 text-gray-900">⏱️ Timing Analysis</h2>
                  {attemptId && (
                    <QuizTimingBreakdown
                      attemptId={parseInt(attemptId as string)}
                      quizId={parseInt(id as string)}
                    />
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Share Section */}
          <div className="mt-8 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 Share Your Result</h3>
            <div className="flex gap-3 flex-wrap">
              <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                📸 Share on Social
              </button>
              <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                🔗 Copy Link
              </button>
              <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                👥 Challenge Friends
              </button>
            </div>
          </div>
        </div>
      </PageLayout>
    </>
  )
}

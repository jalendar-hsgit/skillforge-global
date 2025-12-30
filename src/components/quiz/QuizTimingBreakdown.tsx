/**
 * Quiz Timing Breakdown - Shows detailed timing stats for quiz attempts
 * Displays per-question time, average time, and comparison
 */
import { useEffect, useState } from 'react'
import { Card } from '@/components/Card'
import { quizAPI } from '@/lib/newFeaturesAPI'

interface QuizAttemptTiming {
  id: number
  quiz_id: number
  score: number
  time_spent_seconds: number
  question_times?: Record<string, number>
  completed_at: string
}

interface TimingStats {
  totalTime: number
  averageTimePerQuestion: number
  minTime: number
  maxTime: number
  questionCount: number
  questionBreakdown: Array<{
    questionId: string
    timeSpent: number
    position: number
  }>
}

export default function QuizTimingBreakdown({ attemptId }: { attemptId: number }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [attempt, setAttempt] = useState<QuizAttemptTiming | null>(null)
  const [stats, setStats] = useState<TimingStats | null>(null)

  useEffect(() => {
    let mounted = true

    const fetchAttemptDetails = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await quizAPI.getAttemptDetails(attemptId)
        
        if (mounted) {
          setAttempt(data)

          // Calculate stats
          const times = Object.values(data.question_times || {})
          const totalTime = data.time_spent_seconds || 0
          const questionCount = times.length || 1
          const avgTime = Math.round(totalTime / questionCount)

          const breakdown = Object.entries(data.question_times || {}).map(
            ([qId, time], idx) => ({
              questionId: qId,
              timeSpent: time as number,
              position: idx + 1,
            })
          )

          setStats({
            totalTime,
            averageTimePerQuestion: avgTime,
            minTime: Math.min(...times, 0),
            maxTime: Math.max(...times, 0),
            questionCount,
            questionBreakdown: breakdown,
          })
        }
      } catch (err: any) {
        if (mounted) setError(err.message || 'Failed to load timing details')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    fetchAttemptDetails()
    return () => {
      mounted = false
    }
  }, [attemptId])

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center gap-2 text-gray-600">
          <span className="animate-spin">⏳</span>
          <span>Loading timing details...</span>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="p-6 border-red-200 bg-red-50">
        <p className="text-sm text-red-600">{error}</p>
      </Card>
    )
  }

  if (!attempt || !stats) {
    return null
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  const getTimeColor = (time: number, avg: number) => {
    if (time < avg) return 'text-green-600'
    if (time > avg * 1.5) return 'text-red-600'
    return 'text-yellow-600'
  }

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <Card className="p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Timing Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-xs text-gray-600 font-medium">Total Time</p>
            <p className="text-xl font-bold text-blue-600 mt-1">
              {formatTime(stats.totalTime)}
            </p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <p className="text-xs text-gray-600 font-medium">Questions</p>
            <p className="text-xl font-bold text-purple-600 mt-1">
              {stats.questionCount}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-xs text-gray-600 font-medium">Avg/Question</p>
            <p className="text-xl font-bold text-green-600 mt-1">
              {formatTime(stats.averageTimePerQuestion)}
            </p>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <p className="text-xs text-gray-600 font-medium">Quickest</p>
            <p className="text-xl font-bold text-orange-600 mt-1">
              {formatTime(stats.minTime)}
            </p>
          </div>
        </div>
      </Card>

      {/* Per-Question Breakdown */}
      <Card className="p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Per-Question Time</h3>
        <div className="space-y-2">
          {stats.questionBreakdown.map((q) => {
            const barWidth = (q.timeSpent / stats.maxTime) * 100
            const timeColor = getTimeColor(q.timeSpent, stats.averageTimePerQuestion)
            return (
              <div key={q.questionId} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-700">Question {q.position}</span>
                  <span className={`font-semibold ${timeColor}`}>
                    {formatTime(q.timeSpent)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      q.timeSpent < stats.averageTimePerQuestion
                        ? 'bg-green-500'
                        : q.timeSpent > stats.averageTimePerQuestion * 1.5
                        ? 'bg-red-500'
                        : 'bg-yellow-500'
                    }`}
                    style={{ width: `${barWidth}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Score and Meta */}
      <Card className="p-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600 font-medium">Score</p>
            <p className="text-2xl font-bold text-blue-600 mt-1">{attempt.score}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 font-medium">Completed</p>
            <p className="text-sm text-gray-700 mt-1">
              {new Date(attempt.completed_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}

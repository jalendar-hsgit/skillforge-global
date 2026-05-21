import { useState, useEffect } from 'react'
import { newFeaturesAPI } from '@/lib/newFeaturesAPI'

// Types
interface LeaderboardData {
  [key: string]: Array<{
    rank: number
    userId: string
    userName: string
    coins?: number
    achievements?: number
    score?: number
  }>
}

interface QuizTimingData {
  attemptId: number
  quizId: number
  totalTime: number
  questions: Array<{
    questionId: number
    text: string
    timeSpent: number
    averageTime: number
  }>
}

interface AdminMetricsData {
  totalUsers: number
  activeUsers: number
  totalCourses: number
  activeCourses: number
  revenue: number
  engagement: number
  userGrowth: number
  courseGrowth: number
}

// ============ useLeaderboard Hook ============
export const useLeaderboard = (
  categoryFilter?: string,
  friendsOnly?: boolean,
  limit: number = 50
) => {
  const [leaderboards, setLeaderboards] = useState<LeaderboardData>({})
  const [activeTab, setActiveTab] = useState<string>('global_coins')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState({ limit, offset: 0 })

  useEffect(() => {
    const fetchLeaderboards = async () => {
      try {
        setLoading(true)
        setError(null)

        const data = await newFeaturesAPI.getAllLeaderboards()

        // Filter by category if provided
        const filtered = categoryFilter
          ? Object.fromEntries(
              Object.entries(data).filter(([key]) =>
                key.includes(categoryFilter)
              )
            )
          : data

        // Filter by friends if needed (this would need user's friends list)
        if (friendsOnly) {
          // TODO: Implement friends filtering
          console.log('Friends filtering not yet implemented')
        }

        setLeaderboards(filtered)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load leaderboards')
      } finally {
        setLoading(false)
      }
    }

    fetchLeaderboards()
  }, [categoryFilter, friendsOnly])

  return {
    leaderboards,
    activeTab,
    setActiveTab,
    loading,
    error,
    pagination,
    setPagination,
  }
}

// ============ useQuizTiming Hook ============
export const useQuizTiming = (attemptId: number, quizId?: number) => {
  const [timingData, setTimingData] = useState<QuizTimingData | null>(null)
  const [questions, setQuestions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState({
    totalTime: 0,
    averagePerQuestion: 0,
    fastest: 0,
    slowest: 0,
  })

  useEffect(() => {
    const fetchTimingData = async () => {
      try {
        setLoading(true)
        setError(null)

        const data = await newFeaturesAPI.getQuizTimingAnalytics(attemptId)

        setTimingData(data)
        setQuestions(data.questions || [])

        // Calculate stats
        if (data.questions && data.questions.length > 0) {
          const times: number[] = data.questions.map((q: { timeSpent?: number }) => q.timeSpent || 0)
          setStats({
            totalTime: times.reduce((a: number, b: number) => a + b, 0),
            averagePerQuestion: times.reduce((a: number, b: number) => a + b, 0) / times.length,
            fastest: Math.min(...times),
            slowest: Math.max(...times),
          })
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load timing data')
      } finally {
        setLoading(false)
      }
    }

    if (attemptId) {
      fetchTimingData()
    }
  }, [attemptId, quizId])

  return {
    timingData,
    questions,
    loading,
    error,
    stats,
  }
}

// ============ useAdminMetrics Hook ============
export const useAdminMetrics = (userRole: string, period: number = 30) => {
  const [metrics, setMetrics] = useState<AdminMetricsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [growth, setGrowth] = useState<any>(null)
  const [health, setHealth] = useState<any>(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true)
        setError(null)

        // Check admin role
        if (userRole !== 'admin' && userRole !== 'superadmin') {
          throw new Error('Unauthorized: Admin access required')
        }

        // Fetch all metrics in parallel
        const [metricsData, growthData, healthData] = await Promise.all([
          newFeaturesAPI.getAdminMetrics(period),
          newFeaturesAPI.getUserGrowth(period),
          newFeaturesAPI.getSystemHealth(),
        ])

        setMetrics(metricsData)
        setGrowth(growthData)
        setHealth(healthData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load metrics')
      } finally {
        setLoading(false)
      }
    }

    if (userRole) {
      fetchMetrics()
    }
  }, [userRole, period])

  const refetch = async () => {
    setLoading(true)
    try {
      const [metricsData, growthData, healthData] = await Promise.all([
        newFeaturesAPI.getAdminMetrics(period),
        newFeaturesAPI.getUserGrowth(period),
        newFeaturesAPI.getSystemHealth(),
      ])

      setMetrics(metricsData)
      setGrowth(growthData)
      setHealth(healthData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh metrics')
    } finally {
      setLoading(false)
    }
  }

  return {
    metrics,
    growth,
    health,
    loading,
    error,
    refetch,
  }
}

// ============ useQuizHistory Hook ============
export const useQuizHistory = (limit: number = 20) => {
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState({ limit, offset: 0 })

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true)
        setError(null)

        const data = await newFeaturesAPI.getQuizHistory(pagination.limit, pagination.offset)
        setHistory(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load quiz history')
      } finally {
        setLoading(false)
      }
    }

    fetchHistory()
  }, [pagination])

  const nextPage = () => {
    setPagination(prev => ({
      ...prev,
      offset: prev.offset + prev.limit,
    }))
  }

  const prevPage = () => {
    setPagination(prev => ({
      ...prev,
      offset: Math.max(0, prev.offset - prev.limit),
    }))
  }

  return {
    history,
    loading,
    error,
    pagination,
    nextPage,
    prevPage,
  }
}

// ============ useATSScoring Hook ============
export const useATSScoring = (resumeId: number) => {
  const [scoreHistory, setScoreHistory] = useState<any[]>([])
  const [improvements, setImprovements] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchATSData = async () => {
      try {
        setLoading(true)
        setError(null)

        const [history, improvementList] = await Promise.all([
          newFeaturesAPI.getATSScoreHistory(resumeId),
          newFeaturesAPI.getATSImprovements(resumeId),
        ])

        setScoreHistory(history)
        setImprovements(improvementList)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load ATS data')
      } finally {
        setLoading(false)
      }
    }

    if (resumeId) {
      fetchATSData()
    }
  }, [resumeId])

  return {
    scoreHistory,
    improvements,
    loading,
    error,
  }
}

// ============ useUserRank Hook ============
export const useUserRank = (userId?: string) => {
  const [rank, setRank] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchRank = async () => {
      try {
        setLoading(true)
        setError(null)

        if (userId) {
          const data = await newFeaturesAPI.getUserRank(userId)
          setRank(data)
        } else {
          const data = await newFeaturesAPI.getMyRank()
          setRank(data)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load rank')
      } finally {
        setLoading(false)
      }
    }

    fetchRank()
  }, [userId])

  return {
    rank,
    loading,
    error,
  }
}

// ============ useResumeComparison Hook ============
export const useResumeComparison = (resumeIds: number[]) => {
  const [comparison, setComparison] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        setLoading(true)
        setError(null)

        if (resumeIds.length > 0) {
          const data = await newFeaturesAPI.compareResumes(resumeIds)
          setComparison(data)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to compare resumes')
      } finally {
        setLoading(false)
      }
    }

    if (resumeIds.length > 0) {
      fetchComparison()
    }
  }, [resumeIds.join(',')])

  return {
    comparison,
    loading,
    error,
  }
}

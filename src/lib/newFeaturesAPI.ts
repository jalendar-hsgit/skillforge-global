/**
 * API Service Layer for New Features
 * Handles calls to all 24 new endpoints
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

interface QuizAttemptTiming {
  attempt_id: number
  question_times: Record<string, number>
  answers: Record<string, string>
  total_time: number
}

interface ATSScoreRequest {
  resume_text?: string
  resume_id?: number
}

interface LeaderboardParams {
  limit?: number
  offset?: number
  period_days?: number
}

/**
 * QUIZ TIME TRACKING ENDPOINTS
 */
export const quizAPI = {
  // Submit quiz attempt with timing data
  submitAttemptWithTiming: async (data: QuizAttemptTiming) => {
    const res = await fetch(`${API_BASE}/api/v1x/quizzes-db/attempt-with-timing`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to submit quiz attempt')
    return res.json()
  },

  // Get detailed attempt with timing breakdown
  getAttemptDetails: async (attemptId: number) => {
    const res = await fetch(`${API_BASE}/api/v1x/quizzes-db/attempt/${attemptId}/details`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch attempt details')
    return res.json()
  },

  // Get user's quiz history with timing stats
  getUserHistory: async (limit: number = 20, offset: number = 0) => {
    const res = await fetch(
      `${API_BASE}/api/v1x/quizzes-db/user/history?limit=${limit}&offset=${offset}`,
      { credentials: 'include' }
    )
    if (!res.ok) throw new Error('Failed to fetch quiz history')
    return res.json()
  },

  // Get time analytics by quiz
  getTimeAnalytics: async () => {
    const res = await fetch(`${API_BASE}/api/v1x/quizzes-db/analytics/time-per-quiz`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch time analytics')
    return res.json()
  },
}

/**
 * RESUME ATS SCORING ENDPOINTS
 */
export const atsAPI = {
  // Score raw resume text
  scoreResume: async (resumeText: string) => {
    const res = await fetch(`${API_BASE}/api/v1x/resume-scoring/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ resume_text: resumeText }),
    })
    if (!res.ok) throw new Error('Failed to score resume')
    return res.json()
  },

  // Score existing resume from database
  scoreResumeById: async (resumeId: number) => {
    const res = await fetch(`${API_BASE}/api/v1x/resume-scoring/score-by-resume/${resumeId}`, {
      method: 'POST',
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to score resume')
    return res.json()
  },

  // Get user's scoring history
  getScoringHistory: async () => {
    const res = await fetch(`${API_BASE}/api/v1x/resume-scoring/score-history`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch scoring history')
    return res.json()
  },

  // Get improvement suggestions
  getImprovements: async (resumeId: number) => {
    const res = await fetch(`${API_BASE}/api/v1x/resume-scoring/improvements/${resumeId}`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch improvements')
    return res.json()
  },

  // Compare multiple resumes
  compareResumes: async (resumeIds: number[]) => {
    const res = await fetch(`${API_BASE}/api/v1x/resume-scoring/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ resume_ids: resumeIds }),
    })
    if (!res.ok) throw new Error('Failed to compare resumes')
    return res.json()
  },
}

/**
 * LEADERBOARD ENDPOINTS
 */
export const leaderboardAPI = {
  // Global coins leaderboard
  getGlobalCoins: async (params: LeaderboardParams = {}) => {
    const query = new URLSearchParams({
      limit: (params.limit || 100).toString(),
      offset: (params.offset || 0).toString(),
    })
    const res = await fetch(`${API_BASE}/api/v1x/leaderboard/global/coins?${query}`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch global coins leaderboard')
    return res.json()
  },

  // Global achievements leaderboard
  getGlobalAchievements: async (params: LeaderboardParams = {}) => {
    const query = new URLSearchParams({
      limit: (params.limit || 100).toString(),
      offset: (params.offset || 0).toString(),
    })
    const res = await fetch(
      `${API_BASE}/api/v1x/leaderboard/global/achievements?${query}`,
      { credentials: 'include' }
    )
    if (!res.ok) throw new Error('Failed to fetch achievements leaderboard')
    return res.json()
  },

  // Weekly coins leaderboard
  getWeeklyCoins: async (params: LeaderboardParams = {}) => {
    const query = new URLSearchParams({
      limit: (params.limit || 50).toString(),
      offset: (params.offset || 0).toString(),
    })
    const res = await fetch(`${API_BASE}/api/v1x/leaderboard/weekly/coins?${query}`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch weekly leaderboard')
    return res.json()
  },

  // Coding category leaderboard
  getCodingLeaderboard: async (params: LeaderboardParams = {}) => {
    const query = new URLSearchParams({
      limit: (params.limit || 100).toString(),
      offset: (params.offset || 0).toString(),
    })
    const res = await fetch(`${API_BASE}/api/v1x/leaderboard/category/coding?${query}`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch coding leaderboard')
    return res.json()
  },

  // Quiz category leaderboard
  getQuizzesLeaderboard: async (params: LeaderboardParams = {}) => {
    const query = new URLSearchParams({
      limit: (params.limit || 100).toString(),
      offset: (params.offset || 0).toString(),
    })
    const res = await fetch(`${API_BASE}/api/v1x/leaderboard/category/quizzes?${query}`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch quizzes leaderboard')
    return res.json()
  },

  // Friend rankings
  getFriendLeaderboard: async (params: LeaderboardParams = {}) => {
    const query = new URLSearchParams({
      limit: (params.limit || 50).toString(),
      offset: (params.offset || 0).toString(),
    })
    const res = await fetch(`${API_BASE}/api/v1x/leaderboard/friends?${query}`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch friend leaderboard')
    return res.json()
  },

  // Get specific user's rank
  getUserRank: async (userId: number) => {
    const res = await fetch(`${API_BASE}/api/v1x/leaderboard/user-rank/${userId}`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch user rank')
    return res.json()
  },

  // Get current user's rank
  getMyRank: async () => {
    const res = await fetch(`${API_BASE}/api/v1x/leaderboard/my-rank`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch my rank')
    return res.json()
  },
}

/**
 * ADMIN METRICS ENDPOINTS
 */
export const adminMetricsAPI = {
  // Dashboard summary with KPIs
  getDashboardSummary: async () => {
    const res = await fetch(`${API_BASE}/api/v1x/admin-metrics/dashboard-summary`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch dashboard summary')
    return res.json()
  },

  // User growth analytics
  getUserGrowth: async (periodDays: number = 30) => {
    const res = await fetch(
      `${API_BASE}/api/v1x/admin-metrics/user-growth?period_days=${periodDays}`,
      { credentials: 'include' }
    )
    if (!res.ok) throw new Error('Failed to fetch user growth data')
    return res.json()
  },

  // Course analytics
  getCourseAnalytics: async () => {
    const res = await fetch(`${API_BASE}/api/v1x/admin-metrics/course-analytics`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch course analytics')
    return res.json()
  },

  // Engagement metrics
  getEngagementMetrics: async () => {
    const res = await fetch(`${API_BASE}/api/v1x/admin-metrics/engagement-metrics`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch engagement metrics')
    return res.json()
  },

  // System health status
  getSystemHealth: async () => {
    const res = await fetch(`${API_BASE}/api/v1x/admin-metrics/system-health`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch system health')
    return res.json()
  },

  // Revenue metrics
  getRevenueMetrics: async () => {
    const res = await fetch(`${API_BASE}/api/v1x/admin-metrics/revenue-metrics`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch revenue metrics')
    return res.json()
  },

  // Admin logs/audit trail
  getAdminLogs: async (limit: number = 50, offset: number = 0) => {
    const res = await fetch(
      `${API_BASE}/api/v1x/admin-metrics/admin-logs?limit=${limit}&offset=${offset}`,
      { credentials: 'include' }
    )
    if (!res.ok) throw new Error('Failed to fetch admin logs')
    return res.json()
  },
}

// Export all APIs with nested namespaces
export const newFeaturesAPI = {
  quiz: quizAPI,
  ats: atsAPI,
  leaderboard: leaderboardAPI,
  admin: adminMetricsAPI,

  // Convenience methods for hooks (flat access)
  getAllLeaderboards: async () => {
    const [globalCoins, globalAchievements, weeklyCoins, coding, quizzes] = await Promise.all([
      leaderboardAPI.getGlobalCoins(),
      leaderboardAPI.getGlobalAchievements(),
      leaderboardAPI.getWeeklyCoins(),
      leaderboardAPI.getCodingLeaderboard(),
      leaderboardAPI.getQuizzesLeaderboard(),
    ])
    return {
      global_coins: globalCoins,
      global_achievements: globalAchievements,
      weekly_coins: weeklyCoins,
      coding: coding,
      quizzes: quizzes,
    }
  },

  getQuizTimingAnalytics: async (attemptId: number) => {
    return quizAPI.getAttemptDetails(attemptId)
  },

  getAdminMetrics: async (periodDays: number = 30) => {
    return adminMetricsAPI.getDashboardSummary()
  },

  getUserGrowth: async (periodDays: number = 30) => {
    return adminMetricsAPI.getUserGrowth(periodDays)
  },

  getSystemHealth: async () => {
    return adminMetricsAPI.getSystemHealth()
  },

  getQuizHistory: async (limit: number = 20, offset: number = 0) => {
    return quizAPI.getUserHistory(limit, offset)
  },

  getATSScoreHistory: async (resumeId: number) => {
    return atsAPI.getScoringHistory()
  },

  getATSImprovements: async (resumeId: number) => {
    return atsAPI.getImprovements(resumeId)
  },

  getUserRank: async (userId: string) => {
    return leaderboardAPI.getUserRank(parseInt(userId))
  },

  getMyRank: async () => {
    return leaderboardAPI.getMyRank()
  },

  compareResumes: async (resumeIds: number[]) => {
    return atsAPI.compareResumes(resumeIds)
  },
}

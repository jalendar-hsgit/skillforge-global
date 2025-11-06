// Hook for fetching dashboard analytics
import { useState, useEffect } from 'react';
import type { DashboardStats } from '@/components/DashboardAnalytics';

interface LearningPath {
  path: string;
  title: string;
  total_videos: number;
  completed_videos: number;
  percentage: number;
  last_watched?: string;
}

interface QuizAnalytics {
  total_quizzes: number;
  avg_score_percentage: number;
  performance_trend: Array<{ date: string; avg_score: number }>;
  topic_breakdown: Array<{ topic: string; count: number }>;
  difficulty_distribution: {
    easy: number;
    medium: number;
    hard: number;
  };
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
}

export function useDashboardStats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/dashboard/stats', {
      credentials: 'include',
    })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch dashboard stats');
        return res.json();
      })
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return { stats, loading, error };
}

export function useLearningPaths() {
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/dashboard/learning-paths', {
      credentials: 'include',
    })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch learning paths');
        return res.json();
      })
      .then((data) => {
        setPaths(data.paths || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return { paths, loading, error };
}

export function useQuizAnalytics(days: number = 30) {
  const [analytics, setAnalytics] = useState<QuizAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/dashboard/quiz-analytics?days=${days}`, {
      credentials: 'include',
    })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch quiz analytics');
        return res.json();
      })
      .then((data) => {
        setAnalytics(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [days]);

  return { analytics, loading, error };
}

export function useAchievements() {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/dashboard/achievements', {
      credentials: 'include',
    })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch achievements');
        return res.json();
      })
      .then((data) => {
        setAchievements(data.achievements || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return { achievements, loading, error };
}

/**
 * Solution Sharing API Client
 * Handles community solutions, voting, and bookmarking
 */

import { API_BASE } from './apiBase';

export interface ChallengeSubmission {
  code: string;
  language: string;
  explanation?: string;
  complexity_explanation?: string;
  approach_tags?: string[];
  difficulty_for_user?: string;
}

export interface SolutionSummary {
  id: number;
  challenge_id: number;
  user: {
    id: number;
    username: string;
  };
  language: string;
  score: number;
  test_cases_passed: number;
  helpful_votes: number;
  unhelpful_votes: number;
  view_count: number;
  complexity_explanation?: string;
  approach_tags?: string[];
  difficulty_for_user?: string;
  created_at: string;
}

export interface DetailedSolution extends SolutionSummary {
  code: string;
  explanation?: string;
  execution_time_ms?: number;
  memory_used_mb?: number;
  user_vote?: string; // "helpful" or "unhelpful" if user voted
}

export interface CommunitySolutionsResponse {
  total: number;
  solutions: SolutionSummary[];
}

export interface BookmarkSolution {
  id: number;
  challenge_id: number;
  language: string;
  score: number;
  helpful_votes: number;
  created_at: string;
  bookmarked_at: string;
}

export interface BookmarksResponse {
  total: number;
  bookmarks: BookmarkSolution[];
}

export interface UserSolutionsResponse {
  total: number;
  solutions: SolutionSummary[];
}

class SolutionAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_BASE}/api/v1x/solutions`;
  }

  /**
   * Share a solution to a challenge with the community
   */
  async shareSolution(
    challengeId: number,
    submission: ChallengeSubmission,
    token?: string
  ): Promise<any> {
    const params = new URLSearchParams();
    params.append('code', submission.code);
    params.append('language', submission.language);
    if (submission.explanation) params.append('explanation', submission.explanation);
    if (submission.complexity_explanation)
      params.append('complexity_explanation', submission.complexity_explanation);
    if (submission.approach_tags)
      params.append('approach_tags', JSON.stringify(submission.approach_tags));
    if (submission.difficulty_for_user)
      params.append('difficulty_for_user', submission.difficulty_for_user);

    const response = await fetch(`${this.baseURL}/challenges/${challengeId}/share`, {
      method: 'POST',
      body: params,
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Failed to share solution: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get community solutions for a challenge
   */
  async getChallengeSolutions(
    challengeId: number,
    sortBy: 'votes' | 'recent' | 'helpful' = 'votes',
    language?: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<CommunitySolutionsResponse> {
    const params = new URLSearchParams();
    params.append('sort_by', sortBy);
    if (language) params.append('language', language);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await fetch(
      `${this.baseURL}/challenges/${challengeId}/solutions?${params}`,
      {
        method: 'GET',
        credentials: 'include',
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch solutions: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get detailed solution with code
   */
  async getSolution(solutionId: number, token?: string): Promise<DetailedSolution> {
    const response = await fetch(`${this.baseURL}/solutions/${solutionId}`, {
      method: 'GET',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch solution: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Vote on a solution (helpful/unhelpful)
   */
  async voteSolution(
    solutionId: number,
    voteType: 'helpful' | 'unhelpful',
    token?: string
  ): Promise<any> {
    const params = new URLSearchParams();
    params.append('vote_type', voteType);

    const response = await fetch(`${this.baseURL}/solutions/${solutionId}/vote`, {
      method: 'POST',
      body: params,
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Failed to vote on solution: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Bookmark a solution for later reference
   */
  async bookmarkSolution(solutionId: number, token?: string): Promise<any> {
    const response = await fetch(`${this.baseURL}/solutions/${solutionId}/bookmark`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Failed to bookmark solution: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get all bookmarks for current user
   */
  async getBookmarks(limit: number = 20, offset: number = 0, token?: string): Promise<BookmarksResponse> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await fetch(`${this.baseURL}/bookmarks?${params}`, {
      method: 'GET',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch bookmarks: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get solutions shared by a specific user
   */
  async getUserSolutions(
    userId: number,
    limit: number = 20,
    offset: number = 0
  ): Promise<UserSolutionsResponse> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await fetch(`${this.baseURL}/users/${userId}/solutions?${params}`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch user solutions: ${response.statusText}`);
    }

    return response.json();
  }
}

export default new SolutionAPI();

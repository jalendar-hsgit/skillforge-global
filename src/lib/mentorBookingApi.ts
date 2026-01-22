/**
 * Mentor Booking API - Type-safe wrapper for mentor session operations
 * Integrates with backend /api/v1x/mentors endpoints
 */

import { apiGet, apiPost } from './api';

// ============ Types ============

export interface MentorProfile {
  id: number;
  user_id: number;
  email: string;
  bio: string;
  expertise: string; // comma-separated skills
  hourly_rate: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'SUSPENDED';
  total_sessions: number;
  average_rating: number;
  user: {
    full_name: string;
    email: string;
  };
  created_at: string;
}

export interface AvailabilitySlot {
  id: number;
  mentor_id: number;
  day_of_week: number; // 0=Monday, 6=Sunday
  date?: string; // YYYY-MM-DD for specific dates
  start_time: string; // HH:MM format
  end_time: string; // HH:MM format
  is_available: boolean;
  is_booked: boolean;
  timezone?: string;
}

export interface AvailabilityResponse {
  slots: AvailabilitySlot[];
}

export interface SessionBookingRequest {
  mentor_id: number;
  topic: string;
  description?: string;
  scheduled_at: string; // ISO 8601 datetime
  duration_minutes: number;
}

export interface MentorSession {
  id: number;
  mentor_id: number;
  student_id: number;
  topic: string;
  description?: string;
  scheduled_at: string;
  duration_minutes: number;
  status: 'PENDING' | 'CONFIRMED' | 'COMPLETED' | 'CANCELLED';
  meeting_url?: string;
  price: number;
  payment_status: 'pending' | 'completed' | 'failed';
  mentor_notes?: string;
  student_feedback?: string;
  created_at: string;
}

export interface SessionListResponse {
  sessions: MentorSession[];
  total: number;
}

export interface MentorListResponse {
  mentors: MentorProfile[];
}

// ============ API Functions ============

/**
 * Get all approved mentors
 */
export async function getMentors(limit: number = 50): Promise<MentorProfile[]> {
  try {
    const response = await apiGet(`/api/v1x/mentors?limit=${limit}`);
    return response.data || [];
  } catch (error) {
    console.error('Error fetching mentors:', error);
    return [];
  }
}

/**
 * Get a specific mentor's profile
 */
export async function getMentorProfile(mentorId: number): Promise<MentorProfile | null> {
  try {
    const response = await apiGet(`/api/v1x/mentors/${mentorId}`);
    return response.data || null;
  } catch (error) {
    console.error('Error fetching mentor profile:', error);
    return null;
  }
}

/**
 * Search for mentors by expertise and filters
 */
export async function searchMentors(
  expertise?: string,
  minRating?: number,
  maxRate?: number,
  limit: number = 50
): Promise<MentorProfile[]> {
  try {
    const params = new URLSearchParams();
    if (expertise) params.append('expertise', expertise);
    if (minRating !== undefined) params.append('min_rating', minRating.toString());
    if (maxRate !== undefined) params.append('max_rate', maxRate.toString());
    params.append('limit', limit.toString());

    const response = await apiGet(`/api/v1x/mentors/search?${params.toString()}`);
    return response.data || [];
  } catch (error) {
    console.error('Error searching mentors:', error);
    return [];
  }
}

/**
 * Get available slots for a mentor
 */
export async function getAvailableSlots(mentorId: number): Promise<AvailabilitySlot[]> {
  try {
    const response = await apiGet(`/api/v1x/mentors/availability/${mentorId}`);
    return response.data?.slots || [];
  } catch (error) {
    console.error('Error fetching availability slots:', error);
    return [];
  }
}

/**
 * Book a mentor session
 */
export async function bookSession(request: SessionBookingRequest): Promise<MentorSession> {
  try {
    const response = await apiPost('/api/v1x/mentors/sessions', request);
    if (!response.success) {
      throw new Error(response.message || 'Failed to book session');
    }
    return response.data;
  } catch (error) {
    console.error('Error booking session:', error);
    throw error;
  }
}

/**
 * Get current user's sessions (as student)
 */
export async function getMyBookings(): Promise<MentorSession[]> {
  try {
    const response = await apiGet('/api/v1x/mentors/sessions/my?as_mentor=false');
    return response.data?.sessions || [];
  } catch (error) {
    console.error('Error fetching bookings:', error);
    return [];
  }
}

/**
 * Get a specific session details
 */
export async function getSessionDetails(sessionId: number): Promise<MentorSession | null> {
  try {
    const response = await apiGet(`/api/v1x/mentors/sessions/${sessionId}`);
    return response.data || null;
  } catch (error) {
    console.error('Error fetching session details:', error);
    return null;
  }
}

/**
 * Update session status (e.g., cancel booking)
 */
export async function updateSessionStatus(
  sessionId: number,
  status: 'PENDING' | 'CONFIRMED' | 'COMPLETED' | 'CANCELLED'
): Promise<MentorSession> {
  try {
    const response = await apiPost(`/api/v1x/mentors/sessions/${sessionId}`, { status });
    if (!response.success) {
      throw new Error(response.message || 'Failed to update session');
    }
    return response.data;
  } catch (error) {
    console.error('Error updating session:', error);
    throw error;
  }
}

/**
 * Submit feedback for a completed session
 */
export async function submitSessionFeedback(
  sessionId: number,
  feedback: string
): Promise<MentorSession> {
  try {
    const response = await apiPost(`/api/v1x/mentors/sessions/${sessionId}`, {
      student_feedback: feedback
    });
    if (!response.success) {
      throw new Error(response.message || 'Failed to submit feedback');
    }
    return response.data;
  } catch (error) {
    console.error('Error submitting feedback:', error);
    throw error;
  }
}

/**
 * Submit a review for a completed session
 */
export async function submitReview(
  sessionId: number,
  rating: number,
  reviewText: string,
  tags?: string[]
): Promise<any> {
  try {
    const response = await apiPost('/api/v1x/mentors/reviews', {
      session_id: sessionId,
      rating,
      review_text: reviewText,
      tags: tags || []
    });
    if (!response.success) {
      throw new Error(response.message || 'Failed to submit review');
    }
    return response.data;
  } catch (error) {
    console.error('Error submitting review:', error);
    throw error;
  }
}

export interface MentorSearchRequest {
  expertise?: string;
  minRating?: number;
  maxRate?: number;
  limit?: number;
}

export interface AvailabilitySlotRequest {
  mentor_id?: number;
  day_of_week: number;
  date?: string;
  start_time: string;
  end_time: string;
  timezone?: string;
}

export interface ReviewSubmitRequest {
  session_id: number;
  rating: number;
  review_text: string;
  tags?: string[];
}

/**
 * Mentor Session Management API Client
 * Handles availability, booking, and feedback operations
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

// ============================================================
// TYPES & INTERFACES
// ============================================================

export interface TimeSlot {
  start: string; // "HH:MM" format
  end: string;   // "HH:MM" format
}

export interface AvailabilitySlot {
  id: string;
  mentor_id: string;
  day_of_week?: number; // 0-6 for recurring, null for specific date
  date?: string; // ISO date string
  start_time: string; // "HH:MM"
  end_time: string;   // "HH:MM"
  is_available: boolean;
  is_booked: boolean;
  timezone: string;
  created_at: string;
}

export interface MentorSessionDetail {
  id: string;
  mentor_id: string;
  student_id: string;
  topic: string;
  description?: string;
  scheduled_at: string; // ISO datetime
  duration_minutes: number;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'no_show';
  meeting_url?: string;
  price: number;
  payment_status: string;
  mentor_notes?: string;
  student_feedback?: string;
  created_at: string;
  completed_at?: string;
  cancelled_at?: string;
}

export interface SessionListResponse {
  sessions: MentorSessionDetail[];
  total: number;
  upcoming: number;
  completed: number;
  cancelled: number;
}

export interface SessionFeedback {
  id: string;
  session_id: string;
  mentor_feedback?: string;
  student_notes?: string;
  recording_url?: string;
  duration_actual?: number;
  session_quality_rating?: number; // 1-5
  key_topics?: string;
  follow_up_required: boolean;
  created_at: string;
  updated_at: string;
}

export interface MentorRating {
  mentor_id: string;
  average_rating: number;
  total_reviews: number;
  five_star: number;
  four_star: number;
  three_star: number;
  two_star: number;
  one_star: number;
}

export interface BookSessionRequest {
  mentor_id: string;
  topic: string;
  description?: string;
  scheduled_at: string; // ISO datetime
  duration_minutes: number; // 30, 60, or 90
}

export interface AvailabilityRequest {
  day_of_week?: number; // 0-6 for recurring
  date?: string; // ISO date for specific date
  start_time: string; // "HH:MM"
  end_time: string; // "HH:MM"
  timezone?: string;
}

export interface SessionFeedbackRequest {
  mentor_feedback?: string;
  student_notes?: string;
  recording_url?: string;
  duration_actual?: number;
  session_quality_rating?: number; // 1-5
  key_topics?: string;
  follow_up_required?: boolean;
}

// ============================================================
// AVAILABILITY ENDPOINTS
// ============================================================

export async function getMentorAvailability(token: string): Promise<AvailabilitySlot[]> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/availability`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch availability');
  }

  const data = await response.json();
  return data.slots || [];
}

export async function createAvailabilitySlot(
  slot: AvailabilityRequest,
  token: string
): Promise<AvailabilitySlot> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/availability`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(slot),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create availability');
  }

  return response.json();
}

export async function updateAvailabilitySlot(
  slotId: string,
  updates: Partial<AvailabilityRequest>,
  token: string
): Promise<AvailabilitySlot> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/availability/${slotId}`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updates),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update availability');
  }

  return response.json();
}

export async function deleteAvailabilitySlot(slotId: string, token: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/availability/${slotId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete availability');
  }

  return response.json();
}

// ============================================================
// SESSION BOOKING & MANAGEMENT
// ============================================================

export async function getAvailableSlots(mentorId: string): Promise<AvailabilitySlot[]> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/availability/${mentorId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch available slots');
  }

  const data = await response.json();
  // Backend returns wrapped response: { slots: [...] }
  return data.slots || [];
}

export async function bookSession(
  booking: BookSessionRequest,
  token: string
): Promise<MentorSessionDetail> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/sessions/book`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(booking),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to book session');
  }

  return response.json();
}

export async function getMySessions(token: string): Promise<SessionListResponse> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/sessions/my-sessions`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch sessions');
  }

  return response.json();
}

export async function getSessionDetails(sessionId: string, token: string): Promise<MentorSessionDetail> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/sessions/${sessionId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch session');
  }

  return response.json();
}

export async function confirmSession(sessionId: string, token: string): Promise<MentorSessionDetail> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/sessions/${sessionId}/confirm`, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to confirm session');
  }

  return response.json();
}

export async function cancelSession(sessionId: string, reason: string, token: string): Promise<MentorSessionDetail> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/sessions/${sessionId}/cancel`, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ cancellation_reason: reason }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to cancel session');
  }

  return response.json();
}

// ============================================================
// FEEDBACK & RATINGS
// ============================================================

export async function submitSessionFeedback(
  sessionId: string,
  feedback: SessionFeedbackRequest,
  token: string
): Promise<SessionFeedback> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/sessions/${sessionId}/feedback`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(feedback),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit feedback');
  }

  return response.json();
}

export async function getSessionFeedback(sessionId: string, token: string): Promise<SessionFeedback> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/sessions/${sessionId}/feedback`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch feedback');
  }

  return response.json();
}

export async function getMentorRatings(mentorId: string): Promise<MentorRating> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/${mentorId}/ratings`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch ratings');
  }

  return response.json();
}

// ============================================================
// SESSION DURATION OPTIONS
// ============================================================

export const SESSION_DURATIONS = [
  { value: 30, label: '30 minutes' },
  { value: 60, label: '1 hour' },
  { value: 90, label: '1.5 hours' },
];

export const DAYS_OF_WEEK = [
  { value: 0, label: 'Monday' },
  { value: 1, label: 'Tuesday' },
  { value: 2, label: 'Wednesday' },
  { value: 3, label: 'Thursday' },
  { value: 4, label: 'Friday' },
  { value: 5, label: 'Saturday' },
  { value: 6, label: 'Sunday' },
];

export const SESSION_STATUSES = [
  { value: 'pending', label: 'Pending Confirmation', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'confirmed', label: 'Confirmed', color: 'bg-blue-100 text-blue-800' },
  { value: 'completed', label: 'Completed', color: 'bg-green-100 text-green-800' },
  { value: 'cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-800' },
  { value: 'no_show', label: 'No Show', color: 'bg-gray-100 text-gray-800' },
];

const RAW_BASE = process.env.NEXT_PUBLIC_API_BASE?.trim() || "http://localhost:8001";
export const API_BASE = RAW_BASE.replace(/\/+$/, "");

function buildUrl(path: string) {
  const clean = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${clean}`;
}

export async function apiGet(path: string) {
  const url = buildUrl(path);
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    let errorMsg = `GET ${url} failed (${res.status})`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        errorMsg = errorData.detail;
      }
    } catch (e) {
      // If JSON parsing fails, use default error message
    }
    throw new Error(errorMsg);
  }
  try {
    return await res.json();
  } catch (e) {
    // Fallback to text for endpoints that return plain text
    return await res.text();
  }
}

export async function apiPost(path: string, data: any) {
  const url = buildUrl(path);
  const res = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data ?? {})
  });
  if (!res.ok) {
    let errorMsg = `POST ${url} failed (${res.status})`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        errorMsg = errorData.detail;
      }
    } catch (e) {
      // If JSON parsing fails, use default error message
    }
    throw new Error(errorMsg);
  }
  try {
    return await res.json();
  } catch (e) {
    return await res.text();
  }
}

export async function apiPatch(path: string, data: any) {
  const url = buildUrl(path);
  const res = await fetch(url, {
    method: "PATCH",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data ?? {})
  });
  if (!res.ok) {
    let errorMsg = `PATCH ${url} failed (${res.status})`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        errorMsg = errorData.detail;
      }
    } catch (e) {
      // If JSON parsing fails, use default error message
    }
    throw new Error(errorMsg);
  }
  try {
    return await res.json();
  } catch (e) {
    return await res.text();
  }
}

export async function apiPut(path: string, data: any) {
  const url = buildUrl(path);
  const res = await fetch(url, {
    method: "PUT",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data ?? {})
  });
  if (!res.ok) {
    let errorMsg = `PUT ${url} failed (${res.status})`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        errorMsg = errorData.detail;
      }
    } catch (e) {
      // If JSON parsing fails, use default error message
    }
    throw new Error(errorMsg);
  }
  try {
    return await res.json();
  } catch (e) {
    return await res.text();
  }
}

export async function apiDelete(path: string) {
  const url = buildUrl(path);
  const res = await fetch(url, {
    method: "DELETE",
    credentials: "include",
  });
  if (!res.ok) {
    let errorMsg = `DELETE ${url} failed (${res.status})`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        errorMsg = errorData.detail;
      }
    } catch (e) {
      // If JSON parsing fails, use default error message
    }
    throw new Error(errorMsg);
  }
  try {
    return await res.json();
  } catch (e) {
    return await res.text();
  }
}

// Compatibility wrapper for apiCall - some pages use this with method parameter
export async function apiCall(path: string, options?: { method?: string; [key: string]: any }) {
  const method = options?.method || 'GET'
  
  if (method === 'GET') {
    return await apiGet(path)
  } else if (method === 'POST') {
    const { method, ...data } = options || {}
    return await apiPost(path, data)
  } else {
    throw new Error(`Unsupported method: ${method}`)
  }
}

// =============== MENTOR BOOKING API FUNCTIONS ===============

export async function getMentors(filters?: {
  expertise?: string;
  minRating?: number;
  maxPrice?: number;
  minPrice?: number;
  query?: string;
  availability?: boolean;
  sortBy?: string;
  limit?: number;
  offset?: number;
}) {
  const params = new URLSearchParams();
  if (filters?.query) params.append('query', filters.query);
  if (filters?.expertise) params.append('expertise', filters.expertise);
  if (filters?.minRating) params.append('min_rating', String(filters.minRating));
  if (filters?.maxPrice) params.append('max_price', String(filters.maxPrice));
  if (filters?.minPrice) params.append('min_price', String(filters.minPrice));
  if (filters?.availability) params.append('availability', String(filters.availability));
  if (filters?.sortBy) params.append('sort_by', filters.sortBy);
  if (filters?.limit) params.append('limit', String(filters.limit));
  if (filters?.offset) params.append('offset', String(filters.offset));
  
  const path = `/api/v1x/mentors${params.toString() ? '?' + params.toString() : ''}`;
  return apiGet(path);
}

export async function getMentor(mentorId: number) {
  return apiGet(`/api/v1x/mentors/${mentorId}`);
}

export async function getMentorAvailability(mentorId: number) {
  return apiGet(`/api/v1x/mentors/availability/${mentorId}`);
}

export async function bookMentorSession(booking: {
  mentor_id: number;
  scheduled_at: string;
  topic: string;
  duration_minutes?: number;
  description?: string;
}) {
  return apiPost('/api/v1x/mentors/sessions', booking);
}

export async function getMyMentorSessions() {
  return apiGet('/api/v1x/mentors/sessions/my');
}

export async function cancelMentorSession(sessionId: number) {
  return apiPatch(`/api/v1x/mentors/sessions/${sessionId}`, { 
    status: 'cancelled' 
  });
}

// =============== REVIEWS & RATINGS ===============

export async function submitMentorReview(review: {
  session_id: number;
  rating: number;
  review_text?: string;
  tags?: string;
}) {
  return apiPost('/api/v1x/mentors/reviews', review);
}

export async function getMentorReviews(mentorId: number, limit?: number) {
  const params = new URLSearchParams();
  if (limit) params.append('limit', String(limit));
  const path = `/api/v1x/mentors/reviews/${mentorId}${params.toString() ? '?' + params.toString() : ''}`;
  return apiGet(path);
}

export async function updateMentorReview(reviewId: number, updates: {
  rating?: number;
  review_text?: string;
  tags?: string;
}) {
  return apiPatch(`/api/v1x/mentors/reviews/${reviewId}`, updates);
}

export async function deleteMentorReview(reviewId: number) {
  return apiDelete(`/api/v1x/mentors/reviews/${reviewId}`);
}

// =============== SESSION FEEDBACK ===============

export async function submitSessionFeedback(sessionId: number, feedback: {
  mentor_feedback?: string;
  student_notes?: string;
  recording_url?: string;
  duration_actual?: number;
  session_quality_rating?: number;
  key_topics?: string;
  follow_up_required?: boolean;
}) {
  return apiPost(`/api/v1x/mentors/sessions/${sessionId}/feedback`, feedback);
}

export async function getSessionFeedback(sessionId: number) {
  return apiGet(`/api/v1x/mentors/sessions/${sessionId}/feedback`);
}

// =============== ADVANCED SEARCH & FILTERING ===============

export async function searchMentors(filters: {
  query?: string;
  expertise?: string;
  minRating?: number;
  maxPrice?: number;
  minPrice?: number;
  availability?: boolean;
  sortBy?: string;
  limit?: number;
  offset?: number;
}) {
  return getMentors(filters); // Reuse the enhanced getMentors function
}

// =============== CALENDAR & EXPORT ===============

export async function exportCalendarAsIcal() {
  const response = await fetch(buildUrl('/api/v1x/mentors/calendar/export?format=ical'), {
    credentials: 'include'
  });
  if (!response.ok) {
    throw new Error(`Calendar export failed (${response.status})`);
  }
  const data = await response.json();
  return data.ical_data; // Returns iCal string
}

export async function getCalendarEvents(startDate?: string, endDate?: string) {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  const path = `/api/v1x/mentors/calendar/events${params.toString() ? '?' + params.toString() : ''}`;
  return apiGet(path);
}

export async function exportCalendarToGoogle() {
  return apiGet('/api/v1x/mentors/calendar/export?format=google');
}

// =============== EMAIL NOTIFICATIONS ===============

export async function sendBookingConfirmation(sessionId: number) {
  return apiPost(`/api/v1x/mentors/emails/confirmation`, { session_id: sessionId });
}

export async function sendSessionReminder(sessionId: number) {
  return apiPost(`/api/v1x/mentors/emails/reminder`, { session_id: sessionId });
}

export async function sendReviewRequest(sessionId: number) {
  return apiPost(`/api/v1x/mentors/emails/review-request`, { session_id: sessionId });
}


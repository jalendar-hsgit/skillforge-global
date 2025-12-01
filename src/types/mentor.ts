// Shared mentor portal types
export interface MentorProfile {
  id: number;
  bio: string;
  expertise: string | string[];
  hourly_rate: number;
  average_rating?: number;
  total_sessions?: number;
  status: string;
}

export interface SessionResponse {
  id: number;
  mentor_id: number;
  student_id: number;
  topic: string;
  description?: string;
  scheduled_at: string;
  duration_minutes: number;
  status: string;
  meeting_url?: string;
  price?: number;
  payment_status?: string;
  mentor_notes?: string;
  student_feedback?: string;
  created_at?: string;
}

export interface SessionListResponse {
  sessions: SessionResponse[];
  total: number;
}

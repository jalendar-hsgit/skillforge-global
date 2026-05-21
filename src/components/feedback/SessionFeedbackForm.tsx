/**
 * Session feedback form component
 * Allows mentors and students to add feedback after sessions
 */

import React from 'react';
import { submitSessionFeedback } from '@/lib/api';

interface SessionFeedbackFormProps {
  sessionId: number;
  userRole: 'mentor' | 'student';
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function SessionFeedbackForm({
  sessionId,
  userRole,
  onSuccess,
  onCancel
}: SessionFeedbackFormProps) {
  const [feedback, setFeedback] = React.useState({
    mentor_feedback: '',
    student_notes: '',
    recording_url: '',
    duration_actual: undefined as number | undefined,
    session_quality_rating: 5,
    key_topics: '',
    follow_up_required: false
  });

  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (userRole === 'mentor' && !feedback.mentor_feedback.trim()) {
      setError('Please provide your feedback');
      return;
    }
    
    if (userRole === 'student' && !feedback.student_notes.trim()) {
      setError('Please share your notes');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await submitSessionFeedback(sessionId, {
        mentor_feedback: userRole === 'mentor' ? feedback.mentor_feedback : undefined,
        student_notes: userRole === 'student' ? feedback.student_notes : undefined,
        recording_url: feedback.recording_url || undefined,
        duration_actual: feedback.duration_actual,
        session_quality_rating: feedback.session_quality_rating,
        key_topics: feedback.key_topics || undefined,
        follow_up_required: feedback.follow_up_required
      });

      setFeedback({
        mentor_feedback: '',
        student_notes: '',
        recording_url: '',
        duration_actual: undefined,
        session_quality_rating: 5,
        key_topics: '',
        follow_up_required: false
      });
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit feedback');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-gray-50 rounded-lg">
      <h3 className="text-lg font-semibold">
        {userRole === 'mentor' ? 'Mentor Feedback' : 'Student Notes'}
      </h3>

      {error && (
        <div className="p-3 bg-red-100 text-red-700 rounded text-sm">
          {error}
        </div>
      )}

      {/* Main feedback/notes */}
      <div>
        <label className="block text-sm font-medium mb-2">
          {userRole === 'mentor' ? 'Feedback for Student *' : 'Session Notes *'}
        </label>
        <textarea
          value={userRole === 'mentor' ? feedback.mentor_feedback : feedback.student_notes}
          onChange={(e) =>
            setFeedback({
              ...feedback,
              [userRole === 'mentor' ? 'mentor_feedback' : 'student_notes']: e.target.value
            })
          }
          placeholder={
            userRole === 'mentor'
              ? "Share your observations and recommendations..."
              : "What did you learn? Any questions for next session?"
          }
          maxLength={2000}
          rows={4}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <span className="text-xs text-gray-500">
          {(userRole === 'mentor' ? feedback.mentor_feedback : feedback.student_notes).length}/2000
        </span>
      </div>

      {/* Optional fields for mentor */}
      {userRole === 'mentor' && (
        <>
          <div>
            <label className="block text-sm font-medium mb-2">Recording URL</label>
            <input
              type="url"
              value={feedback.recording_url}
              onChange={(e) => setFeedback({ ...feedback, recording_url: e.target.value })}
              placeholder="Link to session recording (if available)"
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Actual Duration (minutes)</label>
            <input
              type="number"
              value={feedback.duration_actual || ''}
              onChange={(e) =>
                setFeedback({
                  ...feedback,
                  duration_actual: e.target.value ? Number(e.target.value) : undefined
                })
              }
              placeholder="How long did the session actually last?"
              min="0"
              max="600"
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Key Topics Covered</label>
            <input
              type="text"
              value={feedback.key_topics}
              onChange={(e) => setFeedback({ ...feedback, key_topics: e.target.value })}
              placeholder="Comma-separated topics (e.g., React, hooks, state management)"
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={feedback.follow_up_required}
              onChange={(e) => setFeedback({ ...feedback, follow_up_required: e.target.checked })}
              className="rounded"
            />
            <span className="text-sm">Follow-up session required</span>
          </label>
        </>
      )}

      {/* Session quality rating */}
      <div>
        <label className="block text-sm font-medium mb-2">Session Quality</label>
        <select
          value={feedback.session_quality_rating}
          onChange={(e) =>
            setFeedback({ ...feedback, session_quality_rating: Number(e.target.value) })
          }
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="5">⭐⭐⭐⭐⭐ Excellent</option>
          <option value="4">⭐⭐⭐⭐ Good</option>
          <option value="3">⭐⭐⭐ Average</option>
          <option value="2">⭐⭐ Fair</option>
          <option value="1">⭐ Needs Improvement</option>
        </select>
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-2">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md font-medium disabled:bg-gray-400"
        >
          {loading ? 'Saving...' : 'Save Feedback'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

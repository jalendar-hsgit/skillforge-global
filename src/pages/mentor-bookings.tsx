'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import styles from '../styles/mentor-bookings.module.css';
import { getMyBookings, submitSessionFeedback, MentorSession } from '../lib/mentorBookingApi';
import Link from 'next/link';

export default function MentorBookingsPage() {
  const router = useRouter();
  const [bookings, setBookings] = useState<MentorSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [feedbackId, setFeedbackId] = useState<number | null>(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  useEffect(() => {
    loadBookings();
  }, []);

  const loadBookings = async () => {
    try {
      setLoading(true);
      const data = await getMyBookings();
      setBookings(data);
    } catch (err) {
      setError('Failed to load bookings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFeedback = async (sessionId: number) => {
    if (!feedbackText.trim()) {
      setError('Please enter feedback');
      return;
    }

    try {
      setSubmittingFeedback(true);
      await submitSessionFeedback(sessionId, feedbackText);
      setFeedbackId(null);
      setFeedbackText('');
      await loadBookings();
    } catch (err) {
      setError('Failed to submit feedback');
      console.error(err);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const getStatusColor = (status: string): string => {
    const statusMap: { [key: string]: string } = {
      PENDING: 'pending',
      CONFIRMED: 'pending',
      COMPLETED: 'success',
      CANCELLED: 'error',
    };
    return statusMap[status] || 'pending';
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading your bookings...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.pageContent}>
        <div className={styles.header}>
          <h1 className={styles.title}>My Mentor Sessions</h1>
          <Link href="/mentor-booking">
            <button className={styles.bookButton}>Book New Session</button>
          </Link>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        {bookings.length === 0 ? (
          <div className={styles.emptyState}>
            <p className={styles.emptyMessage}>No mentor sessions booked yet</p>
            <Link href="/mentor-booking">
              <button className={styles.bookButton}>Book Your First Session</button>
            </Link>
          </div>
        ) : (
          <div className={styles.bookingsTable}>
            <table>
              <thead>
                <tr>
                  <th>Mentor Topic</th>
                  <th>Date & Time</th>
                  <th>Duration</th>
                  <th>Status</th>
                  <th>Price</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {bookings.map((booking) => (
                  <tr key={booking.id}>
                    <td className={styles.topicCell}>{booking.topic}</td>
                    <td>{formatDate(booking.scheduled_at)}</td>
                    <td>{booking.duration_minutes} min</td>
                    <td>
                      <span className={`${styles.status} ${styles[getStatusColor(booking.status)]}`}>
                        {booking.status}
                      </span>
                    </td>
                    <td>${booking.price.toFixed(2)}</td>
                    <td className={styles.actionCell}>
                      {booking.status === 'COMPLETED' && !booking.student_feedback && (
                        <button
                          onClick={() => setFeedbackId(booking.id)}
                          className={styles.actionButton}
                        >
                          Add Feedback
                        </button>
                      )}
                      {booking.meeting_url && booking.status === 'CONFIRMED' && (
                        <a
                          href={booking.meeting_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={styles.actionButton}
                        >
                          Join Call
                        </a>
                      )}
                      <button
                        onClick={() => router.push(`/mentor-booking/${booking.id}`)}
                        className={styles.viewButton}
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Feedback Modal */}
        {feedbackId && (
          <div className={styles.modal}>
            <div className={styles.modalContent}>
              <h3>Add Feedback</h3>
              <textarea
                placeholder="Share your experience with this mentor session..."
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                className={styles.feedbackInput}
                rows={4}
              />
              <div className={styles.modalButtons}>
                <button
                  onClick={() => setFeedbackId(null)}
                  className={styles.cancelButton}
                  disabled={submittingFeedback}
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSubmitFeedback(feedbackId)}
                  className={styles.submitButton}
                  disabled={submittingFeedback}
                >
                  {submittingFeedback ? 'Submitting...' : 'Submit Feedback'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { Bell, Mail, Calendar, Send, Check, AlertCircle } from 'lucide-react';
import { API_BASE } from '@/lib/apiBase';

interface PendingReminders {
  overdue_followups: number;
  upcoming_interviews: number;
  total_pending: number;
}

export default function JobNotifications() {
  const [pending, setPending] = useState<PendingReminders | null>(null);
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPendingReminders();
  }, []);

  const fetchPendingReminders = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1x/job-applications-notifications/pending-reminders`, {
        credentials: 'include',
      });
      if (res.ok) {
        setPending(await res.json());
      }
    } catch (err) {
      console.error('Error fetching pending reminders:', err);
    }
  };

  const sendFollowUpReminders = async () => {
    try {
      setSending(true);
      setError('');
      setMessage('');
      
      const res = await fetch(`${API_BASE}/api/v1x/job-applications-notifications/send-follow-up-reminders`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (res.ok) {
        const data = await res.json();
        setMessage(data.message);
        fetchPendingReminders();
      } else {
        setError('Failed to send follow-up reminders');
      }
    } catch (err) {
      setError('An error occurred while sending reminders');
    } finally {
      setSending(false);
    }
  };

  const sendInterviewReminders = async () => {
    try {
      setSending(true);
      setError('');
      setMessage('');
      
      const res = await fetch(`${API_BASE}/api/v1x/job-applications-notifications/send-interview-reminders?hours_before=24`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (res.ok) {
        const data = await res.json();
        setMessage(data.message);
        fetchPendingReminders();
      } else {
        setError('Failed to send interview reminders');
      }
    } catch (err) {
      setError('An error occurred while sending reminders');
    } finally {
      setSending(false);
    }
  };

  if (!pending) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="h-16 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <Bell className="w-6 h-6 text-blue-600" />
        Email Notifications
      </h3>

      {/* Pending Reminders Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200">
          <p className="text-sm text-red-600 font-semibold">Overdue Follow-ups</p>
          <p className="text-3xl font-bold text-red-700">{pending.overdue_followups}</p>
        </div>

        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-4 rounded-lg border border-yellow-200">
          <p className="text-sm text-yellow-600 font-semibold">Upcoming Interviews (48h)</p>
          <p className="text-3xl font-bold text-yellow-700">{pending.upcoming_interviews}</p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-600 font-semibold">Total Pending</p>
          <p className="text-3xl font-bold text-blue-700">{pending.total_pending}</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3">
        <button
          onClick={sendFollowUpReminders}
          disabled={sending || pending.overdue_followups === 0}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Mail className="w-5 h-5" />
          {sending ? 'Sending...' : `Send Follow-up Reminders (${pending.overdue_followups})`}
        </button>

        <button
          onClick={sendInterviewReminders}
          disabled={sending || pending.upcoming_interviews === 0}
          className="w-full flex items-center justify-center gap-2 bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Calendar className="w-5 h-5" />
          {sending ? 'Sending...' : `Send Interview Reminders (${pending.upcoming_interviews})`}
        </button>
      </div>

      {/* Success/Error Messages */}
      {message && (
        <div className="mt-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <Check className="w-5 h-5" />
          {message}
        </div>
      )}

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* Configuration Note */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>📧 Email Configuration:</strong> To enable email notifications, set environment variables:
          <code className="block mt-2 bg-blue-100 p-2 rounded text-xs">
            SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL
          </code>
        </p>
      </div>
    </div>
  );
}

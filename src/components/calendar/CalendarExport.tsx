/**
 * Calendar export buttons component
 * Allows users to export sessions in different formats
 */

import React from 'react';
import { exportCalendarAsIcal, getCalendarEvents } from '@/lib/api';

interface CalendarExportProps {
  onExportStart?: () => void;
  onExportComplete?: () => void;
}

export function CalendarExport({ onExportStart, onExportComplete }: CalendarExportProps) {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const [success, setSuccess] = React.useState('');

  const handleExportIcal = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    onExportStart?.();

    try {
      const icalData = await exportCalendarAsIcal();
      
      // Create and download .ics file
      const element = document.createElement('a');
      const file = new Blob([icalData], { type: 'text/calendar' });
      element.href = URL.createObjectURL(file);
      element.download = 'mentor-sessions.ics';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);

      setSuccess('Calendar exported successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export calendar');
    } finally {
      setLoading(false);
      onExportComplete?.();
    }
  };

  const handleExportGoogle = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    onExportStart?.();

    try {
      // In a real app, this would open Google's OAuth flow
      // For now, we'll show a message
      setSuccess('Opening Google Calendar integration...');
      // await exportCalendarToGoogle();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export to Google Calendar');
    } finally {
      setLoading(false);
      onExportComplete?.();
    }
  };

  return (
    <div className="space-y-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
      <h3 className="font-semibold text-blue-900">Export Your Calendar</h3>
      
      {error && (
        <div className="p-3 bg-red-100 text-red-700 rounded text-sm">
          {error}
        </div>
      )}
      
      {success && (
        <div className="p-3 bg-green-100 text-green-700 rounded text-sm">
          {success}
        </div>
      )}

      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={handleExportIcal}
          disabled={loading}
          className="flex flex-col items-center gap-2 p-3 bg-white border rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          <span className="text-lg">📅</span>
          <span className="text-sm font-medium">iCalendar</span>
          <span className="text-xs text-gray-500">(.ics file)</span>
        </button>

        <button
          onClick={handleExportGoogle}
          disabled={loading}
          className="flex flex-col items-center gap-2 p-3 bg-white border rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          <span className="text-lg">🔗</span>
          <span className="text-sm font-medium">Google Calendar</span>
          <span className="text-xs text-gray-500">Link account</span>
        </button>
      </div>

      <p className="text-xs text-gray-600 text-center">
        Export your mentor sessions to your preferred calendar app
      </p>
    </div>
  );
}

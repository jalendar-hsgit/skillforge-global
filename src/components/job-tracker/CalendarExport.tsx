'use client';

import { useState } from 'react';
import { Calendar, Download, ExternalLink } from 'lucide-react';
import { API_BASE } from '@/lib/apiBase';

interface CalendarExportProps {
  applicationId: number;
  interviewIndex: number;
  showAllInterviews?: boolean;
}

export default function CalendarExport({ applicationId, interviewIndex, showAllInterviews = false }: CalendarExportProps) {
  const [exporting, setExporting] = useState(false);

  const downloadICalSingle = async () => {
    try {
      setExporting(true);
      const res = await fetch(
        `${API_BASE}/api/v1x/job-applications-calendar/${applicationId}/interview/${interviewIndex}/ical`,
        { credentials: 'include' }
      );
      
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `interview-${applicationId}.ics`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error downloading iCal:', error);
      alert('Failed to download calendar file');
    } finally {
      setExporting(false);
    }
  };

  const downloadICalAll = async () => {
    try {
      setExporting(true);
      const res = await fetch(
        `${API_BASE}/api/v1x/job-applications-calendar/${applicationId}/all-interviews/ical`,
        { credentials: 'include' }
      );
      
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `all-interviews-${applicationId}.ics`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error downloading iCal:', error);
      alert('Failed to download calendar file');
    } finally {
      setExporting(false);
    }
  };

  const openGoogleCalendar = async () => {
    try {
      const res = await fetch(
        `${API_BASE}/api/v1x/job-applications-calendar/${applicationId}/interview/${interviewIndex}/google-calendar`,
        { credentials: 'include' }
      );
      
      if (res.ok) {
        const data = await res.json();
        window.open(data.url, '_blank');
      }
    } catch (error) {
      console.error('Error opening Google Calendar:', error);
      alert('Failed to open Google Calendar');
    }
  };

  const openOutlook = async () => {
    try {
      const res = await fetch(
        `${API_BASE}/api/v1x/job-applications-calendar/${applicationId}/interview/${interviewIndex}/outlook`,
        { credentials: 'include' }
      );
      
      if (res.ok) {
        const data = await res.json();
        window.open(data.url, '_blank');
      }
    } catch (error) {
      console.error('Error opening Outlook:', error);
      alert('Failed to open Outlook');
    }
  };

  return (
    <div className="space-y-2">
      <p className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
        <Calendar className="w-4 h-4" />
        Export to Calendar
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        {/* Google Calendar */}
        <button
          onClick={openGoogleCalendar}
          disabled={exporting}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition text-sm disabled:opacity-50"
        >
          <ExternalLink className="w-4 h-4" />
          Google Calendar
        </button>

        {/* Outlook */}
        <button
          onClick={openOutlook}
          disabled={exporting}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition text-sm disabled:opacity-50"
        >
          <ExternalLink className="w-4 h-4" />
          Outlook
        </button>

        {/* iCal Download */}
        <button
          onClick={showAllInterviews ? downloadICalAll : downloadICalSingle}
          disabled={exporting}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm disabled:opacity-50"
        >
          <Download className="w-4 h-4" />
          {exporting ? 'Exporting...' : 'Download .ics'}
        </button>
      </div>

      <p className="text-xs text-gray-500 mt-2">
        💡 Use Google Calendar or Outlook links to add directly, or download .ics file for Apple Calendar, Outlook desktop, or other calendar apps
      </p>
    </div>
  );
}

// Component for downloading all upcoming interviews
export function DownloadAllInterviews() {
  const [exporting, setExporting] = useState(false);
  const [days, setDays] = useState(30);

  const downloadAllUpcoming = async () => {
    try {
      setExporting(true);
      const res = await fetch(
        `${API_BASE}/api/v1x/job-applications-calendar/upcoming-interviews?days=${days}`,
        { credentials: 'include' }
      );
      
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `upcoming-interviews.ics`;
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        alert('No upcoming interviews found');
      }
    } catch (error) {
      console.error('Error downloading all interviews:', error);
      alert('Failed to download calendar file');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <Calendar className="w-6 h-6 text-purple-600" />
        Export All Upcoming Interviews
      </h3>

      <p className="text-gray-600 mb-4">
        Download all your upcoming interviews in one calendar file
      </p>

      <div className="flex items-center gap-4">
        <label className="text-sm font-semibold text-gray-700">
          Next
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="ml-2 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={7}>7 days</option>
            <option value={14}>14 days</option>
            <option value={30}>30 days</option>
            <option value={60}>60 days</option>
            <option value={90}>90 days</option>
          </select>
        </label>

        <button
          onClick={downloadAllUpcoming}
          disabled={exporting}
          className="flex-1 flex items-center justify-center gap-2 bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
        >
          <Download className="w-5 h-5" />
          {exporting ? 'Exporting...' : 'Download All Interviews (.ics)'}
        </button>
      </div>

      <div className="mt-4 p-4 bg-purple-50 border border-purple-200 rounded-lg">
        <p className="text-sm text-purple-800">
          <strong>📅 Calendar Import:</strong> After downloading, open the .ics file with your calendar app to import all interviews at once. They'll include reminders 1 hour before each interview.
        </p>
      </div>
    </div>
  );
}

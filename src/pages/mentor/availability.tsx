'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useProtectedPage } from '@/lib/useProtectedPage';
import { useToast } from '@/components/Toast';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import Layout from '@/components/Layout';
import Button from '@/components/Button';
import Card from '@/components/Card';
import Input from '@/components/Input';
import {
  getMentorAvailability,
  createAvailabilitySlot,
  updateAvailabilitySlot,
  deleteAvailabilitySlot,
  AvailabilitySlot,
  AvailabilityRequest,
  DAYS_OF_WEEK,
} from '@/lib/api/mentorSessionApi';

export default function MentorAvailabilityPage() {
  const router = useRouter();
  const { user, loading: authLoading, isAuthorized } = useProtectedPage('mentor');
  const { addToast } = useToast();

  const [availabilitySlots, setAvailabilitySlots] = useState<AvailabilitySlot[]>([]);
  const [loading, setLoading] = useState(true);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('10:00');
  const [timezone, setTimezone] = useState('UTC');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  // Quick bulk options
  const [bulkDay, setBulkDay] = useState<number | null>(null);
  const [bulkStart, setBulkStart] = useState('09:00');
  const [bulkEnd, setBulkEnd] = useState('17:00');

  // Load availability
  useEffect(() => {
    if (authLoading) return;
    if (!isAuthorized) return;
    loadAvailability();
  }, [isAuthorized, authLoading]);

  const loadAvailability = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      const slots = await getMentorAvailability(token);
      setAvailabilitySlots(slots || []);
    } catch (error: any) {
      addToast({
        type: 'error',
        message: 'Failed to load availability: ' + (error.message || 'Unknown error'),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddSlot = async () => {
    if (!selectedDay && selectedDay !== 0) {
      addToast({ type: 'error', message: 'Please select a day' });
      return;
    }

    if (!startTime || !endTime) {
      addToast({ type: 'error', message: 'Please select times' });
      return;
    }

    if (startTime >= endTime) {
      addToast({ type: 'error', message: 'Start time must be before end time' });
      return;
    }

    try {
      setIsSubmitting(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');

      const request: AvailabilityRequest = {
        day_of_week: selectedDay,
        start_time: startTime,
        end_time: endTime,
        timezone,
      };

      if (editingId) {
        await updateAvailabilitySlot(editingId, request, token);
        addToast({ type: 'success', message: 'Availability updated' });
        setEditingId(null);
      } else {
        await createAvailabilitySlot(request, token);
        addToast({ type: 'success', message: 'Availability slot added' });
      }

      setShowForm(false);
      setSelectedDay(null);
      setStartTime('09:00');
      setEndTime('10:00');
      await loadAvailability();
    } catch (error: any) {
      addToast({ type: 'error', message: error.message || 'Failed to save' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteSlot = async (slotId: string) => {
    if (!confirm('Delete this availability slot?')) return;

    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      await deleteAvailabilitySlot(slotId, token);
      addToast({ type: 'success', message: 'Slot deleted' });
      await loadAvailability();
    } catch (error: any) {
      addToast({ type: 'error', message: error.message });
    }
  };

  const handleEditSlot = (slot: AvailabilitySlot) => {
    if (slot.day_of_week !== null && slot.day_of_week !== undefined) {
      setSelectedDay(slot.day_of_week);
      setStartTime(slot.start_time);
      setEndTime(slot.end_time);
      setTimezone(slot.timezone || 'UTC');
      setEditingId(slot.id);
      setShowForm(true);
    }
  };

  const handleAddBulkSlots = async () => {
    if (bulkDay === null || bulkDay === undefined) {
      addToast({ type: 'error', message: 'Select a day' });
      return;
    }

    try {
      setIsSubmitting(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');

      // Create 1-hour slots throughout the day
      const [startHour] = bulkStart.split(':').map(Number);
      const [endHour] = bulkEnd.split(':').map(Number);

      for (let hour = startHour; hour < endHour; hour++) {
        const start = `${String(hour).padStart(2, '0')}:00`;
        const end = `${String(hour + 1).padStart(2, '0')}:00`;

        const request: AvailabilityRequest = {
          day_of_week: bulkDay,
          start_time: start,
          end_time: end,
          timezone,
        };

        await createAvailabilitySlot(request, token);
      }

      addToast({ type: 'success', message: `Added ${endHour - startHour} slots` });
      setBulkDay(null);
      await loadAvailability();
    } catch (error: any) {
      addToast({ type: 'error', message: error.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (authLoading) {
    return <LoadingSpinner message="Loading..." />;
  }

  if (!isAuthorized) {
    return null;
  }

  if (loading) {
    return <LoadingSpinner message="Loading your availability..." />;
  }

  // Group slots by day
  const slotsByDay = DAYS_OF_WEEK.map(day => ({
    ...day,
    slots: availabilitySlots.filter(s => s.day_of_week === day.value),
  }));

  return (
    <Layout maxWidth="2xl">
      <div className="px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Availability Manager</h1>
          <p className="text-gray-600">Set when you're available for mentoring sessions.</p>
        </div>

        {/* Quick Add Bulk Slots */}
        <Card className="p-6 mb-8 bg-blue-50 border border-blue-200">
          <h2 className="text-xl font-bold mb-4">Quick Add: Full Day Slots</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Day</label>
              <select
                value={bulkDay ?? ''}
                onChange={(e) => setBulkDay(e.target.value ? Number(e.target.value) : null)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select day...</option>
                {DAYS_OF_WEEK.map(day => (
                  <option key={day.value} value={day.value}>{day.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Start Time</label>
              <input
                type="time"
                value={bulkStart}
                onChange={(e) => setBulkStart(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">End Time</label>
              <input
                type="time"
                value={bulkEnd}
                onChange={(e) => setBulkEnd(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={handleAddBulkSlots}
                disabled={isSubmitting}
                loading={isSubmitting}
                className="w-full"
              >
                Add Slots
              </Button>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-3">Creates 1-hour slots for each hour in the range.</p>
        </Card>

        {/* Weekly Schedule */}
        <div className="space-y-4">
          {slotsByDay.map(day => (
            <Card key={day.value} className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">{day.label}</h3>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    setSelectedDay(day.value);
                    setStartTime('09:00');
                    setEndTime('10:00');
                    setEditingId(null);
                    setShowForm(true);
                  }}
                >
                  + Add Slot
                </Button>
              </div>

              {day.slots.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No availability set</p>
              ) : (
                <div className="space-y-2">
                  {day.slots.map(slot => (
                    <div
                      key={slot.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                    >
                      <div>
                        <p className="font-medium">
                          {slot.start_time} - {slot.end_time}
                        </p>
                        <p className="text-sm text-gray-600">{slot.timezone}</p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEditSlot(slot)}
                          className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteSlot(slot.id)}
                          className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>

        {/* Modal Form */}
        {showForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="absolute inset-0" onClick={() => setShowForm(false)} />
            <Card className="relative p-6 max-w-md w-full mx-4">
              <h3 className="text-xl font-bold mb-4">
                {editingId ? 'Edit Slot' : 'Add Slot'}
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Day</label>
                  <select
                    value={selectedDay ?? ''}
                    onChange={(e) => setSelectedDay(Number(e.target.value))}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Select...</option>
                    {DAYS_OF_WEEK.map(day => (
                      <option key={day.value} value={day.value}>{day.label}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Start Time</label>
                    <input
                      type="time"
                      value={startTime}
                      onChange={(e) => setStartTime(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">End Time</label>
                    <input
                      type="time"
                      value={endTime}
                      onChange={(e) => setEndTime(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Timezone</label>
                  <select
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    <option>UTC</option>
                    <option>America/New_York</option>
                    <option>America/Chicago</option>
                    <option>America/Denver</option>
                    <option>America/Los_Angeles</option>
                    <option>Europe/London</option>
                    <option>Europe/Paris</option>
                    <option>Asia/Tokyo</option>
                    <option>Asia/Dubai</option>
                    <option>Australia/Sydney</option>
                  </select>
                </div>

                <div className="flex gap-3">
                  <Button
                    variant="secondary"
                    className="flex-1"
                    onClick={() => setShowForm(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    className="flex-1"
                    onClick={handleAddSlot}
                    loading={isSubmitting}
                  >
                    Save
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Info */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="font-bold mb-2">Tips:</h3>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• Set your weekly availability so students can book sessions</li>
            <li>• Use bulk add to quickly create multiple 1-hour slots for a full day</li>
            <li>• Your timezone helps students see correct times in their local time</li>
            <li>• You can edit or delete slots at any time</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}

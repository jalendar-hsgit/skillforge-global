import { useState, useEffect } from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { API_BASE } from '@/lib/apiBase';

interface AvailabilitySlot {
  id?: number;
  day_of_week?: number | null;
  date?: string | null;
  start_time: string;
  end_time: string;
  is_available: boolean;
  is_booked: boolean;
  timezone: string;
}

interface AvailabilityCalendarProps {
  mentorId: number;
  editable?: boolean;
}

export default function AvailabilityCalendar({ mentorId, editable = false }: AvailabilityCalendarProps) {
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [showAddModal, setShowAddModal] = useState(false);
  
  // Add slot form state
  const [newSlot, setNewSlot] = useState({
    isRecurring: false,
    dayOfWeek: 1, // Monday
    specificDate: '',
    startTime: '09:00',
    endTime: '10:00',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
  });

  const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  useEffect(() => {
    fetchAvailability();
  }, [mentorId]);

  const fetchAvailability = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${API_BASE}/api/v1x/mentors/availability/${mentorId}`,
        { credentials: 'include' }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch availability');
      }

      const data = await response.json();
      setSlots(data.slots || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addAvailabilitySlot = async () => {
    try {
      setError('');

      const response = await fetch(
        `${API_BASE}/api/v1x/mentors/availability`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            day_of_week: newSlot.isRecurring ? newSlot.dayOfWeek : null,
            date: !newSlot.isRecurring ? newSlot.specificDate : null,
            start_time: newSlot.startTime,
            end_time: newSlot.endTime,
            timezone: newSlot.timezone
          })
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to add slot');
      }

      await fetchAvailability();
      setShowAddModal(false);
      
      // Reset form
      setNewSlot({
        isRecurring: false,
        dayOfWeek: 1,
        specificDate: '',
        startTime: '09:00',
        endTime: '10:00',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const deleteSlot = async (slotId: number) => {
    if (!confirm('Delete this availability slot?')) return;

    try {
      const response = await fetch(
        `${API_BASE}/api/v1x/mentors/availability/${slotId}`,
        {
          method: 'DELETE',
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete slot');
      }

      await fetchAvailability();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const getWeekDates = () => {
    const week = [];
    const curr = new Date(selectedDate);
    const first = curr.getDate() - curr.getDay();

    for (let i = 0; i < 7; i++) {
      const date = new Date(curr.setDate(first + i));
      week.push(date);
    }
    return week;
  };

  const getSlotsForDate = (date: Date) => {
    const dayOfWeek = date.getDay();
    const dateStr = date.toISOString().split('T')[0];

    return slots.filter(slot => {
      // Recurring slots matching day of week
      if (slot.day_of_week === dayOfWeek && slot.is_available) {
        return true;
      }
      // Specific date slots
      if (slot.date && slot.date.startsWith(dateStr) && slot.is_available) {
        return true;
      }
      return false;
    });
  };

  const navigateWeek = (direction: 'prev' | 'next') => {
    const newDate = new Date(selectedDate);
    newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
    setSelectedDate(newDate);
  };

  const formatTime = (time: string) => {
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  if (loading) {
    return (
      <Card>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Card>
    );
  }

  const weekDates = getWeekDates();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Availability Calendar
          </h2>
          <p className="text-gray-600">
            {selectedDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </p>
        </div>
        {editable && (
          <Button
            onClick={() => setShowAddModal(true)}
            variant="primary"
          >
            + Add Availability
          </Button>
        )}
      </div>

      {error && (
        <Card className="bg-red-50 border-red-200">
          <p className="text-red-700">{error}</p>
        </Card>
      )}

      {/* Week Navigation */}
      <div className="flex items-center justify-between">
        <Button
          onClick={() => navigateWeek('prev')}
          variant="outline"
        >
          ← Previous Week
        </Button>
        <Button
          onClick={() => setSelectedDate(new Date())}
          variant="outline"
        >
          Today
        </Button>
        <Button
          onClick={() => navigateWeek('next')}
          variant="outline"
        >
          Next Week →
        </Button>
      </div>

      {/* Calendar Grid */}
      <Card>
        <div className="grid grid-cols-7 gap-2">
          {weekDates.map((date, idx) => {
            const daySlots = getSlotsForDate(date);
            const isToday = date.toDateString() === new Date().toDateString();
            const isPast = date < new Date() && !isToday;

            return (
              <div
                key={idx}
                className={`min-h-[150px] border rounded-lg p-3 ${
                  isToday ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                } ${isPast ? 'bg-gray-50 opacity-60' : ''}`}
              >
                <div className="text-center mb-2">
                  <p className="text-xs font-medium text-gray-600">
                    {daysOfWeek[date.getDay()]}
                  </p>
                  <p className={`text-lg font-bold ${
                    isToday ? 'text-blue-600' : 'text-gray-900'
                  }`}>
                    {date.getDate()}
                  </p>
                </div>

                <div className="space-y-1">
                  {daySlots.length === 0 ? (
                    <p className="text-xs text-gray-400 text-center">
                      No slots
                    </p>
                  ) : (
                    daySlots.map((slot, slotIdx) => (
                      <div
                        key={slot.id || slotIdx}
                        className={`text-xs p-2 rounded ${
                          slot.is_booked
                            ? 'bg-red-100 text-red-700'
                            : 'bg-green-100 text-green-700'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium">
                              {formatTime(slot.start_time)}
                            </p>
                            <p className="text-[10px]">
                              {formatTime(slot.end_time)}
                            </p>
                          </div>
                          {editable && slot.id && !slot.is_booked && (
                            <button
                              onClick={() => deleteSlot(slot.id!)}
                              className="text-red-600 hover:text-red-800"
                              title="Delete"
                            >
                              ×
                            </button>
                          )}
                        </div>
                        {slot.is_booked && (
                          <p className="text-[10px] mt-1">Booked</p>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Recurring Slots Summary */}
      {editable && slots.some(s => s.day_of_week !== null) && (
        <Card>
          <h3 className="text-lg font-bold text-gray-900 mb-3">
            Recurring Availability
          </h3>
          <div className="space-y-2">
            {daysOfWeek.map((day, idx) => {
              const daySlots = slots.filter(s => s.day_of_week === idx && s.is_available);
              if (daySlots.length === 0) return null;

              return (
                <div key={idx} className="flex items-center gap-3">
                  <span className="font-medium text-gray-700 w-24">{day}:</span>
                  <div className="flex flex-wrap gap-2">
                    {daySlots.map((slot, slotIdx) => (
                      <span
                        key={slot.id || slotIdx}
                        className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-2"
                      >
                        {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                        {slot.id && (
                          <button
                            onClick={() => deleteSlot(slot.id!)}
                            className="hover:text-red-600"
                          >
                            ×
                          </button>
                        )}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Add Availability Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">
                Add Availability
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              {/* Recurring Toggle */}
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="recurring"
                  checked={newSlot.isRecurring}
                  onChange={(e) => setNewSlot({ ...newSlot, isRecurring: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <label htmlFor="recurring" className="text-sm font-medium text-gray-700">
                  Recurring (every week)
                </label>
              </div>

              {/* Day Selection */}
              {newSlot.isRecurring ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Day of Week
                  </label>
                  <select
                    value={newSlot.dayOfWeek}
                    onChange={(e) => setNewSlot({ ...newSlot, dayOfWeek: Number(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {daysOfWeek.map((day, idx) => (
                      <option key={idx} value={idx}>{day}</option>
                    ))}
                  </select>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Specific Date
                  </label>
                  <input
                    type="date"
                    value={newSlot.specificDate}
                    onChange={(e) => setNewSlot({ ...newSlot, specificDate: e.target.value })}
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}

              {/* Time Range */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Time
                  </label>
                  <input
                    type="time"
                    value={newSlot.startTime}
                    onChange={(e) => setNewSlot({ ...newSlot, startTime: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Time
                  </label>
                  <input
                    type="time"
                    value={newSlot.endTime}
                    onChange={(e) => setNewSlot({ ...newSlot, endTime: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Timezone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Timezone
                </label>
                <input
                  type="text"
                  value={newSlot.timezone}
                  onChange={(e) => setNewSlot({ ...newSlot, timezone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="America/New_York"
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <Button
                  onClick={addAvailabilitySlot}
                  variant="primary"
                  disabled={!newSlot.isRecurring && !newSlot.specificDate}
                  className="flex-1"
                >
                  Add Slot
                </Button>
                <Button
                  onClick={() => setShowAddModal(false)}
                  variant="outline"
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

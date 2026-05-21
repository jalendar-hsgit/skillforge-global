import { useState, useEffect } from 'react';
import { Button } from './Button';
import { Card } from './Card';
import { Input } from './Input';

interface BookingFormProps {
  mentorId: number;
  mentorName: string;
  hourlyRate: number;
  onSuccess?: (sessionId: number) => void;
  onError?: (error: string) => void;
}

export function BookingForm({
  mentorId,
  mentorName,
  hourlyRate,
  onSuccess,
  onError
}: BookingFormProps) {
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [topic, setTopic] = useState('');
  const [description, setDescription] = useState('');
  const [duration, setDuration] = useState(60);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedDate || !selectedTime || !topic) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const scheduledAt = `${selectedDate}T${selectedTime}:00`;
      
      const response = await fetch('/api/v1x/mentors/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mentor_id: mentorId,
          scheduled_at: scheduledAt,
          topic,
          duration_minutes: duration,
          description: description || null
        }),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Booking failed');
      }

      const sessionData = await response.json();
      
      if (onSuccess && sessionData.id) {
        onSuccess(sessionData.id);
      }
    } catch (err: any) {
      const message = err.message || 'Booking failed';
      setError(message);
      onError?.(message);
    } finally {
      setLoading(false);
    }
  };

  // Get minimum date (tomorrow)
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDate = tomorrow.toISOString().split('T')[0];

  // Get maximum date (30 days from now)
  const maxDate = new Date();
  maxDate.setDate(maxDate.getDate() + 30);
  const maxDateStr = maxDate.toISOString().split('T')[0];

  return (
    <Card className="booking-form p-6 space-y-4">
      <h3 className="text-xl font-bold mb-4">Book with {mentorName}</h3>
      
      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        
        {/* Topic Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">
            What would you like to learn? *
          </label>
          <Input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Python basics, Resume review, Algorithm practice"
            required
          />
        </div>

        {/* Date Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Preferred Date *
          </label>
          <Input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            min={minDate}
            max={maxDateStr}
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Select a date within the next 30 days
          </p>
        </div>

        {/* Time Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Preferred Time *
          </label>
          <Input
            type="time"
            value={selectedTime}
            onChange={(e) => setSelectedTime(e.target.value)}
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Mentor is available 9:00 AM - 5:00 PM
          </p>
        </div>

        {/* Duration Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Session Duration
          </label>
          <select
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={30}>30 minutes</option>
            <option value={60}>60 minutes (Recommended)</option>
            <option value={90}>90 minutes</option>
            <option value={120}>2 hours</option>
          </select>
        </div>

        {/* Description (Optional) */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Additional Details (Optional)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Tell the mentor what you'd like to focus on..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
        </div>

        {/* Price Display */}
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-md">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600">Session Cost</p>
              <p className="text-2xl font-bold text-blue-600">
                ${(hourlyRate * (duration / 60)).toFixed(2)}
              </p>
            </div>
            <div className="text-right text-sm text-gray-600">
              <p>${hourlyRate}/hour</p>
              <p>{duration} minutes</p>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50"
        >
          {loading ? 'Booking...' : 'Confirm Booking'}
        </Button>

        <p className="text-xs text-gray-500 text-center">
          A confirmation email will be sent once the mentor accepts your booking.
        </p>
      </form>
    </Card>
  );
}

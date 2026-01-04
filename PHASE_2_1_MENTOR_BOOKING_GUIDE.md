# PHASE 2.1 - MENTOR BOOKING FRONTEND IMPLEMENTATION GUIDE

**Estimated Time**: 3 hours  
**Status**: Ready to Start  
**Difficulty**: Medium  
**Dependencies**: Phase 1 Complete (✅), Backend mentor endpoints tested ✅

---

## Overview

Phase 2.1 focuses on **completing the mentor booking flow** - allowing users to:
1. View available mentors and their availability
2. Select date/time from mentor availability slots
3. Create a booking and see confirmation
4. View their upcoming and past bookings

This is the highest-impact feature for MVP (blocks course purchases, blocks community reputation).

---

## Architecture

### Frontend Components to Build

```
src/pages/mentors/[id].tsx         (exists - add booking form)
src/pages/mentors/[id]/book.tsx    (NEW - booking confirmation)
src/components/BookingForm.tsx     (NEW - core booking widget)
src/components/AvailabilityGrid.tsx (NEW - calendar-like display)
src/components/BookingSuccess.tsx  (NEW - confirmation page)
```

### API Integration Points

**Existing (Phase 1 tested):**
- `GET /api/v1x/mentors`  - List mentors ✅
- `GET /api/v1x/mentors/{id}` - Get mentor details
- `GET /api/v1x/mentors/{id}/availability` - Get availability slots

**Need to verify/implement:**
- `POST /api/v1x/mentor-sessions/book` - Create booking (CRITICAL)
- `GET /api/v1x/mentor-sessions/my-sessions` - User's bookings
- `GET /api/v1x/mentor-sessions/{id}` - Session details

### Data Flow

```
Mentors Page [list all mentors]
    ↓
Mentor Detail [id].tsx [click mentor]
    ↓
BookingForm Component [select availability]
    ↓
POST /api/v1x/mentor-sessions/book [create booking]
    ↓
Booking Success Page [confirmation]
```

---

## Step 1: Verify API Endpoints Exist (15 minutes)

### 1.1 Check Backend Mentor Endpoints

```bash
# Test listing mentors
curl http://localhost:8001/api/v1x/mentors

# Test getting specific mentor
curl http://localhost:8001/api/v1x/mentors/1

# Test availability slots for mentor
curl http://localhost:8001/api/v1x/mentors/1/availability
```

**Expected Response for /api/v1x/mentors/1/availability:**
```json
[
  {
    "id": 1,
    "mentor_id": 1,
    "day_of_week": "Monday",
    "start_time": "09:00",
    "end_time": "17:00"
  },
  ...
]
```

### 1.2 Check Booking Endpoint

```bash
# Try creating a booking (might 404 if not implemented)
curl -X POST http://localhost:8001/api/v1x/mentor-sessions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "mentor_id": 1,
    "scheduled_at": "2026-01-10T14:00:00",
    "topic": "Python Basics",
    "duration_minutes": 60
  }'
```

**If endpoint doesn't exist**: Create simple FastAPI endpoint:
```python
@router.post("/mentor-sessions")
def create_mentor_session(
    session: MentorSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new mentor session booking"""
    # Implementation here
```

---

## Step 2: Build API Integration Layer (15 minutes)

### 2.1 Update `src/lib/api.ts`

Add these functions to your API client:

```typescript
// Get list of all mentors
export async function getMentors(filters?: {
  expertise?: string;
  minRating?: number;
  maxPrice?: number;
}) {
  const params = new URLSearchParams();
  if (filters?.expertise) params.append('expertise', filters.expertise);
  if (filters?.minRating) params.append('min_rating', String(filters.minRating));
  if (filters?.maxPrice) params.append('max_price', String(filters.maxPrice));
  
  return apiCall(`/mentors?${params.toString()}`);
}

// Get mentor details including reviews
export async function getMentor(mentorId: number) {
  return apiCall(`/mentors/${mentorId}`);
}

// Get available time slots for a mentor
export async function getMentorAvailability(mentorId: number) {
  return apiCall(`/mentors/${mentorId}/availability`);
}

// Book a mentor session
export async function bookMentorSession(booking: {
  mentor_id: number;
  scheduled_at: string;  // ISO 8601 format: "2026-01-10T14:00:00"
  topic: string;
  duration_minutes?: number;
}) {
  return apiCall('/mentor-sessions', {
    method: 'POST',
    body: JSON.stringify(booking)
  });
}

// Get user's bookings
export async function getMyMentorSessions() {
  return apiCall('/mentor-sessions/my-sessions');
}

// Cancel a session
export async function cancelMentorSession(sessionId: number) {
  return apiCall(`/mentor-sessions/${sessionId}`, {
    method: 'DELETE'
  });
}
```

---

## Step 3: Create Components (60 minutes)

### 3.1 BookingForm Component

**File:** `src/components/BookingForm.tsx`

```typescript
import { useState, useEffect } from 'react';
import { Button } from './Button';
import { Card } from './Card';
import { Input } from './Input';
import { bookMentorSession } from '@/lib/api';

interface AvailabilitySlot {
  id: number;
  day_of_week: string;
  start_time: string;
  end_time: string;
  mentor_id: number;
}

export interface BookingFormProps {
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
  const [availableSlots, setAvailableSlots] = useState<AvailabilitySlot[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [topic, setTopic] = useState('');
  const [duration, setDuration] = useState(60);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch availability slots
    fetchAvailability();
  }, [mentorId]);

  const fetchAvailability = async () => {
    try {
      const { data } = await fetch(
        `http://localhost:8001/api/v1x/mentors/${mentorId}/availability`
      ).then(r => r.json());
      setAvailableSlots(data || []);
    } catch (err) {
      setError('Failed to load availability');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedDate || !selectedTime || !topic) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const scheduledAt = `${selectedDate}T${selectedTime}:00`;
      
      const response = await bookMentorSession({
        mentor_id: mentorId,
        scheduled_at: scheduledAt,
        topic,
        duration_minutes: duration
      });

      if (onSuccess && response.data?.id) {
        onSuccess(response.data.id);
      }
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Booking failed';
      setError(message);
      onError?.(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="booking-form">
      <h3 className="text-xl font-bold mb-4">Book with {mentorName}</h3>
      
      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        
        {/* Topic Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">
            What would you like to learn?
          </label>
          <Input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Python basics, Resume review"
            required
          />
        </div>

        {/* Date Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Preferred Date
          </label>
          <Input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            required
          />
        </div>

        {/* Time Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Preferred Time
          </label>
          <Input
            type="time"
            value={selectedTime}
            onChange={(e) => setSelectedTime(e.target.value)}
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Mentor is available 9:00 AM - 5:00 PM (Check availability)
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
            className="w-full px-3 py-2 border rounded"
          >
            <option value={30}>30 minutes</option>
            <option value={60}>60 minutes (Recommended)</option>
            <option value={90}>90 minutes</option>
            <option value={120}>2 hours</option>
          </select>
        </div>

        {/* Price Display */}
        <div className="bg-blue-50 p-3 rounded">
          <p className="text-sm">
            <strong>Session Cost:</strong> ${(hourlyRate * (duration / 60)).toFixed(2)}
          </p>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={loading}
          className="w-full"
        >
          {loading ? 'Booking...' : 'Confirm Booking'}
        </Button>
      </form>
    </Card>
  );
}
```

### 3.2 AvailabilityGrid Component (Optional - for visual calendar)

**File:** `src/components/AvailabilityGrid.tsx`

```typescript
import { useState, useEffect } from 'react';

interface TimeSlot {
  time: string;
  available: boolean;
}

interface AvailabilityGridProps {
  mentorId: number;
  onSelectSlot: (date: string, time: string) => void;
}

export function AvailabilityGrid({ mentorId, onSelectSlot }: AvailabilityGridProps) {
  const [weeks, setWeeks] = useState<any[]>([]);
  const [selectedWeek, setSelectedWeek] = useState(0);

  // Generate next 4 weeks of availability
  useEffect(() => {
    const weeksData = [];
    const today = new Date();

    for (let w = 0; w < 4; w++) {
      const weekStart = new Date(today);
      weekStart.setDate(today.getDate() + (w * 7));

      const days = [];
      for (let d = 0; d < 7; d++) {
        const date = new Date(weekStart);
        date.setDate(weekStart.getDate() + d);
        
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        const dateStr = date.toISOString().split('T')[0];

        days.push({
          date: dateStr,
          dayName,
          times: generateTimeSlots() // 9 AM to 5 PM in 30-min intervals
        });
      }
      weeksData.push(days);
    }
    setWeeks(weeksData);
  }, [mentorId]);

  const generateTimeSlots = (): TimeSlot[] => {
    const slots: TimeSlot[] = [];
    for (let hour = 9; hour < 17; hour++) {
      slots.push({
        time: `${hour.toString().padStart(2, '0')}:00`,
        available: true
      });
      slots.push({
        time: `${hour.toString().padStart(2, '0')}:30`,
        available: true
      });
    }
    return slots;
  };

  if (weeks.length === 0) return <div>Loading...</div>;

  const currentWeek = weeks[selectedWeek];

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {weeks.map((_, idx) => (
          <button
            key={idx}
            onClick={() => setSelectedWeek(idx)}
            className={`px-3 py-2 text-sm rounded ${
              selectedWeek === idx
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200'
            }`}
          >
            Week {idx + 1}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-2">
        {currentWeek.map((day) => (
          <div key={day.date} className="border rounded p-2">
            <p className="font-bold text-center mb-2">
              {day.dayName}
              <br />
              {day.date}
            </p>
            <div className="space-y-1">
              {day.times.map((slot) => (
                <button
                  key={slot.time}
                  onClick={() => onSelectSlot(day.date, slot.time)}
                  disabled={!slot.available}
                  className={`text-xs px-2 py-1 rounded w-full ${
                    slot.available
                      ? 'bg-green-100 hover:bg-green-200 cursor-pointer'
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  {slot.time}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 3.3 BookingSuccess Component

**File:** `src/components/BookingSuccess.tsx`

```typescript
import { useRouter } from 'next/router';
import { Button } from './Button';
import { Card } from './Card';

export interface BookingSuccessProps {
  sessionId: number;
  mentorName: string;
  scheduledAt: string;
  topic: string;
  price: number;
}

export function BookingSuccess({
  sessionId,
  mentorName,
  scheduledAt,
  topic,
  price
}: BookingSuccessProps) {
  const router = useRouter();

  const date = new Date(scheduledAt);
  const formattedDate = date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric'
  });
  const formattedTime = date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <Card className="text-center space-y-6">
      <div className="text-6xl">✓</div>

      <h2 className="text-2xl font-bold">Booking Confirmed!</h2>

      <div className="bg-blue-50 p-4 rounded space-y-2">
        <p>
          <strong>Mentor:</strong> {mentorName}
        </p>
        <p>
          <strong>Topic:</strong> {topic}
        </p>
        <p>
          <strong>Date & Time:</strong> {formattedDate} at {formattedTime}
        </p>
        <p>
          <strong>Cost:</strong> ${price.toFixed(2)}
        </p>
        <p className="text-xs text-gray-600">
          <strong>Session ID:</strong> {sessionId}
        </p>
      </div>

      <div className="space-y-3">
        <p className="text-gray-600">
          You'll receive a confirmation email with meeting details.
        </p>

        <div className="flex gap-3 justify-center">
          <Button
            onClick={() => router.push('/mentors')}
            variant="outline"
          >
            Back to Mentors
          </Button>
          <Button
            onClick={() => router.push('/dashboard')}
          >
            Go to Dashboard
          </Button>
        </div>
      </div>
    </Card>
  );
}
```

---

## Step 4: Build Mentor Detail Page with Booking (45 minutes)

### 4.1 Update Mentor Detail Page

**File:** `src/pages/mentors/[id].tsx`

Add booking section to the existing mentor detail page (around line 100-150):

```typescript
import { useState } from 'react';
import { BookingForm } from '@/components/BookingForm';

export default function MentorDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const [mentor, setMentor] = useState<any>(null);
  const [bookingSuccess, setBookingSuccess] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);

  // ... existing code to fetch mentor ...

  const handleBookingSuccess = (newSessionId: number) => {
    setSessionId(newSessionId);
    setBookingSuccess(true);
  };

  if (bookingSuccess && sessionId) {
    return (
      <Layout>
        <BookingSuccess
          sessionId={sessionId}
          mentorName={mentor.user?.full_name || 'Mentor'}
          scheduledAt={new Date().toISOString()} // Get from response
          topic="Booking confirmed"
          price={mentor.hourly_rate}
        />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="grid grid-cols-3 gap-8">
        {/* Left: Mentor info (existing) */}
        <div className="col-span-2">
          {/* existing mentor details */}
        </div>

        {/* Right: Booking form */}
        <div>
          <BookingForm
            mentorId={parseInt(id as string)}
            mentorName={mentor?.user?.full_name || 'Mentor'}
            hourlyRate={mentor?.hourly_rate || 0}
            onSuccess={handleBookingSuccess}
          />
        </div>
      </div>
    </Layout>
  );
}
```

---

## Step 5: Add User Sessions Display (30 minutes)

### 5.1 Create User Sessions Page

**File:** `src/pages/mentors/my-sessions.tsx`

```typescript
import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { getMyMentorSessions, cancelMentorSession } from '@/lib/api';

interface Session {
  id: number;
  mentor_id: number;
  mentor_name: string;
  scheduled_at: string;
  topic: string;
  status: string;
  price: number;
  duration_minutes: number;
}

export default function MySessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await getMyMentorSessions();
      setSessions(response.data || []);
    } catch (err) {
      console.error('Failed to load sessions', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (sessionId: number) => {
    if (!confirm('Cancel this booking?')) return;

    try {
      await cancelMentorSession(sessionId);
      setSessions(sessions.filter(s => s.id !== sessionId));
    } catch (err) {
      console.error('Failed to cancel', err);
    }
  };

  return (
    <Layout title="My Mentor Sessions">
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Scheduled Sessions</h1>

        {loading ? (
          <p>Loading...</p>
        ) : sessions.length === 0 ? (
          <Card>
            <p>No sessions booked yet.</p>
            <Button onClick={() => router.push('/mentors')}>
              Find a Mentor
            </Button>
          </Card>
        ) : (
          sessions.map(session => (
            <Card key={session.id} className="space-y-3">
              <div className="flex justify-between">
                <div>
                  <h3 className="font-bold">{session.mentor_name}</h3>
                  <p className="text-gray-600">{session.topic}</p>
                  <p className="text-sm text-gray-500">
                    {new Date(session.scheduled_at).toLocaleString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-bold">${session.price.toFixed(2)}</p>
                  <p className="text-sm text-gray-600">
                    {session.duration_minutes} mins
                  </p>
                  <span className={`inline-block mt-2 px-2 py-1 rounded text-xs ${
                    session.status === 'PENDING' ? 'bg-yellow-100' :
                    session.status === 'COMPLETED' ? 'bg-green-100' :
                    'bg-gray-100'
                  }`}>
                    {session.status}
                  </span>
                </div>
              </div>

              {session.status === 'PENDING' && (
                <Button
                  variant="outline"
                  onClick={() => handleCancel(session.id)}
                  className="w-full"
                >
                  Cancel Booking
                </Button>
              )}
            </Card>
          ))
        )}
      </div>
    </Layout>
  );
}
```

---

## Testing Checklist

- [ ] Backend endpoints return correct data
  - [ ] `GET /api/v1x/mentors` returns mentor list
  - [ ] `GET /api/v1x/mentors/{id}` returns detail
  - [ ] `GET /api/v1x/mentors/{id}/availability` returns slots
  - [ ] `POST /api/v1x/mentor-sessions` creates booking

- [ ] Frontend components display correctly
  - [ ] Mentor listing page loads
  - [ ] Mentor detail page shows booking form
  - [ ] BookingForm validates input
  - [ ] Date/time selection works

- [ ] Booking flow works end-to-end
  - [ ] Select mentor
  - [ ] Choose date/time
  - [ ] Submit booking
  - [ ] See success confirmation
  - [ ] Session appears in "My Sessions"

- [ ] Error handling
  - [ ] Invalid input shows error
  - [ ] API errors display properly
  - [ ] Network errors handled

---

## Files to Create/Modify

| File | Status | Lines |
|------|--------|-------|
| `src/lib/api.ts` | Modify | +50 |
| `src/components/BookingForm.tsx` | Create | 150 |
| `src/components/AvailabilityGrid.tsx` | Create | 120 |
| `src/components/BookingSuccess.tsx` | Create | 70 |
| `src/pages/mentors/[id].tsx` | Modify | +40 |
| `src/pages/mentors/my-sessions.tsx` | Create | 120 |

**Total New Code**: ~650 lines

---

## Success Criteria

✅ Users can view all mentors with availability  
✅ Users can select date/time from calendar  
✅ Booking creates session in database  
✅ Confirmation page shows booking details  
✅ Users can see their upcoming bookings  
✅ Users can cancel bookings  
✅ All API responses are correct format  

---

## Estimated Timeline

- 15 min: API verification
- 15 min: API integration layer  
- 60 min: Component development
- 45 min: Page implementation
- 30 min: Testing & fixes

**Total: 3 hours**

---

## Next Phase (2.2)

Once booking is complete, move to:
- **Course Purchase System** (3 hours)
- **Marketplace Order System** (3 hours)  
- **Full Dashboard Integration** (2 hours)

---

**Start here**: First, verify the backend mentor endpoints are working by testing them with curl. Then build the API layer in `src/lib/api.ts`.

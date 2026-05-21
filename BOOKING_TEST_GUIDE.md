# Session Booking Quick Test Guide

## Setup
1. Ensure backend is running: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001`
2. Ensure frontend is running: `npm run dev` (from root)
3. Database should have mentors seeded (run `python backend/seed_mentors.py` if needed)

## Test Flow

### Step 1: Login
- Navigate to `/login`
- Login with any student account (or create one)
- Or use email: `student1@test.com` password: `password123`

### Step 2: Browse Mentors
- Navigate to `/mentors`
- Click on any mentor card
- Should see: Mentor profile with bio, skills, rating, reviews

### Step 3: Check Availability
- Look for "Available Slots" section
- Should show a calendar or list of available times
- Each slot should have:
  - ✅ Full date (e.g., "Monday, January 15, 2024")
  - ✅ Time range (e.g., "2:00 PM - 3:00 PM")
  - ✅ Future dates only (no past dates)

### Step 4: Book Session
- Click "Book a Session" button
- Should see booking form with:
  - ✅ Time slot selector (8 slots shown)
  - ✅ Duration dropdown (30min, 1hr, 1.5hr, 2hr)
  - ✅ Topic input (min 5 characters)
  - ✅ Notes textarea (optional)
  - ✅ Booking summary on right (updates when slot selected)

### Step 5: Select Slot & Book
1. Click a time slot button
   - ✅ Button highlights (purple border)
   - ✅ Summary updates with:
     - Full date and time
     - Duration
     - Total cost
2. Enter session topic (e.g., "Learn FastAPI")
3. Optionally add notes
4. Click "Book Session" (or "Book & Pay" if mentor charges)

### Step 6: Confirm Booking
- ✅ Success message appears
- ✅ Redirected to dashboard after 2 seconds
- Or payment modal appears (if mentor hourly_rate > 0)

## What to Verify

### ✅ Availability Expansion
- Recurring slots (e.g., "Monday") should expand to multiple future dates
- Specific date slots should appear only once on that date
- All slots should be in the future (no past dates)

### ✅ Color Consistency
- No error styling with undefined colors
- Demo message uses `techBlue` (valid Tailwind color)
- Selection highlights use `forgePurple`

### ✅ Date/Time Formatting
- Dates: "Monday, January 15, 2024" (full format)
- Times: "2:00 PM", "2:00 PM - 4:00 PM" (12-hour format)

### ✅ Slot Selection
- Selected slot has purple border and background
- Unselected slots have neutral appearance
- Hover shows tech blue effect
- Summary updates correctly when slot changes

### ✅ Booking Submission
- Form validation works:
  - Can't submit without selecting slot (if slots available)
  - Can't submit without topic
  - Topic must be 5+ characters
- Booking creates session with correct `scheduled_at`

### ✅ Fallback Mode
- If mentor has NO availability:
  - Message shows: "Demo Mode: No availability slots found..."
  - Can still book (uses tomorrow 10:00 AM)
  - No slot selector shown
  - Fallback date shown in summary

## Expected Backend Responses

### GET /api/v1x/mentors/{id}/availability
```json
{
  "slots": [
    {
      "id": 1,
      "mentor_id": 1,
      "day_of_week": 0,           // Monday
      "date": null,               // Recurring slot
      "start_time": "09:00",
      "end_time": "12:00",
      "is_available": true,
      "is_booked": false,
      "timezone": "UTC"
    },
    {
      "id": 10,
      "mentor_id": 1,
      "day_of_week": null,        // Specific date
      "date": "2024-01-15T00:00:00Z",
      "start_time": "14:00",
      "end_time": "17:00",
      "is_available": true,
      "is_booked": false,
      "timezone": "UTC"
    }
  ]
}
```

### POST /api/v1x/mentors/sessions
Request:
```json
{
  "mentor_id": 1,
  "scheduled_at": "2024-01-15T14:00:00.000Z",
  "duration_minutes": 60,
  "topic": "Learn FastAPI",
  "description": "Help me understand async/await"
}
```

Response (201):
```json
{
  "id": 100,
  "mentor_id": 1,
  "student_id": 5,
  "topic": "Learn FastAPI",
  "description": "Help me understand async/await",
  "scheduled_at": "2024-01-15T14:00:00",
  "duration_minutes": 60,
  "status": "pending",
  "price": 85.00,
  "created_at": "2024-01-14T10:00:00"
}
```

## Troubleshooting

### No slots appear
- Check backend logs for availability fetch errors
- Verify mentors exist and are approved
- Ensure availability slots are seeded in database
- Check `is_available` field is true for slots

### Slots show but can't select
- Check browser console for JavaScript errors
- Verify slot object has `expanded_date` property
- Check Tailwind CSS is compiled (colors showing)

### Booking fails
- Check API endpoint responding with 200
- Verify topic is 5+ characters
- Check mentor exists and is approved
- Look for validation errors in response

### Payment modal doesn't appear
- Mentor's `hourly_rate` should be > 0
- Session `price` should be calculated correctly
- Check payment component is imported and rendered

## Files Changed
- `src/pages/mentors/[id]/book.tsx` - Availability expansion logic, color fixes, slot selection fix

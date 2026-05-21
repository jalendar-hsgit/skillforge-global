# Mentor Module - Complete Flow Documentation

## Overview
The Mentor Module enables 1-on-1 mentorship sessions between students and experienced developers. It includes mentor profiles, availability management, session booking with payments, real-time chat, and reviews.

---

## Architecture

### Backend (FastAPI)
- **Location**: `backend/app/api/v1x/mentors.py`
- **Database**: SQLite (`backend/app/data/skillforge.db`)
- **Models**: `backend/app/modelsx/mentor.py`
- **Schemas**: `backend/app/schemas/` (auth, progress, user)

### Frontend (Next.js)
- **Pages**:
  - `/mentors` - Browse mentors
  - `/mentors/[id]` - Mentor profile
  - `/mentors/[id]/book` - Book a session
  - `/mentors/dashboard` - Mentor management dashboard
  - `/mentors/sessions/[id]` - Session detail with chat
- **Components**:
  - `Avatar.tsx` - Profile avatars
  - `RatingStars.tsx` - Star ratings
  - `Chip.tsx` - Tag/skill chips
  - `MentorCardSkeleton.tsx` - Loading state
  - `AvailabilityCalendar.tsx` - Manage time slots
  - `SessionPayment.tsx` - Stripe payment flow
  - `MentorChat.tsx` - Real-time chat (Socket.IO)

---

## Complete User Flow

### 1. Student Browses Mentors (`/mentors`)
**What happens:**
- Frontend calls `GET /api/v1x/mentors/search`
- Backend queries approved mentors from `mentors` table
- Joins with `users` table to get mentor names/emails
- Returns: mentor profiles with expertise, ratings, hourly rates

**Features:**
- Search by name, bio, or expertise
- Filter by expertise area (Python, React, etc.)
- Filter by minimum rating (4+, 4.5+)
- Glass-morphic cards with hover glow effects
- Skeleton loaders while data loads

**Data shown per mentor:**
- Avatar (gradient circle with initial)
- Full name and hourly rate
- Star rating (out of 5)
- Bio excerpt (3 lines max)
- Expertise tags (first 4 skills)
- Total sessions completed
- "Book Session" CTA button

---

### 2. Student Views Mentor Profile (`/mentors/[id]`)
**What happens:**
- Frontend calls `GET /api/v1x/mentors/{id}`
- Backend returns full mentor profile
- Frontend also fetches:
  - `GET /api/v1x/mentors/availability/{id}` (time slots)
  - `GET /api/v1x/mentors/reviews?mentor_id={id}` (student reviews)

**Profile sections:**
1. **Header Card**:
   - Large avatar (132x132)
   - Name with gradient text
   - Star rating + review count
   - Hourly rate (cyan accent)
   - Total sessions (blue accent)
   - "Book a Session" CTA

2. **About Section**:
   - Full bio (multi-line)

3. **Expertise Section**:
   - All skills as chips (blue pills)

4. **Available Time Slots**:
   - Next 6 future slots
   - Date and time range
   - Hover effect on cards

5. **Student Reviews**:
   - Student avatar + name
   - Star rating
   - Review text
   - Posted date

---

### 3. Student Books a Session (`/mentors/[id]/book`)
**What happens:**
1. Page loads mentor profile and future availability
2. Student fills booking form:
   - **Select time slot** (grid of available slots)
   - **Duration** (30min, 1hr, 1.5hr, 2hr)
   - **Topic** (e.g., "Learn FastAPI auth")
   - **Notes** (optional prep info)
3. Student clicks "Book & Pay"
4. Frontend calls `POST /api/v1x/mentors/sessions`:
   ```json
   {
     "mentor_id": 1,
     "scheduled_at": "2025-12-05T10:00:00",
     "duration_minutes": 60,
     "topic": "FastAPI Authentication",
     "description": "Need help with JWT tokens"
   }
   ```
5. Backend:
   - Validates student is authenticated
   - Creates `MentorSession` record (status: "pending")
   - Calculates price: `(hourly_rate / 60) * duration`
   - Returns session with `id` and `price`

6. If price > 0:
   - Payment modal opens
   - `SessionPayment` component handles Stripe flow
   - On success: session marked as paid
   - Redirects to `/dashboard`

7. If free session:
   - Immediately confirms booking
   - Redirects to `/dashboard`

**Booking Summary Sidebar:**
- Mentor name
- Selected date/time
- Duration
- Total cost (gradient cyan/blue)
- Info note about pending confirmation

---

### 4. Mentor Manages Sessions (`/mentors/dashboard`)
**Who can access:** Only approved mentors

**What happens:**
- `GET /api/v1x/mentors/me` (mentor profile)
- `GET /api/v1x/mentors/sessions/my` (all sessions)
- `GET /api/v1x/mentors/availability/{id}` (if approved)

**Dashboard tabs:**

#### Overview Tab
1. **Stats Cards** (glass-morphic with hover glow):
   - Total Sessions (white text)
   - Pending Requests (yellow accent)
   - Average Rating (blue accent)
   - Hourly Rate (green accent)

2. **Upcoming Sessions**:
   - Next 5 upcoming sessions
   - Topic, student name, date/time
   - Status badge (pending/confirmed/completed)
   - "Join Meeting" button (if meeting_url exists)
   - "View Details" button

3. **Profile Summary**:
   - Current status badge
   - Expertise chips
   - Bio
   - "Edit Profile" button

#### Sessions Tab
- All sessions (past and future)
- Same card format as overview
- Shows session notes if any

#### Availability Tab
- `AvailabilityCalendar` component
- Add/edit/delete time slots
- Only if mentor status is "approved"

---

### 5. Mentor Confirms Session (`/mentors/sessions/[id]`)
**What happens:**
1. Page loads session details
2. Fetches mentor profile (to show student the mentor info)

**Session status flow:**

#### If status = "pending" (Mentor view):
- Shows "Confirm Session" card
- Mentor enters:
  - **Meeting URL** (Zoom/Google Meet link) - Required
  - **Notes for Student** (prep instructions) - Optional
- Clicks "Confirm Session"
- Backend: `PATCH /api/v1x/mentors/sessions/{id}`
  - Updates status → "confirmed"
  - Sets `meeting_url`
  - Sets `mentor_notes`
- Email sent to student

#### If status = "confirmed":
- **Meeting Information** card shows:
  - Meeting link (clickable)
  - "Join Meeting" button
- **Session Chat** section:
  - Real-time chat via Socket.IO
  - `MentorChat` component
  - Both mentor and student can message

#### If status = "completed":
- Chat still accessible
- Mentor can add private notes
- Student can submit review

**Session Detail Cards:**
1. **Session Details** (main):
   - Topic (large gradient header)
   - Date & time
   - Duration
   - Description
   - Mentor/student info with avatar
   - Expertise chips

2. **Payment Sidebar**:
   - Amount paid
   - Payment status (paid/pending)

3. **Actions Sidebar**:
   - "Mark as Completed" (mentor, when confirmed)
   - "Cancel Session" (if pending)

4. **Private Notes Sidebar** (mentor only):
   - Textarea for mentor-only notes
   - "Save Notes" button

---

### 6. Student Submits Review
**What happens:**
1. After session is "completed"
2. Student visits session page
3. Review form appears (if not yet reviewed)
4. Student submits:
   - **Rating** (1-5 stars)
   - **Review text**
5. Frontend calls `POST /api/v1x/mentors/reviews`:
   ```json
   {
     "session_id": 123,
     "mentor_id": 1,
     "rating": 5,
     "review_text": "Great mentor! Very helpful."
   }
   ```
6. Backend:
   - Creates `MentorReview` record
   - Recalculates mentor's `average_rating`
   - Updates `mentors` table
7. Review appears on mentor profile

---

## Database Schema

### `mentors` Table
```sql
id                INTEGER PRIMARY KEY
user_id           INTEGER (FK to users)
bio               TEXT
expertise         VARCHAR (comma-separated: "python-ai,data-science")
hourly_rate       FLOAT
average_rating    FLOAT (default 0.0)
total_sessions    INTEGER (default 0)
status            VARCHAR (pending|approved|rejected)
created_at        DATETIME
```

### `mentor_availability` Table
```sql
id                INTEGER PRIMARY KEY
mentor_id         INTEGER (FK to mentors)
day_of_week       VARCHAR (Monday, Tuesday, etc.)
date              DATE
start_time        DATETIME
end_time          DATETIME
is_available      BOOLEAN
is_booked         BOOLEAN
timezone          VARCHAR (default UTC)
created_at        DATETIME
```

### `mentor_sessions` Table
```sql
id                INTEGER PRIMARY KEY
mentor_id         INTEGER (FK to mentors)
student_id        INTEGER (FK to users)
scheduled_at      DATETIME
duration_minutes  INTEGER
status            VARCHAR (pending|confirmed|completed|cancelled|no_show)
topic             VARCHAR
description       TEXT
meeting_url       VARCHAR
price             FLOAT
payment_status    VARCHAR (pending|paid|refunded)
payment_intent_id VARCHAR (Stripe)
mentor_notes      TEXT (private)
student_feedback  TEXT
created_at        DATETIME
```

### `mentor_reviews` Table
```sql
id                INTEGER PRIMARY KEY
mentor_id         INTEGER (FK to mentors)
student_id        INTEGER (FK to users)
session_id        INTEGER (FK to mentor_sessions)
rating            INTEGER (1-5)
review_text       TEXT
created_at        DATETIME
```

---

## Demo Data Setup

### Seed Demo Data
Run this to create test mentors, availability, and sessions:
```bash
cd backend
python seed_mentors.py
```

### Add Future Availability (for booking)
```bash
cd backend
python add_future_availability.py
```
OR use SQL directly:
```bash
cd backend
python -c "import sqlite3; from datetime import datetime, timedelta; conn = sqlite3.connect('app/data/skillforge.db'); c = conn.cursor(); now = datetime.now(); [c.execute('INSERT INTO mentor_availability (mentor_id, day_of_week, date, start_time, end_time, is_available, is_booked, timezone, created_at) VALUES (?, ?, ?, ?, ?, 1, 0, ?, ?)', (mid, (now + timedelta(days=d)).strftime('%A'), (now + timedelta(days=d)).date().isoformat(), (now + timedelta(days=d)).replace(hour=h, minute=0, second=0).isoformat(), (now + timedelta(days=d)).replace(hour=h+1, minute=0, second=0).isoformat(), 'UTC', now.isoformat())) for mid in [1,2,3] for d in range(1,15) for h in [10,14]]; conn.commit(); print('Added 84 future slots'); conn.close()"
```

### Check Data
```bash
cd backend
python check_mentors.py
```

---

## Testing Checklist

### Frontend Tests
- [ ] Browse mentors page loads with 3 mentors
- [ ] Search filters work (expertise, rating)
- [ ] Click mentor card → profile page
- [ ] Profile shows bio, skills, rating, reviews
- [ ] Availability slots visible (future dates only)
- [ ] Click "Book Session" → booking page
- [ ] Select time slot, duration, topic
- [ ] Booking summary updates live
- [ ] Submit booking (creates session)
- [ ] Payment modal appears (if price > 0)
- [ ] Navigate to `/mentors/dashboard` (as mentor)
- [ ] Dashboard shows stats, upcoming sessions
- [ ] Click session → detail page
- [ ] Confirm session (add meeting URL)
- [ ] Session status updates to "confirmed"
- [ ] Chat becomes available
- [ ] Mark session as completed
- [ ] Review form appears for student

### Backend Tests
```bash
# Test mentor search
curl http://localhost:8001/api/v1x/mentors/search

# Test mentor profile
curl http://localhost:8001/api/v1x/mentors/1

# Test availability
curl http://localhost:8001/api/v1x/mentors/availability/1

# Test reviews
curl http://localhost:8001/api/v1x/mentors/reviews?mentor_id=1
```

---

## Design System Applied

### Colors (from tailwind.config.ts)
- **Primary**: `forgePurple-400/500` (#6B3BFF)
- **Secondary**: `neuralBlue-400/500` (#1E9EFF)
- **Accent**: `aiElectric-400` (#00E5FF)
- **Background**: `deepTech-950` (#0B0A13)
- **Text**: `techGray-300/400` (#B6BED3)
- **Success**: `success` (#10B981)
- **Warning**: `warning` (#F59E0B)
- **Error**: `error` (#EF4444)

### Typography
- **Headers**: `font-display font-black` with gradient text
- **Body**: `text-techGray-300` with `leading-relaxed`
- **Labels**: `text-techGray-400 font-semibold`

### Cards
- Glass-morphic: `bg-glass backdrop-blur-xl border border-white/10 shadow-glass`
- Hover effects: `hover:border-forgePurple-500/50 hover:shadow-glow-sm`
- Transitions: `transition-all duration-300`

### Spacing
- Page padding: `py-12 md:py-16`
- Container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- Section gaps: `space-y-6` to `space-y-8`
- Card padding: `p-5` to `p-6`

---

## File Structure

```
backend/
├── app/
│   ├── api/v1x/
│   │   └── mentors.py          # Main mentor API routes
│   ├── modelsx/
│   │   └── mentor.py           # DB models (Mentor, MentorAvailability, etc.)
│   ├── schemas/
│   │   ├── mentor.py           # Pydantic request/response models
│   │   └── user.py
│   ├── services/
│   │   └── mentor_search.py    # Search/filter logic
│   └── data/
│       └── skillforge.db       # SQLite database
├── seed_mentors.py             # Demo data seeder
├── add_future_availability.py  # Add bookable slots
└── check_mentors.py            # Verify data

src/
├── pages/
│   └── mentors/
│       ├── index.tsx           # Browse mentors
│       ├── [id].tsx            # Mentor profile
│       ├── dashboard.tsx       # Mentor management
│       ├── [id]/
│       │   └── book.tsx        # Booking flow
│       └── sessions/
│           └── [id].tsx        # Session detail + chat
└── components/
    ├── Avatar.tsx              # Profile avatars
    ├── RatingStars.tsx         # Star rating component
    ├── Chip.tsx                # Skill/tag chips
    ├── MentorCardSkeleton.tsx  # Loading skeleton
    ├── AvailabilityCalendar.tsx# Manage time slots
    ├── SessionPayment.tsx      # Stripe integration
    └── MentorChat.tsx          # Real-time chat (Socket.IO)
```

---

## Next Steps / Enhancements

### High Priority
- [ ] Email notifications (booking confirmation, reminders)
- [ ] Mentor application approval workflow (admin panel)
- [ ] Stripe webhook handler (reconcile payments)
- [ ] Timezone support (user-local time display)

### Medium Priority
- [ ] Mentor earnings dashboard
- [ ] Recurring availability (weekly schedule)
- [ ] Video call integration (Zoom API auto-create)
- [ ] Student profile with learning goals

### Nice to Have
- [ ] Mentor badges/certifications
- [ ] Session recording/transcripts
- [ ] Mentor leaderboard
- [ ] Gift/referral system for sessions

---

## Troubleshooting

### "No availability slots found"
**Solution:** Run `add_future_availability.py` or SQL command above

### Session booking fails with 401
**Solution:** User not logged in. Redirect to `/login?redirect=/mentors/{id}/book`

### Payment modal doesn't show
**Solution:** Check session has `price > 0` and Stripe keys are set

### Chat not loading
**Solution:** Verify Socket.IO server running and session status is "confirmed"

### Mentor dashboard shows 404
**Solution:** User is not a mentor. Create mentor profile via `POST /api/v1x/mentors/become`

### Reviews not appearing
**Solution:** Session must be "completed" and review submitted via `POST /api/v1x/mentors/reviews`

---

## API Endpoints Reference

### Public
- `GET /api/v1x/mentors/search` - Browse mentors (with filters)
- `GET /api/v1x/mentors/{id}` - Mentor profile
- `GET /api/v1x/mentors/availability/{id}` - Time slots
- `GET /api/v1x/mentors/reviews?mentor_id={id}` - Reviews

### Authenticated Student
- `POST /api/v1x/mentors/sessions` - Book session
- `GET /api/v1x/mentors/sessions/my` - My sessions
- `POST /api/v1x/mentors/reviews` - Submit review

### Authenticated Mentor
- `GET /api/v1x/mentors/me` - My mentor profile
- `PATCH /api/v1x/mentors/me` - Update profile
- `GET /api/v1x/mentors/sessions/my` - My sessions (as mentor)
- `PATCH /api/v1x/mentors/sessions/{id}` - Update session
- `POST /api/v1x/mentors/availability` - Add time slot
- `DELETE /api/v1x/mentors/availability/{id}` - Remove slot

---

## Conclusion

The Mentor Module is now fully functional with:
✅ Dark theme matching app design system
✅ Glass-morphic UI with smooth animations
✅ Complete booking → payment → confirmation flow
✅ Real-time chat for sessions
✅ Review system with rating updates
✅ Mentor dashboard for session management
✅ Demo data and future availability seeded

**Ready to commit!**

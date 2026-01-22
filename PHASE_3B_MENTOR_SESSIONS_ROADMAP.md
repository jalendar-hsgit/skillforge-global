# Phase 3B: Mentor Session Management System

## Overview
Build complete mentor session booking, scheduling, and feedback system.

## Architecture

### Database Models (Backend)

#### 1. MentorAvailability (if not complete)
- `id`: Primary key
- `mentor_id`: Foreign key to Mentor
- `day_of_week`: 0-6 (Monday-Sunday)
- `start_time`: Time slot start (HH:MM)
- `end_time`: Time slot end (HH:MM)
- `is_available`: Boolean (can toggle on/off)
- `created_at`, `updated_at`: Timestamps

#### 2. MentorSession (enhance existing)
- `id`: Primary key
- `mentor_id`: Foreign key to Mentor
- `student_id`: Foreign key to User
- `topic`: String (session topic)
- `scheduled_at`: DateTime (when session happens)
- `duration_minutes`: Integer (30, 60, 90 min)
- `status`: Enum (PENDING, CONFIRMED, COMPLETED, CANCELLED)
- `price`: Decimal (session rate)
- `notes`: Text (session notes from mentor)
- `cancellation_reason`: Text (if cancelled)
- `created_at`, `updated_at`: Timestamps

#### 3. SessionFeedback (NEW)
- `id`: Primary key
- `session_id`: Foreign key to MentorSession
- `rating_mentor`: Integer (1-5 stars) - student rates mentor
- `rating_session`: Integer (1-5 stars) - session quality
- `mentor_feedback`: Text - mentor feedback to student
- `student_feedback`: Text - student feedback to mentor
- `mentor_submitted`: Boolean (mentor submitted feedback)
- `student_submitted`: Boolean (student submitted feedback)
- `created_at`, `updated_at`: Timestamps

### API Endpoints (Backend)

#### Mentor Availability
1. `GET /api/v1x/mentor-sessions/my-availability` - Get mentor's availability
2. `POST /api/v1x/mentor-sessions/availability` - Create availability slot
3. `PUT /api/v1x/mentor-sessions/availability/{id}` - Update availability
4. `DELETE /api/v1x/mentor-sessions/availability/{id}` - Delete availability

#### Session Booking
5. `GET /api/v1x/mentor-sessions/available-slots/{mentor_id}` - Get available slots
6. `POST /api/v1x/mentor-sessions/book` - Book a session
7. `GET /api/v1x/mentor-sessions/my-sessions` - Get student/mentor sessions
8. `PATCH /api/v1x/mentor-sessions/{id}/confirm` - Confirm session (mentor)
9. `PATCH /api/v1x/mentor-sessions/{id}/cancel` - Cancel session

#### Feedback
10. `POST /api/v1x/mentor-sessions/{id}/feedback` - Submit feedback
11. `GET /api/v1x/mentor-sessions/{id}/feedback` - Get feedback for session
12. `GET /api/v1x/mentors/{mentor_id}/ratings` - Get mentor's ratings

### Frontend Pages

#### Mentor Dashboard
1. **Availability Manager** (`/mentor/availability`)
   - Weekly calendar view
   - Add/edit/delete availability slots
   - Bulk operations (e.g., "Set Mon-Fri 9-5")
   - Toggle availability on/off

2. **Session Management** (`/mentor/sessions`)
   - List of scheduled sessions
   - Upcoming sessions
   - Completed sessions
   - Session details modal
   - Confirm/cancel session buttons
   - Mark as completed

3. **Feedback & Ratings** (`/mentor/feedback`)
   - Sessions awaiting feedback
   - Give feedback to students
   - View student feedback
   - Rating history
   - Average rating display

#### Student Pages
4. **Session Booking** (`/student/book-session/{mentor_id}`)
   - Mentor profile & availability
   - Calendar with available slots
   - Session duration selector (30/60/90 min)
   - Topic input
   - Booking confirmation

5. **My Sessions** (`/student/sessions`)
   - Upcoming sessions
   - Past sessions
   - Session reminders
   - Cancel/reschedule options
   - Leave feedback (if completed)

6. **Mentor Selection** (`/student/find-mentors`)
   - List all available mentors
   - Filter by expertise
   - Sort by rating/price
   - View mentor profiles
   - Quick book button

## Implementation Plan

### Phase 3B.1: Backend Models & Schemas (Today)
- [ ] Create SessionFeedback model
- [ ] Create/update Pydantic schemas
- [ ] Register models in main.py
- [ ] Initialize database

### Phase 3B.2: Backend API Endpoints (Today/Next)
- [ ] Availability CRUD (4 endpoints)
- [ ] Session booking endpoints (7 endpoints)
- [ ] Feedback endpoints (3 endpoints)
- [ ] Comprehensive error handling
- [ ] Permission checks

### Phase 3B.3: Frontend Pages (Next)
- [ ] Mentor availability manager
- [ ] Session booking calendar
- [ ] Session management dashboard
- [ ] Feedback submission forms

### Phase 3B.4: Frontend Components
- [ ] Calendar widget
- [ ] Availability selector
- [ ] Session card component
- [ ] Rating/feedback component

### Phase 3B.5: Demo Data & Testing
- [ ] Seed availability slots (all mentors)
- [ ] Seed sessions (mix of statuses)
- [ ] Seed feedback/ratings
- [ ] End-to-end testing

## Feature Details

### Availability Management
- Mentors set their weekly availability (repeating slots)
- Toggle availability on/off
- Support for time zones
- Bulk operations (e.g., copy previous week)

### Session Booking
- Students see mentor availability calendar
- Select date/time and duration
- Confirm booking details
- Mentor receives notification
- Mentor accepts/rejects in 24h

### Session Management
- Countdown timer before session
- Mark as completed when done
- Automatic status updates
- Session reminders (email/notifications)

### Feedback System
- Both mentor and student can leave feedback
- 5-star ratings
- Text feedback
- Feedback visible after both submitted
- Average rating calculation

## Demo Data to Seed

**Availability Slots**: 
- Each mentor: Mon-Fri 9am-5pm (slots every hour)
- 4 mentors × 45 slots = 180 availability records

**Sessions**:
- 8 completed sessions (with feedback)
- 4 upcoming sessions (pending/confirmed)
- 2 cancelled sessions

**Feedback**:
- 8 feedback records (from completed sessions)
- Mix of ratings (3-5 stars)

## Success Criteria

✅ Mentor can set and manage availability
✅ Student can see available slots and book
✅ Mentor can confirm/cancel sessions
✅ Both can leave feedback and ratings
✅ Ratings update mentor profile
✅ Demo data loads and displays correctly
✅ All pages compile and render
✅ Full end-to-end workflow works

## Timeline

- **Phase 3B.1**: 1-2 hours (models, schemas, API)
- **Phase 3B.2**: 2-3 hours (endpoints, logic)
- **Phase 3B.3-4**: 2-3 hours (frontend)
- **Phase 3B.5**: 1-2 hours (testing, fixes)

**Total**: ~6-10 hours for complete Phase 3B

---

**Ready to start Phase 3B.1? Let's build the backend models and schemas!**

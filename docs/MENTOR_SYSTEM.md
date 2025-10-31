# v1.2.0 Mentor System Documentation

## Overview

The Mentor System allows users who have demonstrated expertise (completed learning paths with high quiz scores) to become mentors and help other students. This creates a community-driven learning ecosystem.

## Architecture

### Backend (FastAPI)

#### Database Models (`backend/app/modelsx/mentor.py`)
- **Mentor**: Profiles for mentors (bio, expertise, hourly_rate, ratings)
- **MentorSession**: Bookings between students and mentors
- **MentorAvailability**: Time slots when mentors are available
- **MentorMessage**: Chat messages for real-time communication
- **MentorReview**: Student feedback after sessions

#### API Endpoints (`backend/app/api/v1x/mentors.py`)

##### Eligibility & Application
- `GET /api/v1x/mentors/eligibility` - Check if user can become mentor
  - Requires: 1+ completed path AND 80%+ average quiz score
- `POST /api/v1x/mentors/apply` - Apply to become mentor
  - Body: `{ bio, expertise[], hourly_rate }`
  - Creates mentor profile with `status: "pending"`

##### Profile Management
- `GET /api/v1x/mentors/me` - Get own mentor profile
- `PATCH /api/v1x/mentors/me` - Update profile
- `GET /api/v1x/mentors/{id}` - Get mentor by ID (public)

##### Search
- `GET /api/v1x/mentors/search` - Search mentors
  - Query params: `expertise`, `min_rating`, `max_price`
  - Returns only approved mentors

##### Session Booking
- `POST /api/v1x/mentors/sessions` - Book session
  - Body: `{ mentor_id, start_time, duration_minutes, topic, notes }`
  - Creates session with `status: "pending"`
- `GET /api/v1x/mentors/sessions/my` - Get user's sessions
- `PATCH /api/v1x/mentors/sessions/{id}` - Update session status
  - Mentor can confirm/complete/cancel

##### Availability Management
- `POST /api/v1x/mentors/availability` - Add availability slot
  - Body: `{ start_time, end_time }`
- `GET /api/v1x/mentors/availability/{mentor_id}` - Get mentor's availability

##### Reviews
- `POST /api/v1x/mentors/reviews` - Submit review
  - Body: `{ session_id, rating, comment }`
  - Can only review completed sessions
- `GET /api/v1x/mentors/reviews/{mentor_id}` - Get mentor reviews

#### Business Logic (`backend/app/services/mentor_service.py`)

##### MentorEligibilityService
```python
def check_eligibility(user_id: int, db: Session) -> dict:
    # Check completed paths
    # Calculate quiz average
    # Return { eligible: bool, requirements: {...}, reasons: [] }
```

##### MentorSearchService
```python
def search_mentors(
    expertise: Optional[str],
    min_rating: Optional[float],
    max_price: Optional[float],
    db: Session
) -> List[Mentor]:
    # Filter by expertise (case-insensitive, partial match)
    # Filter by rating >= min_rating
    # Filter by hourly_rate <= max_price
    # Return only approved mentors
```

##### SessionManagementService
```python
def validate_booking(mentor_id, start_time, duration, db):
    # Check mentor exists and is approved
    # Check no conflicting bookings
    # Return validation result

def generate_meeting_url(session_id):
    # TODO: Integrate Zoom/Google Meet API
    # Currently returns placeholder URL
```

### Frontend (Next.js)

#### Pages

##### `/mentors` - Mentor Listing
- Browse all approved mentors
- Search by name/expertise
- Filter by expertise, rating, max price
- Click mentor card → view profile

##### `/mentors/[id]` - Mentor Profile
- View mentor details (bio, expertise, rating, reviews)
- See available time slots
- Click "Book Session" → booking page

##### `/mentors/become` - Become a Mentor
- Check eligibility (auto-checks on page load)
- Application form:
  - Bio (min 100 characters)
  - Expertise (select from list + custom)
  - Hourly rate ($20-$200 slider)
- Shows eligibility requirements if not eligible

##### `/mentors/dashboard` - Mentor Dashboard
- Overview tab: Stats + upcoming sessions
- Sessions tab: All sessions (pending/confirmed/completed)
- Availability tab: Manage time slots
- Profile summary with edit button

##### `/mentors/[id]/book` - Book Session
- Select from available time slots (calendar grid)
- Choose duration (30min, 1hr, 1.5hr, 2hr)
- Enter topic and notes
- See cost calculation (hourly_rate * duration/60)
- Submit booking (status: pending)

## User Flows

### Becoming a Mentor

1. **Student completes requirements**
   - Completes at least 1 learning path
   - Maintains 80%+ average on quizzes

2. **Apply to become mentor**
   - Visit `/mentors/become`
   - System checks eligibility automatically
   - If eligible: Fill application form
   - If not eligible: See progress toward requirements

3. **Application review** (manual step)
   - Admin reviews application
   - Updates `status` to "approved" or "rejected"

4. **Set availability**
   - Once approved, mentor adds time slots
   - POST `/api/v1x/mentors/availability`

### Booking a Session

1. **Browse mentors**
   - Student visits `/mentors`
   - Searches/filters to find suitable mentor

2. **View profile**
   - Click mentor card → `/mentors/{id}`
   - Read bio, reviews, see availability

3. **Book session**
   - Click "Book Session" → `/mentors/{id}/book`
   - Select time slot from calendar
   - Choose duration
   - Enter topic and notes
   - Submit (creates session with status: "pending")

4. **Mentor confirms**
   - Mentor sees pending booking in dashboard
   - PATCH `/api/v1x/mentors/sessions/{id}` with `status: "confirmed"`
   - Meeting URL generated (placeholder for now)

5. **Session happens**
   - Both parties receive meeting link
   - Join at scheduled time

6. **Complete & review**
   - After session, mentor marks as "completed"
   - Student can submit review (rating + comment)

## Testing

### Backend Tests (`backend/tests/test_mentor_simple.py`)

19 test cases covering:
- Authentication requirements
- Eligibility checks
- Application flow
- Profile management
- Search functionality
- Session booking
- Availability management
- Review submission

Run tests:
```powershell
cd backend
pytest tests/test_mentor_simple.py -v
```

## Database Schema

### mentors
```sql
id INTEGER PRIMARY KEY
user_id INTEGER FOREIGN KEY → users.id
bio TEXT
expertise JSON (array of strings)
hourly_rate FLOAT
status VARCHAR (pending/approved/rejected)
average_rating FLOAT
total_sessions INTEGER
created_at TIMESTAMP
updated_at TIMESTAMP
```

### mentor_sessions
```sql
id INTEGER PRIMARY KEY
mentor_id INTEGER FOREIGN KEY → mentors.id
student_id INTEGER FOREIGN KEY → users.id
start_time TIMESTAMP
end_time TIMESTAMP
duration_minutes INTEGER
status VARCHAR (pending/confirmed/completed/cancelled)
topic VARCHAR
notes TEXT
meeting_url VARCHAR
created_at TIMESTAMP
```

### mentor_availability
```sql
id INTEGER PRIMARY KEY
mentor_id INTEGER FOREIGN KEY → mentors.id
start_time TIMESTAMP
end_time TIMESTAMP
is_available BOOLEAN
```

### mentor_messages
```sql
id INTEGER PRIMARY KEY
session_id INTEGER FOREIGN KEY → mentor_sessions.id
sender_id INTEGER FOREIGN KEY → users.id
content TEXT
created_at TIMESTAMP
```

### mentor_reviews
```sql
id INTEGER PRIMARY KEY
session_id INTEGER FOREIGN KEY → mentor_sessions.id
mentor_id INTEGER FOREIGN KEY → mentors.id
student_id INTEGER FOREIGN KEY → users.id
rating INTEGER (1-5)
comment TEXT
created_at TIMESTAMP
```

## Next Steps (Future Enhancements)

### 1. Real-time Chat (WebSocket)
- Install `python-socketio`
- Create WebSocket endpoints
- Frontend: Socket.io client
- Enable messaging during sessions

### 2. Video Integration
- **Option A: Zoom API**
  - Create meetings programmatically
  - Get join URLs for both parties
- **Option B: Google Meet API**
  - Generate meeting links via Calendar API
- **Option C: Jitsi** (open-source)
  - Embedded video calling

### 3. Payment Processing
- **Stripe Integration**
  - Create PaymentIntent before session
  - Hold funds until session completed
  - Transfer to mentor (minus platform fee)
- **Flow:**
  1. Student books → creates Stripe PaymentIntent
  2. Student confirms payment → funds held
  3. Session completes → funds released to mentor
  4. Refund policy for cancellations

### 4. Notifications
- Email notifications for:
  - Booking requests (mentor)
  - Booking confirmations (student)
  - Session reminders (both)
  - Review requests (student)
- Optional SMS via Twilio

### 5. Admin Panel
- Review pending mentor applications
- Approve/reject with comments
- View all sessions
- Handle disputes

## Configuration

### Environment Variables
```bash
# Already configured in backend/app/core/config.py
DATABASE_URL=sqlite:///./skillforge.db
JWT_SECRET=your-secret-key
FRONTEND_ORIGIN=http://localhost:3000

# Future additions
ZOOM_API_KEY=...
ZOOM_API_SECRET=...
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
```

## API Examples

### Check Eligibility
```bash
curl -X GET http://localhost:8001/api/v1x/mentors/eligibility \
  -H "Cookie: token=<jwt-token>"
```

Response:
```json
{
  "eligible": true,
  "requirements": {
    "completed_paths": 2,
    "quiz_average": 87.5
  },
  "reasons": []
}
```

### Apply to Become Mentor
```bash
curl -X POST http://localhost:8001/api/v1x/mentors/apply \
  -H "Content-Type: application/json" \
  -H "Cookie: token=<jwt-token>" \
  -d '{
    "bio": "I have 5 years of Python experience...",
    "expertise": ["Python", "FastAPI", "Docker"],
    "hourly_rate": 60.0
  }'
```

### Search Mentors
```bash
curl -X GET "http://localhost:8001/api/v1x/mentors/search?expertise=Python&min_rating=4.0"
```

### Book Session
```bash
curl -X POST http://localhost:8001/api/v1x/mentors/sessions \
  -H "Content-Type: application/json" \
  -H "Cookie: token=<jwt-token>" \
  -d '{
    "mentor_id": 1,
    "start_time": "2025-11-01T14:00:00Z",
    "duration_minutes": 60,
    "topic": "Learn FastAPI Authentication",
    "notes": "Need help implementing JWT"
  }'
```

## Deployment Checklist

- [x] Database migrations run
- [x] Backend tests passing
- [x] Frontend pages created
- [ ] WebSocket server configured
- [ ] Video integration API keys
- [ ] Payment gateway configured
- [ ] Email service configured
- [ ] Admin approval workflow tested
- [ ] Load testing completed

## Git History

```bash
# v1.2.0 Mentor System Commits
7d2d0fc - feat(mentors): add session booking page
e2a5328 - test(mentors): add comprehensive test suite
93038e6 - feat(mentors): add backend API, models, services, and frontend UI

# View changes
git log --oneline --grep="mentors"
```

## Support

For questions or issues with the mentor system:
1. Check API logs: `backend/app/main.py`
2. Review test cases: `backend/tests/test_mentor_simple.py`
3. Inspect database: `sqlite3 skillforge.db`
4. Frontend console: Browser DevTools

## Metrics to Track

- Total mentors (approved)
- Total sessions (completed)
- Average mentor rating
- Booking conversion rate
- Session completion rate
- Revenue (if payments enabled)

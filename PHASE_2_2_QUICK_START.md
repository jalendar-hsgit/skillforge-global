# Phase 2.2: Quick Start Guide

**Build Time**: 2+ hours  
**Status**: ✅ Complete  
**Features**: All 5 implemented and ready to use  

---

## 🚀 Get Started in 5 Minutes

### Step 1: Backend is Already Running
The database models and API endpoints are automatically created when you start the backend:

```bash
cd backend
python seed_all_demo_data.py  # Optional: refresh demo data
uvicorn app.main:app --reload --port 8001
```

✅ Your backend now has:
- 16 new API endpoints
- SessionFeedback table
- All validation & error handling

### Step 2: Test an Endpoint
```bash
# Get mentors with advanced filtering
curl "http://localhost:8001/api/v1x/mentors?min_rating=4&max_price=75"

# Submit a review
curl -X POST "http://localhost:8001/api/v1x/mentors/reviews" \
  -H "Content-Type: application/json" \
  -d '{"session_id":1,"rating":5,"review_text":"Great!"}'
```

### Step 3: Add Components to Your Pages

**In any page that shows mentors:**
```typescript
import { MentorFilters } from '@/components/mentors/MentorFilters';
import { searchMentors } from '@/lib/api';

export default function MentorsPage() {
  const [mentors, setMentors] = React.useState([]);
  
  return (
    <>
      <MentorFilters onFiltersChange={(filters) => {
        searchMentors(filters).then(setMentors);
      }} />
      {mentors.map(m => <MentorCard key={m.id} mentor={m} />)}
    </>
  );
}
```

**In any page that shows sessions:**
```typescript
import { CalendarExport } from '@/components/calendar/CalendarExport';

export default function SessionsPage() {
  return (
    <>
      <h1>My Sessions</h1>
      <CalendarExport />
      {/* Your sessions list */}
    </>
  );
}
```

**In mentor detail page:**
```typescript
import { ReviewList } from '@/components/reviews/ReviewList';

export default function MentorProfile({ mentorId }) {
  return (
    <>
      <MentorInfo id={mentorId} />
      <ReviewList mentorId={mentorId} maxReviews={10} />
    </>
  );
}
```

### Step 4: Test in Browser
Run your frontend:
```bash
npm run dev
```

✅ All new features should work immediately!

---

## 📦 What You Get

### 1. Reviews & Ratings
- 5-star interactive rating component
- Review submission form with tags
- Review list with statistics
- Easy to add to any page

### 2. Advanced Mentor Search
- Text search by name/expertise
- Filter by price range, rating, availability
- Sort by rating, price, or popularity
- Live filter updates

### 3. Session Feedback
- Post-session notes for mentors and students
- Record actual session duration
- Track covered topics
- Mark follow-ups needed

### 4. Calendar Export
- Export sessions as .ics file
- Integrates with Google Calendar, Outlook, Apple Calendar
- Download with one click

### 5. Email Notifications
- API ready for sending emails
- Booking confirmations
- Session reminders
- Review requests

---

## 🎯 Common Implementations

### Implement Reviews on Mentor Profile
**File**: `src/pages/mentors/[id]/index.tsx`

```typescript
import { ReviewList } from '@/components/reviews/ReviewList';

// In your mentor profile component:
<ReviewList mentorId={mentor.id} maxReviews={10} />
```

### Implement Search on Mentors Listing
**File**: `src/pages/mentors/index.tsx`

```typescript
import { MentorFilters } from '@/components/mentors/MentorFilters';

// In your mentors list page:
const [filters, setFilters] = React.useState({});

<MentorFilters onFiltersChange={setFilters} />
// Results update automatically as filters change
```

### Implement Calendar Export on My Sessions
**File**: `src/pages/mentors/my-sessions.tsx`

```typescript
import { CalendarExport } from '@/components/calendar/CalendarExport';

// In your my-sessions page:
<CalendarExport />
```

### Implement Feedback After Session
**File**: `src/pages/mentors/sessions/[id]/details.tsx`

```typescript
import { SessionFeedbackForm } from '@/components/feedback/SessionFeedbackForm';

// After session is completed:
{session.status === 'completed' && (
  <SessionFeedbackForm 
    sessionId={session.id}
    userRole={isMentor ? 'mentor' : 'student'}
  />
)}
```

---

## 🔗 API Function Reference

```typescript
// Reviews API
submitMentorReview(review)      // POST review
getMentorReviews(mentorId)      // GET mentor's reviews
updateMentorReview(id, updates) // PATCH review
deleteMentorReview(id)          // DELETE review

// Search API
searchMentors(filters)          // GET with filters
getMentors(filters)             // Alternative name

// Feedback API
submitSessionFeedback(id, data) // POST feedback
getSessionFeedback(id)          // GET feedback

// Calendar API
exportCalendarAsIcal()          // Download .ics file
getCalendarEvents(start, end)   // GET events
exportCalendarToGoogle()        // Google integration

// Email API
sendBookingConfirmation(id)     // Send email
sendSessionReminder(id)         // Send email
sendReviewRequest(id)           // Send email
```

---

## ✨ Features Highlights

### Reviews
```
✨ 5-star interactive rating
✨ Rich text reviews with tags
✨ Average rating + distribution
✨ User-friendly UI
```

### Search
```
✨ Real-time filtering
✨ Multi-criteria search
✨ Advanced filters toggle
✨ Sorting options
```

### Feedback
```
✨ Mentor notes & observations
✨ Student learning summary
✨ Recording links
✨ Topic tracking
```

### Calendar
```
✨ Universal .ics format
✨ One-click download
✨ Google Calendar ready
✨ Date range filtering
```

---

## 🧪 Quick Test Commands

### Test Reviews Endpoint
```bash
# Create a review
curl -X POST http://localhost:8001/api/v1x/mentors/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "rating": 5,
    "review_text": "Excellent mentor!",
    "tags": "helpful,patient"
  }'

# Get reviews for mentor
curl http://localhost:8001/api/v1x/mentors/reviews/1
```

### Test Search Endpoint
```bash
# Search with filters
curl "http://localhost:8001/api/v1x/mentors?query=python&min_rating=4&max_price=75&sort_by=rating"
```

### Test Feedback Endpoint
```bash
# Submit feedback
curl -X POST http://localhost:8001/api/v1x/mentors/sessions/1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "mentor_feedback": "Great session!",
    "student_notes": "Learned a lot"
  }'
```

### Test Calendar Export
```bash
# Export as iCal
curl http://localhost:8001/api/v1x/mentors/calendar/export?format=ical
```

---

## 🎨 Component Props Reference

### MentorFilters
```typescript
<MentorFilters 
  onFiltersChange={(filters) => {...}}
  loading={isLoading}
/>
```

### ReviewForm
```typescript
<ReviewForm
  sessionId={number}
  mentorId={number}
  onSuccess={() => {...}}
  onCancel={() => {...}}
/>
```

### ReviewList
```typescript
<ReviewList
  mentorId={number}
  maxReviews={number}  // default 5
/>
```

### CalendarExport
```typescript
<CalendarExport
  onExportStart={() => {...}}
  onExportComplete={() => {...}}
/>
```

### SessionFeedbackForm
```typescript
<SessionFeedbackForm
  sessionId={number}
  userRole="mentor" | "student"
  onSuccess={() => {...}}
  onCancel={() => {...}}
/>
```

---

## 🚨 Troubleshooting

### Reviews not showing
- Check mentor ID is correct
- Verify reviews exist in database
- Check browser console for errors

### Search not returning results
- Verify mentors have "approved" status
- Check filter values match data
- Try removing filters one by one

### Calendar export not downloading
- Check browser download settings
- Verify API is returning iCal data
- Check browser console for errors

### Components not rendering
- Verify all imports are correct
- Check parent component passes required props
- Check TypeScript types match

---

## 📚 More Resources

**Full Documentation**: `PHASE_2_2_COMPLETE_GUIDE.md`  
**Implementation Plan**: `PHASE_2_2_IMPLEMENTATION_PLAN.md`  
**Phase 2.1 Booking**: `PHASE_2_1_QUICK_START.md`  

---

## ✅ Checklist for Integration

- [ ] Backend running with SessionFeedback table created
- [ ] API endpoints tested and returning data
- [ ] Components imported in target pages
- [ ] Styling matches existing design system
- [ ] Error handling displays user messages
- [ ] Loading states show while fetching
- [ ] Mobile responsive on phone/tablet
- [ ] Accessibility testing (keyboard nav, screen readers)
- [ ] Tested with demo data
- [ ] Ready for production!

---

**Everything is ready to use! Start by adding one component to a page and test it out.** 🎉

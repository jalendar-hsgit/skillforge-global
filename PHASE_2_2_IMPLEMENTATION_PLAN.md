# Phase 2.2: Complete Feature Implementation Plan

**Scope**: All 5 features for mentor booking enhancement  
**Estimated Time**: 5-6 hours  
**Start Date**: 2026-01-01  

---

## 📋 Implementation Order

### Layer 1: Database Models & Schemas (Foundation)
- [ ] MentorReview model
- [ ] SessionFeedback model  
- [ ] Export configuration models
- [ ] Pydantic schemas for all

### Layer 2: Backend API Endpoints
- [ ] Reviews endpoints (GET, POST, PATCH)
- [ ] Search/Filter endpoints (GET with parameters)
- [ ] Email service integration (async tasks)
- [ ] Feedback endpoints (POST)
- [ ] Calendar export endpoints (GET iCal, Google)

### Layer 3: Frontend Components
- [ ] Review form component
- [ ] Rating display component
- [ ] Mentor search filters widget
- [ ] Calendar export buttons
- [ ] Feedback form
- [ ] Review list display

### Layer 4: Frontend Pages
- [ ] Enhanced mentor list with filters
- [ ] Mentor profile with reviews
- [ ] Session completion/review page
- [ ] Calendar/export page
- [ ] My sessions with feedback

### Layer 5: Integration & Testing
- [ ] End-to-end testing all features
- [ ] Demo data seeding
- [ ] Documentation

---

## 🗄️ Database Schema Additions

### MentorReview Table
```python
class MentorReview(Base):
    id: int (PK)
    mentor_id: int (FK)
    student_id: int (FK) 
    session_id: int (FK) - optional
    rating: int (1-5 stars)
    title: str
    comment: str (text)
    created_at: datetime
    updated_at: datetime
```

### SessionFeedback Table
```python
class SessionFeedback(Base):
    id: int (PK)
    session_id: int (FK)
    mentor_feedback: str (text)
    student_feedback: str (text)
    student_notes: str (text)
    recording_url: str - optional
    session_date: datetime
    created_at: datetime
```

### CalendarExportLog Table (optional)
```python
class CalendarExport(Base):
    id: int (PK)
    user_id: int (FK)
    export_type: str (google, ical)
    exported_at: datetime
    export_count: int
```

---

## 🔌 API Endpoints to Create

### Reviews Endpoints
```
POST   /api/v1x/mentors/{mentor_id}/reviews
GET    /api/v1x/mentors/{mentor_id}/reviews
GET    /api/v1x/mentors/sessions/{session_id}/my-review
PATCH  /api/v1x/reviews/{review_id}
DELETE /api/v1x/reviews/{review_id}
```

### Search & Filter Endpoints
```
GET    /api/v1x/mentors?expertise=python&min_rating=4&max_price=75&sort=rating
GET    /api/v1x/mentors/search?q=sarah&expertise=ai
```

### Email Endpoints
```
POST   /api/v1x/emails/send-confirmation/{session_id}
POST   /api/v1x/emails/send-reminder/{session_id}
POST   /api/v1x/emails/send-review-request/{session_id}
```

### Feedback Endpoints
```
POST   /api/v1x/sessions/{session_id}/feedback
GET    /api/v1x/sessions/{session_id}/feedback
PATCH  /api/v1x/sessions/{session_id}/feedback
```

### Calendar Export Endpoints
```
GET    /api/v1x/calendar/export?format=ical
GET    /api/v1x/calendar/export?format=google
GET    /api/v1x/calendar/sessions.ics
```

---

## 🎨 Frontend Components to Create

### Reviews Components
- `ReviewForm.tsx` - Form to submit rating + comment
- `ReviewDisplay.tsx` - Show individual review
- `ReviewList.tsx` - List all reviews for mentor
- `RatingStars.tsx` - Interactive 5-star rating
- `ReviewStats.tsx` - Average rating + breakdown

### Search Components
- `MentorFilters.tsx` - Filter sidebar
- `SearchBar.tsx` - Search input
- `SortOptions.tsx` - Dropdown for sorting

### Feedback Components
- `FeedbackForm.tsx` - Post-session feedback
- `FeedbackDisplay.tsx` - Show feedback

### Calendar Components
- `CalendarExportButton.tsx` - Download buttons
- `CalendarView.tsx` - Calendar layout of sessions

---

## 📄 New Pages to Create

### Enhanced Pages
- `/mentors` - Add filters & search
- `/mentors/[id]` - Add reviews section
- `/mentors/[id]/book` - Add review after completion
- `/mentors/my-sessions` - Add feedback column

### New Pages
- `/mentors/[id]/reviews` - Full reviews page
- `/calendar` - Calendar view of sessions
- `/calendar/export` - Export options

---

## 🔐 Authentication & Authorization

### Reviews
- Students can POST/PATCH/DELETE own reviews
- Anyone can read reviews
- Mentor can't review own sessions
- One review per session

### Feedback
- Mentor can POST feedback
- Student can POST feedback
- Both can read after posted

### Calendar Export
- Users can only export own calendar

---

## 📊 Feature Details

### 1️⃣ Reviews & Ratings
- **Rating**: 1-5 stars (required)
- **Title**: Short title (required)
- **Comment**: Detailed feedback (optional)
- **Display**: Latest reviews, average rating
- **Permissions**: Students review mentors, visible to all

### 2️⃣ Advanced Search
- **Filters**: expertise, min_rating, max_price, availability
- **Sort**: by rating, price, popularity, newest
- **Search**: text search on name + bio
- **Results**: paginated list with live update

### 3️⃣ Email Notifications
- **Booking confirmation**: When session is created
- **Reminder**: 24 hours before session
- **Review request**: After session completion
- **Status updates**: When session status changes

### 4️⃣ Session Feedback
- **Mentor feedback**: Notes from mentor about student
- **Student notes**: Student's summary of what learned
- **Recording URL**: Link to session video
- **Display**: In session details and my-sessions

### 5️⃣ Calendar Export
- **iCal format**: Download `.ics` file for Google/Outlook
- **Google Calendar**: Direct integration link
- **Calendar view**: Visual calendar of sessions
- **Sync**: Option to auto-sync

---

## Implementation Sequence

```
Day 1 (Now):
├─ Step 1: Database models & migrations
├─ Step 2: Pydantic schemas
├─ Step 3: Backend API endpoints
└─ Step 4: Backend testing

Day 2:
├─ Step 5: Frontend API functions
├─ Step 6: Review components
├─ Step 7: Search components
└─ Step 8: Feedback components

Day 3:
├─ Step 9: Calendar components
├─ Step 10: Page updates
├─ Step 11: Integration testing
└─ Step 12: Demo data + documentation
```

---

## 🎯 Success Criteria

All features complete when:
- ✅ Database models created & tested
- ✅ API endpoints working (30+ endpoints)
- ✅ Frontend components built & styled
- ✅ All CRUD operations functional
- ✅ 10+ test scenarios passing
- ✅ Demo data seeded
- ✅ Documentation complete

---

## 📈 Expected Metrics

| Feature | API Endpoints | Components | Pages | LOC |
|---------|---------------|-----------|-------|-----|
| Reviews | 5 | 5 | 2 | 800 |
| Search | 2 | 3 | 1 | 400 |
| Email | 3 | 0 | 0 | 300 |
| Feedback | 3 | 2 | 1 | 350 |
| Calendar | 3 | 3 | 1 | 400 |
| **Total** | **16** | **13** | **5** | **2250** |

---

## 🚀 Ready to Start!

This plan covers all features systematically. Implementation will be:
1. **Modular** - each feature self-contained
2. **Incremental** - test after each feature
3. **Documented** - as we build
4. **Tested** - with demo data

Let's begin! 🎯

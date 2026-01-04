# Phase 2.2: Complete Testing Guide

**Last Updated**: January 1, 2026  
**Status**: Ready for QA Testing  
**Test Scenarios**: 20+ covered  

---

## 🧪 Quick Testing (15 minutes)

### 1. Test Review Endpoints (3 min)
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

# Expected: 201 Created with review data

# Get reviews for mentor
curl http://localhost:8001/api/v1x/mentors/reviews/1

# Expected: 200 OK with reviews list and statistics
```

### 2. Test Search Endpoints (3 min)
```bash
# Simple search
curl "http://localhost:8001/api/v1x/mentors?query=python"

# Expected: 200 OK with matching mentors

# Advanced search
curl "http://localhost:8001/api/v1x/mentors?min_rating=4&max_price=75&sort_by=rating"

# Expected: 200 OK with filtered and sorted results
```

### 3. Test Feedback Endpoints (3 min)
```bash
# Submit feedback
curl -X POST http://localhost:8001/api/v1x/mentors/sessions/1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "mentor_feedback": "Great progress!",
    "student_notes": "Learned a lot"
  }'

# Expected: 201 Created with feedback data

# Get feedback
curl http://localhost:8001/api/v1x/mentors/sessions/1/feedback

# Expected: 200 OK with feedback data
```

### 4. Test Calendar Export (3 min)
```bash
# Export as iCal
curl http://localhost:8001/api/v1x/mentors/calendar/export?format=ical

# Expected: 200 OK with iCal file content (string)

# Get calendar events
curl "http://localhost:8001/api/v1x/mentors/calendar/events?start_date=2026-01-01&end_date=2026-12-31"

# Expected: 200 OK with list of calendar events
```

### 5. Test Email Endpoints (3 min)
```bash
# Send confirmation
curl -X POST http://localhost:8001/api/v1x/mentors/emails/confirmation \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1}'

# Expected: 200 OK with success message
```

**Total Time**: ~15 minutes ✅

---

## 🎯 Feature-Specific Testing

### Reviews & Ratings Testing

#### Test Case 1: Submit Review
```bash
Preconditions:
- User is logged in
- Session exists and is COMPLETED
- No existing review for this session

Steps:
1. Submit review with rating=5, text="Great!"
2. Verify 201 Created response
3. Verify review appears in GET /reviews/{mentor_id}
4. Verify mentor.average_rating updated

Expected: ✅ Review created and visible
```

#### Test Case 2: Update Review
```bash
Preconditions:
- Review exists

Steps:
1. PATCH review with new rating=4
2. Verify 200 OK response
3. GET reviews and verify new rating
4. Verify average_rating recalculated

Expected: ✅ Review updated correctly
```

#### Test Case 3: Delete Review
```bash
Preconditions:
- Review exists
- User owns the review

Steps:
1. DELETE review
2. Verify 200 OK response
3. GET reviews and verify it's gone
4. Verify average_rating recalculated

Expected: ✅ Review deleted successfully
```

#### Test Case 4: Cannot Review Own Sessions
```bash
Preconditions:
- User is a mentor
- User completed their own session (shouldn't happen)

Steps:
1. Try to submit review for own session
2. Verify 403 Forbidden

Expected: ✅ Access denied as expected
```

---

### Advanced Search Testing

#### Test Case 1: Text Search
```bash
Steps:
1. GET /mentors?query=python
2. Verify results include mentors with "python" in bio/expertise
3. Verify non-matching mentors excluded

Expected: ✅ Text search works
```

#### Test Case 2: Filter by Expertise
```bash
Steps:
1. GET /mentors?expertise=web-dev
2. Verify only web-dev mentors returned
3. Try with multiple: ?expertise=web-dev,python

Expected: ✅ Expertise filtering works
```

#### Test Case 3: Filter by Price Range
```bash
Steps:
1. GET /mentors?min_price=50&max_price=100
2. Verify only mentors in $50-100 range returned
3. Try edge cases (0, 500)

Expected: ✅ Price filtering works
```

#### Test Case 4: Filter by Rating
```bash
Steps:
1. GET /mentors?min_rating=4
2. Verify only mentors with rating >= 4 returned
3. Try with 4.5, 5

Expected: ✅ Rating filtering works
```

#### Test Case 5: Availability Filter
```bash
Steps:
1. GET /mentors?availability=true
2. Verify only mentors with available slots returned
3. GET /mentors?availability=false or omit

Expected: ✅ Availability filtering works
```

#### Test Case 6: Sorting Options
```bash
Steps:
1. GET /mentors?sort_by=name
2. Verify results sorted A-Z
3. Try sort_by=rating, price, newest
4. Verify each sorts correctly

Expected: ✅ All sort options work
```

#### Test Case 7: Combined Filters
```bash
Steps:
1. GET /mentors?query=python&min_rating=4&max_price=75&availability=true&sort_by=rating
2. Verify all filters applied
3. Results should show top-rated Python mentors under $75

Expected: ✅ Combined filters work together
```

---

### Session Feedback Testing

#### Test Case 1: Mentor Adds Feedback
```bash
Preconditions:
- Session completed
- User is the mentor

Steps:
1. POST feedback with mentor_feedback, recording_url, key_topics
2. Verify 201 Created
3. GET feedback and verify mentor_feedback populated
4. Verify student_notes empty (mentor didn't add)

Expected: ✅ Mentor can add feedback
```

#### Test Case 2: Student Adds Notes
```bash
Preconditions:
- Session completed
- User is the student

Steps:
1. POST feedback with student_notes
2. Verify 201 Created
3. GET feedback and verify student_notes populated
4. Verify mentor_feedback empty (student didn't add)

Expected: ✅ Student can add notes
```

#### Test Case 3: Both Add Feedback
```bash
Preconditions:
- Session completed

Steps:
1. Mentor POSTs mentor_feedback
2. Verify 201 Created
3. Student POSTs student_notes
4. Verify 200 OK (updates existing)
5. GET feedback shows both

Expected: ✅ Both can contribute to feedback
```

#### Test Case 4: Update Feedback
```bash
Preconditions:
- Feedback exists

Steps:
1. PATCH feedback with new mentor_feedback
2. Verify 200 OK
3. GET feedback and verify updated

Expected: ✅ Feedback can be updated
```

#### Test Case 5: Quality Rating
```bash
Preconditions:
- Feedback exists

Steps:
1. POST with session_quality_rating=5
2. Verify stored correctly
3. Try 1, 3, 5 ratings

Expected: ✅ Quality rating works
```

---

### Calendar Export Testing

#### Test Case 1: Export as iCal
```bash
Steps:
1. GET /calendar/export?format=ical
2. Verify 200 OK
3. Response contains "BEGIN:VCALENDAR"
4. Verify contains all user's sessions as VEVENT
5. Download file and verify it's valid .ics

Expected: ✅ iCal export works
```

#### Test Case 2: Calendar Events List
```bash
Steps:
1. GET /calendar/events
2. Verify 200 OK
3. Response is array of CalendarEventResponse
4. Verify each has title, start_time, end_time
5. Filter by date range

Expected: ✅ Calendar events list works
```

#### Test Case 3: Date Range Filtering
```bash
Steps:
1. GET /calendar/events?start_date=2026-01-01&end_date=2026-01-31
2. Verify only January sessions returned
3. Try different date ranges

Expected: ✅ Date filtering works
```

#### Test Case 4: Include Past Sessions
```bash
Steps:
1. GET /calendar/export?format=ical&include_past=false
2. Verify only future sessions included
3. GET with include_past=true
4. Verify includes past sessions

Expected: ✅ Past sessions filtering works
```

---

### Email Notifications Testing

#### Test Case 1: Send Confirmation
```bash
Steps:
1. POST /emails/confirmation with session_id
2. Verify 200 OK
3. Check response has success:true, message
4. Verify sent_at timestamp

Expected: ✅ Confirmation endpoint works
```

#### Test Case 2: Send Reminder
```bash
Steps:
1. POST /emails/reminder with session_id
2. Verify 200 OK
3. Admin-only check

Expected: ✅ Reminder endpoint works
```

#### Test Case 3: Send Review Request
```bash
Steps:
1. POST /emails/review-request with session_id
2. Verify 200 OK
3. Admin-only check

Expected: ✅ Review request endpoint works
```

---

## 🧬 Frontend Component Testing

### ReviewForm Component
```
✅ Can select 1-5 stars
✅ Can type review text
✅ Can add tags (from suggestions or custom)
✅ Shows character count
✅ Submit button disabled until title entered
✅ Shows loading state during submission
✅ Shows success message
✅ Clears form after success
✅ Shows error message on failure
✅ Cancel button works (if provided)
```

### MentorFilters Component
```
✅ Text search input works
✅ Sort dropdown changes sort order
✅ Advanced filters toggle shows/hides
✅ Expertise checkboxes filter results
✅ Price range inputs work
✅ Rating dropdown filters
✅ Availability checkbox filters
✅ Filters trigger onFiltersChange callback
✅ Reset button clears all filters
✅ Loading state disables inputs
```

### ReviewList Component
```
✅ Loads reviews on mount
✅ Displays average rating
✅ Shows rating distribution bars
✅ Lists recent reviews
✅ Shows review text and tags
✅ Shows creation date
✅ Shows total review count
✅ Displays "No reviews" if none exist
✅ Shows loading state
✅ Shows error message on failure
```

### CalendarExport Component
```
✅ iCal button triggers export
✅ Google Calendar button works
✅ Shows loading state
✅ Shows success message
✅ File downloads when iCal clicked
✅ Shows error on failure
```

### SessionFeedbackForm Component
```
✅ Mentor can enter feedback
✅ Student can enter notes
✅ Recording URL field works
✅ Duration input works
✅ Quality rating dropdown works
✅ Topics field works
✅ Follow-up checkbox works
✅ Submit disabled until required field filled
✅ Shows loading state
✅ Shows success/error messages
```

---

## 📊 Testing Checklist

### Backend Testing
- [ ] All 16 endpoints return correct status codes
- [ ] Request validation working (invalid input → 422)
- [ ] Authorization checks working (unauthorized → 403)
- [ ] Database records created correctly
- [ ] Relationships maintained properly
- [ ] Average ratings calculated correctly
- [ ] Search filters applied correctly
- [ ] Pagination working (limit/offset)
- [ ] Error messages user-friendly
- [ ] Timestamps created/updated properly

### Frontend Testing
- [ ] All 9 components render without errors
- [ ] Props validated (TypeScript)
- [ ] Loading states show while fetching
- [ ] Error states show user-friendly messages
- [ ] Forms submit with valid data
- [ ] Forms validate required fields
- [ ] Callbacks triggered on success/error
- [ ] Components responsive on mobile
- [ ] Keyboard navigation works
- [ ] Screen reader compatible

### Integration Testing
- [ ] Component → API → Database flow works
- [ ] Form submission → database update → display refresh
- [ ] Real-time filtering works
- [ ] File downloads work
- [ ] Error recovery works
- [ ] State management correct
- [ ] Session management correct
- [ ] Authentication working
- [ ] Authorization enforced
- [ ] No console errors

### Security Testing
- [ ] Cannot access other users' data
- [ ] Cannot modify other users' reviews
- [ ] SQL injection prevented
- [ ] XSS attacks prevented
- [ ] CSRF tokens working
- [ ] Rate limiting ready
- [ ] No sensitive data in logs
- [ ] No credentials in URLs

---

## 🔍 Manual Testing Steps

### End-to-End Review Test
1. Log in as student
2. Go to completed session
3. Click "Leave Review"
4. Rate mentor 5 stars
5. Write short review
6. Add tags
7. Submit form
8. See success message
9. Go to mentor profile
10. Verify review shows in reviews list
11. Verify average rating updated
12. Try to submit another review for same session (should fail)
13. Edit review (if implemented)
14. Delete review (if implemented)

### End-to-End Search Test
1. Go to Mentors page
2. Enter search text (e.g., "python")
3. Verify results update
4. Click "+ Advanced Filters"
5. Set min price $50
6. Set max price $100
7. Select expertise "Python & AI"
8. Select "Only available mentors"
9. Change sort to "Highest Rating"
10. Verify all filters applied
11. Click "Reset Filters"
12. Verify all filters cleared

### End-to-End Calendar Export Test
1. Go to My Sessions
2. Verify sessions listed
3. Click "Download iCal" button
4. Verify file downloads as .ics
5. Open file in text editor
6. Verify iCalendar format is correct
7. Try importing to Google Calendar (if available)
8. Verify sessions appear in calendar

---

## 🚨 Error Scenarios

### Test: Invalid Session ID
```bash
curl -X POST http://localhost:8001/api/v1x/mentors/reviews \
  -d '{
    "session_id": 99999,
    "rating": 5,
    "review_text": "Test"
  }'

Expected: 404 Not Found
```

### Test: Review Not Completed Session
```bash
curl -X POST http://localhost:8001/api/v1x/mentors/reviews \
  -d '{
    "session_id": 1,
    "rating": 5,
    "review_text": "Test"
  }'

Expected: 400 Bad Request (session not completed)
```

### Test: Invalid Rating
```bash
curl -X POST http://localhost:8001/api/v1x/mentors/reviews \
  -d '{
    "session_id": 1,
    "rating": 10,  # Invalid (should be 1-5)
    "review_text": "Test"
  }'

Expected: 422 Unprocessable Entity
```

### Test: Unauthorized Access
```bash
# Try to update review you don't own
curl -X PATCH http://localhost:8001/api/v1x/mentors/reviews/1 \
  -d '{"rating": 1}'

Expected: 403 Forbidden
```

---

## 📈 Performance Testing

### Load Testing
```bash
# Generate multiple requests to test performance
for i in {1..100}; do
  curl http://localhost:8001/api/v1x/mentors?limit=20
done

Expected: All requests complete in <5 seconds
```

### Database Performance
```bash
# Get list of reviews (with 1000s of records)
curl http://localhost:8001/api/v1x/mentors/reviews/1?limit=50

Expected: Response in <100ms
```

---

## ✅ Final Checklist

Before deploying Phase 2.2:

- [ ] All 16 endpoints tested
- [ ] All 9 components tested
- [ ] No console errors
- [ ] No database errors
- [ ] All validations working
- [ ] Error handling working
- [ ] Mobile responsive
- [ ] Accessibility checked
- [ ] Security review done
- [ ] Performance acceptable
- [ ] Documentation reviewed
- [ ] Team trained on features
- [ ] Ready to release!

---

## 🎯 Testing Tools

### Recommended Tools
- **Postman**: API testing and automation
- **Insomnia**: REST client alternative
- **curl**: Command-line API testing
- **React DevTools**: Component inspection
- **Browser DevTools**: Network inspection
- **Jest**: Unit testing (optional)
- **Cypress**: E2E testing (optional)

---

**Happy Testing!** 🧪✅

If all tests pass, Phase 2.2 is ready for production! 🚀

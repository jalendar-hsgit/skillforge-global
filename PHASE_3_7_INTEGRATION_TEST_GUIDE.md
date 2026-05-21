# Phase 3.7: Integration Testing Guide

**Purpose**: Verify that real-time events are properly emitted and received  
**Duration**: ~30 minutes  
**Prerequisites**: Backend running, frontend running, browser DevTools open  

---

## Setup

### Prerequisites
1. ✅ Backend code modified (Phase 3.7 complete)
2. ✅ Frontend WebSocket client ready (Phase 3.6 complete)
3. ✅ All syntax validated
4. Node.js and Python installed
5. Browser with DevTools (Chrome/Firefox)

### Start Services

**Terminal 1 - Backend**:
```bash
cd backend
# Install dependencies if needed
pip install -r requirements.txt

# Create database and seed data
python init_db.py
python seed_all_demo_data.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 2 - Frontend**:
```bash
# From repo root
npm install  # if needed
npm run dev

# Frontend should be at http://localhost:3000
```

---

## Test 1: Learning Path Enrollment

**Objective**: Verify `on_learning_path_enrolled` event is emitted

### Steps

1. **Open Browser DevTools**
   - Open http://localhost:3000
   - Open DevTools → Network tab
   - Filter by WebSocket (WS)

2. **Login as User**
   - Use demo account: `john.doe@example.com` / password
   - Or create new account

3. **Enroll in Learning Path**
   - Navigate to Learning Paths section
   - Click "Enroll" on any path (e.g., "Python Fundamentals")
   - Action triggers `POST /api/v1/learning-paths/{path_id}/enroll`

4. **Verify Event in WebSocket**
   - In DevTools Network tab, click WebSocket connection
   - Look for message containing:
     ```json
     {
       "type": "PATH_PROGRESS_UPDATE",
       "user_id": <current_user_id>,
       "data": {
         "path_id": <path_id>,
         "path_title": "Python Fundamentals",
         "difficulty": "beginner|intermediate|advanced",
         "action": "enrolled",
         "completion_percentage": 0
       }
     }
     ```

5. **Verify Frontend Notification**
   - Should see toast notification: "Successfully enrolled in [Path Name]"
   - Or real-time progress update visible on page

### Expected Results
- ✅ Learning path shows as enrolled
- ✅ WebSocket receives PATH_PROGRESS_UPDATE event
- ✅ User sees real-time notification
- ✅ No console errors

---

## Test 2: Challenge Completion

**Objective**: Verify `on_challenge_completed` event is emitted

### Steps

1. **Navigate to Learning Path**
   - Go to enrolled learning path
   - Find a challenge to complete

2. **Complete Challenge**
   - Click challenge
   - Complete the challenge requirements
   - Submit/save changes
   - Action triggers `POST /api/v1/learning-paths/{path_id}/challenges/{challenge_id}/complete`

3. **Monitor WebSocket Events**
   - Watch DevTools Network > WebSocket
   - Should receive PATH_PROGRESS_UPDATE with:
     ```json
     {
       "type": "PATH_PROGRESS_UPDATE",
       "data": {
         "path_id": <path_id>,
         "challenge_id": <challenge_id>,
         "challenge_name": "Challenge Name",
         "points_earned": <points>,
         "completion_percentage": <percentage>,
         "is_path_completed": true|false
       }
     }
     ```

4. **Verify UI Updates**
   - Progress bar updates in real-time
   - Challenge marked as completed
   - Points added to user total
   - Toast notification showing completion

### Expected Results
- ✅ Challenge marked completed immediately
- ✅ Points awarded visibly
- ✅ Progress percentage updates
- ✅ WebSocket event received
- ✅ Real-time notification shown

---

## Test 3: Message Sending

**Objective**: Verify `on_message_created` event is emitted to recipient

### Steps

1. **Open Two Browser Windows**
   - Window 1: Login as User A (e.g., john.doe@example.com)
   - Window 2: Login as User B (e.g., jane.smith@example.com)
   - Keep DevTools open in both

2. **Start Conversation**
   - In Window 1: Navigate to Messages
   - Click "New Message" or select User B
   - Open conversation with User B

3. **Send Message**
   - Type message: "Hello from User A"
   - Click Send
   - Action triggers `POST /api/v1/messages`

4. **Monitor WebSocket Events**
   - Window 1: Watch DevTools WebSocket
   - Should receive MESSAGE_SENT with status: "delivered"
   - Window 2: Should receive MESSAGE_SENT with full message content

5. **Verify in UI**
   - Window 1: Message appears in conversation (local)
   - Window 2: Message appears instantly in conversation (real-time)
   - Both show message with timestamp

### Expected Results
- ✅ Message appears in Window 1
- ✅ Message appears instantly in Window 2 (real-time!)
- ✅ Both Windows receive WebSocket events
- ✅ Delivery confirmation shown
- ✅ No need to refresh

---

## Test 4: Forum Thread Creation

**Objective**: Verify `on_forum_thread_created` event is emitted

### Steps

1. **Navigate to Forum**
   - Go to Forum section
   - Select a topic (e.g., "General Discussion")

2. **Create Thread**
   - Click "New Thread"
   - Title: "Test Thread for Real-Time Events"
   - Content: "Testing Phase 3.7 event integration"
   - Click Post
   - Action triggers `POST /api/v1/forum/topics/{topic_id}/threads`

3. **Monitor WebSocket**
   - DevTools Network > WebSocket
   - Should receive FORUM_THREAD_CREATED:
     ```json
     {
       "type": "FORUM_THREAD_CREATED",
       "data": {
         "thread_id": <thread_id>,
         "topic_id": <topic_id>,
         "author_id": <user_id>,
         "author_name": "User Name",
         "title": "Test Thread for Real-Time Events",
         "created_at": "2026-01-01T12:00:00"
       }
     }
     ```

4. **Verify UI**
   - Thread appears in forum topic instantly
   - Thread shows correct author and timestamp
   - Real-time notification displays

### Expected Results
- ✅ Thread appears immediately
- ✅ WebSocket event received
- ✅ Thread shows author and timestamp correctly
- ✅ Other users see thread in real-time (if multiple active)

---

## Test 5: Forum Reply

**Objective**: Verify `on_forum_reply_posted` event is emitted

### Steps

1. **Open Forum Thread**
   - Navigate to thread created in Test 4
   - Or open any existing thread

2. **Post Reply**
   - Click "Reply"
   - Type: "Testing forum reply event"
   - Submit
   - Action triggers `POST /api/v1/forum/threads/{thread_id}/replies`

3. **Monitor WebSocket**
   - Should receive FORUM_REPLY_POSTED:
     ```json
     {
       "type": "FORUM_REPLY_POSTED",
       "data": {
         "reply_id": <reply_id>,
         "thread_id": <thread_id>,
         "topic_id": <topic_id>,
         "author_id": <user_id>,
         "author_name": "User Name",
         "content": "Testing forum reply event",
         "created_at": "2026-01-01T12:00:00"
       }
     }
     ```

4. **Verify UI**
   - Reply appears in thread
   - Shows author and timestamp
   - Real-time notification (if subscribed)

### Expected Results
- ✅ Reply appears immediately
- ✅ WebSocket event received
- ✅ Reply count updated
- ✅ No refresh needed

---

## Test 6: Skill Validation

**Objective**: Verify `on_skill_validated` event is emitted

### Steps

1. **Login as Admin/Mentor**
   - Use demo admin: `admin@skillforge.com`
   - Or mentor account

2. **Navigate to Skills**
   - Go to Skills Management or User Profile
   - Find "Validate Skill" or "Endorse Skill"

3. **Validate a User's Skill**
   - Select a skill to validate
   - Select a user
   - Choose proficiency level
   - Click Validate/Endorse
   - Action triggers `POST /api/v1/skills`

4. **Monitor WebSocket**
   - Should receive SKILL_VALIDATED:
     ```json
     {
       "type": "SKILL_VALIDATED",
       "data": {
         "skill_id": <skill_id>,
         "user_id": <user_id>,
         "skill_name": "Python",
         "proficiency_level": "expert|intermediate|beginner",
         "confidence_score": 0.85,
         "endorsement_count": 1
       }
     }
     ```

5. **Verify UI**
   - Skill shows as validated in user profile
   - User receives real-time notification
   - Endorsement count updates

### Expected Results
- ✅ Skill marked as validated
- ✅ User profile updates in real-time
- ✅ WebSocket event received
- ✅ Notification displayed to user

---

## Test 7: Certificate Issuance

**Objective**: Verify `on_certificate_issued` event is emitted

### Steps

1. **Complete Learning Path** (if not already done)
   - Enroll in path
   - Complete all challenges
   - Path should be 100% complete

2. **Issue Certificate**
   - Path completion should trigger certificate
   - Or admin can issue certificate manually
   - Action triggers `POST /api/v1/certificates`

3. **Monitor WebSocket**
   - Should receive CERTIFICATE_ISSUED:
     ```json
     {
       "type": "CERTIFICATE_ISSUED",
       "data": {
         "certificate_id": <cert_id>,
         "user_id": <user_id>,
         "certificate_number": "CERT-2026-001",
         "path_id": <path_id>,
         "path_title": "Python Fundamentals",
         "issue_date": "2026-01-01T12:00:00"
       }
     }
     ```

4. **Verify UI**
   - Certificate appears in user profile
   - Certificate displayed in learning path
   - User receives prominent notification
   - Certificate details viewable

### Expected Results
- ✅ Certificate created and assigned
- ✅ Certificate visible in user account
- ✅ WebSocket event received
- ✅ Real-time notification shows
- ✅ Certificate can be downloaded

---

## Test 8: Multi-User Real-Time Sync

**Objective**: Verify multiple users receive real-time updates

### Steps

1. **Open 3+ Browser Windows**
   - Window A: User A (john.doe@example.com)
   - Window B: User B (jane.smith@example.com)
   - Window C: Admin (admin@skillforge.com)

2. **Create Forum Thread in Window A**
   - Navigate to Forum
   - Create new thread
   - Title: "Multi-User Real-Time Test"

3. **Monitor in Windows B & C**
   - Both should see thread appear instantly
   - Both should receive WebSocket event
   - No refresh needed

4. **Post Reply in Window B**
   - Reply to the thread
   - Watch Window A & C receive event in real-time

5. **Verify Sync**
   - All three windows show same content
   - Timestamps consistent
   - Events received by all relevant users

### Expected Results
- ✅ All users see updates in real-time
- ✅ No conflicts or duplicate data
- ✅ All receive WebSocket events
- ✅ Content consistent across clients

---

## Troubleshooting

### WebSocket Events Not Appearing

**Check 1**: WebSocket Connected?
- DevTools → Network → Filter "WS"
- Should show WebSocket connection
- Status: "101 Switching Protocols"

**Check 2**: Event Imports Correct?
```bash
grep "from app.services.realtime_events" backend/app/api/v1/*.py
```
Should show all imports from app.services

**Check 3**: Function Made Async?
```bash
grep "async def" backend/app/api/v1/*.py | grep -E "enroll|complete|issue|send_message|create_thread|create_reply|create_skill"
```

**Check 4**: Backend Running?
```bash
curl http://localhost:8001/docs
```
Should load Swagger API docs

### Events Received but No UI Update

**Check**:
- Frontend event handlers registered
- Component subscription to events
- React state updates triggered
- No console errors

### API Endpoint Fails

**Check**:
- Error message in response
- Browser console logs
- Backend logs for tracebacks
- Database query issues

---

## Passing Criteria

✅ All 8 tests pass when:
- All WebSocket events received
- All UI updates appear
- No console errors
- No backend errors
- Multi-user sync works
- Real-time notifications display
- Event data is correct

---

## Performance Metrics to Check

While testing, monitor:

| Metric | Expected | Check In |
|--------|---|---|
| WebSocket latency | <100ms | Browser Network tab |
| Event receipt | Instant | Monitor messages |
| UI update | <200ms | Visual inspection |
| Backend response | <500ms | Network tab |
| Memory usage | Stable | DevTools Performance |

---

## Success Indicators

After all tests, you should see:
- ✅ 8/8 tests passing
- ✅ Events received for all actions
- ✅ Real-time notifications working
- ✅ Multi-user sync functioning
- ✅ No errors in console or backend
- ✅ Zero syntax issues
- ✅ Production-ready system

---

## Final Verification

Run this checklist:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] WebSocket connection established
- [ ] Learning path enrollment events received
- [ ] Challenge completion events received
- [ ] Message sending events received
- [ ] Forum thread events received
- [ ] Forum reply events received
- [ ] Skill validation events received
- [ ] Certificate events received
- [ ] Multi-user real-time sync works
- [ ] No console errors in browser
- [ ] No errors in backend logs
- [ ] All 7+ modified endpoints functional
- [ ] Event signatures match specs
- [ ] Real-time notifications display

---

## Success!

If all tests pass, Phase 3.7 Backend Event Integration is **VERIFIED AND READY FOR PRODUCTION**.

The SkillForge platform now provides complete real-time event-driven experiences across all major user interactions.

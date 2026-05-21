# 🧪 COMPREHENSIVE TESTING GUIDE - Forums & Practice System

**Project:** SkillForge Global  
**Created:** January 2, 2026  
**Status:** Ready for QA Testing

---

## 📋 PRE-TEST CHECKLIST

Before starting tests, verify:

- [ ] Backend running: `http://localhost:8001/docs` (check for Swagger)
- [ ] Frontend running: `http://localhost:3001` (should load without errors)
- [ ] Database ready: 207 tables created
- [ ] Demo data seeded: Run `python backend/seed_all_demo_data.py`

**Status Check Command:**
```bash
# Check backend
curl http://localhost:8001/api/v1x/forums/categories

# Check frontend
curl http://localhost:3001/forums
```

---

## 🧪 TEST SUITE 1: FORUM SYSTEM

### Test Group 1.1: Forum Index Page

**Test 1.1.1 - Load Forum Index**
- **Steps:**
  1. Open http://localhost:3001/forums
  2. Wait for page to load
  3. Verify page title is "Community Forums"
  4. Check for category list

- **Expected Results:**
  - Page loads without errors
  - Categories display with emoji and names
  - Thread count shows for each category
  - "New Thread" button visible
  - Search box appears

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.1.2 - Display Forum Categories**
- **Steps:**
  1. Scroll to categories section
  2. Count categories displayed
  3. Hover over each category
  4. Click on a category

- **Expected Results:**
  - At least 4 categories show (if seeded)
  - Hover effect shows on category button
  - Category button changes color when selected
  - Thread list filters to show only threads in that category

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.1.3 - Search Threads**
- **Steps:**
  1. Click on search box
  2. Type "python" (or any keyword from demo data)
  3. Wait for results to filter
  4. Clear search box
  5. Verify threads reappear

- **Expected Results:**
  - Search box accepts input
  - Results filter in real-time
  - Only threads matching search term display
  - Clearing search shows all threads again

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.1.4 - Sort Options**
- **Steps:**
  1. Click "Recent" sort button
  2. Verify threads sort by latest first
  3. Click "Popular" sort button
  4. Verify threads sort by most popular first
  5. Try "Viewed" and "Unanswered" options

- **Expected Results:**
  - All 4 sort buttons work
  - Thread order changes appropriately
  - Pagination resets to page 1
  - Sort button highlights when selected

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.1.5 - Pagination**
- **Steps:**
  1. Scroll to bottom of thread list
  2. Check pagination controls
  3. Click "Next" button
  4. Verify page 2 threads load
  5. Click "Previous" button
  6. Verify page 1 threads reappear

- **Expected Results:**
  - Pagination controls visible
  - "Previous" disabled on page 1
  - "Next" disabled on last page
  - Page number displayed correctly
  - Page transition is smooth

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

### Test Group 1.2: Thread Creation

**Test 1.2.1 - Load Create Thread Page**
- **Steps:**
  1. Click "Create Thread" button on forums index
  2. Wait for page to load
  3. Verify form elements present

- **Expected Results:**
  - Page loads at `/forums/create`
  - Form with all fields visible
  - Category dropdown populated
  - Thread type buttons show

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.2.2 - Create New Thread**
- **Steps:**
  1. Select thread type: "Question"
  2. Select category from dropdown
  3. Enter title: "Test Question about Python"
  4. Enter content: "How do I use decorators in Python?"
  5. Add tags: "python, decorators, advanced"
  6. Click "Create Thread" button

- **Expected Results:**
  - Form validates input
  - Submit button shows loading state
  - Redirects to thread detail page
  - New thread displays with correct info
  - Author set to current user

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.2.3 - Form Validation**
- **Steps:**
  1. Leave title field empty
  2. Try to submit form
  3. Verify error message shows
  4. Fill title but leave content empty
  5. Try to submit
  6. Verify error shows

- **Expected Results:**
  - Error messages display for missing fields
  - Form doesn't submit with missing required fields
  - Error is clear about which field is missing

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.2.4 - Thread Type Selection**
- **Steps:**
  1. Click each thread type option
  2. Verify selection highlights
  3. Read description for each type
  4. Verify all types selectable

- **Expected Results:**
  - All 4 thread types available:
    - ❓ Question
    - 💬 Discussion
    - 📚 Resource
    - 🐛 Bug Report
  - Selected type highlights
  - Descriptions visible for each

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

### Test Group 1.3: Thread Detail View

**Test 1.3.1 - View Thread Details**
- **Steps:**
  1. From forum index, click any thread
  2. Wait for thread detail page to load
  3. Examine thread information

- **Expected Results:**
  - Thread title displays prominently
  - Thread content shows fully
  - Author info and avatar visible
  - Thread creation date shown
  - Category breadcrumb displays

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.3.2 - Thread Statistics**
- **Steps:**
  1. Scroll through thread detail
  2. Look for statistics section
  3. Verify all stats display

- **Expected Results:**
  - View count shown (e.g., "👁️ 42 views")
  - Reply count shown (e.g., "💬 5 replies")
  - Vote count shown (e.g., "👍 3 votes")
  - Stats update if thread is voted on

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.3.3 - Thread Tags**
- **Steps:**
  1. Scroll to find tags section
  2. Verify tags from thread creation display
  3. Check tag formatting

- **Expected Results:**
  - Tags display below thread content
  - Tags formatted as hashtags (e.g., #python)
  - Tags clickable (optional enhancement)
  - Correct number of tags shown

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

### Test Group 1.4: Reply System

**Test 1.4.1 - Load Replies**
- **Steps:**
  1. View a thread with existing replies
  2. Scroll down to replies section
  3. Verify replies display

- **Expected Results:**
  - Replies section labeled "Answers"
  - Reply count matches what was shown in header
  - Each reply shows author, content, date
  - Reply voting buttons visible

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.4.2 - Post New Reply**
- **Steps:**
  1. Scroll to "Your Answer" section at bottom
  2. Click in reply textarea
  3. Type a reply: "You can use decorators like this: @decorator_name"
  4. Click "Post Answer" button

- **Expected Results:**
  - Textarea accepts input
  - Submit button shows loading state
  - New reply appears at bottom of list
  - Author set to current user
  - Timestamp shows "just now"

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.4.3 - Vote on Reply**
- **Steps:**
  1. Find a reply with vote button
  2. Click upvote button (👍)
  3. Verify vote count increases
  4. Click again to verify toggle

- **Expected Results:**
  - Vote button shows thumbs up emoji
  - Vote count increments after click
  - Button shows loading state during vote
  - Vote count updates in real-time

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.4.4 - Accepted Answer Badge**
- **Steps:**
  1. Look for any reply with "✓ Accepted Answer" badge
  2. Verify badge styling
  3. Check badge positioning

- **Expected Results:**
  - Accepted answers show with green badge
  - Badge appears near author name
  - Reply card has slightly different styling
  - Reply listed before non-accepted replies

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

### Test Group 1.5: User Experience

**Test 1.5.1 - Loading States**
- **Steps:**
  1. When submitting a new thread, observe loading state
  2. Watch submit button during form submission
  3. Verify loading spinner shows

- **Expected Results:**
  - Submit button shows spinner during submission
  - Button is disabled while loading
  - User can see request is processing

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.5.2 - Error Handling**
- **Steps:**
  1. Try to create thread without filling form
  2. Trigger an error if possible
  3. Check error message display

- **Expected Results:**
  - Error messages are clear and helpful
  - Error text is readable (proper contrast)
  - User knows how to fix the error

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 1.5.3 - Responsive Design**
- **Steps:**
  1. View forum page on desktop (full width)
  2. Open browser dev tools
  3. Test on tablet size (768px)
  4. Test on mobile size (375px)

- **Expected Results:**
  - Desktop: 2+ column layout
  - Tablet: Single column with adjusted spacing
  - Mobile: Touch-friendly buttons and spacing
  - No horizontal scrolling needed
  - All content readable

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

## 🧪 TEST SUITE 2: PRACTICE SYSTEM

### Test Group 2.1: Challenge List

**Test 2.1.1 - Load Practice Index**
- **Steps:**
  1. Open http://localhost:3001/practice
  2. Wait for page load
  3. Verify challenges display

- **Expected Results:**
  - Page loads without errors
  - Challenge list displays
  - Each challenge shows title, difficulty, tags
  - Search box visible
  - Difficulty filter buttons visible

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 2.1.2 - Filter by Difficulty**
- **Steps:**
  1. Click "Easy" difficulty button
  2. Verify list shows only easy challenges
  3. Click "Medium" difficulty
  4. Verify list updates
  5. Click "Hard" difficulty
  6. Verify list updates

- **Expected Results:**
  - Filter buttons highlight when selected
  - Challenge list filters correctly
  - Challenge counts match selected difficulty
  - "All Difficulties" button resets filter

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 2.1.3 - Search Challenges**
- **Steps:**
  1. Click search box
  2. Type "array" or other keyword
  3. Verify results filter
  4. Clear search
  5. Verify all challenges reappear

- **Expected Results:**
  - Search filters challenges in real-time
  - Only matching challenges show
  - Search works on title and description
  - Clearing search restores full list

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

### Test Group 2.2: Challenge Editor

**Test 2.2.1 - Open Challenge**
- **Steps:**
  1. Click on any challenge from list
  2. Wait for challenge detail page to load
  3. Verify editor loads

- **Expected Results:**
  - Problem description displays
  - Code editor loads
  - Language selector visible (Python, JavaScript, etc.)
  - Run and Submit buttons available

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 2.2.2 - Write and Run Code**
- **Steps:**
  1. In code editor, write simple Python code:
     ```python
     def solution(n):
         return n * 2
     ```
  2. Click "Run" or "Execute" button
  3. Verify output displays

- **Expected Results:**
  - Code editor accepts input
  - Run button executes code
  - Output panel shows results
  - Execution is reasonably fast (<5 seconds)
  - No console errors

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 2.2.3 - Change Language**
- **Steps:**
  1. Click language selector dropdown
  2. Select a different language (JavaScript, Java, etc.)
  3. Verify syntax highlighting changes
  4. Verify placeholder code updates

- **Expected Results:**
  - Language dropdown works
  - Syntax highlighting changes with language
  - Editor shows appropriate placeholder for new language

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 2.2.4 - Test Cases Display**
- **Steps:**
  1. Scroll down to test cases section
  2. Verify test cases display
  3. Check expected vs actual output

- **Expected Results:**
  - Test cases show input and expected output
  - After running code, actual output displays
  - Visual indication if test passed/failed
  - Number of passing tests shown

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 2.2.5 - Submit Solution**
- **Steps:**
  1. Write a working solution
  2. Click "Submit" button
  3. Wait for submission to process

- **Expected Results:**
  - Submit button shows loading state
  - Submission processes
  - Success message displays if correct
  - Challenge marked as completed
  - Score/coins awarded (if applicable)

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

### Test Group 2.3: Submissions History

**Test 2.3.1 - View Submissions Page**
- **Steps:**
  1. Navigate to http://localhost:3001/practice/submissions
  2. Wait for page load
  3. Verify submissions display

- **Expected Results:**
  - Submissions page loads
  - List of past submissions shows
  - Each submission shows challenge, status, date
  - Status badges (Accepted, Wrong Answer, etc.)

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 2.3.2 - Filter Submissions**
- **Steps:**
  1. Look for status filter buttons
  2. Click "Accepted" filter
  3. Verify only accepted submissions show
  4. Try other status filters

- **Expected Results:**
  - Filter buttons available for statuses
  - Filters work correctly
  - Submission count updates
  - Can view all submissions again

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 2.3.3 - View Past Code**
- **Steps:**
  1. Click on a past submission
  2. Verify submitted code displays
  3. Check code is correct

- **Expected Results:**
  - Past code loads and displays
  - Syntax highlighting applies
  - Code is read-only (not editable in submissions)
  - Language shown with code

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

### Test Group 2.4: Leaderboard

**Test 2.4.1 - View Leaderboard**
- **Steps:**
  1. Navigate to http://localhost:3001/practice/leaderboard
  2. Wait for page load
  3. Verify rankings display

- **Expected Results:**
  - Leaderboard page loads
  - Top users listed with rank
  - User names and scores/challenges solved shown
  - Ranking positions visible (1st, 2nd, 3rd, etc.)

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 2.4.2 - Time Period Filter**
- **Steps:**
  1. Look for time period buttons (Week, Month, All-time)
  2. Click "Weekly"
  3. Verify leaderboard updates
  4. Click "Monthly"
  5. Verify update
  6. Click "All-time"
  7. Verify update

- **Expected Results:**
  - All time periods available
  - Leaderboard updates appropriately
  - Rankings change based on time period
  - Current selection highlighted

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 2.4.3 - User Stats**
- **Steps:**
  1. Examine leaderboard entries
  2. Verify all user information displays

- **Expected Results:**
  - User rank/position shown
  - User name/avatar visible
  - Challenges solved count shown
  - Points or coins displayed
  - Rankings are in correct order

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

### Test Group 2.5: Cloud Simulator (If Applicable)

**Test 2.5.1 - Open Simulator**
- **Steps:**
  1. Find and click Cloud Simulator link
  2. Wait for simulator to load
  3. Verify terminal/file system ready

- **Expected Results:**
  - Simulator page loads
  - Terminal interface visible
  - File system accessible
  - Command prompt ready

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

## 📊 INTEGRATION TESTS

### Test 3.1: API Backend Connectivity

**Test 3.1.1 - Forum Routes Available**
- **Steps:**
  ```bash
  curl http://localhost:8001/api/v1x/forums/categories
  curl http://localhost:8001/api/v1x/forums/threads
  curl http://localhost:8001/api/v1x/forums/threads/1/replies
  ```

- **Expected Results:**
  - All endpoints return HTTP 200 (or 401 for auth-required)
  - Responses contain proper JSON
  - Data structure matches expectations

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 3.1.2 - Practice Routes Available**
- **Steps:**
  ```bash
  curl http://localhost:8001/api/v1x/practice/challenges
  curl http://localhost:8001/api/v1x/practice/submissions
  curl http://localhost:8001/api/v1x/practice/leaderboard
  ```

- **Expected Results:**
  - All endpoints return HTTP 200
  - Responses contain proper JSON
  - Data structure matches expectations

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

### Test 3.2: Frontend-Backend Integration

**Test 3.2.1 - Forum Data Loading**
- **Steps:**
  1. Open browser DevTools (F12)
  2. Go to Network tab
  3. Navigate to http://localhost:3001/forums
  4. Observe API calls

- **Expected Results:**
  - API calls to /api/v1x/forums/categories
  - API calls to /api/v1x/forums/threads
  - HTTP 200 status for all calls
  - Data loads into UI

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

**Test 3.2.2 - Practice Data Loading**
- **Steps:**
  1. Open browser DevTools
  2. Go to Network tab
  3. Navigate to http://localhost:3001/practice
  4. Observe API calls

- **Expected Results:**
  - API calls to /api/v1x/practice/challenges
  - HTTP 200 status
  - Challenges load into list

- **Pass/Fail:** [ ] Pass [ ] Fail
- **Notes:** ___________

---

## 🎯 SUMMARY REPORT

### Test Results

**Forum System Tests:**
- Group 1.1 (Index Page): [ ] Pass [ ] Fail
- Group 1.2 (Creation): [ ] Pass [ ] Fail
- Group 1.3 (Detail): [ ] Pass [ ] Fail
- Group 1.4 (Replies): [ ] Pass [ ] Fail
- Group 1.5 (UX): [ ] Pass [ ] Fail

**Practice System Tests:**
- Group 2.1 (List): [ ] Pass [ ] Fail
- Group 2.2 (Editor): [ ] Pass [ ] Fail
- Group 2.3 (Submissions): [ ] Pass [ ] Fail
- Group 2.4 (Leaderboard): [ ] Pass [ ] Fail
- Group 2.5 (Simulator): [ ] Pass [ ] Fail

**Integration Tests:**
- Group 3.1 (API): [ ] Pass [ ] Fail
- Group 3.2 (Frontend-Backend): [ ] Pass [ ] Fail

---

### Overall Score

**Total Tests:** 40+  
**Passed:** _____ 
**Failed:** _____  
**Success Rate:** _____%

---

### Issues Found

| # | Component | Issue | Severity | Notes |
|---|-----------|-------|----------|-------|
| 1 | | | [ ] High [ ] Medium [ ] Low | |
| 2 | | | [ ] High [ ] Medium [ ] Low | |
| 3 | | | [ ] High [ ] Medium [ ] Low | |

---

### Recommendations

- [ ] All tests passed - ready for production
- [ ] Minor fixes needed - schedule for next sprint
- [ ] Major issues found - address before deployment
- [ ] Additional testing needed - specify areas

---

**Tester Name:** _______________  
**Date:** _______________  
**Sign-Off:** _______________

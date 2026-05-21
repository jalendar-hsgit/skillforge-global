# Testing Video Progress & Badges - Step-by-Step Guide

**Purpose:** Verify both features work without breaking existing functionality  
**Time:** ~10-15 minutes  
**Difficulty:** Easy - just copy/paste commands

---

## Prerequisites

✅ Backend running on http://localhost:8001  
✅ Frontend running on http://localhost:3000  
✅ Logged in with test account (john.doe@example.com / password123 OR create new)

---

## Part 1: Video Progress Tracking

### 1.1 Test Progress API Endpoint

**Goal:** Verify progress can be saved and retrieved

```bash
# Open PowerShell and get your auth token
# First, login to get token
curl -X POST "http://localhost:8001/api/v1/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "john.doe@example.com",
    "password": "password123"
  }' | ConvertFrom-Json | Select-Object -ExpandProperty access_token

# Save the token (replace YOUR_TOKEN below)
$TOKEN = "YOUR_TOKEN"

# Test 1: Update progress to 25%
curl -X POST "http://localhost:8001/api/v1x/progress-db" `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    "video_id": 1,
    "progress_percent": 25
  }'

# Expected response: {"ok": true}
```

**Expected Result:**
- Response shows `{"ok": true}`
- No errors in console

### 1.2 Test Progress Retrieval

```bash
# Get all progress records
curl -X GET "http://localhost:8001/api/v1x/progress-db" `
  -H "Authorization: Bearer $TOKEN"

# Expected: List of progress records including video_id 1 with 25% progress
```

**Expected Result:**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "video_id": 1,
    "progress_percent": 25,
    "updated_at": "2026-01-21T02:15:00"
  }
]
```

### 1.3 Test Progress Bar in Browser

**Goal:** See progress bar on video watch page

```
1. Go to http://localhost:3000
2. Navigate to a learning path or marketplace
3. Click on a video to watch
4. Should see a progress bar below the video title
5. Progress bar should be empty (or show previous progress if exists)
```

**Expected Result:**
- Progress bar visible
- Shows 0% or previous progress
- Color starts red/orange
- "0% Complete" text shows

### 1.4 Test Progress Update in Browser

```javascript
// Open browser console (F12) on watch page and run:
fetch('/api/v1x/progress-db', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  credentials: 'include',
  body: JSON.stringify({
    video_id: 1,
    progress_percent: 50
  })
})
.then(r => r.json())
.then(d => console.log('Success:', d))
.catch(e => console.error('Error:', e))
```

**Expected Result:**
- Console shows `Success: {ok: true}`
- Page doesn't refresh
- Progress bar should update (if page auto-refreshes)

### 1.5 Test Course Completion (Triggers Badge Award)

```bash
# Update progress to 100% to complete course
curl -X POST "http://localhost:8001/api/v1x/progress-db" `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    "video_id": 1,
    "progress_percent": 100
  }'

# Then check if badge was awarded
curl -X GET "http://localhost:8001/api/v1x/badges/user/earned" `
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:**
- Progress update returns `{"ok": true}`
- Badge endpoint returns list of badges (may be empty if no completion badges set up)

---

## Part 2: Badge System

### 2.1 Test Get All Badges

**Goal:** Verify badge system is accessible

```bash
curl -X GET "http://localhost:8001/api/v1x/badges" `
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:**
```json
[
  {
    "id": 1,
    "name": "First Step",
    "description": "Complete your first challenge",
    "icon_url": "https://...",
    "category": "challenge",
    "rarity": "common",
    "points_value": 5,
    "is_active": true
  },
  ...
]
```

- Should return array of badge objects
- Each badge has: id, name, description, icon, rarity, points
- If empty, that's okay (no badges created yet)

### 2.2 Test Get User's Earned Badges

**Goal:** See which badges user has earned

```bash
curl -X GET "http://localhost:8001/api/v1x/badges/user/earned" `
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:**
```json
[
  {
    "user_id": 123,
    "badge_id": 1,
    "first_earned_at": "2026-01-21T02:15:00",
    "last_earned_at": "2026-01-21T02:15:00",
    "earn_count": 1,
    "badge": {
      "id": 1,
      "name": "First Step",
      ...
    }
  }
]
```

- Should return array of earned badges (may be empty)
- Shows when badge was earned

### 2.3 Test Get Badge Stats

**Goal:** See badge statistics

```bash
curl -X GET "http://localhost:8001/api/v1x/badges/user/stats" `
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:**
```json
{
  "total_earned_badges": 0,
  "total_points": 0,
  "in_progress_count": 0,
  "achievements_count": 0,
  "rare_badges": 0,
  "epic_badges": 0,
  "legendary_badges": 0
}
```

- Shows user's badge statistics
- May be zeros if no badges earned yet

### 2.4 Test Badges on Profile Page

**Goal:** See badges displayed on profile

```
1. Go to http://localhost:3000/profile
2. Scroll down to "Achievements" section
3. Should see badge grid displayed
4. Badges show in color-coded sections:
   - "Earned Badges" (top)
   - "Locked Badges" (bottom)
5. Each badge shows:
   - Icon/image
   - Rarity level
   - Name and description
   - Points value
   - Date earned (if earned)
   - "Locked" label (if not earned)
```

**Expected Result:**
- Achievements section visible
- Badge grid displays correctly
- Colors match rarity levels
- No console errors

---

## Part 3: Regression Testing

### 3.1 Test Authentication Still Works

```bash
# Login should still work normally
curl -X POST "http://localhost:8001/api/v1/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "john.doe@example.com",
    "password": "password123"
  }'
```

**Expected Result:** Valid token returned

### 3.2 Test Courses Still Work

```bash
curl -X GET "http://localhost:8001/api/v1x/courses" `
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:** List of courses returned

### 3.3 Test Mentors Still Work

```bash
curl -X GET "http://localhost:8001/api/v1x/mentors" `
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:** List of mentors returned

### 3.4 Test Watch Page Still Works

```
1. Go to http://localhost:3000/watch/1
2. Should load video player
3. Should show video title and controls
4. Progress bar should be visible (new feature)
5. Video player should work normally
```

**Expected Result:**
- Video loads
- Player controls work
- Progress bar shows
- No console errors

### 3.5 Test Profile Page Still Works

```
1. Go to http://localhost:3000/profile
2. Should show profile card
3. Should show statistics
4. Should show achievements section (new feature)
5. Should show quick stats
```

**Expected Result:**
- Profile loads completely
- All sections render
- No console errors

---

## Part 4: Quick Diagnostic Test

**Run entire system check:**

```bash
# PowerShell script to test all endpoints

$TOKEN = "YOUR_TOKEN"  # From login above
$results = @()

# Test 1: Backend health
try {
    $health = curl -X GET "http://localhost:8001/healthz" -s
    $results += "✓ Backend Health: OK"
} catch {
    $results += "✗ Backend Health: FAILED - $_"
}

# Test 2: Auth
try {
    $auth = curl -X POST "http://localhost:8001/api/v1/auth/login" `
      -H "Content-Type: application/json" `
      -d '{"email":"john.doe@example.com","password":"password123"}' -s | ConvertFrom-Json
    $results += "✓ Authentication: OK"
} catch {
    $results += "✗ Authentication: FAILED - $_"
}

# Test 3: Courses
try {
    $courses = curl -X GET "http://localhost:8001/api/v1x/courses" `
      -H "Authorization: Bearer $TOKEN" -s
    $results += "✓ Courses: OK"
} catch {
    $results += "✗ Courses: FAILED - $_"
}

# Test 4: Progress
try {
    $progress = curl -X GET "http://localhost:8001/api/v1x/progress-db" `
      -H "Authorization: Bearer $TOKEN" -s
    $results += "✓ Progress: OK"
} catch {
    $results += "✗ Progress: FAILED - $_"
}

# Test 5: Badges
try {
    $badges = curl -X GET "http://localhost:8001/api/v1x/badges" `
      -H "Authorization: Bearer $TOKEN" -s
    $results += "✓ Badges: OK"
} catch {
    $results += "✗ Badges: FAILED - $_"
}

# Test 6: Mentors
try {
    $mentors = curl -X GET "http://localhost:8001/api/v1x/mentors" `
      -H "Authorization: Bearer $TOKEN" -s
    $results += "✓ Mentors: OK"
} catch {
    $results += "✗ Mentors: FAILED - $_"
}

# Display results
Write-Host "DIAGNOSTIC TEST RESULTS:"
Write-Host "======================="
foreach ($result in $results) {
    Write-Host $result
}
```

---

## Part 5: Troubleshooting

### Issue: "404 not found" on progress endpoint

**Solution:**
```
1. Make sure backend is running on port 8001
2. Check URL is exactly: /api/v1x/progress-db
3. Check authorization header is correct
4. Try: http://localhost:8001/healthz first to verify backend
```

### Issue: "Unauthorized" error

**Solution:**
```
1. Make sure token is valid (not expired)
2. Login again to get fresh token:
   curl -X POST "http://localhost:8001/api/v1/auth/login" ...
3. Include full token in header:
   -H "Authorization: Bearer [FULL_TOKEN]"
```

### Issue: Progress bar not showing on watch page

**Solution:**
```
1. Check browser console for errors (F12)
2. Make sure you're logged in
3. Try hard refresh (Ctrl+Shift+R)
4. Check video ID is valid in URL: /watch/1 (or /watch/2, etc)
```

### Issue: Badges not showing on profile

**Solution:**
```
1. Check profile page loads: /profile
2. Scroll down to "Achievements" section
3. Check browser console (F12) for errors
4. Make sure you're logged in
5. Try clearing cache and reload
```

---

## Summary Checklist

Use this checklist to verify everything works:

### Video Progress
- [ ] Progress API endpoint responds (POST)
- [ ] Progress retrieval works (GET)
- [ ] Progress bar displays in browser
- [ ] Progress updates when clicking "Mark Complete"
- [ ] Progress persists after page refresh

### Badges
- [ ] Badge API endpoint responds (GET /badges)
- [ ] User badges endpoint works (GET /badges/user/earned)
- [ ] Badge stats endpoint works (GET /badges/user/stats)
- [ ] Badges display on profile page
- [ ] Badge rarity colors are correct
- [ ] No console errors on profile page

### Regression Tests
- [ ] Authentication still works
- [ ] Can view courses
- [ ] Can view mentors
- [ ] Can watch videos
- [ ] Profile page loads
- [ ] No errors in backend console

### Final Status
- [ ] All tests pass
- [ ] No breaking changes observed
- [ ] Ready for production use

---

## Next Steps

Once testing is complete:

1. ✅ **Document Results** - Keep this checklist for reference
2. ✅ **User Training** - Show users the new features
3. ✅ **Monitor** - Watch for any issues in production
4. ✅ **Seed Badges** - Create actual badges in database if not done
5. ✅ **Future Enhancements** - Plan next phase features

---

**Questions?** Check the main implementation document:  
`VIDEO_PROGRESS_BADGES_IMPLEMENTATION.md`

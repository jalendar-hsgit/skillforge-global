# Phase 2.5 Full Testing Execution Guide

## 🎯 Objective
Execute comprehensive testing of Phase 2.5 Backend Settings Integration to verify all features work correctly before proceeding to Phase 3A.

## ⏱️ Timeline
- **Setup & Start Services:** 3-5 minutes
- **Quick Tests (1-4):** 5 minutes
- **API Testing with curl:** 10 minutes
- **Comprehensive Tests (5-16+):** 20-30 minutes
- **Error & Edge Case Testing:** 15 minutes
- **Database Verification:** 5 minutes
- **Total Estimated Time:** 60-90 minutes

---

## 📋 Phase 1: Setup (3-5 minutes)

### Step 1.1: Prepare Database
```bash
# Terminal 1 (from project root)
cd backend

# OPTION A: Reset database (if needed)
rm app/data/skillforge.db

# Seed demo data
python seed_all_demo_data.py
```

**Expected Output:**
```
✓ Created 7 users
✓ Created 4 mentors
✓ Created 5 courses
✓ Seeding complete
```

### Step 1.2: Start Backend Service
```bash
# Terminal 1 (from backend directory)
python -m uvicorn app.main:app --reload --port 8001
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete
```

**Verification:**
- [ ] Backend running at `http://localhost:8001`
- [ ] No errors in console
- [ ] Ready for requests

### Step 1.3: Start Frontend Service
```bash
# Terminal 2 (from project root)
npm run dev
```

**Expected Output:**
```
> next dev
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

**Verification:**
- [ ] Frontend running at `http://localhost:3000`
- [ ] No errors in console
- [ ] Page loads in browser

---

## 🧪 Phase 2: Quick Functionality Tests (5 minutes)

### Test 1: Login & Navigate to Settings

**Steps:**
1. Open `http://localhost:3000` in browser
2. Click "Sign In" button
3. Enter email: `john.doe@example.com`
4. Enter password: `password123`
5. Click "Sign In"
6. Wait for redirect to `/dashboard`

**Verification:**
- [ ] Login successful
- [ ] Redirected to dashboard
- [ ] User name appears (John Doe)
- [ ] "View My Profile" button visible at bottom

**Expected:** ✅ Logged in successfully

---

### Test 2: Navigate to Settings Page

**Steps:**
1. From dashboard, click "View My Profile" button (blue gradient at bottom)
2. On profile page, find Settings link (or go directly to `/settings`)
3. Wait for Settings page to load

**Verification:**
- [ ] Profile page loads
- [ ] Settings page loads
- [ ] Page title is "Settings"
- [ ] No loading spinner
- [ ] All 4 sections visible:
  - [ ] Notifications (with 🔔 icon)
  - [ ] Privacy & Security (with 🔒 icon)
  - [ ] Preferences (with 🎨 icon)
  - [ ] Account (with 👤 icon)

**Expected:** ✅ Settings page loaded successfully

---

### Test 3: Verify Settings Load from API

**Steps:**
1. On Settings page, open DevTools: `F12`
2. Go to Network tab
3. Refresh page: `F5`
4. Look for `GET /api/v1x/account/settings` request

**Verification:**
- [ ] GET request to `/api/v1x/account/settings` appears
- [ ] Status code is 200
- [ ] Response contains all 8 fields:
  - [ ] email_notifications
  - [ ] push_notifications
  - [ ] two_factor_enabled
  - [ ] theme
  - [ ] language
  - [ ] timezone
  - [ ] profile_visibility
  - [ ] activity_status
- [ ] All toggles show correct state (ON/OFF)
- [ ] All dropdowns show correct value
- [ ] No "undefined" values

**Expected:** ✅ Settings loaded from API successfully

---

### Test 4: Toggle a Setting and Save

**Steps:**
1. Click "Email Notifications" toggle
2. Toggle should switch OFF (gray)
3. Click "Save Settings" button
4. Watch for status change

**Verification:**
- [ ] Toggle switches visually
- [ ] Button shows "Saving..." status
- [ ] PATCH request appears in Network tab
- [ ] Request goes to `/api/v1x/account/settings`
- [ ] Request body shows: `{"email_notifications": false}`
- [ ] Response status is 200
- [ ] Button shows "✓ Saved" (green)
- [ ] Status auto-clears after 2 seconds
- [ ] Return to "Save Settings" text

**Expected:** ✅ Setting saved successfully

---

## 🔌 Phase 3: API Endpoint Testing (10 minutes)

### Prerequisites: Get JWT Token

**Steps:**
1. Open new terminal (Terminal 3)
2. Get login token:

```bash
# Replace with actual credentials
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@example.com","password":"password123"}' | jq '.access_token' -r
```

**Expected Output:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Verification:**
- [ ] Token obtained successfully
- [ ] Token is long string (not error message)
- [ ] Save token for next tests: `TOKEN=eyJ...`

---

### Test 5: GET Settings Endpoint (API)

**Steps:**
```bash
TOKEN="paste_your_token_here"

curl -X GET http://localhost:8001/api/v1x/account/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response:**
```json
{
  "email_notifications": false,
  "push_notifications": true,
  "two_factor_enabled": false,
  "theme": "auto",
  "language": "en",
  "timezone": "UTC",
  "profile_visibility": "public",
  "activity_status": true
}
```

**Verification:**
- [ ] Status code: 200
- [ ] All 8 fields present
- [ ] email_notifications: false (from previous test)
- [ ] All fields have correct values
- [ ] No errors in response

**Expected:** ✅ GET endpoint working correctly

---

### Test 6: PATCH Settings Endpoint (Single Field)

**Steps:**
```bash
TOKEN="paste_your_token_here"

curl -X PATCH http://localhost:8001/api/v1x/account/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme":"dark"}' | jq .
```

**Expected Response:**
```json
{
  "email_notifications": false,
  "push_notifications": true,
  "two_factor_enabled": false,
  "theme": "dark",
  "language": "en",
  "timezone": "UTC",
  "profile_visibility": "public",
  "activity_status": true
}
```

**Verification:**
- [ ] Status code: 200
- [ ] theme changed to "dark"
- [ ] Other fields unchanged
- [ ] Response includes all 8 fields

**Expected:** ✅ PATCH single field working

---

### Test 7: PATCH Settings Endpoint (Multiple Fields)

**Steps:**
```bash
TOKEN="paste_your_token_here"

curl -X PATCH http://localhost:8001/api/v1x/account/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"timezone":"EST","language":"es"}' | jq .
```

**Expected Response:**
```json
{
  "email_notifications": false,
  "push_notifications": true,
  "two_factor_enabled": false,
  "theme": "dark",
  "language": "es",
  "timezone": "EST",
  "profile_visibility": "public",
  "activity_status": true
}
```

**Verification:**
- [ ] Status code: 200
- [ ] timezone changed to "EST"
- [ ] language changed to "es"
- [ ] Other fields unchanged
- [ ] All 8 fields in response

**Expected:** ✅ PATCH multiple fields working

---

### Test 8: PATCH Boolean Toggle

**Steps:**
```bash
TOKEN="paste_your_token_here"

curl -X PATCH http://localhost:8001/api/v1x/account/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"two_factor_enabled":true}' | jq .
```

**Expected Response:**
```json
{
  ...
  "two_factor_enabled": true,
  ...
}
```

**Verification:**
- [ ] Status code: 200
- [ ] two_factor_enabled changed to true
- [ ] Boolean conversion working (true/false)
- [ ] Other fields preserved

**Expected:** ✅ Boolean conversion working

---

## 🌐 Phase 4: Frontend Comprehensive Tests (20-30 minutes)

### Test 9: Persistence After Refresh

**Steps:**
1. Go back to browser with Settings page
2. Verify current state shows:
   - Email Notifications: OFF
   - Theme: Dark
   - Language: Español (es)
   - Timezone: EST
   - 2FA: ON
3. Refresh page: `F5`
4. Wait for page to reload
5. Check Network tab for GET request
6. Verify all values still match

**Verification:**
- [ ] Page loads without errors
- [ ] GET request made automatically
- [ ] All settings persist after refresh:
   - [ ] Email Notifications: OFF
   - [ ] Theme: Dark
   - [ ] Language: Español
   - [ ] Timezone: EST
   - [ ] 2FA: ON

**Expected:** ✅ Settings persist across refreshes

---

### Test 10: Change Multiple Settings Together

**Steps:**
1. Make multiple changes:
   - Toggle "Push Notifications" OFF
   - Change "Profile Visibility" to "Private"
   - Change "Timezone" to "PST"
2. Click "Save Settings"
3. Wait for "✓ Saved" status

**Verification:**
- [ ] All toggles update visually
- [ ] All dropdowns show correct values
- [ ] Single PATCH request sent
- [ ] Request includes all 3 changed fields
- [ ] Status shows "✓ Saved"

**Expected:** ✅ Multiple changes saved together

---

### Test 11: Verify UI Status Feedback

**Steps:**
1. Click "Save Settings"
2. Observe button text change

**Verification:**
- [ ] Button immediately shows "Saving..."
- [ ] After ~1 second shows "✓ Saved" (green)
- [ ] After 2 seconds returns to "Save Settings"
- [ ] Color feedback: Saving (normal) → Saved (green) → normal

**Expected:** ✅ Status feedback working

---

### Test 12: Cancel Button Navigation

**Steps:**
1. Click "Cancel" button
2. Observe navigation

**Verification:**
- [ ] Redirected to `/dashboard`
- [ ] Dashboard page loads
- [ ] User still logged in

**Expected:** ✅ Cancel navigates correctly

---

### Test 13: Links in Settings

**Steps:**
1. Click "View Profile" link in Account section
2. Verify navigation to profile page
3. Go back to settings
4. Click "Change Password" link
5. Verify navigation (even if page doesn't exist yet)

**Verification:**
- [ ] "View Profile" goes to `/profile`
- [ ] Profile page loads
- [ ] "Change Password" link goes to `/security/change-password`
- [ ] Links use proper routing

**Expected:** ✅ Links working correctly

---

### Test 14: Logout Button

**Steps:**
1. Click "Logout" link in Account section
2. Observe result

**Verification:**
- [ ] Logout executed
- [ ] Redirected to login page (or home)
- [ ] Session cleared (auth token removed)
- [ ] Can't access settings without logging in again

**Expected:** ✅ Logout working

---

## ⚠️ Phase 5: Error & Edge Case Testing (15 minutes)

### Test 15: Network Error Handling

**Steps:**
1. Stop backend server: `Ctrl+C` in Terminal 1
2. On Settings page, make a change
3. Click "Save Settings"
4. Observe error handling

**Verification:**
- [ ] Request fails (network error)
- [ ] Button shows "✗ Error" (red)
- [ ] Error doesn't crash page
- [ ] Can still interact with page
- [ ] Error auto-clears after 2 seconds

**Steps (Cleanup):**
1. Restart backend: `python -m uvicorn app.main:app --reload --port 8001`
2. Wait for "Application startup complete"

**Expected:** ✅ Error handling working

---

### Test 16: Invalid Field Value (Validation)

**Steps:**
1. Use curl to test invalid theme:

```bash
TOKEN="your_token"

curl -X PATCH http://localhost:8001/api/v1x/account/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme":"invalid_theme"}' | jq .
```

**Expected Response:**
```json
{
  "detail": "Invalid input"
  // OR validation error message
}
```

**Verification:**
- [ ] Request rejected (4xx status)
- [ ] Error message provided
- [ ] Invalid value not saved to database

**Expected:** ✅ Validation working

---

### Test 17: Unauthorized Access (No Token)

**Steps:**
```bash
# Without Authorization header
curl -X GET http://localhost:8001/api/v1x/account/settings \
  -H "Content-Type: application/json" | jq .
```

**Expected Response:**
```json
{"detail": "Not authenticated"}
```

**Verification:**
- [ ] Status code: 401 (Unauthorized)
- [ ] Error message provided
- [ ] Access denied without token

**Expected:** ✅ Authentication required

---

### Test 18: Invalid Token

**Steps:**
```bash
# With invalid token
curl -X GET http://localhost:8001/api/v1x/account/settings \
  -H "Authorization: Bearer invalid_token_xyz" \
  -H "Content-Type: application/json" | jq .
```

**Expected Response:**
```json
{"detail": "Invalid credentials"}
```

**Verification:**
- [ ] Status code: 401
- [ ] Error message provided
- [ ] Access denied with invalid token

**Expected:** ✅ Token validation working

---

## 💾 Phase 6: Database Verification (5 minutes)

### Test 19: Verify Database Persistence

**Steps:**
```bash
# Terminal 3
# Navigate to backend directory
cd backend

# Open SQLite CLI
sqlite3 app/data/skillforge.db

# Inside sqlite3:
SELECT email, email_notifications, theme, language, timezone, two_factor_enabled 
FROM users 
WHERE email = 'john.doe@example.com';
```

**Expected Output:**
```
john.doe@example.com|0|dark|es|EST|1
```

**Verification:**
- [ ] Database file exists
- [ ] User row exists
- [ ] email_notifications = 0 (false)
- [ ] theme = "dark"
- [ ] language = "es"
- [ ] timezone = "EST"
- [ ] two_factor_enabled = 1 (true)

**Steps (Exit SQLite):**
```
.quit
```

**Expected:** ✅ Database persistence verified

---

## 📱 Phase 7: Responsive Design Check (Optional - 5 minutes)

### Test 20: Mobile View

**Steps:**
1. Open Settings page in browser
2. Press `F12` for DevTools
3. Press `Ctrl+Shift+M` to toggle device toolbar
4. Select "iPhone 12" or similar
5. Test functionality on mobile view

**Verification:**
- [ ] Layout stacks vertically
- [ ] Text is readable
- [ ] Toggles are clickable
- [ ] Dropdowns work
- [ ] Buttons are full width
- [ ] No horizontal scroll
- [ ] All 4 sections visible

**Expected:** ✅ Responsive design working

---

## ✅ Final Checklist

### All Tests Passed?
- [ ] Test 1: Login & Navigate ✓
- [ ] Test 2: Settings Page Loads ✓
- [ ] Test 3: API Load ✓
- [ ] Test 4: Save Toggle ✓
- [ ] Test 5: GET Endpoint ✓
- [ ] Test 6: PATCH Single Field ✓
- [ ] Test 7: PATCH Multiple Fields ✓
- [ ] Test 8: Boolean Conversion ✓
- [ ] Test 9: Persistence ✓
- [ ] Test 10: Multiple Changes ✓
- [ ] Test 11: Status Feedback ✓
- [ ] Test 12: Cancel Navigation ✓
- [ ] Test 13: Links ✓
- [ ] Test 14: Logout ✓
- [ ] Test 15: Error Handling ✓
- [ ] Test 16: Validation ✓
- [ ] Test 17: Unauthorized ✓
- [ ] Test 18: Invalid Token ✓
- [ ] Test 19: Database ✓
- [ ] Test 20: Responsive (Optional) ✓

### Overall Status: 🟢 ALL TESTS PASSING

---

## 🎯 Next Steps

If all tests pass (✅):
1. You're ready to proceed to **Phase 3A: Mentor Verification System**
2. Start Phase 3A planning and implementation

If any tests fail (❌):
1. Check error message
2. See troubleshooting in PHASE2_5_TESTING_GUIDE.md
3. Fix issue and re-run failed test
4. Proceed when all pass

---

## 🚀 Ready to Test?

**Services to Keep Running:**
- Terminal 1: Backend (`python -m uvicorn app.main:app --reload --port 8001`)
- Terminal 2: Frontend (`npm run dev`)
- Terminal 3: For curl commands and database checks

**Let's verify Phase 2.5 is working perfectly, then move to Phase 3A!**

# Phase 2.5: Backend Settings Integration - Testing Guide

## Overview
Phase 2.5 integrates the frontend Settings page with real backend API endpoints. Users can now save and retrieve their settings (notifications, theme, timezone, etc.) from the database.

## Changes Made

### 1. Backend Changes

#### User Model (`backend/app/models/user.py`)
Added 8 new columns to the User table:
- `email_notifications` (Integer: 0/1) - Default: 1 (True)
- `push_notifications` (Integer: 0/1) - Default: 1 (True)
- `two_factor_enabled` (Integer: 0/1) - Default: 0 (False)
- `theme` (String) - Default: "auto"
- `language` (String) - Default: "en"
- `timezone` (String) - Default: "UTC"
- `profile_visibility` (String) - Default: "public"
- `activity_status` (Integer: 0/1) - Default: 1 (True)

#### API Endpoints (`backend/app/api/v1x/account.py`)
**GET /api/v1x/account/settings**
- Retrieves user settings with boolean conversion (0/1 → true/false)
- Returns: UserSettingsResponse with 8 fields
- Auth: Requires JWT token (Bearer token)
- Error: 404 if user not found

**PATCH /api/v1x/account/settings**
- Updates any subset of settings (all fields optional)
- Converts boolean → integer (true → 1, false → 0) for storage
- Returns: Updated UserSettingsResponse
- Auth: Requires JWT token
- Error: 404 if user not found
- Behavior: Only provided fields are updated (exclude_unset=True)

#### Schemas (`backend/app/schemas/user.py`)
- `UserSettingsResponse`: Response model with 8 fields and proper defaults
- `UserSettingsUpdate`: Request model with validation (regex for theme, language, profile_visibility)

### 2. Frontend Changes

#### Settings Page (`src/pages/settings/index.tsx`)
**New: Fetch Settings on Load**
```typescript
useEffect(() => {
  if (user && !authLoading && !loading) {
    fetchSettings()
  }
}, [user, authLoading, loading])

const fetchSettings = async () => {
  const response = await fetch('/api/v1x/account/settings', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  })
  // Convert snake_case from API to camelCase
}
```

**Updated: Save Settings**
- Converts camelCase (frontend) to snake_case (backend)
- Makes PATCH request to `/api/v1x/account/settings`
- Shows status: "Saving..." → "✓ Saved" → "idle"
- Handles errors gracefully

**Field Mapping**
| Frontend (camelCase) | Backend (snake_case) |
|---|---|
| emailNotifications | email_notifications |
| pushNotifications | push_notifications |
| twoFactorEnabled | two_factor_enabled |
| profileVisibility | profile_visibility |
| activityStatus | activity_status |

---

## Testing Checklist

### ✅ Setup
- [ ] Backend running: `python -m uvicorn app.main:app --reload --port 8001` (from `backend/` dir)
- [ ] Frontend running: `npm run dev` (from repo root)
- [ ] Database has latest User model columns
- [ ] Logged in as demo user (john.doe@example.com / password)

### ✅ Verify API Endpoints

#### Test 1: GET Settings (Fetch)
```bash
curl -X GET http://localhost:8001/api/v1x/account/settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "email_notifications": true,
  "push_notifications": true,
  "two_factor_enabled": false,
  "theme": "auto",
  "language": "en",
  "timezone": "UTC",
  "profile_visibility": "public",
  "activity_status": true
}
```

#### Test 2: PATCH Settings (Update Theme)
```bash
curl -X PATCH http://localhost:8001/api/v1x/account/settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme": "dark"}'
```

**Expected Response:**
```json
{
  "email_notifications": true,
  "push_notifications": true,
  "two_factor_enabled": false,
  "theme": "dark",  # Changed
  "language": "en",
  "timezone": "UTC",
  "profile_visibility": "public",
  "activity_status": true
}
```

#### Test 3: PATCH Settings (Toggle Notification)
```bash
curl -X PATCH http://localhost:8001/api/v1x/account/settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_notifications": false}'
```

**Expected Response:**
```json
{
  "email_notifications": false,  # Changed
  "push_notifications": true,
  ...
}
```

### ✅ Frontend Testing

#### Test 4: Page Load - Settings Load from API
1. Navigate to `http://localhost:3000/settings`
2. Page should display current settings (fetched from backend)
3. Check Network tab → `GET /api/v1x/account/settings` (200 OK)
4. Settings should match database values

**Verification:**
- [ ] No "undefined" or loading spinner persists
- [ ] All toggles and dropdowns show correct values
- [ ] Network tab shows successful API call

#### Test 5: Toggle Email Notifications
1. On settings page, click "Email Notifications" toggle
2. Toggle should switch immediately (optimistic UI)
3. Click "Save Settings" button
4. Status should show "Saving..." → "✓ Saved"
5. Check Network tab → `PATCH /api/v1x/account/settings` with `{"email_notifications": false}`

**Verification:**
- [ ] Toggle visually changes
- [ ] Save button shows correct status
- [ ] API request sent with correct payload (snake_case)
- [ ] Response shows updated value

#### Test 6: Change Theme Dropdown
1. Click Theme dropdown, select "dark"
2. Dropdown shows "Dark" selected
3. Click "Save Settings"
4. Status shows "✓ Saved"
5. Refresh page
6. Theme dropdown should still show "dark"

**Verification:**
- [ ] Dropdown reflects selection
- [ ] API request includes `{"theme": "dark"}`
- [ ] Value persists after refresh
- [ ] API returns new value in GET response

#### Test 7: Change Multiple Settings at Once
1. Toggle "Push Notifications" OFF
2. Change Theme to "light"
3. Change Language to "es"
4. Change Timezone to "EST"
5. Click "Save Settings"
6. Verify all settings save correctly

**Verification:**
- [ ] All toggles update as changed
- [ ] Single PATCH request with 4 fields
- [ ] Status shows "✓ Saved"
- [ ] All values persist on refresh

#### Test 8: Verify Privacy & Security Settings
1. Toggle "Two-Factor Authentication" ON
2. Change "Profile Visibility" to "private"
3. Click "Save Settings"
4. Verify both save correctly

**Verification:**
- [ ] Both settings appear in PATCH request
- [ ] Both persist in database
- [ ] GET returns correct values

#### Test 9: Navigation & Links
1. Click "View Profile" link
2. Should navigate to `/profile` and show profile
3. Go back to settings
4. Click "Logout" link
5. Should log out and redirect to login page

**Verification:**
- [ ] Links navigate correctly
- [ ] Profile page shows data
- [ ] Logout clears session

#### Test 10: Error Handling
1. Stop backend server
2. On settings page, click "Save Settings"
3. Status should show "✗ Error"
4. Error should auto-clear after 2 seconds
5. Restart backend

**Verification:**
- [ ] Error status displays when API fails
- [ ] Error clears automatically
- [ ] No console errors (except network error)
- [ ] Can continue using page after error

### ✅ Database Verification

#### Test 11: Verify Database Persistence
```bash
# From backend directory
sqlite3 app/data/skillforge.db

# Check settings columns exist
.schema users

# Check settings for demo user
SELECT id, email, email_notifications, theme, timezone, profile_visibility 
FROM users 
WHERE email = 'john.doe@example.com';
```

**Expected Output:**
```
id | email | email_notifications | theme | timezone | profile_visibility
1  | john.doe@example.com | 1 | auto | UTC | public
```

After changing settings to theme="dark":
```
id | email | email_notifications | theme | timezone | profile_visibility
1  | john.doe@example.com | 1 | dark | UTC | public
```

### ✅ Responsive Design Testing

#### Test 12: Mobile/Tablet View
1. Open settings page on desktop
2. Press F12 (DevTools)
3. Toggle device toolbar (Ctrl+Shift+M)
4. Test on iPhone 12 (390px width)
5. Verify:
   - Layout stacks vertically
   - Toggles are clickable
   - Dropdowns are readable
   - Save/Cancel buttons are full width
   - No horizontal scroll

#### Test 13: Dark Mode Theme
1. Settings page should inherit dark theme
2. Background: Dark gradient
3. Text: White
4. Inputs: White/10 background
5. Verify good contrast and readability

### ✅ Security Testing

#### Test 14: Unauthenticated Access
1. Log out completely (clear tokens)
2. Try to navigate to `/settings` directly
3. Should redirect to `/login?redirect=/settings`
4. After login, should redirect back to `/settings`

#### Test 15: Invalid Token
1. In DevTools, go to Application → Cookies → localhost
2. Find auth token, manually edit it to invalid string
3. Refresh settings page
4. Should redirect to login page

#### Test 16: CSRF/CORS
1. Settings page should send `credentials: 'include'`
2. API should accept requests from frontend origin
3. Check Network tab → Request headers should include Authorization

---

## Quick Test Sequence (5 minutes)

1. **Start Services** (1 min)
   ```bash
   # Terminal 1: Backend
   cd backend
   python -m uvicorn app.main:app --reload --port 8001
   
   # Terminal 2: Frontend
   npm run dev
   ```

2. **Navigate to Settings** (1 min)
   - Go to `http://localhost:3000/dashboard`
   - Click "View My Profile" button
   - Click "Settings" link (or navigate directly to `/settings`)

3. **Test Save/Load Cycle** (2 min)
   - Verify initial settings load from API
   - Toggle "Email Notifications" OFF
   - Change Theme to "dark"
   - Click "Save Settings"
   - See "✓ Saved" status
   - Refresh page
   - Verify settings persisted (both still changed)

4. **Check Network** (1 min)
   - Open DevTools → Network tab
   - Repeat save
   - Verify:
     - GET request on page load: `/api/v1x/account/settings`
     - PATCH request on save: `/api/v1x/account/settings` with payload
     - Both return 200 OK

---

## Known Issues & Troubleshooting

### Issue: Settings page shows all default values
**Cause:** GET endpoint not being called, or user not authenticated
**Solution:**
1. Check browser console for errors
2. Verify JWT token is valid
3. Check Network tab → GET /api/v1x/account/settings returns 200
4. If 401, re-login

### Issue: Save button shows error immediately
**Cause:** API endpoint not responding or database not updated
**Solution:**
1. Verify backend is running (`http://localhost:8001/docs`)
2. Check if User model columns exist in database
3. Test PATCH endpoint manually with curl
4. Check backend logs for errors

### Issue: Settings not persisting after refresh
**Cause:** PATCH endpoint not committing to database
**Solution:**
1. Check backend logs for database errors
2. Verify `db.commit()` is being called in PATCH endpoint
3. Test PATCH with curl to see actual response
4. Check database manually with sqlite3

### Issue: TypeError: Cannot read property 'email_notifications' of undefined
**Cause:** API response doesn't include field
**Solution:**
1. Check API response format (should use snake_case)
2. Verify field mapping in fetchSettings()
3. Check backend schema has all 8 fields
4. Verify getattr() defaults are being used

---

## Success Criteria

✅ **All tests should pass:**
1. Settings page loads without errors
2. GET endpoint returns all 8 settings fields
3. PATCH endpoint updates any field successfully
4. Settings persist in database across page refreshes
5. Frontend converts camelCase ↔ snake_case correctly
6. Error handling shows "✗ Error" status
7. Unauthenticated users redirect to login
8. Responsive design works on mobile

✅ **No console errors:**
- No 404s for API calls
- No undefined variables
- No CORS errors
- No authentication errors

✅ **Network requests correct:**
- GET /api/v1x/account/settings on page load
- PATCH /api/v1x/account/settings with snake_case fields
- Both requests include Authorization header
- Credentials: include is set

---

## Next Steps After Phase 2.5

### Phase 3 Options:
1. **Mentor Verification System** (8-12 hours)
   - Mentor approval workflow
   - Verification document upload
   - Admin review dashboard

2. **Resume Features** (12-16 hours)
   - Resume upload and management
   - PDF preview
   - Share resume link

3. **Job Application Tracking** (6-10 hours)
   - Application status pipeline
   - Interview tracking
   - Contact history

### Related Tasks:
- [ ] Password change endpoint implementation
- [ ] Two-factor authentication setup
- [ ] Email notification preferences enforcement
- [ ] Theme application across all pages
- [ ] Language/i18n implementation

---

## Testing Log

Date: _______
Tester: _______

- [ ] Setup complete
- [ ] API endpoints tested (manual curl)
- [ ] Frontend page load tested
- [ ] Save/load cycle tested
- [ ] Error handling tested
- [ ] Database persistence verified
- [ ] Responsive design verified
- [ ] Security testing passed
- [ ] All 13+ tests passed

**Issues Found:**
_________________________________

**Status:** ☐ Ready for Phase 3 / ☐ Needs fixes

# Phase 2.5: Quick Start - Run & Test (5 minutes)

## One-Time Setup

### 1. Database Reset (if needed)
```bash
cd backend
# Remove old database if it has issues
rm app/data/skillforge.db

# Seed demo data (creates tables + demo users)
python seed_all_demo_data.py
```

## Start Services

### Terminal 1: Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete
```

### Terminal 2: Frontend
```bash
npm run dev
```

**Expected Output:**
```
> next dev
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

## Test Flow (5 minutes)

### Step 1: Login (1 min)
1. Open `http://localhost:3000`
2. Click "Sign In"
3. Email: `john.doe@example.com`
4. Password: `password123`
5. Click "Sign In"
6. Should redirect to `/dashboard`

### Step 2: Navigate to Settings (1 min)
1. From dashboard, click "View My Profile" button (blue gradient at bottom)
2. On profile page, look for "Settings" link (or navigate directly to `/settings`)
3. Settings page should load with all controls visible
4. Page title: "Settings"
5. 4 sections: Notifications, Privacy & Security, Preferences, Account

### Step 3: Test Load (1 min)
1. Open DevTools: F12
2. Go to Network tab
3. Refresh page (F5)
4. Should see `GET /api/v1x/account/settings` with 200 status
5. Response should show all 8 settings fields
6. All toggles and dropdowns should show values

### Step 4: Test Save (2 min)

**Test 4A: Toggle Notification**
1. Click "Email Notifications" toggle
2. Toggle should switch OFF (gray)
3. Click "Save Settings" button
4. Status shows "Saving..." → "✓ Saved"
5. Check Network tab → PATCH request to `/api/v1x/account/settings`
6. Payload should show: `{"email_notifications": false}`
7. Response should show updated value

**Test 4B: Change Theme**
1. Click Theme dropdown
2. Select "Dark"
3. Click "Save Settings"
4. Status shows "✓ Saved"
5. Network tab shows: `{"theme": "dark"}`

**Test 4C: Persistence**
1. Refresh page (F5)
2. Email Notifications should still be OFF
3. Theme should still be "dark"
4. Network tab shows GET request with updated values

### Step 5: Error Handling (optional, 30 sec)
1. Stop backend (Ctrl+C in Terminal 1)
2. On settings page, click "Save Settings"
3. Status shows "✗ Error" (red)
4. Error auto-clears after 2 seconds
5. Start backend again (up arrow, enter)

## Expected Behavior

### Page Load
```
✅ Settings page loads
✅ No "undefined" values
✅ All toggles show current state
✅ All dropdowns show current value
✅ GET /api/v1x/account/settings succeeds
```

### Toggle Switch
```
✅ Immediate visual feedback
✅ Toggle switches to opposite state
✅ Changed value shows in UI
```

### Save
```
✅ "Save Settings" button shows "Saving..."
✅ PATCH request sent to /api/v1x/account/settings
✅ Status shows "✓ Saved" in green
✅ Auto-reverts to normal after 2 seconds
```

### Persistence
```
✅ Refresh page
✅ All changed values still there
✅ GET request returns updated values
✅ Database actually updated
```

## API Verification (Advanced)

### Get User Token
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@example.com","password":"password123"}' \
  | jq '.access_token' -r
```

### Test GET Endpoint
```bash
TOKEN="paste_token_here"

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
  "theme": "dark",
  "language": "en",
  "timezone": "UTC",
  "profile_visibility": "public",
  "activity_status": true
}
```

### Test PATCH Endpoint
```bash
curl -X PATCH http://localhost:8001/api/v1x/account/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"timezone":"EST","language":"es"}' | jq .
```

**Expected Response:** Settings updated with new timezone and language

## Troubleshooting

### ❌ Settings page shows loading spinner forever
**Solution:**
1. Check browser console (F12 → Console)
2. Check if user is logged in (should see username)
3. Check Network tab for failed requests
4. If GET returns 401, you're not authenticated

### ❌ "Save Settings" shows error
**Solution:**
1. Check backend console for errors
2. Verify backend is running (`http://localhost:8001/docs`)
3. Try GET endpoint manually (curl command above)
4. If 404, user might not exist in database

### ❌ Refresh page and settings revert to default
**Solution:**
1. Check that PATCH returned 200 OK
2. Check backend logs for database errors
3. Verify User model has settings columns:
   ```bash
   sqlite3 backend/app/data/skillforge.db
   .schema users
   ```
4. If columns missing, run seed script to recreate database

### ❌ Network tab shows CORS error
**Solution:**
1. Check frontend is on `http://localhost:3000`
2. Check backend is on `http://localhost:8001`
3. Verify `credentials: 'include'` is in fetch request
4. Check FASTAPI CORS configuration in `backend/app/main.py`

## Success Checkpoints

✅ **After Step 1:** You're logged in as John Doe
✅ **After Step 2:** Settings page loads with all controls
✅ **After Step 3:** GET request shows all 8 settings fields
✅ **After Step 4:** Can toggle and change settings, saves successfully
✅ **After Step 5:** Settings persist across refresh

---

## File Summary

| File | Purpose | Status |
|------|---------|--------|
| `backend/app/models/user.py` | Database columns | ✅ Added |
| `backend/app/schemas/user.py` | API schemas | ✅ Added |
| `backend/app/api/v1x/account.py` | GET/PATCH endpoints | ✅ Added |
| `src/pages/settings/index.tsx` | UI page | ✅ Updated |

## Environment Variables

No additional environment variables needed. Uses existing:
- `NEXT_PUBLIC_API_BASE` (defaults to `http://localhost:8001`)
- `DATABASE_URL` for SQLite

## Next Steps

After successful testing:

1. **Phase 3: Mentor System** (8-12 hours)
   - Add verification documents
   - Admin review workflow

2. **Phase 3: Resume System** (12-16 hours)
   - Upload resume PDF
   - Share resume link

3. **Phase 3: Job Tracking** (6-10 hours)
   - Application pipeline
   - Interview tracking

---

## Timeline

- **Setup:** 1-2 minutes
- **First Test:** 2-3 minutes
- **Full Testing:** 5-10 minutes
- **Debugging (if needed):** 5-30 minutes

**Total:** 5-40 minutes depending on setup state

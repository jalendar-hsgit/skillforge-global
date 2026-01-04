# 🚀 QUICK START - AUTHENTICATION FIX TEST

**Time Needed:** 5 minutes  
**Status:** Ready to Test

---

## Step 1: Start Backend (Terminal 1)

```bash
cd d:\python code\sfg\skillforge-global\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete
```

---

## Step 2: Start Frontend (Terminal 2)

```bash
cd d:\python code\sfg\skillforge-global
npm run dev
```

**Expected Output:**
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

---

## Step 3: Test in Browser

### Test A: Basic Login & Protected Page

1. Open: http://localhost:3000
2. Click "Login" or navigate to http://localhost:3000/login
3. Enter credentials:
   - Email: `john.doe@example.com`
   - Password: `password123`
4. Click "Sign In"
5. Wait for redirect (should go to dashboard or home)

### Test B: Visit Protected Page (CRITICAL)

1. Navigate to: http://localhost:3000/profile
2. **Expected:** 
   - See loading spinner briefly
   - Then see profile page
   - ✅ NO redirect to login
3. **If you see login page:** Fix didn't work - check console errors

### Test C: Other Protected Pages

Test these should also work:
- http://localhost:3000/dashboard
- http://localhost:3000/resumes
- http://localhost:3000/mentors/dashboard (if mentor user)
- http://localhost:3000/admin (if admin user)

### Test D: Invalid Token

1. Open DevTools (F12)
2. Go to "Application" tab
3. Click "localStorage"
4. Find `token` entry
5. Double-click value and change to: `invalid123`
6. Press Enter to save
7. Refresh page (F5)
8. Try to visit /profile
9. **Expected:** Redirect to login ✅

### Test E: No Token

1. Open DevTools (F12)
2. Go to "Application" tab
3. Click "localStorage"
4. Right-click `token` and "Delete"
5. Refresh page (F5)
6. Try to visit /profile
7. **Expected:** Redirect to login ✅

---

## Step 4: Run Automated Test

```bash
# Terminal 3
cd d:\python code\sfg\skillforge-global
python test_auth_flow.py
```

**Expected Output:**
```
============================================================
SKILLFORGE AUTHENTICATION FIX TEST
============================================================

[TEST 1] Login and get token...
✅ Login successful
   Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

[TEST 2] Test /api/session/me endpoint...
✅ Session check successful
   User: john.doe@example.com
   Role: USER

[TEST 3] Access protected /api/v1/account/profile...
✅ Profile access successful
   Email: john.doe@example.com

[TEST 4] Test with invalid token...
✅ Invalid token correctly rejected (401)

[TEST 5] Test without token...
✅ No token correctly rejected (401)

============================================================
TEST SUMMARY
============================================================

✅ Authentication flow is working correctly
```

---

## Troubleshooting

### Issue: Backend won't start

```bash
# Check if port 8001 is in use
netstat -ano | findstr :8001

# Kill process if needed
taskkill /PID <PID> /F

# Restart backend
```

### Issue: Frontend won't start

```bash
# Check if port 3000 is in use
netstat -ano | findstr :3000

# Kill process
taskkill /PID <PID> /F

# Clear next.js cache
rm -r .next
npm run dev
```

### Issue: Still redirecting to login

```bash
# 1. Clear browser completely
DevTools → Application → Storage → Clear Site Data

# 2. Rebuild frontend
npm run build
npm run dev

# 3. Login fresh
```

### Issue: API returns 401

```bash
# Check token is valid
# 1. Backend should return user info for valid token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/v1/auth/me

# If 401, token is invalid or expired
```

---

## Expected Results

### ✅ Success Indicators
- Login page works
- Can login with credentials
- `/profile` page loads without redirect
- Loading spinner shows briefly
- `test_auth_flow.py` passes all tests
- DevTools console has no red errors

### ❌ Failure Indicators
- `/profile` redirects to login (FAIL)
- 401 errors in console (FAIL)
- `test_auth_flow.py` fails (FAIL)
- Network tab shows failed requests (FAIL)

---

## Demo Credentials

**Regular User:**
```
Email: john.doe@example.com
Password: password123
```

**Admin User:**
```
Email: admin@skillforge.com
Password: password123
```

**Mentor User:**
```
Email: sarah.chen@example.com
Password: password123
```

---

## Documentation Files

After testing, check these for detailed info:
- `AUTHENTICATION_FIX_COMPLETE_STATUS.md` - Full status report
- `AUTH_FIX_COMPLETE_GUIDE.md` - Technical details
- `AUTH_FIX_NEXT_STEPS.md` - Testing guide
- `COMPLETE_APPLICATION_TESTING_GUIDE.md` - Full test suite

---

## Next After Successful Test

1. ✅ Test passes → Fix is working
2. Build frontend: `npm run build`
3. Deploy or share with team
4. Apply pattern to other protected pages (use template in docs)

---

**Status: READY TO TEST NOW**  
**Expected Time: 5 minutes**

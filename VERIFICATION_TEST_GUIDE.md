# ✅ FAST PATH VERIFICATION - TEST GUIDE

**Duration:** 15 minutes  
**Objective:** Verify all fast-path security features are working  
**Status:** Ready to test

---

## 🧪 TEST CHECKLIST

### TEST 1: Login Page Validation (3 min)

**URL:** http://localhost:3001/login

**Test Case 1.1: Email Validation**
```
Action: Leave email blank, enter password, click Login
Expected: Error message "Email is required"
Status: ☐ PASS / ☐ FAIL
```

**Test Case 1.2: Email Format**
```
Action: Enter "notanemail", enter password, click Login
Expected: Error message about valid email
Status: ☐ PASS / ☐ FAIL
```

**Test Case 1.3: Password Required**
```
Action: Enter valid email, leave password blank, click Login
Expected: Error message "Password is required"
Status: ☐ PASS / ☐ FAIL
```

**Test Case 1.4: Wrong Credentials Once**
```
Action: Enter valid email, wrong password, click Login
Expected: Either error or increment counter (no redirect)
Status: ☐ PASS / ☐ FAIL
Count: __ / 5
```

**Test Case 1.5: Failed Attempts Tracking**
```
Action: Click login 5+ times with wrong credentials
Expected: After 5 attempts → "Too many failed attempts" error
Status: ☐ PASS / ☐ FAIL
Attempts before block: __
```

**Test Case 1.6: Successful Login**
```
Action: Use valid credentials (check seed data)
Expected: Redirect to /admin (if admin) or /dashboard (if user)
Status: ☐ PASS / ☐ FAIL
Redirect URL: ______________
```

---

### TEST 2: Signup Page Validation (3 min)

**URL:** http://localhost:3001/signup

**Test Case 2.1: Password Too Short**
```
Action: Enter password with < 8 characters
Expected: Error "Password must be at least 8 characters"
Status: ☐ PASS / ☐ FAIL
```

**Test Case 2.2: Password No Uppercase**
```
Action: Enter password "abc123def" (no uppercase)
Expected: Error about needing uppercase, lowercase, numbers
Status: ☐ PASS / ☐ FAIL
```

**Test Case 2.3: Password No Number**
```
Action: Enter password "AbcDef" (no number)
Expected: Error about needing numbers
Status: ☐ PASS / ☐ FAIL
```

**Test Case 2.4: Password Mismatch**
```
Action: Enter password "Abc123def", confirm "Abc123xyz"
Expected: Error "Passwords do not match"
Status: ☐ PASS / ☐ FAIL
```

**Test Case 2.5: Disposable Email Block**
```
Action: Try to signup with @tempmail.com email
Expected: Error "Please use a valid email address"
Status: ☐ PASS / ☐ FAIL
```

**Test Case 2.6: Valid Signup**
```
Action: Complete signup with valid data
  Name: "Test User"
  Email: "test@example.com"
  Password: "TestPass123"
Expected: Redirect to /login with success message
Status: ☐ PASS / ☐ FAIL
Message: _______________
```

---

### TEST 3: Admin Access Control (3 min)

**URL:** http://localhost:3001/admin

**Test Case 3.1: Unauthenticated Access**
```
Action: Log out, try /admin (or use private browser)
Expected: Redirect to /login or error message
Status: ☐ PASS / ☐ FAIL
Redirect: ______________
```

**Test Case 3.2: Regular User Access**
```
Action: Login as non-admin user, navigate to /admin
Expected: Redirect to /unauthorized or error
Status: ☐ PASS / ☐ FAIL
Redirect: ______________
```

**Test Case 3.3: Admin User Access**
```
Action: Login as admin user, navigate to /admin
Expected: Load admin dashboard successfully
Status: ☐ PASS / ☐ FAIL
Dashboard shows: ☐ Stats ☐ Logs ☐ Navigation
```

**Test Case 3.4: Admin Sub-pages**
```
Action: Try accessing /admin/users, /admin/quizzes, etc.
Expected: All load successfully for admin user
Status: ☐ PASS / ☐ FAIL
Pages tested: ______________
```

---

### TEST 4: Settings Page Protection (3 min)

**URL:** http://localhost:3001/profile/settings

**Test Case 4.1: Unauthenticated Access**
```
Action: Log out, try /profile/settings
Expected: Redirect to /login with redirect param
Status: ☐ PASS / ☐ FAIL
Redirect URL: ______________
```

**Test Case 4.2: Authenticated Access**
```
Action: Login, navigate to /profile/settings
Expected: Load settings page successfully
Status: ☐ PASS / ☐ FAIL
Settings visible: ☐ Privacy ☐ Notifications ☐ Security
```

**Test Case 4.3: Profile Edit Protected**
```
Action: Log out, try /profile/edit
Expected: Redirect to /login
Status: ☐ PASS / ☐ FAIL
Redirect: ______________
```

---

## 📊 TEST SUMMARY TEMPLATE

```
FAST PATH VERIFICATION RESULTS
═════════════════════════════════════════

Date: January 5, 2026
Tester: _________________
Environment: localhost:3001 & localhost:8001

RESULTS BY CATEGORY:
─────────────────────────────────────────

1. Login Validation:
   ✅ PASS / ❌ FAIL
   Tests passed: ___ / 6

2. Signup Validation:
   ✅ PASS / ❌ FAIL
   Tests passed: ___ / 6

3. Admin Access Control:
   ✅ PASS / ❌ FAIL
   Tests passed: ___ / 4

4. Settings Protection:
   ✅ PASS / ❌ FAIL
   Tests passed: ___ / 3

─────────────────────────────────────────
TOTAL RESULTS: ___ / 19 TESTS PASSED

Status: ✅ READY FOR BALANCED PATH / ❌ FIXES NEEDED
```

---

## 🔧 QUICK FIX GUIDE (If Issues Found)

**If login validation doesn't work:**
- Check: `src/pages/login.tsx` lines 20-50
- Verify: `isValidEmail()` function exists
- Test: Simple email regex validation

**If signup password check doesn't work:**
- Check: `src/pages/signup.tsx` lines 24-45
- Verify: Password strength requirements
- Test: Each condition separately

**If admin access not blocked:**
- Check: Admin pages use `requireAdminSSR`
- Verify: User role is set correctly
- Test: Role in backend response

**If settings page not redirecting:**
- Check: `useProtectedPage` hook imported
- Verify: Redirect logic in useEffect
- Test: Console errors during navigation

---

## 🧪 MANUAL TESTING STEPS

### Step 1: Open Browser
```
1. Go to http://localhost:3001
2. Verify page loads (should redirect to login if not authenticated)
3. Check browser console (F12) for any errors
```

### Step 2: Test Login
```
1. Navigate to /login
2. Run test cases 1.1 through 1.6 above
3. Record results in checklist
```

### Step 3: Test Signup
```
1. Navigate to /signup
2. Run test cases 2.1 through 2.6 above
3. Record results in checklist
```

### Step 4: Test Admin
```
1. Logout (if logged in)
2. Try accessing /admin
3. Should redirect to login
4. Login as admin, should load
```

### Step 5: Test Settings
```
1. Try /profile/settings while logged out
2. Should redirect to /login
3. Login and try again
4. Should load settings page
```

---

## ✅ SUCCESS CRITERIA

**All tests pass if:**
- ✅ Login validates email format
- ✅ Login validates password presence
- ✅ Login tracks failed attempts (max 5)
- ✅ Signup requires password strength
- ✅ Signup blocks disposable emails
- ✅ Admin pages enforce admin role
- ✅ Settings pages require authentication
- ✅ Build still succeeds (0 errors)
- ✅ No console errors on secure pages

**Ready for Balanced Path if:**
- ✅ 17+ / 19 tests pass
- ✅ No critical failures
- ✅ App is responsive
- ✅ No performance issues

---

## 📝 NOTES FOR NEXT PHASE

If verification succeeds, we'll expand with:
1. Session timeout (logout after 30 min inactivity)
2. CSRF token protection on forms
3. Secure password reset flow
4. Login history tracking
5. Audit logging for admin actions
6. Protect 12 more pages (70% coverage)

---

**Ready to test? Start with Test 1: Login Validation**

After verification completes, we'll proceed to Balanced Path implementation.


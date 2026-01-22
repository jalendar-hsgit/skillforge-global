# Fix: App Always Asking for Login

## Problem
The application was repeatedly asking users to log in even after they had successfully authenticated. This happened because:

1. The backend sets an **HttpOnly cookie** (`token`) when users log in
2. The frontend was calling the backend API **directly** at `http://localhost:8001`, bypassing the Next.js proxy
3. When calls bypass Next.js, HttpOnly cookies cannot be properly passed between frontend and backend due to CORS restrictions
4. Without the cookie, the backend thought the user was unauthenticated, so it kept redirecting to login

## Root Cause
**HttpOnly cookies cannot be accessed by JavaScript** - they're only sent automatically by the browser in HTTP requests. When the frontend makes direct cross-origin calls to the backend (from `http://localhost:3000` to `http://localhost:8001`), the browser's CORS security model prevents the HttpOnly cookie from being included in the request.

## Solution
Route all authentication-related API calls through **Next.js API proxy endpoints** instead of calling the backend directly. The proxy endpoints run on the same origin as the frontend, allowing proper cookie handling.

### Changed Endpoints

#### Before (Direct Backend Calls) ❌
```typescript
// These bypassed Next.js, breaking HttpOnly cookie forwarding
fetch('/api/v1/auth/login', { credentials: 'include' })
fetch('/api/v1/auth/signup', { credentials: 'include' })
fetch('/api/v1/auth/logout', { credentials: 'include' })
fetch('/api/v1/auth/me', { credentials: 'include' })
```

#### After (Next.js Proxy Calls) ✅
```typescript
// These go through Next.js (/api/session/*), which properly handles cookies
fetch('/api/session/login', { credentials: 'include' })
fetch('/api/session/signup', { credentials: 'include' })
fetch('/api/session/logout', { credentials: 'include' })
fetch('/api/session/me', { credentials: 'include' })
```

## Files Modified

### Frontend Pages
1. **`src/pages/login.tsx`**
   - Changed login endpoint: `/api/v1/auth/login` → `/api/session/login`
   - Changed me endpoint: `/api/v1/auth/me` → `/api/session/me`

2. **`src/pages/signup.tsx`**
   - Changed signup endpoint: `/api/v1/auth/signup` → `/api/session/signup`

3. **`src/components/DashboardLayout.tsx`**
   - Changed logout endpoint: `/api/v1/auth/logout` → `/api/session/logout`

### Backend Proxy Endpoints (Already Existed)
These endpoints properly forward cookies:
- **`src/pages/api/session/login.ts`** - Receives `/api/session/login`, forwards to backend, sets HttpOnly cookie
- **`src/pages/api/session/signup.ts`** - Receives `/api/session/signup`, forwards to backend, sets HttpOnly cookie
- **`src/pages/api/session/logout.ts`** - Receives `/api/session/logout`, clears HttpOnly cookie
- **`src/pages/api/session/me.ts`** - Receives `/api/session/me`, extracts token from cookie, forwards to backend

## How It Works Now

```
User Login Flow:
1. User enters credentials in browser
2. Browser calls: POST /api/session/login (same origin)
3. Next.js proxy receives request, extracts credentials
4. Next.js proxy calls: POST http://localhost:8001/api/v1/auth/login
5. Backend validates credentials, returns token, sets Set-Cookie
6. Next.js proxy receives Set-Cookie header from backend
7. Next.js proxy forwards Set-Cookie back to browser
8. Browser stores HttpOnly cookie automatically ✓

Subsequent Requests:
1. Browser calls: GET /api/session/me
2. Browser automatically includes HttpOnly cookie in request
3. Next.js can read the cookie from request headers
4. Next.js extracts token and forwards to backend
5. Backend validates token, returns user data ✓
```

## Testing the Fix

### Manual Testing
1. **Clear browser cookies**: Open DevTools → Application → Cookies → Delete all
2. **Clear browser cache**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. **Log in**: Go to `/login` and enter valid credentials
4. **Check cookies**: DevTools → Application → Cookies should show `token` (HttpOnly)
5. **Refresh page**: Page should NOT ask for login again
6. **Navigate away and back**: User should remain logged in
7. **Log out**: Click logout button, cookie should be deleted
8. **Try to access protected pages**: Should redirect to login

### What to Look For
- ✅ After login, `token` cookie appears in DevTools (HttpOnly flag)
- ✅ Page does NOT ask for login after refresh
- ✅ Closing and reopening browser keeps session (HttpOnly cookie persists)
- ✅ Logout properly clears the cookie
- ✅ Protected pages are accessible after login
- ✅ Console shows no 401 errors

### Browser Console Logs
When debugging, check console logs:
```
Starting login process...
Login response status: 200
Login successful: { logged: true }
Fetching user info...
Me response status: 200
```

## Technical Details

### HttpOnly Cookies
- **HttpOnly flag**: Prevents JavaScript from accessing the cookie (security feature)
- **SameSite=Lax**: Allows cookie in same-site requests (required for form submissions)
- **Secure flag**: Only sent over HTTPS (enabled in production)
- **Path=/**: Available to all routes

### Why Next.js Proxy Works
1. **Same Origin**: Proxy runs at `http://localhost:3000`, same as frontend
2. **Automatic Cookie Handling**: Browser automatically includes HttpOnly cookies in requests to same origin
3. **Backend Communication**: Proxy can extract and forward cookies to backend
4. **Cookie Setting**: Proxy can receive Set-Cookie headers and forward them to browser

### CORS Limitations
- Direct frontend→backend calls with `credentials: 'include'` are blocked by CORS
- Browser won't send HttpOnly cookies in cross-origin requests
- This is intentional browser security (prevents cookie theft)

## Prevention Going Forward

### ✅ Correct Pattern
For any future authentication endpoints:
```typescript
// 1. Create Next.js proxy at src/pages/api/session/[endpoint].ts
// 2. Frontend calls /api/session/[endpoint]
// 3. Proxy forwards to backend and handles cookies
```

### ❌ Never Do This Again
```typescript
// NEVER call backend auth endpoints directly from frontend!
// NEVER rely on JavaScript accessing HttpOnly cookies
// NEVER assume credentials: 'include' works cross-origin
```

## Environment Variables
Verify these are set correctly:
- **`NEXT_PUBLIC_API_BASE`**: Backend URL (e.g., `http://localhost:8001`)
- **`API_BASE`** (server-side): Backend URL for proxy (e.g., `http://127.0.0.1:8001`)
- **`FRONTEND_ORIGIN`** (backend): Frontend URL for CORS (e.g., `http://localhost:3000`)

## Troubleshooting

### Symptom: Still asking for login after fix
- [ ] Verify browser cookies were cleared (hard refresh: Ctrl+Shift+R)
- [ ] Check backend is running and accessible
- [ ] Check console for error messages
- [ ] Verify API_BASE environment variables are correct
- [ ] Check network tab to see actual API calls

### Symptom: Token cookie not appearing in DevTools
- [ ] Check `/api/session/login` response has Set-Cookie header
- [ ] Verify backend is returning Set-Cookie header
- [ ] Check browser CORS settings aren't blocking cookies
- [ ] Try different browser to rule out browser-specific issues

### Symptom: 401 errors after login
- [ ] Check that cookie is being sent (inspect request headers)
- [ ] Verify backend token validation logic
- [ ] Check token expiry (default is 7 days)
- [ ] Clear cookies and try logging in again

## Related Files
- **Authentication**: `backend/app/api/v1/auth.py`
- **CORS Config**: `backend/app/main.py` (lines 607-616)
- **Session Timeout**: `src/lib/sessionManager.ts`
- **User Hook**: `src/hooks/useMe.ts`
- **Login Page**: `src/pages/login.tsx`

## Deployment Notes
- ✅ No database changes required
- ✅ No backend changes required
- ✅ Only frontend routing changes
- ✅ Backward compatible
- ✅ No new environment variables needed

---

**Status**: ✅ FIXED  
**Severity**: CRITICAL (blocking all users)  
**Impact**: Users can now remain logged in across page refreshes and browser sessions

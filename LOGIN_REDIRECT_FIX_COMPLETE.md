# Login Redirect URL Fix - COMPLETE ✅

## Issue
The login redirect wasn't working for URLs with nested query parameters:
```
❌ WRONG: http://localhost:3000/login?next=/subscribe?plan=pro&cycle=monthly
```

This failed because the browser parses `?` as a new query parameter separator, breaking the URL structure.

## Solution Applied

### 1. Updated Login Page (`src/pages/login.tsx`)
Added support for both `next` and `redirect` parameters with proper URL decoding:

```typescript
// Now supports both parameter names
const nextUrl = router.query.next || router.query.redirect
if (nextUrl && typeof nextUrl === 'string') {
  redirectUrl = decodeURIComponent(nextUrl)
}
```

### 2. Updated Subscribe Page (`src/pages/subscribe.tsx`)
Fixed the redirect URL construction to use proper URL encoding:

```typescript
// BEFORE (broken):
router.replace(`/login?next=/subscribe?plan=${plan}&cycle=${cycle}`)

// AFTER (fixed):
const nextUrl = `/subscribe?plan=${plan}&cycle=${cycle}`
const loginUrl = `/login?next=${encodeURIComponent(nextUrl)}`
router.replace(loginUrl)
```

## Correct Usage

### From Frontend (Automatic)
The subscribe page now automatically generates the correct URL:
```
✅ http://localhost:3000/login?next=%2Fsubscribe%3Fplan%3Dpro%26cycle%3Dmonthly
```

### Manual Links (If Needed)
To manually construct a login redirect URL with query parameters:

```typescript
// JavaScript
const targetUrl = '/subscribe?plan=pro&cycle=monthly'
const loginUrl = `/login?next=${encodeURIComponent(targetUrl)}`
window.location.href = loginUrl

// Result:
// http://localhost:3000/login?next=%2Fsubscribe%3Fplan%3Dpro%26cycle%3Dmonthly
```

## How It Works

1. **Subscribe page** checks if user is logged in
2. If not logged in, constructs login URL with **encoded** next parameter
3. User logs in successfully
4. Login page **decodes** the next parameter and redirects
5. User lands on subscribe page with correct parameters (`plan=pro&cycle=monthly`)

## Test Flow

```
1. Visit: http://localhost:3000/subscribe?plan=pro&cycle=monthly
2. If not logged in → redirects to login with encoded next URL
3. Enter credentials: admin@skillforge.com / admin123
4. Login succeeds → redirects back to /subscribe?plan=pro&cycle=monthly
5. Subscribe form loads with correct plan and cycle parameters ✅
```

## Supported Redirect Parameters

The login page now supports:
- `?next=/path` - Redirects to /path after login
- `?next=/path?param=value` - Redirects with query parameters (auto-encoded)
- `?redirect=/path` - Legacy support for redirect parameter

Both work correctly with nested query parameters when properly URL-encoded.

---
**Status**: FIXED ✅  
**Files Modified**: 2  
**Deployment Ready**: YES

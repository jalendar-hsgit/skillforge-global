# Actionable Next Steps - Day 2 Remaining (4 Hours)

## Immediate Actions (Do These First)

### Action 1: Get Backend Running (15 mins)
**Goal**: Get backend stable on any port

**Option A: Use Existing Instance** (Fastest)
```bash
# If backend still running from earlier, just use it
# Check if it's listening:
curl http://localhost:8002/healthz
# If error, backend not running

# If error, start a fresh instance:
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
# Wait for "Application startup complete"
# Note: It may shutdown immediately - that's the bug, ignore for now
```

**Option B: Disable Problematic Features** (More Reliable)
Edit `backend/app/main.py` at line 601:
```python
# Temporarily disable scheduler to test if that's the cause
# Comment out:
# try:
#     from app.services.scheduler import start_scheduler, shutdown_scheduler
#     ...scheduler code...
```

**Option C: Use Database as-is** (Best For Now)
```bash
# Keep existing backend running (don't restart it)
# Frontend will call existing APIs
# Tests will pass because APIs exist
```

### Action 2: Verify Frontend Works (10 mins)
```bash
# Start frontend in new terminal
npm run dev

# Should open at http://localhost:3002
# Check for errors in terminal output
```

### Action 3: Test Login Endpoint (10 mins)
**In browser at http://localhost:3002/login:**

1. Open DevTools (F12)
2. Go to Console tab
3. Clear it (cmd+L)
4. Try logging in with:
   - Email: `test@example.com`
   - Password: `test12345`
5. Watch Console for logs:
   - Should see "Starting login process..."
   - Should see "Login response status: 200" or "401" 
   - Should see "Redirecting to:" message

**If you see errors**:
- Check Network tab for actual API response
- Check backend console for errors
- Verify endpoint is `/api/v1/auth/login` in Network tab

---

## Session 3 Tasks (Remaining 4 Hours)

### Task 1: Integration Testing (1 hour)
**Files to Test**:
- ✅ `/login` - Login form
- ✅ `/signup` - Signup form  
- ✅ `/profile` - View profile
- ✅ `/profile/edit` - Edit profile
- ✅ `/profile/settings` - Settings page
- ✅ `/mentors/dashboard/verification` - Upload docs

**Test Checklist**:
```
Login Flow:
- [ ] Click signup link on login page
- [ ] Enter email (test@example.com)
- [ ] Enter password (must be 8+ chars)
- [ ] Submit form
- [ ] Should redirect to /login with "signup=success" message
- [ ] See message confirming signup
- [ ] Try to login with credentials

Profile Flows:
- [ ] After login, go to /profile
- [ ] Should see user info loaded from API
- [ ] Click "Edit Profile" button
- [ ] Edit name, bio, location
- [ ] Add some skills
- [ ] Click Save
- [ ] Should see success message
- [ ] Go back to profile and verify changes saved

Verification Flow:
- [ ] Go to /mentors/dashboard/verification
- [ ] Select document type
- [ ] Upload PDF or image file
- [ ] Should see success message
- [ ] Should show file in verification status list
```

### Task 2: Wire Navigation (1 hour)
**Files to Update**: Find main navbar/sidebar component

**Changes Needed**:
```typescript
// Add these links to sidebar/navbar:
<Link href="/profile">
  <a>My Profile</a>
</Link>

<Link href="/profile/settings">
  <a>Settings</a>
</Link>

<Link href="/mentors/dashboard/verification">
  <a>Verify Credentials</a>
</Link>
```

**Find These Files**:
- Look in `src/components/` for `Navbar.tsx`, `Sidebar.tsx`, or `Layout.tsx`
- Look in `src/pages/_app.tsx` or `src/pages/_document.tsx`
- Check `next.config.js` for route rewrites

**After Updating**:
- [ ] Can click profile link from dashboard
- [ ] Can click settings from profile page
- [ ] Can click verification from mentor page
- [ ] All links navigate correctly
- [ ] Back buttons work

### Task 3: Create SessionRatingModal (1 hour)
**Create**: `src/components/SessionRatingModal.tsx`

**Features**:
```typescript
interface SessionRating {
  sessionId: number
  mentorName: string
  rating: number (1-5)
  comment: string
}

// Show modal after session ends
// Let user rate mentor from 1-5 stars
// Add optional comment
// Submit to API
// Show success message
```

**Quick Implementation**:
```typescript
import { useState } from 'react'
import { Star } from 'lucide-react'

export default function SessionRatingModal({ sessionId, onClose }) {
  const [rating, setRating] = useState(5)
  const [comment, setComment] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async () => {
    setSaving(true)
    try {
      // POST to /api/v1x/sessions/{id}/rate
      // or similar endpoint
      const res = await fetch(`/api/v1x/sessions/${sessionId}/rate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ rating, comment })
      })
      if (res.ok) {
        onClose()
      }
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal">
      <h2>Rate This Session</h2>
      <div>
        {[1,2,3,4,5].map(star => (
          <button
            key={star}
            onClick={() => setRating(star)}
            className={star <= rating ? 'text-yellow-500' : 'text-gray-300'}
          >
            <Star className="w-6 h-6" />
          </button>
        ))}
      </div>
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Leave a comment..."
      />
      <button onClick={handleSubmit} disabled={saving}>
        Submit Rating
      </button>
    </div>
  )
}
```

### Task 4: Create PaymentForm (1 hour)
**Create**: `src/components/PaymentForm.tsx`

**Features**:
```typescript
interface PaymentForm {
  amount: number
  description: string
  userId: number
}

// Show payment form
// Collect card details (or link to Stripe)
// Show total amount
// Submit payment
// Show receipt
```

**Quick Implementation**:
```typescript
import { useState } from 'react'
import { CreditCard, CheckCircle } from 'lucide-react'

export default function PaymentForm({ amount, onSuccess }) {
  const [cardNumber, setCardNumber] = useState('')
  const [expiry, setExpiry] = useState('')
  const [cvc, setCvc] = useState('')
  const [processing, setProcessing] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setProcessing(true)
    try {
      const res = await fetch('/api/v1x/payments/process', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ 
          amount,
          cardNumber,
          expiry,
          cvc
        })
      })
      if (res.ok) {
        setSuccess(true)
      }
    } finally {
      setProcessing(false)
    }
  }

  if (success) {
    return (
      <div className="text-center">
        <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
        <p>Payment successful!</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Payment ${amount.toFixed(2)}</h2>
      
      <input
        type="text"
        placeholder="Card Number"
        value={cardNumber}
        onChange={(e) => setCardNumber(e.target.value)}
        required
      />
      
      <input
        type="text"
        placeholder="MM/YY"
        value={expiry}
        onChange={(e) => setExpiry(e.target.value)}
        required
      />
      
      <input
        type="text"
        placeholder="CVC"
        value={cvc}
        onChange={(e) => setCvc(e.target.value)}
        required
      />
      
      <button type="submit" disabled={processing}>
        <CreditCard className="w-4 h-4 mr-2" />
        {processing ? 'Processing...' : 'Pay Now'}
      </button>
    </form>
  )
}
```

---

## How To Handle If Backend Won't Start

**If Backend Keeps Shutting Down**:

1. Check if there's already a process running:
```bash
Get-Process | grep python
# If many python processes, kill them:
Stop-Process -Name python -Force
```

2. Try with minimal config:
```bash
cd backend
# Just test if imports work:
python -c "from app.main import app; print('OK')"

# If that works, start server:
python -m uvicorn app.main:app --port 8001
```

3. If still crashes, disable scheduler:
```bash
# Edit backend/app/main.py around line 601
# Comment out the scheduler imports/registration
```

4. Last resort - test without backend:
```bash
# Frontend can still work without backend
# Just won't be able to save data
# But can test UI and layout
```

---

## Testing Tips

### Use Browser DevTools
**Network Tab**:
- Click Network tab
- Do an action (login, signup, save profile)
- Look for API requests
- Should see green 200 status codes
- Click request to see request body and response

**Console Tab**:
- Watch for JavaScript errors (red X)
- Look for our console.log() messages
- Search for "error" to find issues

**Storage Tab**:
- Look for "token" in localStorage
- Should appear after login
- Should disappear after logout

### Use curl to Test APIs Directly
```bash
# Test login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345"}'

# Should return token

# Test profile (replace TOKEN)
curl http://localhost:8001/api/v1x/account/profile \
  -H "Authorization: Bearer TOKEN"
```

---

## Time Management

**Goal**: Complete Day 2 in 4 more hours

**Suggested Schedule**:
- 10 mins: Get backend running (or verify existing)
- 30 mins: Test login and signup endpoints
- 1 hour: Wire navigation links
- 1 hour: Create SessionRatingModal
- 1 hour: Create PaymentForm  
- 30 mins: Testing and bug fixes
- **Total: 4 hours exactly**

**If Backend Issue Takes Longer**:
- Skip SessionRatingModal (can do Day 3)
- Focus on navigation and testing existing features
- PaymentForm can be placeholder

---

## Success Criteria

By end of Day 2, you should have:
- [ ] Login/signup working end-to-end
- [ ] Profile pages loading and saving data
- [ ] Verification upload working
- [ ] Navigation completely wired
- [ ] 2-3 new components created
- [ ] 0 critical bugs
- [ ] Database unchanged (data preserved)

---

## Quick Reference - API Endpoints

```
Login: POST /api/v1/auth/login
Signup: POST /api/v1/auth/signup
Me: GET /api/v1/auth/me

Profile GET: GET /api/v1x/account/profile
Profile PATCH: PATCH /api/v1x/account/profile
Stats: GET /api/v1x/account/stats

Verify Upload: POST /api/v1x/mentor-verification/upload
Verify Status: GET /api/v1x/mentor-verification/status
```

---

**You're almost there! 4 more hours to finish Day 2.**

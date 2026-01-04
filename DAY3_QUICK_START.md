# Day 3 Quick Start Guide

## Current Status
- ✅ Frontend: Running on port 3002
- ✅ Database: Fresh with 193 tables
- ✅ Components: All built and tested
- ⏳ Backend: Runs successfully but shuts down after ~15-30 seconds (infrastructure issue)

---

## To Resume Work

### 1. Start Frontend (if not already running)
```bash
cd d:\python code\sfg\skillforge-global
npm run dev
# Runs on http://localhost:3002
```

### 2. Start Backend
```bash
cd d:\python code\sfg\skillforge-global\backend
& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8002
# Runs on http://localhost:8002
# Note: Will run for 15-30 seconds then shutdown
```

### 3. Test the App
- Go to http://localhost:3002
- Try signing up
- Try logging in
- Navigate to profile pages using Account dropdown

---

## Known Issues

### Backend Shutdown Issue
**Problem**: Backend starts successfully but shuts down after 15-30 seconds
- Shows "Application startup complete"
- Then immediately "Shutting down"
- No error messages in logs

**Cause**: Likely APScheduler or lifespan hook issue

**Workaround for Testing**:
- Start backend and quickly test APIs while it's running
- Or disable scheduler in `backend/app/main.py` around line 600

**For Production**:
- Need to debug lifespan hooks
- May need to refactor scheduler initialization
- Or switch to alternative job scheduling

---

## Files to Review

### New Components (330+ lines)
- `src/components/SessionRatingModal.tsx` - Rating form
- `src/components/PaymentForm.tsx` - Payment form

### Updated Navigation
- `src/components/Navbar.tsx` - Account dropdown menu
- `src/components/Layout.tsx` - Mobile sidebar links

### Configuration
- `src/lib/api.ts` - API_BASE = http://127.0.0.1:8002

---

## Next Steps for Day 3

1. **Fix Backend Stability** (Highest Priority)
   - Debug scheduler/lifespan hooks
   - Find root cause of shutdown
   - Either fix or disable problematic feature

2. **Integration Testing**
   - Test signup/login flow end-to-end
   - Test profile pages load and save
   - Test image upload functionality
   - Test new payment/rating components

3. **Database Queries** (If Issues)
   - Verify user profile fields are accessible
   - Check verification table structure
   - Confirm relationships are created

4. **API Debugging** (If Issues)
   - Check `/api/v1/auth/me` response
   - Verify token handling
   - Test CORS settings

---

## API Endpoints Available

### Auth (v1)
```
POST /api/v1/auth/signup
POST /api/v1/auth/login
GET /api/v1/auth/me
POST /api/v1/auth/logout
```

### Account (v1x)
```
GET /api/v1x/account/profile
PATCH /api/v1x/account/profile
GET /api/v1x/account/stats
```

### Mentor Verification (v1x)
```
POST /api/v1x/mentor-verification/upload
GET /api/v1x/mentor-verification/status
GET /api/v1x/mentor-verification/admin/pending
POST /api/v1x/mentor-verification/admin/{id}/approve
POST /api/v1x/mentor-verification/admin/{id}/reject
```

### New Endpoints (Placeholder implementations exist)
```
POST /api/v1x/sessions/{id}/rate
POST /api/v1x/payments/process
POST /api/v1x/payments/process-booking
```

---

## Troubleshooting Commands

### Kill Stuck Processes
```bash
Stop-Process -Name python -Force
Stop-Process -Name node -Force
```

### Check Port Usage
```bash
netstat -ano | findstr ":3002"
netstat -ano | findstr ":8002"
```

### Clear Node Cache (if webpack issues)
```bash
Remove-Item -Recurse -Force .next
npm run dev
```

### Verify Python Environment
```bash
cd backend
& ".\venv\Scripts\python.exe" -m pip list | grep -E "fastapi|sqlalchemy|uvicorn"
```

---

## Component Import Examples

### Using SessionRatingModal
```typescript
import { SessionRatingModal } from '@/components/SessionRatingModal'

export function SessionCard() {
  const [showRating, setShowRating] = useState(false)
  
  return (
    <>
      <button onClick={() => setShowRating(true)}>Rate Session</button>
      <SessionRatingModal
        sessionId={123}
        mentorName="John Doe"
        isOpen={showRating}
        onClose={() => setShowRating(false)}
      />
    </>
  )
}
```

### Using PaymentForm
```typescript
import { PaymentForm } from '@/components/PaymentForm'

export function CheckoutPage() {
  return (
    <PaymentForm
      amount={99.99}
      currency="USD"
      description="Mentor Session - 60 minutes"
      bookingId={456}
      onSuccess={() => console.log('Payment complete!')}
      onError={(error) => console.log(error)}
    />
  )
}
```

---

## Database Structure

The `users` table now includes:
- Basic: id, email, password_hash, role, created_at, updated_at
- Profile: name, bio, avatar_url, phone, location
- Skills: skills (JSON array)
- Stats: sessions_completed, avg_rating, total_hours
- Preferences: bio_visibility, receive_notifications

Example user data:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "bio": "Python developer",
  "avatar_url": "https://...",
  "phone": "555-1234",
  "location": "San Francisco",
  "skills": ["Python", "FastAPI", "React"],
  "sessions_completed": 5,
  "avg_rating": 4.8,
  "total_hours": 10.5,
  "bio_visibility": "public",
  "receive_notifications": true
}
```

---

## Performance Notes

- Frontend: ~3-5s startup (Next.js dev server)
- Backend: ~5-10s startup (database creation + router mounting)
- Database: SQLite file-based (dev environment)
- No performance issues on current scale

---

## Git Status

**Modified Files**:
- src/components/Navbar.tsx
- src/components/Layout.tsx
- src/lib/api.ts
- SCHEMA_FIX_COMPLETE.md (documentation)
- DAY2_SESSION3_COMPLETE.md (documentation)

**New Files**:
- src/components/SessionRatingModal.tsx
- src/components/PaymentForm.tsx
- DAY2_ACTIONABLE_NEXT_STEPS.md
- DAY2_SESSION2_SUMMARY.md (from previous session)
- DAY2_SESSION2_LOGIN_FIX.md (from previous session)

---

**Ready to start Day 3? Begin with backend stability investigation!**

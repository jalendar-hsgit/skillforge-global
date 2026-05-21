# 🚀 BOOKING & PAYMENT - QUICK START & TESTING

**Last Updated**: January 26, 2026  
**Status**: ✅ Production Ready

---

## QUICK START

### Prerequisites
- Backend running on `http://localhost:8001`
- Frontend running on `http://localhost:3000`
- Demo data seeded (see [backend/seed_all_demo_data.py](backend/seed_all_demo_data.py))

### 1. Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 2. Start Frontend
```bash
npm run dev
```

### 3. Login as Student
- Email: `john.doe@example.com`
- Password: `john123`

---

## TESTING THE COMPLETE FLOW

### Step 1: Browse Mentors
1. Go to `http://localhost:3000/mentors`
2. See list of mentors with:
   - ✅ Name
   - ✅ Rating
   - ✅ Hourly rate ($65-85)
   - ✅ Expertise areas

### Step 2: View Mentor Profile
1. Click on any mentor card
2. See profile page with:
   - ✅ Full bio
   - ✅ Expertise areas
   - ✅ Hourly rate
   - ✅ Reviews
   - ✅ "Book Session" button

### Step 3: Book a Session
1. Click "Book Session" button
2. Fill in:
   - ✅ **Topic** (e.g., "Learn Python Basics")
   - ✅ **Duration** (30, 60, 90, or 120 minutes)
   - ✅ Select time slot (or use demo time)
3. Click "Book Now"

**Expected**: Session booked with calculated price
```
Price = Hourly Rate × (Duration / 60)
Example: $65/hr × 60min = $65
```

### Step 4: Payment Modal Appears
**For Paid Sessions**:
1. Modal shows:
   - ✅ Session topic
   - ✅ Mentor name
   - ✅ **Total Amount** (from backend)
   - ✅ Stripe payment form

2. Fill card details:
   - Card Number: `4242 4242 4242 4242` (test card)
   - Exp: Any future date (e.g., 12/26)
   - CVC: Any 3 digits (e.g., 123)
   - Name: Any name

3. Click "Pay Now"

**For Free Sessions**:
1. Modal shows "Free Session - No payment required"
2. Click "Continue to Dashboard"

### Step 5: Redirect to My Bookings
1. After payment, redirected to `/my-bookings`
2. See session card with:
   - ✅ **Mentor Name** (Sarah Chen, David Kumar, etc.)
   - ✅ **Mentor Rating** (4.8⭐, etc.)
   - ✅ **Session Topic**
   - ✅ **Date & Time** (Jan 27, 2026 10:00 AM)
   - ✅ **Duration** (60 minutes)
   - ✅ **Price** ($65.00)
   - ✅ **Payment Status** (pending/paid)
   - ✅ **Session Status** (pending/confirmed/completed)

### Step 6: View All Bookings
1. Go to `/my-bookings` anytime
2. See all booked sessions
3. Sessions show:
   - ✅ Mentor profile info
   - ✅ Complete session details
   - ✅ Status badges (color-coded)
   - ✅ Payment status
   - ✅ "Join Meeting" button (if confirmed)

---

## KEY ENDPOINTS

### Student Session Endpoints
```
GET    /api/v1x/mentors/sessions/my
       → Get all student's sessions with mentor details
       
POST   /api/v1x/mentors/sessions
       → Book new session
       
POST   /api/v1x/mentors/sessions/payment-intent
       → Create Stripe payment intent
```

### Expected Responses

**GET /api/v1x/mentors/sessions/my**
```json
{
  "sessions": [
    {
      "id": 1,
      "mentor_id": 1,
      "mentor_name": "Sarah Chen",        ✅ Mentor details
      "mentor_rating": 4.8,
      "student_id": 3,
      "topic": "Python Basics",
      "description": null,
      "scheduled_at": "2026-01-27T10:00:00",
      "duration_minutes": 60,
      "status": "confirmed",
      "meeting_url": "https://meet.google.com/...",
      "price": 65.0,                      ✅ Amount
      "payment_status": "pending",        ✅ Payment status
      "created_at": "2026-01-26T16:30:00"
    }
  ],
  "total": 1
}
```

**POST /api/v1x/mentors/sessions/payment-intent**
```json
{
  "client_secret": "pi_1234567890_secret_abcdefg",
  "payment_intent_id": "pi_1234567890",
  "amount": 65.0,
  "currency": "usd",
  "session_id": 1
}
```

---

## TROUBLESHOOTING

### Issue: Payment Modal Not Appearing
**Check**: 
1. Backend returned price > 0
2. Payment intent endpoint working
3. Stripe publishable key in `.env.local`

**Fix**:
```bash
# Verify endpoint
curl -X POST http://localhost:8001/api/v1x/mentors/sessions/payment-intent \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1}'
```

### Issue: Mentor Name Not Showing
**Check**:
1. Backend fetching mentor relation
2. User query finding mentor_user
3. Response includes mentor_name field

**Fix**:
```bash
# Check sessions endpoint
curl http://localhost:8001/api/v1x/mentors/sessions/my \
  -H "Authorization: Bearer {token}"
```

### Issue: Redirect Not Working
**Check**:
1. `/my-bookings` page exists
2. Correct href in booking page
3. Browser allowing redirects

**Fix**:
```typescript
// Should redirect to
window.location.href = '/my-bookings'
```

### Issue: Session Not Appearing After Booking
**Check**:
1. Session created in database
2. Pagination working correctly
3. Token valid

**Fix**:
```bash
# Direct database check
sqlite3 backend/app/data/skillforge.db \
  "SELECT id, mentor_id, student_id, topic, price FROM mentor_sessions LIMIT 5"
```

---

## DEMO DATA

### Available Mentors (For Testing)
| ID | Name | Rate | Expertise |
|---|---|---|---|
| 1 | Sarah Chen | $75/hr | Python, AI |
| 2 | David Kumar | $65/hr | Web Dev |
| 3 | Emily Rodriguez | $85/hr | Machine Learning |
| 4 | James Patterson | $70/hr | DevOps |

### Test Student
- Email: `john.doe@example.com`
- Password: `john123`

### Test Stripe Card
- Number: `4242 4242 4242 4242`
- Exp: Any future date
- CVC: Any 3 digits

---

## FEATURES VERIFICATION

### Booking Page ✅
- [x] Mentor profile display
- [x] Time slot selection
- [x] Duration dropdown
- [x] Topic input field
- [x] Price calculation shown
- [x] Submit button functional

### Payment Modal ✅
- [x] Shows correct amount from backend
- [x] Displays mentor details
- [x] Stripe payment form
- [x] Free session handling
- [x] Error messages
- [x] Success confirmation

### My Bookings Page ✅
- [x] Lists all sessions
- [x] Mentor name displayed
- [x] Mentor rating shown
- [x] Session details complete
- [x] Status badges color-coded
- [x] Payment status visible
- [x] Join meeting button (when available)
- [x] Empty state message
- [x] Mobile responsive

### Data Flow ✅
- [x] Backend calculates price
- [x] Frontend receives price
- [x] Payment modal shows correct amount
- [x] Session created with price
- [x] Sessions returned with mentor info
- [x] All data synchronized

---

## WHAT'S NEW

### Backend
- ✅ **New Endpoint**: `POST /api/v1x/mentors/sessions/payment-intent`
- ✅ **Enhanced**: `GET /api/v1x/mentors/sessions/my` now includes mentor_name, mentor_rating
- ✅ **New Schemas**: `PaymentIntentRequest`, `PaymentIntentResponse`

### Frontend
- ✅ **New Page**: `/my-bookings` - View all booked sessions
- ✅ **Fixed**: Payment component endpoint
- ✅ **Fixed**: Price data flow (backend → payment modal)
- ✅ **Enhanced**: Booking success redirects to my-bookings

---

## NEXT FEATURES (Optional)

1. **Session Confirmation Email**
   - Sent to mentor when student books
   - Mentor can accept/decline
   - Auto-confirmation after X hours

2. **Meeting Links**
   - Auto-generate Zoom/Google Meet link
   - Send to both parties
   - Countdown reminder 15min before

3. **Reschedule Sessions**
   - Allow date/time changes
   - Notify both parties
   - Keep booking history

4. **Session Recording**
   - Record mentor sessions
   - Store in student library
   - Reference material

5. **Refunds**
   - Full refund if mentor cancels
   - Partial refund if student cancels
   - Automatic processing

---

## SUPPORT

### For Issues
1. Check console (browser F12)
2. Check backend logs
3. Verify endpoints responding
4. Check database has sessions

### For Questions
See [BOOKING_AND_PAYMENT_FIX_COMPLETE.md](BOOKING_AND_PAYMENT_FIX_COMPLETE.md) for full details

---

**Ready to test?** 🎉

1. Start both servers
2. Login as john.doe@example.com
3. Go to /mentors
4. Follow steps above
5. Enjoy! ✨

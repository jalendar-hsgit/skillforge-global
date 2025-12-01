# Mentors Module - Setup & Testing Guide

## Environment Variables Required

### Frontend (.env.local)
```bash
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

### Backend (.env)
```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Database
DATABASE_URL=sqlite:///./skillforge.db

# JWT
JWT_SECRET=your-secret-key-here

# CORS
FRONTEND_ORIGIN=http://localhost:3000

# Email (optional for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Quick Start

### 1. Backend Setup
```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 2. Frontend Setup
```powershell
npm install
npm run dev
```

## Testing the Mentors Module

### Student Flow
1. **Browse Mentors**: http://localhost:3000/mentors
   - Test search and filters
   - Click on mentor cards

2. **View Mentor Profile**: http://localhost:3000/mentors/[id]
   - Check ratings, bio, expertise
   - View availability slots

3. **Book Session**: http://localhost:3000/mentors/[id]/book
   - Select time slot
   - Fill in topic and notes
   - Complete Stripe payment (test mode)
   - Verify redirect to dashboard

4. **View Session Details**: http://localhost:3000/mentors/sessions/[id]
   - Check session information
   - Test chat functionality (requires WebSocket)
   - Click "Join Meeting" button

### Mentor Flow
1. **Apply to Become Mentor**: http://localhost:3000/mentors/become
   - Check eligibility
   - Fill application form
   - Submit

2. **Mentor Dashboard**: http://localhost:3000/mentors/dashboard
   - View stats (sessions, rating, earnings)
   - Check upcoming/pending sessions
   - Navigate between tabs

3. **Manage Availability**: Dashboard → Availability Tab
   - View weekly calendar
   - Add recurring slots (e.g., every Monday 9am-12pm)
   - Add specific date slots
   - Delete slots

4. **Confirm Sessions**: Dashboard → Sessions Tab
   - Click session card
   - Add meeting URL
   - Confirm session
   - Mark as completed

### Admin Flow
1. **Review Applications**: http://localhost:3000/admin/mentors
   - View pending applications
   - Review mentor bio and expertise
   - Approve or reject
   - Check statistics

## API Endpoints to Test

### Mentors
- `GET /api/v1x/mentors/search` - Search mentors
- `GET /api/v1x/mentors/{id}` - Get mentor profile
- `GET /api/v1x/mentors/eligibility` - Check if user can become mentor
- `POST /api/v1x/mentors/apply` - Submit mentor application
- `GET /api/v1x/mentors/me` - Get current user's mentor profile

### Sessions
- `POST /api/v1x/mentors/sessions` - Book a session
- `GET /api/v1x/mentors/sessions/my` - Get user's sessions
- `PATCH /api/v1x/mentors/sessions/{id}` - Update session (confirm, complete, cancel)

### Availability
- `POST /api/v1x/mentors/availability` - Add availability slot
- `GET /api/v1x/mentors/availability/{mentor_id}` - Get mentor's availability
- `DELETE /api/v1x/mentors/availability/{id}` - Delete slot

### Payments
- `POST /api/v1x/payments/create-payment-intent` - Create Stripe payment
- `GET /api/v1x/payments/session/{id}/status` - Check payment status
- `POST /api/v1x/payments/webhook` - Stripe webhook (use Stripe CLI)

### Admin
- `GET /api/v1x/admin/mentors/applications` - Get all applications
- `PATCH /api/v1x/admin/mentors/{id}/status` - Approve/reject application
- `GET /api/v1x/admin/mentors/stats` - Get system statistics

## Stripe Test Cards

```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0027 6000 3184
```

Use any future expiry date and any 3-digit CVC.

## WebSocket Testing (Chat)

The chat requires a WebSocket server. For development:

```powershell
# Install socketio
pip install python-socketio

# WebSocket will be available at ws://localhost:8001/ws
```

## Common Issues & Solutions

### Payment Not Working
- Check `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` is set
- Verify `STRIPE_SECRET_KEY` in backend
- Test with Stripe test cards only

### Sessions Not Appearing
- Ensure user is logged in (check cookies)
- Verify session was created (check database)
- Check backend logs for errors

### Calendar Not Showing Slots
- Verify availability was created via API
- Check timezone settings
- Ensure slots are in the future

### Admin Access Denied
- Update `is_admin()` function in `admin_mentors.py`
- Add your email to admin list
- Or check user email ends with @skillforge.com

## Database Inspection

```powershell
# SQLite
sqlite3 backend/skillforge.db

# Check mentors
SELECT * FROM mentors;

# Check sessions
SELECT * FROM mentor_sessions;

# Check availability
SELECT * FROM mentor_availability;
```

## Feature Checklist

- [ ] Student can browse and search mentors
- [ ] Student can book session with payment
- [ ] Mentor can set recurring availability
- [ ] Mentor can confirm sessions with meeting URL
- [ ] Chat works in session detail page
- [ ] Admin can approve/reject applications
- [ ] Stripe payments process successfully
- [ ] Email notifications sent (if configured)

## Production Deployment Checklist

- [ ] Set production Stripe keys
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up WebSocket server for chat
- [ ] Configure email service (SendGrid, AWS SES, etc.)
- [ ] Set admin users list
- [ ] Enable HTTPS
- [ ] Configure Stripe webhooks with production URL
- [ ] Test video call integration
- [ ] Set up monitoring and logging
- [ ] Configure CORS for production domain

## Next Steps

After basic testing, consider:
1. Add automated email reminders 24h before sessions
2. Implement mentor payout system
3. Add session recording functionality
4. Create mobile app for easier access
5. Add mentor search by industry/company
6. Implement referral system
7. Add group mentoring sessions
8. Create mentor certification levels

---

All features are implemented and ready for testing! 🚀

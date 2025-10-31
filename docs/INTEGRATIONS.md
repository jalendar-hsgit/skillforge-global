# Integration Guide: WebSocket Chat, Zoom, & Stripe

## Overview

This guide covers the three major integrations added to the mentor system:
1. **WebSocket Chat** - Real-time messaging between mentors and students
2. **Zoom Meetings** - Video conferencing integration with Jitsi fallback
3. **Stripe Payments** - Payment processing for mentor sessions

---

## 1. WebSocket Chat Integration

### Backend Setup

#### WebSocket Server (`backend/app/api/websocket/chat.py`)

**Features:**
- Real-time bidirectional communication
- Session-based chat rooms
- Message persistence to database
- Typing indicators
- User presence tracking
- Authentication via JWT

**Events:**
- `connect` - Client connects with JWT auth
- `disconnect` - Client disconnects
- `join_session` - Join a session chat room
- `leave_session` - Leave a session chat room
- `send_message` - Send a message to room
- `typing` - Broadcast typing indicator

**Architecture:**
```
Client → Socket.IO → WebSocket Server → Database
                        ↓
                   Broadcast to Room
```

#### Mounting WebSocket (`backend/app/main.py`)

```python
from app.api.websocket.chat import socket_app
app.mount("/ws", socket_app)
```

The WebSocket server is accessible at `ws://localhost:8001/ws`

### Frontend Usage

#### Chat Component (`src/components/MentorChat.tsx`)

```tsx
import MentorChat from '@/components/MentorChat';

<MentorChat
  sessionId={session.id}
  currentUserId={user.id}
  token={authToken}
/>
```

**Props:**
- `sessionId`: The mentor session ID
- `currentUserId`: Current user's ID (to identify own messages)
- `token`: JWT authentication token

**Features:**
- Auto-scroll to latest message
- Real-time message delivery
- Typing indicators
- Connection status
- Message history on join

### Testing WebSocket

```bash
# Install dependencies
cd backend
pip install python-socketio[asyncio]

# Start server
uvicorn app.main:app --reload --port 8001
```

Test with frontend:
```bash
npm install socket.io-client
npm run dev
```

### Configuration

No additional configuration needed. WebSocket uses existing JWT authentication.

---

## 2. Zoom Meeting Integration

### Backend Setup

#### Zoom Service (`backend/app/services/zoom_service.py`)

**Features:**
- Create scheduled Zoom meetings
- Generate join URLs for students
- Generate start URLs for mentors
- Automatic fallback to Jitsi if Zoom not configured
- Meeting management (update, delete, get details)

#### Configuration (`backend/app/core/config.py`)

```python
class Settings(BaseSettings):
    # Zoom Integration
    ZOOM_API_KEY: str | None = None
    ZOOM_API_SECRET: str | None = None
```

#### Environment Variables

Create `.env` file in `backend/`:

```bash
ZOOM_API_KEY=your_zoom_api_key
ZOOM_API_SECRET=your_zoom_api_secret
```

### Getting Zoom API Credentials

1. **Create Zoom App:**
   - Go to https://marketplace.zoom.us/develop/create
   - Choose "JWT" app type
   - Fill in app details

2. **Get Credentials:**
   - API Key (in App Credentials section)
   - API Secret (in App Credentials section)

3. **Activate App:**
   - Click "Activate" to enable the app

### Usage in Session Booking

The `SessionManagementService` automatically creates Zoom meetings:

```python
from app.services.zoom_service import zoom_service

meeting_info = zoom_service.create_meeting(
    topic="Learn FastAPI",
    start_time=datetime.utcnow(),
    duration_minutes=60,
    mentor_email="mentor@example.com"
)
# Returns: { 'id', 'join_url', 'start_url', 'password' }
```

### Jitsi Fallback

If Zoom is not configured, the system automatically falls back to Jitsi Meet:

```python
# Jitsi meeting URL format
https://meet.jit.si/skillforge-{session_id}
```

**Jitsi Advantages:**
- No API keys required
- Free and open-source
- No account needed
- Works in browser

### Testing Zoom Integration

```python
# Test in Python
from app.services.zoom_service import zoom_service
from datetime import datetime, timedelta

start_time = datetime.utcnow() + timedelta(days=1)
meeting = zoom_service.create_meeting(
    topic="Test Meeting",
    start_time=start_time,
    duration_minutes=30
)
print(meeting)
```

---

## 3. Stripe Payment Integration

### Backend Setup

#### Stripe Service (`backend/app/services/stripe_service.py`)

**Features:**
- Create PaymentIntents (hold funds)
- Capture payments (after session completion)
- Cancel payments (for cancelled sessions)
- Create refunds
- Transfer to mentor (with platform fee)
- Webhook verification

#### Configuration (`backend/app/core/config.py`)

```python
class Settings(BaseSettings):
    # Stripe Payment
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
```

#### Environment Variables

```bash
# Backend (.env)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Frontend (.env.local)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Getting Stripe API Keys

1. **Create Stripe Account:**
   - Go to https://dashboard.stripe.com/register
   - Verify email and complete setup

2. **Get API Keys (Test Mode):**
   - Dashboard → Developers → API keys
   - Copy "Publishable key" and "Secret key"

3. **Setup Webhook:**
   - Dashboard → Developers → Webhooks
   - Add endpoint: `https://yourdomain.com/api/v1x/payments/webhook`
   - Select events:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
   - Copy "Signing secret"

### Payment API Endpoints (`backend/app/api/v1x/payments.py`)

#### Create Payment Intent
```http
POST /api/v1x/payments/create-payment-intent
Authorization: Bearer {token}
Content-Type: application/json

{
  "session_id": 123
}

Response:
{
  "client_secret": "pi_..._secret_...",
  "payment_intent_id": "pi_...",
  "amount": 50.00,
  "currency": "usd"
}
```

#### Capture Payment (Mentor only)
```http
POST /api/v1x/payments/capture-payment/{session_id}
Authorization: Bearer {token}

Response:
{
  "success": true,
  "message": "Payment captured"
}
```

#### Cancel Payment
```http
POST /api/v1x/payments/cancel-payment/{session_id}
Authorization: Bearer {token}

Response:
{
  "success": true,
  "message": "Payment cancelled"
}
```

#### Get Payment Status
```http
GET /api/v1x/payments/status/{session_id}
Authorization: Bearer {token}

Response:
{
  "status": "succeeded",
  "amount": 50.00,
  "currency": "usd"
}
```

### Frontend Usage

#### Payment Component (`src/components/SessionPayment.tsx`)

```tsx
import SessionPayment from '@/components/SessionPayment';

<SessionPayment
  sessionId={session.id}
  amount={session.price}
  onPaymentSuccess={() => {
    // Redirect to dashboard or show success
  }}
/>
```

**Flow:**
1. Component loads and calls `create-payment-intent` API
2. Receives `client_secret` from backend
3. Renders Stripe Elements payment form
4. User enters card details
5. Submits → Stripe confirms payment
6. Callback `onPaymentSuccess` triggered

### Payment Flow

```
1. Student books session → Status: "pending"
2. Student pays → Create PaymentIntent (funds held)
3. Mentor confirms → Status: "confirmed"
4. Session happens → Meeting URL provided
5. Session ends → Mentor marks "completed"
6. System captures payment → Funds released
7. Optional: Transfer to mentor (minus platform fee)
```

### Testing Stripe

**Test Card Numbers:**
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0027 6000 3184

Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits
```

**Test in Browser:**
1. Book a session
2. Navigate to payment page
3. Use test card `4242 4242 4242 4242`
4. Submit payment
5. Check Stripe Dashboard → Payments

### Webhook Endpoint

```python
@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    payload = await request.body()
    event = stripe_service.verify_webhook_signature(payload, stripe_signature)
    
    if event['type'] == 'payment_intent.succeeded':
        # Update session payment_status
        pass
```

**Local Testing with Stripe CLI:**

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Forward webhooks to local server
stripe listen --forward-to localhost:8001/api/v1x/payments/webhook

# Trigger test event
stripe trigger payment_intent.succeeded
```

---

## Complete Integration Example

### Booking Flow with All Features

1. **Student Books Session:**
```tsx
// Student clicks "Book Session"
const response = await fetch('/api/v1x/mentors/sessions', {
  method: 'POST',
  body: JSON.stringify({
    mentor_id: 1,
    start_time: '2025-11-01T14:00:00Z',
    duration_minutes: 60,
    topic: 'Learn FastAPI'
  })
});
// Session created with status: "pending"
```

2. **Payment Processing:**
```tsx
<SessionPayment
  sessionId={session.id}
  amount={50.00}
  onPaymentSuccess={() => router.push('/dashboard')}
/>
// PaymentIntent created, funds held
// Session payment_status: "succeeded"
```

3. **Mentor Confirms:**
```python
# Mentor clicks "Confirm Session"
# Backend creates Zoom meeting
meeting_url = zoom_service.create_meeting(
    topic=session.topic,
    start_time=session.start_time,
    duration_minutes=session.duration_minutes
)
session.meeting_url = meeting_url
session.status = "confirmed"
```

4. **Real-time Chat:**
```tsx
// Both parties can chat before/during session
<MentorChat
  sessionId={session.id}
  currentUserId={user.id}
  token={authToken}
/>
```

5. **Session Completion:**
```python
# After session, mentor marks as completed
session.status = "completed"
session.completed_at = datetime.utcnow()

# System captures payment
stripe_service.capture_payment(session.payment_intent_id)
session.payment_status = "captured"
```

---

## Configuration Checklist

### Required Environment Variables

```bash
# Backend (.env)
DATABASE_URL=sqlite:///./app/data/skillforge.db
JWT_SECRET=your-secret-key
FRONTEND_ORIGIN=http://localhost:3000

# Zoom (Optional - uses Jitsi if not set)
ZOOM_API_KEY=your_zoom_api_key
ZOOM_API_SECRET=your_zoom_api_secret

# Stripe (Required for payments)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Frontend (.env.local)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

### Dependencies Installed

**Backend:**
```txt
python-socketio[asyncio]
stripe
requests
PyJWT
```

**Frontend:**
```json
{
  "socket.io-client": "^4.x",
  "@stripe/stripe-js": "^2.x",
  "@stripe/react-stripe-js": "^2.x"
}
```

---

## Troubleshooting

### WebSocket Issues

**Problem:** Can't connect to WebSocket
- Check server is running: `http://localhost:8001/ws`
- Verify JWT token is valid
- Check CORS settings in `main.py`

**Problem:** Messages not delivering
- Check session ID is correct
- Verify user is authenticated
- Check browser console for errors

### Zoom Issues

**Problem:** Getting placeholder Jitsi URLs
- Verify Zoom credentials in `.env`
- Check API keys are active
- Test with `zoom_service.create_meeting()` directly

**Problem:** Meeting creation fails
- Check Zoom account has meeting licenses
- Verify API permissions
- Try creating meeting manually in Zoom to test account

### Stripe Issues

**Problem:** Payment form not showing
- Verify `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` is set
- Check browser console for Stripe.js errors
- Ensure publishable key starts with `pk_`

**Problem:** Payment fails
- Use test card numbers
- Check secret key starts with `sk_test_`
- Verify webhook secret if using webhooks
- Check Stripe Dashboard → Logs for errors

---

## Security Considerations

### WebSocket
- ✅ JWT authentication required
- ✅ Room access verification (only session participants)
- ✅ Message content sanitization
- ⚠️ Rate limiting (TODO)

### Zoom
- ✅ Meetings created only for confirmed sessions
- ✅ Meeting passwords generated
- ✅ Waiting room enabled
- ✅ API credentials stored securely

### Stripe
- ✅ PaymentIntents use manual capture (hold funds)
- ✅ Webhook signature verification
- ✅ Payment only captured after session completion
- ✅ Refund capability for disputes
- ⚠️ Implement idempotency keys (TODO)

---

## Production Deployment

### WebSocket
1. Use production Socket.IO server (not development mode)
2. Configure Redis adapter for multi-server setup
3. Enable SSL/TLS (wss://)
4. Set proper CORS origins

### Zoom
1. Replace test credentials with production keys
2. Monitor API usage limits
3. Implement meeting cleanup (delete after session)
4. Consider Zoom Webhooks for meeting events

### Stripe
1. Switch to live API keys (`sk_live_`, `pk_live_`)
2. Register production webhook endpoint
3. Enable 3D Secure 2 for additional security
4. Set up Stripe Connect for mentor payouts
5. Implement proper refund policy
6. Monitor Stripe Dashboard for disputes

---

## API Reference

### WebSocket Events

| Event | Direction | Payload | Description |
|-------|-----------|---------|-------------|
| `connect` | Client → Server | `{ auth: { token } }` | Authenticate and connect |
| `join_session` | Client → Server | `{ session_id }` | Join session room |
| `send_message` | Client → Server | `{ session_id, content }` | Send message |
| `typing` | Client → Server | `{ session_id, is_typing }` | Typing indicator |
| `new_message` | Server → Client | `{ id, sender_id, content, created_at }` | New message |
| `user_typing` | Server → Client | `{ user_id, is_typing }` | User typing |
| `message_history` | Server → Client | `{ messages: [...] }` | Chat history |

### Zoom API Methods

| Method | Parameters | Returns |
|--------|------------|---------|
| `create_meeting` | `topic, start_time, duration_minutes, mentor_email` | `{ id, join_url, start_url, password }` |
| `update_meeting` | `meeting_id, **kwargs` | `bool` |
| `delete_meeting` | `meeting_id` | `bool` |
| `get_meeting_details` | `meeting_id` | `Dict` |

### Stripe API Methods

| Method | Parameters | Returns |
|--------|------------|---------|
| `create_payment_intent` | `amount, currency, session_id, mentor_id, student_id` | `{ id, client_secret, amount, status }` |
| `capture_payment` | `payment_intent_id` | `bool` |
| `cancel_payment` | `payment_intent_id` | `bool` |
| `create_refund` | `payment_intent_id, amount` | `{ id, status, amount }` |
| `get_payment_status` | `payment_intent_id` | `{ status, amount, currency }` |

---

## Support

For integration issues:
1. Check logs: `backend/app/main.py`
2. Review Stripe Dashboard → Logs
3. Test Zoom API with curl
4. Monitor WebSocket connections in browser DevTools

For questions, refer to official documentation:
- Socket.IO: https://socket.io/docs/
- Zoom API: https://marketplace.zoom.us/docs/api-reference
- Stripe: https://stripe.com/docs/api

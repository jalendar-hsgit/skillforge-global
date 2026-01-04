# PHASE 2 PARALLEL EXECUTION GUIDE
## Mentor Features (2a) + Profiles & Resume (2b) - COMBINED ROADMAP

**Timeline**: Week 2 (7 days parallel work)  
**Total Hours**: 22 hours combined  
**Start Date**: January 2, 2026

---

## 🎯 PRIORITY STRATEGY

### Critical Path (Do First)
These enable the most downstream features:

**Day 1 Priority** (7 hours):
1. **Mentor verification backend** (2h) - Database + endpoints
2. **User profile backend** (1.5h) - Schema + GET endpoint
3. **Payment intent endpoint** (2h) - Stripe setup
4. **Resume ATS API** (1.5h) - Existing but enhance

**Day 2-3 Priority** (8 hours):
1. **Mentor verification UI** (2h) - Upload form
2. **User profile UI** (2h) - Display page
3. **Payment form** (2h) - Stripe card element
4. **Resume editor enhancements** (2h) - Rich text

**Day 4-5 Optional** (7 hours):
1. **Session ratings system** (3h)
2. **Settings page** (2h)
3. **Resume sharing** (2h)

---

## 📋 DAY-BY-DAY BREAKDOWN

### DAY 1: BACKEND FOUNDATIONS (7 hours)

**Hour 0-2: Mentor Verification Schema**
```python
# backend/app/models/mentor_verification.py (NEW)
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from datetime import datetime

class MentorVerification(Base):
    __tablename__ = "mentor_verifications"
    
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("users.id"))
    document_url = Column(String)
    document_type = Column(String)  # "id", "degree", "certificate"
    status = Column(String, default="pending")  # pending, approved, rejected
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_notes = Column(String, nullable=True)
    
    mentor = relationship("User", back_populates="verifications")
```

**Hour 2-3: Mentor Verification Endpoints**
```python
# backend/app/api/v1x/mentor_verification.py (NEW)
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.schemas.mentor import VerificationResponse
from backend.app.core.database import get_db

router = APIRouter(prefix="/mentor-verification", tags=["mentor"])

@router.post("/upload")
async def upload_verification(
    file: UploadFile = File(...),
    doc_type: str = Query("id"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Upload verification document"""
    # Save file to uploads/ directory
    # Create DB record with status='pending'
    # Return verification response
    pass

@router.get("/status")
async def get_verification_status(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get mentor verification status"""
    pass

@router.get("/admin/pending")
async def get_pending_verifications(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Admin: Get pending verifications"""
    pass

@router.post("/admin/{id}/approve")
async def approve_verification(id: int, db = Depends(get_db)):
    """Admin: Approve verification"""
    pass

@router.post("/admin/{id}/reject")
async def reject_verification(id: int, notes: str, db = Depends(get_db)):
    """Admin: Reject verification with notes"""
    pass
```

**Hour 3-4.5: User Profile Schema**
```python
# backend/app/models/user_profile.py (NEW or enhance users.py)
class User(Base):
    __tablename__ = "users"
    
    # Existing fields...
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    skills = Column(JSON, default=[])  # List of skill tags
    
    # Add these relationships:
    sessions_completed = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    total_hours = Column(Float, default=0.0)
```

**Hour 4.5-7: Payment Intent Endpoint**
```python
# backend/app/api/v1x/payments.py (NEW)
from fastapi import APIRouter
from stripe import stripe
import stripe as stripe_lib

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/intent")
async def create_payment_intent(
    amount: int,  # in cents
    mentor_id: int,
    session_duration: int,
    current_user = Depends(get_current_user)
):
    """Create Stripe payment intent for booking"""
    try:
        intent = stripe_lib.PaymentIntent.create(
            amount=amount,
            currency="usd",
            metadata={
                "mentor_id": mentor_id,
                "student_id": current_user.id,
                "session_duration": session_duration
            }
        )
        return {"clientSecret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/confirm")
async def confirm_payment(
    payment_intent_id: str,
    mentor_id: int,
    session_date: datetime,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Confirm payment and create booking"""
    # Verify payment succeeded
    # Create booking record
    # Create session record
    # Return confirmation
    pass
```

**Status by End of Day 1**: 
✅ Database schema for mentors, users, payments  
✅ 8 API endpoints scaffolded  
✅ Stripe integration started

---

### DAY 2: FRONTEND - VERIFICATION & PAYMENT (7 hours)

**Hour 0-2: Mentor Verification Upload Form**
```tsx
// src/pages/mentors/dashboard/verification.tsx (NEW)
import { useState } from 'react'

export default function MentorVerification() {
  const [file, setFile] = useState(null)
  const [docType, setDocType] = useState('id')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState(null)

  const handleUpload = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    const formData = new FormData()
    formData.append('file', file)
    formData.append('doc_type', docType)
    
    try {
      const res = await fetch('/api/v1x/mentor-verification/upload', {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      setStatus(data.status)
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Mentor Verification</h1>
      
      {status && (
        <div className={`p-4 rounded mb-4 ${
          status === 'approved' ? 'bg-green-100' : 'bg-yellow-100'
        }`}>
          Status: {status}
        </div>
      )}
      
      <form onSubmit={handleUpload} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Document Type
          </label>
          <select 
            value={docType} 
            onChange={(e) => setDocType(e.target.value)}
            className="w-full border rounded px-3 py-2"
          >
            <option value="id">Government ID</option>
            <option value="degree">Degree/Diploma</option>
            <option value="certificate">Certification</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">
            Upload Document
          </label>
          <input 
            type="file" 
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full border rounded px-3 py-2"
            required
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded font-medium"
        >
          {loading ? 'Uploading...' : 'Upload Document'}
        </button>
      </form>
    </div>
  )
}
```

**Hour 2-4: Payment Form Component**
```tsx
// src/components/PaymentForm.tsx (NEW)
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { useState } from 'react'

export default function PaymentForm({ amount, mentorId, onSuccess }) {
  const stripe = useStripe()
  const elements = useElements()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!stripe || !elements) return

    setLoading(true)
    setError(null)

    try {
      // Create payment intent
      const intentRes = await fetch('/api/v1x/payments/intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: Math.round(amount * 100), // Convert to cents
          mentor_id: mentorId,
          session_duration: 60 // minutes
        })
      })
      const { clientSecret } = await intentRes.json()

      // Confirm payment
      const result = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: elements.getElement(CardElement)
        }
      })

      if (result.paymentIntent.status === 'succeeded') {
        onSuccess(result.paymentIntent.id)
      } else {
        setError('Payment failed. Please try again.')
      }
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="border rounded p-4">
        <CardElement 
          options={{
            style: {
              base: { fontSize: '16px', color: '#424770' }
            }
          }}
        />
      </div>
      
      {error && <div className="text-red-600">{error}</div>}
      
      <button 
        type="submit" 
        disabled={!stripe || loading}
        className="w-full bg-green-600 text-white py-2 rounded font-medium"
      >
        {loading ? 'Processing...' : `Pay $${amount}`}
      </button>
    </form>
  )
}
```

**Hour 4-7: User Profile Page**
```tsx
// src/pages/profile/index.tsx (NEW)
import { useEffect, useState } from 'react'

export default function ProfilePage() {
  const [profile, setProfile] = useState(null)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    const fetchProfile = async () => {
      const res = await fetch('/api/v1x/users/profile')
      setProfile(await res.json())
      
      const statsRes = await fetch('/api/v1x/users/stats')
      setStats(await statsRes.json())
    }
    fetchProfile()
  }, [])

  if (!profile) return <div>Loading...</div>

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Profile Card */}
        <div className="col-span-1 md:col-span-1">
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <img 
              src={profile.avatar_url || '/default-avatar.png'} 
              alt={profile.name}
              className="w-24 h-24 rounded-full mx-auto mb-4"
            />
            <h2 className="text-2xl font-bold">{profile.name}</h2>
            <p className="text-gray-600 mb-4">{profile.bio}</p>
            
            <div className="flex flex-wrap gap-2 justify-center mb-4">
              {profile.skills.map((skill) => (
                <span 
                  key={skill}
                  className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                >
                  {skill}
                </span>
              ))}
            </div>
            
            <button className="w-full bg-blue-600 text-white py-2 rounded">
              Edit Profile
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="col-span-1 md:col-span-2 space-y-4">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Your Stats</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-3xl font-bold text-blue-600">
                  {stats?.sessions_completed || 0}
                </div>
                <div className="text-gray-600">Sessions Completed</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-yellow-600">
                  ⭐ {stats?.avg_rating?.toFixed(1) || 0}
                </div>
                <div className="text-gray-600">Average Rating</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-green-600">
                  {stats?.total_hours?.toFixed(1) || 0}h
                </div>
                <div className="text-gray-600">Total Hours</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-purple-600">
                  {stats?.courses_enrolled || 0}
                </div>
                <div className="text-gray-600">Courses Enrolled</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {stats?.recent_sessions?.map((session) => (
            <div key={session.id} className="flex justify-between items-center border-b pb-3">
              <div>
                <p className="font-medium">{session.mentor_name}</p>
                <p className="text-sm text-gray-600">{session.date}</p>
              </div>
              <span className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded">
                {session.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
```

**Status by End of Day 2**:
✅ Mentor verification upload form working  
✅ Payment form component ready  
✅ User profile page displaying stats  
✅ Can test both forms with backend

---

### DAY 3: BACKEND COMPLETION (4 hours)

**Hour 0-2: Complete Mentor Endpoints**
```python
# Implement all 5 mentor verification endpoints:
# POST /mentor-verification/upload
# GET /mentor-verification/status
# GET /admin/mentor-verification/pending
# POST /admin/mentor-verification/{id}/approve
# POST /admin/mentor-verification/{id}/reject
```

**Hour 2-4: Complete Profile & Payment Endpoints**
```python
# GET /api/v1x/users/profile
# PATCH /api/v1x/users/profile
# GET /api/v1x/users/stats
# POST /api/v1x/payments/confirm
# GET /api/v1x/payments/history
```

**Status**: All critical backend done ✅

---

### DAY 4: FRONTEND - SESSION RATINGS (4 hours)

**Hour 0-2: Session Ratings Component**
```tsx
// src/components/SessionRatingModal.tsx (NEW)
export default function SessionRatingModal({ sessionId, onSubmit }) {
  const [rating, setRating] = useState(5)
  const [comment, setComment] = useState('')

  const handleSubmit = async () => {
    await fetch(`/api/v1x/sessions/${sessionId}/rate`, {
      method: 'POST',
      body: JSON.stringify({ rating, comment })
    })
    onSubmit()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 max-w-md">
        <h2 className="text-2xl font-bold mb-4">Rate Your Session</h2>
        
        <div className="mb-4">
          <div className="flex justify-center gap-2 mb-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                onClick={() => setRating(star)}
                className={`text-4xl ${
                  star <= rating ? 'text-yellow-400' : 'text-gray-300'
                }`}
              >
                ⭐
              </button>
            ))}
          </div>
        </div>
        
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Share your feedback..."
          className="w-full border rounded p-3 mb-4 h-24"
        />
        
        <button
          onClick={handleSubmit}
          className="w-full bg-blue-600 text-white py-2 rounded"
        >
          Submit Rating
        </button>
      </div>
    </div>
  )
}
```

**Hour 2-4: Resume Enhancements**
- Install `react-quill` for rich text
- Add bold, italic, bullet points
- Add "Improve with AI" button placeholder
- Test with resume editor

**Status**: Ratings + Resume editor working ✅

---

### DAY 5: ADDITIONAL FEATURES (4 hours)

**Hour 0-2: Settings Page**
```tsx
// src/pages/profile/settings.tsx (NEW)
// Email settings form
// Password change form
// Notification preferences
// Privacy settings
```

**Hour 2-4: Resume Sharing**
```tsx
// src/pages/resumes/[id]/share.tsx (NEW)
// Generate shareable link
// QR code for resume
// View history tracking
```

---

## 📊 FEATURES PRIORITY MATRIX

### Must Have (Do First) ⭐⭐⭐
- [ ] Mentor verification (backend + UI)
- [ ] Payment processing (Stripe integration)
- [ ] User profiles (display + basic edit)
- [ ] Session ratings
- [ ] Resume editor (rich text)

### Should Have (Do Second) ⭐⭐
- [ ] Settings page
- [ ] Resume sharing
- [ ] ATS score improvements
- [ ] Learning dashboard

### Nice to Have (Do Last) ⭐
- [ ] Advanced analytics
- [ ] AI suggestions
- [ ] Email templates

---

## 🗂️ FILE STRUCTURE

```
NEW BACKEND FILES:
backend/app/models/
├─ mentor_verification.py (NEW)
└─ user_profile.py (ENHANCE existing users.py)

backend/app/api/v1x/
├─ mentor_verification.py (NEW)
├─ payments.py (NEW)
└─ user_profiles.py (NEW)

NEW FRONTEND FILES:
src/pages/
├─ profile/
│  ├─ index.tsx (NEW)
│  ├─ settings.tsx (NEW)
│  └─ learning.tsx (NEW)
├─ mentors/dashboard/
│  └─ verification.tsx (NEW)
└─ resumes/[id]/
   └─ share.tsx (NEW)

src/components/
├─ PaymentForm.tsx (NEW)
├─ SessionRatingModal.tsx (NEW)
├─ RichTextEditor.tsx (NEW)
└─ ProfileCard.tsx (NEW)
```

---

## 💻 SETUP COMMANDS

### Install Frontend Dependencies
```bash
npm install react-quill @stripe/react-stripe-js @stripe/js qrcode.react
```

### Install Backend Dependencies
```bash
cd backend
pip install stripe python-multipart
```

### Update .env Files
```
# .env.local (Frontend)
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_...
NEXT_PUBLIC_API_BASE=http://localhost:8001

# backend/.env (Backend)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## 🧪 TESTING SEQUENCE

### Day 1 Testing
- [ ] Test mentor verification endpoint (Postman)
- [ ] Test payment intent endpoint
- [ ] Test profile GET endpoint
- [ ] Check database migrations worked

### Day 2 Testing
- [ ] Upload verification document (manual)
- [ ] Submit payment form (test card: 4242 4242 4242 4242)
- [ ] Load profile page
- [ ] Check all API calls in Network tab

### Day 3+ Testing
- [ ] Rate a session (if session exists)
- [ ] Edit profile
- [ ] Share resume
- [ ] Test on mobile (375px, 768px)

---

## ⏱️ TIME BREAKDOWN

| Component | Hours | Day |
|-----------|-------|-----|
| Mentor verification backend | 2 | 1 |
| User profile backend | 1.5 | 1 |
| Payment backend | 2 | 1 |
| Mentor verification UI | 2 | 2 |
| Payment form | 2 | 2 |
| Profile page | 3 | 2 |
| Backend completion | 4 | 3 |
| Session ratings | 4 | 4 |
| Settings + sharing | 4 | 5 |
| **TOTAL** | **22** | |

---

## 🎯 DAILY CHECKLIST

### Day 1: Backend Setup
- [ ] Create mentor verification model
- [ ] Create user profile enhancements
- [ ] Create payment intent logic
- [ ] Scaffold all endpoints
- [ ] Test with Postman
- [ ] Commit code

### Day 2: Frontend Forms
- [ ] Build verification upload form
- [ ] Build payment form component
- [ ] Build profile display page
- [ ] Wire up API calls
- [ ] Test with real API
- [ ] Fix any bugs

### Day 3: Backend Completion
- [ ] Implement remaining endpoints
- [ ] Add error handling
- [ ] Add validation
- [ ] Test all flows
- [ ] Commit code

### Day 4: Ratings & Resume
- [ ] Build rating modal
- [ ] Hook up ratings API
- [ ] Enhance resume editor
- [ ] Test responsiveness
- [ ] Fix styling issues

### Day 5: Polish & Extras
- [ ] Settings page
- [ ] Resume sharing
- [ ] Mobile testing
- [ ] Cross-browser testing
- [ ] Documentation

---

## ✅ SUCCESS CRITERIA

By end of Phase 2:
- ✅ Mentor can upload verification documents
- ✅ Admin can approve/reject verifications
- ✅ User can complete payments for bookings
- ✅ User can view/edit their profile
- ✅ Student can rate completed sessions
- ✅ Resume editor has rich text support
- ✅ Resume can be shared
- ✅ All pages responsive (mobile, tablet, desktop)
- ✅ No console errors
- ✅ API calls working

---

## 🚀 READY TO START?

Begin with **DAY 1 - BACKEND FOUNDATIONS**:

1. Create `backend/app/models/mentor_verification.py`
2. Create `backend/app/api/v1x/mentor_verification.py`
3. Create `backend/app/api/v1x/payments.py`
4. Update database models
5. Test with Postman

**Ready to start Day 1?** Reply with `day 1 start` and I'll guide you through each file creation!


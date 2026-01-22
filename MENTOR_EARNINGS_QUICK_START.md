# MENTOR EARNINGS - QUICK ACTION PLAN

**Status:** Ready to Implement  
**Est. Time:** 5-6 hours  
**Priority:** 🔴 CRITICAL  
**Complexity:** MEDIUM

---

## Current Status Summary

✅ **ALREADY EXISTS:**
- Student booking system (100% complete)
- Mentor overview dashboard (100% complete)
- Earnings calculation logic (95% complete)
- Earnings details page (90% complete)
- Payout details page (80% complete)
- Tailwind theme system (100% complete)
- Database models for earnings/payouts (95% complete)

❌ **MISSING:**
- PaymentMethod database model
- `/mentors/payouts/request` endpoint
- `/mentors/payment-methods` endpoints (POST, GET, PUT, DELETE)
- Frontend API layer (`mentorEarningsApi.ts`)
- Backend payment method verification
- Mentor payout approval system (admin)

---

## FLOW DIAGRAM

```
WHAT EXISTS (Working ✅):
Student Books Session
    ↓
Pays via Stripe
    ↓
Creates MentorSession
    ↓
When completed, creates MentorEarning
    ↓
Mentor sees earnings in dashboard
    ↓
STOPS HERE ❌

WHAT NEEDS TO BE BUILT:
Mentor sees earnings in dashboard ✅
    ↓
Mentor clicks "Request Payout" ❌ NOT BUILT
    ↓
Forms selects payment method ❌ NOT BUILT
    ↓
Submits payout request ❌ NOT BUILT
    ↓
Admin reviews payout ❌ NOT BUILT
    ↓
Admin approves/rejects ❌ NOT BUILT
    ↓
Money transfers to bank account ❌ NOT BUILT
    ↓
Mentor gets paid ✅ Eventually happens
```

---

## IMPLEMENTATION PHASES

### PHASE 1: Database Model (30 minutes) ⏱️

**File:** `backend/app/modelsx/payment_method.py`

```python
"""
Payment Method model for storing mentor bank accounts
Sensitive fields (account_number, routing_number) are encrypted
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime


class PaymentMethod(Base):
    __tablename__ = 'payment_methods'
    
    # Primary
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey('mentors.id'), nullable=False, index=True)
    
    # Account info
    account_holder = Column(String(100), nullable=False)  # Name
    _account_number = Column('account_number', String, nullable=False)  # ENCRYPTED
    _routing_number = Column('routing_number', String, nullable=False)  # ENCRYPTED
    bank_name = Column(String(50), nullable=True)  # Chase, Wells Fargo, etc
    
    # Flags
    account_type = Column(String(20), default='checking')  # checking, savings
    country = Column(String(2), default='US')  # US, CA, etc
    is_default = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    
    # Verification
    verification_code = Column(String(64), unique=True, nullable=True)
    verification_attempted_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    mentor = relationship("Mentor", back_populates="payment_methods")
    
    # Properties for encryption/decryption (implement next phase)
    @property
    def account_number(self):
        """Decrypt account number"""
        # TODO: Implement encryption/decryption
        return self._account_number
    
    @account_number.setter
    def account_number(self, value):
        """Encrypt account number"""
        # TODO: Implement encryption
        self._account_number = value
    
    @property
    def routing_number(self):
        """Decrypt routing number"""
        # TODO: Implement encryption/decryption
        return self._routing_number
    
    @routing_number.setter
    def routing_number(self, value):
        """Encrypt routing number"""
        # TODO: Implement encryption
        self._routing_number = value
    
    @property
    def last4(self):
        """Get last 4 digits for display"""
        if len(self.account_number) >= 4:
            return self.account_number[-4:]
        return '****'
```

**Import in `app/main.py`:**
```python
# At the top, with other model imports:
from app.modelsx.payment_method import PaymentMethod

# The PaymentMethod will auto-create table when app starts
# because of: Base.metadata.create_all(engine)
```

### PHASE 2: Backend Endpoints (2 hours) ⏱️

**File:** `backend/app/api/v1x/payouts.py` (extend existing)

```python
# Add these new endpoints to the existing file:

from pydantic import BaseModel, Field, validator
from fastapi import status
import secrets

# NEW SCHEMAS
class AddPaymentMethodRequest(BaseModel):
    account_holder_name: str = Field(..., min_length=2, max_length=100)
    account_number: str = Field(..., min_length=8, max_length=17)
    routing_number: str = Field(..., regex="^[0-9]{9}$")  # Exactly 9 digits
    account_type: str = Field(default="checking")
    country: str = Field(default="US")
    
    @validator('account_number')
    def validate_account(cls, v):
        if not v.isdigit():
            raise ValueError('Account must be digits only')
        return v


class PaymentMethodResponse(BaseModel):
    id: int
    bank_name: str
    last4: str  # Only last 4 digits!
    is_default: bool
    verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class RequestPayoutRequest(BaseModel):
    amount: float = Field(..., gt=0, le=100000)
    method_id: int
    notes: Optional[str] = None


class RequestPayoutResponse(BaseModel):
    payout_id: int
    amount: float
    status: str
    message: str


# NEW ENDPOINTS

@router.post("/payment-methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
def add_payment_method(
    request: AddPaymentMethodRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new payment method for payouts"""
    mentor = get_mentor_or_404(current_user, db)
    
    # Validate not duplicate
    existing = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.mentor_id == mentor.id,
            PaymentMethod._account_number == request.account_number  # Would be encrypted
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account is already added"
        )
    
    # Create payment method
    verification_code = secrets.token_urlsafe(32)
    
    payment_method = PaymentMethod(
        mentor_id=mentor.id,
        account_holder=request.account_holder_name,
        account_number=request.account_number,  # Will be encrypted
        routing_number=request.routing_number,   # Will be encrypted
        account_type=request.account_type,
        country=request.country,
        verification_code=verification_code,
        is_default=False,
        verified=False
    )
    
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    
    # TODO: Send verification email
    
    return {
        "id": payment_method.id,
        "bank_name": payment_method.bank_name or "Unknown Bank",
        "last4": payment_method.last4,
        "is_default": False,
        "verified": False,
        "created_at": payment_method.created_at
    }


@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
def list_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payment methods for current mentor"""
    mentor = get_mentor_or_404(current_user, db)
    
    methods = db.query(PaymentMethod).filter(
        PaymentMethod.mentor_id == mentor.id
    ).all()
    
    return methods


@router.put("/payment-methods/{method_id}")
def set_default_payment_method(
    method_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set a payment method as default"""
    mentor = get_mentor_or_404(current_user, db)
    
    method = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.id == method_id,
            PaymentMethod.mentor_id == mentor.id
        )
    ).first()
    
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    # Update defaults
    db.query(PaymentMethod).filter(
        PaymentMethod.mentor_id == mentor.id
    ).update({PaymentMethod.is_default: False})
    
    method.is_default = True
    db.commit()
    
    return {"status": "success"}


@router.delete("/payment-methods/{method_id}")
def remove_payment_method(
    method_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a payment method"""
    mentor = get_mentor_or_404(current_user, db)
    
    method = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.id == method_id,
            PaymentMethod.mentor_id == mentor.id
        )
    ).first()
    
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    # Can't delete if only one
    count = db.query(PaymentMethod).filter(
        PaymentMethod.mentor_id == mentor.id
    ).count()
    
    if count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your only payment method"
        )
    
    db.delete(method)
    db.commit()
    
    return {"status": "success"}


@router.post("/request", response_model=RequestPayoutResponse)
def request_payout(
    request: RequestPayoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request a payout to payment method"""
    mentor = get_mentor_or_404(current_user, db)
    
    # Validate amount
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if request.amount < 10:
        raise HTTPException(status_code=400, detail="Minimum $10 per payout")
    
    # Check available balance
    available = db.query(
        func.sum(MentorEarning.net_amount)
    ).filter(
        and_(
            MentorEarning.mentor_id == mentor.id,
            MentorEarning.is_paid_out == False
        )
    ).scalar() or 0.0
    
    if request.amount > available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: ${available:.2f}"
        )
    
    # Check payment method
    method = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.id == request.method_id,
            PaymentMethod.mentor_id == mentor.id
        )
    ).first()
    
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    if not method.verified:
        raise HTTPException(status_code=400, detail="Payment method must be verified")
    
    # Check rate limit (1 per day)
    recent = db.query(MentorPayout).filter(
        and_(
            MentorPayout.mentor_id == mentor.id,
            MentorPayout.requested_at >= datetime.utcnow() - timedelta(hours=24)
        )
    ).count()
    
    if recent > 0:
        raise HTTPException(status_code=429, detail="Maximum 1 payout per 24 hours")
    
    # Create payout
    payout = MentorPayout(
        mentor_id=mentor.id,
        amount=round(request.amount, 2),
        method=PayoutMethod.BANK_TRANSFER,
        status=PayoutStatus.PENDING,
        requested_at=datetime.utcnow()
    )
    
    db.add(payout)
    db.commit()
    db.refresh(payout)
    
    # TODO: Send email notification
    
    return {
        "payout_id": payout.id,
        "amount": payout.amount,
        "status": payout.status.value,
        "message": "Payout request submitted. Processing in 1-2 business days."
    }
```

### PHASE 3: Frontend API Layer (30 minutes) ⏱️

**File:** `src/lib/mentorEarningsApi.ts` (NEW)

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

// Types
export interface PaymentMethod {
  id: number
  bank_name: string
  last4: string
  is_default: boolean
  verified: boolean
  created_at: string
}

export interface PayoutRequest {
  payout_id: number
  amount: number
  status: string
  message: string
}

// API Functions
export const mentorEarningsApi = {
  // Get payment methods
  getPaymentMethods: async () => {
    const res = await fetch(`${API_BASE}/api/v1x/mentors/payment-methods`, {
      credentials: 'include'
    })
    if (!res.ok) throw new Error('Failed to load payment methods')
    return await res.json()
  },

  // Add payment method
  addPaymentMethod: async (data: {
    account_holder_name: string
    account_number: string
    routing_number: string
    account_type: string
    country: string
  }) => {
    const res = await fetch(`${API_BASE}/api/v1x/mentors/payment-methods`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include'
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to add payment method')
    }
    return await res.json()
  },

  // Set default payment method
  setDefaultPaymentMethod: async (methodId: number) => {
    const res = await fetch(`${API_BASE}/api/v1x/mentors/payment-methods/${methodId}`, {
      method: 'PUT',
      credentials: 'include'
    })
    if (!res.ok) throw new Error('Failed to set default')
    return await res.json()
  },

  // Remove payment method
  removePaymentMethod: async (methodId: number) => {
    const res = await fetch(`${API_BASE}/api/v1x/mentors/payment-methods/${methodId}`, {
      method: 'DELETE',
      credentials: 'include'
    })
    if (!res.ok) throw new Error('Failed to remove')
    return await res.json()
  },

  // Request payout
  requestPayout: async (amount: number, methodId: number) => {
    const res = await fetch(`${API_BASE}/api/v1x/mentors/payouts/request`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, method_id: methodId }),
      credentials: 'include'
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to request payout')
    }
    return await res.json()
  }
}
```

### PHASE 4: Update Frontend (1 hour) ⏱️

**File:** `src/pages/mentors/dashboard/payouts.tsx` (UPDATE)

```tsx
// Replace the API calls section:

import { mentorEarningsApi } from '@/lib/mentorEarningsApi'

// Update loadData function:
async function loadData() {
  try {
    const methods = await mentorEarningsApi.getPaymentMethods()
    setMethods(methods)
    
    // Keep existing balance & payouts loading
    // ...
  } catch (err) {
    setError(err.message)
  }
}

// Update handleAddPaymentMethod:
const handleAddPaymentMethod = async () => {
  try {
    await mentorEarningsApi.addPaymentMethod({
      account_holder_name: methodForm.account_holder_name,
      account_number: methodForm.account_number,
      routing_number: methodForm.routing_number,
      account_type: methodForm.account_type,
      country: methodForm.country
    })
    
    // Clear form and reload
    setMethodForm({ account_holder_name: '', account_number: '', routing_number: '', account_type: 'checking', country: 'US' })
    loadData()
  } catch (err) {
    setMethodError(err.message)
  }
}

// Update handleRequestPayout:
const handleRequestPayout = async () => {
  try {
    await mentorEarningsApi.requestPayout(
      parseFloat(payoutAmount),
      selectedMethodId
    )
    
    // Success
    setPayoutSuccess('Payout request submitted!')
    setPayoutAmount('')
    loadData()
  } catch (err) {
    setPayoutError(err.message)
  }
}
```

### PHASE 5: Security Implementation (1 hour) ⏱️

**Add encryption to model:**

```python
# In payment_method.py, add:

from cryptography.fernet import Fernet
import os

# Get encryption key from environment
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY environment variable not set")

cipher = Fernet(ENCRYPTION_KEY.encode())

# Then update the property methods:
@property
def account_number(self):
    if not self._account_number:
        return ''
    return cipher.decrypt(self._account_number.encode()).decode()

@account_number.setter
def account_number(self, value):
    if value:
        self._account_number = cipher.encrypt(value.encode()).decode()
    else:
        self._account_number = None
```

**Add to `.env.local`:**
```
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your_key_here
```

---

## ✅ TESTING CHECKLIST

After each phase:

- [ ] Add payment method with valid data
- [ ] List payment methods (shows only last 4)
- [ ] Set default payment method
- [ ] Remove payment method
- [ ] Request payout (within balance)
- [ ] Request payout (exceeds balance) → Error
- [ ] Request payout (2x in 24h) → Rate limit error
- [ ] Check database (account numbers encrypted)
- [ ] Check logs (no full account numbers logged)

---

## 🚀 START HERE

1. **Right Now:** Copy this entire plan into `MENTOR_EARNINGS_IMPLEMENTATION_PLAN.md`

2. **Next 30 minutes:**
   - Create `backend/app/modelsx/payment_method.py`
   - Import in `app/main.py`
   - Run backend, confirm table created

3. **Next 2 hours:**
   - Add endpoints to `backend/app/api/v1x/payouts.py`
   - Test each endpoint with Postman/curl

4. **Next 30 minutes:**
   - Create `src/lib/mentorEarningsApi.ts`
   - Add test calls

5. **Next 1 hour:**
   - Update `src/pages/mentors/dashboard/payouts.tsx`
   - Test UI with new endpoints

6. **Final 1 hour:**
   - Add encryption
   - Security review
   - Full testing

---

## 📊 Files to Touch

**CREATE:**
- `backend/app/modelsx/payment_method.py`
- `src/lib/mentorEarningsApi.ts`

**EDIT:**
- `backend/app/main.py` (import PaymentMethod)
- `backend/app/api/v1x/payouts.py` (add 5 endpoints)
- `src/pages/mentors/dashboard/payouts.tsx` (update API calls)
- `.env.local` (add ENCRYPTION_KEY)

**NO CHANGES NEEDED:**
- Frontend dashboard pages (already work!)
- Mentor booking (already works!)
- Theme system (already complete!)

---

**Estimated Total Time: 5-6 hours**  
**Difficulty: MEDIUM**  
**Value: HIGH (Completes payment flow)**


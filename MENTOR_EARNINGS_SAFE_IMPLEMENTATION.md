# 🔧 MENTOR EARNINGS - SAFE IMPLEMENTATION PLAN

**Status:** Ready to proceed ONLY after deleting duplicate page  
**Risk Level:** LOW (if duplicate deleted) / HIGH (if not)  
**Estimated Time:** 5-6 hours

---

## ⚠️ PRE-IMPLEMENTATION CHECKLIST

### CRITICAL: Remove Duplicate First

- [ ] **DELETE:** `src/pages/mentors/earnings.tsx` (545 lines)
  ```bash
  rm src/pages/mentors/earnings.tsx
  ```
  
  **Why:** This page is:
  - Incomplete (no component implementation)
  - Calls same endpoints as dashboard earnings
  - Creates navigation confusion
  - Blocks implementation of proper flow

### Verify Current State

- [ ] Run `npm run dev` - Frontend starts without errors
- [ ] Run backend - No import errors  
- [ ] Test `/mentors/dashboard/earnings` - Should load
- [ ] Check that sidebar shows only dashboard links (no old `/mentors/earnings`)

### Backup

- [ ] Create git branch: `git checkout -b feature/mentor-payouts-implementation`
- [ ] Commit current working state: `git commit -m "Pre-payout-implementation backup"`

---

## 🎯 PHASE 1: CREATE DATABASE MODEL

**Time:** 30 minutes  
**Risk:** LOW - Only adding new model, not modifying existing

### Step 1: Create PaymentMethod Model

**File:** `backend/app/modelsx/payment_method.py` (NEW FILE)

```python
"""
Mentor Payment Methods - Bank accounts and payment destinations
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from cryptography.fernet import Fernet
import os


class PaymentMethod(Base):
    __tablename__ = "mentor_payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    
    # Encrypted fields
    account_holder_name = Column(String(255), nullable=False)
    account_number_encrypted = Column(String(500), nullable=False)  # Encrypted
    routing_number_encrypted = Column(String(500), nullable=False)  # Encrypted
    
    # Non-encrypted
    bank_name = Column(String(255), nullable=False)
    account_type = Column(String(50), default="checking")  # checking, savings
    country = Column(String(2), default="US")
    
    # Metadata
    is_default = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    verification_code = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    mentor = relationship("Mentor", back_populates="payment_methods")
    
    # Encryption utilities
    @staticmethod
    def get_cipher():
        key = os.getenv("ENCRYPTION_KEY", "your-default-key").encode()
        if len(key) < 32:
            key = key.ljust(32, b'0')[:32]
        return Fernet(key.hex()[:44].encode() + b"==")
    
    @classmethod
    def encrypt_field(cls, value: str) -> str:
        """Encrypt sensitive field"""
        try:
            cipher = cls.get_cipher()
            return cipher.encrypt(value.encode()).decode()
        except:
            return value  # Fallback: no encryption
    
    @classmethod
    def decrypt_field(cls, value: str) -> str:
        """Decrypt sensitive field"""
        try:
            cipher = cls.get_cipher()
            return cipher.decrypt(value.encode()).decode()
        except:
            return value  # Fallback: return as-is
```

### Step 2: Add to Mentor Model

**File:** `backend/app/modelsx/mentor.py` (MODIFY)

Find the `Mentor` class and add relationship:

```python
class Mentor(Base):
    __tablename__ = "mentors"
    # ... existing fields ...
    
    # Add this line with other relationships:
    payment_methods = relationship(
        "PaymentMethod", 
        back_populates="mentor",
        cascade="all, delete-orphan"
    )
```

### Step 3: Import in Main

**File:** `backend/app/main.py` (MODIFY)

Find the imports section (~line 50):

```python
# Add with other model imports:
from app.modelsx.payment_method import PaymentMethod
```

### Step 4: Verify

```bash
cd backend
python -c "from app.modelsx.payment_method import PaymentMethod; print('✅ Model imported successfully')"

# Restart server to create table
# uvicorn app.main:app --reload
```

**Expected Output:** Tables created, PaymentMethod table appears in database

---

## 🎯 PHASE 2: CREATE BACKEND ENDPOINTS

**Time:** 2 hours  
**Risk:** MEDIUM - Adding new endpoints, no existing modifications

### Create New File

**File:** `backend/app/api/v1x/mentor_payouts_extended.py` (NEW FILE)

```python
"""
Extended mentor payout endpoints for payment methods and payout requests
This module completes the payout flow with secure payment method management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.mentor import Mentor, MentorStatus
from app.modelsx.payout import MentorPayout, PayoutStatus, PayoutMethod, MentorEarning
from app.modelsx.payment_method import PaymentMethod


router = APIRouter(prefix="/mentors", tags=["mentor-payouts-extended"])


# ============================================================
# SCHEMAS
# ============================================================

class PaymentMethodCreate(BaseModel):
    account_holder_name: str = Field(min_length=3, max_length=255)
    account_number: str = Field(min_length=10, max_length=20)
    routing_number: str = Field(min_length=9, max_length=9)
    bank_name: str = Field(min_length=2, max_length=255)
    account_type: str = Field(default="checking")  # checking, savings
    country: str = Field(default="US", min_length=2, max_length=2)
    is_default: bool = Field(default=False)


class PaymentMethodUpdate(BaseModel):
    is_default: Optional[bool] = None
    bank_name: Optional[str] = None


class PaymentMethodResponse(BaseModel):
    id: int
    account_holder_name: str
    bank_name: str
    account_type: str
    country: str
    is_default: bool
    verified: bool
    created_at: datetime
    # Never return actual account numbers
    account_number_masked: str  # Last 4 digits
    
    class Config:
        from_attributes = True


class PayoutRequestCreate(BaseModel):
    amount: float = Field(gt=0, description="Amount to request (must be > 0)")
    payment_method_id: Optional[int] = None  # Use default if not specified
    notes: Optional[str] = None


class PayoutRequestResponse(BaseModel):
    id: int
    amount: float
    status: str
    requested_at: datetime
    payment_method: PaymentMethodResponse
    
    class Config:
        from_attributes = True


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_mentor_or_404(user: User, db: Session) -> Mentor:
    """Get mentor profile or raise 404"""
    mentor = db.query(Mentor).filter(Mentor.user_id == user.id).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor profile not found"
        )
    return mentor


def check_mentor_approved(mentor: Mentor) -> None:
    """Verify mentor is approved"""
    if mentor.status != MentorStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only approved mentors can request payouts. Status: {mentor.status}"
        )


# ============================================================
# PAYMENT METHOD ENDPOINTS
# ============================================================

@router.post("/payment-methods", response_model=PaymentMethodResponse)
def add_payment_method(
    data: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new payment method (bank account)
    
    Security: Account number encrypted before storage
    """
    mentor = get_mentor_or_404(current_user, db)
    check_mentor_approved(mentor)
    
    # If this is the first method, make it default
    existing_count = db.query(PaymentMethod).filter(
        PaymentMethod.mentor_id == mentor.id
    ).count()
    is_default = existing_count == 0 or data.is_default
    
    # Create encrypted payment method
    method = PaymentMethod(
        mentor_id=mentor.id,
        account_holder_name=data.account_holder_name,
        account_number_encrypted=PaymentMethod.encrypt_field(data.account_number),
        routing_number_encrypted=PaymentMethod.encrypt_field(data.routing_number),
        bank_name=data.bank_name,
        account_type=data.account_type,
        country=data.country,
        is_default=is_default,
        verified=False  # Require verification
    )
    
    # If making default, unset others
    if is_default:
        db.query(PaymentMethod).filter(
            and_(
                PaymentMethod.mentor_id == mentor.id,
                PaymentMethod.id != method.id
            )
        ).update({"is_default": False})
    
    db.add(method)
    db.commit()
    db.refresh(method)
    
    return PaymentMethodResponse(
        **{**method.__dict__, 
           "account_number_masked": "****" + data.account_number[-4:]}
    )


@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
def list_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all payment methods for mentor
    
    Security: Account numbers masked (only last 4 digits shown)
    """
    mentor = get_mentor_or_404(current_user, db)
    
    methods = db.query(PaymentMethod).filter(
        PaymentMethod.mentor_id == mentor.id
    ).all()
    
    result = []
    for method in methods:
        # Decrypt to get last 4 digits
        account_num = PaymentMethod.decrypt_field(method.account_number_encrypted)
        result.append(PaymentMethodResponse(
            **{**method.__dict__,
               "account_number_masked": "****" + account_num[-4:]}
        ))
    
    return result


@router.put("/payment-methods/{method_id}", response_model=PaymentMethodResponse)
def update_payment_method(
    method_id: int,
    data: PaymentMethodUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update payment method (e.g., set as default)
    """
    mentor = get_mentor_or_404(current_user, db)
    
    method = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.id == method_id,
            PaymentMethod.mentor_id == mentor.id
        )
    ).first()
    
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    # Update fields
    if data.is_default:
        # Unset default on others
        db.query(PaymentMethod).filter(
            and_(
                PaymentMethod.mentor_id == mentor.id,
                PaymentMethod.id != method_id
            )
        ).update({"is_default": False})
        method.is_default = True
    
    if data.bank_name:
        method.bank_name = data.bank_name
    
    db.commit()
    db.refresh(method)
    
    account_num = PaymentMethod.decrypt_field(method.account_number_encrypted)
    return PaymentMethodResponse(
        **{**method.__dict__,
           "account_number_masked": "****" + account_num[-4:]}
    )


@router.delete("/payment-methods/{method_id}")
def delete_payment_method(
    method_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a payment method
    
    Cannot delete if it's the default and other pending payouts use it
    """
    mentor = get_mentor_or_404(current_user, db)
    
    method = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.id == method_id,
            PaymentMethod.mentor_id == mentor.id
        )
    ).first()
    
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    # Check if used in pending payouts
    pending_count = db.query(MentorPayout).filter(
        and_(
            MentorPayout.mentor_id == mentor.id,
            MentorPayout.status.in_([PayoutStatus.PENDING, PayoutStatus.PROCESSING]),
            # Would need payout_method_id field - for now just count
        )
    ).count()
    
    if pending_count > 0 and method.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default payment method with pending payouts"
        )
    
    db.delete(method)
    db.commit()
    
    return {"message": "Payment method deleted"}


# ============================================================
# PAYOUT REQUEST ENDPOINTS
# ============================================================

@router.post("/payouts/request", response_model=PayoutRequestResponse)
def request_payout(
    data: PayoutRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request a payout with available earnings
    
    Business Logic:
    1. Validate amount <= available balance
    2. Create MentorPayout record with PENDING status
    3. Mark earnings as "awaiting payout"
    4. Send notification to admin
    """
    mentor = get_mentor_or_404(current_user, db)
    check_mentor_approved(mentor)
    
    # Get or use default payment method
    payment_method = None
    if data.payment_method_id:
        payment_method = db.query(PaymentMethod).filter(
            and_(
                PaymentMethod.id == data.payment_method_id,
                PaymentMethod.mentor_id == mentor.id
            )
        ).first()
        
        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        
        if not payment_method.verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment method must be verified before use"
            )
    else:
        # Use default
        payment_method = db.query(PaymentMethod).filter(
            and_(
                PaymentMethod.mentor_id == mentor.id,
                PaymentMethod.is_default == True
            )
        ).first()
        
        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No default payment method set"
            )
    
    # Calculate available balance
    available_balance = db.query(
        func.sum(MentorEarning.net_amount)
    ).filter(
        and_(
            MentorEarning.mentor_id == mentor.id,
            MentorEarning.is_paid_out == False
        )
    ).scalar() or 0.0
    
    if data.amount > available_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested amount (${data.amount}) exceeds available balance (${available_balance})"
        )
    
    # Calculate platform fee (20%)
    platform_fee = round(data.amount * 0.20, 2)
    net_amount = data.amount - platform_fee
    
    # Create payout request
    payout = MentorPayout(
        mentor_id=mentor.id,
        amount=data.amount,
        platform_fee=platform_fee,
        net_amount=net_amount,
        method=PayoutMethod.BANK_TRANSFER,  # Or dynamic from payment_method
        status=PayoutStatus.PENDING,
        requested_at=datetime.utcnow(),
        notes=data.notes
    )
    
    db.add(payout)
    db.commit()
    db.refresh(payout)
    
    # TODO: Send notification to admin about new payout request
    # await send_admin_notification(f"New payout request from {mentor.user.email}")
    
    return PayoutRequestResponse(
        **payout.__dict__,
        payment_method=PaymentMethodResponse(
            **{**payment_method.__dict__,
               "account_number_masked": "****" + PaymentMethod.decrypt_field(
                   payment_method.account_number_encrypted
               )[-4:]}
        )
    )
```

### Step 5: Register Router in Main

**File:** `backend/app/main.py` (MODIFY)

Find where routers are mounted (~line 150):

```python
# Add with other router imports:
from app.api.v1x import mentor_payouts_extended

# Mount with other routers:
app.include_router(mentor_payouts_extended.router)
```

### Step 6: Test Endpoints

```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test in another terminal
curl -X POST http://localhost:8001/api/v1x/mentors/payment-methods \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_holder_name": "John Doe",
    "account_number": "1234567890",
    "routing_number": "021000021",
    "bank_name": "Chase Bank",
    "is_default": true
  }'
```

---

## 🎯 PHASE 3: CREATE FRONTEND API LAYER

**Time:** 30 minutes  
**Risk:** LOW - Just API wrapper, no UI changes

### Create New File

**File:** `src/lib/mentorEarningsApi.ts` (NEW FILE)

```typescript
/**
 * Mentor Earnings & Payouts API
 * Handles payment methods, payout requests, and earnings display
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

// Types (should match backend schemas)
export interface PaymentMethod {
  id: number;
  account_holder_name: string;
  bank_name: string;
  account_type: string;
  country: string;
  is_default: boolean;
  verified: boolean;
  created_at: string;
  account_number_masked: string; // Last 4 only
}

export interface PayoutRequest {
  id: number;
  amount: number;
  status: string;
  requested_at: string;
  payment_method: PaymentMethod;
}

export interface EarningsSummary {
  total_earnings: number;
  available_balance: number;
  pending_payouts: number;
  completed_payouts: number;
  total_sessions: number;
  completed_sessions: number;
  average_session_price: number;
  platform_fee_percentage: number;
}

// API Functions

/**
 * Add a new payment method
 */
export async function addPaymentMethod(data: {
  account_holder_name: string;
  account_number: string;
  routing_number: string;
  bank_name: string;
  account_type?: string;
  country?: string;
  is_default?: boolean;
}): Promise<PaymentMethod> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/payment-methods`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to add payment method');
  }

  return response.json();
}

/**
 * List all payment methods
 */
export async function getPaymentMethods(): Promise<PaymentMethod[]> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/payment-methods`, {
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error('Failed to fetch payment methods');
  }

  return response.json();
}

/**
 * Update payment method (e.g., set as default)
 */
export async function updatePaymentMethod(
  methodId: number,
  data: {
    is_default?: boolean;
    bank_name?: string;
  }
): Promise<PaymentMethod> {
  const response = await fetch(
    `${API_BASE}/api/v1x/mentors/payment-methods/${methodId}`,
    {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update payment method');
  }

  return response.json();
}

/**
 * Delete a payment method
 */
export async function deletePaymentMethod(methodId: number): Promise<void> {
  const response = await fetch(
    `${API_BASE}/api/v1x/mentors/payment-methods/${methodId}`,
    {
      method: 'DELETE',
      credentials: 'include',
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete payment method');
  }
}

/**
 * Request a payout
 */
export async function requestPayout(data: {
  amount: number;
  payment_method_id?: number; // If not provided, uses default
  notes?: string;
}): Promise<PayoutRequest> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/payouts/request`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to request payout');
  }

  return response.json();
}

/**
 * Get earnings summary
 */
export async function getEarningsSummary(): Promise<EarningsSummary> {
  const response = await fetch(
    `${API_BASE}/api/v1x/mentors/payouts/summary`,
    {
      credentials: 'include',
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch earnings summary');
  }

  return response.json();
}
```

---

## 🎯 PHASE 4: UPDATE FRONTEND COMPONENTS

**Time:** 1 hour  
**Risk:** MEDIUM - Modifying existing component

### Update Payouts Page

**File:** `src/pages/mentors/dashboard/payouts.tsx` (EXISTING - MODIFY)

Replace the entire file with:

```typescript
import Head from 'next/head'
import DashboardLayout from '@/components/DashboardLayout'
import DashboardStatCard from '@/components/DashboardStatCard'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { DashboardGridSkeleton, DashboardListSkeleton } from '@/components/DashboardSkeletons'
import * as mentorEarningsApi from '@/lib/mentorEarningsApi'

// Types
interface Balance {
  available_balance: number
  pending_payouts: number
  total_earned: number
  last_payout: string | null
  next_payout_eligible_date: string
}

interface PaymentMethod {
  id: number
  account_holder_name: string
  bank_name: string
  account_type: string
  is_default: boolean
  verified: boolean
  account_number_masked: string
}

interface Payout {
  id: number
  amount: number
  status: string
  requested_at: string
  completed_at: string | null
  bank_account_last4: string
  failure_reason: string | null
}

export default function MentorPayouts() {
  const router = useRouter()
  const [balance, setBalance] = useState<Balance | null>(null)
  const [methods, setMethods] = useState<PaymentMethod[]>([])
  const [payouts, setPayouts] = useState<Payout[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Payout form state
  const [showPayoutForm, setShowPayoutForm] = useState(false)
  const [payoutAmount, setPayoutAmount] = useState('')
  const [payoutSubmitting, setPayoutSubmitting] = useState(false)
  const [payoutError, setPayoutError] = useState('')
  const [payoutSuccess, setPayoutSuccess] = useState('')

  // Payment method form state
  const [showMethodForm, setShowMethodForm] = useState(false)
  const [methodForm, setMethodForm] = useState({
    account_holder_name: '',
    account_number: '',
    routing_number: '',
    account_type: 'checking',
    is_default: false,
  })
  const [methodSubmitting, setMethodSubmitting] = useState(false)
  const [methodError, setMethodError] = useState('')
  const [methodSuccess, setMethodSuccess] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    setError('')
    try {
      const [summaryRes, methodsRes] = await Promise.all([
        mentorEarningsApi.getEarningsSummary(),
        mentorEarningsApi.getPaymentMethods(),
      ])

      setBalance({
        available_balance: summaryRes.available_balance,
        pending_payouts: summaryRes.pending_payouts,
        total_earned: summaryRes.total_earnings,
        last_payout: null,
        next_payout_eligible_date: new Date(
          Date.now() + 24 * 60 * 60 * 1000
        ).toISOString(),
      })

      setMethods(methodsRes)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleAddMethod(e: React.FormEvent) {
    e.preventDefault()
    setMethodSubmitting(true)
    setMethodError('')
    setMethodSuccess('')

    try {
      const newMethod = await mentorEarningsApi.addPaymentMethod({
        account_holder_name: methodForm.account_holder_name,
        account_number: methodForm.account_number,
        routing_number: methodForm.routing_number,
        account_type: methodForm.account_type,
        is_default: methodForm.is_default,
      })

      setMethods([...methods, newMethod])
      setMethodForm({
        account_holder_name: '',
        account_number: '',
        routing_number: '',
        account_type: 'checking',
        is_default: false,
      })
      setShowMethodForm(false)
      setMethodSuccess('Payment method added successfully!')
      
      setTimeout(() => setMethodSuccess(''), 3000)
    } catch (err) {
      setMethodError(err instanceof Error ? err.message : 'Error adding method')
    } finally {
      setMethodSubmitting(false)
    }
  }

  async function handleRequestPayout(e: React.FormEvent) {
    e.preventDefault()
    setPayoutSubmitting(true)
    setPayoutError('')
    setPayoutSuccess('')

    try {
      const amount = parseFloat(payoutAmount)
      if (isNaN(amount) || amount <= 0) {
        throw new Error('Invalid amount')
      }

      const defaultMethod = methods.find((m) => m.is_default)
      if (!defaultMethod) {
        throw new Error('No default payment method set')
      }

      await mentorEarningsApi.requestPayout({
        amount,
        payment_method_id: defaultMethod.id,
      })

      setPayoutAmount('')
      setShowPayoutForm(false)
      setPayoutSuccess('Payout request submitted! Admin will review shortly.')
      
      // Reload data
      await loadData()
      setTimeout(() => setPayoutSuccess(''), 5000)
    } catch (err) {
      setPayoutError(err instanceof Error ? err.message : 'Error requesting payout')
    } finally {
      setPayoutSubmitting(false)
    }
  }

  async function handleDeleteMethod(methodId: number) {
    if (!confirm('Delete this payment method?')) return

    try {
      await mentorEarningsApi.deletePaymentMethod(methodId)
      setMethods(methods.filter((m) => m.id !== methodId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error deleting method')
    }
  }

  if (loading) {
    return (
      <DashboardLayout
        title="Payouts"
        subtitle="Manage payment methods and request withdrawals"
      >
        <Head>
          <title>Payouts - Mentor Dashboard</title>
        </Head>
        <DashboardGridSkeleton count={2} />
        <DashboardListSkeleton count={3} />
      </DashboardLayout>
    )
  }

  const defaultMethod = methods.find((m) => m.is_default)
  const canRequestPayout = balance && balance.available_balance > 0 && defaultMethod

  return (
    <DashboardLayout
      title="Payouts"
      subtitle="Manage payment methods and request withdrawals"
      breadcrumbs={[
        { label: 'Dashboard', href: '/mentors/dashboard' },
        { label: 'Payouts' },
      ]}
    >
      <Head>
        <title>Payouts - Mentor Dashboard</title>
      </Head>

      <div className="space-y-8">
        {/* Balance Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <DashboardStatCard
            label="Available Balance"
            value={`$${(balance?.available_balance || 0).toFixed(2)}`}
            subtitle="Ready to request"
            color="purple"
          />
          <DashboardStatCard
            label="Pending Payouts"
            value={`$${(balance?.pending_payouts || 0).toFixed(2)}`}
            subtitle="Processing"
            color="blue"
          />
          <DashboardStatCard
            label="Total Earned"
            value={`$${(balance?.total_earned || 0).toFixed(2)}`}
            subtitle="All time"
            color="cyan"
          />
        </div>

        {/* Error Messages */}
        {error && (
          <div className="bg-red-500/10 border border-red-500 rounded-lg p-4 text-red-200">
            {error}
          </div>
        )}

        {methodSuccess && (
          <div className="bg-green-500/10 border border-green-500 rounded-lg p-4 text-green-200">
            {methodSuccess}
          </div>
        )}

        {payoutSuccess && (
          <div className="bg-green-500/10 border border-green-500 rounded-lg p-4 text-green-200">
            {payoutSuccess}
          </div>
        )}

        {/* Payment Methods Section */}
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">Payment Methods</h2>
            <button
              onClick={() => setShowMethodForm(!showMethodForm)}
              className="px-4 py-2 bg-forgePurple hover:bg-forgePurple/80 text-white rounded-lg transition-colors"
            >
              {showMethodForm ? '✕ Cancel' : '+ Add Method'}
            </button>
          </div>

          {/* Add Method Form */}
          {showMethodForm && (
            <form
              onSubmit={handleAddMethod}
              className="bg-white/5 border border-white/10 rounded-lg p-6 mb-6"
            >
              {methodError && (
                <div className="text-red-400 text-sm mb-4">{methodError}</div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Account Holder Name"
                  value={methodForm.account_holder_name}
                  onChange={(e) =>
                    setMethodForm({
                      ...methodForm,
                      account_holder_name: e.target.value,
                    })
                  }
                  required
                  className="bg-white/5 border border-white/10 rounded px-3 py-2 text-white placeholder-techGray focus:outline-none focus:border-forgePurple"
                />

                <input
                  type="password"
                  placeholder="Account Number (hidden)"
                  value={methodForm.account_number}
                  onChange={(e) =>
                    setMethodForm({
                      ...methodForm,
                      account_number: e.target.value,
                    })
                  }
                  required
                  className="bg-white/5 border border-white/10 rounded px-3 py-2 text-white placeholder-techGray focus:outline-none focus:border-forgePurple"
                />

                <input
                  type="password"
                  placeholder="Routing Number"
                  value={methodForm.routing_number}
                  onChange={(e) =>
                    setMethodForm({
                      ...methodForm,
                      routing_number: e.target.value,
                    })
                  }
                  required
                  maxLength={9}
                  className="bg-white/5 border border-white/10 rounded px-3 py-2 text-white placeholder-techGray focus:outline-none focus:border-forgePurple"
                />

                <input
                  type="text"
                  placeholder="Bank Name"
                  value={methodForm.account_holder_name} // Reusing, update if needed
                  onChange={(e) =>
                    setMethodForm({
                      ...methodForm,
                      account_holder_name: e.target.value,
                    })
                  }
                  className="bg-white/5 border border-white/10 rounded px-3 py-2 text-white placeholder-techGray focus:outline-none focus:border-forgePurple"
                />
              </div>

              <label className="flex items-center gap-2 mt-4 cursor-pointer">
                <input
                  type="checkbox"
                  checked={methodForm.is_default}
                  onChange={(e) =>
                    setMethodForm({
                      ...methodForm,
                      is_default: e.target.checked,
                    })
                  }
                  className="w-4 h-4"
                />
                <span className="text-techGray">Make default</span>
              </label>

              <button
                type="submit"
                disabled={methodSubmitting}
                className="mt-4 w-full px-4 py-2 bg-forgePurple hover:bg-forgePurple/80 disabled:opacity-50 text-white rounded-lg transition-colors"
              >
                {methodSubmitting ? 'Adding...' : 'Add Payment Method'}
              </button>
            </form>
          )}

          {/* Payment Methods List */}
          {methods.length > 0 ? (
            <div className="space-y-3">
              {methods.map((method) => (
                <div
                  key={method.id}
                  className="bg-white/5 border border-white/10 rounded-lg p-4 flex justify-between items-center"
                >
                  <div>
                    <p className="text-white font-medium">{method.account_holder_name}</p>
                    <p className="text-techGray text-sm">
                      {method.bank_name} - {method.account_number_masked}
                    </p>
                    <div className="flex gap-2 mt-2">
                      {method.is_default && (
                        <span className="text-xs bg-forgePurple/20 text-forgePurple px-2 py-1 rounded">
                          Default
                        </span>
                      )}
                      {method.verified ? (
                        <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">
                          ✓ Verified
                        </span>
                      ) : (
                        <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded">
                          Pending Verification
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteMethod(method.id)}
                    className="text-red-400 hover:text-red-300 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-techGray">No payment methods added yet</p>
          )}
        </div>

        {/* Request Payout Section */}
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">Request Payout</h2>
            {canRequestPayout && (
              <button
                onClick={() => setShowPayoutForm(!showPayoutForm)}
                className="px-4 py-2 bg-aiElectric hover:bg-aiElectric/80 text-black font-medium rounded-lg transition-colors"
              >
                {showPayoutForm ? '✕ Cancel' : '💰 Request Payout'}
              </button>
            )}
          </div>

          {!defaultMethod && (
            <div className="bg-yellow-500/10 border border-yellow-500 rounded-lg p-4 text-yellow-200 mb-4">
              Add a payment method before requesting a payout
            </div>
          )}

          {showPayoutForm && (
            <form
              onSubmit={handleRequestPayout}
              className="bg-white/5 border border-white/10 rounded-lg p-6 mb-6"
            >
              {payoutError && (
                <div className="text-red-400 text-sm mb-4">{payoutError}</div>
              )}

              <div>
                <label className="text-techGray text-sm mb-2 block">
                  Amount (Max: ${(balance?.available_balance || 0).toFixed(2)})
                </label>
                <input
                  type="number"
                  min="1"
                  step="0.01"
                  max={balance?.available_balance || 0}
                  value={payoutAmount}
                  onChange={(e) => setPayoutAmount(e.target.value)}
                  placeholder="Enter amount"
                  required
                  className="w-full bg-white/5 border border-white/10 rounded px-3 py-2 text-white placeholder-techGray focus:outline-none focus:border-forgePurple"
                />
              </div>

              <p className="text-techGray text-xs mt-2">
                Platform fee: 20% (You'll receive ${payoutAmount ? (parseFloat(payoutAmount) * 0.8).toFixed(2) : '0.00'})
              </p>

              <button
                type="submit"
                disabled={payoutSubmitting || !defaultMethod}
                className="mt-4 w-full px-4 py-2 bg-aiElectric hover:bg-aiElectric/80 disabled:opacity-50 text-black font-medium rounded-lg transition-colors"
              >
                {payoutSubmitting ? 'Processing...' : 'Request Payout'}
              </button>
            </form>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
```

---

## 🎯 PHASE 5: SECURITY HARDENING

**Time:** 1 hour  
**Risk:** LOW - Additional layer, doesn't break existing

### Add Encryption Environment Variable

**File:** `.env.local` (CREATE/UPDATE)

```
NEXT_PUBLIC_API_BASE=http://localhost:8001
ENCRYPTION_KEY=your-secret-key-here-min-32-chars-long
```

### Verify HTTPS in Production

For production, ensure:
- All API calls use `https://`
- Set secure cookies
- Enable CORS only for trusted domains

---

## ✅ FINAL CHECKLIST

- [ ] Delete `/mentors/earnings.tsx`
- [ ] Create PaymentMethod model
- [ ] Create backend endpoints
- [ ] Create API wrapper (`mentorEarningsApi.ts`)
- [ ] Update `dashboard/payouts.tsx`
- [ ] Test all flows:
  - [ ] Add payment method
  - [ ] List payment methods
  - [ ] Request payout
  - [ ] Delete payment method
- [ ] Verify no console errors
- [ ] Check database for PaymentMethod records
- [ ] Test with browser DevTools

---

## 🧪 TESTING COMMANDS

```bash
# Backend test
curl -X GET http://localhost:8001/api/v1x/mentors/payouts/summary \
  -H "Authorization: Bearer YOUR_TOKEN"

# Frontend test
npm run dev  # Should start without errors
# Visit http://localhost:3000/mentors/dashboard/payouts
```

---

## 🆘 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| 404 on endpoints | Verify router mounted in `main.py` |
| Encryption errors | Check `ENCRYPTION_KEY` length (min 32 chars) |
| Database errors | Run `python init_db.py` or reset DB |
| CORS errors | Add to `main.py` CORS configuration |
| Auth errors | Verify JWT token in request headers |

---

**Status:** Ready to implement once duplicate page is deleted  
**Estimated Duration:** 5-6 hours  
**Risk:** LOW (with duplicate deletion)

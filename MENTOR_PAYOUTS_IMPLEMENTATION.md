# Mentor Payouts & Withdrawals - Complete Implementation Guide

## 🎯 Overview

This guide explains how to implement the complete payout system so mentors can withdraw their earnings.

---

## 💰 PART 1: BACKEND PAYOUT ENDPOINTS

### Endpoint 1: Get Available Balance
```
GET /api/v1x/mentors/balance
Response:
{
  "available_balance": 5000.00,
  "pending_payouts": 200.00,
  "total_earned": 5200.00,
  "last_payout": "2025-12-25",
  "next_payout_eligible_date": "2026-01-01"
}
```

### Endpoint 2: Get Payout History
```
GET /api/v1x/mentors/payouts?limit=50&offset=0
Response:
{
  "payouts": [
    {
      "id": 1,
      "mentor_id": 5,
      "amount": 500.00,
      "status": "completed",  // pending, processing, completed, failed
      "requested_at": "2025-12-25T10:00:00",
      "completed_at": "2025-12-26T15:30:00",
      "bank_account_last4": "1234",
      "failure_reason": null,
      "notes": "Monthly payout"
    }
  ],
  "total": 12
}
```

### Endpoint 3: Request Withdrawal
```
POST /api/v1x/mentors/payouts/request
Request Body:
{
  "amount": 500.00,
  "payment_method": "bank_transfer",  // or "stripe"
  "notes": "Monthly withdrawal"
}

Response:
{
  "payout_id": 5,
  "status": "pending",
  "amount": 500.00,
  "estimated_completion": "2025-12-26",
  "message": "Payout request submitted. We'll review and process within 24 hours."
}
```

### Endpoint 4: List Bank Accounts
```
GET /api/v1x/mentors/payment-methods
Response:
{
  "accounts": [
    {
      "id": 1,
      "type": "bank_account",
      "account_holder": "John Doe",
      "account_number": "****1234",
      "routing_number": "****5678",
      "bank_name": "Chase Bank",
      "country": "US",
      "is_default": true,
      "verified": true,
      "created_at": "2025-12-20"
    }
  ]
}
```

### Endpoint 5: Add Bank Account
```
POST /api/v1x/mentors/payment-methods
Request Body:
{
  "account_holder_name": "John Doe",
  "account_number": "1234567890",
  "routing_number": "021000021",
  "account_type": "checking",  // or "savings"
  "country": "US",
  "is_default": true
}

Response:
{
  "id": 2,
  "status": "pending_verification",
  "account_holder_name": "John Doe",
  "account_number": "****7890",
  "message": "Bank account added. Please verify with the test deposits we'll send."
}
```

### Endpoint 6: Verify Bank Account (Micro-deposits)
```
POST /api/v1x/mentors/payment-methods/{id}/verify
Request Body:
{
  "deposit1": 0.05,  // First micro-deposit amount
  "deposit2": 0.13   // Second micro-deposit amount
}

Response:
{
  "id": 2,
  "status": "verified",
  "message": "Bank account verified successfully!"
}
```

---

## 🔧 PART 2: BACKEND IMPLEMENTATION

### File: `backend/app/api/v1x/payouts.py` (NEW)

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.mentor import Mentor, MentorSession, SessionStatus
from app.schemas.mentor import Payout Schema, PayoutRequestSchema  # Create these

router = APIRouter(prefix="/mentors", tags=["mentors-payouts"])

@router.get("/balance")
def get_mentor_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mentor's available balance and earning summary."""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    # Calculate available balance (completed sessions only)
    completed_total = db.query(func.sum(MentorSession.price)).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED
        )
    ).scalar() or Decimal(0)
    
    # Calculate pending payouts
    pending_payouts = db.query(func.sum(MentorPayout.amount)).filter(
        and_(
            MentorPayout.mentor_id == mentor.id,
            MentorPayout.status == "processing"
        )
    ).scalar() or Decimal(0)
    
    available_balance = completed_total - pending_payouts
    
    # Get last payout
    last_payout = db.query(MentorPayout).filter(
        MentorPayout.mentor_id == mentor.id
    ).order_by(MentorPayout.completed_at.desc()).first()
    
    return {
        "available_balance": float(available_balance),
        "pending_payouts": float(pending_payouts),
        "total_earned": float(completed_total),
        "last_payout": last_payout.completed_at if last_payout else None,
        "next_payout_eligible_date": (last_payout.completed_at + timedelta(days=7)) if last_payout else datetime.utcnow()
    }

@router.get("/payouts")
def get_payout_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mentor's payout history."""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    query = db.query(MentorPayout).filter(MentorPayout.mentor_id == mentor.id)
    
    if status:
        query = query.filter(MentorPayout.status == status)
    
    total = query.count()
    payouts = query.order_by(MentorPayout.requested_at.desc()).limit(limit).offset(offset).all()
    
    return {
        "payouts": [
            {
                "id": p.id,
                "mentor_id": p.mentor_id,
                "amount": float(p.amount),
                "status": p.status,
                "requested_at": p.requested_at,
                "completed_at": p.completed_at,
                "bank_account_last4": p.bank_account_last4,
                "failure_reason": p.failure_reason,
                "notes": p.notes
            }
            for p in payouts
        ],
        "total": total
    }

@router.post("/payouts/request")
def request_payout(
    request: PayoutRequestSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request a payout withdrawal."""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    # Check balance
    balance_response = get_mentor_balance(current_user, db)
    available = Decimal(str(balance_response["available_balance"]))
    requested = Decimal(str(request.amount))
    
    if requested > available:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Available: ${available}"
        )
    
    # Check minimum payout amount
    if requested < Decimal("50.00"):
        raise HTTPException(
            status_code=400,
            detail="Minimum payout amount is $50"
        )
    
    # Create payout record
    payout = MentorPayout(
        mentor_id=mentor.id,
        amount=requested,
        status="pending",
        payment_method=request.payment_method,
        requested_at=datetime.utcnow(),
        notes=request.notes or ""
    )
    
    db.add(payout)
    db.commit()
    db.refresh(payout)
    
    return {
        "payout_id": payout.id,
        "status": payout.status,
        "amount": float(payout.amount),
        "estimated_completion": (datetime.utcnow() + timedelta(days=1)).date(),
        "message": "Payout request submitted. We'll review and process within 24 hours."
    }

@router.get("/payment-methods")
def get_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mentor's saved payment methods."""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    accounts = db.query(MentorPaymentMethod).filter(
        MentorPaymentMethod.mentor_id == mentor.id
    ).order_by(MentorPaymentMethod.is_default.desc()).all()
    
    return {
        "accounts": [
            {
                "id": acc.id,
                "type": acc.type,
                "account_holder": acc.account_holder_name,
                "account_number": f"****{acc.account_number[-4:]}",
                "routing_number": f"****{acc.routing_number[-4:]}",
                "bank_name": acc.bank_name,
                "country": acc.country,
                "is_default": acc.is_default,
                "verified": acc.verified,
                "created_at": acc.created_at
            }
            for acc in accounts
        ]
    }

@router.post("/payment-methods")
def add_payment_method(
    request: PaymentMethodSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new bank account for payouts."""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    # Validate bank account (simplified - in production use Plaid/Stripe)
    if len(request.account_number) < 8:
        raise HTTPException(status_code=400, detail="Invalid account number")
    
    # Create payment method
    account = MentorPaymentMethod(
        mentor_id=mentor.id,
        type="bank_account",
        account_holder_name=request.account_holder_name,
        account_number=request.account_number,
        routing_number=request.routing_number,
        account_type=request.account_type,
        bank_name="",  # Get from bank lookup in production
        country=request.country,
        is_default=request.is_default,
        verified=False,
        created_at=datetime.utcnow()
    )
    
    # Set as default if needed
    if request.is_default:
        db.query(MentorPaymentMethod).filter(
            MentorPaymentMethod.mentor_id == mentor.id
        ).update({"is_default": False})
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return {
        "id": account.id,
        "status": "pending_verification",
        "account_holder_name": account.account_holder_name,
        "account_number": f"****{account.account_number[-4:]}",
        "message": "Bank account added. Please verify with the test deposits we'll send."
    }

@router.post("/payment-methods/{account_id}/verify")
def verify_payment_method(
    account_id: int,
    request: VerifyPaymentMethodSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify bank account with micro-deposits."""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    account = db.query(MentorPaymentMethod).filter(
        and_(
            MentorPaymentMethod.id == account_id,
            MentorPaymentMethod.mentor_id == mentor.id
        )
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    # TODO: Verify micro-deposit amounts with Stripe/Plaid
    # For now, just mark as verified
    account.verified = True
    db.commit()
    db.refresh(account)
    
    return {
        "id": account.id,
        "status": "verified",
        "message": "Bank account verified successfully!"
    }
```

### Models: `backend/app/modelsx/payouts.py` (NEW)

```python
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base

class MentorPayout(Base):
    __tablename__ = "mentor_payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    payment_method = Column(String, nullable=False)  # bank_transfer, stripe
    requested_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    bank_account_last4 = Column(String, nullable=True)
    failure_reason = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    mentor = relationship("Mentor", back_populates="payouts")

class MentorPaymentMethod(Base):
    __tablename__ = "mentor_payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False, index=True)
    type = Column(String, default="bank_account")  # bank_account, stripe_account
    account_holder_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    routing_number = Column(String, nullable=False)
    account_type = Column(String)  # checking, savings
    bank_name = Column(String)
    country = Column(String, default="US")
    is_default = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    mentor = relationship("Mentor", back_populates="payment_methods")
```

---

## 🎨 PART 3: FRONTEND IMPLEMENTATION

### Create New Payout Request Component

File: `src/pages/mentors/dashboard/payouts.tsx`

```tsx
import Head from 'next/head'
import Layout from '@/components/Layout'
import AdminHeader from '@/components/AdminHeader'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'

type Balance = {
  available_balance: number
  pending_payouts: number
  total_earned: number
  last_payout: string | null
  next_payout_eligible_date: string
}

type Payout = {
  id: number
  amount: number
  status: string
  requested_at: string
  completed_at: string | null
  bank_account_last4: string
  failure_reason: string | null
  notes: string
}

type PaymentMethod = {
  id: number
  type: string
  account_holder: string
  account_number: string
  routing_number: string
  bank_name: string
  is_default: boolean
  verified: boolean
  created_at: string
}

export default function MentorPayouts() {
  const router = useRouter()
  const [balance, setBalance] = useState<Balance | null>(null)
  const [payouts, setPayouts] = useState<Payout[]>([])
  const [methods, setMethods] = useState<PaymentMethod[]>([])
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
    country: 'US',
    is_default: false
  })
  const [methodSubmitting, setMethodSubmitting] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
      
      const [balanceRes, payoutsRes, methodsRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1x/mentors/balance`, { credentials: 'include' }),
        fetch(`${API_BASE}/api/v1x/mentors/payouts`, { credentials: 'include' }),
        fetch(`${API_BASE}/api/v1x/mentors/payment-methods`, { credentials: 'include' })
      ])

      if (balanceRes.ok) {
        setBalance(await balanceRes.json())
      }
      if (payoutsRes.ok) {
        const data = await payoutsRes.json()
        setPayouts(data.payouts || [])
      }
      if (methodsRes.ok) {
        const data = await methodsRes.json()
        setMethods(data.accounts || [])
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleRequestPayout = async () => {
    if (!payoutAmount || !methods.length) {
      setPayoutError(methods.length === 0 ? 'Please add a payment method first' : 'Enter amount')
      return
    }

    setPayoutSubmitting(true)
    setPayoutError('')
    setPayoutSuccess('')

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
      const res = await fetch(`${API_BASE}/api/v1x/mentors/payouts/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(payoutAmount),
          payment_method: 'bank_transfer'
        }),
        credentials: 'include'
      })

      if (res.ok) {
        const data = await res.json()
        setPayoutSuccess(`Payout request submitted! (ID: #${data.payout_id})`)
        setPayoutAmount('')
        setShowPayoutForm(false)
        loadData() // Refresh data
      } else {
        const data = await res.json()
        setPayoutError(data.detail || 'Failed to request payout')
      }
    } catch (err: any) {
      setPayoutError(err?.message || 'Error submitting payout')
    } finally {
      setPayoutSubmitting(false)
    }
  }

  const handleAddPaymentMethod = async () => {
    setMethodSubmitting(true)
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
      const res = await fetch(`${API_BASE}/api/v1x/mentors/payment-methods`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(methodForm),
        credentials: 'include'
      })

      if (res.ok) {
        setShowMethodForm(false)
        setMethodForm({
          account_holder_name: '',
          account_number: '',
          routing_number: '',
          account_type: 'checking',
          country: 'US',
          is_default: false
        })
        loadData() // Refresh payment methods
      } else {
        alert('Failed to add payment method')
      }
    } catch (err) {
      alert('Error adding payment method')
    } finally {
      setMethodSubmitting(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-techGray">Loading payout information...</div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <Head>
        <title>Payouts & Withdrawals – Mentor Dashboard</title>
      </Head>

      <AdminHeader 
        title="Payouts & Withdrawals"
        subtitle="Manage your earnings and payment methods"
        showBackButton={true}
        backUrl="/mentors/dashboard"
      />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Balance Summary */}
        {balance && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 border border-green-500/30 rounded-xl p-6">
              <div className="text-techGray text-sm mb-2">Available Balance</div>
              <div className="text-4xl font-bold text-green-400 mb-2">
                ${balance.available_balance.toFixed(2)}
              </div>
              <div className="text-xs text-techGray">Ready to withdraw</div>
            </div>

            <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 border border-yellow-500/30 rounded-xl p-6">
              <div className="text-techGray text-sm mb-2">Pending Payouts</div>
              <div className="text-4xl font-bold text-yellow-400 mb-2">
                ${balance.pending_payouts.toFixed(2)}
              </div>
              <div className="text-xs text-techGray">Being processed</div>
            </div>

            <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-xl p-6">
              <div className="text-techGray text-sm mb-2">Total Earned</div>
              <div className="text-4xl font-bold text-blue-400 mb-2">
                ${balance.total_earned.toFixed(2)}
              </div>
              <div className="text-xs text-techGray">All time</div>
            </div>
          </div>
        )}

        {/* Payment Methods Section */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Payment Methods</h2>
            <button
              onClick={() => setShowMethodForm(!showMethodForm)}
              className="px-4 py-2 bg-forgePurple hover:bg-forgePurple/80 text-white font-medium rounded-lg transition-colors"
            >
              {showMethodForm ? '✕ Close' : '+ Add Method'}
            </button>
          </div>

          {showMethodForm && (
            <div className="bg-white/5 p-6 rounded-lg mb-6 border border-white/10">
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Account Holder Name"
                  value={methodForm.account_holder_name}
                  onChange={(e) => setMethodForm({...methodForm, account_holder_name: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                />
                <input
                  type="text"
                  placeholder="Account Number"
                  value={methodForm.account_number}
                  onChange={(e) => setMethodForm({...methodForm, account_number: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                />
                <input
                  type="text"
                  placeholder="Routing Number"
                  value={methodForm.routing_number}
                  onChange={(e) => setMethodForm({...methodForm, routing_number: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                />
                <select
                  value={methodForm.account_type}
                  onChange={(e) => setMethodForm({...methodForm, account_type: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-techBlue"
                >
                  <option value="checking">Checking</option>
                  <option value="savings">Savings</option>
                </select>
                <button
                  onClick={handleAddPaymentMethod}
                  disabled={methodSubmitting}
                  className="w-full px-4 py-2 bg-techBlue hover:bg-techBlue/80 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
                >
                  {methodSubmitting ? 'Adding...' : 'Add Payment Method'}
                </button>
              </div>
            </div>
          )}

          {methods.length === 0 ? (
            <div className="text-center py-8 text-techGray">
              <div className="text-4xl mb-3">💳</div>
              <p className="mb-4">No payment methods added yet</p>
              <button
                onClick={() => setShowMethodForm(true)}
                className="px-4 py-2 bg-techBlue text-white rounded-lg hover:bg-techBlue/80"
              >
                Add Your First Method
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {methods.map((method) => (
                <div key={method.id} className="bg-white/5 p-4 rounded-lg border border-white/10 hover:border-techBlue/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-white font-medium">{method.account_holder}</h3>
                        {method.is_default && (
                          <span className="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded">Default</span>
                        )}
                        {!method.verified && (
                          <span className="text-xs bg-yellow-600/20 text-yellow-400 px-2 py-1 rounded">Pending Verification</span>
                        )}
                      </div>
                      <div className="text-sm text-techGray">
                        {method.bank_name} - ****{method.account_number.slice(-4)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-techGray">Added {new Date(method.created_at).toLocaleDateString()}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Request Payout Section */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Request a Payout</h2>
            <button
              onClick={() => setShowPayoutForm(!showPayoutForm)}
              disabled={!balance || balance.available_balance === 0}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
            >
              {showPayoutForm ? '✕ Close' : '💰 Request Withdrawal'}
            </button>
          </div>

          {showPayoutForm && (
            <div className="bg-white/5 p-6 rounded-lg border border-white/10 mb-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-techGray mb-2">Amount ($)</label>
                  <input
                    type="number"
                    min="50"
                    step="0.01"
                    placeholder="500.00"
                    value={payoutAmount}
                    onChange={(e) => setPayoutAmount(e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-techBlue"
                  />
                  {balance && (
                    <div className="text-xs text-techGray mt-2">
                      Available: ${balance.available_balance.toFixed(2)} | Minimum: $50
                    </div>
                  )}
                </div>

                {payoutError && (
                  <div className="bg-red-500/20 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-sm">
                    {payoutError}
                  </div>
                )}

                {payoutSuccess && (
                  <div className="bg-green-500/20 border border-green-500/30 text-green-400 px-4 py-3 rounded-lg text-sm">
                    {payoutSuccess}
                  </div>
                )}

                <button
                  onClick={handleRequestPayout}
                  disabled={payoutSubmitting || !payoutAmount}
                  className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
                >
                  {payoutSubmitting ? 'Processing...' : 'Submit Payout Request'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Payout History */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Payout History</h2>

          {payouts.length === 0 ? (
            <div className="text-center py-8 text-techGray">
              <p className="text-4xl mb-3">📋</p>
              <p>No payouts yet. Request your first withdrawal above.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {payouts.map((payout) => (
                <div key={payout.id} className="bg-white/5 p-4 rounded-lg border border-white/10">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <div className="text-white font-medium">Payout #{payout.id}</div>
                      <div className="text-sm text-techGray">
                        {new Date(payout.requested_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-green-400">
                        ${payout.amount.toFixed(2)}
                      </div>
                      <span className={`text-xs px-2 py-1 rounded inline-block ${
                        payout.status === 'completed' ? 'bg-green-600/20 text-green-400'
                        : payout.status === 'processing' ? 'bg-yellow-600/20 text-yellow-400'
                        : payout.status === 'failed' ? 'bg-red-600/20 text-red-400'
                        : 'bg-blue-600/20 text-blue-400'
                      }`}>
                        {payout.status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  {payout.failure_reason && (
                    <div className="text-sm text-red-400 mt-2">Reason: {payout.failure_reason}</div>
                  )}
                  {payout.completed_at && (
                    <div className="text-sm text-techGray mt-2">
                      Completed: {new Date(payout.completed_at).toLocaleDateString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
```

---

## 📋 PART 4: IMPLEMENTATION CHECKLIST

- [ ] Create `backend/app/api/v1x/payouts.py` with endpoints
- [ ] Create `backend/app/modelsx/payouts.py` with models
- [ ] Create Payout schemas in `backend/app/schemas/`
- [ ] Update Mentor model to include relationships to payouts
- [ ] Create `src/pages/mentors/dashboard/payouts.tsx` frontend
- [ ] Add payout link to main mentor dashboard
- [ ] Update ROUTES to include `/mentors/dashboard/payouts`
- [ ] Test payout request flow
- [ ] Set up Stripe/payment processor integration
- [ ] Implement admin approval panel for payouts
- [ ] Add email notifications for payout status
- [ ] Test bank account verification

---

**Next Step**: Implement backend endpoints first, then frontend.


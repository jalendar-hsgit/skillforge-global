# Phase 2B: Seller Payout System Implementation 🎯

**Status**: Implementation in Progress  
**Version**: 1.0  
**Last Updated**: January 25, 2026

---

## Overview

Phase 2B implements complete seller payout functionality:
- **Mentor payouts** for completed sessions (80% commission)
- **Marketplace seller payouts** for product sales (80% commission)
- **Payout request system** for sellers to request earnings
- **Admin approval workflow** to process and pay sellers
- **Earnings tracking** with detailed transaction records

---

## Architecture

### Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌─────────────────┐         ┌──────────────────────────┐   │
│  │ Mentor Session  │         │ Marketplace Product Sale│   │
│  │ COMPLETED       │         │ Order COMPLETED         │   │
│  └────────┬────────┘         └────────────┬─────────────┘   │
│           │                              │                  │
│           └──────────┬───────────────────┘                  │
│                      │                                       │
│              ┌───────▼────────┐                             │
│              │ Stripe Webhook │                             │
│              │ payment_intent │                             │
│              │ .succeeded     │                             │
│              └───────┬────────┘                             │
│                      │                                       │
│         ┌────────────▼──────────────────┐                   │
│         │ Create Earning Record         │                   │
│         │ MentorEarning or              │                   │
│         │ SellerEarning (new)           │                   │
│         │                               │                   │
│         │ gross_amount: 100             │                   │
│         │ platform_fee: 20 (20%)        │                   │
│         │ net_amount: 80 (80%)          │                   │
│         └────────────┬───────────────────┘                   │
│                      │                                       │
│         ┌────────────▼───────────────────────┐              │
│         │ Seller Requests Payout             │              │
│         │ POST /seller/payouts/request       │              │
│         │ or                                 │              │
│         │ POST /mentors/payouts/request      │              │
│         └────────────┬───────────────────────┘              │
│                      │                                       │
│         ┌────────────▼───────────────────────┐              │
│         │ Admin Approves & Processes        │              │
│         │ PUT /admin/payouts/{id}/approve   │              │
│         │                                   │              │
│         │ - Validate minimum payout         │              │
│         │ - Process via Stripe/Bank/PayPal  │              │
│         │ - Update payout status            │              │
│         │ - Mark earnings as paid_out       │              │
│         │ - Send email notification         │              │
│         └────────────┬───────────────────────┘              │
│                      │                                       │
│         ┌────────────▼───────────────────────┐              │
│         │ Seller Receives Funds              │              │
│         │ Notification Email Sent            │              │
│         │ Dashboard Updated                  │              │
│         └────────────────────────────────────┘              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Commission Structure

### Mentor Sessions
```
Booking Price:           $100
Platform Commission:       $20 (20%)
Mentor Earnings:           $80 (80%)

Example:
- User books 1-hour session with Sarah Chen ($75/hr)
- Price charged to student: $75
- Platform gets: $15 (20%)
- Sarah gets: $60 (80%)
```

### Marketplace Products
```
Product Price:           $50
Platform Commission:       $10 (20%)
Seller Earnings:           $40 (80%)

Example:
- Customer buys cheat sheet template
- Price charged to customer: $50
- Platform gets: $10 (20%)
- Seller gets: $40 (80%)
```

### Courses
```
Course Price:            $99.99
Platform Commission:     $99.99 (100%)
Instructor Earnings:       $0 (0%)

Note: Courses are 100% platform revenue (different business model)
```

---

## Models

### 1. MentorEarning (existing, enhanced)

```python
class MentorEarning(Base):
    """Individual earnings from completed mentor sessions"""
    __tablename__ = "mentor_earnings"
    
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"))
    session_id = Column(Integer, ForeignKey("mentor_sessions.id"), unique=True)
    
    # Amounts
    gross_amount = Column(Float)      # What student paid
    platform_fee = Column(Float)      # 20% commission
    net_amount = Column(Float)        # 80% for mentor
    
    # Payout tracking
    payout_id = Column(Integer, ForeignKey("mentor_payouts.id"))
    is_paid_out = Column(Boolean, default=False)
    
    # Timestamps
    earned_at = Column(DateTime, default=datetime.utcnow)
    paid_out_at = Column(DateTime)
```

### 2. SellerEarning (new)

```python
class SellerEarning(Base):
    """Individual earnings from marketplace product sales"""
    __tablename__ = "seller_earnings"
    
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    product_id = Column(Integer, ForeignKey("digital_products.id"))
    
    # Amounts
    gross_amount = Column(Float)      # What customer paid
    platform_fee = Column(Float)      # 20% commission
    net_amount = Column(Float)        # 80% for seller
    
    # Payout tracking
    payout_id = Column(Integer, ForeignKey("seller_payouts.id"))
    is_paid_out = Column(Boolean, default=False)
    
    # Timestamps
    earned_at = Column(DateTime, default=datetime.utcnow)
    paid_out_at = Column(DateTime)
```

### 3. MentorPayout (existing, enhanced)

```python
class MentorPayout(Base):
    """Payout request from mentor for their earnings"""
    __tablename__ = "mentor_payouts"
    
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"))
    
    # Amounts
    amount = Column(Float)            # Requested amount
    platform_fee = Column(Float)      # Fee for payout processing
    net_amount = Column(Float)        # Amount mentor receives after fee
    
    # Status
    status = Column(Enum(PayoutStatus))  # pending, processing, completed, failed
    method = Column(Enum(PayoutMethod))  # stripe, bank_transfer, paypal
    
    # External references
    stripe_transfer_id = Column(String)   # For Stripe Connect
    paypal_transaction_id = Column(String) # For PayPal
    bank_account_last4 = Column(String)    # For bank transfer
    
    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    completed_at = Column(DateTime)
```

### 4. SellerPayout (existing, enhanced)

```python
class SellerPayout(Base):
    """Payout request from seller for their marketplace earnings"""
    __tablename__ = "seller_payouts"
    
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("users.id"))
    
    # Period
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Amounts
    total_sales = Column(Float)       # Total sales amount in period
    platform_fee = Column(Float)      # Total fees (20% of sales)
    payout_amount = Column(Float)     # Amount seller receives (80%)
    
    # Status
    status = Column(String)           # pending, processing, completed, failed
    
    # Payout details
    payout_method = Column(String)    # stripe, bank_transfer, paypal
    transaction_id = Column(String)   # External transaction reference
    
    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
```

---

## API Endpoints

### Mentor Payouts

#### 1. Get Earnings Summary
```
GET /api/v1x/mentors/payouts/earnings
Response:
{
    "total_earnings": 2450.00,        # All earned ever
    "available_balance": 850.50,      # Not yet paid out
    "pending_payouts": 0.00,          # Requested but not approved
    "completed_payouts": 1600.00,     # Already received
    "total_sessions": 32,
    "completed_sessions": 31,
    "average_session_price": 78.50,
    "platform_fee_percentage": 20.0
}
```

#### 2. Get Detailed Earnings
```
GET /api/v1x/mentors/payouts/earnings/details?skip=0&limit=20
Response:
[
    {
        "id": 1,
        "session_id": 15,
        "student_name": "John Doe",
        "topic": "Python Basics",
        "gross_amount": 75.00,
        "platform_fee": 15.00,
        "net_amount": 60.00,
        "earned_at": "2026-01-20T10:30:00Z",
        "is_paid_out": false,
        "payout_id": null
    }
]
```

#### 3. Request Payout
```
POST /api/v1x/mentors/payouts/request
Request:
{
    "amount": 500.00,
    "method": "stripe"  # stripe, bank_transfer, paypal
}

Response:
{
    "id": 42,
    "mentor_id": 5,
    "amount": 500.00,
    "platform_fee": 0.00,
    "net_amount": 500.00,
    "status": "pending",
    "method": "stripe",
    "requested_at": "2026-01-25T10:30:00Z",
    "processed_at": null,
    "completed_at": null
}
```

#### 4. Get Payout History
```
GET /api/v1x/mentors/payouts/history?status=completed&skip=0&limit=20
Response:
[
    {
        "id": 40,
        "mentor_id": 5,
        "amount": 250.00,
        "status": "completed",
        "method": "stripe",
        "stripe_transfer_id": "tr_1234567890",
        "requested_at": "2026-01-15T08:00:00Z",
        "completed_at": "2026-01-16T15:30:00Z"
    }
]
```

---

### Seller Payouts (Marketplace)

#### 1. Get Seller Earnings Summary
```
GET /api/v1x/seller/earnings
Response:
{
    "total_earnings": 1230.50,        # All earned ever
    "available_balance": 350.25,      # Not yet paid out
    "pending_payouts": 0.00,          # Requested but not approved
    "completed_payouts": 880.25,      # Already received
    "total_sales": 20,                # Products sold
    "total_revenue": 1540.00,         # Before commission
    "period_average": 77.00
}
```

#### 2. Get Seller Earnings Details
```
GET /api/v1x/seller/earnings/details?skip=0&limit=20
Response:
[
    {
        "id": 1,
        "order_id": 52,
        "product_id": 8,
        "product_name": "React Cheat Sheet",
        "gross_amount": 39.99,
        "platform_fee": 8.00,
        "net_amount": 31.99,
        "earned_at": "2026-01-22T14:20:00Z",
        "is_paid_out": false,
        "payout_id": null
    }
]
```

#### 3. Request Marketplace Payout
```
POST /api/v1x/seller/payouts/request
Request:
{
    "amount": 300.00,
    "method": "stripe"
}

Response:
{
    "id": 15,
    "seller_id": 3,
    "amount": 300.00,
    "status": "pending",
    "method": "stripe",
    "requested_at": "2026-01-25T10:30:00Z",
    "processed_at": null,
    "completed_at": null
}
```

#### 4. Get Seller Payout History
```
GET /api/v1x/seller/payouts/history?status=completed&skip=0&limit=20
Response:
[
    {
        "id": 13,
        "seller_id": 3,
        "amount": 200.00,
        "status": "completed",
        "method": "stripe",
        "transaction_id": "tr_0987654321",
        "requested_at": "2026-01-20T09:00:00Z",
        "completed_at": "2026-01-21T16:45:00Z"
    }
]
```

---

### Admin Payout Management

#### 1. List All Pending Payouts
```
GET /api/v1x/admin/payouts?status=pending&skip=0&limit=50
Response:
[
    {
        "id": 42,
        "user_id": 5,
        "user_name": "Sarah Chen",
        "user_type": "mentor",  # mentor, seller
        "amount": 500.00,
        "method": "stripe",
        "status": "pending",
        "requested_at": "2026-01-25T10:30:00Z"
    }
]
```

#### 2. Get Payout Details
```
GET /api/v1x/admin/payouts/{payout_id}
Response:
{
    "id": 42,
    "user_id": 5,
    "user_name": "Sarah Chen",
    "user_email": "sarah@example.com",
    "user_type": "mentor",
    "amount": 500.00,
    "method": "stripe",
    "status": "pending",
    "stripe_transfer_id": null,
    "requested_at": "2026-01-25T10:30:00Z",
    "earnings_breakdown": [
        {
            "session_id": 120,
            "student": "John Doe",
            "amount": 80.00,
            "earned_at": "2026-01-24T15:00:00Z"
        }
    ]
}
```

#### 3. Approve & Process Payout
```
PUT /api/v1x/admin/payouts/{payout_id}/approve
Request:
{
    "notes": "Approved - verified account"
}

Response:
{
    "id": 42,
    "user_id": 5,
    "amount": 500.00,
    "status": "processing",
    "stripe_transfer_id": "tr_1234567890",
    "processed_at": "2026-01-25T11:00:00Z",
    "message": "Payout approved and processing"
}

Actions triggered:
- ✅ Status changed: pending → processing
- ✅ Stripe transfer initiated (if using Stripe)
- ✅ Earnings marked as is_paid_out=true
- ✅ Email sent to seller with payout details
```

#### 4. Reject Payout
```
PUT /api/v1x/admin/payouts/{payout_id}/reject
Request:
{
    "reason": "Insufficient account verification"
}

Response:
{
    "id": 42,
    "status": "rejected",
    "failure_reason": "Insufficient account verification",
    "message": "Payout rejected - reason sent to user"
}

Actions triggered:
- ✅ Status changed: pending → rejected
- ✅ Email sent to seller with rejection reason
- ✅ Earnings remain available for next payout request
```

#### 5. Retry Failed Payout
```
POST /api/v1x/admin/payouts/{payout_id}/retry
Response:
{
    "id": 42,
    "status": "processing",
    "stripe_transfer_id": "tr_9876543210",
    "message": "Payout retry initiated"
}
```

---

## Implementation Steps

### Step 1: Create SellerEarning Model

**File**: `backend/app/modelsx/marketplace.py` (add new model)

```python
class SellerEarning(Base):
    """Individual earnings from marketplace product sales"""
    __tablename__ = "seller_earnings"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    product_id = Column(Integer, ForeignKey("digital_products.id", ondelete="CASCADE"), nullable=False)
    
    # Amounts
    gross_amount = Column(Float, nullable=False)  # What customer paid
    platform_fee = Column(Float, default=0.0)     # 20% commission
    net_amount = Column(Float, nullable=False)    # 80% for seller
    
    # Payout tracking
    payout_id = Column(Integer, ForeignKey("seller_payouts.id", ondelete="SET NULL"), nullable=True, index=True)
    is_paid_out = Column(Boolean, default=False)
    
    # Timestamps
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    paid_out_at = Column(DateTime, nullable=True)
    
    # Relationships
    seller = relationship("User", foreign_keys=[seller_id], backref="seller_earnings")
    order = relationship("Order", backref="earning")
    product = relationship("DigitalProduct", backref="earnings")
    payout = relationship("SellerPayout", backref="earnings")
    
    def __repr__(self):
        return f"<SellerEarning(id={self.id}, seller_id={self.seller_id}, net_amount={self.net_amount})>"
```

---

### Step 2: Enhance Stripe Webhook to Create Earning Records

**File**: `backend/app/api/v1x/stripe_webhook.py`

Modify `payment_intent.succeeded` handler:

```python
# Determine order type and create earning record
order = db.query(Order).filter(Order.id == order_id).first()

if order.course_id:
    # Course order - 100% to platform
    pass  # No earning record for courses
elif order.digital_product_id:
    # Marketplace order - create SellerEarning
    product = db.query(DigitalProduct).filter(
        DigitalProduct.id == order.digital_product_id
    ).first()
    
    gross_amount = order.amount / 100  # Convert from cents
    platform_fee = gross_amount * 0.20  # 20% commission
    net_amount = gross_amount * 0.80    # 80% to seller
    
    earning = SellerEarning(
        seller_id=product.seller_id,
        order_id=order.id,
        product_id=product.id,
        gross_amount=gross_amount,
        platform_fee=platform_fee,
        net_amount=net_amount,
        earned_at=datetime.utcnow()
    )
    db.add(earning)
    db.commit()
    
    # Send email
    await email_service.send_marketplace_order_confirmation(...)
```

---

### Step 3: Create Seller Payouts Endpoints

**File**: `backend/app/api/v1x/seller.py` (add new endpoints)

```python
# 1. Get earnings summary
@router.get("/earnings")
def get_seller_earnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get seller's earnings summary"""
    earnings = db.query(SellerEarning).filter(
        SellerEarning.seller_id == current_user.id
    ).all()
    
    total_earnings = sum(e.net_amount for e in earnings)
    paid_out = sum(e.net_amount for e in earnings if e.is_paid_out)
    available = total_earnings - paid_out
    
    return {
        "total_earnings": total_earnings,
        "available_balance": available,
        "completed_payouts": paid_out,
        "total_sales": len(earnings),
        "total_revenue": sum(e.gross_amount for e in earnings)
    }

# 2. Get earning details
@router.get("/earnings/details")
def get_seller_earnings_details(
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed earning records"""
    earnings = db.query(SellerEarning).filter(
        SellerEarning.seller_id == current_user.id
    ).order_by(desc(SellerEarning.earned_at)).offset(skip).limit(limit).all()
    
    return earnings

# 3. Request payout
@router.post("/payouts/request")
def request_payout(
    request: PayoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request payout for available earnings"""
    # Get available earnings
    available_earnings = db.query(SellerEarning).filter(
        and_(
            SellerEarning.seller_id == current_user.id,
            SellerEarning.is_paid_out == False
        )
    ).all()
    
    available_amount = sum(e.net_amount for e in available_earnings)
    
    if request.amount > available_amount:
        raise HTTPException(status_code=400, detail="Insufficient available balance")
    
    if request.amount < 10.0:  # Minimum $10
        raise HTTPException(status_code=400, detail="Minimum payout is $10")
    
    # Create payout request
    payout = SellerPayout(
        seller_id=current_user.id,
        amount=request.amount,
        status="pending",
        payout_method=request.method,
        requested_at=datetime.utcnow()
    )
    db.add(payout)
    db.commit()
    
    return payout

# 4. Get payout history
@router.get("/payouts/history")
def get_payout_history(
    status: Optional[str] = None,
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get seller's payout history"""
    query = db.query(SellerPayout).filter(
        SellerPayout.seller_id == current_user.id
    )
    
    if status:
        query = query.filter(SellerPayout.status == status)
    
    payouts = query.order_by(desc(SellerPayout.requested_at)).offset(skip).limit(limit).all()
    
    return payouts
```

---

### Step 4: Enhance Admin Payouts for Both Types

**File**: `backend/app/api/v1x/admin_payouts.py` (enhance existing)

```python
@router.get("/payouts")
def list_all_payouts(
    status: Optional[str] = None,
    user_type: Optional[str] = None,  # mentor, seller
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all pending payouts (mentors + sellers)"""
    
    # Get mentor payouts
    mentor_payouts = db.query(MentorPayout).all()
    mentor_payouts_data = []
    for mp in mentor_payouts:
        mentor_user = db.query(User).join(
            Mentor, User.id == Mentor.user_id
        ).filter(Mentor.id == mp.mentor_id).first()
        
        if status and mp.status != status:
            continue
        
        mentor_payouts_data.append({
            "id": mp.id,
            "user_id": mentor_user.id if mentor_user else None,
            "user_name": mentor_user.name if mentor_user else "Unknown",
            "user_type": "mentor",
            "amount": mp.amount,
            "method": mp.method,
            "status": mp.status,
            "requested_at": mp.requested_at
        })
    
    # Get seller payouts
    seller_payouts = db.query(SellerPayout).all()
    seller_payouts_data = []
    for sp in seller_payouts:
        seller_user = db.query(User).filter(User.id == sp.seller_id).first()
        
        if status and sp.status != status:
            continue
        
        seller_payouts_data.append({
            "id": sp.id,
            "user_id": sp.seller_id,
            "user_name": seller_user.name if seller_user else "Unknown",
            "user_type": "seller",
            "amount": sp.amount,
            "method": sp.payout_method,
            "status": sp.status,
            "requested_at": sp.requested_at
        })
    
    # Combine and filter
    all_payouts = mentor_payouts_data + seller_payouts_data
    
    if user_type:
        all_payouts = [p for p in all_payouts if p["user_type"] == user_type]
    
    # Sort by requested_at desc
    all_payouts.sort(key=lambda x: x["requested_at"], reverse=True)
    
    # Paginate
    total = len(all_payouts)
    all_payouts = all_payouts[skip:skip + limit]
    
    return {"total": total, "payouts": all_payouts}

@router.put("/payouts/{payout_id}/approve")
async def approve_payout(
    payout_id: int,
    request: PayoutApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve and process payout request"""
    
    # Try mentor payout first
    mentor_payout = db.query(MentorPayout).filter(MentorPayout.id == payout_id).first()
    
    if mentor_payout:
        # Process mentor payout
        mentor_payout.status = "processing"
        mentor_payout.processed_at = datetime.utcnow()
        
        # Mark earnings as paid out
        earnings = db.query(MentorEarning).filter(
            MentorEarning.mentor_id == mentor_payout.mentor_id,
            MentorEarning.is_paid_out == False
        ).all()
        
        amount_to_pay = 0
        for earning in earnings:
            if amount_to_pay + earning.net_amount <= mentor_payout.amount:
                earning.is_paid_out = True
                earning.payout_id = mentor_payout.id
                earning.paid_out_at = datetime.utcnow()
                amount_to_pay += earning.net_amount
        
        # Process with Stripe Connect or other method
        # ... (implement based on mentor_payout.method)
        
        # Send email
        mentor_user = db.query(User).join(
            Mentor, User.id == Mentor.user_id
        ).filter(Mentor.id == mentor_payout.mentor_id).first()
        
        if mentor_user:
            asyncio.create_task(
                email_service.send_seller_payout_notification(
                    to_email=mentor_user.email,
                    seller_name=mentor_user.name,
                    amount=mentor_payout.amount,
                    payout_date=datetime.utcnow(),
                    payout_method=mentor_payout.method.value,
                    payout_id=mentor_payout.id
                )
            )
        
        db.commit()
        return mentor_payout
    
    # Try seller payout
    seller_payout = db.query(SellerPayout).filter(SellerPayout.id == payout_id).first()
    
    if seller_payout:
        # Process seller payout
        seller_payout.status = "processing"
        seller_payout.processed_at = datetime.utcnow()
        
        # Mark earnings as paid out
        earnings = db.query(SellerEarning).filter(
            SellerEarning.seller_id == seller_payout.seller_id,
            SellerEarning.is_paid_out == False
        ).all()
        
        amount_to_pay = 0
        for earning in earnings:
            if amount_to_pay + earning.net_amount <= seller_payout.amount:
                earning.is_paid_out = True
                earning.payout_id = seller_payout.id
                earning.paid_out_at = datetime.utcnow()
                amount_to_pay += earning.net_amount
        
        # Process payout
        # ... (implement based on seller_payout.payout_method)
        
        # Send email
        seller_user = db.query(User).filter(User.id == seller_payout.seller_id).first()
        
        if seller_user:
            asyncio.create_task(
                email_service.send_seller_payout_notification(
                    to_email=seller_user.email,
                    seller_name=seller_user.name,
                    amount=seller_payout.amount,
                    payout_date=datetime.utcnow(),
                    payout_method=seller_payout.payout_method,
                    payout_id=seller_payout.id
                )
            )
        
        db.commit()
        return seller_payout
    
    raise HTTPException(status_code=404, detail="Payout not found")
```

---

## Testing Scenarios

### Scenario 1: Mentor Payout Request & Approval

```
1. Mentor completes 5 sessions
   - Session 1: $75 → Mentor: $60, Platform: $15
   - Session 2: $85 → Mentor: $68, Platform: $17
   - Session 3: $75 → Mentor: $60, Platform: $15
   - Session 4: $90 → Mentor: $72, Platform: $18
   - Session 5: $80 → Mentor: $64, Platform: $16
   
   Total Available: $324 (80% of $405)

2. Mentor requests $300 payout
   - POST /api/v1x/mentors/payouts/request
   - Request: {"amount": 300, "method": "stripe"}
   - Response: Payout ID 42, status: pending

3. Admin approves payout
   - PUT /api/v1x/admin/payouts/42/approve
   - Status changes: pending → processing
   - Earnings marked as is_paid_out=true
   - Email sent to mentor

4. Mentor receives email
   - "Your payout of $300 has been approved"
   - "Payment method: Stripe"
   - "You should see funds in 1-2 business days"
```

### Scenario 2: Marketplace Seller Payout

```
1. Seller's products sold
   - Sale 1: Cheat Sheet $39.99 → Seller: $31.99, Platform: $8
   - Sale 2: Template $49.99 → Seller: $39.99, Platform: $10
   - Sale 3: Guide $29.99 → Seller: $23.99, Platform: $6
   
   Total Available: $95.97

2. Seller requests $95 payout
   - POST /api/v1x/seller/payouts/request
   - Request: {"amount": 95, "method": "stripe"}
   - Response: Payout ID 15, status: pending

3. Admin approves payout
   - PUT /api/v1x/admin/payouts/15/approve
   - Seller earnings marked as paid
   - Email notification sent

4. Dashboard Updates
   - Available balance: $95.97 → $0.97
   - Total completed payouts: $0 → $95
```

### Scenario 3: Admin Rejects Payout

```
1. Seller requests $500 payout
   - Available balance: $150
   - Request exceeds available

2. Admin approves anyway (with notes)
   - Error: "Insufficient available balance"
   - Reject the request
   
3. Alternative: Seller requests $150 payout
   - Gets processed successfully
```

---

## Integration with Phase 2A

Phase 2A (Email Receipts) + Phase 2B (Payouts) work together:

```
┌─────────────────────────────────────┐
│ Phase 2A: Email Receipts            │
│ ┌───────────────────────────────┐   │
│ │ Course Order Confirmation     │   │
│ │ Marketplace Order Confirmation│   │  Sends emails to customers
│ │ Payout Notifications          │   │  and sellers
│ └───────────────────────────────┘   │
└─────────────────────────────────────┘
              ↓ ↓ ↓
┌─────────────────────────────────────┐
│ Stripe Webhook Processes Payment    │
│ - Creates Order                     │
│ - Creates MentorEarning or          │
│   SellerEarning                     │
│ - Sends confirmation emails (2A)    │
└─────────────────────────────────────┘
              ↓ ↓ ↓
┌─────────────────────────────────────┐
│ Phase 2B: Seller Payouts            │
│ ┌───────────────────────────────┐   │
│ │ Seller Requests Payout        │   │
│ │ Admin Approves Payment        │   │  Creates payout records
│ │ Funds Transferred             │   │  Sends payout emails
│ │ Dashboard Updated             │   │
│ └───────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Database Changes Required

### New Migration (SQLite auto-creates, no migration needed)

Tables to be created automatically:
1. `seller_earnings` - New table for marketplace earnings
2. Tables already exist:
   - `mentor_earnings` - Enhanced with relationships
   - `mentor_payouts` - Enhanced
   - `seller_payouts` - Enhanced

### Indexes to add

```sql
CREATE INDEX idx_seller_earnings_seller ON seller_earnings(seller_id);
CREATE INDEX idx_seller_earnings_paid ON seller_earnings(is_paid_out);
CREATE INDEX idx_mentor_earnings_paid ON mentor_earnings(is_paid_out);
```

---

## Minimum Payout Amounts

```
Mentor: $10.00
Seller: $10.00
```

These prevent too many small payouts and reduce fees.

---

## Error Handling

### Common Errors

1. **Insufficient Available Balance**
   ```
   Status: 400
   Detail: "Insufficient available balance for requested amount"
   ```

2. **Minimum Payout Not Met**
   ```
   Status: 400
   Detail: "Minimum payout amount is $10.00"
   ```

3. **Payout Not Found**
   ```
   Status: 404
   Detail: "Payout request not found"
   ```

4. **Processing Error**
   ```
   Status: 500
   Detail: "Error processing payout - please try again"
   ```

---

## Completion Checklist

### Models
- [ ] SellerEarning model created in marketplace.py
- [ ] MentorEarning verified complete
- [ ] MentorPayout verified complete
- [ ] SellerPayout verified complete

### Webhooks
- [ ] Stripe webhook creates SellerEarning records
- [ ] Stripe webhook creates MentorEarning records
- [ ] Commission calculations correct (80/20 split)

### Seller Endpoints
- [ ] GET /seller/earnings (summary)
- [ ] GET /seller/earnings/details (detailed)
- [ ] POST /seller/payouts/request (request payout)
- [ ] GET /seller/payouts/history (history)

### Mentor Endpoints
- [ ] GET /mentors/payouts/earnings (summary)
- [ ] GET /mentors/payouts/earnings/details (detailed)
- [ ] POST /mentors/payouts/request (request payout)
- [ ] GET /mentors/payouts/history (history)

### Admin Endpoints
- [ ] GET /admin/payouts (list all)
- [ ] GET /admin/payouts/{id} (details)
- [ ] PUT /admin/payouts/{id}/approve (approve)
- [ ] PUT /admin/payouts/{id}/reject (reject)
- [ ] POST /admin/payouts/{id}/retry (retry)

### Emails
- [ ] Payout approval email sent
- [ ] Payout rejection email sent
- [ ] Payout processing notifications

### Testing
- [ ] Mentor payout flow tested
- [ ] Seller payout flow tested
- [ ] Admin approval tested
- [ ] Email notifications verified
- [ ] Database records created correctly

---

## Next Phase (Phase 2C)

Phase 2C will add:
- **Subscriptions** - Recurring billing for premium features
- **Usage tracking** - Track API calls, mentor hours, storage
- **Tiered pricing** - Different subscription tiers with features
- **Renewal management** - Automatic subscription renewals
- **Cancellation** - User-initiated subscription cancellation

---

## Summary

Phase 2B provides complete seller and mentor payout functionality:
- ✅ Earnings tracking (commission split)
- ✅ Payout requests from sellers
- ✅ Admin approval workflow
- ✅ Stripe/PayPal/Bank transfer support
- ✅ Email notifications
- ✅ Dashboard integration

Total implementation time: ~4-5 hours  
Testing time: ~2-3 hours  
Deployment time: 30 minutes


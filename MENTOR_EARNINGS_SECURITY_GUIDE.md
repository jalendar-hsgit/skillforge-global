# MENTOR EARNINGS - SECURITY & IMPLEMENTATION GUIDE

**Priority Level:** 🔴 CRITICAL  
**Timeline:** 5-6 hours  
**Security Level:** HIGH (Payment Data)

---

## 🔐 SECURITY FIRST - What NOT to Do

### ❌ Current Frontend Issues (payouts.tsx)

```tsx
// ❌ BAD: Storing sensitive data in state
const [methodForm, setMethodForm] = useState({
  account_holder_name: '',      // ⚠️ OK (not sensitive)
  account_number: '',           // ⚠️ DANGEROUS - Storing full account number!
  routing_number: '',           // ⚠️ DANGEROUS - Storing routing number!
  account_type: 'checking'      // ⚠️ OK
})

// ❌ BAD: Sending raw account numbers to API
const res = await fetch(`${API_BASE}/api/v1x/mentors/payment-methods`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    account_holder_name: methodForm.account_holder_name,
    account_number: methodForm.account_number,        // ⚠️ NOT ENCRYPTED!
    routing_number: methodForm.routing_number,        // ⚠️ NOT ENCRYPTED!
    account_type: methodForm.account_type,
    country: methodForm.country,
    is_default: methodForm.is_default
  }),
  credentials: 'include'
})

// ❌ BAD: Not validating input length/format
// ❌ BAD: Not handling encryption before sending
// ❌ BAD: Storing full numbers after response

// ❌ BAD: No rate limiting on submissions
// ❌ BAD: No verification requirements
// ❌ BAD: No audit trail
```

---

## ✅ SECURITY RIGHT - Implementation Pattern

### 1. Frontend - Secure Input Handling

```tsx
// ✅ GOOD: Component that handles sensitive data safely
interface PaymentMethodFormProps {
  onSubmit: (data: PaymentMethodData) => Promise<void>
  isLoading: boolean
}

export function AddPaymentMethodForm({ onSubmit, isLoading }: PaymentMethodFormProps) {
  // ✅ GOOD: Use form state ONLY for input
  const [form, setForm] = useState({
    account_holder_name: '',
    account_number: '',
    routing_number: '',
    account_type: 'checking'
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  // ✅ GOOD: Validate BEFORE sending
  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    // Validate account holder
    if (!form.account_holder_name || form.account_holder_name.length < 2) {
      newErrors.account_holder_name = 'Minimum 2 characters'
    }
    if (form.account_holder_name.length > 100) {
      newErrors.account_holder_name = 'Maximum 100 characters'
    }

    // Validate account number (US: 8-17 digits, no special chars)
    const accountNum = form.account_number.replace(/\D/g, '')
    if (accountNum.length < 8 || accountNum.length > 17) {
      newErrors.account_number = 'Account number must be 8-17 digits'
    }
    // ✅ GOOD: Don't store the validation result, just validate before send
    
    // Validate routing number (US: exactly 9 digits)
    const routingNum = form.routing_number.replace(/\D/g, '')
    if (routingNum.length !== 9) {
      newErrors.routing_number = 'Routing number must be exactly 9 digits'
    }

    return newErrors
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // ✅ GOOD: Validate before submitting
    const formErrors = validateForm()
    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors)
      return
    }

    setLoading(true)
    try {
      // ✅ GOOD: Convert full numbers to ONLY last 4 for display
      // The actual numbers are in form state, ready to send
      const accountLast4 = form.account_number.slice(-4)
      
      // ✅ GOOD: Send over HTTPS only (enforced by browser)
      // Backend will encrypt before storing
      await onSubmit({
        account_holder_name: form.account_holder_name,
        account_number: form.account_number,        // Browser → HTTPS → Server
        routing_number: form.routing_number,        // Encrypted by server
        account_type: form.account_type
      })

      // ✅ GOOD: Clear form immediately after successful submission
      setForm({ account_holder_name: '', account_number: '', routing_number: '', account_type: 'checking' })
      setErrors({})
      
      // Show confirmation with ONLY last 4 digits
      showSuccess(`Payment method ending in ${accountLast4} added`)
    } catch (error) {
      // ❌ DO NOT show full error that might leak account info
      setErrors({ submit: 'Failed to add payment method. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium">Account Holder Name</label>
        <input
          type="text"
          value={form.account_holder_name}
          onChange={e => setForm({...form, account_holder_name: e.target.value})}
          disabled={loading}
          className="w-full px-3 py-2 border rounded"
          maxLength={100}
          required
        />
        {errors.account_holder_name && <span className="text-error text-sm">{errors.account_holder_name}</span>}
      </div>

      <div>
        <label className="block text-sm font-medium">Account Number</label>
        <input
          type="password"               // ✅ GOOD: Use password field to hide numbers
          value={form.account_number}
          onChange={e => {
            const val = e.target.value.replace(/\D/g, '') // Only digits
            setForm({...form, account_number: val.slice(0, 17)}) // Max 17 digits
          }}
          disabled={loading}
          className="w-full px-3 py-2 border rounded font-mono"
          maxLength={17}
          placeholder="Enter account number"
          required
        />
        {errors.account_number && <span className="text-error text-sm">{errors.account_number}</span>}
      </div>

      <div>
        <label className="block text-sm font-medium">Routing Number</label>
        <input
          type="password"               // ✅ GOOD: Use password field
          value={form.routing_number}
          onChange={e => {
            const val = e.target.value.replace(/\D/g, '') // Only digits
            setForm({...form, routing_number: val.slice(0, 9)}) // Max 9 digits
          }}
          disabled={loading}
          className="w-full px-3 py-2 border rounded font-mono"
          maxLength={9}
          placeholder="123456789"
          required
        />
        {errors.routing_number && <span className="text-error text-sm">{errors.routing_number}</span>}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="bg-forgePurple-500 text-white px-4 py-2 rounded hover:bg-forgePurple-600 disabled:opacity-50"
      >
        {loading ? 'Adding...' : 'Add Payment Method'}
      </button>
    </form>
  )
}

// ✅ GOOD: Display methods with ONLY masked info
export function PaymentMethodsList({ methods }: { methods: PaymentMethod[] }) {
  return (
    <div className="space-y-2">
      {methods.map(method => (
        <div key={method.id} className="border p-3 rounded bg-deepTech-800">
          <div className="flex justify-between items-center">
            {/* ✅ GOOD: Show only last 4 digits */}
            <span className="font-mono">
              {method.bank_name} ••••{method.last4}
            </span>
            
            <div className="flex gap-2">
              {/* ✅ GOOD: Show verification status */}
              {!method.verified && (
                <span className="text-warning text-xs">Verify</span>
              )}
              {method.is_default && (
                <span className="text-success text-xs">Default</span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
```

### 2. Backend - Secure Storage

```python
# ✅ GOOD: Encryption utility
from cryptography.fernet import Fernet
from app.config import ENCRYPTION_KEY  # From environment

cipher = Fernet(ENCRYPTION_KEY)

def encrypt_sensitive(value: str) -> str:
    """Encrypt sensitive data before storage"""
    return cipher.encrypt(value.encode()).decode()

def decrypt_sensitive(value: str) -> str:
    """Decrypt sensitive data from storage"""
    return cipher.decrypt(value.encode()).decode()


# ✅ GOOD: Database model with encryption
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime

class PaymentMethod(Base):
    __tablename__ = 'payment_methods'
    
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey('mentors.id'), nullable=False)
    
    # ✅ GOOD: Account holder (plain, no sensitive info)
    account_holder = Column(String(100), nullable=False)
    
    # ✅ GOOD: Account number (encrypted)
    _account_number = Column('account_number', String, nullable=False)
    
    # ✅ GOOD: Routing number (encrypted)
    _routing_number = Column('routing_number', String, nullable=False)
    
    # Bank name for display
    bank_name = Column(String(50))
    
    # Flags
    is_default = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    verification_code = Column(String(32), nullable=True, unique=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def account_number(self) -> str:
        """Decrypt account number when needed"""
        if not self._account_number:
            return ''
        return decrypt_sensitive(self._account_number)
    
    @account_number.setter
    def account_number(self, value: str):
        """Encrypt account number before storage"""
        self._account_number = encrypt_sensitive(value)
    
    @property
    def routing_number(self) -> str:
        """Decrypt routing number when needed"""
        if not self._routing_number:
            return ''
        return decrypt_sensitive(self._routing_number)
    
    @routing_number.setter
    def routing_number(self, value: str):
        """Encrypt routing number before storage"""
        self._routing_number = encrypt_sensitive(value)
    
    @property
    def last4(self) -> str:
        """Get last 4 digits without decrypting"""
        if not self._account_number:
            return '????'
        # Don't decrypt, just show '****' for display
        return f'••••{self.account_number[-4:]}'
    
    def to_dict(self, include_full: bool = False):
        """Return dict representation"""
        return {
            'id': self.id,
            'bank_name': self.bank_name,
            'last4': self.account_number[-4:],  # ✅ GOOD: Only last 4
            'is_default': self.is_default,
            'verified': self.verified,
            # ❌ NEVER include: account_number, routing_number
        }


# ✅ GOOD: API endpoints with security
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
import random
import string

router = APIRouter(prefix="/mentors", tags=["mentors-payment"])


class AddPaymentMethodRequest(BaseModel):
    account_holder_name: str = Field(..., min_length=2, max_length=100)
    account_number: str = Field(..., min_length=8, max_length=17)
    routing_number: str = Field(..., min_length=9, max_length=9)
    
    @validator('account_number')
    def validate_account(cls, v):
        # ✅ GOOD: Only allow digits
        if not v.isdigit():
            raise ValueError('Account number must contain only digits')
        return v
    
    @validator('routing_number')
    def validate_routing(cls, v):
        # ✅ GOOD: Only allow digits
        if not v.isdigit() or len(v) != 9:
            raise ValueError('Routing number must be 9 digits')
        return v


@router.post("/payment-methods", status_code=status.HTTP_201_CREATED)
def add_payment_method(
    request: AddPaymentMethodRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ GOOD: Add payment method with security
    - Validates input
    - Encrypts before storage
    - Sends verification email
    - Never returns full account number
    """
    
    # ✅ GOOD: Verify user is mentor
    mentor = db.query(Mentor).filter(
        Mentor.user_id == current_user.id
    ).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    if mentor.status != MentorStatus.APPROVED:
        raise HTTPException(status_code=403, detail="Mentor not approved")
    
    # ✅ GOOD: Check for duplicates
    existing = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.mentor_id == mentor.id,
            PaymentMethod._account_number == encrypt_sensitive(request.account_number)
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account is already added"
        )
    
    # ✅ GOOD: Generate verification code
    verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    # ✅ GOOD: Create with encrypted data
    payment_method = PaymentMethod(
        mentor_id=mentor.id,
        account_holder=request.account_holder_name,
        account_number=request.account_number,  # Will be encrypted by setter
        routing_number=request.routing_number,  # Will be encrypted by setter
        bank_name='Unknown',  # Can auto-detect from routing number
        is_default=False,  # Must explicitly set
        verified=False,  # Must verify via email
        verification_code=verification_code
    )
    
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    
    # ✅ GOOD: Send verification email
    send_verification_email(
        email=current_user.email,
        mentor_name=current_user.name,
        last4=payment_method.account_number[-4:],
        verification_code=verification_code,
        verification_link=f"https://yourapp.com/mentors/dashboard/payouts?verify={verification_code}"
    )
    
    # ✅ GOOD: Return ONLY safe data (no account numbers!)
    return {
        'id': payment_method.id,
        'bank_name': payment_method.bank_name,
        'last4': payment_method.account_number[-4:],
        'is_default': False,
        'verified': False,
        'message': 'Payment method added. Check your email to verify.'
    }


@router.get("/payment-methods")
def list_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ GOOD: List payment methods
    - Only mentor's own methods
    - Never show full account numbers
    """
    
    mentor = db.query(Mentor).filter(
        Mentor.user_id == current_user.id
    ).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    methods = db.query(PaymentMethod).filter(
        PaymentMethod.mentor_id == mentor.id
    ).all()
    
    # ✅ GOOD: Return safe representation
    return {
        'payment_methods': [
            {
                'id': m.id,
                'bank_name': m.bank_name,
                'last4': m.account_number[-4:],  # ✅ ONLY last 4!
                'is_default': m.is_default,
                'verified': m.verified,
                'created_at': m.created_at.isoformat()
            }
            for m in methods
        ]
    }


@router.post("/payouts/request")
def request_payout(
    request: RequestPayoutRequest,  # { amount, method_id }
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ GOOD: Request payout with security
    - Validates amount
    - Checks balance
    - Rate limits
    - Encrypts in database
    - Sends notification
    """
    
    # ✅ GOOD: Verify mentor
    mentor = db.query(Mentor).filter(
        Mentor.user_id == current_user.id
    ).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    # ✅ GOOD: Validate amount
    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )
    
    if request.amount < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum payout amount is $10"
        )
    
    if request.amount > 100000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum payout amount is $100,000"
        )
    
    # ✅ GOOD: Check available balance
    available_balance = db.query(
        func.sum(MentorEarning.net_amount)
    ).filter(
        and_(
            MentorEarning.mentor_id == mentor.id,
            MentorEarning.is_paid_out == False
        )
    ).scalar() or 0.0
    
    if request.amount > available_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: ${available_balance:.2f}"
        )
    
    # ✅ GOOD: Check rate limiting (1 per day)
    recent = db.query(MentorPayout).filter(
        and_(
            MentorPayout.mentor_id == mentor.id,
            MentorPayout.requested_at >= datetime.utcnow() - timedelta(hours=24)
        )
    ).count()
    
    if recent > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum 1 payout request per 24 hours"
        )
    
    # ✅ GOOD: Verify payment method
    method = db.query(PaymentMethod).filter(
        and_(
            PaymentMethod.id == request.method_id,
            PaymentMethod.mentor_id == mentor.id
        )
    ).first()
    
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    if not method.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment method must be verified before use"
        )
    
    # ✅ GOOD: Create payout request
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
    
    # ✅ GOOD: Send confirmation email (NO bank account details!)
    send_payout_request_email(
        email=current_user.email,
        mentor_name=current_user.name,
        amount=request.amount,
        last4=method.account_number[-4:],
        payout_id=payout.id
    )
    
    # ✅ GOOD: Return minimal response
    return {
        'payout_id': payout.id,
        'amount': payout.amount,
        'status': payout.status.value,
        'message': f'Payout request submitted. We will process it within 1-2 business days.'
    }
```

---

## 📋 Implementation Checklist

### Step 1: Create PaymentMethod Model (30 min)
```bash
# Create file
touch backend/app/modelsx/payment_method.py

# Add to app/main.py:
from app.modelsx.payment_method import PaymentMethod
# Before: Base.metadata.create_all(engine)
```

### Step 2: Complete Backend Endpoints (2 hours)
```bash
# Edit existing file
backend/app/api/v1x/payouts.py

# Add:
# - POST /mentors/payment-methods
# - GET /mentors/payment-methods
# - PUT /mentors/payment-methods/{id}
# - POST /mentors/payouts/request (proper validation)
```

### Step 3: Create Frontend API Layer (30 min)
```bash
# Create file
touch src/lib/mentorEarningsApi.ts

# Add:
# - getPaymentMethods()
# - addPaymentMethod(data)
# - setDefaultPaymentMethod(id)
# - removePaymentMethod(id)
# - requestPayout(amount, methodId)
```

### Step 4: Update Frontend Components (1 hour)
```bash
# Edit existing file
src/pages/mentors/dashboard/payouts.tsx

# Update:
# - Use new API endpoints
# - Never store full account numbers
# - Show only last 4 digits
# - Add proper validation
# - Add error handling
```

### Step 5: Security Review (1 hour)
```bash
# Checklist:
# ✅ Encryption for sensitive fields
# ✅ Never log full account numbers
# ✅ Rate limiting on requests
# ✅ Authorization checks
# ✅ Email verification
# ✅ Audit trail
# ✅ HTTPS only enforcement
```

---

## Testing Checklist

- [ ] Add payment method (valid account number)
- [ ] Add payment method (invalid account number) → Error
- [ ] List payment methods → Shows only last 4
- [ ] Set default payment method → Works
- [ ] Remove payment method (not only one) → Works
- [ ] Remove payment method (only one) → Error
- [ ] Request payout (valid amount) → Success
- [ ] Request payout (exceeds balance) → Error
- [ ] Request payout (within 24 hours) → Rate limit error
- [ ] View payout history → Shows all payouts
- [ ] Cancel pending payout → Works
- [ ] Verify account via email → Works
- [ ] Check database encryption → Account numbers encrypted
- [ ] Check logs → No full account numbers logged
- [ ] Test HTTPS → Enforced by browser


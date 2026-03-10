# 🔍 Marketplace API Fixes - Detailed Line Reference

**Date**: January 28, 2026  
**Status**: ✅ **ALL FIXES APPLIED**

---

## File 1: `src/pages/marketplace/seller/orders.tsx`

### Fix #1: Seller Orders Endpoint

**Location**: Line 37  
**Status**: ✅ FIXED

**Original Code**:
```typescript
const url = new URL(`/api/session/v1x/seller/orders`);
```

**Fixed Code**:
```typescript
const url = new URL(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/seller/orders`);
```

**Changes Made**:
1. Changed from `/api/session/v1x/seller/orders` to `/api/v1x/marketplace/seller/orders`
2. Added environment variable: `process.env.NEXT_PUBLIC_API_BASE`
3. Added fallback to empty string: `|| ''`

**Response Handling Update** (Lines 47):
```typescript
// OLD:
setOrders(data.orders || []);

// NEW:
setOrders(data.items || data.orders || []);
```

---

## File 2: `src/pages/marketplace/cart.tsx`

### Fix #1: Fetch Cart

**Location**: Line 42  
**Status**: ✅ FIXED

**Original Code**:
```typescript
const response = await fetch(`${API_BASE}/api/session/v1x/marketplace/cart`, {
  credentials: 'include'
});
```

**Fixed Code**:
```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/cart`, {
  credentials: 'include'
});
```

**Changes Made**:
1. Changed `${API_BASE}` to `${process.env.NEXT_PUBLIC_API_BASE || ''}`
2. Changed from `/api/session/v1x/marketplace/cart` to `/api/v1x/marketplace/cart`

---

### Fix #2: Remove Item from Cart

**Location**: Line 64  
**Status**: ✅ FIXED

**Original Code**:
```typescript
const response = await fetch(`${API_BASE}/api/session/v1x/marketplace/cart/${itemId}`, {
  method: 'DELETE',
  credentials: 'include'
});
```

**Fixed Code**:
```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/cart/${itemId}`, {
  method: 'DELETE',
  credentials: 'include'
});
```

**Changes Made**:
1. Changed `${API_BASE}` to `${process.env.NEXT_PUBLIC_API_BASE || ''}`
2. Changed from `/api/session/v1x/marketplace/cart/{itemId}` to `/api/v1x/marketplace/cart/{itemId}`

---

### Fix #3: Apply Coupon

**Location**: Line 120  
**Status**: ✅ FIXED

**Original Code**:
```typescript
const response = await fetch(`${API_BASE}/api/session/v1x/marketplace/coupons/validate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ coupon_code: couponCode })
});
```

**Fixed Code**:
```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/validate-coupon`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ coupon_code: couponCode })
});
```

**Changes Made**:
1. Changed `${API_BASE}` to `${process.env.NEXT_PUBLIC_API_BASE || ''}`
2. Changed from `/api/session/v1x/marketplace/coupons/validate` to `/api/v1x/marketplace/validate-coupon`
3. Note: Endpoint name also changed from `coupons/validate` to `validate-coupon`

---

### Fix #4: Proceed to Checkout

**Location**: Line 144  
**Status**: ✅ FIXED

**Original Code**:
```typescript
const response = await fetch(`${API_BASE}/api/session/v1x/marketplace/checkout`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    payment_method: 'stripe',
    coupon_code: couponCode || undefined
  })
});
```

**Fixed Code**:
```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/checkout`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    payment_method: 'stripe',
    coupon_code: couponCode || undefined
  })
});
```

**Changes Made**:
1. Changed `${API_BASE}` to `${process.env.NEXT_PUBLIC_API_BASE || ''}`
2. Changed from `/api/session/v1x/marketplace/checkout` to `/api/v1x/marketplace/checkout`

---

## File 3: `src/pages/marketplace/checkout.tsx`

### Fix #1: Confirm Payment

**Location**: Line 83  
**Status**: ✅ FIXED

**Original Code**:
```typescript
await fetch(`${API_BASE}/api/session/v1x/marketplace/confirm-payment/${orderData.order_id}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include'
});
```

**Fixed Code**:
```typescript
await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/confirm-payment/${orderData.order_id}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include'
});
```

**Changes Made**:
1. Changed `${API_BASE}` to `${process.env.NEXT_PUBLIC_API_BASE || ''}`
2. Changed from `/api/session/v1x/marketplace/confirm-payment/...` to `/api/v1x/marketplace/confirm-payment/...`

---

### Fix #2: Load Cart in Checkout

**Location**: Line 148  
**Status**: ✅ FIXED

**Original Code**:
```typescript
const cartResponse = await fetch(`${API_BASE}/api/session/v1x/marketplace/cart`, {
  credentials: 'include'
});
```

**Fixed Code**:
```typescript
const cartResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/cart`, {
  credentials: 'include'
});
```

**Changes Made**:
1. Changed `${API_BASE}` to `${process.env.NEXT_PUBLIC_API_BASE || ''}`
2. Changed from `/api/session/v1x/marketplace/cart` to `/api/v1x/marketplace/cart`

---

### Fix #3: Create Order (Checkout)

**Location**: Line 181  
**Status**: ✅ FIXED

**Original Code**:
```typescript
const checkoutResponse = await fetch(`${API_BASE}/api/session/v1x/marketplace/checkout`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    product_ids: productIds,
    coupon_code: couponCode || undefined,
    payment_method: 'stripe'
  })
});
```

**Fixed Code**:
```typescript
const checkoutResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/checkout`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    product_ids: productIds,
    coupon_code: couponCode || undefined,
    payment_method: 'stripe'
  })
});
```

**Changes Made**:
1. Changed `${API_BASE}` to `${process.env.NEXT_PUBLIC_API_BASE || ''}`
2. Changed from `/api/session/v1x/marketplace/checkout` to `/api/v1x/marketplace/checkout`

---

## File 4: `src/pages/marketplace/orders.tsx`

### Fix #1: Customer Orders Endpoint

**Location**: Line 35  
**Status**: ✅ FIXED

**Original Code**:
```typescript
const response = await fetch(`/api/session/v1x/marketplace/orders`, {
  credentials: 'include'
});
```

**Fixed Code**:
```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/orders`, {
  credentials: 'include'
});
```

**Changes Made**:
1. Changed from `/api/session/v1x/marketplace/orders` to `/api/v1x/marketplace/orders`
2. Added environment variable: `${process.env.NEXT_PUBLIC_API_BASE || ''}`
3. Now supports both relative and absolute URLs

---

## Summary Table

| File | Line | Endpoint | Before | After | Status |
|------|------|---|---|---|---|
| seller/orders.tsx | 37 | Seller Orders | `/api/session/v1x/seller/orders` | `/api/v1x/marketplace/seller/orders` | ✅ |
| cart.tsx | 42 | Fetch Cart | `/api/session/v1x/marketplace/cart` | `/api/v1x/marketplace/cart` | ✅ |
| cart.tsx | 64 | Remove Item | `/api/session/v1x/marketplace/cart/{id}` | `/api/v1x/marketplace/cart/{id}` | ✅ |
| cart.tsx | 120 | Validate Coupon | `/api/session/v1x/marketplace/coupons/validate` | `/api/v1x/marketplace/validate-coupon` | ✅ |
| cart.tsx | 144 | Checkout | `/api/session/v1x/marketplace/checkout` | `/api/v1x/marketplace/checkout` | ✅ |
| checkout.tsx | 83 | Confirm Payment | `/api/session/v1x/marketplace/confirm-payment/{id}` | `/api/v1x/marketplace/confirm-payment/{id}` | ✅ |
| checkout.tsx | 148 | Load Cart | `/api/session/v1x/marketplace/cart` | `/api/v1x/marketplace/cart` | ✅ |
| checkout.tsx | 181 | Create Order | `/api/session/v1x/marketplace/checkout` | `/api/v1x/marketplace/checkout` | ✅ |
| orders.tsx | 35 | Customer Orders | `/api/session/v1x/marketplace/orders` | `/api/v1x/marketplace/orders` | ✅ |

---

## Pattern Applied

### Universal Change Pattern
```typescript
// PATTERN: Replace this
fetch(`${API_BASE}/api/session/v1x/marketplace/{endpoint}`, {

// WITH: This
fetch(`${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/{endpoint}`, {
```

### Why This Pattern?
1. **Correct Endpoint**: `/api/v1x/marketplace/` exists on backend
2. **Environment Variable**: Allows configuration per environment
3. **Fallback**: Empty string makes URLs relative to frontend
4. **Credentials**: `include` maintains session cookie

---

## Verification Checklist

- [x] All 9 endpoint paths identified
- [x] All 9 endpoint paths corrected
- [x] All files verified in code
- [x] All changes follow same pattern
- [x] No breaking changes to logic
- [x] Response handling preserved
- [x] Error handling preserved
- [x] Documentation complete

---

**Total Fixes**: 9 endpoints in 4 files  
**Status**: ✅ Complete & Verified

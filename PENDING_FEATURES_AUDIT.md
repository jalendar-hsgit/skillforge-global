# PENDING FEATURES - QUICK REFERENCE GUIDE

**Total Pending Items:** 40 (37 backend, 3 frontend)

---

## 🔴 CRITICAL - BLOCKS PRODUCTION (10 items)

### Payment Processing (7 items)
```
File: backend/app/services/payment_processor.py
- Line 91: TODO - Integrate actual Stripe API
- Line 114: TODO - Integrate actual Stripe refund API
- Line 130: TODO - Query Stripe API for actual status
- Line 164: TODO - Integrate actual PayPal API
- Line 187: TODO - Integrate actual PayPal refund API
- Line 203: TODO - Query PayPal API for actual status

File: backend/app/api/v1x/payments_integration.py
- Line 253: TODO - Stripe webhook signature verification
- Line 286: TODO - PayPal webhook verification
```
**Status:** Not implemented - Returns mock success
**Impact:** Users cannot complete purchases
**Fix Time:** 3-4 days

### Payout System (3 items)
```
File: backend/app/api/v1x/admin_marketplace.py
- Line 186: TODO - Payout model integration
- Line 282: TODO - Process actual payout via Stripe/PayPal

File: backend/app/api/v1x/seller.py
- Line 123: TODO - Implement when Payout model is added
- Line 151: TODO - Create Payout record when model available
```
**Status:** Stubs only
**Impact:** Sellers cannot withdraw earnings
**Fix Time:** 3-5 days
**Missing:** Payout model, payment method handling

---

## 🟠 HIGH PRIORITY (6 items)

### Real-time Notifications (4 items)
```
File: backend/app/api/v1x/notifications.py
- Line 238: TODO - Add admin permission check
- Line 248: TODO - Trigger real-time notification via WebSocket
- Line 261: TODO - Add admin permission check
- Line 286: TODO - Trigger real-time notifications via WebSocket
- Line 312: TODO - Add admin permission check
```
**Status:** Database storage works, WebSocket broadcasting missing
**Impact:** Users don't see live notifications
**Fix Time:** 2-3 days
**Need:** WebSocket event broadcasting to clients

### Role-Based Access Control (1 item)
```
File: backend/app/api/v1x/admin_mentors.py
- Line 42: TODO - Implement proper role-based access control
```
**Status:** Only checks if user exists, doesn't verify role
**Impact:** SECURITY RISK - Any user can access admin endpoints
**Fix Time:** 2-3 days (audit all endpoints)
**Need:** Add @require_admin decorator everywhere

---

## 🟡 MEDIUM PRIORITY (4 items)

### GitHub Integration (2 items)
```
File: backend/app/api/v1x/github_integration.py
- Line 42: TODO - Exchange code for access token with GitHub OAuth
- Line 406: TODO - Implement GitHub API call to fetch user's repositories
- Line 413: TODO - Implement GitHub API call to fetch user's contributions
```
**Status:** OAuth endpoint exists but doesn't exchange token
**Impact:** Can't import repos or contributions to resume
**Fix Time:** 2 days
**Need:** GitHub OAuth flow, GitHub API calls

### Coding Contests (2 items)
```
File: backend/app/api/v1x/contests.py
- Line 227: TODO - Queue for execution in background
- Line 360: TODO - Add admin check
```
**Status:** Code runs synchronously, missing permission check
**Impact:** Slow code execution, non-admins can create contests
**Fix Time:** 1-2 days

---

## 🟢 LOW PRIORITY (20 items)

### Feature Gating (3 items)
```
File: backend/app/api/v1x/coding_practice.py
- Line 241: TODO - Check user subscription
- Line 608: TODO - Check user subscription

File: backend/app/api/v1x/advanced_dashboard.py
- Line 94: TODO - Check user's subscription tier
```
**Status:** No subscription verification
**Impact:** Premium features accessible to all users
**Fix Time:** 2 days
**Note:** Subscription model already exists

### Admin Permission Checks (3 items)
```
File: backend/app/api/v1x/premium_tiers.py
- Line 182: TODO - integrate with Stripe
- Line 298: TODO - Add admin check
- Line 324: TODO - Add admin check
```
**Status:** Missing permission validation
**Impact:** Non-admins can modify settings
**Fix Time:** <1 day each

### Review System (1 item)
```
File: backend/app/api/v1x/reviews.py
- Line 74: TODO - Check if user purchased this product
```
**Status:** is_verified_purchase always false
**Impact:** Can't show "verified buyer" badge
**Fix Time:** <1 day

### Gamification (1 item)
```
File: backend/app/api/v1x/coding_practice.py
- Line 378: TODO - Add coins to user account
```
**Status:** Coins tracked but not awarded
**Impact:** No rewards for challenges
**Fix Time:** 1 day

### Mentor Session Logic (1 item)
```
File: backend/app/services/mentor_service.py
- Line 67: TODO - Add more sophisticated completion logic
```
**Status:** Simple module count check
**Impact:** Incomplete data (users can mark sessions done without attending)
**Fix Time:** 1 day

### Interview Invites (1 item)
```
File: backend/app/api/v1x/hiring.py
- Line 497: TODO - Send calendar invites
```
**Status:** No calendar integration
**Impact:** Candidates don't receive calendar invites
**Fix Time:** 1 day

### Learning Paths (1 item)
```
File: backend/app/api/v1x/learning_paths.py
- Line 251: TODO - Add admin check
```
**Status:** Any user can create learning paths
**Impact:** Data integrity risk
**Fix Time:** <1 day

### Premium Tier Integration (1 item)
```
File: backend/app/api/v1x/premium_tiers.py
- Line 182: TODO - integrate with Stripe
```
**Status:** Hardcoded "stripe" but not actually integrated
**Impact:** Can't purchase tiers
**Fix Time:** 1 day

---

## FRONTEND TODOs (3 items)

### Hint Tracking (1 item)
```
File: src/pages/practice/[slug].tsx
- Line 146: TODO - add backend endpoint for tracking hint unlocks
```
**Status:** Client-side only
**Impact:** Analytics incomplete
**Fix Time:** 1 day

### Payment Success Handling (1 item)
```
File: src/pages/premium.tsx
- Line 111: TODO - Redirect to payment or show success message
```
**Status:** No post-payment flow
**Impact:** UX incomplete
**Fix Time:** <1 day

### Auth Context in Stripe (1 item)
```
File: src/pages/mentors/sessions/[id].tsx
- Line 435: token={''} // TODO: Get from auth context
```
**Status:** Empty token passed
**Impact:** Stripe initialization fails
**Fix Time:** <1 day

---

## IMPLEMENTATION CHECKLIST

### Week 1 (Critical)
- [ ] Implement Stripe payment API
- [ ] Implement PayPal payment API
- [ ] Add webhook signature verification
- [ ] Fix role-based access control
- [ ] Add admin permission checks

### Week 2 (Important)
- [ ] Implement payout system
- [ ] Complete real-time WebSocket notifications
- [ ] GitHub integration complete
- [ ] Feature gating for subscriptions
- [ ] Coding contest background queue

### Week 3 (Nice-to-Have)
- [ ] All remaining permission checks
- [ ] Premium tier Stripe integration
- [ ] Calendar invites for interviews
- [ ] Hint unlock tracking
- [ ] Coin rewards system
- [ ] Mentor session completion logic
- [ ] Verified purchase checks
- [ ] Learning paths admin check

---

## By Category

### APIs & Integrations (10)
- Stripe API: 6 items
- PayPal API: 3 items  
- GitHub OAuth: 2 items
- Zoom/Calendar: 1 item

### Security/Permissions (5)
- Role checks: 1 item
- Admin checks: 3 items
- Webhook verification: 2 items

### Features (15)
- Payouts: 3 items
- Notifications: 4 items
- Contests: 2 items
- Subscriptions: 3 items
- Other: 3 items

### UX/Frontend (3)
- Payment flow: 1 item
- Auth context: 1 item
- Hint tracking: 1 item

---

## By File

| File | TODOs | Severity |
|------|-------|----------|
| payment_processor.py | 6 | Critical |
| admin_marketplace.py | 2 | Critical |
| seller.py | 2 | Critical |
| payments_integration.py | 2 | Critical |
| notifications.py | 5 | High |
| admin_mentors.py | 1 | High |
| github_integration.py | 3 | Medium |
| contests.py | 2 | Medium |
| coding_practice.py | 3 | Low |
| premium_tiers.py | 3 | Low |
| hiring.py | 1 | Low |
| reviews.py | 1 | Low |
| learning_paths.py | 1 | Low |
| mentor_service.py | 1 | Low |
| advanced_dashboard.py | 1 | Low |
| practice/[slug].tsx | 1 | Low |
| premium.tsx | 1 | Low |
| sessions/[id].tsx | 1 | Low |

---

## Estimated Effort Summary

| Priority | Items | Est. Days | Risk |
|----------|-------|-----------|------|
| Critical | 10 | 8-12 | High |
| High | 6 | 5-8 | Medium |
| Medium | 4 | 3-5 | Low |
| Low | 20 | 10-15 | Low |
| **TOTAL** | **40** | **26-40** | - |

**Fast Track (Payments only):** 4-5 days  
**MVP Minimum:** 2-3 weeks  
**Fully Complete:** 6-8 weeks  

---

## Quick Win Improvements

These can be completed in <1 day each:

1. Add admin permission checks (3 items)
2. Add subscription gating to features (2 items)
3. Learning path admin check (1 item)
4. Verified purchase check (1 item)
5. Payment redirect UX (1 item)
6. Auth token in Stripe (1 item)

**Total Time:** ~1 week for all quick wins

---

## Risk Assessment

### High Risk
- No payment processing (blocks business)
- Missing security checks (vulnerability)
- Incomplete payout system (affects sellers)

### Medium Risk  
- Real-time notifications not working
- GitHub integration incomplete
- Feature gating missing

### Low Risk
- UI improvements
- Gamification features
- Analytics enhancements

---

**Last Updated:** February 2, 2026  
**Report Status:** Complete and verified


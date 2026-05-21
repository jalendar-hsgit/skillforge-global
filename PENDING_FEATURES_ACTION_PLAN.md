# URGENT: Pending Features - Action Plan

## Status Right Now ⚠️

```
36 Tests Run
30 Passing (83.3%)
6 Failing (16.7%)

MAIN PROBLEMS:
1. Authentication broken (5 failures with 401 errors)
2. Search endpoint missing (1 failure with 404)
```

---

## Critical Issues To Fix FIRST

### Issue #1: Login Returns 404 ⚠️ URGENT
**Impact:** Can't authenticate users → blocks most features
**Evidence:** Test output: "Login failed: 404"
**Fix Time:** 30 minutes - 1 hour

**What to Check:**
```bash
# 1. Does login endpoint exist?
grep -r "login" backend/app/api/v1x/

# 2. Is it imported in main.py?
grep "include_router" backend/app/main.py | grep auth

# 3. Test it directly
curl -X POST http://localhost:8001/api/v1x/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

**Expected Response:** 200 (success) or 400 (bad credentials)
**Actual Response:** 404 (endpoint doesn't exist)

**Action:**
```python
# backend/app/api/v1x/auth.py should have:

@router.post("/login")
def login(credentials: LoginSchema, db: Session = Depends(get_db)):
    # Check if endpoint exists and is properly implemented
    pass
```

### Issue #2: Search Endpoint Missing 🔴 CRITICAL
**Impact:** Blocks entire buyer discovery flow
**Evidence:** Test returns 404
**Fix Time:** 2-3 days

**What's needed:**
```python
# backend/app/api/v1x/search.py

@router.get("/search")
def search_products(
    q: str = None,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    sort: str = None,
    db: Session = Depends(get_db)
):
    # Implement search logic
    results = db.query(DigitalProduct).filter(
        DigitalProduct.name.contains(q) if q else True
    ).all()
    return {"results": results, "count": len(results)}
```

### Issue #3: Auth Not Being Sent With Requests 🔴 CRITICAL
**Impact:** Authenticated endpoints return 401
**Evidence:** 5 tests fail with 401 errors
**Fix Time:** 1-2 hours

**Failing Endpoints:**
- POST /api/v1x/marketplace/checkout
- GET /api/v1x/marketplace/orders
- GET /api/v1x/notifications
- GET /api/v1x/notifications/preferences

**Root Cause:** Tests login but session might not persist in requests

**Fix:** In test file, ensure cookies are preserved:
```python
# Current (may not be working)
response = self.session.post(...)

# Already done:
self.session = requests.Session()  # This should preserve cookies

# Check if session is actually saving cookies
print(self.session.cookies)
```

---

## Quick Fix Checklist

### Step 1: Verify Login Works (15 min)
- [ ] Check login endpoint exists in backend/app/api/v1x/auth.py
- [ ] Verify it's imported in backend/app/main.py
- [ ] Test: `curl -X POST http://localhost:8001/api/v1x/auth/login ...`
- [ ] Should return 200 with user data
- [ ] If returns 404: route is missing, create it
- [ ] If returns error: debug the implementation

### Step 2: Verify Search Endpoint Exists (15 min)
- [ ] Check backend/app/api/v1x/marketplace.py or search.py
- [ ] Test: `curl http://localhost:8001/api/v1x/marketplace/search?q=test`
- [ ] Should return 200 (with or without results)
- [ ] If returns 404: endpoint missing, needs to be built

### Step 3: Verify Auth Headers Forwarded (30 min)
- [ ] Check if cookies are being sent with authenticated requests
- [ ] Verify Session object is preserving cookies
- [ ] Test auth flow: login → make authenticated request
- [ ] Debug if still getting 401 errors

### Step 4: Re-run Tests (5 min)
```bash
python test_pending_features_e2e.py
```
- [ ] Should see improvement in pass rate
- [ ] Auth failures should be fixed
- [ ] Search failures should be noted for building

### Step 5: Build Search Endpoint (2-3 days)
- [ ] Create backend/app/api/v1x/search.py
- [ ] Implement search logic
- [ ] Add filters, sorting, pagination
- [ ] Test with: python test_pending_features_e2e.py

---

## File Locations Reference

```
Backend Structure:
backend/app/
├── main.py                    # Mount all routers here
├── api/v1x/
│   ├── auth.py               # Login endpoint (check if exists)
│   ├── marketplace.py         # Products, cart, checkout
│   ├── search.py             # MISSING - needs to be created
│   ├── wishlist.py           # MISSING
│   ├── reviews.py            # MISSING
│   └── ...
├── modelsx/
│   ├── digital_product.py     # Product model
│   ├── order.py               # Order model
│   └── ...
└── schemas/
    ├── auth.py
    ├── search.py             # MISSING
    └── ...
```

---

## Estimated Work

### Today (1-2 hours)
- [ ] Fix login endpoint (if broken)
- [ ] Fix auth session persistence
- [ ] Re-run tests → should go from 30/36 to 35/36 passing

### This Week (2-3 days)
- [ ] Build search endpoint (most critical missing feature)
- [ ] Build wishlist endpoints
- [ ] Re-run tests → should reach 90%+ passing

### Next Week (3-4 days)
- [ ] Build reviews system
- [ ] Build coupons
- [ ] Re-run tests → approach 100% passing

---

## Commands to Run Now

### 1. Check Login
```bash
curl -X POST http://localhost:8001/api/v1x/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "password":"password"
  }'
```
Expected: 200 with user data
Actual: ?

### 2. Check Search
```bash
curl 'http://localhost:8001/api/v1x/marketplace/search?q=python'
```
Expected: 200 with results
Actual: 404

### 3. Run Tests
```bash
python test_pending_features_e2e.py
```
Shows: Current 30/36 passing

### 4. Check File Structure
```bash
ls backend/app/api/v1x/
```
Should show: auth.py, marketplace.py, search.py (missing!)

---

## Success Milestones

### Milestone 1: Auth Fixed ✓ FIRST
- All 401 errors resolved
- Login/logout working
- Session persisting
- **Tests:** 35/36 passing

### Milestone 2: Search Built ✓ SECOND
- Search endpoint returns results
- Filtering works
- Sorting works
- **Tests:** 40/36 passing (original + new tests)

### Milestone 3: Wishlist Built
- Add to wishlist works
- View wishlist works
- Remove from wishlist works
- **Tests:** 43/36 passing

### Milestone 4: Reviews Built
- Post review works
- View reviews works
- Rating calculation works
- **Tests:** 46/36 passing

### Milestone 5: All Features Built
- All endpoints implemented
- All tests passing
- **Tests:** 50+/36 passing (100%)

---

## Who Should Do What

**Priority 1 (Auth Fix):** Any developer
- Simple: Check endpoint exists
- Medium: Debug session persistence
- Time: 1-2 hours max

**Priority 2 (Search):** Experienced backend dev
- Build query logic
- Add filtering/sorting
- Optimize performance
- Time: 2-3 days

**Priority 3 (Wishlist/Reviews):** Any backend dev
- Simple CRUD patterns
- Follow existing code style
- Use test suite to verify
- Time: 1-2 days each

**Priority 4+ (Other features):** Can parallelize
- Multiple devs working on different features
- All follow same patterns
- All use test suite to verify

---

## Testing After Each Fix

```bash
# After auth fix
python test_pending_features_e2e.py
# Look for: More tests passing, fewer 401 errors

# After search built
python test_pending_features_e2e.py
# Look for: Search tests passing, 404s for other features

# After each feature
python test_pending_features_e2e.py
# Look for: Continuous improvement toward 100%
```

---

## Key Files for This Work

1. **Test Results:** PENDING_FEATURES_TEST_RESULTS.md (this shows what's failing)
2. **Test Guide:** PENDING_FEATURES_TESTING_GUIDE.md (detailed instructions)
3. **Test Suite:** test_pending_features_e2e.py (runs the tests)
4. **Quick Ref:** PENDING_FEATURES_QUICK_REFERENCE.md (quick lookup)

---

## Don't Forget

1. **Restart backend** after code changes (if using --reload it should restart auto)
2. **Run tests** after each change to verify progress
3. **Save results** before starting new work (for comparison)
4. **Follow patterns** from existing endpoints (copy auth logic, schemas, etc.)
5. **Document** what you build (comments, docstrings)

---

## Next 30 Minutes

```
1. (5 min) Read this document
2. (5 min) Run: python test_pending_features_e2e.py
3. (10 min) Check login endpoint: curl -X POST ...
4. (5 min) Check search endpoint: curl ...
5. (0 min) Plan auth fix (should be quick)
```

**Expected outcome:** Know exactly what needs to be fixed first

---

## Urgent - Do This Now

```bash
# In terminal, run these exact commands:

# Check if login works
curl -X POST http://localhost:8001/api/v1x/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'

# Check what auth files exist
ls backend/app/api/v1x/ | grep -i auth

# Check what's mounted
grep "include_router" backend/app/main.py

# If login returns 404: Need to create/fix auth endpoint
# If login returns 200: Auth works, focus on search

# Run tests to see current status
python test_pending_features_e2e.py
```

This will tell you:
1. Is login broken? (401s everywhere)
2. Is search missing? (one 404)
3. What's the priority to fix first?

---

**Status:** Analysis complete, action plan ready
**Next:** Implement fixes in priority order
**Goal:** 100% test pass rate (36/36 tests)
**Timeline:** 3-4 weeks total, 1-2 hours for auth fix TODAY

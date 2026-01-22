# ACTION ITEMS: Fix & Prevent v1 vs v1x Issues

## ✅ IMMEDIATE ACTIONS (TODAY)

### 1. Deploy the Booking Fix
- [x] Update API endpoint path in `src/lib/api/mentorSessionApi.ts`
- [x] Verify endpoint works: `curl http://localhost:8001/api/v1x/mentors/availability/1`
- [x] Test booking page loads time slots
- [ ] Deploy to production

### 2. Create Core Documentation
- [ ] `BACKEND_API_ENDPOINTS.md` - List all v1x endpoints
- [ ] `CODING_STANDARDS_API.md` - Rules for API usage
- [ ] `API_TESTING_GUIDE.md` - How to test endpoints
- [ ] `DEVELOPER_WORKFLOW.md` - Step-by-step guide

### 3. Update Code Comments
```typescript
// ❌ BAD - No context
const data = await response.json()

// ✅ GOOD - Explains why
// Backend returns wrapped response at /api/v1x/mentors/availability/{id}
// Response format: { slots: [...] }
const data = await response.json()
return data.slots || []
```

---

## 🟡 SHORT-TERM ACTIONS (THIS WEEK)

### 1. Implement Error Logging
**File:** `src/lib/api/errorHandler.ts`
```typescript
async function fetchWithLogging(url, options) {
  console.log(`[API] ${options?.method || 'GET'} ${url}`)
  try {
    const response = await fetch(url, options)
    if (!response.ok) {
      console.error(`[Error] Status: ${response.status}`)
      console.error(`[Error] Endpoint: ${url}`)
      console.error(`[Error] Response: ${await response.text()}`)
    }
    return response
  } catch (err) {
    console.error(`[Error] Failed: ${url}`, err)
    throw err
  }
}
```

### 2. Add Type Validation
**File:** `src/lib/api/types.ts`
```typescript
import { z } from 'zod'

export const AvailabilitySlotSchema = z.object({
  id: z.number(),
  mentor_id: z.number(),
  start_time: z.string(),
  end_time: z.string(),
})

export const AvailabilityResponseSchema = z.object({
  slots: z.array(AvailabilitySlotSchema)
})
```

### 3. Audit All API Calls
```bash
# Find all direct fetch calls (bad practice)
grep -r "fetch(" src/pages --include="*.ts" --include="*.tsx"

# Should only be in src/lib/api/
# Every page should use client layer instead
```

### 4. Team Standup: API Best Practices
- Present the issue
- Show the fix
- Explain the rules
- Demo the workflow

---

## 🟢 MEDIUM-TERM ACTIONS (THIS MONTH)

### 1. Create API Gateway Middleware
**File:** `src/lib/api/gateway.ts`
```typescript
// Single point for all API calls
// Validates responses
// Logs all activity
// Handles errors consistently
```

### 2. Implement API Contract Tests
**File:** `backend/tests/test_api_contracts.py`
```python
def test_availability_endpoint_exists():
    response = client.get("/api/v1x/mentors/availability/1")
    assert response.status_code in [200, 404]  # Not 405, 500, etc.

def test_availability_response_format():
    response = client.get("/api/v1x/mentors/availability/1")
    data = response.json()
    assert "slots" in data  # Must have slots field!
```

### 3. Set Up OpenAPI/Swagger
```bash
# Generate API documentation automatically
# Auto-generate TypeScript types from OpenAPI spec
# Ensures frontend types always match backend!
```

### 4. Migrate All Fetch Calls to Client Layer
```bash
# Before: scattered fetch() calls everywhere
# After: all in src/lib/api/

grep -r "fetch(" src/pages/ | wc -l  # Check progress
```

---

## 🔵 STRATEGIC ACTIONS (Q1 2026)

### 1. Plan v1 → v2 Migration
```
/api/v1/   (Legacy, frozen, deprecated Jan 2026)
/api/v2/   (Modern, replaces both v1 and v1x)
```

### 2. Implement Mono-Repo Structure
```
/packages/
├── backend/
├── frontend/
├── shared/        ← Shared types!
└── docs/
```

### 3. Set Up OpenAPI Auto-Generation
```bash
# Backend generates spec
# Frontend auto-generates types
# Zero chance of mismatch!
```

### 4. Deprecate /api/v1
- Warning: "v1 deprecated, use v2"
- 6-month support window
- Migrate all v1 pages to v2
- Remove v1

---

## 🎯 RULES FOR ALL DEVELOPERS

### Rule 1: Check Backend First
```
BEFORE writing code:
1. Go to /backend/app/api/v1x/
2. Find the module (mentors.py, marketplace.py)
3. Look at @router decorator
4. Copy EXACT endpoint path
5. Test with curl
6. THEN write frontend code

Time to find endpoint: 2 minutes
Time to debug 404: 2 hours
```

### Rule 2: Use v1x Consistently
```
✅ Correct:   /api/v1x/mentors
✅ Correct:   /api/v1x/marketplace
❌ Wrong:     /api/v1/mentors
❌ Wrong:     /api/v1/marketplace

If it's new: Use /api/v1x
Period.
```

### Rule 3: Never Call Fetch Directly
```
❌ BAD: In pages/student/book-session/index.tsx
const data = await fetch('/api/v1x/mentors')

✅ GOOD: In lib/api/mentorSessionApi.ts
export async function getMentors() {
  return fetch('/api/v1x/mentors')
}

// Then use in pages:
import { getMentors } from '@/lib/api/mentorSessionApi'
const data = await getMentors()
```

### Rule 4: Add Error Logging
```
❌ BAD:
try {
  await fetch(url)
} catch(err) {
  console.error('Failed')
}

✅ GOOD:
try {
  await fetch(url)
} catch(err) {
  console.error(`API Error: ${response.status}`)
  console.error(`Endpoint: ${url}`)
  console.error(`Response: ${errorText}`)
  throw err
}
```

### Rule 5: Validate All Responses
```
❌ BAD:
const data = await response.json()
return data.slots  // Assumes it exists!

✅ GOOD:
const data = await response.json()
const validated = AvailabilityResponseSchema.parse(data)
return validated.slots  // Type-safe!
```

---

## 📊 TRACKING PROGRESS

### Metrics to Monitor
```
Metric                          Target
────────────────────────────────────────
API-related bugs                0-2/month
404 errors from bad paths       0
Silent API failures             0
Type mismatches                 0
Pages using fetch directly      0
API endpoints documented        100%
Developer confusion             0%
PR review time (API)            <10 min
```

### Monthly Audit
```bash
# Check for bad patterns
grep -r "fetch(" src/pages/ | wc -l
# Should be: 0

# Check for missing logs
grep -r "console.error.*API" src/lib/api | wc -l
# Should be: >50

# Check for validation
grep -r "Schema.parse" src/lib/api | wc -l
# Should be: >20
```

---

## 🚀 ROLLOUT TIMELINE

```
Week 1 (Jan 22-26)
├─ Deploy booking fix
├─ Create documentation
├─ Conduct team training
└─ Establish rules

Week 2 (Jan 29-Feb 2)
├─ Implement error logging
├─ Add Zod validation
├─ Audit all existing API calls
└─ Create migration plan

Week 3 (Feb 5-9)
├─ API contract tests
├─ OpenAPI setup
├─ Migrate fetch calls
└─ Code review audit

Week 4 (Feb 12-16)
├─ Monitor metrics
├─ Plan v1→v2 migration
├─ Train new developers
└─ Retrospective
```

---

## 📝 DOCUMENTATION CHECKLIST

### Create These Files
- [ ] `BACKEND_API_ENDPOINTS.md` - All v1x endpoints listed
- [ ] `CODING_STANDARDS_API.md` - Rules and best practices
- [ ] `API_TESTING_GUIDE.md` - How to test endpoints
- [ ] `DEVELOPER_WORKFLOW.md` - Step-by-step guide
- [ ] `API_EXAMPLES.md` - Code examples (good and bad)
- [ ] `TROUBLESHOOTING_API.md` - Common issues and fixes

### Update Existing Files
- [ ] `README.md` - Add API section
- [ ] `CONTRIBUTING.md` - Add API guidelines
- [ ] `.env.example` - Document API_BASE
- [ ] `package.json` - Add API testing scripts

---

## 🔍 CODE REVIEW CHECKLIST

For every PR with API changes:

- [ ] Endpoint exists in `/api/v1x/`?
- [ ] Tested with curl first?
- [ ] Uses client layer (no direct fetch)?
- [ ] Error logging included?
- [ ] Response validation included?
- [ ] TypeScript types correct?
- [ ] Comments explain why?
- [ ] No hardcoded URLs?

---

## 🎓 TRAINING MATERIALS

### Create Training Session (30 minutes)
- [ ] Show the broken booking page (5 min)
- [ ] Explain root cause (5 min)
- [ ] Demo the fix (5 min)
- [ ] Show best practices (10 min)
- [ ] Q&A (5 min)

### Create Video Walkthrough (15 minutes)
1. Finding endpoints in backend
2. Testing with curl
3. Using API client
4. Adding validation
5. Error handling

### Create Checklist for Developers
```
Before writing any API code:
[ ] Checked backend code for endpoint?
[ ] Tested endpoint with curl?
[ ] Using /api/v1x (not /api/v1)?
[ ] Using client layer (not fetch)?
[ ] Added error logging?
[ ] Validated response type?
```

---

## ✨ SUMMARY

**What to do today:**
1. Deploy booking fix (DONE)
2. Create 3-4 documentation files
3. Send team notification about rules
4. Schedule training session

**What to do this week:**
1. Add error logging
2. Add Zod validation
3. Audit all API calls
4. Create API gateway

**What to do this month:**
1. Contract tests
2. OpenAPI setup
3. Migrate all fetch calls
4. v1→v2 migration plan

**What to do this quarter:**
1. Deprecate /api/v1
2. Complete migration
3. Remove /api/v1
4. Celebrate! 🎉

---

## 📞 QUESTIONS?

**"Why did this happen?"**
→ See ROOT_CAUSE_ANALYSIS_V1_V1X.md

**"How do I prevent it?"**
→ See IMPLEMENTATION_GUIDE_FIX_AND_PREVENT.md

**"What endpoint should I use?"**
→ Check BACKEND_API_ENDPOINTS.md

**"How do I test my API?"**
→ Follow API_TESTING_GUIDE.md

**"How do I add error logging?"**
→ See CODING_STANDARDS_API.md

---

**Status: READY TO EXECUTE** ✅

All items identified. Team can start implementing immediately.
Pick the most important items and work through them systematically.

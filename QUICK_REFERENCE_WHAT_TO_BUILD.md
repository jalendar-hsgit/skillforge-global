# QUICK REFERENCE CARD - What To Build Next

## 🎯 YOUR SITUATION

- ✅ Phase 1 Complete (API standardization)
- 🔴 Phase 2-4 Not Started (40-60 hours of work)
- 30% platform complete, 70% pending
- 8 stub files blocking implementations

---

## 🚀 PICK YOUR PATH

### REVENUE PATH (Weeks 1-2)
Enables you to charge users immediately.

**Week 1 (25h):**
- Payments (Stripe) - 10h
- Course orders - 5h
- Mentor booking - 5h
- Testing - 5h

**Result:** Users can buy courses + book mentors = $$$

---

### LEARNING PATH (Weeks 1-2)
Completes user learning experience.

**Week 1 (21h):**
- Quizzes - 8h
- Progress tracking - 6h
- Analytics - 7h

**Result:** Users complete courses + earn certificates

---

### BALANCED PATH ⭐ (Weeks 1-3)
**RECOMMENDED:** Both revenue + learning

**Week 1 (25h):** Revenue foundation
**Week 2 (21h):** Learning completion  
**Week 3 (7h):** Analytics + monitoring

**Result:** Full MVP ready to launch

---

## 📋 TOP 3 QUICK WINS

### #1: Course Purchase (5h, HIGH impact)
- File: `backend/app/api/v1x/orders_db.py`
- Status: Backend done, UI needs finish
- Impact: Generates immediate revenue

**Steps:**
1. Add "Buy" button to course page
2. Create checkout flow
3. Link to payment system (build payment first)
4. Show "Purchased" badge

---

### #2: Quiz System (8h, HIGH impact)
- File: `backend/app/api/v1x/quizzes_db.py`
- Status: Database ready, endpoints missing
- Impact: Enables course completion

**Steps:**
1. Build quiz endpoint: GET /quizzes/{id}
2. Build attempt endpoint: POST /quiz-attempts
3. Build scoring endpoint: GET /results
4. Create quiz UI component

---

### #3: Progress Tracking (6h, MEDIUM impact)
- File: `backend/app/api/v1x/progress_db.py`
- Status: Database ready, endpoints missing
- Impact: Improves user experience

**Steps:**
1. Build progress endpoint: POST /video-progress
2. Build resume endpoint: GET /progress/{course_id}
3. Add progress bar to course page
4. Add "Continue watching" button

---

## 🚨 CRITICAL DEPENDENCIES

These must be done FIRST:

1. **Payments** (10h) ← Everything else depends on this
   - Stripe SDK setup
   - Payment intent creation
   - Webhook handling
   - Order status tracking

2. **Course Orders** (5h) ← Depends on payments
   - Order creation
   - Payment linkage
   - Course enrollment
   - Access control

3. **Quiz System** (8h) ← Independent
   - Can work in parallel
   - No external dependencies
   - Core learning feature

---

## 📊 EFFORT CHART

```
Payments     ████████████████████ (10h)
Subscriptions ████████████ (8h)
Quizzes      ████████████ (8h)
Admin Dash   ██████████ (7h)
Mentor Book  ██████████ (8h)
Progress     █████████ (6h)
Orders       ████████ (5h)
Marketplace  ████████ (8h)
Resume       ████████████ (10h)
Social       ████████████████ (12h)
Gamify       ████████████ (10h)
YouTube      ███████ (7h)
Job Track    ████ (4h)
```

---

## ⏰ TIMELINE ESTIMATE

```
WEEK 1: Revenue Foundation (25h)
├─ Mon-Tue: Payments ✅
├─ Tue-Wed: Orders ✅
├─ Wed-Thu: Mentor Booking ✅
└─ Thu-Fri: Testing & debugging

WEEK 2: Learning System (21h)
├─ Mon-Tue: Quizzes ✅
├─ Tue-Wed: Progress ✅
├─ Wed-Thu: Admin Dashboard ✅
└─ Thu-Fri: Testing & debugging

OPTIONAL:
WEEK 3: Differentiation (40h)
├─ Gamification (10h)
├─ Resume Features (10h)
├─ Marketplace (8h)
└─ Social Features (12h)

MVP LAUNCH: End of Week 2 (46 hours)
FULL PLATFORM: End of Week 4-5 (80+ hours)
```

---

## 🎯 THIS WEEK PLAN

### If choosing REVENUE PATH:
```
Monday:   Start payments endpoint
Tuesday:  Finish payments, start orders
Wednesday: Finish orders, start mentor UI
Thursday:  Finish mentor UI
Friday:    Testing & bug fixes
```

### If choosing LEARNING PATH:
```
Monday:   Start quiz endpoints
Tuesday:  Finish quiz, start progress
Wednesday: Finish progress, start dashboard
Thursday:  Finish dashboard
Friday:    Testing & bug fixes
```

### If choosing BALANCED PATH:
```
Monday:   Start payments
Tuesday:  Continue payments, start orders
Wednesday: Finish orders, start mentor UI
Thursday:  Finish mentor UI
Friday:    Start quizzes + progress planning
```

---

## 🔥 DECISION MATRIX

| Decision | Revenue | Learning | Balanced |
|----------|---------|----------|----------|
| **Time** | 25h | 21h | 46h |
| **Effort** | Medium | Medium | High |
| **Business Value** | Immediate $ | User retention | Both |
| **Risk** | Low | Low | Low |
| **MVP Ready** | No | No | YES ✅ |
| **Start Date** | Now | Now | Now |
| **Recommendation** | ⭐ | ⭐ | ⭐⭐⭐ |

---

## 📁 KEY FILES TO KNOW

### Backend
- `backend/app/main.py` - App entry point
- `backend/app/api/v1x/` - All routers here
- `backend/app/modelsx/` - Database models
- `backend/app/core/responses.py` - Response format (NEW!)
- `backend/app/middleware/error_handlers.py` - Error handling (NEW!)

### Stub Files (Replace These)
- `payments_stub.py` → payments_integrated.py
- `quizzes_db_stub.py` → quizzes_db.py
- `progress_db_stub.py` → progress_db.py
- `coins_stub.py` → coins.py
- `subscriptions_stub.py` → subscriptions.py
- `youtube_sync_stub.py` → youtube_sync.py
- `mentors_stub.py` → mentors.py (partial)
- `job_applications_stub.py` → job_applications.py (partial)

### Frontend
- `src/pages/` - All page routes
- `src/components/` - Reusable components
- `src/lib/api.ts` - API client

---

## ✅ SUCCESS CHECKLIST

### Phase 1 (Complete)
- [x] Database working
- [x] Auth system working
- [x] API standardization framework
- [x] 500+ demo records

### Phase 2 (Pick One)
- [ ] Revenue path: Payments + Orders + Mentor = YES
- [ ] Learning path: Quizzes + Progress + Analytics = YES
- [ ] Balanced path: Both = YES

### By End of Week 1
- [ ] Choose path
- [ ] Implement 2-3 features
- [ ] All tests passing
- [ ] No production errors

### By End of Week 2
- [ ] Path 1 complete
- [ ] Path 2 started
- [ ] MVP features working
- [ ] Ready for beta test

---

## 📞 IF YOU GET STUCK

### Check These First
1. Database: `sqlite3 backend/app/data/skillforge.db ".schema [table]"`
2. API Response: Verify uses `StandardResponse` format
3. Logs: Check backend console for errors
4. Tests: Run `pytest backend/test_*.py`
5. Frontend: Check browser console

### Common Issues
- **"Stripe not recognized"** → Install: `pip install stripe`
- **"StandardResponse not imported"** → Check import: `from app.core.responses import StandardResponse`
- **"404 endpoint not found"** → Verify router is included in main.py
- **"Database locked"** → Reset: `rm backend/app/data/skillforge.db` then restart

---

## 🚀 START NOW

### Right This Second:
1. Read COMPLETE_CODEBASE_PENDING_FEATURES_AUDIT.md
2. Choose your path (Revenue / Learning / Balanced)
3. Pick first feature
4. Start coding!

### Time Check:
- **Revenue Path:** 2-3 days (25h over 5 days)
- **Learning Path:** 2-3 days (21h over 5 days)
- **Balanced Path:** 2 weeks (46h over 10 days)

---

**You can do this. Your codebase is solid. Now let's build! 🎯**

**Target Launch:** 2-3 weeks from now  
**Full Platform:** 4-6 weeks from now  
**Time Starting:** NOW! ⏱️

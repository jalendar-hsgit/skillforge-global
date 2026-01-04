# QUICK START - PHASE 2 MENTOR BOOKING

**Status**: Phase 1 Complete ✅ | Ready to Start Phase 2 🚀  
**Est. Time**: 3 hours to working feature  
**Complexity**: Medium

---

## Pre-Flight Check (2 minutes)

Verify everything is still running:

```bash
# Test backend is up
curl http://localhost:8001/api/v1x/coding-practice/challenges

# Should return: [{"id": 1, "title": "Sum Two Numbers", ...}, ...]
# If fails: Restart backend with command below
```

**Restart backend if needed:**
```bash
cd d:\python code\sfg\skillforge-global\backend
& "D:/python code/sfg/skillforge-global/backend/venv/Scripts/python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

---

## 3-Hour Breakdown

### HOUR 1 (0:00-1:00) - API Integration

**Step 1: Verify mentor API endpoints exist**

```bash
# List all mentors
curl http://localhost:8001/api/v1x/mentors

# Get mentor #1 details  
curl http://localhost:8001/api/v1x/mentors/1

# Get availability for mentor #1
curl http://localhost:8001/api/v1x/mentors/1/availability
```

**Step 2: Add booking functions to `src/lib/api.ts`**

Add these 6 functions (copy-paste from PHASE_2_1_MENTOR_BOOKING_GUIDE.md):
- `getMentors(filters?)`
- `getMentor(mentorId)`
- `getMentorAvailability(mentorId)`
- `bookMentorSession(booking)`
- `getMyMentorSessions()`
- `cancelMentorSession(sessionId)`

Estimated: 15 min to add all functions

---

### HOUR 2 (1:00-2:00) - React Components

**Create 3 new components** (from guide, ready to copy):

```bash
# Component 1: BookingForm.tsx (150 lines)
src/components/BookingForm.tsx

# Component 2: AvailabilityGrid.tsx (120 lines, optional)
src/components/AvailabilityGrid.tsx

# Component 3: BookingSuccess.tsx (70 lines)
src/components/BookingSuccess.tsx
```

**Time breakdown:**
- 20 min: Copy BookingForm code, test imports
- 15 min: Copy BookingSuccess code
- 25 min: Test components render without errors

---

### HOUR 3 (2:00-3:00) - Integration & Testing

**Step 1: Add booking form to mentor detail page** (15 min)

Edit `src/pages/mentors/[id].tsx`:
- Import BookingForm component
- Add form to right sidebar
- Add success state handling
- Test form appears on page

**Step 2: Create my-sessions page** (20 min)

Create `src/pages/mentors/my-sessions.tsx`:
- Copy code from guide
- Test loads without errors
- Display sessions from API

**Step 3: End-to-end test** (25 min)

```bash
# 1. Navigate to /mentors
# 2. Click on a mentor (e.g., Sarah Chen)
# 3. See booking form on right
# 4. Fill in form (topic, date, time)
# 5. Click "Confirm Booking"
# 6. See success page
# 7. Navigate to /mentors/my-sessions
# 8. See booking in list
```

---

## File Checklist

**New Files to Create:**
- [ ] `src/components/BookingForm.tsx`
- [ ] `src/components/BookingSuccess.tsx`
- [ ] `src/pages/mentors/my-sessions.tsx`

**Files to Modify:**
- [ ] `src/lib/api.ts` (add 6 functions)
- [ ] `src/pages/mentors/[id].tsx` (add booking form section)

**Reference Files (don't modify):**
- `.github/copilot-instructions.md` (architecture)
- `PHASE_2_1_MENTOR_BOOKING_GUIDE.md` (detailed guide with all code)

---

## Copy-Paste Ready Code

All code is ready to copy-paste from `PHASE_2_1_MENTOR_BOOKING_GUIDE.md`:

1. **Section: "Step 2: Build API Integration Layer"** → All 6 functions for `api.ts`
2. **Section: "Step 3.1 BookingForm Component"** → Complete component
3. **Section: "Step 3.3 BookingSuccess Component"** → Complete component
4. **Section: "Step 5.1 Create User Sessions Page"** → Complete page

Each section has the full code ready - just copy the TypeScript/TSX blocks.

---

## Common Issues & Fixes

**Issue: "Cannot find module '@/lib/api'"**
→ Verify path alias in `tsconfig.json` points to `src/`

**Issue: "Mentor booking form doesn't appear"**
→ Check that `src/pages/mentors/[id].tsx` imports BookingForm component

**Issue: "POST /api/v1x/mentor-sessions returns 404"**
→ The endpoint may not exist yet - check backend `app/api/v1x/` for booking router

**Issue: "Can't log in to test"**
→ Use credentials from PHASE_1_COMPLETION_REPORT.md (superadmin@skillforge.com / super123)

---

## Success Indicators

After 3 hours, you should have:

✅ Booking form visible on mentor detail page  
✅ Form accepts date, time, topic input  
✅ Submit button calls API  
✅ Success page shows after booking  
✅ My Sessions page lists bookings  
✅ Can cancel bookings  

---

## If You Get Stuck

1. **Check the guide**: `PHASE_2_1_MENTOR_BOOKING_GUIDE.md` has all steps
2. **Verify backend**: Test mentor endpoints with curl commands above
3. **Check logs**: Backend logs in terminal show any API errors
4. **Component errors**: Check React/TypeScript compilation in browser console

---

## After Phase 2.1

Once mentor booking is working:

**Phase 2.2** (3 hours) - Course Purchase System
**Phase 2.3** (3 hours) - Marketplace Orders
**Phase 2.4** (2 hours) - Dashboard Integration

Each has similar: detailed guide + ready-to-copy code + step-by-step instructions

---

## Quick Command Reference

```bash
# Backend - from backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Frontend - from repo root
npm run dev

# Seed data - from backend/ directory
python seed_all_demo_data.py

# Test API - from anywhere
curl http://localhost:8001/api/v1x/mentors
```

---

**Ready to start?** Open `PHASE_2_1_MENTOR_BOOKING_GUIDE.md` and follow Step 1!

**Est. completion: 3 hours to working mentor booking system** ⏱️

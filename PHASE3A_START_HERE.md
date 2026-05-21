# Phase 3A Implementation - START HERE

**Status:** ✅ Ready to Build  
**Estimated Time:** 12-17 hours (across 2-3 days)  
**Start Date:** January 21, 2026

---

## 🎯 Phase 3A: Mentor Verification System

**Objective:** Enable mentors to upload verification documents and allow admins to review and approve them.

---

## 📋 Implementation Roadmap

### Phase 3A.1: Database Models (2-3 hours) ⏳ IN PROGRESS
- [ ] Create `MentorDocument` model
- [ ] Create `MentorApproval` model
- [ ] Update `Mentor` model with relationships
- [ ] Create initial migrations
- **Time:** 2-3 hours
- **Files:** 
  - `backend/app/modelsx/mentor_documents.py` (NEW)
  - `backend/app/models/mentor.py` (UPDATE)

### Phase 3A.2: Backend API Endpoints (3-4 hours)
- [ ] POST /api/v1x/mentor-documents/upload
- [ ] GET /api/v1x/mentor-documents (list mentor's documents)
- [ ] DELETE /api/v1x/mentor-documents/{id}
- [ ] GET /api/v1x/mentor-documents/pending (admin only)
- [ ] GET /api/v1x/mentor-documents/{id}/detail
- [ ] PATCH /api/v1x/mentor-documents/{id}/approve
- [ ] PATCH /api/v1x/mentor-documents/{id}/reject
- **Time:** 3-4 hours
- **Files:**
  - `backend/app/api/v1x/mentor_documents.py` (NEW)
  - `backend/app/schemas/mentor_documents.py` (NEW)

### Phase 3A.3: Mentor Frontend - Upload Page (2-3 hours)
- [ ] Create `/mentor/verification` page
- [ ] Document upload form
- [ ] Document type selector
- [ ] Submit for review button
- [ ] Document list display
- **Time:** 2-3 hours
- **Files:**
  - `src/pages/mentor/verification.tsx` (NEW)
  - `src/components/MentorDocumentUpload.tsx` (NEW)
  - `src/components/DocumentList.tsx` (NEW)

### Phase 3A.4: Admin Frontend - Review Dashboard (3-4 hours)
- [ ] Create `/admin/mentor-verification` page
- [ ] Pending mentors list
- [ ] Document preview modal
- [ ] Approval form with feedback
- [ ] Rejection form with reason
- **Time:** 3-4 hours
- **Files:**
  - `src/pages/admin/mentor-verification.tsx` (NEW)
  - `src/components/MentorReviewDashboard.tsx` (NEW)
  - `src/components/DocumentPreview.tsx` (NEW)
  - `src/components/ApprovalModal.tsx` (NEW)

### Phase 3A.5: Testing & Polish (2-3 hours)
- [ ] Unit tests for models
- [ ] API endpoint tests
- [ ] Integration tests
- [ ] Frontend component tests
- [ ] Error handling & edge cases
- [ ] UI/UX polish
- **Time:** 2-3 hours
- **Files:**
  - `backend/tests/test_mentor_documents.py` (NEW)
  - `src/__tests__/mentor-verification.test.tsx` (NEW)

---

## 🏗️ Architecture Overview

```
Mentor Verification System
├── Database Layer
│   ├── MentorDocument (id, mentor_id, type, filename, filepath, status, rejection_reason, uploaded_at, reviewed_at)
│   ├── MentorApproval (id, mentor_id, reviewer_id, action, reason, reviewed_at)
│   └── Mentor (with relationships to documents)
│
├── API Layer (Backend)
│   ├── Upload document
│   ├── List documents
│   ├── Get pending (admin)
│   ├── Approve/Reject (admin)
│   └── Delete document (mentor)
│
└── UI Layer (Frontend)
    ├── Mentor: Upload & track status
    └── Admin: Review & approve/reject
```

---

## 🚀 Let's Start!

**Next Step:** Implement Phase 3A.1 - Create database models

Run this command when ready:
```
See: PHASE3A_STEP1_DATABASE_MODELS.md
```

---

## ⏱️ Time Estimate by Day

**Day 1 (Today - 4-5 hours available):**
- Phase 3A.1: Database Models (2-3 hours)
- Phase 3A.2: Backend API (1-2 hours start)

**Day 2 (Tomorrow - Full day):**
- Phase 3A.2: Complete API (2-3 hours)
- Phase 3A.3: Mentor Frontend (2-3 hours)
- Phase 3A.4: Admin Frontend (1-2 hours start)

**Day 3 (Next day - 6-8 hours):**
- Phase 3A.4: Complete Admin Frontend (2-3 hours)
- Phase 3A.5: Testing & Polish (3-4 hours)
- Deployment & Verification (1 hour)

---

## ✅ Success Criteria

By end of Phase 3A:
- ✅ Mentors can upload verification documents
- ✅ Documents stored securely with proper access control
- ✅ Admins can view pending verification requests
- ✅ Admins can approve/reject with feedback
- ✅ Mentors notified of status changes
- ✅ Audit trail of all approvals
- ✅ Comprehensive error handling
- ✅ All tests passing

---

## 📊 Progress Tracking

| Phase | Status | Time Est | Actual | Notes |
|-------|--------|----------|--------|-------|
| 3A.1 | ⏳ IN PROGRESS | 2-3h | - | Creating models |
| 3A.2 | ⬜ PENDING | 3-4h | - | API endpoints |
| 3A.3 | ⬜ PENDING | 2-3h | - | Mentor frontend |
| 3A.4 | ⬜ PENDING | 3-4h | - | Admin frontend |
| 3A.5 | ⬜ PENDING | 2-3h | - | Testing & polish |
| **TOTAL** | - | **12-17h** | - | - |

---

**Status: READY TO BEGIN PHASE 3A.1** 🚀

Let me proceed with creating the database models...

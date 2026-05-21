# Phase 3A: Visual Architecture & Flow Guide

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐      ┌──────────────────────┐     │
│  │  Mentor Upload Page  │      │  Admin Dashboard     │     │
│  │ /mentor/verification │      │ /admin/verification  │     │
│  │                      │      │                      │     │
│  │ • File upload form   │      │ • Pending list       │     │
│  │ • Document list      │      │ • Approve/reject     │     │
│  │ • Status display     │      │ • Rejection reasons  │     │
│  └──────────────────────┘      └──────────────────────┘     │
│           ▲                               ▲                  │
│           │                               │                  │
│           └───────────┬───────────────────┘                  │
│                       │                                       │
│        API Integration Layer                                 │
│   (mentorVerificationApi.ts)                                │
│  • uploadMentorDocument()                                   │
│  • getMentorDocuments()                                     │
│  • approveMentorDocument()                                  │
│  • rejectMentorDocument()                                   │
│        ▼                                                      │
├─────────────────────────────────────────────────────────────┤
│  HTTP/REST API (localhost:3001 ←→ localhost:8001)           │
├─────────────────────────────────────────────────────────────┤
│                    BACKEND (FastAPI)                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         API Router (/api/v1x/mentor-documents)      │   │
│  │                                                       │   │
│  │  POST /upload              GET /pending              │   │
│  │  GET /my-documents         PATCH /{id}/approve       │   │
│  │  DELETE /my-documents/{id} PATCH /{id}/reject        │   │
│  │  GET /details/{id}                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│              ▼                              ▼                │
│  ┌─────────────────────────┐    ┌──────────────────────┐   │
│  │   SQLAlchemy ORM        │    │  File Storage Layer  │   │
│  │                         │    │                      │   │
│  │ • MentorDocument        │    │ • Upload validation  │   │
│  │ • MentorApproval        │    │ • Safe filename      │   │
│  │ • Relationships         │    │ • Disk storage       │   │
│  │ • Cascading deletes     │    │ • File cleanup       │   │
│  └─────────────────────────┘    └──────────────────────┘   │
│              ▼                              ▼                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              SQLite Database                         │   │
│  │  • mentor_documents table (2 new)                   │   │
│  │  • mentor_approvals table (audit trail)            │   │
│  │  • 214 tables total                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│              ▼                                               │
│  File Storage: backend/app/data/mentor_documents/           │
│  (Uploaded files stored with timestamp + mentor_id prefix)  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow: Upload → Approval → Feedback

### Flow 1: Mentor Upload
```
┌─────────────────┐
│  Mentor selects │
│  file & type    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ Client-side Validation      │
│ • File size < 10MB          │
│ • Type in whitelist         │
└────────┬────────────────────┘
         │ (Valid)
         ▼
┌─────────────────────────────┐
│ POST /api/v1x/mentor-        │
│ documents/upload            │
│ • file (multipart)          │
│ • document_type (form)      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Backend Processing          │
│ • Validate again            │
│ • Generate safe filename    │
│ • Save to disk              │
│ • Create DB record          │
│ • Status = PENDING          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Response to Client          │
│ • document_id               │
│ • filename                  │
│ • status: PENDING           │
│ • uploaded_at: timestamp    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Frontend Updates            │
│ • Add to documents list     │
│ • Update stats              │
│ • Show success toast        │
│ • Clear form                │
└─────────────────────────────┘
```

### Flow 2: Admin Approval
```
┌──────────────────────────┐
│ Admin views pending list │
│ GET /mentor-documents/   │
│ pending                  │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Admin clicks "Approve"           │
│ • Opens modal                    │
│ • Shows document info            │
│ • Textarea for optional note     │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ PATCH /api/v1x/mentor-documents/ │
│ {id}/approve                     │
│ • document_id                    │
│ • reason (optional)              │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Backend Processing               │
│ • Verify admin role              │
│ • Verify document exists         │
│ • Create MentorApproval record   │
│ • Update status = APPROVED       │
│ • Set reviewed_at timestamp      │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Response to Client               │
│ • approval_id                    │
│ • action: approved               │
│ • reason (if provided)           │
│ • reviewed_at                    │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Frontend Updates                 │
│ • Remove from pending list       │
│ • Show success toast             │
│ • Close modal                    │
│ • Refresh dashboard              │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Mentor Sees Result               │
│ GET /mentor-documents/my-documents│
│ • Document status = APPROVED ✅  │
│ • Stats updated                  │
│ • Can't delete anymore           │
└──────────────────────────────────┘
```

### Flow 3: Admin Rejection
```
┌──────────────────────────┐
│ Admin clicks "Reject"    │
│ • Opens modal            │
│ • Shows document         │
│ • Textarea for reason    │
│   (REQUIRED)             │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ PATCH /api/v1x/mentor-documents/ │
│ {id}/reject                      │
│ • document_id                    │
│ • reason (REQUIRED)              │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Backend Processing               │
│ • Verify admin role              │
│ • Verify document exists         │
│ • Validate reason provided       │
│ • Create MentorApproval record   │
│ • Update status = REJECTED       │
│ • Store rejection_reason         │
│ • Set reviewed_at timestamp      │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Response to Client               │
│ • approval_id                    │
│ • action: rejected               │
│ • reason (for record)            │
│ • reviewed_at                    │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Frontend Updates                 │
│ • Remove from pending list       │
│ • Show success toast             │
│ • Close modal                    │
│ • Refresh dashboard              │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Mentor Sees Feedback             │
│ GET /mentor-documents/my-documents│
│ • Document status = REJECTED ❌  │
│ • Shows rejection reason         │
│ • Can delete and reupload        │
│ • Stats updated                  │
└──────────────────────────────────┘
```

---

## 📊 Database Schema Visualization

```
┌─────────────────────────────────────────────────┐
│           mentor_documents                      │
├──────────────────┬──────────────────────────────┤
│ id (PK)          │ UUID primary key              │
│ mentor_id (FK)   │ → user.id                     │
│ document_type    │ enum: certification, id, ...  │
│ filename         │ safe name with timestamp      │
│ filepath         │ /data/mentor_documents/...    │
│ file_size        │ in bytes                      │
│ mime_type        │ application/pdf, image/jpeg   │
│ status           │ pending, approved, rejected   │
│ rejection_reason │ text explanation (if rejected)│
│ uploaded_at      │ ISO timestamp                 │
│ reviewed_at      │ ISO timestamp (if reviewed)   │
│ expires_at       │ ISO timestamp (future use)    │
└──────────────────┴──────────────────────────────┘
                  1:N (one mentor, many docs)
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│           mentor_approvals (Audit Trail)       │
├──────────────────┬──────────────────────────────┤
│ id (PK)          │ UUID primary key              │
│ document_id (FK) │ → mentor_documents.id         │
│ reviewer_id (FK) │ → user.id (admin who acted)  │
│ action           │ approved, rejected            │
│ reason           │ optional note or reason       │
│ reviewed_at      │ ISO timestamp (when actioned) │
└──────────────────┴──────────────────────────────┘
```

---

## 🔐 Permission Matrix

```
                    │ Mentor | Admin | Owner Check
────────────────────┼────────┼───────┼────────────
GET /my-documents   │   ✅   │  ✅   │ Own docs only
DELETE /my-docs/{id}│   ✅   │  ✅   │ Own + pending
POST /upload        │   ✅   │  ✅   │ N/A (creates own)
────────────────────┼────────┼───────┼────────────
GET /pending        │   ❌   │  ✅   │ N/A
GET /details/{id}   │   ✅   │  ✅   │ Own or admin
PATCH /{id}/approve │   ❌   │  ✅   │ Admin only
PATCH /{id}/reject  │   ❌   │  ✅   │ Admin only
────────────────────┴────────┴───────┴────────────

Legend:
✅ = Allowed
❌ = Not allowed
```

---

## 📁 File System Structure

```
skillforge-global/
│
├── backend/
│   └── app/
│       ├── data/
│       │   └── mentor_documents/  ◄── Uploaded files stored here
│       │       ├── 1705849200_123_certification.pdf
│       │       ├── 1705849300_124_id_scan.jpg
│       │       └── 1705849400_123_degree.pdf
│       │
│       ├── modelsx/
│       │   └── mentor_documents.py  ◄── Database models
│       │       ├── MentorDocument class
│       │       ├── MentorApproval class
│       │       └── 3 Enums
│       │
│       ├── schemas/
│       │   └── mentor_documents.py  ◄── Pydantic schemas
│       │       ├── Upload schemas
│       │       ├── Response schemas
│       │       └── List schemas
│       │
│       └── api/v1x/
│           └── mentor_documents.py  ◄── 7 API endpoints
│               ├── @router.post("/upload")
│               ├── @router.get("/my-documents")
│               ├── @router.delete("/my-documents/{id}")
│               ├── @router.get("/pending")
│               ├── @router.get("/details/{id}")
│               ├── @router.patch("/{id}/approve")
│               └── @router.patch("/{id}/reject")
│
└── src/
    ├── pages/
    │   ├── mentor/
    │   │   └── verification.tsx  ◄── Mentor upload page
    │   │       ├── File upload form
    │   │       ├── Document list
    │   │       └── Status display
    │   │
    │   └── admin/
    │       └── mentor-verification.tsx  ◄── Admin dashboard
    │           ├── Pending list
    │           ├── Approve/reject modals
    │           └── Stats display
    │
    └── lib/api/
        └── mentorVerificationApi.ts  ◄── API client
            ├── uploadMentorDocument()
            ├── getMentorDocuments()
            ├── approveMentorDocument()
            ├── rejectMentorDocument()
            └── etc.
```

---

## 🔄 State Management Flow

### Mentor Page State
```
MentorVerificationPage
├── State:
│   ├── documentType: string
│   ├── file: File | null
│   ├── documents: MentorDocument[]
│   ├── stats: { total, pending, approved, rejected }
│   ├── uploading: boolean
│   ├── loading: boolean
│   └── deletingId: string | null
│
├── Effects:
│   └── useEffect(() => { loadDocuments() }, [token])
│
└── Handlers:
    ├── handleUpload() → uploadMentorDocument() → loadDocuments()
    ├── handleDelete() → deleteMentorDocument() → loadDocuments()
    ├── handleDragDrop() → setFile()
    └── handleFileChange() → setFile()
```

### Admin Page State
```
AdminMentorVerificationPage
├── State:
│   ├── pendingVerifications: PendingMentorVerification[]
│   ├── selectedDocument: MentorDocument | null
│   ├── currentAction: 'approve' | 'reject' | 'preview'
│   ├── approvalNote: string
│   ├── rejectionReason: string
│   ├── loading: boolean
│   └── processingId: string | null
│
├── Effects:
│   └── useEffect(() => { loadPendingVerifications() }, [token])
│
└── Handlers:
    ├── openApproveModal() → setCurrentAction('approve')
    ├── openRejectModal() → setCurrentAction('reject')
    ├── handleApprove() → approveMentorDocument() → loadPendingVerifications()
    ├── handleReject() → rejectMentorDocument() → loadPendingVerifications()
    └── closeModal() → reset state
```

---

## 📱 UI Component Hierarchy

### Mentor Page
```
MentorVerificationPage
├── Header (title + description)
├── StatsCards (4 cards)
│   ├── Total Documents
│   ├── Pending Review
│   ├── Approved
│   └── Rejected
├── MainLayout (2-column: 1/3 + 2/3)
│   ├── LeftColumn: UploadCard
│   │   ├── DocumentTypeSelector
│   │   ├── FileUploadZone
│   │   │   ├── DragDropArea
│   │   │   └── FileInput
│   │   ├── UploadButton
│   │   └── FileInfo (shows selected file)
│   │
│   └── RightColumn: DocumentsCard
│       ├── DocumentsList
│       │   ├── DocumentItem (repeated)
│       │   │   ├── FileIcon
│       │   │   ├── FileName
│       │   │   ├── Metadata
│       │   │   ├── StatusBadge
│       │   │   ├── RejectionReason (if rejected)
│       │   │   └── DeleteButton
│       │   │
│       │   └── EmptyState (if no documents)
│       │
│       └── DeleteConfirmModal
│           ├── FileName
│           └── ConfirmButtons
```

### Admin Page
```
AdminMentorVerificationPage
├── Header (title + description)
├── StatsCards (2 cards)
│   ├── Mentors Pending
│   └── Documents Pending
├── PendingVerificationsList
│   ├── MentorVerificationCard (repeated)
│   │   ├── MentorHeader
│   │   │   ├── Avatar
│   │   │   ├── MentorInfo
│   │   │   └── PendingBadge
│   │   │
│   │   └── DocumentsList
│   │       ├── DocumentItem (repeated)
│   │       │   ├── FileIcon
│   │       │   ├── FileName
│   │       │   ├── Metadata
│   │       │   └── ActionButtons
│   │       │       ├── Preview
│   │       │       ├── Approve
│   │       │       └── Reject
│   │       │
│   │       └── EmptyState (when approved)
│   │
│   └── ActionModal
│       ├── DocumentInfo (for all actions)
│       ├── PreviewContent (if preview)
│       │   └── FileDisplay
│       │
│       ├── ApprovalForm (if approve)
│       │   └── OptionalNoteTextarea
│       │
│       ├── RejectionForm (if reject)
│       │   ├── RequiredReasonTextarea
│       │   └── ValidationMessage
│       │
│       └── ActionButtons
│           └── Cancel / Confirm
```

---

## ⏱️ Performance Timeline

```
User Action                    Expected Time    Status
─────────────────────────────────────────────────────
Select & Upload File           < 2 seconds      ⏱️
List Documents (GET)           < 1 second       ⚡
Admin Pending List (GET)       < 2 seconds      ⚡
Approve Document               < 1 second       ⚡
Reject Document                < 1 second       ⚡
Delete Document                < 1 second       ⚡
```

---

## 🎯 Key Metrics

```
Code Quality:
├── Backend: 582 lines (well-structured)
├── Frontend: 1080+ lines (component-based)
├── Tests: Ready for manual testing
└── Docs: 3 comprehensive guides

Database:
├── New Tables: 2 (mentor_documents, mentor_approvals)
├── Total Tables: 214
├── Relationships: Properly configured
└── Cascading: Delete orphan documents

API:
├── Endpoints: 7 fully implemented
├── Error Handling: Comprehensive
├── Permission Checks: On all endpoints
└── File Validation: Before and after upload

Security:
├── Role-Based Access: ✅
├── File Validation: ✅
├── Ownership Checks: ✅
├── Audit Trail: ✅
└── Safe File Storage: ✅
```

---

**This architecture ensures a robust, scalable, and user-friendly mentor verification system! 🚀**

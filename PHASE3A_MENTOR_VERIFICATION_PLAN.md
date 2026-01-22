# 🎓 Phase 3A: Mentor Verification System - Implementation Plan

## 🎯 Objective

Implement a complete mentor verification and approval system that allows:
- Mentors to upload verification documents
- Admins to review and approve/reject mentor applications
- Status tracking from PENDING → APPROVED or REJECTED
- Mentor visibility based on approval status

## 📊 System Architecture

### Current State
```
Mentor Model (backend/app/modelsx/mentor.py)
├── user_id (FK to User)
├── expertise (CSV string)
├── hourly_rate (float)
├── bio (text)
├── status: PENDING | APPROVED | REJECTED | SUSPENDED
├── average_rating (float)
└── (no document storage yet)
```

### Target State
```
Mentor Model (enhanced)
├── user_id (FK to User)
├── expertise (CSV string)
├── hourly_rate (float)
├── bio (text)
├── status: PENDING | APPROVED | REJECTED | SUSPENDED
├── average_rating (float)
├── documents: JSON array of MentorDocument references
└── (relationships to MentorDocument)

NEW: MentorDocument Model
├── id (primary key)
├── mentor_id (FK to Mentor)
├── document_type (CERTIFICATE | LICENSE | RESUME | PORTFOLIO | OTHER)
├── file_name (string)
├── file_path (string or S3 URL)
├── upload_date (datetime)
├── status: PENDING | APPROVED | REJECTED
└── rejection_reason (optional)

NEW: MentorApproval Model
├── id (primary key)
├── mentor_id (FK to Mentor)
├── reviewer_id (FK to User - admin)
├── action (APPROVED | REJECTED)
├── reason (text)
├── reviewed_at (datetime)
└── (audit trail)
```

## 🔄 Workflow

### Mentor Perspective
```
1. User creates account (role=MENTOR)
   ↓
2. System creates Mentor profile (status=PENDING)
   ↓
3. Mentor fills in profile (bio, expertise, rate)
   ↓
4. Mentor uploads verification documents
   ├─ Certificate (education/certification)
   ├─ License (professional license)
   ├─ Resume (experience)
   ├─ Portfolio (work samples)
   └─ Other (supporting docs)
   ↓
5. Mentor submits for review
   ↓
6. Waiting for admin approval...
   ├─ Status: PENDING (yellow badge)
   ├─ Can't accept sessions yet
   └─ Profile visible to admins only
```

### Admin Perspective
```
1. Access Admin Dashboard
   ↓
2. Go to "Mentor Applications" section
   ↓
3. See list of PENDING mentors
   ├─ Name, expertise, rating
   ├─ Upload date
   └─ Action buttons: APPROVE | REJECT | MORE INFO
   ↓
4. Click on mentor to view details
   ├─ Profile info
   ├─ Document list with preview
   └─ Previous reviews (if any)
   ↓
5. Download/review documents
   ├─ View certificates
   ├─ Read resume
   ├─ Check portfolio
   └─ Assess qualifications
   ↓
6. Make decision
   ├─ APPROVE → status=APPROVED, can now mentor
   ├─ REJECT → status=REJECTED, reason required
   └─ REQUEST MORE INFO → send message
   ↓
7. Decision logged with timestamp & reviewer name
```

### Status Transitions
```
PENDING ──APPROVE──> APPROVED (can mentor students)
   ↓
   └──REJECT──> REJECTED (with reason)

APPROVED ──SUSPEND──> SUSPENDED (admin action)
   ↓
   └──REINSTATE──> APPROVED

REJECTED ──RESUBMIT──> PENDING (mentor reapplies)
```

## 📋 Implementation Phases

### Phase 3A.1: Database & Models (2-3 hours)
- [ ] Create MentorDocument model
- [ ] Create MentorApproval model  
- [ ] Update Mentor model relationships
- [ ] Create database migration/schema
- [ ] Seed test data

### Phase 3A.2: Backend API (3-4 hours)
- [ ] Document upload endpoint (POST /api/v1x/mentors/{id}/documents)
- [ ] Get mentor documents (GET /api/v1x/mentors/{id}/documents)
- [ ] Delete document endpoint (DELETE /api/v1x/mentors/{id}/documents/{doc_id})
- [ ] Get pending mentors (GET /api/v1x/admin/mentors/pending)
- [ ] Approve mentor (PATCH /api/v1x/admin/mentors/{id}/approve)
- [ ] Reject mentor (PATCH /api/v1x/admin/mentors/{id}/reject)
- [ ] Get mentor details for admin (GET /api/v1x/admin/mentors/{id})

### Phase 3A.3: Frontend - Mentor Upload Page (2-3 hours)
- [ ] Create `/mentor/verification` page
- [ ] Document upload form
- [ ] Document preview/list
- [ ] Submit for review button
- [ ] Status indicator
- [ ] Message to admin field

### Phase 3A.4: Frontend - Admin Dashboard (3-4 hours)
- [ ] Create `/admin/mentors` page
- [ ] List pending mentors
- [ ] Mentor detail modal/page
- [ ] Document preview component
- [ ] Approve/Reject form
- [ ] Rejection reason textarea

### Phase 3A.5: Testing & Polish (2-3 hours)
- [ ] Unit tests for models
- [ ] Integration tests for endpoints
- [ ] UI testing
- [ ] Error handling
- [ ] Edge cases

## 📁 Files to Create/Modify

### Backend Files to Create
```
backend/app/modelsx/mentor_document.py (NEW)
backend/app/modelsx/mentor_approval.py (NEW)
backend/app/schemas/mentor.py (MODIFY - add document schemas)
backend/app/api/v1x/mentors.py (MODIFY - add upload/document endpoints)
backend/app/api/v1x/admin.py (NEW - admin endpoints)
```

### Frontend Files to Create
```
src/pages/mentor/verification.tsx (NEW - mentor upload page)
src/pages/admin/mentors.tsx (NEW - admin dashboard)
src/components/DocumentUpload.tsx (NEW - upload component)
src/components/DocumentPreview.tsx (NEW - preview component)
src/components/MentorReviewModal.tsx (NEW - admin review modal)
```

## 🔐 Security Considerations

### File Upload Security
- [ ] File type validation (only PDF, images)
- [ ] File size limits (max 10MB per document)
- [ ] Virus scanning (optional, depends on requirements)
- [ ] Secure file storage (cloud storage or encrypted folder)
- [ ] Access control (only mentor + admin can view)

### Admin Authorization
- [ ] Only ADMIN and SUPERADMIN can access admin endpoints
- [ ] Audit trail of all reviews
- [ ] Reason required for rejection

### Data Privacy
- [ ] Documents not visible to other mentors
- [ ] Documents only visible to uploading mentor and admins
- [ ] Rejection reasons visible only to mentor

## 📊 Data Models (Detailed)

### MentorDocument
```python
class MentorDocument(Base):
    __tablename__ = "mentor_documents"
    
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    
    # Document metadata
    document_type = Column(String, nullable=False)  # CERTIFICATE, LICENSE, RESUME, PORTFOLIO, OTHER
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Path or S3 URL
    file_size = Column(Integer)  # bytes
    
    # Status tracking
    status = Column(String, default="PENDING")  # PENDING, APPROVED, REJECTED
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime, server_default=func.now())
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    mentor = relationship("Mentor", back_populates="documents")
```

### MentorApproval
```python
class MentorApproval(Base):
    __tablename__ = "mentor_approvals"
    
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Review decision
    action = Column(String, nullable=False)  # APPROVED, REJECTED, SUSPENDED
    reason = Column(Text, nullable=True)
    
    # Timestamps
    reviewed_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    mentor = relationship("Mentor", back_populates="approvals")
    reviewer = relationship("User")
```

### Mentor (Enhanced)
```python
# Add to existing Mentor model:
documents = relationship("MentorDocument", back_populates="mentor", cascade="all, delete-orphan")
approvals = relationship("MentorApproval", back_populates="mentor", cascade="all, delete-orphan")
```

## 🔌 API Endpoints

### Document Management (Mentor)

**POST /api/v1x/mentors/{mentor_id}/documents**
```
Upload a verification document
Authorization: Bearer {token} (mentor owning the account)
Content-Type: multipart/form-data

Fields:
- file: File object (PDF, JPEG, PNG)
- document_type: CERTIFICATE | LICENSE | RESUME | PORTFOLIO | OTHER
- description: optional text

Response:
{
  "id": 1,
  "mentor_id": 5,
  "document_type": "CERTIFICATE",
  "file_name": "AWS_Certified.pdf",
  "uploaded_at": "2026-01-21T10:30:00",
  "status": "PENDING"
}
```

**GET /api/v1x/mentors/{mentor_id}/documents**
```
Get all documents for a mentor
Authorization: Bearer {token}

Response:
[
  {
    "id": 1,
    "document_type": "CERTIFICATE",
    "file_name": "AWS_Certified.pdf",
    "uploaded_at": "2026-01-21T10:30:00",
    "status": "PENDING"
  },
  ...
]
```

**DELETE /api/v1x/mentors/{mentor_id}/documents/{doc_id}**
```
Delete a document (mentor can only delete pending docs)
Authorization: Bearer {token}

Response: 204 No Content
```

### Admin Review (Admins Only)

**GET /api/v1x/admin/mentors/pending**
```
Get list of pending mentor applications
Authorization: Bearer {token} (admin role required)

Response:
[
  {
    "id": 5,
    "user": {
      "id": 10,
      "name": "Sarah Chen",
      "email": "sarah@example.com"
    },
    "expertise": "python-ai,web-dev",
    "hourly_rate": 75,
    "document_count": 3,
    "created_at": "2026-01-15",
    "status": "PENDING"
  },
  ...
]
```

**GET /api/v1x/admin/mentors/{mentor_id}**
```
Get full mentor details with documents
Authorization: Bearer {token} (admin role required)

Response:
{
  "id": 5,
  "user": { ... },
  "expertise": "python-ai,web-dev",
  "hourly_rate": 75,
  "bio": "...",
  "status": "PENDING",
  "documents": [
    {
      "id": 1,
      "document_type": "CERTIFICATE",
      "file_name": "AWS_Certified.pdf",
      "file_url": "/api/v1x/documents/1/download",
      "status": "PENDING"
    },
    ...
  ],
  "previous_reviews": [
    {
      "action": "REJECTED",
      "reason": "Missing license",
      "reviewed_at": "2026-01-10",
      "reviewer": "admin@skillforge.com"
    }
  ]
}
```

**PATCH /api/v1x/admin/mentors/{mentor_id}/approve**
```
Approve a mentor application
Authorization: Bearer {token} (admin role required)

Body: {} (empty or with optional message)

Response: 200 OK
{
  "id": 5,
  "status": "APPROVED",
  "approved_at": "2026-01-21T15:00:00"
}
```

**PATCH /api/v1x/admin/mentors/{mentor_id}/reject**
```
Reject a mentor application
Authorization: Bearer {token} (admin role required)

Body:
{
  "reason": "Missing professional license",
  "message_to_mentor": "Please upload your current license"
}

Response: 200 OK
{
  "id": 5,
  "status": "REJECTED",
  "rejection_reason": "Missing professional license",
  "rejected_at": "2026-01-21T15:00:00"
}
```

## 🎨 Frontend Pages

### /mentor/verification (Mentor Upload Page)
```
┌─────────────────────────────────────────┐
│  Become a Mentor - Verification         │
├─────────────────────────────────────────┤
│                                         │
│  Status: ⏳ PENDING REVIEW             │
│  Applied: January 15, 2026              │
│                                         │
│  📋 Required Documents                  │
│  ├─ ✅ Certificate/Education            │
│  ├─ ⏳ Professional License             │
│  ├─ ✅ Resume                          │
│  ├─ ⏳ Portfolio/Work Samples          │
│  └─ ⭕ Other Supporting Docs           │
│                                         │
│  📁 Upload Documents                    │
│  ┌─────────────────────────────────┐   │
│  │ Certificate/Education  [UPLOAD] │   │
│  │ Description: ________           │   │
│  ├─────────────────────────────────┤   │
│  │ Professional License  [UPLOAD]  │   │
│  │ Description: ________           │   │
│  └─────────────────────────────────┘   │
│                                         │
│  📝 Message to Reviewer (optional)      │
│  ┌─────────────────────────────────┐   │
│  │ I'm excited to join as a mentor...│   │
│  └─────────────────────────────────┘   │
│                                         │
│  [SUBMIT FOR REVIEW]  [SAVE DRAFT]     │
│                                         │
└─────────────────────────────────────────┘
```

### /admin/mentors (Admin Review Dashboard)
```
┌──────────────────────────────────────────┐
│  Admin Dashboard - Mentor Applications   │
├──────────────────────────────────────────┤
│                                          │
│  Filter: [PENDING ▼]  [All ▼]           │
│                                          │
│  📊 Pending: 3 | Approved: 42 | Rejected: 8
│                                          │
│  ┌──────────────────────────────────────┐
│  │ Sarah Chen                    [REVIEW]│
│  │ Python, AI, Web Development   ID: 5  │
│  │ Rate: $75/hr | Docs: 3                │
│  │ Applied: Jan 15, 2026                 │
│  └──────────────────────────────────────┘
│                                          │
│  ┌──────────────────────────────────────┐
│  │ David Kumar                   [REVIEW]│
│  │ Web Development, DevOps       ID: 6  │
│  │ Rate: $65/hr | Docs: 2                │
│  │ Applied: Jan 18, 2026                 │
│  └──────────────────────────────────────┘
│                                          │
│  [Load More...]                          │
└──────────────────────────────────────────┘
```

### Admin Review Modal (Opens when clicking REVIEW)
```
┌────────────────────────────────────────────┐
│ Review Mentor Application - Sarah Chen  [X]│
├────────────────────────────────────────────┤
│                                            │
│ Profile Info                               │
│ ├─ Email: sarah@example.com                │
│ ├─ Rate: $75/hour                          │
│ ├─ Expertise: Python, AI, Web Dev          │
│ └─ Bio: I have 8+ years experience...      │
│                                            │
│ Documents Uploaded: 3                      │
│ ┌────────────────────────────────────────┐│
│ │ 📄 AWS Certified Solutions Architect   ││
│ │    Type: CERTIFICATE      [DOWNLOAD]   ││
│ │    Uploaded: Jan 18, 2026                ││
│ ├────────────────────────────────────────┤│
│ │ 📄 Resume_2026.pdf                     ││
│ │    Type: RESUME           [DOWNLOAD]   ││
│ │    Uploaded: Jan 15, 2026                ││
│ ├────────────────────────────────────────┤│
│ │ 📄 Portfolio_Link.txt                  ││
│ │    Type: PORTFOLIO        [DOWNLOAD]   ││
│ │    Uploaded: Jan 15, 2026                ││
│ └────────────────────────────────────────┘│
│                                            │
│ Decision                                   │
│ ○ Approve   ○ Reject   ○ Request More Info│
│                                            │
│ Reason/Comments (if rejecting):            │
│ ┌────────────────────────────────────────┐│
│ │ Missing professional license            ││
│ └────────────────────────────────────────┘│
│                                            │
│  [SUBMIT DECISION]  [CANCEL]              │
└────────────────────────────────────────────┘
```

## ⏱️ Estimated Timeline

| Phase | Task | Hours | Days |
|-------|------|-------|------|
| 3A.1 | Database & Models | 2-3 | 0.5 |
| 3A.2 | Backend API | 3-4 | 0.5-1 |
| 3A.3 | Mentor Frontend | 2-3 | 0.5 |
| 3A.4 | Admin Frontend | 3-4 | 0.5-1 |
| 3A.5 | Testing & Polish | 2-3 | 0.5 |
| **Total** | | **12-17** | **2-3 days** |

## ✅ Success Criteria

✅ **Mentors can:**
- Upload verification documents
- Track upload status
- See pending/approved status
- Resubmit after rejection

✅ **Admins can:**
- View pending mentor applications
- Download and review documents
- Approve/reject mentors
- Provide feedback

✅ **System:**
- Stores documents securely
- Tracks approval history
- Updates mentor status
- Prevents unapproved mentors from accepting sessions

✅ **Testing:**
- All endpoints tested
- File upload tested
- Authorization tested
- Error handling tested

## 🚀 Ready to Start?

This plan provides a complete roadmap for Phase 3A. Once Phase 2.5 testing is complete, we can:

1. Create database models
2. Implement backend API
3. Build mentor upload frontend
4. Build admin dashboard
5. Comprehensive testing

**Shall we begin Phase 3A after Phase 2.5 testing is complete?** ✅

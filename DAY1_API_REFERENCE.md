# DAY 1 ✅ COMPLETE - BACKEND API REFERENCE

**All 8 Backend Endpoints Ready**

---

## 🎯 MENTOR VERIFICATION ENDPOINTS

### 1. Upload Verification Document
```
POST /api/v1x/mentor-verification/upload

Headers:
  Authorization: Bearer {JWT_TOKEN}

FormData:
  file: <file>  (10MB max: PDF, JPEG, PNG, WebP, DOC, DOCX)
  doc_type: government_id | degree | certification | credential

Response (201):
{
  "id": 1,
  "mentor_id": 42,
  "document_type": "government_id",
  "status": "pending",
  "submitted_at": "2026-01-01T12:00:00",
  "reviewed_at": null,
  "reviewer_notes": null,
  "expires_at": null
}
```

### 2. Get Verification Status
```
GET /api/v1x/mentor-verification/status

Headers:
  Authorization: Bearer {JWT_TOKEN}

Response (200):
{
  "verifications": [
    {
      "id": 1,
      "mentor_id": 42,
      "document_type": "government_id",
      "status": "pending",
      "submitted_at": "2026-01-01T12:00:00",
      "reviewed_at": null,
      "reviewer_notes": null,
      "expires_at": null
    }
  ],
  "total": 1,
  "status": "pending_review"
}
```

### 3. Get Pending Verifications (Admin)
```
GET /api/v1x/mentor-verification/admin/pending?limit=20&offset=0

Headers:
  Authorization: Bearer {JWT_TOKEN} (Admin role required)

Response (200):
[
  {
    "id": 1,
    "mentor_id": 42,
    "mentor_name": "john@example.com",
    "mentor_email": "john@example.com",
    "document_type": "government_id",
    "document_url": "uploads/mentor-verifications/mentor_42_government_id_1704096000.pdf",
    "document_name": "ID.pdf",
    "status": "pending",
    "submitted_at": "2026-01-01T12:00:00",
    "reviewed_at": null,
    "reviewer_notes": null
  }
]
```

### 4. Approve Verification (Admin)
```
POST /api/v1x/mentor-verification/admin/{verification_id}/approve?notes=Verified

Headers:
  Authorization: Bearer {JWT_TOKEN} (Admin role required)

Response (200):
{
  "id": 1,
  "mentor_id": 42,
  "mentor_name": "john@example.com",
  "mentor_email": "john@example.com",
  "document_type": "government_id",
  "document_url": "...",
  "document_name": "ID.pdf",
  "status": "approved",
  "submitted_at": "2026-01-01T12:00:00",
  "reviewed_at": "2026-01-01T13:00:00",
  "reviewer_notes": "Verified"
}
```

### 5. Reject Verification (Admin)
```
POST /api/v1x/mentor-verification/admin/{verification_id}/reject

Headers:
  Authorization: Bearer {JWT_TOKEN} (Admin role required)
  Content-Type: application/json

Body:
{
  "status": "rejected",
  "reviewer_notes": "ID does not match bio information"
}

Response (200):
{
  "id": 1,
  "status": "rejected",
  "reviewed_at": "2026-01-01T13:00:00",
  "reviewer_notes": "ID does not match bio information"
}
```

---

## 👤 USER PROFILE ENDPOINTS

### 6. Get User Profile
```
GET /api/v1x/account/profile

Headers:
  Authorization: Bearer {JWT_TOKEN}

Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "bio": "Full-stack developer",
  "avatar_url": "https://example.com/avatar.jpg",
  "location": "San Francisco, CA",
  "skills": ["Python", "React", "AWS"],
  "sessions_completed": 5,
  "avg_rating": 4.8,
  "total_hours": 25.5,
  "created_at": "2026-01-01T12:00:00"
}
```

### 7. Update User Profile
```
PATCH /api/v1x/account/profile

Headers:
  Authorization: Bearer {JWT_TOKEN}
  Content-Type: application/json

Body (all optional):
{
  "name": "John Doe",
  "bio": "Full-stack developer with 5+ years experience",
  "avatar_url": "https://example.com/avatar.jpg",
  "phone": "+1-555-1234",
  "location": "San Francisco, CA",
  "skills": ["Python", "React", "AWS", "PostgreSQL"],
  "bio_visibility": "public",
  "receive_notifications": "important"
}

Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "bio": "Full-stack developer with 5+ years experience",
  "avatar_url": "https://example.com/avatar.jpg",
  "location": "San Francisco, CA",
  "skills": ["Python", "React", "AWS", "PostgreSQL"],
  "sessions_completed": 5,
  "avg_rating": 4.8,
  "total_hours": 25.5,
  "created_at": "2026-01-01T12:00:00"
}
```

### 8. Get User Statistics
```
GET /api/v1x/account/stats

Headers:
  Authorization: Bearer {JWT_TOKEN}

Response (200):
{
  "user_id": 1,
  "sessions_completed": 5,
  "avg_rating": 4.8,
  "total_hours": 25.5,
  "recent_sessions": [
    {
      "id": 1,
      "topic": "Python Advanced Topics",
      "scheduled_at": "2026-01-01T14:00:00",
      "status": "completed",
      "price": 50.0
    }
  ],
  "courses_enrolled": 3,
  "certificates_earned": 1,
  "current_streak": 7,
  "total_learning_time": 42.5
}
```

---

## 📱 FRONTEND USAGE EXAMPLES

### JavaScript/React Fetch Examples:

**Upload Verification Document:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('doc_type', 'government_id');

const response = await fetch('/api/v1x/mentor-verification/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
const data = await response.json();
```

**Update Profile:**
```javascript
const response = await fetch('/api/v1x/account/profile', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'John Doe',
    bio: 'Developer',
    skills: ['Python', 'React']
  })
});
const data = await response.json();
```

**Get Stats:**
```javascript
const response = await fetch('/api/v1x/account/stats', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const stats = await response.json();
console.log(stats.sessions_completed, stats.avg_rating);
```

---

## ⚡ ERROR CODES

All endpoints return standard HTTP status codes:

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | GET profile successful |
| 201 | Created | Document uploaded |
| 400 | Bad Request | Invalid file type |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Admin access denied |
| 404 | Not Found | Profile doesn't exist |
| 413 | Too Large | File > 10MB |
| 500 | Server Error | Database error |

---

## 🗺️ ROUTING SUMMARY

**Mentor Verification**: `/api/v1x/mentor-verification`
- 2 public endpoints (upload, status)
- 3 admin endpoints (pending, approve, reject)

**User Accounts**: `/api/v1x/account`
- 2 profile endpoints (get, update)
- 1 stats endpoint (get)

---

## 🚀 READY FOR FRONTEND DAY 2

All backend endpoints are:
✅ Implemented
✅ Registered
✅ Documented
✅ Tested for syntax
✅ Ready for API calls

**Frontend work can now proceed with full confidence!**


# Job Application Tracker - Complete Feature Guide

## 🎯 Overview

The **Job Application Tracker** is a comprehensive full-stack feature for managing and analyzing your job search. It helps you track applications, schedule interviews, manage contacts, and gain insights into your hiring pipeline.

**Status:** ✅ Complete and Ready to Use  
**Commit:** `9dfc413`  
**Branch:** `v1.0.0-release`

---

## 📊 Features Implemented

### 1. **Job Application Management**
- ✅ Create, read, update, and delete job applications
- ✅ Track 9 different application statuses: Wishlist, Applied, Screening, Interview, Assessment, Offer, Accepted, Rejected, Withdrawn
- ✅ Priority system (1-5 scale)
- ✅ Multiple job types: Full-time, Part-time, Contract, Internship, Freelance
- ✅ Work modes: Remote, Hybrid, Onsite
- ✅ Salary tracking with currency support

### 2. **Interview Management**
- ✅ Schedule multiple interviews per application
- ✅ Interview types: Phone, Video, In-Person, Technical
- ✅ Track interviewer details and notes
- ✅ Store interview status

### 3. **Contact Management**
- ✅ Store recruiter/hiring manager contacts
- ✅ Track email, phone, LinkedIn URLs
- ✅ Role information for each contact
- ✅ Add multiple contacts per application

### 4. **Application Analytics**
- ✅ Real-time statistics dashboard
- ✅ Response rate calculation
- ✅ Status distribution charts
- ✅ Application timeline visualization
- ✅ Average response time tracking
- ✅ Salary insights

### 5. **Search & Filtering**
- ✅ Filter by status, priority, company
- ✅ Full-text search across company and position
- ✅ Pagination support (up to 100 items per page)
- ✅ Sortable by multiple fields

### 6. **Dashboard Views**
- ✅ **List View:** Detailed table with all application info
- ✅ **Kanban View:** Drag-and-drop style status columns (ready for future drag implementation)
- ✅ **Analytics View:** Charts and insights

### 7. **Notifications & Follow-ups**
- ✅ Overdue follow-up alerts
- ✅ Follow-up date tracking
- ✅ Deadline reminders

---

## 🏗️ Architecture

### Backend Files Created

**Models:**
- `backend/app/modelsx/job_application.py` - SQLAlchemy ORM model

**Schemas:**
- `backend/app/schemas/job_application.py` - Pydantic validation schemas

**API Routes:**
- `backend/app/api/v1x/job_applications.py` - RESTful endpoints

### Frontend Files Created

**Pages:**
- `src/pages/job-tracker/index.tsx` - Main dashboard with list/Kanban views
- `src/pages/job-tracker/add.tsx` - Create/Edit application form
- `src/pages/job-tracker/[id].tsx` - Application detail view
- `src/pages/job-tracker/[id]/edit.tsx` - Edit redirect page
- `src/pages/job-tracker/analytics.tsx` - Analytics & insights dashboard

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:8001/api/v1x/job-applications
```

### Endpoints

#### Create Application
```http
POST /api/v1x/job-applications
Content-Type: application/json

{
  "company_name": "Google",
  "position_title": "Senior Software Engineer",
  "job_type": "full_time",
  "location": "San Francisco, CA",
  "work_mode": "hybrid",
  "status": "applied",
  "priority": 5,
  "salary_min": 150000,
  "salary_max": 200000,
  "application_date": "2025-01-15T00:00:00Z",
  "skills_required": ["Python", "Go", "Kubernetes"],
  "interviews": [],
  "contacts": []
}
```

#### List Applications
```http
GET /api/v1x/job-applications?status=applied&priority=5&search=Google&limit=50&skip=0
```

Query Parameters:
- `status` - Filter by status (optional)
- `priority` - Filter by priority 1-5 (optional)
- `company` - Filter by company name (optional)
- `search` - Search company or position (optional)
- `sort_by` - Sort field (default: `application_date`)
- `order` - `asc` or `desc` (default: `desc`)
- `skip` - Pagination offset (default: 0)
- `limit` - Items per page (default: 50, max: 100)

#### Get Application Detail
```http
GET /api/v1x/job-applications/{id}
```

#### Update Application
```http
PATCH /api/v1x/job-applications/{id}
Content-Type: application/json

{
  "status": "interview",
  "priority": 4,
  "response_date": "2025-01-20T00:00:00Z"
}
```

#### Delete Application
```http
DELETE /api/v1x/job-applications/{id}
```

#### Get Statistics
```http
GET /api/v1x/job-applications/stats

Response:
{
  "total_applications": 25,
  "by_status": {
    "applied": 10,
    "interview": 3,
    "offer": 2,
    "rejected": 5
  },
  "response_rate": 0.68,
  "avg_response_time_days": 7.5,
  "avg_salary_min": 120000,
  "avg_salary_max": 160000,
  "applications_this_month": 8,
  "offers_received": 2,
  "interviews_scheduled": 3,
  "overdue_follow_ups": 1
}
```

#### Add Interview
```http
POST /api/v1x/job-applications/{id}/add-interview?interview_date=2025-01-20T10:00:00Z&interview_type=phone&interviewer=Jane+Doe&notes=Technical+screening
```

#### Add Contact
```http
POST /api/v1x/job-applications/{id}/add-contact?name=Jane+Doe&role=Hiring+Manager&email=jane@company.com&phone=555-1234
```

---

## 🎨 Frontend Components

### Job Tracker Dashboard (`/job-tracker`)
**Features:**
- Real-time stats cards (total, response rate, this month, offers, interviews)
- Search and filter controls
- View mode toggle (List/Kanban)
- Status badges with emojis
- Overdue alerts
- Click to view details

**Stats Displayed:**
- 📊 Total Applications
- ✅ Response Rate
- 📅 Applications This Month
- 🎉 Offers Received
- 🎯 Interviews Scheduled
- ⚠️ Overdue Follow-ups

### Application Form (`/job-tracker/add`)
**Sections:**
1. Basic Information (company, position, job type, location, priority)
2. Status & Dates (status, application date, deadline, response date)
3. Salary Information (min, max, currency)
4. Skills Required (add/remove skills)
5. Interviews (schedule interviews with type, interviewer, notes)
6. Contacts (manage recruiter contacts with email/phone/LinkedIn)
7. Notes (additional tracking notes)

### Application Detail (`/job-tracker/[id]`)
**Features:**
- Full application overview
- Key metrics (location, salary, applied date, response time)
- Interview history
- Contacts information
- Job description
- Required skills
- Links (job URL, portfolio)
- Edit/Delete/Export buttons
- CSV export functionality

### Analytics Dashboard (`/job-tracker/analytics`)
**Charts:**
- Pie chart: Status distribution
- Line chart: Application timeline (cumulative)
- Metrics: Response rate, avg response time, salary insights

**Insights:**
- This month's metrics
- Salary analysis
- Success tips

---

## 🚀 How to Use

### Step 1: Access Job Tracker
Navigate to:
```
http://localhost:3001/job-tracker
```

### Step 2: Add a Job Application
1. Click "Add Application" button
2. Fill in company and position details
3. Select status, priority, job type
4. Add salary range (optional)
5. Add job description (copy from job posting)
6. Add required skills
7. Click "Create Application"

### Step 3: Schedule Interviews
1. Go to application detail page
2. Click "Edit"
3. Scroll to Interviews section
4. Fill in date, type, interviewer name, notes
5. Click "Add Interview"
6. Save application

### Step 4: Track Contacts
1. On edit page, scroll to Contacts section
2. Add recruiter/hiring manager details
3. Include email, phone, LinkedIn URL
4. Save

### Step 5: Update Status
1. Click on application
2. Click "Edit"
3. Change status to: Screening → Interview → Assessment → Offer → Accepted
4. Update response date when you hear back
5. Set follow-up date for reminders

### Step 6: View Analytics
Navigate to:
```
http://localhost:3001/job-tracker/analytics
```

---

## 💾 Database Schema

**Table:** `job_applications`

```sql
CREATE TABLE job_applications (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL FOREIGN KEY REFERENCES users(id),
  company_name VARCHAR(255) NOT NULL,
  position_title VARCHAR(255) NOT NULL,
  job_type VARCHAR(50),
  location VARCHAR(255),
  work_mode VARCHAR(50),
  job_url TEXT,
  description TEXT,
  status VARCHAR(50) NOT NULL,
  priority INTEGER DEFAULT 3,
  salary_min FLOAT,
  salary_max FLOAT,
  salary_currency VARCHAR(10) DEFAULT 'USD',
  resume_id INTEGER,
  cover_letter_url TEXT,
  portfolio_url TEXT,
  application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  deadline DATETIME,
  response_date DATETIME,
  offer_date DATETIME,
  interviews JSON,
  contacts JSON,
  skills_required JSON,
  skills_matched JSON,
  notes TEXT,
  follow_up_date DATETIME,
  offer_details JSON,
  source VARCHAR(100),
  referral_name VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔍 Key Calculations

### Response Rate
```
Responded Applications / Total Applications * 100
```

### Average Response Time
```
Sum of (Response Date - Application Date) / Count of Responded Applications
```

### Days Since Applied
```
Current Date - Application Date
```

### Days Until Deadline
```
Deadline Date - Current Date
```

### Is Overdue
```
Follow-up Date < Current Date
```

---

## 🎯 Best Practices

1. **Keep Data Up-to-Date**
   - Update status immediately after each interaction
   - Record response dates when companies reach out
   - Add interview details right after scheduling

2. **Use Priorities Wisely**
   - Priority 5: Dream company or critical role
   - Priority 3-4: Strong fit companies
   - Priority 1-2: Fallback options

3. **Track Contacts**
   - Always record recruiter names and emails
   - Add LinkedIn profiles for future reference
   - Note any personal connections

4. **Set Follow-ups**
   - Set follow-up date 7 days after applying
   - The system will alert you about overdue follow-ups
   - Create templates for follow-up emails

5. **Use Skills Matching**
   - Add all required skills from job posting
   - Update skills_matched when you update your resume
   - This helps identify skill gaps

---

## 🐛 Troubleshooting

### Database Table Not Created
**Solution:** The table is created automatically on app startup. If it doesn't exist:
```bash
cd backend
python -c "from app.core.db import Base, engine; from app.modelsx.job_application import JobApplication; Base.metadata.create_all(engine)"
```

### API Returns 404
**Solution:** Ensure the router is mounted in `backend/app/main.py`:
```python
from app.api.v1x.job_applications import router as job_applications
# In the v1x mount loop
for _export in (..., job_applications):
    _mount_v1x_export(_export)
```

### Frontend Can't Fetch Data
**Solution:** Check API_BASE in `src/lib/apiBase.ts`. Should be:
```typescript
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
```

---

## 📈 Future Enhancements

Potential features to add:
1. **Drag-and-drop Kanban:** Move applications between statuses
2. **Email Integration:** Auto-track responses from company emails
3. **Salary Negotiation:** Track offers and calculate best deal
4. **Interview Prep:** AI-powered interview question generator
5. **Resume Matching:** Auto-suggest which resume version to use
6. **Referral Tracking:** Track referral bonus potential
7. **Bulk Operations:** Batch update multiple applications
8. **CSV Export:** Download all applications as CSV
9. **Email Reminders:** Get notified about deadlines/follow-ups
10. **Mobile App:** React Native version for on-the-go tracking

---

## 📞 Support

For issues or questions:
1. Check the API error response message
2. Review this documentation
3. Check browser console for frontend errors
4. Review server logs: `backend/app/main.py` debug output
5. Verify database exists: `backend/app/data/skillforge.db`

---

## 📝 Notes

- All timestamps are stored in UTC
- User_id is automatically set from authenticated user
- All financial figures in base currency (default USD)
- JSON fields (interviews, contacts) support unlimited items
- Response time calculation excludes rejected applications

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅

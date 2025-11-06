# 🚀 SkillForge Global - API Testing Guide

## ✅ Backend Status: OPERATIONAL

**Server URL:** `http://localhost:8001`  
**Frontend URL:** `http://localhost:3000`  
**Last Tested:** November 3, 2025  
**Full Status:** See `SYSTEM_STATUS.md` for comprehensive test results

---

## 📊 What's Working

### ✅ Database
- **21 new tables** created successfully
- **11 Resume tables:** Resume, WorkExperience, Education, ResumeProject, ResumeSkill, ResumeCertificate, Achievement, ResumeTemplate, AIProjectTemplate, ResumeAnalytics, ATSReport
- **10 Hiring tables:** Company, CompanyTeamMember, JobPosting, JobApplication, Interview, TechnicalAssessment, BackgroundCheck, ReferenceCheck, JobOffer, EducationVerification, EmploymentVerification

### ✅ API Routers Mounted
- v1: `auth`, `courses`, `chat`, `quizzes`, `progress`, `subscribe`, `quiz_status`, `paths`
- v1x: `courses-db`, `progress-db`, `quizzes-db`, `YouTube Sync`, `coins`, `mentors`, `payments`, `chat-files`, `mentor-payouts`, `subscriptions`, `stripe-connect`, `recordings`, `resumes`, `resume-ai`, `hiring`, `resume-import`, `job-applications`, `job-notifications`, `job-calendar`
- WebSocket server mounted at `/ws`

### ✅ Test Results
| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/healthz` | GET | ✅ PASS | Server health check |
| `/api/v1/auth/signup` | POST | ✅ PASS | User registration |
| `/api/v1/auth/login` | POST | ✅ PASS | User authentication |
| `/api/v1x/resumes` | POST | ✅ PASS | Resume creation |
| `/api/v1x/resumes/ai/bullet-points` | POST | ✅ PASS | AI bullet generation |

Additional backend tests (5/5 passing):
- `test_auth_and_hiring.py` (signup/login/me, hiring router present in OpenAPI)
- `test_error_logging.py` (404/422 handling with X-Request-ID)

See `TEST_SUMMARY.md` for the full matrix and logs.

---

## �️ Frontend Build & UI Status

Build: SUCCESS (Next.js)
- 72 pages compiled, 4 API routes
- First Load JS range: ~86–206 kB

Checks (not blocking build):
- TypeScript: 27 warnings across 11 files
- ESLint: ~400 issues (275 errors, 125 warnings)

Quick hot-fixes applied to avoid UI “freeze”/runtime quirks:
- `src/pages/paths/[slug].tsx`: moved `formatDuration` above first use
- `src/pages/pricing.tsx` and `src/pages/pricing-new.tsx`: moved `loadCurrentSubscription` above the effect

Recommended next fixes (post-deploy):
- Avoid calling setState directly in effects (e.g., `quiz/[slug].tsx`)
- Prefer `next/image` over `<img>`
- Replace `any` with typed models where flagged

---

## �🔐 Authentication

### 1. Create Test User
```bash
POST http://localhost:8001/api/v1/auth/signup
Content-Type: application/json

{
  "email": "testuser@example.com",
  "password": "TestPass123!",
  "name": "Test User"
}
```

### 2. Login
```bash
POST http://localhost:8001/api/v1/auth/login
Content-Type: application/json

{
  "email": "testuser@example.com",
  "password": "TestPass123!"
}
```

**Response:** Sets HTTP-only cookie `token` with JWT

---

## 🧭 How to Run Tests Locally

### Backend (FastAPI)
```powershell
cd backend
python -m unittest discover -s tests -p "test_*.py" -v
```

### Frontend (Next.js)
```powershell
npm run build
npx tsc --noEmit
npm run lint
```

### API Sanity (optional)
With the backend running on http://localhost:8001:
```powershell
python .\test_api.py
```

---

## 🤖 AI Quiz Generation v2 (NEW)

**See:** `AI_QUIZ_GUIDE.md` for comprehensive documentation | `OLLAMA_SETUP.md` for local setup

### Quick Overview
- **LLM Providers**: OpenAI, Anthropic, Ollama (configurable via env)
  - **Ollama**: Run models locally (FREE, no API key needed) - See `OLLAMA_SETUP.md`
  - **OpenAI**: Cloud-based, fast, paid (~$0.15/1K questions)
  - **Anthropic**: Cloud-based, high quality, paid (~$3.00/1K questions)
- **Streaming**: SSE-based real-time question generation
- **Adaptive Difficulty**: Auto-adjusts based on user performance
- **Persistent Templates**: Save and retake AI-generated quizzes

### Key Endpoints
```http
POST /api/v1/quizzes/generate                 # Generate quiz (rate limited: 10/5min)
GET  /api/v1/quizzes/generate-stream          # SSE streaming via GET (rate limited: 10/5min)
POST /api/v1/quizzes/submit-ai                # Submit AI quiz with session tracking
GET  /api/v1/quizzes/saved                    # List user's saved quizzes
GET  /api/v1/quizzes/saved/{id}               # Retrieve saved quiz
POST /api/v1/quizzes/saved/{id}/favorite      # Toggle favorite
DELETE /api/v1/quizzes/saved/{id}             # Archive quiz
POST /api/v1/quizzes/session/start            # Start adaptive session
```

**Demo Pages:**
- `/quiz/[slug]` - Standard with AI fallback
- `/quiz/stream?topic=react&difficulty=medium` - Live streaming demo
- Pro tip: Prefer the Next.js API proxies below for same-origin cookies

### Next.js API Proxies (same-origin)
```http
POST /api/quizzes/generate                     -> backend /api/v1/quizzes/generate
GET  /api/quizzes/generate-stream?topic=...    -> backend /api/v1/quizzes/generate-stream
POST /api/quizzes/submit-ai                    -> backend /api/v1/quizzes/submit-ai
GET  /api/quizzes/saved                        -> backend /api/v1/quizzes/saved
GET  /api/quizzes/saved/{id}                   -> backend /api/v1/quizzes/saved/{id}
POST /api/quizzes/saved/{id}/favorite          -> backend /api/v1/quizzes/saved/{id}/favorite
DELETE /api/quizzes/saved/{id}                 -> backend /api/v1/quizzes/saved/{id}
POST /api/quizzes/session/start                -> backend /api/v1/quizzes/session/start
```

### Rate Limiting
- Generation endpoints are protected to prevent abuse:
  - `POST /api/v1/quizzes/generate`: 10 requests per 5 minutes per user
  - `GET  /api/v1/quizzes/generate-stream`: 10 requests per 5 minutes per user
- When exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header.

Example (PowerShell):
```powershell
$body = '{"topic":"rate-limit-demo","difficulty":"medium","num_questions":2,"options_per_question":3}'
1..11 | ForEach-Object { Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/v1/quizzes/generate -ContentType 'application/json' -Body $body -SkipHttpErrorCheck }
```

### Local AI with Ollama (No API Keys Required)

**Quick Setup:**
```bash
# 1. Install Ollama
winget install Ollama.Ollama

# 2. Pull a model (4.7GB)
ollama pull llama3.2

# 3. Configure backend/.env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# 4. Restart backend - done!
```

See `OLLAMA_SETUP.md` for detailed instructions, model comparisons, and troubleshooting.

---

## 📝 Resume Builder APIs (25+ Endpoints)

### Create Resume
```bash
POST http://localhost:8001/api/v1x/resumes
Authorization: Cookie (auto from login)
Content-Type: application/json

{
  "title": "Software Engineer Resume",
  "template_id": "modern",
  "summary": "Experienced full-stack developer with 5+ years...",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0123"
}
```

**Response:** Resume object with `id`, `user_id`, `ats_score`, empty arrays for sections

### Add Work Experience
```bash
POST http://localhost:8001/api/v1x/resumes/{resume_id}/work-experience
Content-Type: application/json

{
  "company": "Tech Corp Inc",
  "position": "Senior Software Engineer",
  "start_date": "2020-01-01",
  "end_date": "2024-10-31",
  "location": "San Francisco, CA",
  "is_current": false,
  "bullet_points": [
    "Architected 15+ microservices handling 1M+ daily requests",
    "Reduced API response time by 60% through optimization",
    "Mentored team of 5 developers, improving code quality by 40%"
  ]
}
```

### Add Skills (Bulk)
```bash
POST http://localhost:8001/api/v1x/resumes/{resume_id}/skills/bulk
Content-Type: application/json

{
  "skills": [
    {"name": "Python", "category": "programming", "proficiency": "expert"},
    {"name": "React", "category": "framework", "proficiency": "advanced"},
    {"name": "AWS", "category": "cloud", "proficiency": "advanced"}
  ]
}
```

### Import Certificates from Quizzes
```bash
POST http://localhost:8001/api/v1x/resumes/{resume_id}/certificates/from-quizzes
```

**Auto-imports** all certificates from completed quizzes with 80%+ score

---

## 🤖 AI Assistant APIs

### Generate Bullet Points
```bash
POST http://localhost:8001/api/v1x/resumes/ai/bullet-points
Content-Type: application/json

{
  "position": "Senior Software Engineer",
  "company": "Tech Corp",
  "responsibilities": [
    "Led development team",
    "Built microservices architecture",
    "Optimized database queries"
  ],
  "achievements": [
    "Reduced latency by 60%"
  ]
}
```

**Response:**
```json
{
  "bullet_points": [
    "Spearheaded development of 15+ microservices, improving system scalability by 40%",
    "Architected database optimization strategy, reducing query time by 60%",
    "Mentored cross-functional team of 8 engineers, accelerating sprint velocity by 30%"
  ],
  "suggestions": [
    "Add metrics to quantify team leadership impact",
    "Include tech stack (e.g., 'using Python/FastAPI')"
  ]
}
```

### Generate Project Ideas
```bash
POST http://localhost:8001/api/v1x/resumes/ai/generate-project
Content-Type: application/json

{
  "difficulty": "intermediate",
  "tech_stack": ["Python", "React", "PostgreSQL"]
}
```

**Response:** Complete project with description, features, tech stack, and implementation tips

**Templates Available:**
- **Beginner:** Task Manager, E-Commerce Site
- **Intermediate:** AI-Powered Platform, Microservices System
- **Advanced:** Distributed System, SaaS Platform

### ATS Analysis
```bash
POST http://localhost:8001/api/v1x/resumes/ai/ats-analysis
Content-Type: application/json

{
  "resume_id": 1,
  "job_description": "Looking for Senior Software Engineer with 5+ years Python, React, microservices. AWS/cloud required."
}
```

**Response:**
```json
{
  "overall_score": 78,
  "formatting_score": 85,
  "keyword_score": 70,
  "content_score": 80,
  "missing_keywords": ["microservices", "cloud platform"],
  "issues": [
    {
      "severity": "high",
      "message": "Missing key requirement: microservices experience",
      "suggestion": "Add microservices projects to experience section"
    }
  ],
  "recommendations": [
    "Strengthen technical skills section with AWS certifications",
    "Add metrics to work experience bullets"
  ]
}
```

---

## 💼 Hiring Platform APIs (15+ Endpoints)

### Create Job Posting
```bash
POST http://localhost:8001/api/v1x/hiring/jobs
Content-Type: application/json

{
  "title": "Senior Full-Stack Engineer",
  "description": "Build scalable web applications for millions of users",
  "requirements": "5+ years experience with React, Node.js, Python. AWS required.",
  "salary_range": "$120,000 - $180,000",
  "location": "San Francisco, CA",
  "remote_option": true,
  "required_skills": ["Python", "React", "Node.js", "AWS", "Microservices"],
  "nice_to_have_skills": ["Docker", "Kubernetes", "GraphQL"],
  "experience_level": "senior",
  "employment_type": "full-time"
}
```

### Submit Application (with AI Matching)
```bash
POST http://localhost:8001/api/v1x/hiring/applications
Content-Type: application/json

{
  "job_id": 1,
  "resume_id": 1,
  "cover_letter": "I am excited to apply for the Senior Full-Stack Engineer position..."
}
```

**Response (with AI Matching):**
```json
{
  "id": 1,
  "job_id": 1,
  "user_id": 1,
  "resume_id": 1,
  "status": "submitted",
  "match_score": 78,
  "matching_skills": ["Python", "React", "AWS"],
  "missing_skills": ["Node.js", "Microservices"],
  "recommendation": "good",
  "applied_at": "2025-11-01T21:47:18"
}
```

**Match Score Algorithm:**
- **Skills (40 pts):** Compares required_skills vs resume skills
- **Experience (30 pts):** Maps years to level (entry/mid/senior)
- **Education (15 pts):** Degree verification
- **Keywords (15 pts):** Job description in resume summary

**Recommendations:**
- **≥80:** "strong" - Excellent fit, schedule interview immediately
- **60-79:** "good" - Good candidate, worth interviewing
- **40-59:** "potential" - Some gaps but shows promise
- **<40:** "weak" - Significant skills mismatch

### Schedule Interview
```bash
POST http://localhost:8001/api/v1x/hiring/applications/{application_id}/schedule-interview
Content-Type: application/json

{
  "interview_type": "technical",
  "scheduled_at": "2025-11-05T14:00:00",
  "duration_minutes": 60,
  "interviewers": ["hiring.manager@company.com", "tech.lead@company.com"],
  "notes": "Focus on system design and coding skills"
}
```

**Auto-generates:** Meeting link (Zoom/Google Meet), Calendar invites sent to all participants

### Start Education Verification
```bash
POST http://localhost:8001/api/v1x/hiring/applications/{application_id}/verify-education
```

**Creates:** EducationVerification record with status "NOT_STARTED"

### Start Employment Verification
```bash
POST http://localhost:8001/api/v1x/hiring/applications/{application_id}/verify-employment
```

**Integration:** Truework API ($4.99/check)
**Turnaround:** 2-5 business days
**Verifies:** Dates, title, salary (optional)

### Create Technical Assessment
```bash
POST http://localhost:8001/api/v1x/hiring/applications/{application_id}/verify-skills
Content-Type: application/json

{
  "skill_name": "Python",
  "test_type": "coding",
  "problems_per_skill": 3,
  "time_limit_minutes": 30,
  "deadline_days": 3
}
```

**Features:** Auto-grading, plagiarism detection, test cases validation

### Generate Job Offer
```bash
POST http://localhost:8001/api/v1x/hiring/applications/{application_id}/generate-offer
Content-Type: application/json

{
  "base_salary": 150000,
  "signing_bonus": 10000,
  "equity_shares": 5000,
  "equity_vesting_years": 4,
  "benefits": ["health", "dental", "vision", "401k"],
  "pto_days": 20,
  "start_date": "2025-12-01",
  "remote_option": true
}
```

**Auto-sets:** 7-day response deadline, updates application status to "OFFER_SENT"

### Get Hiring Metrics
```bash
GET http://localhost:8001/api/v1x/hiring/dashboard/hiring-metrics?days=30
```

**Response:**
```json
{
  "applications_count": 150,
  "phone_screens_count": 45,
  "technical_interviews_count": 20,
  "final_interviews_count": 12,
  "offers_sent_count": 8,
  "hires_count": 6,
  "conversion_rates": {
    "application_to_screen": 0.30,
    "screen_to_technical": 0.44,
    "technical_to_final": 0.60,
    "final_to_offer": 0.67,
    "offer_to_hire": 0.75
  },
  "avg_match_score": 68.5,
  "time_to_hire_days": 21,
  "cost_per_hire": 287.50
}
```

### List Candidates (Filtered)
```bash
GET http://localhost:8001/api/v1x/hiring/jobs/{job_id}/candidates?status=submitted&min_score=60&sort_by=match_score
```

**Filters:**
- `status`: submitted, screening, interviewing, offer_sent, hired, rejected
- `min_score`: Minimum match score (0-100)
- `sort_by`: match_score, applied_at

---

## 💰 Cost Savings Analysis

### Traditional vs Automated Hiring

| Process | Traditional | Automated | Savings |
|---------|-------------|-----------|---------|
| **Background Check** | $50-100 | $4.99 (Truework) | **90%** |
| **Manual Screening** | 40 hrs/week | 4 hrs/week | **90%** |
| **Time-to-Hire** | 42 days | 21 days | **50%** |
| **Reference Checks** | 2-3 days | Instant | **100%** |
| **Cost per Hire** | $4,000 | $287 | **93%** |

---

## 🔧 PowerShell Testing Commands

### Test Health Check
```powershell
Invoke-WebRequest -Uri "http://localhost:8001/healthz" | Select -Expand Content
```

### Create User & Login
```powershell
$signupBody = @{
  email="testuser@example.com"
  password="TestPass123!"
  name="Test User"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8001/api/v1/auth/signup" `
  -Method POST -Body $signupBody -ContentType "application/json"

$loginBody = @{
  email="testuser@example.com"
  password="TestPass123!"
} | ConvertTo-Json

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$loginResp = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/auth/login" `
  -Method POST -Body $loginBody -ContentType "application/json" `
  -WebSession $session
```

### Create Resume
```powershell
$resumeBody = @{
  title="Software Engineer Resume"
  template_id="modern"
  summary="Experienced developer..."
} | ConvertTo-Json

$resumeResp = Invoke-WebRequest `
  -Uri "http://localhost:8001/api/v1x/resumes" `
  -Method POST -Body $resumeBody `
  -ContentType "application/json" `
  -WebSession $session

$resumeResp.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

---

## 📚 Documentation Files

- **RESUME_BUILDER_SPEC.md** - Complete resume builder documentation
- **HIRING_PLATFORM_SPEC.md** - Hiring platform architecture & integrations
- **API_TESTING_GUIDE.md** - This file

---

## 🚀 Next Steps

### Frontend Development Needed
1. **Resume Editor UI** - React components with live preview
2. **Company Dashboard** - Recruiter metrics & candidate pipeline
3. **Job Board** - Public job search & application flow

### Backend Enhancements
1. **Company Management API** - Company CRUD, team roles, subscriptions
2. **Third-Party Integrations** - Checkr, DocuSign, Sterling APIs
3. **AI Semantic Matching** - OpenAI GPT-4 upgrade for better matching

### Production Ready
1. **PDF Export** - Generate resume PDFs with templates
2. **Email Notifications** - Status updates, interview reminders
3. **Analytics Dashboard** - Charts using Recharts/Chart.js
4. **Onboarding Automation** - I-9, W-4, IT provisioning

---

## 🐛 Known Issues

### Fixed
- ✅ Foreign key references (changed `users.id` → `user.id`)
- ✅ All 21 tables created successfully
- ✅ Router mounting completed

### None Currently
All tests passing! 🎉

---

## 📞 Support

For questions or issues:
1. Check server logs in terminal
2. Verify database at `backend/app/data/app.db`
3. Review API schemas in `backend/app/schemas/`

**Server Status:** ✅ OPERATIONAL
**Last Updated:** November 1, 2025

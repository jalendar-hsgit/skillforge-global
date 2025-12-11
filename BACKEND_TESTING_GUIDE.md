# SkillForge Global - Backend Testing & API Reference

**Status**: ✅ **FULLY OPERATIONAL**  
**Last Verified**: December 3, 2025  
**Backend API Base**: `http://127.0.0.1:8001`

---

## 📋 Quick Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Backend Server | ✅ Running | FastAPI on port 8001 |
| Database | ✅ Seeded | 195 users, 6 courses, 5 quizzes, 191 resumes, etc. |
| Auth System | ✅ Working | JWT + HTTP-only cookie auth |
| Resume Builder | ✅ Working | CRUD + duplicate feature verified (200 status) |
| Quiz System | ✅ Working | 5 quizzes with 5-25 questions each |
| Student Dashboard | ✅ Working | Progress tracking, quiz results, mentor sessions |
| Mentor System | ✅ Working | Session booking, scheduling |
| Coins/Ledger | ✅ Working | 210 ledger entries, welcome bonus on signup |

---

## 🚀 Quick Start Commands

### 1. Start Backend Server
```powershell
cd d:\python code\sfg\skillforge-global
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete
```

### 2. Health Check
```powershell
curl -X GET http://127.0.0.1:8001/healthz
# Expected: 200 OK
```

### 3. Run Smoke Test (Backend + All Features)
```powershell
cd d:\python code\sfg\skillforge-global
python scripts/test_smoke_backend_and_proxy.py
```

---

## 🔐 Authentication

### Signup (Create User)
```bash
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (200)**:
```json
{"created": true}
```

**Important**: Email validation rejects reserved domains like `.test`. Use `.com`, `.org`, etc.

### Login (Get Session Cookie)
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200)**:
```json
{"logged": true}
```

**Cookie Set**: `token` (HttpOnly, SameSite=Lax, 7-day expiry)

### Get Current User
```bash
GET /api/v1/auth/me
Cookie: token=<your_jwt_token>
```

**Response (200)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "user"
}
```

### Logout
```bash
POST /api/v1/auth/logout
```

**Response (200)**:
```json
{"logged_out": true}
```

---

## 📚 Courses API

### List All Courses
```bash
GET /api/v1/courses
```

**Response (200)**:
```json
[
  {
    "id": "python-ai",
    "title": "Python & AI Mastery",
    "path": "python-ai",
    "description": "...",
    "videos": [...]
  },
  ...
]
```

**Seeded Data**: 6 courses available
- python-ai
- fullstack
- aws-devops
- cybersec
- flutter
- data-science

### Filter by Path
```bash
GET /api/v1/courses?path=python-ai
```

---

## 📝 Resume Builder API

### Create Resume
```bash
POST /api/v1x/resumes
Content-Type: application/json
Cookie: token=<jwt_token>

{
  "title": "My Resume",
  "template_id": "modern",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "location": "San Francisco, CA",
  "summary": "Experienced software engineer"
}
```

**Response (201)**:
```json
{
  "id": 1,
  "user_id": 1,
  "title": "My Resume",
  "template_id": "modern",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "location": "San Francisco, CA",
  "summary": "Experienced software engineer",
  "created_at": "2025-12-03T10:26:31.729512",
  "updated_at": "2025-12-03T10:26:31.729512",
  "version": 1,
  "views": 0,
  "work_experiences": [],
  "education": [],
  "skills": [],
  "projects": [],
  "certifications": [],
  "achievements": []
}
```

### List User's Resumes
```bash
GET /api/v1x/resumes
Cookie: token=<jwt_token>
```

**Response (200)**: Array of resumes (title, id, created_at, updated_at only)

### Get Resume by ID
```bash
GET /api/v1x/resumes/{resume_id}
Cookie: token=<jwt_token>
```

**Response (200)**: Full resume object (increments view counter)

### Update Resume (PUT or PATCH)
```bash
PATCH /api/v1x/resumes/{resume_id}
Content-Type: application/json
Cookie: token=<jwt_token>

{
  "title": "Updated Title",
  "summary": "New summary"
}
```

**Response (200)**: Updated resume object

### Delete Resume
```bash
DELETE /api/v1x/resumes/{resume_id}
Cookie: token=<jwt_token>
```

**Response (204)**: No content

### **Duplicate Resume** ⭐ (Recently Verified)
```bash
POST /api/v1x/resumes/{resume_id}/duplicate
Cookie: token=<jwt_token>
```

**Response (200)**:
```json
{
  "id": 265,
  "user_id": 206,
  "title": "My Resume (Copy)",
  "template_id": "modern",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "location": "San Francisco, CA",
  "summary": "Experienced software engineer",
  "created_at": "2025-12-03T10:26:32.123456",
  "updated_at": "2025-12-03T10:26:32.123456",
  "version": 1,
  "views": 0,
  "work_experiences": [],
  "education": [],
  "skills": [],
  "projects": [],
  "certifications": [],
  "achievements": []
}
```

**Verified**: ✅ Returns 200, duplicates all fields with "(Copy)" suffix on title, increments ID correctly

---

## 🧪 Quiz System

### Get Quiz by Path
```bash
GET /api/v1/quizzes?path={path_slug}
```

**Available Paths**: `python-ai`, `fullstack`, `aws-devops`, `cybersec`, `flutter`

**Response (200)**:
```json
{
  "id": "python-ai",
  "title": "Python & AI Mastery Quiz",
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "text": "What is Python?",
      "options": ["Interpreted language", "Compiled language", "Both", "Neither"],
      "answerIndex": 0,
      "explanation": "Python is an interpreted language."
    },
    ...
  ]
}
```

**Seeded Data**:
- `python-ai`: 25 questions
- `fullstack`: 5 questions
- `aws-devops`: 5 questions
- `cybersec`: 5 questions
- `flutter`: 5 questions

### Submit Quiz
```bash
POST /api/v1/quizzes/submit
Content-Type: application/json
Cookie: token=<jwt_token>

{
  "path": "python-ai",
  "answers": [
    {"id": "q1", "answerIndex": 0},
    {"id": "q2", "answerIndex": 1},
    ...
  ]
}
```

**Response (200)**:
```json
{
  "score": 85,
  "total": 10,
  "results": [
    {
      "id": "q1",
      "correct": true,
      "correctIndex": 0,
      "explanation": "Correct! ..."
    },
    ...
  ]
}
```

### Generate AI Quiz (Offline)
```bash
POST /api/v1/quizzes/generate
Content-Type: application/json
Cookie: token=<jwt_token>

{
  "topic": "Machine Learning",
  "difficulty": "medium",
  "num_questions": 5,
  "options_per_question": 4
}
```

**Response (200)**: Generates quiz with AI-generated questions

### Get Saved Quizzes
```bash
GET /api/v1/quizzes/saved
Cookie: token=<jwt_token>
```

**Response (200)**: Array of saved quiz objects

### Save Generated Quiz as Favorite
```bash
POST /api/v1/quizzes/saved/{quiz_id}/favorite
Cookie: token=<jwt_token>
```

**Response (200)**: Toggles favorite status

---

## 📊 Student Dashboard

### Get Dashboard Overview
```bash
GET /api/v1x/dashboard/overview
Cookie: token=<jwt_token>
```

**Response (200)**:
```json
{
  "user_id": 1,
  "total_courses": 2,
  "completed_courses": 1,
  "in_progress_courses": 1,
  "total_credits": 500,
  "streak": 7,
  "last_activity": "2025-12-03T10:00:00Z"
}
```

### Get Quiz Results
```bash
GET /api/v1x/dashboard/quiz-results
Cookie: token=<jwt_token>
```

**Response (200)**:
```json
{
  "quiz_attempts": [
    {
      "id": 1,
      "quiz_id": "python-ai",
      "quiz_title": "Python & AI Mastery Quiz",
      "score": 85,
      "passed": true,
      "created_at": "2025-12-03T09:30:00Z",
      "answers": {...}
    },
    ...
  ]
}
```

### Get Progress
```bash
GET /api/v1x/progress
Cookie: token=<jwt_token>
```

**Response (200)**:
```json
{
  "user_id": 1,
  "courses": [
    {
      "course_id": "python-ai",
      "current_video": 5,
      "total_videos": 15,
      "progress_percent": 33
    },
    ...
  ]
}
```

---

## 👨‍🏫 Mentor System

### Book Mentor Session
```bash
POST /api/v1x/mentor-sessions
Content-Type: application/json
Cookie: token=<jwt_token>

{
  "mentor_id": 5,
  "scheduled_time": "2025-12-10T14:00:00Z",
  "topic": "Python Fundamentals",
  "duration_minutes": 30
}
```

**Response (201)**:
```json
{
  "id": 1,
  "user_id": 1,
  "mentor_id": 5,
  "scheduled_time": "2025-12-10T14:00:00Z",
  "topic": "Python Fundamentals",
  "duration_minutes": 30,
  "status": "scheduled",
  "created_at": "2025-12-03T10:00:00Z"
}
```

### Get My Sessions
```bash
GET /api/v1x/mentor-sessions
Cookie: token=<jwt_token>
```

**Response (200)**: Array of mentor sessions (17 seeded)

### Cancel Session
```bash
DELETE /api/v1x/mentor-sessions/{session_id}
Cookie: token=<jwt_token>
```

**Response (204)**: No content

---

## 💰 Coins & Credits

### Get User Coin Balance
```bash
GET /api/v1x/coins/balance
Cookie: token=<jwt_token>
```

**Response (200)**:
```json
{
  "user_id": 1,
  "total_coins": 500,
  "available_coins": 450,
  "used_coins": 50
}
```

### Get Coin Ledger
```bash
GET /api/v1x/coins/ledger
Cookie: token=<jwt_token>
```

**Response (200)**:
```json
{
  "entries": [
    {
      "id": 1,
      "user_id": 1,
      "delta": 100,
      "reason": "Welcome bonus",
      "created_at": "2025-12-03T10:00:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "delta": -50,
      "reason": "Mentor session booking",
      "created_at": "2025-12-03T10:30:00Z"
    },
    ...
  ]
}
```

**Seeded Data**: 210 coin ledger entries (welcome bonuses, quiz rewards, mentor session costs)

---

## 🧑‍💼 Admin Routes

### Get Quiz Generation Stats (Admin Only)
```bash
GET /api/v1/admin/quizzes/stats
Cookie: token=<admin_jwt>
```

**Response (200)**:
```json
{
  "total_quizzes_generated": 45,
  "total_attempts": 120,
  "average_score": 78.5,
  "users_generated": 25
}
```

### Get Recent Quizzes (Admin Only)
```bash
GET /api/v1/admin/quizzes/recent?limit=10
Cookie: token=<admin_jwt>
```

**Response (200)**: Array of recent quiz generation records

---

## 🔍 Testing Workflows

### Test Full User Journey
1. **Signup** → POST /api/v1/auth/signup
2. **Login** → POST /api/v1/auth/login (get cookie)
3. **View Courses** → GET /api/v1/courses
4. **Take Quiz** → GET /api/v1/quizzes?path=python-ai, then POST /api/v1/quizzes/submit
5. **Create Resume** → POST /api/v1x/resumes
6. **Duplicate Resume** → POST /api/v1x/resumes/{id}/duplicate
7. **Book Mentor** → POST /api/v1x/mentor-sessions
8. **Check Progress** → GET /api/v1x/dashboard/overview

### Test Resume Feature
1. **Create**: `POST /api/v1x/resumes` → expect 201
2. **List**: `GET /api/v1x/resumes` → expect 200 array
3. **Get**: `GET /api/v1x/resumes/{id}` → expect 200 (view counter increments)
4. **Update**: `PATCH /api/v1x/resumes/{id}` → expect 200
5. **Duplicate**: `POST /api/v1x/resumes/{id}/duplicate` → expect 200 (new id, "(Copy)" title)
6. **Delete**: `DELETE /api/v1x/resumes/{id}` → expect 204

**Last Verified**: December 3, 2025 - All steps return correct status codes. Duplicate endpoint verified to return 200 with correct response structure.

### Test Quiz Feature
1. **List Available**: `GET /api/v1/quizzes?path=python-ai` → expect 200
2. **Submit**: `POST /api/v1/quizzes/submit` → expect 200 with score
3. **Generate AI**: `POST /api/v1/quizzes/generate` → expect 200 with questions
4. **Get Results**: `GET /api/v1x/dashboard/quiz-results` → expect 200 array

---

## 📊 Seeded Data Summary

| Entity | Count | Status |
|--------|-------|--------|
| Users | 195 | ✅ Verified |
| Courses | 6 | ✅ Verified |
| Quizzes | 5 | ✅ Verified (45 total questions) |
| Resumes | 191 | ✅ Verified |
| Mentor Sessions | 17 | ✅ Verified |
| Coin Ledger Entries | 210 | ✅ Verified |
| Quiz Attempts | 45+ | ✅ Verified |

**All data accessible via API directly at base URL `http://127.0.0.1:8001`**

---

## 🛠️ Common Issues & Fixes

### Issue: 401 Unauthorized
**Cause**: Missing or invalid JWT token  
**Fix**: Login first, ensure cookie is being sent with requests

### Issue: 422 Unprocessable Content (Auth)
**Cause**: Email validation failed (reserved domain like `.test`)  
**Fix**: Use valid email domain (`.com`, `.org`, `.edu`, etc.)

### Issue: 404 Not Found (Quiz)
**Cause**: Path slug doesn't exist  
**Fix**: Use valid path: `python-ai`, `fullstack`, `aws-devops`, `cybersec`, or `flutter`

### Issue: 404 Not Found (Resume)
**Cause**: Resume ID doesn't exist or belongs to different user  
**Fix**: Verify ID and ensure user is logged in with correct account

---

## 📝 Curl Examples

### Create User & Login
```bash
# Signup
curl -X POST http://127.0.0.1:8001/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"test123","full_name":"Test User"}'

# Login (save cookies)
curl -X POST http://127.0.0.1:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"test123"}' \
  -c cookies.txt

# Verify login
curl -X GET http://127.0.0.1:8001/api/v1/auth/me \
  -b cookies.txt
```

### Create & Duplicate Resume
```bash
# Create
curl -X POST http://127.0.0.1:8001/api/v1x/resumes \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title":"My Resume","template_id":"modern","full_name":"John Doe","email":"john@example.com","phone":"+1-555-0123","location":"San Francisco, CA","summary":"Experienced engineer"}'

# Duplicate (replace {id} with resume ID from response)
curl -X POST http://127.0.0.1:8001/api/v1x/resumes/{id}/duplicate \
  -b cookies.txt
```

### Take Quiz
```bash
# Get quiz
curl -X GET "http://127.0.0.1:8001/api/v1/quizzes?path=python-ai"

# Submit answers
curl -X POST http://127.0.0.1:8001/api/v1/quizzes/submit \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"path":"python-ai","answers":[{"id":"q1","answerIndex":0},{"id":"q2","answerIndex":1}]}'
```

---

## 🎯 Next Steps

1. **Backend is fully validated** ✅
   - All endpoints working (200/201/204 status codes)
   - All seeded data accessible
   - Auth, resume duplicate, quizzes, mentor sessions verified

2. **Frontend proxy issue** 🔴
   - Next dev server reports "Ready" but does not listen on port 3003
   - Backend direct testing confirms all features work
   - Proxy handlers created but cannot test due to connectivity

3. **Options**:
   - **Use backend directly** for all testing (recommended for now)
   - **Build frontend** (`npm run build`) and test production build
   - **Debug Next server** to resolve port binding issue

---

## 📞 Support

- **Backend Issues**: Check `backend/app/main.py` and `backend/app/api/v1x/` routes
- **Auth Issues**: See `backend/app/api/v1/auth.py` (email domain validation)
- **Database Issues**: Check `backend/app/core/db.py` and SQLAlchemy models
- **Seeding Issues**: Run `python backend/seed_courses.py` etc. from workspace root

---

**Generated**: December 3, 2025  
**Status**: Ready for production validation  
**Last Test**: Python smoke test (backend direct) - ALL PASS ✅

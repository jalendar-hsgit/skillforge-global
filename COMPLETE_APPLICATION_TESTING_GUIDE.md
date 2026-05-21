# Complete Application Testing Guide
**SkillForge Global - Comprehensive Testing Suite**

**Last Updated:** January 5, 2026
**Version:** 1.0

---

## Table of Contents
1. [Testing Overview](#testing-overview)
2. [Environment Setup](#environment-setup)
3. [Frontend Testing](#frontend-testing)
4. [Backend API Testing](#backend-api-testing)
5. [Integration Testing](#integration-testing)
6. [User Journey Testing](#user-journey-testing)
7. [Performance Testing](#performance-testing)
8. [Security Testing](#security-testing)
9. [Test Data & Seeding](#test-data--seeding)
10. [Reporting & Monitoring](#reporting--monitoring)

---

## Testing Overview

### Test Pyramid
```
        ╔═════════════════════════════╗
        ║   E2E / User Journey Tests  ║  (5-10%)
        ╠═════════════════════════════╣
        ║   Integration Tests         ║  (20-30%)
        ╠═════════════════════════════╣
        ║   API / Unit Tests          ║  (60-70%)
        ╚═════════════════════════════╝
```

### Testing Checklist

- [ ] Frontend Component Testing
- [ ] API Endpoint Testing
- [ ] Database Integration
- [ ] Authentication & Authorization
- [ ] User Workflows
- [ ] Performance & Load Testing
- [ ] Security Vulnerabilities
- [ ] Cross-browser Compatibility
- [ ] Mobile Responsiveness
- [ ] Error Handling

---

## Environment Setup

### Prerequisites

```bash
# Backend
Python 3.13+
FastAPI
SQLAlchemy
SQLite3

# Frontend
Node.js 16+
npm/yarn
Next.js 14.2.33
React 18+

# Testing Tools
pytest (backend)
jest/vitest (frontend)
Postman/curl (API)
Selenium/Playwright (E2E)
```

### Installation

```bash
# Backend setup
cd backend
pip install -r requirements.txt
python init_db.py
python seed_all_demo_data.py

# Frontend setup
npm install
npm run build
```

### Starting Services

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
npm run dev
# Runs on http://localhost:3000

# Terminal 3: Database
# SQLite file at: backend/app/data/skillforge.db
```

---

## Frontend Testing

### 1. Component Testing

**Test File Location:** `src/__tests__/`

```bash
# Run all frontend tests
npm run test

# Run specific test file
npm run test -- LoginPage.test.tsx

# Run with coverage
npm run test -- --coverage
```

**Key Components to Test:**

#### Authentication Components
- [ ] Login page - form validation, submission
- [ ] Signup page - validation, password strength
- [ ] Reset password - token validation
- [ ] OAuth callbacks - provider integration

```javascript
// Example test
describe('LoginPage', () => {
  test('renders login form', () => {
    render(<LoginPage />);
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
  });

  test('submits form with credentials', async () => {
    render(<LoginPage />);
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' }
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    // Assert API call was made
  });
});
```

#### Dashboard Components
- [ ] User profile display
- [ ] Stats cards rendering
- [ ] Recent activity feed
- [ ] Quick action buttons

#### Course/Learning Components
- [ ] Course list display
- [ ] Filter functionality
- [ ] Enrollment button
- [ ] Progress tracking

#### Practice/Code Editor
- [ ] Code editor functionality
- [ ] Syntax highlighting
- [ ] Code execution
- [ ] Test case verification

#### Marketplace Components
- [ ] Product listing
- [ ] Cart operations (add, remove, update)
- [ ] Checkout flow
- [ ] Order history

### 2. Page Navigation Testing

Test all page routes:

```bash
# Test home page
curl http://localhost:3000/

# Test login redirect
curl -L http://localhost:3000/dashboard
# Should redirect to /login if not authenticated

# Test protected routes
# Login first, then access:
# - /profile
# - /dashboard
# - /resumes
# - /mentors/my-sessions
```

### 3. Form Testing

**All Forms to Test:**

- [ ] Login form
- [ ] Signup form
- [ ] Profile edit form
- [ ] Resume builder
- [ ] Job application form
- [ ] Marketplace product creation
- [ ] Mentor application form

**Test Scenarios:**
```
1. Valid submission - success
2. Invalid input - error messages
3. Empty fields - validation errors
4. Email validation - format check
5. Password strength - requirements check
6. File upload - size/type validation
7. Duplicate email - existing user check
```

### 4. Mobile Responsiveness Testing

```bash
# Test responsive design
# Chrome DevTools -> Toggle device toolbar
# Test breakpoints: 320px, 768px, 1024px, 1440px

# Test on actual devices
# iPhone, Android, Tablet

# Test touch interactions
# Tap buttons
# Scroll functionality
# Mobile navigation
```

---

## Backend API Testing

### 1. Setup Testing Environment

```python
# Create conftest.py for pytest fixtures

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    # Login and get token
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### 2. Authentication Testing

**Endpoints to Test:**

```
POST   /api/v1/auth/login
POST   /api/v1/auth/signup
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh-token
POST   /api/v1/auth/forgot-password
POST   /api/v1/auth/reset-password
GET    /api/v1/auth/me
```

**Test Script:**

```python
def test_user_login(client):
    """Test user login"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "john.doe@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["user"]["email"] == "john.doe@example.com"

def test_user_signup(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "New User"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"

def test_invalid_credentials(client):
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "john.doe@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_protected_route_without_token(client):
    """Test accessing protected route without auth"""
    response = client.get("/api/v1/account/profile")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
```

### 3. User Profile Testing

```
GET    /api/v1/account/profile
PUT    /api/v1/account/profile
GET    /api/v1/account/stats
POST   /api/v1/account/avatar
```

**Tests:**
```python
def test_get_profile(client, auth_headers):
    """Get user profile"""
    response = client.get(
        "/api/v1/account/profile",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "email" in response.json()
    assert "name" in response.json()

def test_update_profile(client, auth_headers):
    """Update user profile"""
    response = client.put(
        "/api/v1/account/profile",
        headers=auth_headers,
        json={
            "name": "Updated Name",
            "bio": "New bio",
            "skills": ["Python", "JavaScript"]
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
```

### 4. Courses Testing

```
GET    /api/v1/courses-db           # All courses
GET    /api/v1/courses-db/{id}      # Course detail
POST   /api/v1/courses-db           # Create (admin)
PUT    /api/v1/courses-db/{id}      # Update (admin)
DELETE /api/v1/courses-db/{id}      # Delete (admin)
POST   /api/v1/progress-db          # Track progress
```

**Tests:**
```python
def test_list_courses(client):
    """Get all courses"""
    response = client.get("/api/v1/courses-db")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_get_course_detail(client):
    """Get single course"""
    response = client.get("/api/v1/courses-db/1")
    assert response.status_code == 200
    assert "title" in response.json()
    assert "description" in response.json()
```

### 5. Mentorship Testing

```
GET    /api/v1/mentors              # List mentors
GET    /api/v1/mentors/{id}         # Mentor detail
POST   /api/v1/mentors              # Create mentor
POST   /api/v1/mentors/sessions     # Book session
GET    /api/v1/mentors/my-sessions  # My sessions
PUT    /api/v1/mentors/settings     # Update settings
```

**Tests:**
```python
def test_list_mentors(client):
    """Get all mentors"""
    response = client.get("/api/v1/mentors")
    assert response.status_code == 200
    mentors = response.json()
    assert len(mentors) > 0
    assert all("hourly_rate" in m for m in mentors)

def test_book_session(client, auth_headers):
    """Book mentor session"""
    response = client.post(
        "/api/v1/mentors/sessions",
        headers=auth_headers,
        json={
            "mentor_id": 1,
            "topic": "Python Basics",
            "scheduled_at": "2026-01-10T10:00:00Z"
        }
    )
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"
```

### 6. Job Applications Testing

```
GET    /api/v1x/job-applications        # List applications
POST   /api/v1x/job-applications        # Create application
PUT    /api/v1x/job-applications/{id}   # Update application
GET    /api/v1x/job-applications/stats  # Statistics
```

**Tests:**
```python
def test_create_job_application(client, auth_headers):
    """Create job application"""
    response = client.post(
        "/api/v1x/job-applications",
        headers=auth_headers,
        json={
            "company_name": "Tech Company",
            "position_title": "Software Engineer",
            "status": "APPLIED"
        }
    )
    assert response.status_code == 201
    assert response.json()["company_name"] == "Tech Company"

def test_job_stats(client, auth_headers):
    """Get job application statistics"""
    response = client.get(
        "/api/v1x/job-applications/stats",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "total_applications" in response.json()
    assert "response_rate" in response.json()
```

### 7. Marketplace Testing

```
GET    /api/v1x/Marketplace              # List products
POST   /api/v1x/Marketplace              # Create product
GET    /api/v1x/Marketplace/{id}         # Product detail
POST   /api/v1x/Marketplace/orders       # Create order
GET    /api/v1x/Marketplace/orders       # User orders
```

**Tests:**
```python
def test_list_marketplace_products(client):
    """Get marketplace products"""
    response = client.get("/api/v1x/Marketplace")
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0

def test_create_marketplace_order(client, auth_headers):
    """Create marketplace order"""
    response = client.post(
        "/api/v1x/Marketplace/orders",
        headers=auth_headers,
        json={
            "product_id": 1,
            "quantity": 1,
            "payment_method": "coins"
        }
    )
    assert response.status_code == 201
    assert response.json()["status"] in ["pending", "completed"]
```

### 8. Resumes Testing

```
GET    /api/v1/resumes              # List resumes
POST   /api/v1/resumes              # Create resume
GET    /api/v1/resumes/{id}         # Resume detail
PUT    /api/v1/resumes/{id}         # Update resume
DELETE /api/v1/resumes/{id}         # Delete resume
GET    /api/v1/resumes/{id}/ats-score  # ATS score
```

**Tests:**
```python
def test_create_resume(client, auth_headers):
    """Create new resume"""
    response = client.post(
        "/api/v1/resumes",
        headers=auth_headers,
        json={
            "title": "My Resume",
            "content": {"experience": [], "education": []},
            "template": "professional"
        }
    )
    assert response.status_code == 201
    assert response.json()["title"] == "My Resume"

def test_get_ats_score(client, auth_headers):
    """Get ATS compatibility score"""
    response = client.get(
        "/api/v1/resumes/1/ats-score",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "score" in response.json()
    assert "suggestions" in response.json()
```

### 9. Subscriptions Testing

```
GET    /api/v1x/subscriptions              # Plans
GET    /api/v1x/subscriptions/active       # User's active
POST   /api/v1x/subscriptions              # Subscribe
```

**Tests:**
```python
def test_get_subscription_plans(client):
    """Get available plans"""
    response = client.get("/api/v1x/subscriptions/plans")
    assert response.status_code == 200
    assert len(response.json()) >= 3

def test_subscribe(client, auth_headers):
    """Subscribe to plan"""
    response = client.post(
        "/api/v1x/subscriptions",
        headers=auth_headers,
        json={
            "plan_id": 1,
            "payment_method": "stripe"
        }
    )
    assert response.status_code == 201
```

### 10. Admin Testing

```
GET    /api/v1/admin              # Admin dashboard
GET    /api/v1/admin/users        # User management
POST   /api/v1/admin/users        # Create user
PUT    /api/v1/admin/users/{id}   # Update user
DELETE /api/v1/admin/users/{id}   # Delete user
```

---

## Integration Testing

### 1. End-to-End User Workflows

#### Workflow 1: New User Registration & Profile Setup

```python
def test_user_registration_workflow(client):
    """Complete user registration workflow"""
    
    # Step 1: Register
    signup_response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "New User"
        }
    )
    assert signup_response.status_code == 201
    user_id = signup_response.json()["id"]
    
    # Step 2: Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Complete profile
    profile_response = client.put(
        "/api/v1/account/profile",
        headers=headers,
        json={
            "bio": "Software Developer",
            "skills": ["Python", "JavaScript"],
            "location": "USA"
        }
    )
    assert profile_response.status_code == 200
    
    # Step 4: Verify profile saved
    verify_response = client.get(
        "/api/v1/account/profile",
        headers=headers
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["bio"] == "Software Developer"
```

#### Workflow 2: Booking a Mentor Session

```python
def test_mentor_booking_workflow(client, auth_headers):
    """Complete mentor booking workflow"""
    
    # Step 1: List mentors
    mentors_response = client.get("/api/v1/mentors")
    assert mentors_response.status_code == 200
    mentor_id = mentors_response.json()[0]["id"]
    
    # Step 2: Get mentor details
    mentor_response = client.get(f"/api/v1/mentors/{mentor_id}")
    assert mentor_response.status_code == 200
    hourly_rate = mentor_response.json()["hourly_rate"]
    
    # Step 3: Check availability
    availability_response = client.get(
        f"/api/v1/mentors/{mentor_id}/availability"
    )
    assert availability_response.status_code == 200
    
    # Step 4: Book session
    booking_response = client.post(
        "/api/v1/mentors/sessions",
        headers=auth_headers,
        json={
            "mentor_id": mentor_id,
            "topic": "Python Advanced",
            "scheduled_at": "2026-01-15T15:00:00Z",
            "duration_minutes": 60
        }
    )
    assert booking_response.status_code == 201
    session_id = booking_response.json()["id"]
    
    # Step 5: Verify booking
    session_response = client.get(
        f"/api/v1/mentors/sessions/{session_id}",
        headers=auth_headers
    )
    assert session_response.status_code == 200
    assert session_response.json()["status"] == "PENDING"
```

#### Workflow 3: Course Enrollment & Progress

```python
def test_course_enrollment_workflow(client, auth_headers):
    """Complete course enrollment workflow"""
    
    # Step 1: List courses
    courses_response = client.get("/api/v1/courses-db")
    assert courses_response.status_code == 200
    course_id = courses_response.json()[0]["id"]
    
    # Step 2: Get course details
    course_response = client.get(f"/api/v1/courses-db/{course_id}")
    assert course_response.status_code == 200
    
    # Step 3: Enroll in course
    enroll_response = client.post(
        "/api/v1/progress-db",
        headers=auth_headers,
        json={
            "course_id": course_id,
            "status": "in_progress"
        }
    )
    assert enroll_response.status_code == 201
    
    # Step 4: Update progress
    progress_response = client.put(
        f"/api/v1/progress-db/{course_id}",
        headers=auth_headers,
        json={
            "status": "completed",
            "progress_percentage": 100
        }
    )
    assert progress_response.status_code == 200
```

#### Workflow 4: Marketplace Purchase

```python
def test_marketplace_purchase_workflow(client, auth_headers):
    """Complete marketplace purchase workflow"""
    
    # Step 1: List products
    products_response = client.get("/api/v1x/Marketplace")
    assert products_response.status_code == 200
    product_id = products_response.json()[0]["id"]
    
    # Step 2: Add to cart
    cart_response = client.post(
        "/api/v1x/Marketplace/cart",
        headers=auth_headers,
        json={
            "product_id": product_id,
            "quantity": 1
        }
    )
    assert cart_response.status_code == 201
    
    # Step 3: Create order
    order_response = client.post(
        "/api/v1x/Marketplace/orders",
        headers=auth_headers,
        json={
            "product_id": product_id,
            "payment_method": "coins"
        }
    )
    assert order_response.status_code == 201
    order_id = order_response.json()["id"]
    
    # Step 4: Verify order
    verify_response = client.get(
        f"/api/v1x/Marketplace/orders/{order_id}",
        headers=auth_headers
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["status"] in ["pending", "completed"]
```

#### Workflow 5: Resume Creation & Export

```python
def test_resume_workflow(client, auth_headers):
    """Complete resume creation workflow"""
    
    # Step 1: Create resume
    create_response = client.post(
        "/api/v1/resumes",
        headers=auth_headers,
        json={
            "title": "Software Engineer Resume",
            "template": "professional",
            "content": {
                "experience": [
                    {
                        "company": "Tech Corp",
                        "position": "Senior Developer",
                        "start_date": "2024-01-01",
                        "end_date": "2026-01-01"
                    }
                ],
                "education": [
                    {
                        "institution": "University",
                        "degree": "BS Computer Science",
                        "graduation_date": "2020-05-01"
                    }
                ]
            }
        }
    )
    assert create_response.status_code == 201
    resume_id = create_response.json()["id"]
    
    # Step 2: Get ATS score
    ats_response = client.get(
        f"/api/v1/resumes/{resume_id}/ats-score",
        headers=auth_headers
    )
    assert ats_response.status_code == 200
    assert ats_response.json()["score"] >= 0
    
    # Step 3: Export resume
    export_response = client.get(
        f"/api/v1/resumes/{resume_id}/export",
        headers=auth_headers,
        params={"format": "pdf"}
    )
    assert export_response.status_code == 200
```

---

## User Journey Testing

### Manual Testing Scenarios

#### Journey 1: Beginner Student Path

```
1. Visit http://localhost:3000/ (home page)
2. Click "Get Started" → /signup
3. Create account with email: student@example.com
4. Verify email (skip in dev)
5. Go to /profile/edit
   - Add skills: Python, JavaScript
   - Add bio: "Learning to code"
   - Upload profile picture
6. Go to /learning-paths
   - Browse available paths
   - Enroll in "Python Fundamentals"
7. Complete some lessons
8. Go to /practice
   - Solve coding problems
   - Submit solutions
9. Check /dashboard
   - View progress
   - See achievements
10. Go to /mentors
    - Browse mentors
    - Book a session
11. Check /messages
    - See mentor message
```

#### Journey 2: Mentor Workflow

```
1. Signup with role: MENTOR
2. Go to /mentors/become
3. Fill mentor application:
   - Expertise: Python, AI
   - Hourly rate: $75
   - Bio: "Senior Python Developer"
4. Go to /mentors/settings
   - Set availability: Mon-Fri 9am-5pm
5. Go to /mentors/dashboard
   - Review sessions
   - Accept/reject bookings
6. View /mentors/dashboard/earnings
   - Check monthly earnings
7. View /mentors/dashboard/reviews
   - See student reviews
8. Go to /mentors/dashboard/payouts
   - Link bank account
   - Request payout
```

#### Journey 3: Seller Workflow

```
1. Login as user
2. Go to /marketplace/seller
3. Create product at /marketplace/seller/create-product
   - Title: "Python Cheat Sheet"
   - Price: $9.99
   - Upload file
4. View /marketplace/seller/products
   - List products
   - Edit/delete
5. View /marketplace/seller/orders
   - See customer orders
   - Deliver products
6. Check /marketplace/seller/analytics
   - View sales metrics
   - See revenue trends
```

#### Journey 4: Job Seeker Workflow

```
1. Go to /jobs
   - Browse job listings
2. Add job application at /job-tracker/add
   - Company: Google
   - Position: Software Engineer
   - Status: Applied
3. Go to /job-tracker/analytics
   - View application stats
   - See response rate
4. Create resume at /resumes/new
5. Check resume ATS score at /resumes/[id]/ats-score
6. Share resume at /resumes/[id]/sharing
```

---

## Performance Testing

### Load Testing

```bash
# Install Apache Bench
ab -n 1000 -c 10 http://localhost:3000/

# Test API endpoints
ab -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/v1/account/profile

# Test database query performance
# Measure response time for:
# - GET /courses (list)
# - GET /mentors (with filtering)
# - GET /practice (with pagination)
```

### Database Performance

```sql
-- Check database size
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();

-- Analyze slow queries
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = ?;

-- Index usage
SELECT * FROM sqlite_stat1;
```

### Frontend Performance

```javascript
// Lighthouse audit
// Chrome DevTools → Lighthouse → Generate report

// Check Core Web Vitals
// - Largest Contentful Paint (LCP) < 2.5s
// - First Input Delay (FID) < 100ms
// - Cumulative Layout Shift (CLS) < 0.1
```

---

## Security Testing

### 1. Authentication Security

```
- [ ] SQL Injection
  POST /api/v1/auth/login
  email: "admin'--" 
  → Should not bypass auth

- [ ] CSRF Protection
  Test without CSRF token
  → Should be rejected

- [ ] XSS Prevention
  POST /profile/edit
  bio: "<script>alert('XSS')</script>"
  → Should be sanitized

- [ ] Password Strength
  POST /auth/signup
  password: "123"
  → Should be rejected (too weak)
```

### 2. Authorization Testing

```python
def test_user_cannot_access_others_profile(client, auth_headers):
    """Verify users can't access other profiles"""
    response = client.get(
        "/api/v1/account/profile/999",  # Another user
        headers=auth_headers
    )
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]

def test_user_cannot_delete_others_resume(client, auth_headers):
    """Verify users can't delete other resumes"""
    response = client.delete(
        "/api/v1/resumes/999",  # Another user's resume
        headers=auth_headers
    )
    assert response.status_code == 403
```

### 3. Admin-only Endpoints

```
- [ ] User management (admin only)
  POST /api/v1/admin/users
  Regular user → 403 Forbidden
  
- [ ] Mentor approval (admin only)
  PUT /api/v1/mentors/1/approve
  Regular user → 403 Forbidden
  
- [ ] Content moderation (admin only)
  DELETE /api/v1/forums/posts/1
  Regular user → 403 Forbidden
```

### 4. Rate Limiting

```
- [ ] Login attempts limited
  POST /api/v1/auth/login (repeated)
  After 5 attempts → 429 Too Many Requests
  
- [ ] API rate limits enforced
  GET /api/v1/courses (repeated)
  Exceeds limit → 429 Too Many Requests
```

### 5. Data Validation

```python
def test_invalid_email_format(client):
    """Verify email validation"""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "invalid-email",
            "password": "SecurePass123!",
            "name": "User"
        }
    )
    assert response.status_code == 422
    assert "invalid" in response.json()["detail"][0]["msg"].lower()

def test_file_upload_validation(client, auth_headers):
    """Verify file upload restrictions"""
    # Test oversized file
    # Test wrong file type
    # Test malware signatures
```

---

## Test Data & Seeding

### Seed Demo Data

```bash
# Backend
python backend/seed_all_demo_data.py

# This creates:
# - 7 regular users
# - 4 mentors
# - 5 courses
# - 5 job applications
# - 3 marketplace products
# - 8 mentor sessions
# - 20 availability slots
```

### Test Data Files

**File:** `backend/tests/fixtures/test_data.py`

```python
TEST_USERS = [
    {
        "email": "student@example.com",
        "password": "TestPass123!",
        "name": "Test Student",
        "role": "USER"
    },
    {
        "email": "mentor@example.com",
        "password": "TestPass123!",
        "name": "Test Mentor",
        "role": "MENTOR"
    },
    {
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "name": "Test Admin",
        "role": "ADMIN"
    }
]

TEST_COURSES = [
    {
        "title": "Python Basics",
        "description": "Learn Python",
        "price": 49.99,
        "difficulty": "beginner"
    },
    {
        "title": "Advanced Python",
        "description": "Advanced Python",
        "price": 99.99,
        "difficulty": "advanced"
    }
]
```

---

## Reporting & Monitoring

### Test Results Template

**File:** `TEST_RESULTS.md`

```markdown
# Test Results Report
**Date:** January 5, 2026
**Tester:** [Name]
**Environment:** Development

## Summary
- Total Tests: 150
- Passed: 147 ✅
- Failed: 3 ❌
- Skipped: 0
- Pass Rate: 98%

## Failed Tests
1. Test name
   - Issue: Description
   - Severity: High/Medium/Low
   
## Performance Metrics
- Average API response time: 150ms
- Frontend build time: 45s
- Database query avg: 10ms

## Security Issues
- 0 Critical
- 0 High
- 1 Medium: CORS configuration
- 2 Low: Headers missing

## Recommendations
1. Fix CORS to only allow localhost:3000
2. Add security headers
3. Implement rate limiting
```

### Continuous Monitoring

```bash
# Monitor application health
curl http://localhost:8001/health

# Check API performance
curl http://localhost:8001/metrics

# Database monitoring
# Check: backend/app/data/skillforge.db
# Size, last modified, table counts
```

---

## Quick Test Commands

```bash
# Run all tests
npm run test                          # Frontend
pytest backend/tests/                # Backend
python comprehensive_api_tests.py    # API endpoints

# Run specific test
npm run test -- LoginPage.test.tsx
pytest backend/tests/test_auth.py::test_user_login

# Run with coverage
npm run test -- --coverage
pytest --cov=app backend/tests/

# Run in watch mode
npm run test -- --watch
pytest-watch backend/tests/

# Performance testing
npm run build && npm start
ab -n 1000 -c 10 http://localhost:3000/

# Load testing
python -m locust -f locustfile.py --host=http://localhost:8001
```

---

## Checklist for Testing Complete

### Frontend Testing
- [ ] All pages load correctly
- [ ] Form validation works
- [ ] Navigation functions properly
- [ ] Responsive design verified
- [ ] Error messages display
- [ ] Loading states shown

### Backend Testing
- [ ] Authentication endpoints work
- [ ] CRUD operations successful
- [ ] Validation enforced
- [ ] Permissions checked
- [ ] Database queries optimized
- [ ] Error handling proper

### Integration Testing
- [ ] Complete workflows execute
- [ ] Data persists correctly
- [ ] Cross-service communication works
- [ ] No race conditions
- [ ] Async operations complete

### Security Testing
- [ ] No SQL injection
- [ ] No XSS vulnerabilities
- [ ] Authorization enforced
- [ ] Sensitive data protected
- [ ] Input validated
- [ ] Rate limiting works

### Performance Testing
- [ ] API responses < 500ms
- [ ] Frontend renders < 3s
- [ ] Database queries < 100ms
- [ ] Load test passes
- [ ] Memory usage stable

### User Testing
- [ ] All user journeys work
- [ ] Mobile experience good
- [ ] Accessibility proper
- [ ] Error recovery smooth
- [ ] User feedback implemented

---

## Test Execution Timeline

```
Week 1:
- Setup test environment
- Write unit tests
- Create test fixtures

Week 2:
- Run API tests
- Integration testing
- Performance testing

Week 3:
- Security testing
- User journey testing
- Bug fixes

Week 4:
- Regression testing
- Final validation
- Release preparation
```

---

## Support & Troubleshooting

### Common Issues

**Q: Tests fail with "Connection refused"**
A: Ensure backend is running on port 8001
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Q: Database locking errors**
A: Reset database
```bash
rm backend/app/data/skillforge.db
python backend/init_db.py
python backend/seed_all_demo_data.py
```

**Q: Frontend tests timeout**
A: Increase Jest timeout
```javascript
jest.setTimeout(30000);
```

**Q: API returns 401 Unauthorized**
A: Check token expiration, refresh token
```bash
curl -X POST http://localhost:8001/api/v1/auth/refresh-token
```

---

**Document Version:** 1.0
**Last Updated:** January 5, 2026
**Framework:** Next.js 14.2.33 + FastAPI
**Contact:** development@skillforge.com

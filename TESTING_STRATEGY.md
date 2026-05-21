# Testing Strategy & Code Coverage Plan

## 🎯 Testing Philosophy

**"Test early, test often, test everything that matters"**

Our goal: **80%+ code coverage** with meaningful tests that catch real bugs, not just inflate metrics.

---

## 📊 Coverage Targets by Component

| Component | Target Coverage | Priority | Status |
|-----------|----------------|----------|--------|
| Backend API Routes | 90% | Critical | 🔴 To Do |
| Backend Models | 85% | High | 🔴 To Do |
| Backend Services | 80% | High | 🔴 To Do |
| Frontend Pages | 75% | Medium | 🔴 To Do |
| Frontend Components | 80% | High | 🔴 To Do |
| Frontend Hooks | 90% | Critical | 🔴 To Do |
| E2E Flows | 70% | Critical | 🔴 To Do |

---

## 🔧 Testing Stack

### Backend (Python/FastAPI)
- **Framework:** pytest
- **Coverage:** pytest-cov
- **Mocking:** pytest-mock
- **Async Testing:** pytest-asyncio
- **DB Testing:** pytest-postgresql / in-memory SQLite
- **API Testing:** httpx (FastAPI's test client)

### Frontend (Next.js/React)
- **Framework:** Jest
- **React Testing:** React Testing Library
- **Coverage:** Jest coverage
- **Mocking:** jest-mock
- **API Mocking:** MSW (Mock Service Worker)

### E2E Testing
- **Framework:** Playwright
- **Browsers:** Chromium, Firefox, Safari
- **Visual Regression:** Percy or Playwright screenshots

### Performance Testing
- **Load Testing:** Locust
- **API Benchmarking:** Apache Bench (ab)
- **Frontend:** Lighthouse CI

---

## 🧪 Backend Testing Strategy

### 1. Unit Tests

#### Authentication Tests (`test_auth.py`)
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_token, decode_token

client = TestClient(app)

class TestAuth:
    def test_signup_success(self):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/signup", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        assert response.status_code == 201
        assert "id" in response.json()
        assert response.json()["email"] == "test@example.com"
    
    def test_signup_duplicate_email(self):
        """Test signup with existing email"""
        # First signup
        client.post("/api/v1/auth/signup", json={
            "email": "duplicate@example.com",
            "password": "Pass123!"
        })
        # Second signup with same email
        response = client.post("/api/v1/auth/signup", json={
            "email": "duplicate@example.com",
            "password": "Pass456!"
        })
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_signup_weak_password(self):
        """Test signup with weak password"""
        response = client.post("/api/v1/auth/signup", json={
            "email": "weak@example.com",
            "password": "123"
        })
        assert response.status_code == 400
    
    def test_login_success(self):
        """Test successful login"""
        # Create user
        client.post("/api/v1/auth/signup", json={
            "email": "login@example.com",
            "password": "Pass123!"
        })
        # Login
        response = client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "Pass123!"
        })
        assert response.status_code == 200
        assert "token" in response.cookies
    
    def test_login_wrong_password(self):
        """Test login with incorrect password"""
        response = client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "WrongPass!"
        })
        assert response.status_code == 401
    
    def test_get_me_authenticated(self):
        """Test getting current user when authenticated"""
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "Pass123!"
        })
        token = login_response.cookies.get("token")
        
        # Get user
        response = client.get("/api/v1/auth/me", cookies={"token": token})
        assert response.status_code == 200
        assert response.json()["email"] == "login@example.com"
    
    def test_get_me_unauthenticated(self):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_token_creation_and_decoding(self):
        """Test JWT token creation and decoding"""
        user_id = 123
        token = create_token(user_id)
        assert token is not None
        
        decoded = decode_token(token)
        assert decoded == str(user_id)
    
    def test_token_expiry(self):
        """Test expired token rejection"""
        # Create token with 0 expiry
        import jwt
        from app.core.config import settings
        token = jwt.encode({"sub": "123", "exp": 0}, settings.JWT_SECRET)
        
        decoded = decode_token(token)
        assert decoded is None
```

#### Quiz Tests (`test_quizzes.py`)
```python
class TestQuizzes:
    def test_get_quiz_success(self):
        """Test fetching quiz by path"""
        response = client.get("/api/v1/quizzes?path=python-ai")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "quiz-python-ai-1"
        assert "questions" in data
        assert len(data["questions"]) > 0
    
    def test_get_quiz_invalid_path(self):
        """Test fetching quiz with invalid path"""
        response = client.get("/api/v1/quizzes?path=invalid-path")
        assert response.status_code == 404
    
    def test_submit_quiz_all_correct(self):
        """Test quiz submission with all correct answers"""
        # Get quiz first to know correct answers
        quiz_response = client.get("/api/v1/quizzes?path=python-ai")
        quiz = quiz_response.json()
        
        # Submit all correct answers
        answers = [
            {"id": q["id"], "answerIndex": q["answerIndex"]}
            for q in quiz["questions"]
        ]
        response = client.post("/api/v1/quizzes/submit", json={
            "path": "python-ai",
            "answers": answers
        })
        assert response.status_code == 200
        data = response.json()
        assert data["score"] == data["total"]
        assert all(r["correct"] for r in data["results"])
    
    def test_submit_quiz_partial_correct(self):
        """Test quiz submission with some wrong answers"""
        response = client.post("/api/v1/quizzes/submit", json={
            "path": "python-ai",
            "answers": [
                {"id": "q1", "answerIndex": 0},  # Wrong
                {"id": "q2", "answerIndex": 2},  # Correct
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["score"] < data["total"]
    
    def test_submit_quiz_saves_attempt(self, db_session):
        """Test that quiz attempt is saved to database"""
        # Login first
        login_response = client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "Pass123!"
        })
        token = login_response.cookies.get("token")
        
        # Submit quiz
        client.post("/api/v1/quizzes/submit", 
            json={"path": "python-ai", "answers": []},
            cookies={"token": token}
        )
        
        # Check database
        from app.models.quiz_attempt import QuizAttempt
        attempt = db_session.query(QuizAttempt).filter_by(path="python-ai").first()
        assert attempt is not None
```

#### Progress Tests (`test_progress.py`)
```python
class TestProgress:
    def test_mark_video_complete(self):
        """Test marking video as complete"""
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "Pass123!"
        })
        token = login_response.cookies.get("token")
        
        # Mark video complete
        response = client.post("/api/v1/progress/videos/1", 
            cookies={"token": token}
        )
        assert response.status_code == 200
    
    def test_get_progress(self):
        """Test getting user progress for path"""
        response = client.get("/api/progress/get?path=python-ai")
        assert response.status_code == 200
        assert "completed" in response.json()
```

### 2. Integration Tests

#### Full User Journey (`test_integration.py`)
```python
class TestUserJourney:
    def test_complete_learning_flow(self):
        """Test complete user journey from signup to quiz completion"""
        # 1. Signup
        signup_response = client.post("/api/v1/auth/signup", json={
            "email": f"journey_{uuid.uuid4()}@test.com",
            "password": "SecurePass123!"
        })
        assert signup_response.status_code == 201
        
        # 2. Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": signup_response.json()["email"],
            "password": "SecurePass123!"
        })
        assert login_response.status_code == 200
        token = login_response.cookies.get("token")
        
        # 3. Get courses
        courses_response = client.get("/api/v1x/courses-db")
        assert courses_response.status_code == 200
        
        # 4. Get videos for a course
        videos_response = client.get("/api/v1x/courses-db/python-ai/videos")
        assert videos_response.status_code == 200
        videos = videos_response.json()
        
        # 5. Mark first video complete
        if videos:
            complete_response = client.post(
                f"/api/v1/progress/videos/{videos[0]['id']}",
                cookies={"token": token}
            )
            assert complete_response.status_code == 200
        
        # 6. Get quiz
        quiz_response = client.get("/api/v1/quizzes?path=python-ai")
        assert quiz_response.status_code == 200
        
        # 7. Submit quiz
        submit_response = client.post("/api/v1/quizzes/submit",
            json={"path": "python-ai", "answers": []},
            cookies={"token": token}
        )
        assert submit_response.status_code == 200
        
        # 8. Check progress
        progress_response = client.get("/api/progress/get?path=python-ai")
        assert progress_response.status_code == 200
```

### 3. Database Tests

#### Model Tests (`test_models.py`)
```python
class TestModels:
    def test_user_creation(self, db_session):
        """Test creating a user"""
        from app.models.user import User
        user = User(email="model@test.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.created_at is not None
    
    def test_user_relationships(self, db_session):
        """Test user relationships"""
        from app.models.user import User
        from app.modelsx.progress import VideoProgress
        
        user = User(email="rel@test.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        
        # Add progress
        progress = VideoProgress(user_id=user.id, video_id=1, completed=True)
        db_session.add(progress)
        db_session.commit()
        
        assert len(user.video_progress) == 1
```

---

## 🎨 Frontend Testing Strategy

### 1. Component Tests

#### Button Component (`Button.test.tsx`)
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import Button from '@/components/Button'

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
  
  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    fireEvent.click(screen.getByText('Click'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
  
  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByText('Disabled')).toBeDisabled()
  })
})
```

#### Navbar Component (`Navbar.test.tsx`)
```typescript
import { render, screen } from '@testing-library/react'
import Navbar from '@/components/Navbar'
import { useMe } from '@/hooks/useMe'

jest.mock('@/hooks/useMe')

describe('Navbar', () => {
  it('shows login/signup when not authenticated', () => {
    (useMe as jest.Mock).mockReturnValue({ me: null })
    render(<Navbar />)
    expect(screen.getByText('Login')).toBeInTheDocument()
    expect(screen.getByText('Sign Up')).toBeInTheDocument()
  })
  
  it('shows dashboard link when authenticated', () => {
    (useMe as jest.Mock).mockReturnValue({ 
      me: { id: 1, email: 'test@test.com' } 
    })
    render(<Navbar />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })
})
```

### 2. Page Tests

#### Login Page (`login.test.tsx`)
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import LoginPage from '@/pages/login'
import { useRouter } from 'next/router'

jest.mock('next/router', () => ({
  useRouter: jest.fn()
}))

describe('Login Page', () => {
  const mockPush = jest.fn()
  
  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush })
  })
  
  it('renders login form', () => {
    render(<LoginPage />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })
  
  it('shows error on invalid credentials', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ detail: 'Invalid credentials' })
      })
    ) as jest.Mock
    
    render(<LoginPage />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'wrong@test.com' }
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpass' }
    })
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
    })
  })
  
  it('redirects to dashboard on successful login', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ id: 1 })
      })
    ) as jest.Mock
    
    render(<LoginPage />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@test.com' }
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password' }
    })
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard')
    })
  })
})
```

### 3. Hook Tests

#### useMe Hook (`useMe.test.ts`)
```typescript
import { renderHook, waitFor } from '@testing-library/react'
import { useMe } from '@/hooks/useMe'

describe('useMe', () => {
  it('fetches user data on mount', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ id: 1, email: 'test@test.com' })
      })
    ) as jest.Mock
    
    const { result } = renderHook(() => useMe())
    
    await waitFor(() => {
      expect(result.current.me).toEqual({ id: 1, email: 'test@test.com' })
    })
  })
  
  it('handles fetch error', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: false })
    ) as jest.Mock
    
    const { result } = renderHook(() => useMe())
    
    await waitFor(() => {
      expect(result.current.me).toBeNull()
    })
  })
})
```

---

## 🎭 E2E Testing Strategy

### Playwright Tests (`e2e/auth.spec.ts`)
```typescript
import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('user can sign up, login, and access dashboard', async ({ page }) => {
    const email = `test${Date.now()}@example.com`
    const password = 'SecurePass123!'
    
    // Navigate to signup
    await page.goto('http://localhost:3000/signup')
    
    // Fill signup form
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)
    await page.click('button:has-text("Sign Up")')
    
    // Should redirect to login
    await expect(page).toHaveURL('/login')
    
    // Login
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)
    await page.click('button:has-text("Login")')
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('h1')).toContainText('Welcome back')
  })
})

test.describe('Learning Flow', () => {
  test('user can watch video and complete quiz', async ({ page, context }) => {
    // Login first
    await page.goto('http://localhost:3000/login')
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'Pass123!')
    await page.click('button:has-text("Login")')
    
    // Navigate to paths
    await page.goto('http://localhost:3000/paths/python-ai')
    
    // Click on first video
    await page.click('[data-testid="video-card"]:first-child')
    await expect(page).toHaveURL(/\/watch\/\d+/)
    
    // Mark video as complete
    await page.click('button:has-text("Mark as Complete")')
    await expect(page.locator('.success-message')).toBeVisible()
    
    // Go to quiz
    await page.goto('http://localhost:3000/quiz/python-ai')
    
    // Answer questions
    const questions = page.locator('[data-testid="question"]')
    const count = await questions.count()
    
    for (let i = 0; i < count; i++) {
      await questions.nth(i).locator('input[type="radio"]').first().click()
    }
    
    // Submit quiz
    await page.click('button:has-text("Submit Quiz")')
    
    // Check results
    await expect(page.locator('[data-testid="quiz-results"]')).toBeVisible()
  })
})
```

---

## 📈 Coverage Reporting

### Setup

#### Backend (`pytest.ini`)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

#### Frontend (`jest.config.js`)
```javascript
module.exports = {
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 75,
      lines: 80,
      statements: 80
    }
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.tsx',
    '!src/pages/_app.tsx',
    '!src/pages/_document.tsx'
  ]
}
```

---

## 🚀 CI/CD Integration

### GitHub Actions (`.github/workflows/test.yml`)
```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test -- --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/coverage-final.json
          
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npm run test:e2e
```

---

## ✅ Testing Checklist

### Before Every Release
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Code coverage meets targets
- [ ] No critical bugs in test results
- [ ] Performance tests show no regression
- [ ] Security scan passes
- [ ] Manual smoke testing on staging

---

*Testing Strategy v1.0 - Last Updated: October 31, 2025*

# Testing Guide

## Overview

This project includes automated end-to-end (E2E) tests for backend API endpoints. The tests use pytest with FastAPI TestClient and stub external service calls (Stripe) to enable testing without external dependencies.

## Test Suite Structure

### Backend E2E Tests (`backend/tests_e2e/`)

The curated E2E test suite includes:

- **test_health.py** - Health check endpoint
- **test_auth.py** - Authentication flow (login, signup, /me)
- **test_courses.py** - Courses listing endpoint
- **test_subscriptions.py** - Subscription management (plans, subscribe, cancel) with Stripe stubs
- **test_connect.py** - Stripe Connect onboarding flow with stubs
- **test_payouts.py** - Mentor payout summary endpoint

### Test Configuration

- **Test Database**: `sqlite:///./app/data/test_e2e.db` (isolated from production)
- **Test Secrets**: Set via environment variables in fixtures
- **Fixtures**: `tests_e2e/conftest.py` provides:
  - `client`: FastAPI TestClient
  - `db_session`: SQLAlchemy session
  - `create_user`: Helper to create test users
  - `login`: Helper to authenticate test users
  - `ensure_mentor`: Helper to create test mentors

## Running Tests

### Prerequisites

1. Python 3.10+ (avoid 3.14 due to pydantic-core build issues)
2. Virtual environment with dependencies installed

### Local Test Execution

#### Windows PowerShell

```powershell
# Navigate to backend directory
cd backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies (if not already done)
pip install -r requirements.txt
pip install pytest

# Set environment variables
$env:DATABASE_URL = "sqlite:///./test.db"
$env:JWT_SECRET = "testsecret"
$env:FRONTEND_ORIGIN = "http://localhost:3000"

# Run E2E tests
python -m pytest tests_e2e -v

# Run specific test file
python -m pytest tests_e2e/test_auth.py -v

# Run with coverage (optional)
pip install pytest-cov
python -m pytest tests_e2e --cov=app --cov-report=html
```

#### PowerShell Script

Use the provided script for convenience:

```powershell
.\scripts\run-backend-tests.ps1
```

### CI/CD Execution

Tests run automatically on GitHub Actions via `.github/workflows/ci.yml`:

- **Trigger**: Push to main branch or pull requests
- **Backend Tests**: Installs Python 3.11, dependencies, pytest, sets env vars, runs E2E suite
- **Frontend Build**: Installs Node.js, dependencies, builds Next.js app
- **Deploy** (optional): Placeholder for deployment to Vercel/Render/etc.

## Key Test Patterns

### Stubbing External Services

The tests stub Stripe API calls to avoid external dependencies:

```python
import types
from app.services.stripe_service import stripe_service

# Stub create_subscription method
stripe_service.create_subscription = types.MethodType(
    lambda self, **kwargs: {
        'id': 'sub_test_123',
        'customer': 'cus_test_123',
        'status': 'active',
        'current_period_start': 1700000000,
        'current_period_end': 1702592000,
    },
    stripe_service
)
```

### Authenticated Requests

Use the `login` fixture to authenticate requests:

```python
def test_authenticated_endpoint(client, login):
    c = login(email="test@example.com", password="testpass")
    r = c.get('/api/v1x/subscriptions/current')
    assert r.status_code == 200
```

### Database Isolation

Each test run uses a fresh test database:

```python
@pytest.fixture(scope="session", autouse=True)
def _create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
```

## Troubleshooting

### SQLAlchemy Mapper Initialization Errors

**Issue**: `One or more mappers failed to initialize`

**Cause**: Models with relationships to other models not imported before `Base.metadata.create_all()`

**Solution**: Ensure all models are imported in `app/main.py` before calling `create_all()`:

```python
# Import all models so tables are registered on Base
from app.models import User, Progress, QuizAttempt, CreditLedger, Subscriber
from app.modelsx.mentor import Mentor, MentorSession, MentorAvailability, MentorMessage, MentorReview
from app.modelsx.payout import MentorPayout, MentorEarning
from app.modelsx.subscription import Subscription, PlanFeature, SubscriptionEvent
from app.modelsx.stripe_connect import MentorStripeAccount
from app.modelsx.chat_file import MentorChatFile
# ... etc
```

### 404 Errors for v1x Endpoints

**Issue**: Tests return 404 for `/api/v1x/subscriptions/*` or `/api/v1x/connect/*`

**Cause**: v1x routers not mounted due to import errors (e.g., missing `dateutil` package)

**Solution**: 
1. Check `main.py` console output for "Failed to import" messages
2. Comment out problematic imports in `app/api/v1x/__init__.py` (e.g., `youtube_sync`)
3. Import v1x routers directly in `main.py` with individual try/except blocks

### Pydantic Validation Errors

**Issue**: 422 Unprocessable Entity errors

**Common Causes**:
- Using Pydantic v1 syntax with v2 library:
  - Replace `regex=` with `pattern=` in Field()
  - Replace `@validator` with `@field_validator`
  - Replace `class Config:` with `ConfigDict`
- Incorrect enum values (use lowercase: `'pro'` not `'PRO'`)

**Solution**: Update schemas to Pydantic v2 syntax (see migration guide: https://errors.pydantic.dev/2.8/migration/)

### Python Version Issues

**Issue**: `error: metadata-generation-failed` for pydantic-core

**Cause**: Python 3.14 lacks prebuilt wheels for pydantic-core (requires Rust compilation)

**Solution**: Use Python 3.11 or 3.10:

```powershell
# Recreate venv with Python 3.11
Remove-Item -Recurse -Force .venv
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Test Results

Current E2E test status: **✅ All 6 tests passing**

```
tests_e2e/test_health.py::test_health_check PASSED
tests_e2e/test_auth.py::test_auth_flow PASSED
tests_e2e/test_courses.py::test_courses_list PASSED
tests_e2e/test_subscriptions.py::test_subscription_flow PASSED
tests_e2e/test_connect.py::test_connect_flow PASSED
tests_e2e/test_payouts.py::test_payouts_summary PASSED

=========================== 6 passed, 53 warnings in 4.56s ===========================
```

## Next Steps

1. **Expand Test Coverage**: Add tests for:
   - Mentor CRUD operations
   - Session booking and management
   - File upload/download
   - WebSocket chat

2. **Add Integration Tests**: Test actual Stripe API calls in sandbox mode (separate from E2E)

3. **Frontend E2E Tests**: Add Playwright/Cypress tests for UI flows

4. **Performance Tests**: Add load tests for critical endpoints

5. **Deploy to Staging**: Run E2E tests against staging environment before production deploys

## Resources

- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pydantic V2 Migration Guide](https://errors.pydantic.dev/2.8/migration/)
- [SQLAlchemy Relationship Configuration](https://docs.sqlalchemy.org/en/20/orm/relationships.html)

# Changelog

All notable changes to SkillForge Global will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed - Critical SQLAlchemy Registry Conflict (2025-11-03)

#### Problem
- Signup endpoint was returning 500 errors with "Unexpected token 'I', Internal S... is not valid JSON" 
- Root cause: SQLAlchemy registry conflict - two classes named `JobApplication`:
  - `app.modelsx.job_application.JobApplication` (job tracker, table: `job_application_tracker`)
  - `app.modelsx.hiring.JobApplication` (hiring platform, table: `job_applications`)
- SQLAlchemy uses Python class names for its registry, causing collision

#### Resolution
- **Renamed**: `app.modelsx.hiring.JobApplication` → `HiringJobApplication`
- **Preserved**: Table name remains `job_applications` for backwards compatibility
- **Updated**: All 20+ references in `app/api/v1x/hiring.py` to use new class name
- **Re-enabled**: Hiring router in `app/main.py` after verification
- **Result**: Backend starts cleanly, all routers mount successfully, signup works

### Added - Module-Qualified Relationship Strings (2025-11-03)

#### Motivation
Prevent future SQLAlchemy registry conflicts by using fully-qualified paths for relationships that could have naming collisions.

#### Changes
- **Hiring relationships** now use fully-qualified paths:
  - `JobPosting.applications` → `"app.modelsx.hiring.HiringJobApplication"`
  - `Interview.application` → `"app.modelsx.hiring.HiringJobApplication"`
  - `TechnicalAssessment.application` → `"app.modelsx.hiring.HiringJobApplication"`
  - `BackgroundCheck.application` → `"app.modelsx.hiring.HiringJobApplication"`

- **User model relationships** now use qualified paths to avoid circular imports:
  - `Mentor.user` → `"app.models.user.User"`
  - `MentorSession.student` → `"app.models.user.User"`
  - `MentorReview.student` → `"app.models.user.User"`
  - `Subscription.user` → `"app.models.user.User"`
  - `MentorChatFile.sender` → `"app.models.user.User"`

### Added - User Model Relationships (2025-11-03)

#### Context
During debugging, `User.mentor_profile` and `User.subscription` relationships were temporarily removed to break circular imports.

#### Resolution
- **Restored** both relationships using string-literal references:
  - `User.mentor_profile` → `relationship("Mentor", back_populates="user", uselist=False)`
  - `User.subscription` → `relationship("Subscription", back_populates="user", uselist=False)`
- **Configured** proper `back_populates` on both sides of relationships
- **Verified** no circular import errors, all tests pass

### Added - Database Migration System (2025-11-03)

#### Infrastructure
- **Added**: Alembic 1.17.1 for schema migrations
- **Configured**: `backend/alembic.ini` to use `DATABASE_URL` from environment
- **Created**: `backend/alembic/env.py` with explicit model imports for autogenerate
- **Generated**: Baseline migration (`4fef0e1df469_initial_migration_with_all_models.py`)
- **Documented**: Class rename in migration (`class_rename_note.py`)
- **Stamped**: Database to current revision (`class_rename_note`)

#### Documentation
- **Created**: `backend/MIGRATIONS.md` - Comprehensive guide for using Alembic
- **Updated**: `README.md` with migration quick commands and Windows port cleanup tips

#### Usage
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Check current revision
alembic current
```

### Added - Error Logging Middleware (2025-11-03)

#### Features
- **Request Logging**: All requests/responses logged with unique request IDs (UUID v4)
- **Request ID Tracking**: 
  - Added to response headers: `X-Request-ID`
  - Included in JSON error responses
- **Exception Handlers**:
  - `validation_exception_handler` - Pydantic validation errors with field details
  - `http_exception_handler` - HTTP exceptions with proper status codes
  - `generic_exception_handler` - Catch-all for unexpected errors
- **Debug Mode**: Full stack traces included when `DEBUG=True` in settings
- **Production Mode**: Sanitized error messages when `DEBUG=False`

#### Implementation
- **Created**: `backend/app/core/logging_middleware.py`
- **Integrated**: Single-line call in `app/main.py`: `setup_logging(app)`
- **Tested**: 3 new tests in `test_error_logging.py` (all passing)

#### Example Log Output
```
2025-11-03 00:36:02,023 - app.core.logging_middleware - INFO - [a8128ff1-c3dd-417c-be0c-68c1990e6dd0] POST /api/v1/auth/signup - Client: testclient
2025-11-03 00:36:02,035 - app.core.logging_middleware - WARNING - [a8128ff1-c3dd-417c-be0c-68c1990e6dd0] Validation error: [...]
2025-11-03 00:36:02,038 - app.core.logging_middleware - INFO - [a8128ff1-c3dd-417c-be0c-68c1990e6dd0] Response: 422
```

### Added - Integration Tests (2025-11-03)

#### Test Files
- **`backend/tests/test_auth_and_hiring.py`**: 
  - Auth flow tests (signup → login → /me)
  - Hiring router presence verification in OpenAPI spec
  - 2 tests, all passing

- **`backend/tests/test_error_logging.py`**:
  - Request ID presence in responses
  - Validation error handling
  - Successful request logging
  - 3 tests, all passing

#### Test Results
- Total: 5 tests
- Status: ✅ All passing
- Coverage: Auth, hiring, error handling

### Added - Developer Documentation (2025-11-03)

#### README Updates
- **Windows PowerShell Commands**: How to free port 8001 using `netstat` and `Taskkill`
- **Database Migrations**: Quick reference for common Alembic commands
- **Backend & Frontend Setup**: Clear instructions for running both servers

#### New Documentation Files
- **`MIGRATIONS.md`**: Complete Alembic usage guide with:
  - Quick start commands
  - Migration workflow best practices
  - Model import requirements
  - Troubleshooting tips
  - Production deployment guidelines
  - Documentation of initial migrations

#### Frontend Configuration
- **Created**: `.env.local` with `NEXT_PUBLIC_API_BASE=http://localhost:8001`
- **Fixed**: TypeScript error in `ResumeEditor.tsx` (made `user_id` optional)
- **Centralized**: API base URL in `src/lib/apiBase.ts`

### Changed - Dependencies (2025-11-03)

#### Added to `backend/requirements.txt`
- `alembic==1.17.1` - Database migration management

#### Already Present (Verified)
- `APScheduler==3.10.4` - Background task scheduling
- `fastapi` - Web framework
- `sqlalchemy` - ORM
- `uvicorn` - ASGI server

## Technical Notes

### SQLAlchemy Registry Management
When using SQLAlchemy with multiple model classes:
- **Class names** must be unique across the entire codebase, not just within modules
- Use **fully-qualified relationship paths** for disambiguation: `relationship("app.modelsx.hiring.HiringJobApplication")`
- Use **string-literal references** to avoid circular imports: `relationship("Mentor")` instead of importing

### Migration Strategy
- **No Alembic migrations were run** - database was stamped to current state
- **All existing data preserved** - only metadata tracking added
- **Future schema changes** should use `alembic revision --autogenerate`

### Circular Import Resolution
- **User model** relationships use string literals to avoid importing from `modelsx`
- **Mentor/Subscription models** use fully-qualified paths back to `app.models.user.User`
- **Pattern**: Cross-module relationships should use qualified paths

## Testing Status

### Backend Tests
- ✅ Auth flow (signup/login/me): **PASSING**
- ✅ Hiring router presence: **PASSING**
- ✅ Error logging (404/validation/success): **PASSING**
- **Total**: 5/5 tests passing

### Manual Verification
- ✅ Backend starts without errors
- ✅ All v1x routers mount successfully (19 routers)
- ✅ No SQLAlchemy registry conflicts
- ✅ No circular import errors
- ✅ Signup endpoint returns 200
- ✅ Hiring router accessible

## Next Steps

### Recommended for Next Sprint
1. **CI/CD Setup**: Add GitHub Actions workflow for automated testing
2. **Linting**: Configure flake8/black for backend, ESLint for frontend
3. **Pre-commit Hooks**: Prevent regressions with automated checks
4. **Production Deployment**: Apply Alembic migrations in staging/production
5. **Monitoring**: Add application performance monitoring (APM)

### Optional Improvements
- Add file-based logging for production (rotate logs daily)
- Implement structured logging with JSON output
- Add request/response body logging (with PII redaction)
- Create health check endpoint with database connectivity test

---

**Contributors**: AI pair programming session (2025-11-03)  
**Session Duration**: ~2 hours  
**Files Changed**: 15+ files across backend and frontend  
**Impact**: Critical signup bug fixed, infrastructure significantly improved

# Quick Commands - v1.1.0 Testing

## Install Frontend Test Dependencies

```powershell
npm install --save-dev @testing-library/react@14 @testing-library/jest-dom@6 @testing-library/user-event@14 @swc/jest@0.2 @swc/core@1.3 jest@29 jest-environment-jsdom@29 next-router-mock@0.9 identity-obj-proxy@3
```

## Run Backend Tests

```powershell
# All tests
cd backend
pytest -v --cov=app --cov-report=html

# Only passing tests
pytest tests/test_auth.py -v

# With detailed output
pytest -vv -s

# Stop on first failure
pytest -x

# Specific test
pytest tests/test_auth.py::TestAuthentication::test_signup_success -v
```

## Run Frontend Tests

```powershell
# After installing dependencies
npm test

# With coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

## Coverage Reports

```powershell
# Backend coverage
cd backend
pytest --cov=app --cov-report=html
start htmlcov\index.html

# Frontend coverage
npm run test:coverage
start coverage\lcov-report\index.html
```

## Git Commands

```powershell
# Commit testing infrastructure
git add .
git commit -m "feat(testing): complete v1.1.0 testing infrastructure

- Add pytest configuration with 80% coverage threshold
- Create 106 backend tests (26 passing, 67 need API alignment)
- Set up Jest for frontend testing
- Enhance CI/CD pipeline with coverage reporting
- Add security scanning and linting jobs"

# Push to trigger CI/CD
git push origin develop
```

## CI/CD Pipeline

```powershell
# View pipeline status
# Visit: https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines

# Download coverage artifacts
# Available in GitLab after pipeline runs
```

## Lint Commands

```powershell
# Frontend lint
npm run lint

# Backend lint (install first)
cd backend
pip install flake8 black isort
flake8 app/ --max-line-length=120
black app/
isort app/
```

## Fix Failing Tests

```powershell
# See TEST_FIX_GUIDE.md for details

# Quick fix for models tests
cd backend\tests
(Get-Content test_models.py) -replace 'hash_password', 'get_password_hash' | Set-Content test_models.py

# Run fixed tests
pytest tests/test_auth.py tests/test_integration.py::TestHealthCheck -v
```

## Clean Up

```powershell
# Remove cache
Remove-Item backend\.pytest_cache -Recurse -Force
Remove-Item backend\htmlcov -Recurse -Force
Remove-Item node_modules\.cache -Recurse -Force

# Remove coverage files
Remove-Item backend\.coverage -Force
Remove-Item coverage -Recurse -Force
```

## Database Reset (Testing)

```powershell
cd backend
Remove-Item app\data\*.db -Force
python -c "from app.core.db import Base, engine; Base.metadata.create_all(bind=engine); print('DB reset')"
```

## Start Dev Servers

```powershell
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
npm run dev

# Terminal 3: Run tests
pytest -v --cov=app
```

## View Test Files

```powershell
# List backend tests
dir backend\tests\test_*.py

# List frontend tests
dir -Recurse src\**\__tests__

# Count tests
pytest --collect-only | Select-String "test session starts"
```

## Quick Status Check

```powershell
# Backend test count
pytest --collect-only -q | Select-String "test"

# Coverage summary
pytest --cov=app --cov-report=term | Select-String "TOTAL"

# Pipeline status
git log --oneline -5
git status
```

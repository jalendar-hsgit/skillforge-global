# Resume Feature Testing Guide

## Overview
Complete testing suite for all resume features including creation, editing, export, AI suggestions, and import functionality.

## Test Structure

### Frontend Tests
Located in `src/components/resume/` and `src/pages/resumes/`

#### 1. **ResumeEditor.test.tsx** - Main Resume Editor Tests
- ✅ Resume creation and basic fields
- ✅ Resume field updates (name, email, phone, location)
- ✅ Toolbar button rendering (Save, Export, Preview, etc.)
- ✅ PDF export with data inclusion
- ✅ DOCX export with data inclusion
- ✅ Export error handling
- ✅ Resume save functionality
- ✅ AI suggestions integration
- ✅ Live preview rendering

**Run**: `npm test -- ResumeEditor.test.tsx`

#### 2. **ResumeImportModal.test.tsx** - Resume Import Tests
- ✅ Modal rendering (open/close states)
- ✅ PDF file upload
- ✅ DOCX file upload
- ✅ File type validation
- ✅ File size validation
- ✅ Resume parsing and preview generation
- ✅ Resume creation from import
- ✅ Error handling (invalid files, API failures)
- ✅ Manual field editing
- ✅ AI-enhanced parsing

**Run**: `npm test -- ResumeImportModal.test.tsx`

#### 3. **resumes.test.tsx** - Resume List Page Tests
- ✅ Resume list display
- ✅ Loading states
- ✅ Empty state handling
- ✅ Navigation to create, import, edit pages
- ✅ Resume duplication
- ✅ Resume deletion with confirmation
- ✅ Error handling
- ✅ Metadata display (template, last updated, views)

**Run**: `npm test -- resumes.test.tsx`

### Backend Tests
Located in `backend/tests/`

#### 1. **test_resume_tools.py** - Resume Export & AI Tests
Tests for PDF/DOCX export and AI-powered suggestions

**Run**: `pytest backend/tests/test_resume_tools.py -v`

**Coverage**:
- PDF export with all resume sections
  - Contact information
  - Work experience
  - Education
  - Skills
  - Projects
- DOCX export with formatted sections
- AI-powered suggestions for different sections
- Error handling (invalid resume ID, authentication, missing sections)
- File generation validation

#### 2. **test_resume_import.py** - Resume Import Tests
Tests for file upload, parsing, and preview generation

**Run**: `pytest backend/tests/test_resume_import.py -v`

**Coverage**:
- PDF upload and parsing
- DOCX upload and parsing
- Resume preview without creation
- Name/email/phone extraction
- Section detection (work, education, skills)
- File validation (type, size, format)
- AI-enhanced parsing
- Error handling (corrupted files, missing libraries)

### End-to-End Tests
Comprehensive validation of complete workflows

#### **e2e_resume_validation.py** - Full Workflow Validation
Interactive script that tests the complete resume workflow

**Run**: `python backend/tests/e2e_resume_validation.py`

**Coverage**:
1. User authentication
2. Resume creation with initial fields
3. Detailed field updates
4. Adding work experience
5. Adding education
6. Adding skills
7. Resume retrieval
8. Resume listing
9. PDF export (with file verification)
10. DOCX export (with file verification)
11. AI suggestions generation

**Prerequisites**:
```bash
# Terminal 1: Start backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Run validation
python backend/tests/e2e_resume_validation.py
```

## Installation & Setup

### Frontend Test Dependencies
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest ts-jest @types/jest
```

### Backend Test Dependencies
Already included in `requirements.txt`:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `requests` - HTTP client for E2E tests

## Running Tests

### Run All Tests
```bash
# Frontend
npm test

# Backend
pytest backend/tests/ -v

# With coverage
pytest backend/tests/ --cov=app --cov-report=html
```

### Run Specific Test Suite
```bash
# Frontend - Resume Editor
npm test -- ResumeEditor.test.tsx

# Frontend - Import Modal
npm test -- ResumeImportModal.test.tsx

# Frontend - Resume List
npm test -- resumes.test.tsx

# Backend - Export/Suggestions
pytest backend/tests/test_resume_tools.py -v

# Backend - Import
pytest backend/tests/test_resume_import.py -v
```

### Run with Coverage
```bash
# Frontend coverage
npm test -- --coverage

# Backend coverage
pytest backend/tests/ --cov=app --cov-report=term-missing --cov-report=html
```

## Test Configuration Files

### Frontend
- **jest.config.js** - Jest configuration with TypeScript support
- **jest.setup.js** - Test environment setup, mocks for Next.js, images, router
- **tsconfig.json** - TypeScript configuration (already present)

### Backend
- **pytest.ini** - Pytest configuration (optional)
- **conftest.py** - Shared fixtures and setup

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Resume Feature Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          npm ci
          pip install -r backend/requirements.txt
      
      - name: Run frontend tests
        run: npm test -- --coverage
      
      - name: Run backend tests
        run: pytest backend/tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Coverage Goals

### Frontend
- **Components**: 80%+ coverage
- **Hooks**: 85%+ coverage
- **Pages**: 75%+ coverage

### Backend
- **API Routes**: 85%+ coverage
- **Services**: 90%+ coverage
- **Models**: 100%+ (data models)

## Common Issues & Solutions

### Frontend Tests
**Issue**: "Cannot find module '@/...'"
- **Solution**: Check moduleNameMapper in jest.config.js

**Issue**: "useRouter is not a function"
- **Solution**: Ensure jest.setup.js is loaded and next/router is mocked

**Issue**: "Timeout - async operations not completing"
- **Solution**: Add longer timeout with `jest.setTimeout(15000)`

### Backend Tests
**Issue**: "No module named 'app'"
- **Solution**: Ensure PYTHONPATH includes backend directory
  ```bash
  export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
  ```

**Issue**: "Database connection failed"
- **Solution**: Check DATABASE_URL environment variable and ensure DB is running

## Manual Testing Checklist

### Resume Creation
- [ ] Create new resume
- [ ] Fill in all fields (name, email, phone, etc.)
- [ ] Add work experience with descriptions
- [ ] Add education history
- [ ] Add skills with proficiency levels
- [ ] Save resume successfully
- [ ] Verify data persists on reload

### Resume Export
- [ ] Export to PDF
  - [ ] File downloads successfully
  - [ ] PDF opens in reader
  - [ ] All sections visible (contact, work, education, skills)
  - [ ] Formatting is clean and professional
- [ ] Export to DOCX
  - [ ] File downloads successfully
  - [ ] Opens in Word/compatible editor
  - [ ] All sections preserved
  - [ ] Formatting matches template

### Resume Import
- [ ] Upload PDF resume
  - [ ] File parses successfully
  - [ ] Preview shows extracted data
  - [ ] Can edit extracted fields
  - [ ] Import creates resume in list
- [ ] Upload DOCX resume
  - [ ] File parses successfully
  - [ ] Extract accuracy verified
  - [ ] Import creates resume with correct data

### AI Features
- [ ] Request suggestions for summary
  - [ ] Suggestions appear
  - [ ] Multiple suggestions offered
  - [ ] Can select and apply suggestions
- [ ] Request suggestions for other sections
  - [ ] Works for experience, education, skills

### Navigation
- [ ] Create New button navigates correctly
- [ ] Import button opens modal
- [ ] Resume list shows all resumes
- [ ] Clicking resume opens editor
- [ ] Delete removes resume from list
- [ ] Duplicate creates copy with new ID

## Performance Benchmarks

### Frontend
- Page load: < 3s
- Export action: < 5s
- Suggestions API call: < 10s

### Backend
- PDF generation: < 2s
- DOCX generation: < 2s
- Resume parsing: < 3s
- Suggestions (with LLM): < 10s

## Future Enhancements

- [ ] Visual regression tests with Percy/Chromatic
- [ ] Performance testing with Lighthouse
- [ ] Accessibility testing with axe-core
- [ ] API load testing with k6
- [ ] Mobile device testing
- [ ] Offline capability testing

## Support

For issues or questions about tests:
1. Check test logs: `npm test -- --verbose`
2. Review test files for similar test cases
3. Check backend logs: `tail -f logs/app.log`
4. Run with debugging: `NODE_DEBUG=* npm test`

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing/)

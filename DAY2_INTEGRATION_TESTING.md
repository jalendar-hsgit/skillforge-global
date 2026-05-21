# Day 2 Frontend Integration Testing Guide

**Status**: Components Created - Ready for Integration Testing
**Backend**: Running at http://localhost:8001
**Frontend**: Running at http://localhost:3002

## Quick Start Testing

### 1. Ensure Both Servers are Running

**Backend (FastAPI)**:
```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Frontend (Next.js)**:
```bash
# From workspace root
npm run dev
```

### 2. Test Authentication Flow

1. Visit http://localhost:3002/login
2. Sign up with test account or login
3. Token should be stored in localStorage
4. Should redirect to dashboard

### 3. Test Profile Pages

#### Profile Display (`/profile`)
- [ ] Page loads without errors
- [ ] ProfileCard shows user data from GET /account/profile
- [ ] Avatar displays (or fallback icon)
- [ ] Contact info displays (email, phone, location)
- [ ] Skills tags display
- [ ] Edit button navigates to /profile/edit

#### Profile Edit (`/profile/edit`)
- [ ] Form loads with current profile data
- [ ] Can edit name field
- [ ] Can edit bio field
- [ ] Can edit phone field
- [ ] Can edit location field
- [ ] Can add/remove skills
- [ ] Save button sends PATCH to /account/profile
- [ ] Success message displays on save
- [ ] Validation errors display properly
- [ ] Back button returns to /profile

#### Settings (`/profile/settings`)
- [ ] Privacy visibility dropdown works
- [ ] Notification toggles work
- [ ] Security toggles work
- [ ] Save button works
- [ ] Settings persist (stored in localStorage)

#### Stats Display (on `/profile`)
- [ ] UserStatsCard loads stats from GET /account/stats
- [ ] Shows sessions_completed count
- [ ] Shows avg_rating (1 decimal)
- [ ] Shows total_hours count
- [ ] Shows courses count (calculated)
- [ ] Shows recent_sessions list if available

### 4. Test Mentor Verification (`/mentors/dashboard/verification`)

- [ ] Page loads without errors
- [ ] VerificationUploadForm displays
- [ ] Can select document type from dropdown
- [ ] Can upload file
- [ ] Shows upload progress
- [ ] Shows success message on completion
- [ ] Fetches and displays verification status
- [ ] Shows file details (name, size, status, submitted_at)
- [ ] Shows error if upload fails
- [ ] FAQ section displays

## API Request/Response Examples

### GET /account/profile
```javascript
// Request
fetch('/api/v1x/account/profile', {
  headers: { 'Authorization': 'Bearer <token>' }
})

// Expected Response (200)
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "bio": "Web developer and mentor",
  "avatar_url": "https://...",
  "phone": "+1 (555) 123-4567",
  "location": "San Francisco, CA",
  "skills": ["React", "Python", "FastAPI"]
}

// Error Response (401)
{ "detail": "Not authenticated" }
```

### PATCH /account/profile
```javascript
// Request
fetch('/api/v1x/account/profile', {
  method: 'PATCH',
  headers: { 
    'Authorization': 'Bearer <token>',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: "John Updated",
    bio: "New bio",
    phone: "+1 (555) 999-9999",
    location: "NYC, NY",
    skills: ["React", "TypeScript", "Node.js"]
  })
})

// Expected Response (200)
{ "id": 1, "email": "user@example.com", ... }

// Error Response (422)
{ "detail": [{"loc": ["body", "name"], "msg": "Field required", "type": "..."}] }
```

### GET /account/stats
```javascript
// Request
fetch('/api/v1x/account/stats', {
  headers: { 'Authorization': 'Bearer <token>' }
})

// Expected Response (200)
{
  "sessions_completed": 5,
  "avg_rating": 4.8,
  "total_hours": 12.5,
  "recent_sessions": [
    { "id": 1, "title": "React Basics", "date": "2024-01-15" }
  ]
}
```

### POST /mentor-verification/upload
```javascript
// Request
const formData = new FormData()
formData.append('file', fileInput.files[0])
formData.append('document_type', 'degree')

fetch('/api/v1x/mentor-verification/upload', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer <token>' },
  body: formData
})

// Expected Response (201)
{
  "id": 1,
  "mentor_id": 1,
  "document_type": "degree",
  "document_url": "uploads/mentor-verifications/...",
  "status": "pending",
  "submitted_at": "2024-01-15T10:30:00",
  "reviewer_notes": null
}

// Error Responses
// (400) Invalid file type
{ "detail": "Only PDF and image files allowed" }
// (413) File too large
{ "detail": "File exceeds 10MB limit" }
```

### GET /mentor-verification/status
```javascript
// Request
fetch('/api/v1x/mentor-verification/status', {
  headers: { 'Authorization': 'Bearer <token>' }
})

// Expected Response (200)
{
  "documents": [
    {
      "id": 1,
      "document_type": "degree",
      "status": "pending",
      "submitted_at": "2024-01-15T10:30:00",
      "file_name": "diploma.pdf",
      "file_size": 2048576
    },
    {
      "id": 2,
      "document_type": "government_id",
      "status": "approved",
      "submitted_at": "2024-01-14T09:00:00",
      "reviewed_at": "2024-01-14T14:30:00",
      "reviewer_notes": "ID verified successfully"
    }
  ],
  "verification_status": "approved"
}
```

## Browser DevTools Checks

### Network Tab
- [ ] All API requests show 200 or 201 status
- [ ] JWT token in Authorization header
- [ ] Content-Type is application/json
- [ ] No CORS errors
- [ ] File uploads use multipart/form-data

### Console
- [ ] No JavaScript errors
- [ ] No TypeScript compilation errors
- [ ] localStorage contains 'token' key
- [ ] No unhandled promise rejections

### Application Tab
- [ ] localStorage has 'token' value
- [ ] No console errors or warnings

## Common Issues & Solutions

### Issue: 401 Unauthorized
- **Cause**: Token missing or expired
- **Fix**: Login again, clear localStorage if needed
- **Check**: `localStorage.getItem('token')` in console

### Issue: CORS Error
- **Cause**: Backend not allowing frontend origin
- **Fix**: Check main.py CORS config includes http://localhost:3002
- **Backend**: `origins=["http://localhost:3002", ...]`

### Issue: File Upload Fails
- **Cause**: Wrong file type or too large
- **Fix**: Use PDF or image < 10MB
- **Check**: Browser console for specific error message

### Issue: Components Don't Load Data
- **Cause**: Backend endpoint not responding
- **Fix**: Verify backend server running at :8001
- **Check**: Try curl: `curl http://localhost:8001/healthz`

### Issue: Styling Looks Wrong
- **Cause**: Tailwind CSS not compiled
- **Fix**: Ensure npm run dev is running for frontend
- **Check**: Check browser console for CSS errors

## Validation Testing

### Profile Form Validation
- [ ] Name field accepts any text
- [ ] Bio field max 500 characters
- [ ] Phone field accepts format +1 (555) 123-4567
- [ ] Location field accepts any city/country
- [ ] Skills array handled correctly
- [ ] Empty skills array allowed

### File Upload Validation
- [ ] Only PDF, JPG, PNG accepted
- [ ] Max 10MB file size enforced
- [ ] File name preserved
- [ ] MIME type checked
- [ ] Error messages clear

## Performance Checks

- [ ] Profile page loads < 2 seconds
- [ ] Form submit completes < 5 seconds
- [ ] File upload shows progress
- [ ] No memory leaks in DevTools
- [ ] Responsive on mobile (375px width)
- [ ] Responsive on tablet (768px width)
- [ ] Responsive on desktop (1200px width)

## Accessibility Checks

- [ ] Form labels properly associated with inputs
- [ ] Required fields marked with *
- [ ] Error messages in red with icon
- [ ] Success messages in green with icon
- [ ] Buttons have visible focus state
- [ ] Tab order logical
- [ ] Icons have alt text or aria-label
- [ ] Placeholder text doesn't replace labels

## Next Steps After Testing

1. **Fix Any Issues** - Debug and fix failures
2. **Add Navigation** - Wire profile link in sidebar
3. **Create Remaining Components** - SessionRatingModal, PaymentForm
4. **Integration Test** - Full user flow from signup to profile
5. **Performance Optimization** - Image optimization, lazy loading
6. **Accessibility Pass** - Full a11y testing

## Quick Test URLs

```
Login: http://localhost:3002/login
Profile: http://localhost:3002/profile
Edit Profile: http://localhost:3002/profile/edit
Settings: http://localhost:3002/profile/settings
Verification: http://localhost:3002/mentors/dashboard/verification
Dashboard: http://localhost:3002/dashboard
```

## Running Cypress E2E Tests (Optional)

```bash
# Install if not already
npm install cypress --save-dev

# Run tests
npx cypress open

# Or headless
npx cypress run
```

Create test file: `cypress/e2e/profile.cy.js`
```javascript
describe('Profile Pages', () => {
  beforeEach(() => {
    cy.login() // Custom command
  })

  it('displays profile data', () => {
    cy.visit('/profile')
    cy.contains('Your Profile').should('be.visible')
  })

  it('allows editing profile', () => {
    cy.visit('/profile/edit')
    cy.get('input[placeholder="John Doe"]').type('Jane Doe')
    cy.contains('Save Changes').click()
    cy.contains('Profile updated').should('be.visible')
  })
})
```

---

**Last Updated**: Day 2 Session 1 Complete
**Ready For**: Backend Integration Testing

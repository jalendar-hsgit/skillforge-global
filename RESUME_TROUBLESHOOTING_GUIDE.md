# Resume Features - Troubleshooting & Quick Fix Guide

**Last Updated**: December 30, 2025

---

## 🔍 Common Issues & Solutions

### Issue 1: Pages Not Loading (404 Error)

**Symptom**: `/resumes/[id]/ats-score` or other pages return 404

**Possible Causes**:
1. Backend is not running
2. API routes not mounted
3. Wrong URL structure

**Solution**:
```bash
# 1. Verify backend is running on port 8001
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 2. Check if routers mounted (look for "Mounted v1x router")
# Should see: Mounted v1x router: ['resumes', 'resume-ai', 'resume-export', etc.]

# 3. Try accessing the page directly:
# http://localhost:3000/resumes  (main list)
# http://localhost:3000/resumes/1/ats-score  (with valid resume ID)
```

---

### Issue 2: PDF Export Not Working

**Symptom**: Click export PDF but nothing happens

**Possible Causes**:
1. Backend export endpoint not responding
2. MIME type not correct
3. Browser blocking download

**Solution**:
```bash
# 1. Test backend export endpoint directly
curl -X GET http://localhost:8001/api/v1x/resumes/1/export?format=pdf \
  -H "Cookie: token=YOUR_AUTH_TOKEN"

# 2. Check if response has content (should be binary PDF)
# If error, check backend logs for details

# 3. Browser console - check for any JavaScript errors
# Open DevTools (F12) → Console tab

# 4. Check browser download settings
# Some browsers block downloads from localhost
```

---

### Issue 3: ATS Score Page Shows "No Analysis Yet"

**Symptom**: ATS Score page loads but shows empty state

**Possible Causes**:
1. ATS analysis endpoint not responding
2. Resume doesn't have any analysis data
3. Wrong resume ID in URL

**Solution**:
```bash
# 1. Click "Re-analyze" button to trigger analysis
# This calls POST /api/v1x/resume-ai/ats-analysis

# 2. Check backend for AI endpoint
# Should have: backend/app/api/v1x/resume_ai.py

# 3. Verify resume exists
curl -X GET http://localhost:8001/api/session/resumes/1 \
  -H "Cookie: token=YOUR_AUTH_TOKEN"

# 4. If resume doesn't exist, create one first
# Visit: http://localhost:3000/resumes/new
```

---

### Issue 4: Version History Empty

**Symptom**: Versions page shows no versions

**Possible Causes**:
1. Versioning not enabled
2. Resume is brand new (first version)
3. Backend versioning endpoint not working

**Solution**:
```bash
# 1. Check if backend has version support
# Backend should import: from app.modelsx.resume_comparison import ResumeVersion

# 2. Verify endpoint responds
curl -X GET http://localhost:8001/api/v1x/resumes/1/versions \
  -H "Cookie: token=YOUR_AUTH_TOKEN"

# 3. Make an edit to resume to create new version
# Edit resume and save changes

# 4. Refresh versions page
```

---

### Issue 5: Templates Page Blank

**Symptom**: Templates page loads but shows no templates

**Possible Causes**:
1. API endpoint returning empty list
2. Frontend fallback templates not loading
3. Backend templates table is empty

**Solution**:
```bash
# 1. Check if template endpoint works
curl -X GET http://localhost:8001/api/v1x/resume-templates \
  -H "Cookie: token=YOUR_AUTH_TOKEN"

# 2. If empty response, check backend
# Should have: backend/app/api/v1x/resume_templates.py

# 3. Frontend has fallback templates (hardcoded)
# If backend fails, should show 6 default templates:
# - Modern
# - Classic
# - Creative
# - Minimal
# - Executive
# - Timeline

# 4. Verify by checking browser console
# Should not see any errors
```

---

### Issue 6: Cannot Compare Resumes

**Symptom**: Compare page shows "Need Multiple Resumes" message

**Possible Causes**:
1. User doesn't have 2+ resumes
2. Resume list not loading
3. Backend endpoint returning empty list

**Solution**:
```bash
# 1. Create at least 2 resumes first
# Visit: http://localhost:3000/resumes/new
# Create 2 different resumes

# 2. Verify resumes exist
curl -X GET http://localhost:8001/api/session/resumes \
  -H "Cookie: token=YOUR_AUTH_TOKEN"

# 3. Refresh compare page
# http://localhost:3000/resumes/compare
```

---

### Issue 7: Share Link Not Working

**Symptom**: Can't generate or copy public share link

**Possible Causes**:
1. Backend share settings endpoint not implemented
2. Browser clipboard API issue
3. Permission denied

**Solution**:
```bash
# 1. Check if share settings endpoint exists
curl -X GET http://localhost:8001/api/v1x/resumes/1/share-settings \
  -H "Cookie: token=YOUR_AUTH_TOKEN"

# 2. If endpoint doesn't exist, backend needs implementation
# Check: backend/app/api/v1x/resumes.py

# 3. Test clipboard permission
# Page must be HTTPS or localhost
# Should work on: http://localhost:3000

# 4. Check browser console for errors
# May need to allow clipboard permission
```

---

### Issue 8: Navigation Link Not Showing

**Symptom**: "My Resumes" link not visible in header

**Possible Causes**:
1. Layout component not updated
2. Browser cache issue
3. Screen too small (mobile)

**Solution**:
```bash
# 1. Verify Layout.tsx updated with /resumes link
# File: src/components/Layout.tsx
# Should contain: { href: '/resumes', label: 'My Resumes', icon: '📄' }

# 2. Clear browser cache
# Ctrl+Shift+Delete (Windows/Linux)
# Cmd+Shift+Delete (Mac)

# 3. Hard refresh
# Ctrl+Shift+R (Windows/Linux)
# Cmd+Shift+R (Mac)

# 4. On mobile, check if nav expanded
# Tap hamburger menu (≡) on small screens

# 5. If still not visible, restart dev server
npm run dev
```

---

## 🧪 Testing Commands

### Quick Backend Check
```bash
# Verify backend is running
curl http://localhost:8001/healthz

# Check if resumes router is mounted
curl http://localhost:8001/api/v1x/resumes \
  -H "Cookie: token=YOUR_AUTH_TOKEN"
```

### Testing Export Formats
```bash
# Test PDF export
curl -X GET http://localhost:8001/api/v1x/resumes/1/export?format=pdf \
  -H "Cookie: token=YOUR_AUTH_TOKEN" \
  -o resume.pdf

# Test DOCX export
curl -X GET http://localhost:8001/api/v1x/resumes/1/export?format=docx \
  -H "Cookie: token=YOUR_AUTH_TOKEN" \
  -o resume.docx

# Test HTML export
curl -X GET http://localhost:8001/api/v1x/resumes/1/export?format=html \
  -H "Cookie: token=YOUR_AUTH_TOKEN" \
  -o resume.html

# Test PNG export
curl -X GET http://localhost:8001/api/v1x/resumes/1/export?format=png \
  -H "Cookie: token=YOUR_AUTH_TOKEN" \
  -o resume.png
```

### Testing ATS Analysis
```bash
# Trigger ATS analysis
curl -X POST http://localhost:8001/api/v1x/resume-ai/ats-analysis \
  -H "Content-Type: application/json" \
  -H "Cookie: token=YOUR_AUTH_TOKEN" \
  -d '{"resume_id": 1}'

# Get ATS score
curl -X GET http://localhost:8001/api/v1x/resume-scoring/score-by-resume/1 \
  -H "Cookie: token=YOUR_AUTH_TOKEN"
```

---

## 🛠️ Manual Fixes

### If Import Error Occurs

**Problem**: `ModuleNotFoundError: cannot import name 'Achievement'`

**File to Fix**: `backend/app/api/v1x/resume_export.py`

```python
# Remove this:
from app.modelsx.resume import (
    Resume, WorkExperience, Education, ResumeProject,
    ResumeSkill, ResumeCertificate, ResumeAchievement,
    Language, Publication, Patent, VolunteerWork, Reference
)

# Replace with this:
from app.modelsx.resume import (
    Resume, WorkExperience, Education, ResumeProject,
    ResumeSkill, ResumeCertificate, ResumeAchievement,
    ResumeTemplate
)
```

### If Database Tables Missing

```bash
# Delete existing database
rm backend/app/data/skillforge.db

# Restart backend - it will recreate tables
cd backend
python -m uvicorn app.main:app --reload
```

### If Frontend Won't Rebuild

```bash
# Clear Next.js cache
rm -rf .next

# Restart dev server
npm run dev
```

---

## 📱 Mobile Testing Checklist

- [ ] All pages load on mobile
- [ ] Navigation menu collapses to hamburger
- [ ] Buttons are touch-friendly (min 44px)
- [ ] Text is readable on small screens
- [ ] Forms are usable on mobile
- [ ] No horizontal scroll needed
- [ ] Quick action buttons still accessible

---

## 🔐 Authentication Issues

**If getting 401 or 403 errors**:

```bash
# 1. Verify you're logged in
curl http://localhost:8001/api/v1x/me \
  -H "Cookie: token=YOUR_AUTH_TOKEN"

# 2. If not logged in, login first
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@skilforge.com","password":"password"}'

# 3. Use the token from response in subsequent requests
curl http://localhost:8001/api/v1x/resumes \
  -H "Cookie: token=TOKEN_FROM_LOGIN"

# 4. Or visit frontend and login normally
# http://localhost:3000/login
```

---

## 📞 Getting Help

**If you encounter issues**:

1. **Check this troubleshooting guide** (you're reading it!)
2. **Check backend logs** - look for error messages
3. **Check frontend console** - F12 → Console tab
4. **Check API responses** - use curl commands above
5. **Review code files** - check for obvious issues
6. **Restart services** - backend and frontend

**Files to review**:
- Frontend pages: `src/pages/resumes/*.tsx`
- Backend routers: `backend/app/api/v1x/resume*.py`
- Backend models: `backend/app/modelsx/resume.py`
- Configuration: `backend/app/core/config.py`

---

## ✅ Pre-Production Checklist

Before going live:

- [ ] All pages load without errors
- [ ] All buttons and links work
- [ ] Forms submit correctly
- [ ] Files download/upload correctly
- [ ] Database has proper backups
- [ ] Environment variables set correctly
- [ ] Security headers configured
- [ ] HTTPS enabled
- [ ] Error logging configured
- [ ] Performance acceptable (< 2s page load)

---

**Last Updated**: December 30, 2025  
**Status**: ✅ Ready for Testing

# Resume Module - Quick Testing Guide

## Quick Start (5 minutes)

### 1. Start Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Expected output:
```
[Init] OK Database initialized with 192 tables
Mounted v1x router: ['Resume Export']
Mounted v1x router: ['Resume Templates']
Mounted v1x router: ['Resume Analytics Events']
INFO: Application startup complete
```

### 2. Start Frontend
```bash
npm run dev
```

Expected output:
```
ready - started server on 0.0.0.0:3000
event - compiled client and server successfully
```

### 3. Test Resume Preview & Download

**Steps:**
1. Navigate to: `http://localhost:3000/resumes/[resume_id]/preview`
   - Replace `[resume_id]` with an actual resume ID (e.g., `/resumes/1/preview`)

2. Look for blue "📥 Download" button in top-right corner

3. Click dropdown arrow to see 3 options:
   - 📄 PDF
   - 📝 Word (.docx)
   - 📋 Text (.txt)

4. Click each format to test:
   - **PDF:** Should download as `[name]_YYYYMMDD.pdf`
   - **DOCX:** Should download as `[name].docx`
   - **TXT:** Should download as `[name]_YYYYMMDD.txt`

5. Open downloaded files to verify content

---

## Manual Testing Checklist

### Template Testing (Test with Each Template)

#### Modern Template
```
✓ Name displays in large bold text
✓ Contact info shows (email, phone, location)
✓ Section titles in blue accent color
✓ Work experience with company, position, dates
✓ Skills grouped by category
✓ All text colors preserved in export
```

#### Minimal Template
```
✓ Clean, uncluttered appearance
✓ Minimal styling, focus on content
✓ Light accent colors
✓ Professional appearance
✓ Easy to read in all formats
```

#### Executive Template
```
✓ Sophisticated layout
✓ Professional appearance
✓ Proper section spacing
✓ Executive-friendly design
```

#### Creative Template
```
✓ Unique styling/design elements
✓ Gradient or special formatting visible
✓ Creative industries appropriate
✓ Stands out visually
```

#### Timeline Template
```
✓ Work experience in timeline format
✓ Chronological order visible
✓ Visual timeline rendering
✓ Clean timeline design
```

#### Elegant Blue Template
```
✓ Blue accent colors applied
✓ Elegant styling
✓ Professional appearance
✓ Premium feel
```

### Export Format Testing

#### PDF Export
```
✓ File downloads automatically
✓ Filename matches resume owner name
✓ Opens in PDF viewer
✓ All text visible and readable
✓ Colors match live preview
✓ Fonts display correctly
✓ Page breaks work for multi-page
✓ Margins are consistent
✓ Ready for printing (A4 size)
✓ No broken elements
```

#### DOCX Export
```
✓ File downloads as .docx
✓ Opens in Microsoft Word
✓ All resume content included
✓ Formatting preserved (bold, bullets)
✓ Section headings visible
✓ Work experience with dates
✓ Skills properly formatted
✓ No corruption or errors
✓ Editable in Word
✓ File size reasonable (~100KB)
```

#### TXT Export
```
✓ File downloads as .txt
✓ Opens in text editor
✓ Plain text format
✓ All content readable
✓ Section headers visible
✓ Bullet points formatted (•)
✓ No special characters broken
✓ ATS-friendly format
✓ Can be copy-pasted
✓ Contact info included
```

### Download Functionality
```
✓ Dropdown menu appears on hover
✓ All 3 format options visible
✓ Each button is clickable
✓ File downloads without dialog
✓ Correct filename used
✓ No console errors (F12)
✓ Multiple downloads work
✓ Works with different templates
✓ Works with different resumes
✓ Analytics event tracked (no console errors)
```

### Integration Testing
```
✓ Frontend loads preview page
✓ Resume data displays correctly
✓ All 6 templates render properly
✓ Live preview is responsive
✓ Print CSS works (Ctrl+P)
✓ Browser print fallback works
✓ Share button works
✓ Refresh button works
✓ Back to editor button works
✓ No JavaScript errors in console
```

---

## Testing with cURL (Advanced)

### Test HTML-to-PDF Endpoint
```bash
# 1. Get a resume first
curl -H "Cookie: token=YOUR_TOKEN" \
  http://localhost:8001/api/session/resumes?id=1

# 2. Export to PDF with HTML capture
curl -X POST http://localhost:8001/api/v1x/resumes/1/export-pdf-from-html \
  -H "Cookie: token=YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Test Resume</h1></body></html>",
    "filename": "test.pdf",
    "page_format": "A4",
    "margins": {"top": 20, "bottom": 20, "left": 20, "right": 20}
  }' \
  --output test.pdf
```

### Test DOCX Export
```bash
curl -H "Cookie: token=YOUR_TOKEN" \
  "http://localhost:8001/api/v1x/resumes/1/export?format=docx" \
  --output resume.docx
```

### Test TXT Export
```bash
curl -H "Cookie: token=YOUR_TOKEN" \
  "http://localhost:8001/api/v1x/resumes/1/export?format=txt" \
  --output resume.txt
```

---

## Browser DevTools Testing

### Network Tab (Check Requests)
1. Open DevTools (F12)
2. Click Network tab
3. Download a resume
4. Look for requests:
   - `export-pdf-from-html` - POST to PDF endpoint
   - `export?format=docx` - GET to DOCX endpoint  
   - `export?format=txt` - GET to TXT endpoint
5. Verify response status is 200 (success)

### Console Tab (Check Errors)
1. Open DevTools (F12)
2. Click Console tab
3. Download a resume
4. Should see:
   - No error messages
   - Possible debug message: "Analytics tracking failed" (if analytics down)
5. Verify file downloads complete

### Application Tab (Check Cookies)
1. Open DevTools (F12)
2. Click Application tab
3. Click Cookies
4. Verify `token` cookie exists
5. Token should be HttpOnly (not visible in JS)

---

## Troubleshooting

### Issue: "Resume not found" error
**Solution:**
- Verify resume ID is correct
- Check you're logged in (should have `token` cookie)
- Verify resume belongs to your account

### Issue: PDF export returns 500 error
**Solution:**
- Check backend console for Playwright error
- Verify Playwright is installed: `pip list | grep playwright`
- Try DOCX export (uses ReportLab fallback)

### Issue: File downloads but won't open
**Solution:**
- Check file size: should be >0 bytes
- Try with different template
- Try with different resume
- Check file is not corrupted (try opening in different app)

### Issue: Downloads not tracked in analytics
**Solution:**
- Check analytics endpoint is running
- Check browser console for errors
- Verify user_id and resume_id are set
- Check network tab that analytics request was sent

### Issue: Dropdown menu doesn't appear
**Solution:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh page (Ctrl+Shift+R)
- Check browser supports CSS :hover (should)
- Try different browser

### Issue: Special characters in filename causing errors
**Solution:**
- Filename should be sanitized automatically
- If issue persists, reload backend
- Check resume full_name field has valid characters

---

## Database Validation

### Check Resume Data
```bash
# Connect to SQLite database
sqlite3 backend/app.db

# List all resumes
SELECT id, full_name, title, template_id, downloads FROM resumes;

# Check specific resume
SELECT * FROM resumes WHERE id = 1;

# Check resume relationships
SELECT * FROM work_experiences WHERE resume_id = 1;
SELECT * FROM education WHERE resume_id = 1;
SELECT * FROM skills WHERE resume_id = 1;
```

### Check Analytics Events
```bash
# Check download events
SELECT resume_id, event_type, COUNT(*) as count 
FROM resume_analytics_events 
GROUP BY resume_id, event_type;

# Check latest downloads
SELECT resume_id, event_type, created_at 
FROM resume_analytics_events 
WHERE event_type = 'download' 
ORDER BY created_at DESC LIMIT 10;
```

---

## Performance Testing

### Test PDF Generation Time
```javascript
// Open browser console on preview page
const startTime = performance.now();
// Click PDF export button
// Check console for completion time
```

Expected times:
- PDF: 2-5 seconds (includes Chromium launch)
- DOCX: 500-1000ms
- TXT: 100-300ms

### Test Multiple Downloads
1. Download PDF 5 times
2. Check download counter increments: `resume.downloads`
3. Verify all files are valid
4. Check analytics events recorded

---

## Success Criteria

### ✅ All Tests Passing
- [ ] All 6 templates render in preview
- [ ] All 6 templates export to PDF
- [ ] All 6 templates export to DOCX
- [ ] All 6 templates export to TXT
- [ ] PDF files open correctly
- [ ] DOCX files open in Word
- [ ] TXT files open in editor
- [ ] Download filenames are correct
- [ ] Analytics events recorded
- [ ] No console errors
- [ ] All UI elements responsive
- [ ] Browser print fallback works

### ✅ Production Ready
- [ ] All tests passing
- [ ] No performance issues
- [ ] No memory leaks
- [ ] Error handling robust
- [ ] Security validation complete
- [ ] Database integrity verified
- [ ] API endpoints documented
- [ ] Code reviewed and tested

---

## Quick Commands Reference

```bash
# Start backend
cd backend && uvicorn app.main:app --reload --port 8001

# Start frontend
npm run dev

# Check backend logs
tail -f backend.log

# Test resume preview
curl -H "Cookie: token=TOKEN" http://localhost:8001/api/v1x/resumes/1/preview

# List all templates
curl http://localhost:8001/api/v1x/resume-templates

# Check API health
curl http://localhost:8001/healthz

# View database resume count
sqlite3 backend/app.db "SELECT COUNT(*) FROM resumes;"
```

---

**Created:** [Current Date]
**Status:** Ready for Testing
**Version:** 1.0
**Support:** See RESUME_MODULE_FIX_SUMMARY.md for detailed documentation

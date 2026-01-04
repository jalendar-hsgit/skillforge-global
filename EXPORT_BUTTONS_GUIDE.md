# Resume Export - How to Access the 4 Format Buttons

## Issue
User reported not seeing 4 format buttons on the export page.

## Root Cause Analysis
✅ **Code Status: VERIFIED WORKING**
- Backend export handlers: PDF ✓, DOCX ✓, HTML ✓, PNG ✓, TXT ✓
- Frontend export.tsx: All 4 buttons defined ✓
- All button labels present ✓
- Button rendering logic in place ✓

## Steps to View the 4 Buttons

### 1. **Ensure Both Services Running**
```powershell
# Check backend (Python)
Get-Process -Name python | Where-Object {$_.StartTime -gt (Get-Date).AddMinutes(-5)}

# Check frontend (Node)  
Get-Process -Name node | Where-Object {$_.StartTime -gt (Get-Date).AddMinutes(-5)}

# Both should show running processes
```

### 2. **Clear Frontend Cache & Rebuild** (If buttons still not visible)
```bash
cd "D:\python code\sfg\skillforge-global"

# Kill frontend processes
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force

# Rebuild and restart
npm run build
npm run dev
```

### 3. **Login to Application**
- Go to: http://localhost:3002
- Login with your account credentials
- Make sure you have at least one resume created

### 4. **Navigate to Export Page**
The export page URL format is:
```
http://localhost:3002/resumes/[RESUME_ID]/export
```

**Examples:**
- `http://localhost:3002/resumes/1/export` - First resume
- `http://localhost:3002/resumes/4/export` - Fourth resume

### 5. **What You Should See**
You should see a page with:

**Section: "Choose Format" (2-column grid)**
```
┌─────────────────┐  ┌─────────────────┐
│ 📄 PDF Document │  │ 📄 Microsoft    │
│ Universal       │  │ Word            │
│ format          │  │ Editable        │
│ [Export as PDF] │  │ document        │
│                 │  │ [Export as DOCX]│
└─────────────────┘  └─────────────────┘

┌─────────────────┐  ┌─────────────────┐
│ 🌐 HTML File    │  │ 🖼️ PNG Image    │
│ Web-friendly    │  │ Social media    │
│ format          │  │ friendly        │
│ [Export as HTML]│  │ [Export as PNG] │
└─────────────────┘  └─────────────────┘
```

### 6. **Click Any Button to Test**
Each button should:
1. Show "Exporting..." spinner while processing
2. Download the file in the selected format
3. Show success alert: "Resume exported as PDF/DOCX/HTML/PNG"

## If Buttons Still Not Visible

### Check 1: Verify Page is Loading
Open browser DevTools (F12) and check:
- Console for errors (should be empty)
- Network tab - verify export.tsx loads
- Check that exportOptions has 4 items

### Check 2: Check Resume Exists
```bash
# Test: Get your resumes
curl -s http://localhost:8001/api/v1x/resumes \
  -H "Cookie: token=YOUR_TOKEN" | python -m json.tool

# Look for at least one resume in the list
```

### Check 3: Frontend Build Issue
If buttons defined but not showing:
```bash
# Full rebuild
cd "D:\python code\sfg\skillforge-global"
rm -r .next
npm run build
npm run dev
```

## Button Functionality

### PDF Export
- **Endpoint**: `GET /api/v1x/resumes/{id}/export?format=pdf`
- **Uses**: Playwright for rendering + PDF conversion
- **Output**: Professional PDF matching the live preview
- **Filename**: `resume_title_YYYYMMDD.pdf`

### DOCX Export
- **Endpoint**: `GET /api/v1x/resumes/{id}/export?format=docx`
- **Uses**: python-docx for Word document generation
- **Output**: Editable .docx file
- **Filename**: `resume_title_YYYYMMDD.docx`

### HTML Export (NEW)
- **Endpoint**: `GET /api/v1x/resumes/{id}/export?format=html`
- **Uses**: Template engine with styled HTML
- **Output**: Web-friendly HTML file with CSS
- **Filename**: `resume_title_YYYYMMDD.html`

### PNG Export (NEW)
- **Endpoint**: `GET /api/v1x/resumes/{id}/export?format=png`
- **Uses**: Playwright screenshot at 1024x1400px
- **Output**: High-quality PNG image of full resume
- **Filename**: `resume_title_YYYYMMDD.png`
- **Perfect for**: LinkedIn, Twitter, social media profiles

## Technical Details

### Frontend Component: `src/pages/resumes/[id]/export.tsx`
- Lines 19-69: Define all 4 export options
- Lines 87-120: Handle export button clicks  
- Lines 169-189: Render buttons in grid layout
- Each button:
  - Has unique format identifier
  - Shows correct icon (PDF, Word, HTML, Image)
  - Displays descriptive text
  - Calls backend export endpoint
  - Triggers browser download

### Backend Endpoints: `backend/app/api/v1x/resume_export.py`
- **Line 139**: Main `export_resume()` router
- **Line 221**: `export_pdf()` - Playwright-based PDF
- **Line 577**: `export_pdf_reportlab()` - Fallback PDF
- **Line 921**: `export_docx()` - Word generation
- **Line 1112**: `export_txt()` - Plain text
- **Line 1268**: `export_html()` - HTML export (NEW)
- **Line 1290**: `export_png()` - PNG screenshot (NEW)

## Troubleshooting Checklist

- [ ] Both backend and frontend services are running
- [ ] You are logged in to the application
- [ ] You have at least one resume created
- [ ] You navigated to `/resumes/[ID]/export` (with actual resume ID)
- [ ] Browser DevTools show no errors in console
- [ ] Page loads correctly (header, sections visible)
- [ ] All 4 buttons are visible in the "Choose Format" section
- [ ] Buttons are clickable and show loading state
- [ ] Files download successfully

If you still don't see the buttons after checking all these items, please share:
1. The exact URL you're visiting
2. A screenshot of what you see
3. Browser console errors (F12 → Console tab)

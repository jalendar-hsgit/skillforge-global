# Resume Module - Comprehensive Test Script

## 🎯 Pre-Test Setup

### 1. Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 2. Start Frontend
```bash
cd ..
npm run dev
# This starts Next.js on http://localhost:3000
```

### 3. Browser Console Setup
Keep developer console open (F12) throughout testing to catch errors

---

## ✅ Test Suite 1: Live Preview Display

**Location**: `http://localhost:3000/resumes/[id]/edit`

### Test 1.1: Preview Shows Full Width
**Steps**:
1. Open any resume in editor mode
2. Look at the "Live Preview" panel on the right side
3. **Expected**: Should see FULL resume from top to bottom (not cut off on right)
4. **Check**: Can see all sections: header, experience, education, skills, etc.

**Pass Criteria**: ✅ Entire resume visible, no horizontal scroll needed for preview itself

---

### Test 1.2: Zoom Controls Work
**Steps**:
1. Look for zoom buttons (+ / - / reset / fullscreen)
2. Click zoom in (+) button
3. **Expected**: Preview scales up smoothly
4. Click zoom out (-) button
5. **Expected**: Preview scales down smoothly
6. Click reset button
7. **Expected**: Returns to default zoom

**Pass Criteria**: ✅ All zoom buttons responsive, no glitches

---

### Test 1.3: Fullscreen Mode Works
**Steps**:
1. Click fullscreen button on preview
2. **Expected**: Preview expands to full screen
3. **Expected**: Can still see all content
4. Press Escape to exit fullscreen
5. **Expected**: Returns to normal editor view

**Pass Criteria**: ✅ Fullscreen mode works, content visible in all views

---

### Test 1.4: Preview Updates in Real-Time
**Steps**:
1. Open resume editor with live preview visible
2. Change resume title in the editor
3. **Expected**: Title changes instantly in preview
4. Change a section heading
5. **Expected**: Heading updates immediately in preview
6. Change color/font settings
7. **Expected**: Styling updates in real-time

**Pass Criteria**: ✅ All changes reflect instantly in preview

---

## ✅ Test Suite 2: Template Application

**Location 1**: `http://localhost:3000/resumes/templates`
**Location 2**: Resume editor

### Test 2.1: Browse Templates
**Steps**:
1. Go to `/resumes/templates`
2. **Expected**: See grid of 30 templates
3. **Expected**: See category filter buttons (Modern, Classic, Creative, Executive, Medical, Tech)
4. Click on category filter
5. **Expected**: Templates filtered by category

**Pass Criteria**: ✅ All 30 templates visible, filtering works

---

### Test 2.2: Create New Resume from Template
**Steps**:
1. On templates page, find a template (e.g., "Modern Blue")
2. Click "Create with This" button
3. **Expected**: Navigates to new resume creation
4. **Expected**: Resume created with selected template applied
5. Check resume in list
6. **Expected**: Resume has correct template styling

**Pass Criteria**: ✅ New resume created with proper template_id

---

### Test 2.3: Apply Template to Existing Resume
**Steps**:
1. Go to resume list: `/resumes`
2. Open any resume in editor
3. Look for "Change Template" or "Apply Template" option in editor
4. Select a different template
5. Click "Apply"
6. **Expected**: Styling changes immediately (colors, fonts, layout)
7. **Expected**: Content (experience, skills, etc.) remains unchanged
8. **Expected**: Success message appears

**Pass Criteria**: ✅ Template styling applied, content preserved

---

### Test 2.4: Template Styling Applied Correctly
**Steps**:
1. Apply a template to a resume
2. Check in live preview:
   - Layout matches template (single column, two column, sidebar)
   - Colors match template (accent color, theme)
   - Font matches template choice
   - Picture style matches (circle, square, etc.)

**Pass Criteria**: ✅ All styling attributes match selected template

---

## ✅ Test Suite 3: Resume Duplication

**Location**: `http://localhost:3000/resumes`

### Test 3.1: Duplicate Button Visible
**Steps**:
1. Go to resume list
2. Hover over a resume card
3. **Expected**: See action buttons (Edit, Preview, Duplicate, Delete, etc.)
4. **Expected**: Duplicate button present and clickable

**Pass Criteria**: ✅ Duplicate button visible and accessible

---

### Test 3.2: Duplicate Creates Copy
**Steps**:
1. Click duplicate button on a resume
2. **Expected**: Success message appears
3. **Expected**: New resume added to list
4. **Expected**: New resume title has "(Copy)" suffix
5. Open the duplicated resume
6. **Expected**: All content identical to original

**Pass Criteria**: ✅ Complete copy created with all content

---

### Test 3.3: Duplicated Content Complete
**Steps**:
1. Duplicate a resume
2. Open duplicated resume in editor
3. Check all sections:
   - Personal info (name, email, phone, etc.)
   - Work experience with all details
   - Education with all details
   - Skills
   - Projects
   - Certificates
   - Achievements
4. **Expected**: Everything matches original

**Pass Criteria**: ✅ All content fields duplicated correctly

---

### Test 3.4: Duplicate Has Independent Settings
**Steps**:
1. Duplicate a resume
2. Open the copy in editor
3. Change styling (template, colors, fonts)
4. **Expected**: Original resume unchanged
5. Go back to original
6. **Expected**: Original has original styling

**Pass Criteria**: ✅ Copies are independent instances

---

## ✅ Test Suite 4: Resume Import

**Location**: `http://localhost:3000/resumes/import`

### Test 4.1: Import Page Accessible
**Steps**:
1. Go to `/resumes` list
2. Click "Import Resume" button
3. **Expected**: Import modal opens
4. **Expected**: See file upload area

**Pass Criteria**: ✅ Import interface accessible

---

### Test 4.2: File Upload Works
**Steps**:
1. Have a sample PDF or DOCX resume file ready
2. Drag and drop into import area OR click to browse
3. Select your resume file
4. **Expected**: File accepted
5. **Expected**: Preview shows extracted data

**Pass Criteria**: ✅ File upload works for PDF and DOCX

---

### Test 4.3: Data Extraction Works
**Steps**:
1. After file upload, check extracted fields:
   - Full name
   - Email
   - Phone
   - Professional summary
   - Work experience (all entries)
   - Education (all entries)
   - Skills
   - Projects
2. **Expected**: All major fields extracted

**Pass Criteria**: ✅ All important fields extracted from file

---

### Test 4.4: Imported Resume Complete
**Steps**:
1. Complete import
2. Open imported resume in editor
3. Verify all sections populated:
   - Header with contact info
   - Work experience complete
   - Education complete
   - Skills populated
   - Other sections if they existed

**Pass Criteria**: ✅ Imported resume has all data, no fields lost

---

## ✅ Test Suite 5: Export Functionality

**Location**: Resume editor or preview

### Test 5.1: Export Menu Available
**Steps**:
1. Open any resume
2. Click export button
3. **Expected**: See 4 format options
   - PDF
   - DOCX (Word)
   - HTML
   - PNG

**Pass Criteria**: ✅ All 4 export formats available

---

### Test 5.2: PDF Export Works
**Steps**:
1. Click "Export as PDF"
2. **Expected**: PDF downloads
3. Open PDF file
4. **Expected**: Looks professional, all content visible
5. **Expected**: Formatting matches live preview

**Pass Criteria**: ✅ PDF quality good, content preserved

---

### Test 5.3: DOCX Export Works
**Steps**:
1. Click "Export as DOCX"
2. **Expected**: Word document downloads
3. Open in Microsoft Word or similar
4. **Expected**: Fully editable
5. **Expected**: All content present and formatted

**Pass Criteria**: ✅ DOCX is editable, content preserved

---

### Test 5.4: HTML Export Works
**Steps**:
1. Click "Export as HTML"
2. **Expected**: HTML file downloads
3. Open in browser
4. **Expected**: Web version looks good
5. **Expected**: Can save as web page

**Pass Criteria**: ✅ HTML renders correctly

---

### Test 5.5: PNG Export Works
**Steps**:
1. Click "Export as PNG"
2. **Expected**: Image file downloads
3. Open image
4. **Expected**: Looks like screenshot of resume
5. **Expected**: Text readable, formatting clear

**Pass Criteria**: ✅ PNG image quality good

---

## ✅ Test Suite 6: Navigation & Buttons

**Location**: Various

### Test 6.1: Create New Resume
**Steps**:
1. Go to `/resumes`
2. Click "Create New Resume" button
3. **Expected**: Navigates to new resume creation
4. **Expected**: Can select template
5. **Expected**: Resume created successfully

**Pass Criteria**: ✅ New resume creation works

---

### Test 6.2: Edit Resume
**Steps**:
1. From resume list, click "Edit" on a resume
2. **Expected**: Opens editor
3. **Expected**: Can modify all fields

**Pass Criteria**: ✅ Edit functionality works

---

### Test 6.3: Preview Resume
**Steps**:
1. From resume list, click "Preview"
2. **Expected**: Shows full-page preview
3. **Expected**: Read-only view
4. Can navigate back to list

**Pass Criteria**: ✅ Preview mode works

---

### Test 6.4: Delete Resume
**Steps**:
1. From resume list, click "Delete" on a resume
2. **Expected**: Confirmation dialog
3. Click "Confirm"
4. **Expected**: Resume deleted
5. **Expected**: Removed from list

**Pass Criteria**: ✅ Delete works with confirmation

---

### Test 6.5: Compare Resumes
**Steps**:
1. Go to resume list
2. Select multiple resumes (checkbox)
3. Click "Compare" button
4. **Expected**: Comparison view opens
5. **Expected**: Can see differences side-by-side

**Pass Criteria**: ✅ Comparison feature works

---

## ✅ Test Suite 7: ATS Scoring

**Location**: Resume editor or dedicated page

### Test 7.1: ATS Score Available
**Steps**:
1. Open resume in editor
2. Look for "ATS Score" tab or section
3. **Expected**: Score displayed (0-100)

**Pass Criteria**: ✅ ATS score visible

---

### Test 7.2: ATS Score Calculation
**Steps**:
1. Check ATS score on a resume
2. Change content significantly
3. **Expected**: Score updates
4. Add more keywords
5. **Expected**: Score improves

**Pass Criteria**: ✅ Score responds to content changes

---

### Test 7.3: ATS Recommendations
**Steps**:
1. View ATS report
2. **Expected**: See recommendations for improvement
3. **Expected**: Specific suggestions provided

**Pass Criteria**: ✅ Actionable recommendations shown

---

## ✅ Test Suite 8: Database & Persistence

**Location**: Backend verification

### Test 8.1: Resume Saved to Database
**Steps**:
1. Create a new resume with unique name
2. Refresh page
3. **Expected**: Resume still exists
4. **Expected**: All data preserved

**Pass Criteria**: ✅ Data persists across sessions

---

### Test 8.2: Template Applied Persists
**Steps**:
1. Apply template to resume
2. Refresh page
3. **Expected**: Template styling still applied
4. **Expected**: Template choice saved

**Pass Criteria**: ✅ Template selection persists

---

### Test 8.3: Duplicated Resume Independent
**Steps**:
1. Duplicate a resume
2. Modify the original
3. Check the copy
4. **Expected**: Copy unchanged
5. Modify the copy
6. **Expected**: Original unchanged

**Pass Criteria**: ✅ Copies are separate database records

---

## 🔍 Error Testing

### Test E1: Invalid Template Selection
**Steps**:
1. Try to apply non-existent template ID
2. **Expected**: Error message
3. **Expected**: Resume unchanged

**Pass Criteria**: ✅ Graceful error handling

---

### Test E2: Duplicate without Permissions
**Steps**:
1. Try to duplicate someone else's resume (if applicable)
2. **Expected**: Denied with error
3. **Expected**: No copy created

**Pass Criteria**: ✅ Access control works

---

### Test E3: Export Large Resume
**Steps**:
1. Create resume with lots of content
2. Try to export
3. **Expected**: No timeout
4. **Expected**: Export succeeds

**Pass Criteria**: ✅ Large file handling works

---

## 📊 Test Summary Template

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 1.1 | Preview Full Width | ⬜ | |
| 1.2 | Zoom Controls | ⬜ | |
| 1.3 | Fullscreen Mode | ⬜ | |
| 1.4 | Real-time Updates | ⬜ | |
| 2.1 | Browse Templates | ⬜ | |
| 2.2 | Create from Template | ⬜ | |
| 2.3 | Apply to Existing | ⬜ | |
| 2.4 | Styling Correct | ⬜ | |
| 3.1 | Duplicate Button | ⬜ | |
| 3.2 | Duplicate Creates Copy | ⬜ | |
| 3.3 | Content Complete | ⬜ | |
| 3.4 | Independent Copies | ⬜ | |
| 4.1 | Import Accessible | ⬜ | |
| 4.2 | File Upload Works | ⬜ | |
| 4.3 | Data Extraction | ⬜ | |
| 4.4 | Imported Complete | ⬜ | |
| 5.1 | Export Menu | ⬜ | |
| 5.2 | PDF Export | ⬜ | |
| 5.3 | DOCX Export | ⬜ | |
| 5.4 | HTML Export | ⬜ | |
| 5.5 | PNG Export | ⬜ | |
| 6.1 | Create New | ⬜ | |
| 6.2 | Edit Resume | ⬜ | |
| 6.3 | Preview Resume | ⬜ | |
| 6.4 | Delete Resume | ⬜ | |
| 6.5 | Compare Resumes | ⬜ | |
| 7.1 | ATS Score | ⬜ | |
| 7.2 | Score Calculation | ⬜ | |
| 7.3 | Recommendations | ⬜ | |
| 8.1 | Data Persistence | ⬜ | |
| 8.2 | Template Persists | ⬜ | |
| 8.3 | Copy Independence | ⬜ | |
| E1 | Invalid Template | ⬜ | |
| E2 | Permission Check | ⬜ | |
| E3 | Large Resume | ⬜ | |

**Legend**: ⬜ = Not Started | 🟨 = In Progress | ✅ = Passed | ❌ = Failed

---

## 📝 Notes for Testers

1. **Clear Cache**: Between tests, clear browser cache (Ctrl+Shift+Delete) to ensure latest code
2. **Check Console**: Keep browser dev console open - report any JavaScript errors
3. **Network Tab**: Check Network tab for failed API calls (should be 200/201 status)
4. **Test Data**: Don't be afraid to create/modify test resumes
5. **Revert Changes**: Each test should clean up after itself or not rely on previous state
6. **Report Issues**: If any test fails, note the exact steps and error messages

---

## 🚀 Final Checklist Before Deployment

- [ ] All 35 tests pass (or documented as known issues)
- [ ] No JavaScript errors in console
- [ ] No network errors (all API calls successful)
- [ ] Live preview shows complete resume
- [ ] Template application works end-to-end
- [ ] Duplication creates full copies
- [ ] All export formats work
- [ ] Data persists across sessions
- [ ] No regressions to previous functionality
- [ ] Performance acceptable (page loads < 3 seconds)

---

**Created**: December 31, 2025
**Status**: Ready for Testing ✅


# Resume Module - Comprehensive Audit & Fix Plan

**Status**: 🔴 CRITICAL - Multiple issues identified requiring systematic fixes
**Priority**: 🎯 P0 - Core user feature

## 📋 Issues Identified

### 1. **Frontend Issues**

#### 1.1 Live Preview Card Display (CRITICAL)
- **Issue**: Half display of live preview card
- **Location**: `src/components/resume/LiveTemplatePreview.tsx`
- **Root Cause**: 
  - Container width calculation issues
  - Scale transform not properly accounting for container constraints
  - Missing width constraints on preview card
- **Impact**: Users can't see full resume preview while editing
- **Fix Status**: ⏳ PENDING

#### 1.2 Resume Import Page - Data Not Fully Imported
- **Issue**: Imported resume missing some fields (templates, layouts, styling)
- **Location**: `src/pages/resumes/import.tsx` + `src/components/resume/ResumeImportModal.tsx`
- **Root Cause**:
  - ResumeImportModal not parsing all resume fields from PDF/DOCX
  - Missing field mapping for: template_id, font_family, color_theme, layout, accent_color
  - No validation of imported data before saving
- **Impact**: Imported resumes don't preserve original formatting
- **Fix Status**: ⏳ PENDING

#### 1.3 Resume List Page - Missing Buttons/Actions
- **Issue**: Some action buttons not working (duplicate, compare, advanced features)
- **Location**: `src/pages/resumes/index.tsx` (line 71 onwards)
- **Root Cause**:
  - Duplicate endpoint: `handleDuplicate` calls wrong path `/api/session/v1x/resumes/` (should be `/api/session/resumes/`)
  - Missing compare button implementation
  - Missing advanced features (version history, sharing, ATS score)
- **Impact**: Users can't manage their resumes properly
- **Fix Status**: ⏳ PENDING

#### 1.4 New Resume Page - Template Not Applied on Creation
- **Issue**: Template parameter passed but not creating resume with correct template_id
- **Location**: `src/pages/resumes/new.tsx` (lines 30-45)
- **Root Cause**: 
  - Correct fix was applied (now sending template_id) ✅
  - But needs verification that backend respects it
- **Impact**: Templates not being applied to new resumes
- **Fix Status**: ⏳ PENDING VERIFICATION

#### 1.5 Edit Page - Navigation Issues
- **Issue**: Edit and preview page navigation inconsistent
- **Location**: `src/pages/resumes/[id]/edit.tsx`
- **Root Cause**: Missing robust error handling for resume not found
- **Impact**: Users redirected unexpectedly
- **Fix Status**: ⏳ PENDING

### 2. **Backend Issues**

#### 2.1 Resume Creation - template_id Field
- **Issue**: Resume created but template_id might not be saved correctly
- **Location**: `backend/app/api/v1x/resumes.py` (line 39-48)
- **Root Cause**: Schema accepts template_id but verify it's properly passed to model
- **Impact**: Template selection during creation ignored
- **Fix Status**: ⏳ PENDING VERIFICATION

#### 2.2 Missing Premium Features
- **Issue**: No endpoints for advanced features
- **Location**: `backend/app/api/v1x/` directory
- **Missing**:
  - Resume comparison endpoint (partially exists)
  - Version history endpoint (partially exists)
  - Resume sharing with permissions
  - Advanced ATS scoring
  - Multi-page resume support
  - Template application to existing resumes
- **Impact**: Can't offer premium features
- **Fix Status**: ⏳ PENDING

#### 2.3 Resume Import - Field Mapping
- **Issue**: No backend endpoint to properly parse and import resume data
- **Location**: Missing or incomplete in `backend/app/api/v1x/resume_import.py`
- **Root Cause**: Parser doesn't extract all fields (template, styling, etc.)
- **Impact**: Imported resumes lose formatting
- **Fix Status**: ⏳ PENDING

#### 2.4 Database Schema Issues
- **Issue**: Resume model might be missing fields
- **Location**: `backend/app/modelsx/resume.py`
- **Current**: Has template_id field ✅ 
- **Still Missing**:
  - [ ] sections_order (custom section ordering)
  - [ ] enabled_sections (which sections to show)
  - [ ] import_source (where resume was imported from)
  - [ ] original_template (track original when imported)
- **Fix Status**: ⏳ PENDING

## 🎯 Fix Priorities

### Phase 1: Critical Bugs (Today)
1. Fix live preview card half display
2. Fix resume list duplicate button
3. Fix resume import field mapping
4. Verify template_id is saved on creation

### Phase 2: Missing Features (This week)
1. Implement resume comparison fully
2. Implement version history fully
3. Add template application endpoint
4. Add resume sharing with permissions

### Phase 3: Premium Features (Next week)
1. Advanced ATS scoring
2. Multi-page resume support
3. AI-powered content suggestions
4. Resume analytics

## 📊 Affected Components

### Frontend
```
src/pages/resumes/
├── index.tsx              [🔴 Missing features]
├── import.tsx             [🔴 Data loss]
├── new.tsx                [🟡 Needs verification]
├── [id]/
│   ├── edit.tsx          [🟡 Error handling]
│   ├── preview.tsx       [✅ Working]
│   ├── export.tsx        [✅ Working]
│   ├── ats-score.tsx     [✅ Working]
│   ├── versions.tsx      [🟡 Incomplete]
│   └── sharing.tsx       [🟡 Incomplete]
└── templates.tsx         [✅ Fixed in previous session]

src/components/resume/
├── ResumeEditor.tsx      [🟡 Preview display]
├── LiveTemplatePreview.tsx [🔴 Half display bug]
├── ResumePreview.tsx     [✅ Working]
├── ResumeImportModal.tsx [🔴 Field mapping]
└── ExportOptionsModal.tsx [✅ Working - PDF/DOCX/HTML/PNG]
```

### Backend
```
backend/app/api/v1x/
├── resumes.py           [🟡 Needs verification]
├── resume_templates.py  [✅ Working - fixed in previous session]
├── resume_import.py     [🔴 Incomplete]
├── resume_export.py     [✅ Working]
├── resume_comparison.py [🟡 Incomplete]
└── (missing) premium features endpoints
```

## 🔧 Specific Code Fixes Needed

### Fix 1: LiveTemplatePreview Half Display
```
Problem: width: '100%' combined with scale transform causing overflow
Location: src/components/resume/LiveTemplatePreview.tsx line ~230
Solution: 
- Add max-width constraint to preview container
- Calculate available width properly
- Adjust scale to fit within bounds
```

### Fix 2: Resume List Duplicate Button
```
Problem: handleDuplicate calls /api/session/v1x/resumes/ (wrong path)
Location: src/pages/resumes/index.tsx line 71
Current: `/api/session/v1x/resumes/${resumeId}/duplicate`
Correct: `/api/session/resumes?id=${resumeId}&action=duplicate` (if proxy exists)
OR: Create proper backend endpoint
```

### Fix 3: Resume Import Field Mapping
```
Missing fields in import:
- template_id (which template was this resume using)
- font_family
- color_theme
- layout
- accent_color
- picture_style
- sections_order (if custom)

Need to:
1. Update ResumeImportModal to extract these from PDF/DOCX metadata
2. Or have backend detect and set defaults
3. Store import_source for tracking
```

### Fix 4: Template Application Endpoint
```
Missing: PUT /api/v1x/resumes/{id}/apply-template/{template_id}
Needs to:
- Load template configuration
- Apply layout, colors, fonts to resume
- Preserve content while changing presentation
- Return updated resume object
```

## ✅ Working Features (DO NOT BREAK)

- ✅ Resume templates display (30 seeded)
- ✅ Create resume with template_id parameter
- ✅ Export to PDF/DOCX/HTML/PNG (all 4 formats)
- ✅ Live preview updates
- ✅ ATS scoring
- ✅ Basic CRUD operations
- ✅ Section management
- ✅ Skill/Experience/Education input
- ✅ Resume preview page

## 🚀 Premium Features to Add

### Feature 1: Resume Comparison
- Compare 2 resumes side-by-side
- Highlight differences
- Merge best elements
- Status: Partially implemented

### Feature 2: Version History
- Track all changes
- Restore previous versions
- View diff between versions
- Status: Partially implemented

### Feature 3: Resume Sharing
- Generate shareable links
- Set view/download permissions
- Track who viewed
- Status: Not fully implemented

### Feature 4: Advanced ATS
- Line-by-line scoring
- Keyword optimization
- Format compatibility check
- Status: Partially implemented

### Feature 5: Multi-Page Resumes
- Support resumes 1-10 pages
- Page break management
- Content distribution across pages
- Status: Not implemented

## 📝 Data Integrity Rules

**NEVER REMOVE**:
- Existing resume fields
- Template selection functionality
- Export capabilities
- Section management

**ALWAYS PRESERVE**:
- User's resume content
- Styling preferences
- Import history
- Version information

## 🔄 Testing Checklist

After fixes, test:
- [ ] Import resume from PDF → verify all fields present
- [ ] Create resume with template → verify template applied
- [ ] Edit resume → verify preview updates in real-time
- [ ] Export resume → verify PDF/DOCX/HTML/PNG all work
- [ ] Duplicate resume → verify all fields copied
- [ ] Share resume → verify link works
- [ ] ATS score → verify accuracy
- [ ] Version history → verify rollback works
- [ ] Compare resumes → verify side-by-side works
- [ ] Switch templates → verify styling applied


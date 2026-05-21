# Resume Module - Complete Feature Inventory & Tracking

## 🎯 Purpose

**Critical Document** - This file serves as the single source of truth for ALL resume module features, their implementation status, working code locations, and dependencies. USE THIS TO PREVENT REGRESSIONS.

**Updated**: December 31, 2025
**Status**: All Core Features Documented ✅

---

## 📋 Core Features Status

### ✅ FEATURE: Resume Creation
- **Status**: ✅ WORKING
- **Endpoints**:
  - `POST /api/v1x/resumes` (Create new resume)
  - Query params: `template` (optional) → uses to set template_id
- **Frontend**:
  - Page: `src/pages/resumes/new.tsx`
  - Components: ResumeCreationForm.tsx
  - Dialog: Uses ResumeCreationModal.tsx
- **Database**: Resume table (all fields supported)
- **Fields Used**:
  - title, full_name, email, phone, location, template_id, etc.
- **Test Path**: `/resumes/new` → Fill form → Create
- **CRITICAL**: Lines 50-65 in new.tsx must pass `template_id` to backend
- **Dependencies**: Backend CRUD, Database Resume model
- **Last Verified**: ✅ Works with template selection

---

### ✅ FEATURE: Resume List
- **Status**: ✅ WORKING
- **Endpoints**:
  - `GET /api/v1x/resumes` (Get all user's resumes)
- **Frontend**:
  - Page: `src/pages/resumes/index.tsx`
  - Components: ResumeCard.tsx (displays each resume)
  - Shows: Title, Template, Created Date, Actions
- **Database**: Resume table
- **Test Path**: `/resumes` → View all resumes
- **CRITICAL**: Must show action buttons (Edit, Preview, Duplicate, Delete, Share, Compare)
- **Dependencies**: Backend API, Database
- **Last Verified**: ✅ All resumes load, buttons visible

---

### ✅ FEATURE: Resume Editor
- **Status**: ✅ WORKING
- **Endpoints**:
  - `GET /api/v1x/resumes/{id}` (Get resume details)
  - `PUT /api/v1x/resumes/{id}` (Update resume)
  - `GET /api/v1x/resumes/{id}/sections` (Get all sections)
  - `POST /api/v1x/resumes/{id}/work-experience` (Add work exp)
  - `PUT /api/v1x/resumes/{id}/work-experience/{exp_id}` (Update work exp)
  - `DELETE /api/v1x/resumes/{id}/work-experience/{exp_id}` (Delete work exp)
  - Similar endpoints for: education, skills, projects, certificates, achievements
- **Frontend**:
  - Page: `src/pages/resumes/[id]/edit.tsx`
  - Main Component: `src/components/resume/ResumeEditor.tsx` (1462 lines)
  - Sub-components: WorkExperienceSection.tsx, EducationSection.tsx, SkillsSection.tsx, etc.
  - Live Preview: `LiveTemplatePreview.tsx` (shows real-time preview)
  - Styling Panel: TemplateCustomizer.tsx, ColorPicker.tsx, FontSelector.tsx
- **Database**: Resume, WorkExperience, Education, ResumeSkill, ResumeProject, ResumeCertificate, ResumeAchievement tables
- **Key Features**:
  - ✅ Drag-to-reorder sections
  - ✅ Add/edit/delete each section type
  - ✅ Real-time live preview updates
  - ✅ Change template/fonts/colors
  - ✅ Keyboard shortcuts (Ctrl+S to save)
  - ✅ Auto-save on changes
  - ✅ Undo/Redo for recent changes
- **Test Path**: `/resumes/[id]/edit` → Make changes → See preview update
- **CRITICAL DO NOT BREAK**:
  - LiveTemplatePreview.tsx width calculation (must be 8.5in for A4)
  - ResumeEditor.tsx section management logic
  - API field names (full_name, NOT firstName, lastName)
  - Database model relationships
- **Dependencies**: Backend CRUD, Database, All section endpoints
- **Last Verified**: ✅ Editor works, preview displays correctly

---

### ✅ FEATURE: Resume Preview
- **Status**: ✅ WORKING
- **Endpoints**:
  - `GET /api/v1x/resumes/{id}` (Get resume data)
- **Frontend**:
  - Page: `src/pages/resumes/[id]/preview.tsx`
  - Component: `ResumePreview.tsx` (423 lines, renders full resume)
  - Shows: Full resume in read-only mode, centered, scrollable
- **Database**: Resume + all sections tables
- **Features**:
  - ✅ Full-page view of resume
  - ✅ Uses selected template styling
  - ✅ Shows all sections in proper layout
  - ✅ Professional formatting
  - ✅ Download/Export from this page
- **Test Path**: `/resumes` → Click "Preview" → See full resume
- **CRITICAL**: ResumePreview.tsx must render complete HTML properly
- **Dependencies**: Backend API, Database, ResumePreview component
- **Last Verified**: ✅ Preview displays correctly

---

### ✅ FEATURE: Live Preview Panel
- **Status**: ✅ WORKING (FIXED Dec 31)
- **Component**: `src/components/resume/LiveTemplatePreview.tsx` (288 lines)
- **Features**:
  - ✅ Real-time preview while editing (side panel or expanded mode)
  - ✅ Zoom in/out (+ / - buttons, keyboard shortcuts)
  - ✅ Reset zoom to default
  - ✅ Fullscreen mode (expands to fill window)
  - ✅ Shows current template info (name, font, layout, color)
  - ✅ Updates instantly as user makes changes
- **Key Implementation Details**:
  - Width: Fixed to 8.5in (A4 paper width) - CRITICAL
  - Height: Auto with minHeight 11in (A4 paper height)
  - Scale: Using CSS transform scale() for zoom
  - Center: Using flexbox with justify-center
  - Scroll: Parent container overflow-x-auto for small screens
- **Test Path**: Open editor → Change something → See preview update immediately
- **CRITICAL DO NOT CHANGE**:
  - Width: `width: '8.5in'` (Line ~219)
  - MinHeight: `minHeight: '11in'` (Line ~220)
  - Parent flex: `flex justify-center overflow-x-auto` (Line ~211)
  - Transform origin: `transformOrigin: 'top center'` (Line ~217)
- **Dependencies**: ResumePreview component, Resume data, Template styling
- **Last Verified**: ✅ FIXED Dec 31 - Shows full width, zoom works, displays correctly

---

### ✅ FEATURE: Template Selection
- **Status**: ✅ WORKING
- **Endpoints**:
  - `GET /api/v1x/templates` (List all templates)
  - `GET /api/v1x/templates/{id}` (Get template details)
- **Frontend**:
  - Page: `src/pages/resumes/templates.tsx` (386 lines)
  - Shows: 30 template cards in grid
  - Filter: By category (Modern, Classic, Creative, Executive, Medical, Tech)
  - Actions: "Create with This" (new resume) or "Apply to Resume" (existing)
- **Database**: ResumeTemplate table (30 templates seeded, all active)
- **Template Fields**:
  - id, name, category, description, preview_image, config (JSON), is_active, created_at
- **config JSON includes**:
  - layout, font, accent_color, picture_style, color_theme, text_color, heading_color, line_spacing, background_type, rating_style
- **Features**:
  - ✅ Grid display of templates
  - ✅ Category filtering
  - ✅ Search templates
  - ✅ Create new resume from template
  - ✅ Apply template to existing resume
- **Test Path**: `/resumes/templates` → Browse → "Create with This"
- **CRITICAL DO NOT REMOVE**:
  - 30 seeded templates in database
  - Template configuration data
  - applyTemplate function (must use new endpoint)
- **Dependencies**: Backend template API, Database ResumeTemplate table, create & apply-template endpoints
- **Last Verified**: ✅ All 30 templates visible, filtering works

---

### ✅ FEATURE: Apply Template to Existing Resume
- **Status**: ✅ WORKING (NEW - Added Dec 31)
- **Endpoints**:
  - NEW: `POST /api/v1x/resumes/{resume_id}/apply-template/{template_id}` (Apply template styling)
- **Frontend**:
  - Function: `applyTemplate` in `src/pages/resumes/templates.tsx` (Lines 112-135)
  - Called from: Template browser or editor template selector
  - Uses: Action-based proxy routing via `/api/session/resumes?id=X&action=apply-template&template=Y`
- **Backend Implementation**:
  - File: `backend/app/api/v1x/resumes.py` (Lines 223-282)
  - Function: `apply_template_to_resume`
  - Validates: Resume ownership, template exists, template is active
  - Applies: layout, font_family, accent_color, picture_style, color_theme, text_color, heading_color, line_spacing, background_type, rating_style
  - Preserves: All resume content (work exp, education, skills, etc.)
  - Updates: updated_at timestamp
  - Returns: Complete updated resume object
- **Database**: Updates Resume.template_id and styling fields, leaves content intact
- **Features**:
  - ✅ Validate resume ownership
  - ✅ Validate template exists
  - ✅ Apply complete template config
  - ✅ Preserve all content
  - ✅ Update timestamp
  - ✅ Return updated resume
- **Test Path**: `/resumes` → Open editor → Select template → "Apply" → See styling change
- **CRITICAL**: This is new functionality - ensure not broken in future updates
- **Dependencies**: Template API endpoint, Resume model, validation logic
- **Last Verified**: ✅ NEW - Added Dec 31, code applied successfully

---

### ✅ FEATURE: Duplicate Resume
- **Status**: ✅ WORKING (FIXED Dec 31)
- **Endpoints**:
  - `POST /api/v1x/resumes/{resume_id}/duplicate` (Create copy)
- **Frontend**:
  - Page: `src/pages/resumes/index.tsx`
  - Function: `handleDuplicate` (Lines 72-91)
  - Button: In ResumeCard.tsx action menu
  - Uses: Action-based proxy routing via `/api/session/resumes?id=X&action=duplicate`
  - User feedback: Alert on success/error
  - Navigation: Goes to new resume edit page
- **Backend Implementation**:
  - File: `backend/app/api/v1x/resumes.py` (Lines 189-220)
  - Function: `duplicate_resume`
  - Creates: New Resume record with all fields copied
  - Preserves: All content sections (work exp, education, skills, etc.)
  - Title: Original title + "(Copy)"
  - Updates: created_at timestamp (new)
  - Returns: Complete new resume object
- **Database**: New Resume record created with deep copy of all related sections
- **Features**:
  - ✅ Create complete copy of resume
  - ✅ Preserve all content sections
  - ✅ Add "(Copy)" to title
  - ✅ Create new sections (work exp, education, etc.) from originals
  - ✅ Deep copy (independent records, changes don't affect original)
  - ✅ User feedback on success/failure
  - ✅ Navigate to new resume editor
- **Test Path**: `/resumes` → Click duplicate button → Confirm → See new resume in list
- **CRITICAL**: Must be deep copy (all sections independently copied)
- **Dependencies**: Backend duplicate endpoint, Resume model, section models, proxy routing
- **Last Verified**: ✅ FIXED Dec 31 - Endpoint corrected, error handling added

---

### ✅ FEATURE: Resume Export (All 4 Formats)
- **Status**: ✅ WORKING
- **Endpoints**:
  - `GET /api/v1x/resumes/{id}/export-pdf` (Export as PDF)
  - `GET /api/v1x/resumes/{id}/export-docx` (Export as DOCX)
  - `GET /api/v1x/resumes/{id}/export-html` (Export as HTML)
  - `GET /api/v1x/resumes/{id}/export-png` (Export as PNG)
- **Frontend**:
  - Page: `src/pages/resumes/[id]/export.tsx` (Export page with options)
  - Modal: `ExportOptionsModal.tsx` (Export format selector)
  - Button: In editor and preview pages
  - Downloads: File saved to user's Downloads folder
- **Backend Implementation**:
  - File: `backend/app/api/v1x/resume_export.py` (Handles all 4 formats)
  - Uses: Python libraries (reportlab for PDF, python-docx for DOCX, html2image for PNG)
  - Styling: Respects template colors, fonts, layout
  - Quality: Professional formatting maintained
  - File naming: `{resume_title}_{date}.{format}`
- **Database**: Resume + all sections (read-only for export)
- **Features**:
  - ✅ Export to PDF (professional quality)
  - ✅ Export to DOCX (editable in Word)
  - ✅ Export to HTML (web-viewable)
  - ✅ Export to PNG (image format)
  - ✅ All formatting preserved
  - ✅ Styling applied from template
  - ✅ File downloaded directly
- **Test Path**: Open resume → Click export → Select format → File downloads
- **CRITICAL DO NOT BREAK**: All 4 export formats must remain functional
- **Dependencies**: Export backend endpoints, Template styling, Python export libraries
- **Last Verified**: ✅ All 4 formats working

---

### ✅ FEATURE: Resume Import
- **Status**: ⚠️ PARTIALLY WORKING (Data loss issue noted)
- **Endpoints**:
  - `POST /api/v1x/resumes/import` (Upload and parse file)
  - Accepts: PDF, DOCX, TXT files
- **Frontend**:
  - Page: `src/pages/resumes/import.tsx`
  - Modal: `ResumeImportModal.tsx` (File upload and preview)
  - Steps: 1) Upload file, 2) Review extracted data, 3) Confirm import
  - Shows: Extracted fields in preview before final import
- **Backend Implementation**:
  - File: `backend/app/api/v1x/resume_import.py`
  - Parsers: PDF parser (pdfplumber), DOCX parser (python-docx), TXT parser
  - Extraction: Parses document to extract text and structure
  - Fields Extracted:
    - ✅ Full name
    - ✅ Email
    - ✅ Phone
    - ✅ Professional summary
    - ✅ Work experience (all entries)
    - ✅ Education (all entries)
    - ✅ Skills
    - ✅ Projects (if present)
    - ✅ Certifications
    - ⚠️ NOT EXTRACTED: template_id, font_family, color_theme, layout, accent_color, picture_style, import_source
- **Database**: Resume + all section tables
- **KNOWN ISSUES** ⚠️:
  - template_id not set on import (uses default 'modern')
  - import_source not tracked (where did resume come from)
  - Font/color choices not extracted from original
  - Some field mappings may lose data (needs investigation)
- **Features**:
  - ✅ Accept PDF, DOCX, TXT files
  - ✅ Parse and extract content
  - ✅ Preview extracted data
  - ✅ Create resume from extracted data
  - ✅ Allow manual correction before import
  - ❌ Doesn't preserve template choice
  - ❌ Doesn't track import source
- **Test Path**: `/resumes/import` → Upload file → Review data → Confirm
- **NEEDS FIXING**:
  - Extract and preserve template preferences
  - Track import_source (PDF, DOCX, LinkedIn, etc.)
  - Ensure all fields extracted completely
  - Add manual field editing before final import
- **Dependencies**: Backend import endpoint, File parsers, Resume model
- **Last Verified**: ⚠️ Works but loses template info - NEEDS FIX

---

### ✅ FEATURE: Resume Comparison
- **Status**: ⚠️ PARTIALLY WORKING (Needs UI enhancement)
- **Endpoints**:
  - `POST /api/v1x/resumes/compare` (Compare multiple resumes)
  - Request: List of resume IDs to compare
  - Response: Comparison data structure
- **Frontend**:
  - Page: `src/pages/resumes/compare.tsx` (Comparison view)
  - Component: `ResumeComparisonView.tsx` (Side-by-side display)
  - Triggered: From resume list with multi-select checkboxes
  - Displays: Differences and similarities
- **Backend Implementation**:
  - File: `backend/app/api/v1x/resume_comparison.py`
  - Compares: Structure, content, formatting, styling
  - Output: Detailed comparison report
- **Features**:
  - ⚠️ Compares selected resumes
  - ⚠️ Shows differences
  - ⚠️ Highlights unique content
  - ❌ UI could be more visual
  - ❌ Suggestions for improvements missing
- **Test Path**: `/resumes` → Select 2+ resumes → Click compare
- **NEEDS ENHANCEMENT**:
  - Better visual layout for comparison
  - Add suggestions based on differences
  - Export comparison report
  - Side-by-side content view
- **Dependencies**: Backend comparison endpoint, Resume data
- **Last Verified**: ⚠️ Works but needs UI improvement

---

### ✅ FEATURE: ATS Scoring
- **Status**: ✅ WORKING (Basic)
- **Endpoints**:
  - `GET /api/v1x/resumes/{id}/ats-score` (Calculate ATS score)
  - `GET /api/v1x/resumes/{id}/ats-report` (Get detailed ATS report)
- **Frontend**:
  - Page: `src/pages/resumes/[id]/ats-score.tsx` (ATS scoring page)
  - Component: `ATSScoreCard.tsx` (Score display)
  - Shows: Overall score (0-100), scoring breakdown, recommendations
  - Features: Detailed report, actionable suggestions
- **Backend Implementation**:
  - File: `backend/app/api/v1x/resume_scoring.py`
  - Analyzes:
    - ✅ Keyword coverage
    - ✅ Formatting compliance
    - ✅ Section completeness
    - ✅ Content length
    - ✅ Readability
  - Doesn't analyze: Line-by-line issues, ATS system compatibility
- **Database**: Resume + all sections (read-only)
- **Features**:
  - ✅ Calculate overall ATS score
  - ✅ Break down by criteria
  - ✅ Provide recommendations
  - ✅ Suggest keyword improvements
  - ❌ Advanced line-by-line analysis missing
  - ❌ ATS system-specific compatibility (Taleo, Workday, etc.) not checked
- **Test Path**: Open resume → Go to ATS Score tab → See score and recommendations
- **NEEDS ENHANCEMENT**:
  - Add line-by-line analysis
  - Check specific ATS system compatibility
  - Provide keyword suggestions from job descriptions
  - Track score improvements over time
- **Dependencies**: Backend scoring endpoint, Resume analysis logic
- **Last Verified**: ✅ Works - basic ATS scoring functional

---

### ✅ FEATURE: Resume Version History
- **Status**: ⚠️ PARTIALLY WORKING (Structure exists, UI minimal)
- **Endpoints**:
  - `GET /api/v1x/resumes/{id}/versions` (Get version history)
  - `GET /api/v1x/resumes/{id}/versions/{version_id}` (Get specific version)
  - `POST /api/v1x/resumes/{id}/versions/restore/{version_id}` (Restore version)
- **Frontend**:
  - Page: `src/pages/resumes/[id]/versions.tsx` (Version history page)
  - Component: `ResumeVersionHistory.tsx` (Version list)
  - Shows: Previous versions, dates, changes made
  - Actions: View, compare, restore previous versions
- **Backend Implementation**:
  - File: `backend/app/modelsx/resume.py` (ResumeVersion model)
  - Tracks: Each update with full resume snapshot
  - Records: Change timestamp, user who made change, change summary
  - Allows: Restore to any previous version
- **Database**: ResumeVersion table (linked to Resume)
- **Features**:
  - ✅ Track resume changes
  - ✅ View version history
  - ✅ Restore previous versions
  - ⚠️ UI minimal
  - ❌ Change diffing (what specifically changed)
  - ❌ Comparison between versions
  - ❌ Branching (keep both versions)
- **Test Path**: Edit resume → Make changes → Go to Versions tab → See history
- **NEEDS ENHANCEMENT**:
  - Show detailed change summary
  - Compare two versions side-by-side
  - Allow branching (keep both versions as separate resumes)
  - Auto-save versions every 5 minutes
- **Dependencies**: Backend version endpoints, ResumeVersion model
- **Last Verified**: ⚠️ Works but needs UI enhancement

---

### ✅ FEATURE: Resume Sharing
- **Status**: ⚠️ PARTIALLY WORKING (Basic sharing exists, permissions needed)
- **Endpoints**:
  - `POST /api/v1x/resumes/{id}/share` (Generate share link)
  - `GET /api/v1x/shared-resumes/{share_token}` (View shared resume)
  - `DELETE /api/v1x/resumes/{id}/share/{share_id}` (Revoke share)
- **Frontend**:
  - Page: `src/pages/resumes/[id]/sharing.tsx` (Sharing settings)
  - Component: `ResumeSharingPanel.tsx` (Share interface)
  - Features: Copy share link, manage who can see, set expiration
- **Backend Implementation**:
  - File: `backend/app/modelsx/resume.py` (ResumeShare model)
  - Creates: Unique share tokens for each shared resume
  - Permissions: Can view, can download, can comment
  - Expiration: Optional time-based expiration
- **Database**: ResumeShare table (tracks shares)
- **Features**:
  - ✅ Generate shareable links
  - ✅ Share with email addresses
  - ✅ Track who has access
  - ⚠️ Permissions limited (basic view/download)
  - ❌ No comment/feedback feature
  - ❌ No usage analytics
  - ❌ Expiration not enforced
- **Test Path**: Open resume → Go to Sharing tab → "Share" → Copy link
- **NEEDS ENHANCEMENT**:
  - Add permission levels (view-only, can download, can comment)
  - Implement commenting feature
  - Track view analytics
  - Enforce expiration dates
  - Revoke sharing without deleting resume
- **Dependencies**: Backend sharing endpoints, ResumeShare model
- **Last Verified**: ⚠️ Works but needs permission system

---

## 🔧 System Architecture & Data Flow

### Page Structure
```
/resumes                    → List all resumes (ResumeCard.tsx)
  /new                      → Create new resume (ResumeCreationForm.tsx)
  /templates                → Browse & select templates (TemplateGrid.tsx)
  /import                   → Import resume from file (ResumeImportModal.tsx)
  /[id]                     → View resume (ResumePreview.tsx)
    /edit                   → Edit resume (ResumeEditor.tsx + LiveTemplatePreview.tsx)
    /preview                → Full page preview (ResumePreview.tsx fullscreen)
    /export                 → Export options (ExportOptionsModal.tsx)
    /ats-score              → ATS scoring (ATSScoreCard.tsx + Report)
    /versions               → Version history (ResumeVersionHistory.tsx)
    /sharing                → Share settings (ResumeSharingPanel.tsx)
    /compare                → Compare with others (ResumeComparisonView.tsx)
```

### API Endpoint Structure
```
/api/v1x/resumes
  - POST /                          (Create)
  - GET /                           (List all)
  - GET /{id}                       (Get one)
  - PUT /{id}                       (Update)
  - DELETE /{id}                    (Delete)
  - POST /{id}/duplicate            (Duplicate)
  - POST /{id}/apply-template/{tid} (Apply template)
  - GET /{id}/export-pdf            (Export PDF)
  - GET /{id}/export-docx           (Export DOCX)
  - GET /{id}/export-html           (Export HTML)
  - GET /{id}/export-png            (Export PNG)
  - GET /{id}/ats-score             (ATS score)
  - GET /{id}/ats-report            (ATS report)
  - GET /{id}/versions              (Get versions)
  - GET /{id}/versions/{version_id} (Get version)
  - POST /{id}/versions/restore/{v} (Restore)
  - POST /{id}/share                (Share)
  - DELETE /{id}/share/{sid}        (Revoke share)
  - POST /{id}/work-experience      (Add work exp)
  - ... and all other section endpoints
```

### Frontend Proxy
```
/api/session/resumes
  - GET /api/v1x/resumes            (proxy GET)
  - POST /api/v1x/resumes           (proxy POST)
  - PATCH /api/v1x/resumes/{id}     (proxy PATCH)
  - DELETE /api/v1x/resumes/{id}    (proxy DELETE)
  
  Special actions:
  - ?action=duplicate               (route to /{id}/duplicate)
  - ?action=apply-template&template=X (route to /{id}/apply-template/{X})
```

### Database Relations
```
Resume (main table)
  ├── WorkExperience (one-to-many)
  ├── Education (one-to-many)
  ├── ResumeSkill (one-to-many)
  ├── ResumeProject (one-to-many)
  ├── ResumeCertificate (one-to-many)
  ├── ResumeAchievement (one-to-many)
  ├── ResumeVersion (one-to-many)
  └── ResumeShare (one-to-many)

ResumeTemplate (template library)
  └── Used by Resume.template_id

ResumeATS (scoring cache)
  └── Used by Resume.id
```

---

## 📊 Field Mapping Reference

### Resume Model Main Fields
```
id              - Unique identifier
user_id         - Owner of resume
title           - Resume title (e.g., "Software Engineer")
template_id     - Selected template ID (default: 'modern')
created_at      - Creation timestamp
updated_at      - Last modification timestamp
views           - Number of views (if sharing enabled)

Personal Info Fields:
full_name       - Person's full name
email           - Contact email
phone           - Phone number
location        - City/location
linkedin_url    - LinkedIn profile URL
github_url      - GitHub profile URL
portfolio_url   - Portfolio website URL
website_url     - Personal website URL
summary         - Professional summary

Styling Fields:
font_family     - Font choice (Inter, Roboto, Georgia, etc.)
color_theme     - Color scheme (blue, green, professional, creative, etc.)
background_type - Background treatment (none, gradient, pattern)
picture_style   - Profile picture style (circle, square, rounded, none)
rating_style    - Skill rating visualization (bars, dots, stars, circles)
layout          - Layout type (single-column, two-column, sidebar, etc.)
accent_color    - Primary accent color (hex, e.g., #2563eb)
text_color      - Primary text color (hex)
heading_color   - Heading color (hex)
line_spacing    - Line spacing multiplier (1.0, 1.5, 2.0)
font_size       - Base font size in points
heading_size    - Heading font size in points
show_icons      - Show icons for sections (boolean)
page_margins    - Page margins (in, cm, etc.)
page_size       - Page size (A4, Letter, etc.)
max_pages       - Maximum page count
custom_sections - Custom section definitions (JSON)
sections_order  - Custom section ordering (JSON)
enabled_sections- Which sections are visible (JSON)
```

### Template Config Structure
```json
{
  "layout": "two-column|single-column|sidebar",
  "font": "Inter|Roboto|Georgia|Playfair",
  "accent_color": "#2563eb",
  "picture_style": "circle|square|rounded|none",
  "color_theme": "blue|green|professional|creative",
  "text_color": "#333333",
  "heading_color": "#000000",
  "line_spacing": 1.5,
  "background_type": "none|gradient|pattern",
  "rating_style": "bars|dots|stars|circles",
  "description": "Template description"
}
```

---

## 🚨 Critical DO NOT Modify Lists

### Code That MUST NOT CHANGE
1. **LiveTemplatePreview.tsx** Lines 216-221 (Width/height/transform)
   ```tsx
   width: '8.5in',
   height: 'auto',
   minHeight: '11in',
   transform: `scale(${displayScale})`,
   transformOrigin: 'top center',
   ```

2. **ResumeEditor.tsx** Section management logic (lines ~400-600)
   - Add/edit/delete sections
   - Drag-to-reorder functionality
   - Save handlers

3. **ResumePreview.tsx** Rendering logic (lines ~50-300)
   - HTML structure must match template
   - CSS classes and styling
   - Section rendering order

4. **resumes.py** CRUD operations (lines ~50-180)
   - Create, read, update, delete resumes
   - Section management endpoints
   - Database transactions

5. **resume_export.py** All 4 export formats
   - PDF generation
   - DOCX generation
   - HTML generation
   - PNG generation

### Data That MUST NOT BE DELETED
1. 30 seeded resume templates in database
2. All resume table fields (add new, don't remove)
3. All section models (WorkExperience, Education, etc.)
4. All relationship definitions

### Functionality That MUST NOT BREAK
1. Resume creation with template selection
2. Resume list display with all buttons
3. Resume editing with live preview
4. All 4 export formats
5. Template application
6. Resume duplication
7. ATS scoring
8. Section management
9. Authentication/authorization

---

## 🔄 Change Management Rules

### When Adding New Features
1. ✅ Create new endpoint in backend without modifying existing ones
2. ✅ Create new frontend page/component without modifying existing ones
3. ✅ Add new database fields without removing existing ones
4. ✅ Test that existing features still work
5. ✅ Document in this file what was added
6. ✅ Update TEST_SCRIPT.md with new tests
7. ✅ Get approval before committing

### When Fixing Bugs
1. ✅ Only change the specific buggy code
2. ✅ Verify the fix doesn't break related features
3. ✅ Update this file with fix details
4. ✅ Add test case to verify fix
5. ✅ Run regression tests on related features
6. ✅ Document why the bug occurred

### When Refactoring
1. ❌ DO NOT refactor unless absolutely necessary
2. ✅ If refactoring, do it in a separate branch
3. ✅ Run ALL tests before and after
4. ✅ Verify every single feature still works
5. ✅ Document all changes
6. ✅ Get double approval before merging

---

## 📝 Last 10 Modifications

| Date | Type | Feature | Status | Notes |
|------|------|---------|--------|-------|
| 12/31 | Fix | Live Preview Display | ✅ | Changed width to 8.5in (A4) |
| 12/31 | Fix | Duplicate Button | ✅ | Fixed endpoint path, added error handling |
| 12/31 | Add | Apply Template Endpoint | ✅ | New backend function + proxy support |
| 12/31 | Fix | Template Application | ✅ | Updated frontend to use new endpoint |
| 12/31 | Add | Action Proxy Routing | ✅ | Added support for special actions |
| 12/30 | Add | Template Seeding | ✅ | 30 templates in database |
| 12/30 | Fix | Template Selection | ✅ | Now passes template_id correctly |
| 12/30 | Add | ATS Scoring | ✅ | Basic ATS analysis working |
| 12/30 | Add | Export (All 4) | ✅ | PDF, DOCX, HTML, PNG formats |
| 12/30 | Add | Resume CRUD | ✅ | Complete create, read, update, delete |

---

## 🎯 Next Priority Features

### Priority 1: Fix Data Loss Issues
- [ ] Fix resume import to preserve template preference
- [ ] Add import_source field tracking
- [ ] Enhance field extraction from PDF/DOCX

### Priority 2: Complete Premium Features
- [ ] Enhance ATS scoring (advanced line-by-line)
- [ ] Complete comparison UI
- [ ] Enhance version history UI
- [ ] Add sharing permissions system

### Priority 3: Add Advanced Features
- [ ] Multi-page resume support
- [ ] Custom template builder
- [ ] AI content suggestions
- [ ] Resume analytics (view tracking)
- [ ] Batch operations

---

## ✅ Deployment Checklist

Before deploying any changes:
- [ ] All fixes applied and code committed
- [ ] All 35+ tests passing
- [ ] No JavaScript console errors
- [ ] No network errors (all API calls successful)
- [ ] Live preview displays correctly
- [ ] Template application works end-to-end
- [ ] Duplication creates full copies
- [ ] All export formats work
- [ ] Data persists correctly
- [ ] No regressions to existing features
- [ ] Performance acceptable (< 3 seconds load)
- [ ] This document updated with changes

---

**Document Status**: ✅ Complete & Current
**Last Updated**: December 31, 2025
**Maintained By**: AI Development Team
**Approval Required Before Deployment**: YES


# Resume Module - Developer Quick Reference

**Quick answers to common questions while developing**

---

## ❓ Common Questions & Answers

### Q: "I need to add a new field to resumes, what do I do?"

**A**: Follow this process:

1. **Add to Database Model**
   - File: `backend/app/modelsx/resume.py`
   - Add to Resume class: `new_field = Column(String, nullable=True)`
   - Run migration (or use Base.metadata.create_all)

2. **Add to Backend Schema**
   - File: `backend/app/schemas/resume.py`
   - Add to ResumeCreate: `new_field: Optional[str] = None`
   - Add to ResumeOut: `new_field: Optional[str]`

3. **Add to Frontend Form**
   - File: `src/components/resume/ResumeEditor.tsx`
   - Add input field in appropriate section
   - Add to form data object

4. **Update API Call**
   - File: `src/lib/api.ts` or inline fetch
   - Include new_field in request body

5. **Display in Preview**
   - File: `src/components/resume/ResumePreview.tsx`
   - Add to JSX output if user has set it

6. **Test**
   - Create new resume with field
   - Edit and verify field saves
   - Duplicate and verify field copied
   - Export and verify field included

7. **Document**
   - Add to RESUME_MODULE_COMPLETE_INVENTORY.md
   - Mark in version control

---

### Q: "I need to add a new export format (e.g., RTF)"

**A**: Follow this process:

1. **Create Export Function**
   - File: `backend/app/api/v1x/resume_export.py`
   - Add function: `def export_resume_rtf(resume_id: int, db: Session)`
   - Implement RTF conversion logic
   - Return file with correct MIME type

2. **Add Backend Endpoint**
   - File: `backend/app/api/v1x/resumes.py`
   - Add route: `@router.get("/{id}/export-rtf")`
   - Call export function
   - Return file response

3. **Add Frontend Button**
   - File: `src/components/resume/ExportOptionsModal.tsx`
   - Add button for RTF option
   - Call `/api/session/resumes/{id}?action=export&format=rtf`

4. **Update Proxy** (if using special routing)
   - File: `src/pages/api/session/resumes.ts`
   - Add handling for `action=export&format=rtf`

5. **Test**
   - Open resume export
   - Click RTF button
   - Verify file downloads
   - Open file and check formatting

6. **Document**
   - Add to RESUME_MODULE_COMPLETE_INVENTORY.md feature list

---

### Q: "Live preview is showing weird - how do I fix it?"

**A**: Check these things in order:

1. **Is width set correctly?**
   ```tsx
   width: '8.5in',  // MUST be this value for A4 paper
   minHeight: '11in',
   ```

2. **Is parent container correct?**
   ```tsx
   className="flex justify-center overflow-x-auto"  // Must have these
   ```

3. **Is ResumePreview rendering correctly?**
   - Check ResumePreview.tsx hasn't been modified
   - Verify CSS classes are present

4. **Is scale transform correct?**
   ```tsx
   transform: `scale(${displayScale})`,
   transformOrigin: 'top center',
   ```

5. **Clear browser cache**
   - Press Ctrl+Shift+Delete
   - Clear all cache
   - Reload page

If still broken, revert to last known working commit and fix step by step.

---

### Q: "Template not applying - what's wrong?"

**A**: Debug in this order:

1. **Check backend endpoint exists**
   ```bash
   curl -X POST http://localhost:8001/api/v1x/resumes/1/apply-template/modern
   # Should return updated resume JSON
   ```

2. **Check template exists in database**
   ```python
   # Run in backend shell
   from app.modelsx.resume import ResumeTemplate
   templates = db.query(ResumeTemplate).all()
   print(len(templates))  # Should be 30
   ```

3. **Check frontend is calling correct endpoint**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Apply template
   - Look for request to `/api/session/resumes?id=X&action=apply-template&template=Y`
   - Check response status (should be 200)

4. **Check proxy is routing correctly**
   - File: `src/pages/api/session/resumes.ts`
   - Verify action=apply-template section is present
   - Verify it's calling correct backend URL

5. **Check resume ownership**
   - Ensure you're logged in as resume owner
   - Check user_id matches in database

---

### Q: "Duplicate not working - what's wrong?"

**A**: Debug in this order:

1. **Check duplicate endpoint exists**
   ```bash
   curl -X POST http://localhost:8001/api/v1x/resumes/1/duplicate
   # Should return new resume JSON
   ```

2. **Check API call in frontend**
   - File: `src/pages/resumes/index.tsx` lines 72-91
   - Should call `/api/session/resumes?id=${resumeId}&action=duplicate`
   - NOT `/api/session/v1x/resumes/${id}/duplicate` (old broken way)

3. **Check proxy routing**
   - File: `src/pages/api/session/resumes.ts`
   - Verify action=duplicate section present

4. **Check backend implementation**
   - File: `backend/app/api/v1x/resumes.py` lines 189-220
   - Verify function exists and creates new Resume record

5. **Check database**
   - Verify new Resume record created
   - Verify sections (work exp, education) also created

---

### Q: "Export to PDF not working - what's wrong?"

**A**: Debug in this order:

1. **Check endpoint exists**
   ```bash
   curl http://localhost:8001/api/v1x/resumes/1/export-pdf
   # Should return PDF file
   ```

2. **Check required Python packages installed**
   ```bash
   pip list | grep -i pdf
   # Should have reportlab, pypdf, etc.
   ```

3. **Check file permissions**
   - Backend needs write access to temp directory
   - Check /tmp or %TEMP% is writable

4. **Check frontend is calling correct endpoint**
   - Open DevTools Network tab
   - Click export PDF
   - Look for request to `/api/session/resumes/{id}?action=export&format=pdf`
   - Check response status and headers

5. **Check resume has content**
   - Resume must have at least a name
   - Some content makes better PDF

6. **Check file size not too large**
   - Very large resumes may timeout
   - Check backend timeout settings

---

### Q: "How do I test this locally?"

**A**: Follow this setup:

1. **Start Backend**
   ```bash
   cd backend
   python -m venv venv
   # Activate venv
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **Start Frontend** (in new terminal)
   ```bash
   cd ..
   npm install  # First time only
   npm run dev
   # Opens at http://localhost:3000
   ```

3. **Login & Test**
   - Go to http://localhost:3000/login
   - Sign up new account
   - Go to /resumes
   - Create, edit, duplicate, export, etc.

4. **Monitor Logs**
   - Backend logs show in backend terminal
   - Frontend logs in DevTools console (F12)
   - Network tab shows all API calls

5. **Database Access**
   ```bash
   # If using SQLite
   sqlite3 backend/app.db
   SELECT COUNT(*) FROM resumes;
   SELECT * FROM resume_templates LIMIT 1;
   ```

---

### Q: "I accidentally broke something - how do I rollback?"

**A**: Do this immediately:

1. **Find last known working commit**
   ```bash
   git log --oneline | head -20
   # Find commit before your changes
   ```

2. **Revert the file**
   ```bash
   git checkout <commit_hash> -- path/to/file.tsx
   git checkout <commit_hash> -- path/to/file.py
   ```

3. **Or revert entire commit**
   ```bash
   git revert <commit_hash>  # Creates new commit that undoes changes
   # OR
   git reset --hard <commit_hash>  # Deletes your commits (dangerous)
   ```

4. **Verify it works**
   - Restart dev server
   - Test affected feature
   - Check this document wasn't modified

5. **Try again carefully**
   - Make smaller changes
   - Test after each change
   - Commit frequently

---

### Q: "How do I prevent breaking code when making changes?"

**A**: Follow this protocol:

1. **Before Starting**
   - Read RESUME_MODULE_COMPLETE_INVENTORY.md
   - Know what you're modifying
   - Know what must NOT change

2. **While Coding**
   - Make minimal changes
   - Change one thing at a time
   - Test after each change
   - Don't refactor if you can help it

3. **Before Committing**
   - Run all relevant tests
   - Check live preview displays correctly
   - Test duplicate/export/import
   - Check console for errors (F12)
   - Verify no network errors

4. **In Code Review**
   - Have someone else test
   - Run full test suite
   - Check this document was updated

5. **After Deployment**
   - Monitor for errors
   - Be ready to rollback
   - Check user feedback

---

### Q: "What's the difference between v1 and v1x?"

**A**: Short answer:

- **v1**: File-based backends (uses JSON files in `backend/app/data/`)
- **v1x**: Database-backed endpoints (uses SQLite database)

For resumes, use **v1x** only:
```
/api/v1x/resumes          ← Use this
/api/v1/resumes           ← Don't use this (different system)
```

Routes in:
- `backend/app/api/v1x/` ← Resumes use this
- `backend/app/api/v1/` ← Courses, paths use this

---

### Q: "Where are the resume templates?"

**A**: Three places:

1. **Database** (Active templates)
   ```bash
   SELECT * FROM resume_templates WHERE is_active = true;
   # Returns 30 templates
   ```

2. **Seeding Script**
   - Run once at app startup
   - File: `backend/app/api/v1x/resume_templates.py`
   - Creates 30 templates on first run

3. **Frontend Display**
   - Page: `src/pages/resumes/templates.tsx`
   - Fetches from API and displays

All 30 templates should always be present. If missing, reseed database.

---

### Q: "How do I add a new template?"

**A**: Follow this process:

1. **Add to Seeding Script**
   - File: `backend/app/api/v1x/resume_templates.py`
   - Add new template dict to TEMPLATES list
   - Include: name, category, description, config JSON

2. **Seed Database**
   - Restart backend server
   - Or run: `python -c "from app.seeds.resume_templates import seed; seed()"`

3. **Verify**
   ```bash
   sqlite3 backend/app.db
   SELECT COUNT(*) FROM resume_templates;  # Should be 31
   SELECT name FROM resume_templates WHERE name = 'YourTemplate';
   ```

4. **Test**
   - Go to /resumes/templates
   - Should see new template in grid
   - Should be able to create/apply it

5. **Document**
   - Update RESUME_MODULE_COMPLETE_INVENTORY.md
   - Note template added and when

---

### Q: "What's the current state of the resume module?"

**A**: As of Dec 31, 2025:

| Feature | Status | Notes |
|---------|--------|-------|
| Create | ✅ | Works with template selection |
| List | ✅ | Shows all buttons |
| Edit | ✅ | Live preview working (FIXED) |
| Duplicate | ✅ | Complete copy created (FIXED) |
| Export (4 formats) | ✅ | PDF, DOCX, HTML, PNG all working |
| Templates | ✅ | 30 templates, can apply (FIXED) |
| Import | ⚠️ | Works but loses template info |
| ATS Scoring | ✅ | Basic scoring working |
| Version History | ⚠️ | Exists but UI minimal |
| Sharing | ⚠️ | Exists but no permissions |
| Comparison | ⚠️ | Exists but UI minimal |

See RESUME_MODULE_COMPLETE_INVENTORY.md for full details.

---

### Q: "I need to work on the import feature - where do I start?"

**A**: Follow this path:

1. **Read the Issue**
   - File: RESUME_MODULE_COMPLETE_INVENTORY.md
   - Section: "Resume Import"
   - Understand what's being lost (template_id, font choices, etc.)

2. **Find the Code**
   - Frontend: `src/pages/resumes/import.tsx`
   - Component: `src/components/resume/ResumeImportModal.tsx`
   - Backend: `backend/app/api/v1x/resume_import.py`

3. **Understand the Flow**
   - User uploads PDF/DOCX
   - Backend parses file
   - Extract fields using PDF/DOCX parser
   - Return extracted data to frontend
   - Frontend shows preview
   - User confirms import
   - Backend creates Resume record

4. **Identify the Gap**
   - Backend parser only extracts text content
   - Doesn't extract styling/template preference
   - Doesn't track where resume came from (import_source)

5. **Make Changes**
   - Enhance parser to extract more metadata
   - Add import_source field to Resume model
   - Update schema to accept import_source
   - Test with PDF and DOCX files

6. **Test Thoroughly**
   - Import sample PDF → verify all fields
   - Import sample DOCX → verify all fields
   - Verify no data lost
   - Verify can edit after import
   - Verify can export after import

---

### Q: "How do I deploy to production?"

**A**: Deployment checklist:

1. **Pre-Deployment**
   - All tests passing
   - No console errors
   - Code reviewed
   - RESUME_MODULE_COMPLETE_INVENTORY.md updated
   - No known regressions

2. **Backup Database**
   ```bash
   cp backend/app.db backend/app.db.backup
   ```

3. **Build Frontend**
   ```bash
   npm run build
   # Generates .next/ directory
   ```

4. **Test Production Build Locally**
   ```bash
   npm run start
   # Runs optimized production build
   ```

5. **Deploy**
   - Push to production branch
   - Trigger deployment pipeline
   - Monitor logs for errors
   - Check all features working
   - Be ready to rollback

6. **Post-Deployment**
   - Monitor user feedback
   - Check error logs
   - Verify no data loss
   - Update this document with deployment date

---

## 📚 Quick File Reference

| Purpose | File | Key Lines |
|---------|------|-----------|
| Live preview width | `LiveTemplatePreview.tsx` | 216-221 |
| Duplicate button | `index.tsx` | 72-91 |
| Template application | `resumes.py` (backend) | 223-282 |
| Apply template frontend | `templates.tsx` | 112-135 |
| Proxy routing | `api/session/resumes.ts` | 1-40 |
| Resume editor | `ResumeEditor.tsx` | 1-1462 |
| Resume preview | `ResumePreview.tsx` | 1-423 |
| Template display | `templates.tsx` | 1-386 |
| Export options | `ExportOptionsModal.tsx` | |
| Import resume | `ResumeImportModal.tsx` | |
| ATS scoring | `resume_scoring.py` | |
| CRUD operations | `resumes.py` (backend) | 50-180 |
| Database models | `resume.py` (backend) | |

---

## 🎯 Success Criteria

Your code changes are good if:

✅ All existing features still work
✅ New feature works correctly
✅ No console errors (F12)
✅ No network errors (F12 Network tab)
✅ Live preview displays fully
✅ Duplicate creates complete copy
✅ Templates apply correctly
✅ All exports work (PDF, DOCX, HTML, PNG)
✅ Import completes without data loss
✅ ATS scoring calculates correctly
✅ Performance is acceptable (< 3 sec page load)
✅ This document was updated

If any of these fail, the change is not ready for deployment.

---

**Document Status**: ✅ Complete
**Last Updated**: December 31, 2025
**Next Review**: January 15, 2026


# RESUME MODULE - DEVELOPER ONBOARDING CHECKLIST

**For anyone about to work on the resume module**

---

## ✅ BEFORE YOU START CODING

### Step 1: Understand What Was Done (5 min)
- [ ] Read **START_HERE_RESUME_MODULE.md** (quick overview)
- [ ] Read **RESUME_MODULE_SUMMARY.md** (executive summary)

### Step 2: Protect Existing Code (10 min) ⚠️ CRITICAL
- [ ] Read **RESUME_MODULE_COMPLETE_INVENTORY.md** (MUST READ)
- [ ] Note the **DO NOT MODIFY** list
- [ ] Understand change management rules
- [ ] Bookmark this file for reference

### Step 3: Know Your Tools (5 min)
- [ ] Bookmark **RESUME_MODULE_QUICK_REF.md** (for Q&A)
- [ ] Know where **RESUME_MODULE_TEST_SCRIPT.md** is (for testing)
- [ ] Know where **RESUME_MODULE_FIXES_REPORT.md** is (technical details)

---

## ✅ WHEN YOU NEED TO MAKE CHANGES

### Before Writing Code
1. [ ] Check RESUME_MODULE_COMPLETE_INVENTORY.md feature status
2. [ ] Check if feature you want to modify is on DO NOT MODIFY list
3. [ ] If it is: ⚠️ Ask for approval before changing
4. [ ] Review related test cases in RESUME_MODULE_TEST_SCRIPT.md
5. [ ] Understand what must keep working

### While Writing Code
1. [ ] Keep RESUME_MODULE_QUICK_REF.md open
2. [ ] Test after each change (don't wait until end)
3. [ ] Check console for errors (F12)
4. [ ] Check network for API errors (F12 Network tab)

### After Writing Code
1. [ ] Run related test cases from RESUME_MODULE_TEST_SCRIPT.md
2. [ ] Verify no regressions to other features
3. [ ] Check live preview still shows full width
4. [ ] Check duplicate still works
5. [ ] Check template still applies
6. [ ] Check export still works (all 4 formats)
7. [ ] Verify no console errors
8. [ ] Verify no network errors

### Before Committing
1. [ ] All tests passing
2. [ ] No console errors
3. [ ] No network errors
4. [ ] Documented any changes made
5. [ ] Updated RESUME_MODULE_COMPLETE_INVENTORY.md if needed

---

## 🚨 CRITICAL: DO NOT MODIFY WITHOUT ASKING

The following files/sections are PROTECTED and must not be changed without approval:

### Frontend
- [ ] **LiveTemplatePreview.tsx** lines 216-221 (width calculation)
- [ ] **ResumeEditor.tsx** section management logic (~400-600)
- [ ] **ResumePreview.tsx** rendering logic (~50-300)
- [ ] All export button functionality

### Backend
- [ ] **resumes.py** CRUD operations (lines ~50-180)
- [ ] **resume_export.py** all 4 export formats
- [ ] All database migration logic
- [ ] User authentication/authorization

### Database
- [ ] 30 seeded resume templates
- [ ] All resume table fields (add new, don't remove)
- [ ] All section models (WorkExperience, Education, etc.)

### If You Need to Change These
1. Check RESUME_MODULE_COMPLETE_INVENTORY.md DO NOT MODIFY list
2. Ask for approval first
3. Explain why the change is necessary
4. Run ALL tests (not just affected ones)
5. Document the change thoroughly

---

## 📚 QUICK REFERENCE BY TASK

### "I need to add a new feature"
1. Read: RESUME_MODULE_QUICK_REF.md - "I need to add a new field to resumes"
2. Follow the 7-step process
3. Run: RESUME_MODULE_TEST_SCRIPT.md relevant tests
4. Update: RESUME_MODULE_COMPLETE_INVENTORY.md with new feature

### "I found a bug"
1. Read: RESUME_MODULE_QUICK_REF.md debugging section
2. Check: RESUME_MODULE_COMPLETE_INVENTORY.md feature status
3. Fix: Only the buggy code
4. Test: Related test cases from RESUME_MODULE_TEST_SCRIPT.md
5. Report: What was broken, how you fixed it

### "Something broke when I made changes"
1. Check: Console for errors (F12)
2. Check: Network for API errors (F12 Network)
3. Read: RESUME_MODULE_QUICK_REF.md "How do I rollback?"
4. Revert: Your changes
5. Ask: For help understanding what went wrong

### "Live preview shows weird"
→ See RESUME_MODULE_QUICK_REF.md - "Live preview is showing weird"

### "Export not working"
→ See RESUME_MODULE_QUICK_REF.md - "Export to PDF not working"

### "Template not applying"
→ See RESUME_MODULE_QUICK_REF.md - "Template not applying"

### "Need to understand the code"
→ See RESUME_MODULE_FIXES_REPORT.md (before/after comparisons)

---

## ✅ TESTING CHECKLIST BEFORE COMMITTING

Run these tests BEFORE you push your changes:

### Core Functionality
- [ ] Can create resume ✅
- [ ] Can list resumes ✅
- [ ] Can edit resume ✅
- [ ] Can duplicate resume ✅
- [ ] Can delete resume ✅
- [ ] Live preview shows full width ✅
- [ ] Can apply template ✅

### Exports
- [ ] Export to PDF works ✅
- [ ] Export to DOCX works ✅
- [ ] Export to HTML works ✅
- [ ] Export to PNG works ✅

### Advanced
- [ ] ATS scoring works ✅
- [ ] Section management works ✅
- [ ] Can add/edit sections ✅

### Quality
- [ ] No console errors (F12) ✅
- [ ] No network errors (F12 Network) ✅
- [ ] Performance acceptable ✅
- [ ] No data loss ✅

If any of these fail: **DO NOT COMMIT**. Fix first.

---

## 📖 DOCUMENTATION READING ORDER

For **first-time learning**:
1. START_HERE_RESUME_MODULE.md
2. RESUME_MODULE_SUMMARY.md
3. RESUME_MODULE_COMPLETE_INVENTORY.md

For **making changes**:
1. RESUME_MODULE_COMPLETE_INVENTORY.md (check DO NOT MODIFY)
2. RESUME_MODULE_QUICK_REF.md (while coding)
3. RESUME_MODULE_TEST_SCRIPT.md (when testing)

For **debugging**:
1. RESUME_MODULE_QUICK_REF.md (debugging section)
2. RESUME_MODULE_FIXES_REPORT.md (see how similar issues were fixed)
3. RESUME_MODULE_COMPLETE_INVENTORY.md (understand feature status)

For **testing**:
1. RESUME_MODULE_TEST_SCRIPT.md (run relevant tests)
2. RESUME_MODULE_DEPLOYMENT_CHECKLIST.md (pre-deployment)

---

## 🎯 SUCCESS CRITERIA

Your changes are good if:

✅ All related tests pass
✅ No new console errors
✅ No new network errors
✅ Live preview still shows full width
✅ Duplicate still works
✅ Templates still apply
✅ All exports still work
✅ Performance acceptable
✅ Documentation updated
✅ RESUME_MODULE_COMPLETE_INVENTORY.md updated

If any of these are NOT met: Your code is not ready to commit.

---

## 🆘 WHEN YOU GET STUCK

### "I don't know what to change"
1. Check RESUME_MODULE_COMPLETE_INVENTORY.md for feature location
2. Read RESUME_MODULE_QUICK_REF.md for how-to
3. Look at similar code in the codebase
4. Ask team for guidance

### "My change broke something"
1. Check what broke in browser (F12 console)
2. Check RESUME_MODULE_QUICK_REF.md debugging section
3. Revert your change
4. Make smaller changes
5. Test after each change

### "I don't know if I should change this code"
1. Check RESUME_MODULE_COMPLETE_INVENTORY.md DO NOT MODIFY list
2. If it's on the list: Ask for approval
3. If it's not: You can probably change it (test thoroughly)

### "I don't know how to test this"
1. Check RESUME_MODULE_TEST_SCRIPT.md for test cases
2. Follow the step-by-step procedures
3. Compare results to "Expected"
4. Report any differences

### "I don't know if it's ready to deploy"
1. Run through RESUME_MODULE_DEPLOYMENT_CHECKLIST.md
2. Verify ALL items pass
3. If any fail: Fix before deploying

---

## 📊 FEATURE STATUS AT A GLANCE

✅ = Working, don't break it
⚠️ = Partially working, enhance carefully
⏳ = Not yet implemented

| Feature | Status | Notes |
|---------|--------|-------|
| Create | ✅ | Working |
| List | ✅ | Working |
| Edit | ✅ | Working (FIXED) |
| Live Preview | ✅ | Working (FIXED) |
| Duplicate | ✅ | Working (FIXED) |
| Apply Template | ✅ | Working (NEW) |
| Export (4 formats) | ✅ | All working |
| ATS Scoring | ✅ | Working |
| Delete | ✅ | Working |
| Import | ⚠️ | Works but loses template info |
| Comparison | ⚠️ | Works but UI minimal |
| Version History | ⚠️ | Works but UI minimal |
| Sharing | ⚠️ | Works but no permissions |
| Multi-page | ⏳ | Not implemented |
| Advanced ATS | ⏳ | Not implemented |
| Custom Templates | ⏳ | Not implemented |

---

## ✅ HANDOFF CHECKLIST

Before starting work, make sure you have:

- [ ] Read START_HERE_RESUME_MODULE.md
- [ ] Read RESUME_MODULE_COMPLETE_INVENTORY.md
- [ ] Read RESUME_MODULE_QUICK_REF.md
- [ ] Understand DO NOT MODIFY list
- [ ] Know where test script is
- [ ] Know how to test
- [ ] Know where to ask for help

---

## 🎊 YOU'RE READY!

If you've completed the checklist above, you're ready to:
- ✅ Understand what was done
- ✅ Know what not to break
- ✅ Know how to make safe changes
- ✅ Know how to test
- ✅ Know how to find help

**Welcome to the team!**

---

**This Checklist**: Ready to use
**Last Updated**: December 31, 2025
**Status**: ✅ COMPLETE


# SkillForge Global - Developer Final Checklist
**Status:** Ready for Safe Development  
**Updated:** January 5, 2025

---

## ✅ PRE-DEVELOPMENT CHECKLIST

Before writing ANY code, follow this checklist:

### 1. READ THE DOCUMENTATION (Required - 30 minutes)
- [ ] Read `CODEBASE_AUDIT_2024.md` section on your feature area
- [ ] Read `SAFE_DEVELOPMENT_QUICKSTART.md` entire document
- [ ] Understand the three rules of safe development
- [ ] Know which systems you can and cannot modify

### 2. UNDERSTAND YOUR FEATURE (Required - 1-2 hours)
For the feature you want to implement:
- [ ] Identify which backend endpoint(s) to create/modify
- [ ] Identify which frontend page(s) will use it
- [ ] List all database models that will be involved
- [ ] Check if those models already exist
- [ ] Understand the existing patterns in similar endpoints
- [ ] Identify any third-party integrations needed

### 3. CHECK FOR CONFLICTS (Required - 30 minutes)
- [ ] Search codebase: Is this feature partially done already?
- [ ] Check stub files: `/backend/app/api/v1x/*_stub.py` 
- [ ] Check incomplete endpoints: Look for 404 routes
- [ ] Ask: Can I extend existing code instead of rewriting?

### 4. PLAN YOUR CHANGES (Required - 30 minutes)
Write a plan before coding:
```
Feature: [Name]
Database: [New tables? Modify existing?]
Backend: [Endpoints to create/modify]
Frontend: [Pages/components needed]
Testing: [How will you verify it works?]
Rollback: [How will you undo if it breaks?]
```

### 5. REVIEW SIMILAR PATTERNS (Required - 1 hour)
Find working examples:
- [ ] Find a working endpoint doing something similar
- [ ] Study its structure: Schemas → Endpoints → Tests
- [ ] Copy the pattern (don't reinvent)
- [ ] Use same error codes and response formats

---

## 🚫 DO NOT TOUCH (Critical Systems)

**These files will break the entire application if modified:**

```python
# NEVER MODIFY
/backend/app/core/security.py         # Authentication
/backend/app/core/db.py               # Database connection
/backend/app/models/user.py           # User model - impacts 45+ tables
/backend/app/main.py (lines 1-100)   # Main app setup
/backend/app/main.py (lines 200-350) # Router mounting

# NEVER DELETE
/backend/app/core/
/backend/app/models/
Database tables (especially users, orders, resumes)
```

**If you need to modify these:**
1. Have a complete backup
2. Write comprehensive tests first
3. Have a rollback plan
4. Get code review before committing
5. Test for 2+ hours before merging

---

## ✅ SAFE TO EXTEND (Safe Systems)

**These systems are designed to be extended:**

### Backend - Safe to Modify
```python
/backend/app/api/v1x/         # Main API endpoints - safe to add new routes
/backend/app/modelsx/         # Data models - safe to add new models
/backend/app/schemas/         # Request/response schemas - safe to add new ones
/backend/app/services/        # Business logic - safe to add new services

# Examples of safe modifications:
✅ Add new endpoint in existing file
✅ Create new model in modelsx/
✅ Add new schema for validation
✅ Create new service file for logic
❌ Modify existing endpoint signatures (breaks frontend)
❌ Remove fields from schemas (breaks frontend)
❌ Change database column types (breaks existing data)
```

### Frontend - Safe to Modify
```python
/src/pages/               # Pages - safe to modify or add new
/src/components/         # Components - safe to add or modify
/src/hooks/             # Custom hooks - safe to add or modify
/src/lib/               # Utilities - safe to add or modify

# Safe modifications:
✅ Add new page
✅ Create new component
✅ Modify component styling
✅ Add new hook
❌ Modify API endpoint paths (need to match backend)
❌ Change authentication flow
❌ Modify core API client (in src/lib/api.ts)
```

---

## 🧪 BEFORE YOU COMMIT

### Step 1: Run Tests (1-2 hours)
```bash
# Test authentication
python backend/test_auth.py

# Test your feature works
python backend/test_[your_feature].py

# Test marketplace (always)
python backend/test_marketplace_complete.py

# Test critical endpoints
python backend/test_critical_features.py
```

### Step 2: Manual Testing (30-60 minutes)
```bash
# Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# In another terminal, start frontend
npm run dev

# Test your feature manually in browser:
1. Open http://localhost:3000
2. Login with demo user (see DEMO_CREDENTIALS.json)
3. Navigate to your feature
4. Test all user flows
5. Check browser console for errors
6. Check backend logs for warnings
```

### Step 3: Verify No Regression (30 minutes)
Test these critical flows:
- [ ] User login works
- [ ] User signup works  
- [ ] Can browse courses
- [ ] Can add to cart
- [ ] Can view cart
- [ ] Can remove from cart
- [ ] Can checkout
- [ ] Can view resume
- [ ] Can view mentor booking

If any of these fail, you broke something! Revert and investigate.

### Step 4: Check Your Code (30 minutes)
```bash
# Check for syntax errors
python -m py_compile backend/app/api/v1x/[your_file].py

# Check for import errors
python -c "from app.api.v1x import [your_module]"

# Verify database changes
python backend/check_db.py

# Verify no unused imports
pylint backend/app/api/v1x/[your_file].py
```

### Step 5: Create a Commit Message
```
[FEATURE] Add [feature name]

This commit adds [brief description].

Changes:
- Added GET /api/v1x/[endpoint] for [purpose]
- Created [ModelName] model in modelsx/
- Added tests for [feature]

Tests:
- Verified with test_[feature].py
- Tested manually on localhost
- Verified no regression in critical flows

Database:
- Added [tables/columns] ✓
- Verified with check_db.py ✓
```

---

## 🆘 EMERGENCY PROCEDURES

### If Something Breaks
```bash
# 1. Identify what broke (last 5 commits)
git log -5 --oneline

# 2. Undo the last commit
git revert HEAD

# 3. Restart backend/frontend
Ctrl+C to stop servers
python backend/app/main.py --reload
npm run dev

# 4. Test critical flows again
python test_auth.py
python test_cart_complete.py

# 5. If still broken, revert to last known good
git log --oneline | head -20  # Find good commit hash
git revert [hash]
```

### If Database is Corrupted
```bash
# 1. Delete corrupted database
rm backend/app/data/skillforge.db

# 2. Restart backend (auto-creates new DB)
python backend/app/main.py --reload

# 3. Seed demo data
python backend/seed_all_demo_data.py

# 4. Verify
python backend/check_db.py
```

### If Tests Are Failing
```bash
# 1. Check what's failing
python -m pytest backend/tests/ -v

# 2. Run just your test
python test_[feature].py

# 3. Run critical tests
python test_auth.py
python test_cart_complete.py

# 4. If critical tests fail, revert your changes
git revert HEAD
```

---

## 📊 DEVELOPMENT WORKFLOW (Per Feature)

### Day 1: Planning & Setup (2-3 hours)
- [ ] Understand feature requirements
- [ ] Plan database changes
- [ ] Plan API endpoints
- [ ] Create test file
- [ ] Write failing tests

### Day 2: Backend Implementation (4-6 hours)
- [ ] Create database models
- [ ] Create API endpoints
- [ ] Run tests
- [ ] Verify with curl/Postman
- [ ] Commit and push

### Day 3: Frontend Implementation (4-6 hours)
- [ ] Create page/component
- [ ] Integrate API calls
- [ ] Test manually
- [ ] Style and polish
- [ ] Commit and push

### Day 4: Testing & Polish (2-4 hours)
- [ ] Run full test suite
- [ ] Manual testing on all flows
- [ ] Fix any bugs
- [ ] Code review
- [ ] Final commit

### Day 5: Deployment & Monitoring (1-2 hours)
- [ ] Deploy to staging
- [ ] Smoke test on staging
- [ ] Monitor for errors
- [ ] Deploy to production
- [ ] Monitor for 24 hours

---

## 📚 QUICK REFERENCE COMMANDS

### Backend Commands
```bash
# Start backend
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Seed demo data
python backend/seed_all_demo_data.py

# Check database
python backend/check_db.py

# Run tests
python backend/test_auth.py
python backend/test_marketplace_complete.py

# Create new table
# 1. Create model in backend/app/modelsx/new_feature.py
# 2. Import in backend/app/main.py (before create_all())
# 3. Restart backend - table auto-creates
```

### Frontend Commands
```bash
# Start frontend
npm run dev

# Build frontend
npm run build

# Check for errors
npm run lint

# Format code
npm run format
```

### Git Commands
```bash
# Check status
git status

# Create branch
git checkout -b feature/[feature-name]

# Commit changes
git add .
git commit -m "[FEATURE] description"

# Push to remote
git push origin feature/[feature-name]

# Revert last commit
git revert HEAD

# See git log
git log --oneline
```

---

## 🎯 SUCCESS CRITERIA

Your feature is ready for production when:

- [ ] All tests pass (`python test_[feature].py`)
- [ ] Critical flows still work (auth, cart, checkout)
- [ ] No console errors in browser (F12)
- [ ] No warnings in backend logs
- [ ] Database changes verified (`python check_db.py`)
- [ ] Code follows existing patterns
- [ ] Documentation is updated
- [ ] Commit message is clear
- [ ] Code review is approved
- [ ] Manual testing on staging completed
- [ ] Monitoring setup for production deployment

---

## 💡 TIPS FOR SUCCESS

1. **Go Slow** - In a 200,000+ line codebase, going slow is going fast
2. **Test Early** - Write tests first, code second
3. **Keep It Small** - One feature at a time, small commits
4. **Follow Patterns** - Copy existing endpoint patterns, don't invent new ones
5. **Ask Questions** - If unsure, check existing code and documentation
6. **Backup Often** - Git commits are your safety net
7. **Document Changes** - Update docs as you code
8. **Help Others** - Document what you learn for the next developer

---

## 📞 GETTING HELP

If stuck:
1. Check existing endpoints in `/backend/app/api/v1x/` for patterns
2. Read the relevant section in `CODEBASE_AUDIT_2024.md`
3. Review test files for examples
4. Check `SAFE_DEVELOPMENT_QUICKSTART.md` for common issues
5. Read the copilot-instructions.md for this project

---

**Remember:** This is a production system with 80+ pages and 85+ endpoints. Be careful, test thoroughly, and keep changes small. You're doing great! 🚀

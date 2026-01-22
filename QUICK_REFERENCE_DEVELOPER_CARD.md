# QUICK REFERENCE CARD - SkillForge Global

**Print this or keep it in a tab!**

---

## 🎯 THE 3 RULES OF SAFE DEVELOPMENT

1. **UNDERSTAND DEPENDENCIES** - Know what depends on your change
2. **ALWAYS TEST AFTER CHANGE** - Run test suite after every edit
3. **KEEP CHANGES SMALL** - One feature at a time, small commits

---

## 🚫 DO NOT TOUCH

```
❌ /backend/app/core/security.py         (Auth)
❌ /backend/app/core/db.py               (Database)
❌ /backend/app/models/user.py           (User model)
❌ /backend/app/main.py (lines 1-100)   (Setup)
❌ /backend/app/main.py (lines 200-350) (Routers)
```

---

## ✅ SAFE TO MODIFY

```
✅ /backend/app/api/v1x/        (New endpoints)
✅ /backend/app/modelsx/        (New models)
✅ /backend/app/schemas/        (New schemas)
✅ /backend/app/services/       (New logic)
✅ /src/pages/                  (New pages)
✅ /src/components/             (New components)
```

---

## 🧪 TEST COMMANDS

```bash
# MUST PASS BEFORE YOU CODE
python test_auth.py
python test_cart_complete.py
python test_critical_features.py

# RUN YOUR TEST
python test_[your_feature].py

# RUN ALL TESTS
python -m pytest backend/tests/ -v
```

---

## 🚀 STARTUP COMMANDS

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
npm run dev

# Terminal 3: Seed data
python backend/seed_all_demo_data.py
```

---

## 💾 GIT COMMANDS

```bash
# Check status
git status

# Create branch
git checkout -b feature/[name]

# Commit
git add .
git commit -m "[FEATURE] description"

# Revert last commit
git revert HEAD

# Push
git push origin feature/[name]
```

---

## 🧠 BEFORE YOU CODE

- [ ] Read relevant doc section in CODEBASE_AUDIT_2024.md
- [ ] Check if feature partially exists
- [ ] Review similar endpoint patterns
- [ ] Understand database models needed
- [ ] Write test file first

---

## ⚡ QUICK ENDPOINT TEMPLATE

```python
# In /backend/app/api/v1x/[feature].py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from pydantic import BaseModel

# Schema
class MyRequest(BaseModel):
    field: str

class MyResponse(BaseModel):
    id: int
    field: str
    
    class Config:
        from_attributes = True

# Router
router = APIRouter(prefix="/feature", tags=["feature"])

@router.post("/action")
def my_endpoint(
    req: MyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Your code here
    return {"success": True}
```

---

## ⚡ QUICK MODEL TEMPLATE

```python
# In /backend/app/modelsx/[feature].py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    field = Column(String)
    
    # Relationship
    user = relationship("User", back_populates="my_items")
```

---

## 🔄 FEATURE IMPLEMENTATION CHECKLIST

- [ ] Identify database models needed
- [ ] Create/modify models in modelsx/
- [ ] Import model in app/main.py
- [ ] Create API endpoint in api/v1x/
- [ ] Create Pydantic schemas
- [ ] Write tests in test_[feature].py
- [ ] Test authentication works
- [ ] Test database operations
- [ ] Create frontend page in src/pages/
- [ ] Create API calls in frontend
- [ ] Test manually on localhost
- [ ] Run full test suite
- [ ] Commit and push

---

## 🐛 IF SOMETHING BREAKS

```bash
# Quick rollback
git revert HEAD

# Restart servers
Ctrl+C

# Test critical flows
python test_auth.py
python test_cart_complete.py

# If still broken
git log --oneline
git revert [bad_commit_hash]
```

---

## 📊 SYSTEM STATUS AT A GLANCE

| System | Status | Test File |
|--------|--------|-----------|
| Auth | ✅ | test_auth.py |
| Marketplace | ✅ | test_cart_complete.py |
| Resumes | ✅ | test_resume_module_complete.py |
| Mentors | ✅ Backend | test_mentor_apis.py |
| Courses | ✅ | Marketplace tests |
| Quizzes | ⚠️ | test_critical_features.py |
| Coding | ❌ | 500 error |

---

## 📚 DOCUMENTATION

| Doc | Purpose | Time |
|-----|---------|------|
| 00_START_HERE_AUDIT_COMPLETE.md | Overview | 5 min |
| COMPREHENSIVE_SESSION_SUMMARY.md | Status | 10 min |
| CODEBASE_AUDIT_2024.md | Details | 30 min |
| SAFE_DEVELOPMENT_QUICKSTART.md | Patterns | 30 min |
| DEVELOPER_FINAL_CHECKLIST.md | Checklist | 10 min |
| DOCUMENTATION_COMPLETE_INDEX.md | Full map | 20 min |

---

## 💻 KEY DIRECTORIES

```
Backend:
/backend/app/core/       - Security, database, config
/backend/app/models/     - Base models (user, etc)
/backend/app/modelsx/    - Domain models (45+ files)
/backend/app/schemas/    - Request/response validation
/backend/app/api/v1x/    - Current API endpoints
/backend/app/services/   - Business logic

Frontend:
/src/pages/              - Page components
/src/components/         - Reusable components
/src/hooks/             - Custom hooks
/src/lib/               - Utilities (api.ts for API calls)
```

---

## 🎯 COMMON TASKS

### Add a new endpoint
1. Create in `/backend/app/api/v1x/[feature].py`
2. Follow pattern from similar endpoint
3. Import in `app/main.py` if new router file
4. Mount with `app.include_router()`
5. Write test

### Add a database model
1. Create in `/backend/app/modelsx/[feature].py`
2. Import in `app/main.py`
3. Restart backend (table auto-creates)
4. Add relationships if needed

### Add a frontend page
1. Create in `/src/pages/[path]/[name].tsx`
2. Create API calls
3. Use layout components
4. Test on localhost

### Fix a bug
1. Create test that reproduces issue
2. Make minimal changes to fix
3. Verify test passes
4. Run full test suite
5. Commit with clear message

---

## ⚠️ COMMON MISTAKES TO AVOID

❌ **DON'T:** Change endpoint signatures (breaks frontend)
✅ **DO:** Add new endpoints instead

❌ **DON'T:** Remove fields from schemas
✅ **DO:** Add new fields when needed

❌ **DON'T:** Delete database columns
✅ **DO:** Add new columns when needed

❌ **DON'T:** Modify User model
✅ **DO:** Create new model if needed

❌ **DON'T:** Change router mounting in main.py
✅ **DO:** Only add new routers

❌ **DON'T:** Commit without testing
✅ **DO:** Run tests before every commit

---

## 🔐 SECURITY CHECKLIST

Before committing:
- [ ] Using authentication (get_current_user)
- [ ] Validating user_id matches current_user
- [ ] Input validation with Pydantic
- [ ] No hardcoded secrets
- [ ] Proper error messages (don't expose internals)
- [ ] HTTP status codes correct

---

## 📈 PERFORMANCE TIPS

- Use `joinedload()` for related data
- Add database indexes on foreign keys
- Cache repeated queries
- Paginate large result sets
- Test with large datasets

---

## 🚨 EMERGENCY CONTACTS

**Code Broken?**
→ DEVELOPER_FINAL_CHECKLIST.md "Emergency Procedures"

**Database Broken?**
→ Delete skillforge.db, restart backend, seed data

**Tests Failing?**
→ Run test_auth.py and test_cart_complete.py first

**Don't Know How?**
→ Read SAFE_DEVELOPMENT_QUICKSTART.md "Code Patterns"

**Need Details?**
→ Read CODEBASE_AUDIT_2024.md for your area

---

## ✨ YOU'RE SET!

You now have:
- ✅ Quick reference for common tasks
- ✅ Emergency procedures
- ✅ Test commands ready
- ✅ Key files identified
- ✅ Common mistakes to avoid
- ✅ Security checklist

**Go code something awesome! 🚀**

---

**Bookmark this page for quick reference!**

Last Updated: January 5, 2025

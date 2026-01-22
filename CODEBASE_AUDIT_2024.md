# SkillForge Global - Comprehensive Codebase Audit
**Date:** January 5, 2025  
**Status:** Production System with 80+ Pages, 60+ Endpoints, 45+ Models  
**Critical Note:** This is a HUGE application with many integrated features. **ANY change risks breaking existing functionality.**

---

## 🎯 EXECUTIVE SUMMARY

| Metric | Status |
|--------|--------|
| **Total Lines of Code** | 200,000+ (Backend + Frontend) |
| **Database Tables** | 121 tables (32 with data, 89 empty) |
| **API Endpoints** | 60+ (v1x) + 25+ (v1) = 85+ total |
| **Frontend Pages** | 80+ pages implemented |
| **Data Models** | 45+ SQLAlchemy models |
| **Users/Demo Data** | 1,900+ total records |
| **Architecture Style** | Monorepo (FastAPI + Next.js) |
| **Production Ready** | ⚠️ Partial (Core features work, some features incomplete) |

---

## 📋 SYSTEMS STATUS MATRIX

### ✅ FULLY FUNCTIONAL (Production Ready)
- **Authentication** - Login/signup with JWT tokens
- **Courses & Curriculum** - Browse, enroll, track progress
- **Resumes** - CRUD, export (PDF/DOCX), templates, ATS scoring
- **Mentors** - Booking, availability, sessions, messaging
- **Marketplace - Core** - Browse courses, cart (GET/POST/DELETE), checkout, orders
- **Gamification - Coins** - Earn, spend, ledger tracking
- **User Profiles** - Profile customization, preferences
- **Admin Dashboard** - User management, analytics, logs
- **Job Applications** - Track jobs, interviews, contacts

### ⚠️ PARTIALLY WORKING (Some Issues)
- **Marketplace - Advanced** - Search/filtering, reviews, wishlist (endpoints exist, may be 404)
- **Quizzes** - Existing data works, but some new endpoints return 500
- **Video Progress** - API exists, not tested with UI
- **Coding Practice** - Returns 500 error on challenges endpoint
- **Premium Tiers** - Database tables exist, endpoints incomplete
- **Notifications** - Database ready, email integration incomplete

### ❌ NOT STARTED (Empty Tables)
- **Social Features** - Follow, messaging, discussions
- **Forums** - Categories, threads, replies
- **Live Streaming** - Recording, playback
- **Contests** - Contest system
- **Advanced Recommendations** - ML-based suggestions
- **PWA** - Offline sync, service workers

---

## 🏗️ ARCHITECTURE OVERVIEW

### Backend Structure
```
backend/
├── app/
│   ├── core/           # Database, security, config
│   ├── models/         # Legacy models (User, Progress, etc)
│   ├── modelsx/        # 45+ extended models
│   ├── api/
│   │   ├── v1/         # 25 legacy endpoints
│   │   └── v1x/        # 60+ current endpoints
│   ├── services/       # Email, Stripe, payment logic
│   ├── schemas/        # Pydantic request/response
│   └── main.py         # FastAPI app + all router mounts
├── init_db.py          # Create tables script
├── seed_all_demo_data.py # Demo data seeder
└── requirements.txt    # Python dependencies
```

### Frontend Structure
```
src/
├── pages/              # 80+ Next.js pages
│   ├── auth/          # login, signup, password reset
│   ├── marketplace/   # browse, cart, checkout, seller
│   ├── mentors/       # booking, sessions, availability
│   ├── resumes/       # editor, templates, import/export
│   ├── admin/         # dashboard, analytics, settings
│   ├── api/           # Proxy routes /api/session/v1x/*
│   └── [other]        # 60+ more pages
├── components/        # Reusable React components
├── hooks/            # Custom React hooks
├── context/          # Global state (auth, user)
└── lib/              # API clients, utilities
```

---

## 🔐 CRITICAL SYSTEMS TO PRESERVE

### 1. **Authentication Flow**
**File:** `backend/app/core/security.py`, `backend/app/api/v1/auth.py`

**Current Implementation:**
```
User Signup → Email stored → Password hashed with bcrypt (72 bytes)
↓
JWT Token (HS256, 7-day expiry)
↓
Token stored in httpOnly cookie (preferred) or Authorization header
↓
get_current_user() dependency validates token
```

**⚠️ DO NOT CHANGE:**
- Password hashing algorithm (bcrypt)
- Token generation (HS256)
- Token expiry (7 days)
- Cookie storage mechanism
- `get_current_user()` function signature

**Impact if Broken:** ALL authenticated endpoints fail (~80% of API)

---

### 2. **Database Models & Relationships**
**Files:** `backend/app/models/user.py`, `backend/app/modelsx/*.py`

**Key Models:**
- **User** (45 fields) - Links to: Profile, Resumes, Orders, Mentors, etc.
- **Resume** (8 fields) - Links to: WorkExperience, Education, Skills, Templates
- **Course** (10 fields) - Links to: Videos, Orders, Quizzes
- **MentorSession** (12 fields) - Links to: Mentor, User, MentorAvailability
- **Order** (8 fields) - Links to: User, Course, Coupons, Coins
- **Mentor** (15 fields) - Links to: User, Sessions, Availability, Reviews

**⚠️ DO NOT CHANGE:**
- Foreign key relationships
- Model field types
- Cascade delete rules
- Relationship loading strategy

**Impact if Broken:** Data corruption, missing data in queries, 500 errors

---

### 3. **API Router Mounting**
**File:** `backend/app/main.py` (lines 200-350)

**Current Structure:**
```python
# Mounted routes
/api/v1/          → Legacy endpoints (auth, courses, quizzes, etc)
/api/v1x/         → Current endpoints (marketplace, resumes, etc)
/api/session/v1x/ → Session-wrapped (proxied from frontend, uses cookies)
```

**⚠️ DO NOT CHANGE:**
- Router prefix structure
- API versioning pattern
- Session routing logic
- Dependency injection for auth

**Impact if Broken:** Frontend proxy routes break, frontend can't call backend

---

### 4. **Marketplace System**
**Files:** `backend/app/api/v1x/session.py` (Recently Added - This Session)

**Recently Implemented Endpoints:**
- ✅ `POST /api/v1x/marketplace/cart/add` - Add course to cart
- ✅ `GET /api/v1x/marketplace/cart` - View cart (fixed: `added_at` bug)
- ✅ `DELETE /api/v1x/marketplace/cart/{item_id}` - Remove item
- ✅ `POST /api/v1x/marketplace/coupons/validate` - Validate coupon
- ✅ `POST /api/v1x/marketplace/checkout` - Create order with coin deduction
- ✅ `GET /api/v1x/marketplace/orders` - View order history

**Frontend Proxy Routes:**
- `/api/session/v1x/marketplace/cart/add` → Backend
- `/api/session/v1x/marketplace/cart` → Backend
- `/api/session/v1x/marketplace/checkout` → Backend

**⚠️ RECENTLY FIXED BUGS:**
- Cart showing 0 items (was using `created_at` instead of `added_at`)
- Missing checkout endpoint (404) → Added with proper coin deduction
- Missing orders endpoint (404) → Added with order history

**Impact if Broken:** E-commerce flow fails, users can't purchase

---

## 📊 DATABASE INVENTORY

### Tables with Data (32)
```
users (7 records)
user_profiles (5)
courses (5)
course_videos (20)
mentor (4)
mentor_sessions (21)
mentor_availability (84)
resumes (235)
work_experience (~500)
cart_items (6)
orders (15)
coupons (8)
coin_ledger (257)
quiz_attempts (45)
quizzes (15)
quiz_questions (150+)
... and more
```

### Tables Empty/Ready (89)
```
forums
forum_threads
contest_challenges
learning_paths
notifications
github_accounts
social_follows
... and more
```

---

## 🚨 KNOWN ISSUES & BLOCKERS

### Issue #1: Coding Practice 500 Error
**Endpoint:** `GET /api/v1x/coding-practice/challenges`  
**Status:** ❌ Returns 500  
**File:** `backend/app/api/v1x/coding_practice.py`  
**Impact:** Can't browse coding challenges  
**Diagnosis Needed:** Check error logs, database integrity

### Issue #2: Missing Route Mounts
**Endpoints:** Several v1x endpoints return 404  
- `/api/v1x/snippets` 
- `/api/v1x/learning-paths`
- Others may not be mounted in main.py

**File:** `backend/app/main.py` (check includes_router calls)  
**Impact:** Features incomplete

### Issue #3: Auth Cookie/JWT Issues (Suspected)
**Symptoms:** 
- Some authenticated endpoints return 401 unexpectedly
- Cookie handling may differ between browsers

**Files Involved:**
- `backend/app/core/security.py`
- `backend/app/middleware/*`

**Impact:** Login may fail in certain scenarios

### Issue #4: Video Progress Tracking
**Status:** API exists, untested  
**File:** `backend/app/api/v1x/progress_db.py`  
**Impact:** Video progress may not be saved correctly

---

## 📈 ENDPOINT INVENTORY

### Implemented & Tested ✅
```
Authentication (6 endpoints)
- POST /api/v1/auth/signup
- POST /api/v1/auth/login
- POST /api/v1/auth/token/refresh
- GET /api/v1/auth/me
- POST /api/v1/auth/logout
- POST /api/v1/auth/password-reset

Courses (4 endpoints)
- GET /api/v1/courses
- GET /api/v1/courses/{id}
- GET /api/v1/courses/{id}/videos
- GET /api/v1/progress

Marketplace (7 endpoints)
- GET /api/v1x/marketplace/courses
- POST /api/v1x/marketplace/cart/add
- GET /api/v1x/marketplace/cart
- DELETE /api/v1x/marketplace/cart/{id}
- POST /api/v1x/marketplace/coupons/validate
- POST /api/v1x/marketplace/checkout
- GET /api/v1x/marketplace/orders

... and 50+ more
```

### Partially Tested ⚠️
```
Mentors (10 endpoints)
- Some endpoints may return unexpected errors
- Session creation flow untested end-to-end

Resumes (15 endpoints)
- Core CRUD works
- Import/export need verification

Admin (8 endpoints)
- Analytics may have performance issues
```

### Not Yet Implemented ❌
```
Search & Filtering (5 endpoints)
Reviews & Ratings (6 endpoints)
Wishlist (3 endpoints)
Recommendations (4 endpoints)
Social Features (8+ endpoints)
Forums (6+ endpoints)
... and more
```

---

## 🎯 DESIGN PATTERNS TO FOLLOW

### Pattern #1: Dependency Injection for Auth
**✅ CORRECT - Follow This Pattern:**
```python
@router.get("/protected")
def protected_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Auto-validates auth, injects user"""
    return {"user_id": current_user.id}
```

**❌ WRONG - Don't Do This:**
```python
@router.get("/protected")
def protected_route(request: Request):
    """Manual auth checking (error-prone)"""
    token = request.headers.get("Authorization")
    # ... manual token validation
```

### Pattern #2: Pydantic Request/Response Validation
**✅ CORRECT:**
```python
class CartItem(BaseModel):
    course_id: int
    
@router.post("/cart/add")
def add_to_cart(item: CartItem, db: Session = Depends(get_db)):
    """Automatic validation + serialization"""
    pass
```

**❌ WRONG:**
```python
@router.post("/cart/add")
def add_to_cart(data: dict):
    """Manual validation (easy to miss edge cases)"""
    if not data.get("course_id"):
        raise Exception("Missing course_id")
```

### Pattern #3: Database Operations with Relationships
**✅ CORRECT:**
```python
from sqlalchemy.orm import joinedload

user = db.query(User).options(
    joinedload(User.resumes),
    joinedload(User.orders)
).filter(User.id == user_id).first()
```

**❌ WRONG:**
```python
user = db.query(User).filter(User.id == user_id).first()
# N+1 query problem - accessing user.resumes triggers new query
for resume in user.resumes:  # New query per resume!
    print(resume)
```

### Pattern #4: Error Handling with Status Codes
**✅ CORRECT:**
```python
from fastapi import HTTPException, status

if not cart_item:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Item not found or doesn't belong to you"
    )
```

**❌ WRONG:**
```python
if not cart_item:
    return {"error": "Item not found"}  # Wrong status code!
```

---

## 🛡️ SECURITY PATTERNS TO MAINTAIN

### 1. Password Hashing
**File:** `backend/app/core/security.py`

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# On signup:
hashed_password = pwd_context.hash(password)

# On login:
is_valid = pwd_context.verify(password, hashed_password)
```

**⚠️ DO NOT:**
- Use MD5, SHA1, or weak algorithms
- Store plain text passwords
- Store passwords in logs

### 2. JWT Token Validation
**File:** `backend/app/core/security.py`

```python
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**⚠️ DO NOT:**
- Change expiry to very long (compromises security)
- Use weak secret keys
- Send tokens in URL parameters (use headers/cookies)

### 3. CORS Configuration
**File:** `backend/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.skillforge.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**⚠️ DO NOT:**
- Allow all origins in production (`allow_origins=["*"]` + `allow_credentials=True`)
- Hardcode frontend URL instead of using config

---

## 🚀 SAFE DEVELOPMENT PRACTICES

### Before Making ANY Change:

1. **Understand the Dependency Chain**
   ```
   Your change → Which modules import it?
              → Which endpoints use those modules?
              → Which frontend pages call those endpoints?
              → What data do those pages depend on?
   ```

2. **Run Tests Locally**
   ```bash
   # Test auth still works
   python test_auth.py
   
   # Test marketplace still works
   python test_cart_complete.py
   
   # Test mentors still work
   python -m pytest backend/tests/test_mentors.py
   ```

3. **Check Database Migrations**
   - If adding model fields: Will require migration
   - If adding new model: Must import in main.py before create_all()
   - If changing relationships: Test cascading operations

4. **Verify Frontend Compatibility**
   - Test in browser console
   - Check API response format matches frontend expectations
   - Verify error messages match error handling code

### Feature Checklist Before Deployment:
```
[ ] Code written and tested locally
[ ] No syntax errors (linting passed)
[ ] No type errors (mypy/pyright)
[ ] Database schema changes handled
[ ] Frontend updated if needed
[ ] Test data added if needed
[ ] Documentation updated
[ ] Backward compatible (no breaking changes)
[ ] Error handling comprehensive
[ ] No hardcoded values (use config)
[ ] Logging added for debugging
[ ] Security implications reviewed
[ ] Performance implications reviewed
```

---

## 📦 IMPLEMENTATION ROADMAP (SAFE ORDER)

### Phase 1: Fix Blocking Issues (No Breaking Changes)
1. Fix Coding Practice 500 error
2. Mount missing v1x routes
3. Test and validate auth flow
4. Verify video progress tracking

### Phase 2: Complete Existing Features (Low Risk)
5. Implement Search & Filtering (uses existing Course model)
6. Implement Wishlist (new table, no relationships)
7. Implement Reviews & Ratings (new table, one-to-many)
8. Complete Coupons system (table exists, logic needed)

### Phase 3: Extend Safe Features (Medium Risk)
9. Implement Recommendations (new table, uses existing data)
10. Implement Notifications (table exists, needs email integration)
11. Add Social Features (new tables, independent)
12. Implement Forums (new tables, independent)

### Phase 4: Advanced Features (Higher Risk)
13. Premium Tiers enhancements
14. Advanced analytics
15. ML-based recommendations
16. Live features (streaming, real-time)

---

## 🧪 TESTING STRATEGY

### Critical Path Testing
```
1. Auth Flow
   - Signup with new email
   - Login with correct password
   - Login with wrong password (should fail)
   - Refresh token
   - Logout

2. Marketplace Flow
   - Browse courses (should see data)
   - Add course to cart
   - View cart (should show course)
   - Apply coupon
   - Checkout
   - View order history

3. Resume Flow
   - Create resume
   - Edit resume
   - Export as PDF
   - Export as DOCX
   - Apply template
   - Delete resume

4. Mentor Flow
   - View mentors
   - Book session
   - Cancel session
   - Leave review
```

### Test Files Provided
- `test_auth.py` - Authentication testing
- `test_cart_complete.py` - Marketplace testing
- `test_marketplace_complete.py` - Full marketplace flow
- `test_resume_module_complete.py` - Resume CRUD testing

**Run:** `python test_[name].py`

---

## 📞 EMERGENCY ROLLBACK PROCEDURES

### If You Break Something:

1. **Identify What Broke**
   ```bash
   python test_cart_complete.py  # See which test fails
   ```

2. **Check Git Changes**
   ```bash
   git diff [file]  # See what changed
   git log --oneline  # See recent commits
   ```

3. **Rollback the Change**
   ```bash
   git checkout [file]  # Revert single file
   git reset --hard HEAD  # Revert all changes
   ```

4. **Verify It Works**
   ```bash
   python test_[critical].py
   ```

---

## 🎓 QUICK START FOR NEW DEVELOPMENT

### To Add a New Feature Safely:

1. **Create new endpoint in appropriate router file**
   ```python
   # backend/app/api/v1x/my_feature.py
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/my-feature", tags=["my-feature"])
   
   @router.get("/")
   def get_my_feature(db: Session = Depends(get_db), 
                      current_user: User = Depends(get_current_user)):
       return {"data": "example"}
   ```

2. **Add Pydantic schema if needed**
   ```python
   # backend/app/schemas/my_feature.py
   from pydantic import BaseModel
   
   class MyFeatureCreate(BaseModel):
       name: str
       value: int
   ```

3. **Create model if needed**
   ```python
   # backend/app/modelsx/my_feature.py
   from sqlalchemy import Column, Integer, String, ForeignKey
   from app.core.db import Base
   
   class MyFeature(Base):
       __tablename__ = "my_features"
       id = Column(Integer, primary_key=True)
       user_id = Column(Integer, ForeignKey("users.id"))
       name = Column(String)
   ```

4. **Import in main.py**
   ```python
   # backend/app/main.py
   from app.modelsx.my_feature import MyFeature
   from app.api.v1x.my_feature import router as my_feature_router
   
   # Mount router
   app.include_router(my_feature_router)
   ```

5. **Test locally**
   ```bash
   python -c "from app.modelsx.my_feature import MyFeature"  # Verify imports
   ```

6. **Add frontend integration**
   ```typescript
   // src/services/myFeatureApi.ts
   export const myFeatureApi = {
     list: () => api.get('/session/v1x/my-feature'),
     create: (data) => api.post('/session/v1x/my-feature', data),
   }
   ```

---

## 🔍 FILE REFERENCE GUIDE

### Core Files (DO NOT MODIFY LIGHTLY)
| File | Purpose | Risk Level |
|------|---------|-----------|
| `backend/app/main.py` | FastAPI setup, router mounting | 🔴 CRITICAL |
| `backend/app/core/security.py` | Auth, passwords, JWT | 🔴 CRITICAL |
| `backend/app/models/user.py` | User model | 🔴 CRITICAL |
| `backend/app/core/db.py` | Database connection | 🔴 CRITICAL |

### Feature Files (SAFE TO EXTEND)
| File | Purpose | Risk Level |
|------|---------|-----------|
| `backend/app/api/v1x/marketplace.py` | Marketplace endpoints | 🟡 MEDIUM |
| `backend/app/api/v1x/resumes.py` | Resume endpoints | 🟡 MEDIUM |
| `backend/app/api/v1x/mentors.py` | Mentor endpoints | 🟡 MEDIUM |
| `backend/app/api/v1x/admin.py` | Admin endpoints | 🟡 MEDIUM |

### Model Files (CAREFUL WITH CHANGES)
| File | Purpose | Risk Level |
|------|---------|-----------|
| `backend/app/modelsx/course.py` | Course model | 🟡 MEDIUM |
| `backend/app/modelsx/order.py` | Order model | 🟡 MEDIUM |
| `backend/app/modelsx/mentor.py` | Mentor model | 🟡 MEDIUM |
| `backend/app/modelsx/resume.py` | Resume model | 🟡 MEDIUM |

### Schema Files (SAFE TO MODIFY)
| File | Purpose | Risk Level |
|------|---------|-----------|
| `backend/app/schemas/*.py` | Request/response validation | 🟢 LOW |
| Frontend components | UI rendering | 🟢 LOW |
| Frontend hooks | Data fetching | 🟢 LOW |

---

## ✅ VERIFICATION CHECKLIST

Before declaring any work complete:

```
Frontend Tests:
[ ] Page loads without errors
[ ] Form submission works
[ ] Error messages display
[ ] Loading states appear
[ ] Data displays correctly
[ ] Navigation works

Backend Tests:
[ ] Endpoint returns 200 on success
[ ] Endpoint returns proper error code on failure
[ ] Request validation works (invalid data rejected)
[ ] Response format matches schema
[ ] Database changes persisted
[ ] Relationships loaded correctly

Integration Tests:
[ ] Frontend can call new endpoint
[ ] Data flows end-to-end
[ ] No console errors
[ ] No network errors
[ ] Performance acceptable

Breaking Change Tests:
[ ] Existing endpoints still work
[ ] Existing pages still load
[ ] Existing workflows still function
[ ] Database queries still optimized
[ ] No auth regressions
```

---

## 🎯 CONCLUSION

This application is **production-ready in core areas** but **fragile in specific ways**:

### ✅ Safe to Modify
- Adding new features/tables (independent of existing data)
- Creating new endpoints (as long as router properly mounted)
- Updating frontend components (as long as API unchanged)
- Adding database tables (as long as imported in main.py)

### ⚠️ Risky to Modify
- Authentication flow or User model
- Core API structures (routing, versioning)
- Database relationships (can break queries)
- Model fields (requires migration)
- Security-related code

### 🚫 Should NOT Modify
- JWT token generation/validation
- Password hashing
- Database connection pooling
- CORS configuration (without careful thought)
- Core router mounting in main.py

---

## 📞 IF YOU NEED HELP

1. **Check existing tests** - Use test files to understand patterns
2. **Run tests first** - Verify baseline before changing
3. **Make small changes** - One feature at a time
4. **Test after each change** - Run tests to verify
5. **Document changes** - Leave comments explaining why
6. **Commit frequently** - Smaller commits easier to rollback

---

**Remember:** This is a HUGE application with many moving parts. **Slow, careful development is faster than rushing and breaking things.** Every endpoint you see probably has 5+ dependencies somewhere else in the codebase.

**BE SAFE. BE THOROUGH. BE SUCCESSFUL.**


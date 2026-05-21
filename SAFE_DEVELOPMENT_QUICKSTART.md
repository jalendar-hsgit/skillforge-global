# SkillForge Global - Safe Development Quick Reference
**Last Updated:** January 5, 2025  
**Critical:** Read CODEBASE_AUDIT_2024.md first before making ANY changes

---

## 🎯 THE THREE RULES OF SAFE DEVELOPMENT

### Rule 1: Understand Dependencies
Before changing ANYTHING, ask:
- "What imports this file?"
- "What endpoints use this code?"
- "What frontend pages call those endpoints?"
- "What data do those pages need?"

### Rule 2: Always Test AFTER Change
```bash
# Test authentication still works
python test_auth.py

# Test marketplace still works
python test_cart_complete.py

# Test critical endpoints
python test_marketplace_complete.py
```

### Rule 3: Keep Changes Small
- One feature at a time
- Test after each change
- Commit frequently
- If something breaks, git revert is your friend

---

## 🚨 CRITICAL SYSTEMS (HANDS OFF!)

These systems handle core functionality. **Changing them breaks EVERYTHING.**

| System | Files | Why Critical | Impact if Broken |
|--------|-------|-------------|-----------------|
| **Authentication** | `app/core/security.py` | Controls all user access | 100% of API fails |
| **Database** | `app/core/db.py`, `app/models/user.py` | All data flows through here | Data loss/corruption |
| **Router Setup** | `app/main.py` (lines 200-350) | Maps URLs to endpoints | No endpoints accessible |
| **User Model** | `app/models/user.py` | 45+ other models depend on this | Cascading failures |

**RULE:** If you must modify these, have a backup and test plan.

---

## ✅ SAFE SYSTEMS (OK TO EXTEND)

These systems are well-isolated. You can extend them safely.

| System | Files | What's Safe | What's Not |
|--------|-------|-----------|-----------|
| **Marketplace** | `app/api/v1x/marketplace.py` | ✅ Add new endpoints | ❌ Change Order model |
| **Resumes** | `app/api/v1x/resumes.py` | ✅ Add new features | ❌ Modify Resume relationships |
| **Mentors** | `app/api/v1x/mentors.py` | ✅ Add endpoints | ❌ Change MentorSession schema |
| **Admin** | `app/api/v1x/admin.py` | ✅ Add analytics | ❌ Remove authorization checks |

---

## 🔧 QUICKSTART: Adding a New Feature

### Step 1: Create Endpoint File
```python
# backend/app/api/v1x/my_feature.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/my-feature", tags=["my-feature"])

@router.get("/")
def get_my_feature(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get my feature data"""
    return {"data": "example", "user": current_user.id}
```

### Step 2: Add Request/Response Schema
```python
# backend/app/schemas/my_feature.py
from pydantic import BaseModel

class MyFeatureResponse(BaseModel):
    id: int
    name: str
    value: int
    
    class Config:
        from_attributes = True
```

### Step 3: Create Database Model (if needed)
```python
# backend/app/modelsx/my_feature.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.core.db import Base

class MyFeature(Base):
    __tablename__ = "my_features"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    value = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Step 4: Import Model in main.py
```python
# backend/app/main.py (BEFORE create_all() call)
from app.modelsx.my_feature import MyFeature
```

### Step 5: Mount Router in main.py
```python
# backend/app/main.py (In router include section)
from app.api.v1x.my_feature import router as my_feature_router

app.include_router(my_feature_router)  # This creates /api/v1x/my-feature
```

### Step 6: Test Locally
```bash
# Verify model imports
python -c "from app.modelsx.my_feature import MyFeature; print('OK')"

# Start server
uvicorn app.main:app --reload

# Test endpoint
curl http://localhost:8001/api/v1x/my-feature \
  -H "Authorization: Bearer <your-token>"
```

### Step 7: Add Frontend Integration
```typescript
// src/services/myFeatureApi.ts
import { api } from '@/lib/api'

export const myFeatureApi = {
  list: async () => {
    const res = await api.get('/session/v1x/my-feature')
    return res.data
  },
  
  create: async (data: MyFeatureCreate) => {
    const res = await api.post('/session/v1x/my-feature', data)
    return res.data
  }
}
```

### Step 8: Verify No Breaking Changes
```bash
python test_auth.py           # Auth still works?
python test_cart_complete.py  # Marketplace still works?
python test_marketplace_complete.py # All flows work?
```

---

## 🎓 CODE PATTERNS: DO'S AND DON'TS

### Pattern #1: Authentication
```python
# ✅ DO THIS - Uses dependency injection
@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id}

# ❌ DON'T DO THIS - Manual auth checking
@router.get("/protected")
def protected_route(request: Request):
    token = request.headers.get("Authorization")
    # ... manual parsing and validation
```

### Pattern #2: Database Queries with Relationships
```python
# ✅ DO THIS - Eager load relationships
from sqlalchemy.orm import joinedload

user = db.query(User).options(
    joinedload(User.resumes)
).filter(User.id == user_id).first()

# ❌ DON'T DO THIS - Causes N+1 queries
user = db.query(User).filter(User.id == user_id).first()
for resume in user.resumes:  # New query per resume!
    print(resume)
```

### Pattern #3: Validation
```python
# ✅ DO THIS - Use Pydantic schemas
class CartItemCreate(BaseModel):
    course_id: int

@router.post("/cart/add")
def add_to_cart(item: CartItemCreate):
    # item.course_id is guaranteed valid integer
    pass

# ❌ DON'T DO THIS - Manual validation
@router.post("/cart/add")
def add_to_cart(data: dict):
    if not data.get("course_id"):
        raise Exception("Missing course_id")
    try:
        course_id = int(data["course_id"])
    except ValueError:
        raise Exception("Invalid course_id")
```

### Pattern #4: Error Handling
```python
# ✅ DO THIS - Proper HTTP status codes
from fastapi import HTTPException, status

if not cart_item:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Item not found"
    )

# ❌ DON'T DO THIS - Wrong status codes
if not cart_item:
    return {"error": "Item not found"}  # Returns 200 OK!
```

### Pattern #5: Response Models
```python
# ✅ DO THIS - Explicit response model
class OrderResponse(BaseModel):
    id: int
    total: float
    status: str
    
    class Config:
        from_attributes = True

@router.get("/orders", response_model=List[OrderResponse])
def list_orders():
    orders = db.query(Order).all()
    return orders  # Pydantic serialization

# ❌ DON'T DO THIS - Raw dict responses
@router.get("/orders")
def list_orders():
    orders = db.query(Order).all()
    return [o.__dict__ for o in orders]  # SQLAlchemy internals exposed
```

---

## 🧪 TESTING CHECKLIST

Before declaring work done:

### Unit Tests
- [ ] Function works with valid input
- [ ] Function handles invalid input gracefully
- [ ] Edge cases handled (empty, null, duplicates)
- [ ] Error messages are helpful

### Integration Tests
- [ ] Endpoint returns correct status code
- [ ] Response format matches schema
- [ ] Authentication works (401 if no token)
- [ ] Authorization works (403 if no permission)
- [ ] Database changes persisted

### Regression Tests
- [ ] Auth still works (`test_auth.py`)
- [ ] Marketplace still works (`test_cart_complete.py`)
- [ ] Existing endpoints still respond
- [ ] No console errors in frontend
- [ ] No new network errors

### Performance Tests
- [ ] Database queries optimized (no N+1)
- [ ] Response time acceptable (< 500ms)
- [ ] No memory leaks
- [ ] Pagination works for large datasets

---

## 🐛 DEBUGGING GUIDE

### Backend Error: 500 Internal Server Error

```python
# 1. Check the error logs
# Output appears in console where you ran uvicorn

# 2. Enable detailed error messages
# In backend/app/main.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)

# 3. Add print statements to trace execution
@router.post("/my-endpoint")
def my_endpoint(data: MySchema):
    print(f"Received data: {data}")
    try:
        result = process_data(data)
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Frontend Error: API Request Fails

```typescript
// 1. Check browser console (F12)
// Look for error message and status code

// 2. Check network tab (F12 → Network)
// Click on request, see response body

// 3. Add console logging
const response = await fetch('/api/session/v1x/my-endpoint')
console.log('Status:', response.status)
console.log('Response:', await response.json())

// 4. Use browser fetch with better error handling
try {
  const res = await fetch('/api/session/v1x/my-endpoint', {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  const data = await res.json()
  if (!res.ok) {
    console.error('API Error:', res.status, data)
  }
} catch (error) {
  console.error('Network Error:', error)
}
```

### Database Error: Table Not Found

```python
# 1. Verify model is imported in main.py
# backend/app/main.py should have:
from app.modelsx.my_feature import MyFeature

# 2. Verify table created
from app.core.db import engine, Base
Base.metadata.create_all(engine)  # Called in main.py on startup

# 3. Check if model is registered
from app.core.db import Base
print([table.name for table in Base.metadata.tables.values()])
# Should include your table name
```

---

## 🔄 WORKFLOW: START TO FINISH

### Day 1: Planning
```
1. Identify feature to implement
2. Create issue/ticket
3. Review CODEBASE_AUDIT_2024.md
4. Check for dependencies
5. Design database schema (if needed)
6. Design API endpoints
7. Estimate complexity
```

### Day 2: Development
```
1. Create branch: git checkout -b feature/my-feature
2. Implement endpoint
3. Implement schema
4. Implement model (if needed)
5. Test locally with curl/Postman
6. Fix any bugs
7. Run test suite
```

### Day 3: Integration
```
1. Create frontend component
2. Add API integration
3. Test end-to-end
4. Check responsive design
5. Test error scenarios
6. Run full regression tests
```

### Day 4: Polish
```
1. Add error handling
2. Add logging
3. Add documentation
4. Add comments for complex logic
5. Code review
6. Final testing
```

### Day 5: Deploy
```
1. Merge to main branch
2. Deploy to staging
3. Test on staging
4. Deploy to production
5. Monitor for errors
6. Celebrate! 🎉
```

---

## 📊 ENDPOINTS STATUS REFERENCE

### ✅ Known Working
- Auth endpoints (login, signup)
- Course endpoints (list, get)
- Marketplace endpoints (browse, cart, checkout, orders) - RECENTLY FIXED
- Resume endpoints (CRUD, export)
- Mentor endpoints (list, book)
- Admin endpoints (stats, users)

### ⚠️ Potentially Broken
- Coding practice (returns 500)
- Video progress (untested)
- Search/filtering (endpoints may be 404)
- Some v1x routes (may not be mounted)

### ❌ Not Implemented
- Search results
- Review system
- Wishlist
- Recommendations
- Social features
- Forums

---

## 💾 DATABASE REFERENCE

### Key Tables to Know
```
users          - All platform accounts
courses        - Course definitions
cart_items     - User shopping carts
orders         - Completed purchases
mentors        - Mentor profiles
mentor_sessions - Booked sessions
resumes        - User resumes
coin_ledger    - Currency tracking
```

### Relationships You Need to Know
```
User 1→ Many Resumes
User 1→ Many Orders
User 1→ Many CartItems
User 1→ Many MentorSessions (as student)
User 1→ One Mentor (if role=MENTOR)

Order 1→ One User
Order 1→ One Course
OrderMay have Coupon

Resume 1→ Many WorkExperience
Resume 1→ Many Education
Resume 1→ Many ResumeSkill
```

---

## 🎯 SUCCESS METRICS

After implementing a feature, verify:
```
✅ Code Quality
   - No syntax errors
   - No type errors (TypeScript/Python)
   - No console warnings
   - Follows project patterns

✅ Functionality
   - Feature works as designed
   - All test cases pass
   - Error scenarios handled
   - Edge cases covered

✅ Performance
   - Response time < 500ms
   - Database queries optimized
   - No memory leaks
   - No N+1 queries

✅ Security
   - Authentication enforced
   - Authorization checked
   - Input validated
   - No SQL injection risk
   - No XSS vulnerabilities

✅ Compatibility
   - No breaking changes
   - Backward compatible
   - Existing tests still pass
   - Frontend/backend aligned

✅ Documentation
   - Code commented
   - API documented
   - Database schema documented
   - Deployment instructions clear
```

---

## 🚀 YOU'RE READY

You now have:
1. ✅ Full codebase audit (CODEBASE_AUDIT_2024.md)
2. ✅ Safe development patterns
3. ✅ Testing procedures
4. ✅ Quick reference guide (this file)
5. ✅ Example implementations

**Remember:**
- **Slow development is fast development**
- **Small changes are safer than big ones**
- **Test after every change**
- **Commit frequently**
- **If unsure, read the code first**

---

**Questions?** Check CODEBASE_AUDIT_2024.md or look at similar existing features in the codebase.

**Good luck! Build smart, build safe, build successful! 🚀**


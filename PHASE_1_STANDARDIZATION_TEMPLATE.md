# PHASE 1 QUICK REFERENCE - APPLY STANDARDIZATION TO REMAINING ROUTERS

**Status:** 1 router complete (auth.py), 5+ routers remaining  
**Effort:** 2-3 hours total  
**Template:** Copy-paste friendly

---

## 🎯 STANDARDIZATION TEMPLATE

### Step 1: Add Import at Top of Router File
```python
from app.core.responses import success_response, error_response, ERROR_MESSAGES, SUCCESS_MESSAGES
```

### Step 2: Replace Return Statements

**For Successful Operations:**
```python
# BEFORE:
return {"user_id": 1, "name": "John"}

# AFTER:
return success_response(
    data={"user_id": 1, "name": "John"},
    message="Operation successful",
    path="/api/v1x/endpoint"
)
```

**For List Operations:**
```python
# BEFORE:
return [item1, item2, item3]

# AFTER:
return success_response(
    data={"items": [item1, item2, item3], "total": 3},
    message="Items retrieved successfully",
    path="/api/v1x/endpoint"
)
```

**For Deletion:**
```python
# BEFORE:
return {"deleted": True}

# AFTER:
return success_response(
    data=None,
    message=SUCCESS_MESSAGES["RESOURCE_DELETED"],
    path="/api/v1x/endpoint"
)
```

**For Creation:**
```python
# BEFORE:
return {"id": 5, "name": "New Resource"}

# AFTER:
return success_response(
    data={"id": 5, "name": "New Resource"},
    message=SUCCESS_MESSAGES["RESOURCE_CREATED"],
    path="/api/v1x/endpoint"
)
```

### Step 3: Replace Error Messages

**For HTTPException:**
```python
# BEFORE:
raise HTTPException(status_code=404, detail="Resource not found")

# AFTER:
raise HTTPException(
    status_code=404,
    detail=ERROR_MESSAGES["RESOURCE_NOT_FOUND"]
)
```

---

## 📋 ROUTERS TO UPDATE (In Order of Priority)

### Priority 1: Core Auth & User Features
- [ ] **`backend/app/api/v1x/auth.py`** ✅ DONE
- [ ] **`backend/app/api/v1x/account.py`** - User account management
- [ ] **`backend/app/api/v1x/user_profiles.py`** - User profile endpoints

### Priority 2: Core Learning Features
- [ ] **`backend/app/api/v1x/courses.py`** - Course endpoints
- [ ] **`backend/app/api/v1x/quizzes.py`** - Quiz endpoints
- [ ] **`backend/app/api/v1x/learning_paths.py`** - Learning path endpoints

### Priority 3: Mentor & Jobs
- [ ] **`backend/app/api/v1x/mentors.py`** - Mentor endpoints
- [ ] **`backend/app/api/v1x/job_applications.py`** - Job application endpoints

### Priority 4: Marketplace & Orders
- [ ] **`backend/app/api/v1x/marketplace.py`** - Marketplace endpoints
- [ ] **`backend/app/api/v1x/orders.py`** - Order endpoints
- [ ] **`backend/app/api/v1x/marketplace_checkout.py`** - Checkout endpoints

### Priority 5: Admin Features
- [ ] **`backend/app/api/v1x/admin.py`** - Admin endpoints
- [ ] **`backend/app/api/v1x/admin_marketplace.py`** - Admin marketplace
- [ ] **`backend/app/api/v1x/admin_mentors.py`** - Admin mentor management
- [ ] **`backend/app/api/v1x/admin_analytics.py`** - Analytics endpoints

### Priority 6: Social & Engagement
- [ ] **`backend/app/api/v1x/forums.py`** - Forum endpoints
- [ ] **`backend/app/api/v1x/chat.py`** - Chat endpoints
- [ ] **`backend/app/api/v1x/notifications.py`** - Notification endpoints

---

## 🔄 WORKING PATTERN

For each router file:

1. **Add import** (1 line)
   ```python
   from app.core.responses import success_response, error_response, ERROR_MESSAGES, SUCCESS_MESSAGES
   ```

2. **Find all `return` statements** that return dictionaries
   - Use: Ctrl+F and search for `return {`
   - Count how many there are

3. **Replace each return statement** with standardization
   - Use find-and-replace or manual edits
   - Verify path matches endpoint

4. **Replace error messages** with constants
   - Search for: `raise HTTPException`
   - Replace `detail=` values with `ERROR_MESSAGES[...]`

5. **Test the router**
   - Use existing endpoint to verify

---

## 💡 COMMON PATTERNS

### Pattern 1: Get Single Resource
```python
@router.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["RESOURCE_NOT_FOUND"])
    
    return success_response(
        data=item,  # Already serializable if schema is used
        message="Item retrieved successfully",
        path=f"/api/v1x/items/{item_id}"
    )
```

### Pattern 2: List Resources
```python
@router.get("/items")
def list_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    
    return success_response(
        data={"items": items, "total": len(items)},
        message="Items retrieved successfully",
        path="/api/v1x/items"
    )
```

### Pattern 3: Create Resource
```python
@router.post("/items", status_code=201)
def create_item(data: ItemRequest, db: Session = Depends(get_db)):
    item = Item(**data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return success_response(
        data=item,
        message=SUCCESS_MESSAGES["RESOURCE_CREATED"],
        path="/api/v1x/items"
    )
```

### Pattern 4: Update Resource
```python
@router.put("/items/{item_id}")
def update_item(item_id: int, data: ItemRequest, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["RESOURCE_NOT_FOUND"])
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    
    return success_response(
        data=item,
        message=SUCCESS_MESSAGES["RESOURCE_UPDATED"],
        path=f"/api/v1x/items/{item_id}"
    )
```

### Pattern 5: Delete Resource
```python
@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["RESOURCE_NOT_FOUND"])
    
    db.delete(item)
    db.commit()
    
    return success_response(
        data=None,
        message=SUCCESS_MESSAGES["RESOURCE_DELETED"],
        path=f"/api/v1x/items/{item_id}"
    )
```

---

## ✅ CHECKLIST FOR EACH ROUTER

- [ ] Added import statement at top
- [ ] Found all `return {` statements
- [ ] Replaced each with `success_response()`
- [ ] Updated error messages to use `ERROR_MESSAGES[...]`
- [ ] Verified all paths are correct
- [ ] Tested at least one endpoint manually
- [ ] No syntax errors when starting backend

---

## 🧪 QUICK TEST TEMPLATE

After updating each router, test with:

```bash
# Test successful operation
curl -X GET http://localhost:8001/api/v1x/resource \
  -H "Authorization: Bearer TOKEN"

# Expected output:
{
  "success": true,
  "data": {...},
  "message": "...",
  "error": null,
  "timestamp": "...",
  "path": "/api/v1x/resource"
}

# Test error case
curl -X GET http://localhost:8001/api/v1x/resource/999 \
  -H "Authorization: Bearer TOKEN"

# Expected output:
{
  "success": false,
  "data": null,
  "message": "...",
  "error": "RESOURCE_NOT_FOUND",
  "timestamp": "...",
  "path": "/api/v1x/resource/999"
}
```

---

## ⏱️ TIME ESTIMATE PER ROUTER

- **Small routers** (20-50 endpoints): 30 min
- **Medium routers** (50-100 endpoints): 1 hour
- **Large routers** (100+ endpoints): 1.5 hours

**Total for all routers:** 2-3 hours

---

## 📝 NOTES

1. **Backward Compatibility:** Don't worry about v1 routers yet; focus on v1x
2. **Schema Usage:** If using Pydantic schemas, data is already serializable
3. **Path Variable:** Extract from request path or use string formatting
4. **Testing:** Use curl commands above to verify each update
5. **Git:** Commit after each router is complete: `git commit -m "refactor: standardize responses in [router_name].py"`


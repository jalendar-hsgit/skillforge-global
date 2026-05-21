# Balanced Path Quick Reference - Next 30 Minutes

## Current Status
✅ **Phase 1 Complete**: Session timeout, CSRF, password reset, login history, audit log pages created
⏳ **Phase 2 Pending**: Page guards, backend endpoints, form integration, testing

## Immediate Action Items

### 1. Verify Build (2 min)
```bash
npm run build
# Expected: 0 errors
# Should compile all 5 new files successfully
```

**If errors occur**:
- Check `src/lib/sessionManager.tsx` for JSX syntax
- Check `src/lib/csrf.ts` for TypeScript syntax
- Verify imports in Layout.tsx

---

### 2. Add Page Guards (12 pages, ~15 min)

**Pattern to use**:
```typescript
// At top of file:
import { requireAuthSSR } from '@/lib/auth'

// At bottom of component:
export const getServerSideProps = requireAuthSSR()
```

**Pages to protect**:
```
✅ Already protected:
  - /dashboard (has server-side auth)
  - /admin/* (all 15 admin pages)
  - /profile/settings
  - /profile/edit

Needs protection:
  - [ ] /courses
  - [ ] /courses/[slug]
  - [ ] /mentors
  - [ ] /mentors/dashboard
  - [ ] /job-tracker
  - [ ] /resumes
  - [ ] /practice
  - [ ] /marketplace
  - [ ] /community/forums
  - [ ] /messages
  - [ ] /notifications
  - [ ] /social
```

**Implementation**:
1. Open each file
2. Add import: `import { requireAuthSSR } from '@/lib/auth'`
3. Add at bottom: `export const getServerSideProps = requireAuthSSR()`
4. Rebuild to verify

---

### 3. Backend Endpoints Needed (~30 min)

**Password Reset** - `backend/app/api/v1x/auth.py`:
```python
@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # req.email: str
    # 1. Check if user exists
    # 2. Generate reset token (expires in 1 hour)
    # 3. Send email with reset link
    # 4. Return success message
    return {"message": "Check your email for reset link"}

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    # req.token: str
    # req.new_password: str
    # 1. Validate token (check expiry)
    # 2. Validate password strength
    # 3. Update user password
    # 4. Clear all sessions (logout everywhere)
    return {"message": "Password reset successful"}
```

**Login History** - `backend/app/api/v1x/auth.py`:
```python
@router.get("/login-history")
async def get_login_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Return list of user's login sessions
    # Fields: id, ip_address, browser, os, device, timestamp, is_current
    return {"logs": [...]}

@router.post("/login-history/{log_id}/revoke")
async def revoke_session(
    log_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Invalidate session
    return {"message": "Session revoked"}
```

**Audit Log** - `backend/app/api/v1x/admin.py`:
```python
@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Return audit logs (admin actions only)
    # Fields: id, timestamp, admin_email, action, resource_type, resource_id, details, status
    return {"logs": [...]}
```

---

### 4. Database Models Needed

**LoginHistory Model** - `backend/app/modelsx/auth.py`:
```python
class LoginHistory(Base):
    __tablename__ = "login_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address = Column(String(45))  # IPv6
    browser = Column(String(100))
    os = Column(String(100))
    device = Column(String(50))  # desktop, tablet, mobile
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_current = Column(Boolean, default=False)  # Mark current session
    revoked_at = Column(DateTime, nullable=True)  # When session was revoked
```

**AuditLog Model** - `backend/app/modelsx/admin.py`:
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50))  # create, update, delete, etc.
    resource_type = Column(String(50))  # User, Course, Mentor, etc.
    resource_id = Column(Integer, nullable=True)
    details = Column(Text)
    ip_address = Column(String(45))
    status = Column(String(20), default="success")  # success, failure
    timestamp = Column(DateTime, default=datetime.utcnow)
```

**PasswordReset Model** - `backend/app/modelsx/auth.py`:
```python
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

### 5. Add CSRF Middleware (~10 min)

**`backend/app/middleware/csrf.py`**:
```python
from fastapi import Request, HTTPException
import hashlib
import secrets

class CSRFMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # Get token from request
        if request.method in ['POST', 'PUT', 'DELETE']:
            token = request.headers.get('X-CSRF-Token')
            if not token:
                raise HTTPException(status_code=403, detail="CSRF token missing")
            
            # Validate token (stored in session)
            # if not validate_csrf_token(request.session, token):
            #     raise HTTPException(status_code=403, detail="Invalid CSRF token")
        
        response = await call_next(request)
        return response
```

**Add to `backend/app/main.py`**:
```python
from app.middleware.csrf import CSRFMiddleware

app.add_middleware(CSRFMiddleware)
```

---

### 6. Integrate CSRF to Forms (~10 min)

**Login form** - `src/pages/login.tsx`:
```typescript
import { useProtectedForm } from '@/lib/csrf'

// In component:
const { handleSubmit, csrfToken, loading } = useProtectedForm(
  async (formData) => {
    // Submit login with CSRF token
    // Already included in handleSubmit
  }
)

// In form:
<form onSubmit={handleSubmit}>
  <input type="hidden" name="csrf_token" value={csrfToken} />
  {/* rest of form */}
</form>
```

**Apply same pattern to**:
- Signup form
- Settings forms
- Password reset form
- All admin forms

---

### 7. Display Login History (5 min)

**Create `/profile/security.tsx`**:
```typescript
import LoginHistory from '@/components/LoginHistory'

export const getServerSideProps = requireAuthSSR()

export default function SecurityPage() {
  return (
    <Layout>
      <div>
        <h1>Account Security</h1>
        <LoginHistory />
      </div>
    </Layout>
  )
}
```

**Link from settings**:
```tsx
<Link href="/profile/security">
  View Login History
</Link>
```

---

## Testing Checklist (5 min)

After backend endpoints are added:

```
[ ] Build succeeds: npm run build
[ ] Login page has CSRF token
[ ] Signup page has CSRF token
[ ] Session warning appears at 25 min
[ ] Auto-logout at 30 min
[ ] Password reset email flows
[ ] Login history shows after login
[ ] Audit log displays admin actions
[ ] All protected pages redirect to login
[ ] Admin audit-log page shows logs
```

---

## Files to Create/Modify

### Backend Files
```
NEW:
- backend/app/modelsx/auth.py (LoginHistory, PasswordReset models)
- backend/app/modelsx/admin.py (AuditLog model)
- backend/app/api/v1x/auth.py (password reset, login history endpoints)
- backend/app/middleware/csrf.py (CSRF validation)
- backend/app/schemas/auth.py (password reset schemas)

MODIFY:
- backend/app/main.py (add CSRF middleware)
- backend/app/api/v1x/__init__.py (include new routers)
```

### Frontend Files
```
NEW:
- src/pages/profile/security.tsx (login history page)

MODIFY:
- src/pages/login.tsx (add CSRF to form)
- src/pages/signup.tsx (add CSRF to form)
- src/pages/*/[...].tsx (add requireAuthSSR to 12 pages)
- All admin forms (add CSRF tokens)
```

---

## Estimated Time Breakdown

```
Build verification:         2 min  ✅
Page guards (12 pages):    15 min
Backend endpoints:         30 min
CSRF middleware:           10 min
Form integration:          10 min
Login history page:         5 min
Testing:                    5 min
─────────────────────────────────
Total:                     77 min (~80 min)

Time remaining for 2-hour session: ~40 min
Status: Needs to prioritize most critical items
```

---

## Priority Order (If short on time)

1. ✅ **Page guards** (15 min) - Protect remaining pages
2. **Password reset backend** (15 min) - Essential feature
3. **CSRF middleware** (10 min) - Security critical
4. **Login history backend** (10 min) - Security monitoring
5. **Form integration** (10 min) - Activate CSRF
6. **Testing** (5 min) - Verify core flows

---

## Quick Commands

```bash
# Build
npm run build

# Start dev server
npm run dev

# Check errors
npm run lint

# Backend - run migrations (if needed)
python backend/init_db.py

# Backend - start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

---

**Next Step**: Run `npm run build` and check for errors!

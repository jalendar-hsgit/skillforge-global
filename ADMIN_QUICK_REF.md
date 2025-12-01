# 🔐 Admin System Quick Reference

## Initial Setup (First Time)

```powershell
cd "d:\python code\sfg\skillforge-global\backend"
python setup_first_admin.py
```

Follow the interactive prompts. This creates your first superadmin.

## Daily Operations

### Creating New Admins

**Step 1:** User signs up normally
```
Visit: http://localhost:3000/signup
(They get "user" role automatically)
```

**Step 2:** Superadmin promotes them
```
1. Login as superadmin
2. Go to: http://localhost:3000/admin/users
3. Find user → Change Role → Select "admin" or "superadmin"
```

### Role Hierarchy

```
user         → Basic access (default for all signups)
  ↓
mentor       → Can mentor students (needs approval)
  ↓
admin        → Can manage users, view logs, moderate content
  ↓
superadmin   → Full system access, can promote others
```

### Access URLs

```
Public:
  /signup          → Anyone can register (creates "user")
  /login           → Login page

Admin Only:
  /admin           → Dashboard (admin/superadmin)
  /admin/users     → User management
  /admin/mentors   → Mentor applications
  /admin/sessions  → Session management
  /admin/logs      → Audit trail
```

## Security Rules

✅ **Allowed:**
- Public signup (creates "user" role only)
- Superadmin promoting users to admin
- Admins viewing/managing users
- Superadmins deleting users

❌ **Blocked:**
- Public creation of admin accounts
- Users accessing /admin pages
- Admins promoting to superadmin
- Self-promotion of role

## Emergency Procedures

### Reset Superadmin Password
```powershell
python create_admin.py your.email@company.com superadmin
# Enter new password when prompted
```

### Demote Unauthorized Admin
```powershell
python create_admin.py bad.actor@email.com user
```

### List All Admins
```powershell
python -c "from app.core.db import SessionLocal; from app.models.user import User, UserRole; db = SessionLocal(); [print(f'{u.email} - {u.role}') for u in db.query(User).filter(User.role.in_([UserRole.ADMIN, UserRole.SUPERADMIN])).all()]"
```

## Audit & Monitoring

All admin actions are logged with:
- Who (admin email)
- What (action type)
- When (timestamp)
- Target (user/resource ID)
- Where (IP address)

View at: `http://localhost:3000/admin/logs`

## Key Files

```
Backend:
  backend/setup_first_admin.py      → Interactive first superadmin setup
  backend/create_admin.py           → Promote/create admins (CLI)
  backend/app/api/v1/auth.py        → Signup (user only)
  backend/app/api/v1x/admin.py      → Admin endpoints (role updates)
  backend/app/models/user.py        → User model with role

Frontend:
  src/pages/signup.tsx              → Public signup (user only)
  src/pages/admin/users.tsx         → User management (superadmin)
  src/lib/adminAuth.ts              → SSR auth guard

Documentation:
  ADMIN_SECURITY_GUIDE.md           → Complete security guide
```

## Best Practices

1. **Keep it minimal:** Only 2-3 superadmins max
2. **Use admin for most staff:** Superadmin is for senior personnel only
3. **Monitor logs:** Check /admin/logs weekly
4. **Strong passwords:** 12+ chars, mixed case, numbers, symbols
5. **Document promotions:** Note why someone got admin access
6. **Regular audits:** Review admin list monthly
7. **Secure CLI access:** Only trusted personnel have server access

## Common Tasks

### Promote User to Admin
```
Web: /admin/users → Find user → Change Role → Admin
CLI:  python create_admin.py user@email.com admin
```

### Create New Superadmin
```
CLI only: python create_admin.py new.super@email.com superadmin
(Or use /admin/users if user already exists)
```

### View All Admin Actions
```
Web: /admin/logs → Filter by action type
```

### Remove Admin Access
```
Web: /admin/users → Find user → Change Role → User
```

## Testing

```powershell
# Test 1: Public signup creates user role
Visit /signup → Creates account with role="user" ✓

# Test 2: Admin panel blocked for users
Login as regular user → Visit /admin → Redirected ✓

# Test 3: Superadmin can promote
Login as superadmin → /admin/users → Change role ✓

# Test 4: Actions are logged
Promote user → Check /admin/logs → Entry exists ✓
```

## Support

Questions? See `ADMIN_SECURITY_GUIDE.md` for detailed explanations.

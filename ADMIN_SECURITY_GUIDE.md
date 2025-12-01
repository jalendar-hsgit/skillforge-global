# 🔐 Secure Admin System - Complete Setup Guide

## Security Architecture

### Three-Tier Access Control:
1. **Regular Users** - Self-registered, basic access
2. **Admins** - Promoted by superadmin, can manage users/content  
3. **Superadmins** - Full system access, can promote others

## Initial Setup (First Time Only)

### Step 1: Create First Superadmin (Organization Owner)

**Important:** This is the ONLY time you use the CLI script. This creates your organization's first superadmin account.

```powershell
cd "d:\python code\sfg\skillforge-global\backend"
python create_admin.py founder@yourcompany.com superadmin
```

You'll be prompted for a password (minimum 8 characters).

**Output:**
```
User founder@yourcompany.com not found. Creating new user...
Enter password for new admin: ********
✅ New superadmin user created: founder@yourcompany.com

User Details:
  ID: 1
  Email: founder@yourcompany.com
  Role: superadmin
  Created: 2025-12-01 04:30:15
```

### Step 2: Start the Application

**Backend:**
```powershell
cd "d:\python code\sfg\skillforge-global\backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Frontend:**
```powershell
cd "d:\python code\sfg\skillforge-global"
npm run dev
```

### Step 3: Login as Superadmin

1. Visit: `http://localhost:3000/login`
2. Enter your superadmin credentials
3. You'll be redirected to the dashboard

## Day-to-Day Admin Management

### Creating New Admins (The Secure Way)

**❌ WRONG (Insecure - Now Disabled):**
- Public signup page with role selection
- Anyone can create admin accounts
- Major security vulnerability

**✅ CORRECT (Secure - Current System):**

#### Option 1: Promote Existing User (Recommended)

1. User signs up normally at `/signup` (they become regular user)
2. Superadmin logs into admin panel
3. Goes to `/admin/users`
4. Finds the user in the list
5. Changes their role to `admin` or `superadmin`
6. Action is logged in audit trail

#### Option 2: CLI Script (For Trusted Personnel Only)

```powershell
# Promote existing user
python create_admin.py existing.user@company.com admin

# Create new admin directly
python create_admin.py new.admin@company.com admin
# (Enter password when prompted)
```

### Admin Panel User Management

**Superadmin Dashboard:** `http://localhost:3000/admin`

**Manage Users:** `http://localhost:3000/admin/users`
- View all users
- Filter by role
- Promote/demote users
- Delete users (superadmin only)
- All actions are audit logged

**API Endpoints (for superadmins):**
```
GET  /api/v1x/admin/users              # List all users
POST /api/v1x/admin/users/{id}/role    # Update user role
  Body: {"role": "admin"}  or  {"role": "superadmin"}
  
DELETE /api/v1x/admin/users/{id}       # Delete user (permanent)
```

## Security Best Practices

### ✅ DO:
- Keep superadmin credentials secure (password manager)
- Use strong passwords (12+ characters, mixed case, numbers, symbols)
- Regularly review admin panel audit logs
- Promote users to admin only when necessary
- Use `admin` role for most staff, `superadmin` only for senior IT/founders
- Monitor `/admin/logs` for suspicious activity

### ❌ DON'T:
- Share superadmin credentials
- Create admin accounts via public endpoints
- Leave the `/admin-signup` page accessible (it's now removed)
- Give superadmin access to everyone
- Ignore audit logs

## Access Control Summary

| Feature | User | Admin | Superadmin |
|---------|------|-------|------------|
| Self-register | ✅ | ❌ | ❌ |
| Access courses | ✅ | ✅ | ✅ |
| View admin panel | ❌ | ✅ | ✅ |
| Manage users | ❌ | ✅ | ✅ |
| Promote to admin | ❌ | ❌ | ✅ |
| Delete users | ❌ | ❌ | ✅ |
| View audit logs | ❌ | ✅ | ✅ |
| Manage mentors | ❌ | ✅ | ✅ |
| Platform settings | ❌ | ❌ | ✅ |

## Testing the Secure Flow

### Test 1: Regular User Signup ✅
```powershell
# Anyone can do this
Visit: http://localhost:3000/signup
Email: test.user@example.com
Password: SecurePass123
Role: (not shown - always creates as 'user')
```

### Test 2: Admin Promotion ✅
```powershell
# Only superadmin can do this

# Method A: Via Admin Panel
1. Login as superadmin
2. Visit: http://localhost:3000/admin/users
3. Find user, click "Change Role" → "Admin"

# Method B: Via CLI
python create_admin.py test.user@example.com admin
```

### Test 3: Unauthorized Access ✅
```
# Regular user tries to access admin panel
Visit: http://localhost:3000/admin
→ Redirected to: /login?redirect=/admin
→ After login as regular user: 403 Forbidden or redirect
```

## Troubleshooting

### "I forgot the superadmin password"
```powershell
# Reset via CLI (requires server access)
python create_admin.py founder@company.com superadmin
# Enter new password when prompted
```

### "I need to remove admin access from someone"
```powershell
# Login as superadmin, go to /admin/users
# Find user, change role back to "user"

# Or via CLI:
python create_admin.py problematic.admin@company.com user
```

### "Can I create multiple superadmins?"
Yes, but limit to 2-3 trusted people (founder, CTO, senior IT).
```powershell
python create_admin.py cto@company.com superadmin
python create_admin.py it-lead@company.com superadmin
```

## Migration Notes

If you already have users created with admin/superadmin roles via the old public signup:

```powershell
# Review all admin users
python -c "
from app.core.db import SessionLocal
from app.models.user import User, UserRole
db = SessionLocal()
admins = db.query(User).filter(User.role.in_([UserRole.ADMIN, UserRole.SUPERADMIN])).all()
for u in admins:
    print(f'{u.id}: {u.email} - {u.role}')
db.close()
"

# Demote unauthorized admins
python create_admin.py unauthorized@email.com user
```

## Audit Logging

Every admin action is logged:
- Who performed the action (admin email)
- What action (update_user_role, delete_user, etc.)
- When (timestamp)
- Target resource (user ID, etc.)
- Details (old role → new role)
- IP address and user agent

View logs: `http://localhost:3000/admin/logs`

## Production Deployment

Additional security for production:

1. **HTTPS Only** - Set `secure=True` on cookies
2. **Strong Passwords** - Enforce policy (already has 8 char minimum)
3. **2FA** - Add for superadmin accounts (future enhancement)
4. **Rate Limiting** - Already in place (5 signups/hour per IP)
5. **Audit Alerts** - Monitor for suspicious role changes
6. **Database Backups** - Before bulk user operations

## Summary

**The New Secure Flow:**
```
1. Organization owner → CLI script → First Superadmin created
2. Superadmin logs in → Admin panel access
3. Regular users → Public signup → Basic "user" role
4. Superadmin promotes → Trusted users → Admin/Superadmin roles
5. All actions logged → Audit trail → Security monitoring
```

This is industry-standard secure admin management. No public admin signup, all promotions require existing superadmin authentication.

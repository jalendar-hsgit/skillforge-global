# SkillForge Global - User Credentials

## Test Users for Development & E2E Testing

All users have been created and verified. Use these credentials for login testing.

### Superadmin Account
- **Email:** `superadmin@skillforge.com`
- **Password:** `super123`
- **Role:** SUPERADMIN
- **Access:** Full system access, can manage all users and settings

### Admin Account
- **Email:** `admin@skillforge.com`
- **Password:** `admin123`
- **Role:** ADMIN
- **Access:** Platform administrator, can manage courses, users, and content

### Mentor Account
- **Email:** `mentor@skillforge.com`
- **Password:** `mentor123`
- **Role:** MENTOR
- **Access:** Can mentor students, manage sessions, view earnings

### Regular User Account
- **Email:** `user@skillforge.com`
- **Password:** `user123`
- **Role:** USER
- **Access:** Standard user access, can take courses, quizzes, build resumes

## Login Endpoints

### Backend API (Direct)
```bash
POST http://127.0.0.1:8001/api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@skillforge.com",
  "password": "admin123"
}
```

### Frontend (via UI)
```
http://127.0.0.1:3000/login
```

## Signup

New users can sign up through:
```
POST http://127.0.0.1:8001/api/v1/auth/signup
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "New User" // optional
}
```

**Note:** All public signups default to USER role. Only superadmins can promote users to admin/mentor/superadmin roles.

## Testing Commands

### PowerShell - Test All User Logins
```powershell
cd backend
$tests = @(
    @{email="superadmin@skillforge.com";password="super123";role="Superadmin"},
    @{email="admin@skillforge.com";password="admin123";role="Admin"},
    @{email="mentor@skillforge.com";password="mentor123";role="Mentor"},
    @{email="user@skillforge.com";password="user123";role="User"}
)
foreach ($test in $tests) {
    $body = @{email=$test.email;password=$test.password} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/auth/login" -Method POST -ContentType "application/json" -Body $body
    if ($result.logged) {
        Write-Host "✓ $($test.role) login successful" -ForegroundColor Green
    }
}
```

### cURL - Test Login
```bash
curl -X POST http://127.0.0.1:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@skillforge.com","password":"admin123"}'
```

## Re-creating Users

If you need to recreate or update users, run:
```bash
cd backend
python seed_admin_users.py
```

This script will:
- Create all missing user types
- Update existing users to ensure roles are correct
- Display final status of all users

## Database Location

User data is stored in SQLite database:
- Location: `backend/skillforge.db`
- Table: `users`
- Schema: id, email, password_hash, role, created_at

## Security Notes

- All passwords are hashed using bcrypt
- Auth tokens are stored in HTTP-only cookies
- Default cookie lifespan: 7 days
- Rate limiting is disabled in E2E_TEST_MODE for testing

---
**Last Updated:** December 3, 2025
**Status:** ✅ All users verified and working

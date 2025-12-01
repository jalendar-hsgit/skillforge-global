# Admin System Documentation

## Overview

The SkillForge Global admin system provides comprehensive platform management with role-based access control (RBAC), audit logging, and a powerful dashboard interface.

## Architecture

### Role-Based Access Control (RBAC)

Four user roles with increasing privileges:

1. **User** (`user`) - Regular platform user
2. **Mentor** (`mentor`) - Can apply to become a mentor (application still requires approval)
3. **Admin** (`admin`) - Platform administrator with management capabilities
4. **Superadmin** (`superadmin`) - Full system access, can manage other admins

### Security Model

- **JWT Cookie Authentication**: All admin endpoints require valid authentication
- **Role Guards**: `get_current_admin()` and `get_current_superadmin()` dependencies
- **Audit Logging**: All admin actions are logged with IP, user agent, timestamp
- **Action Restrictions**: 
  - Only superadmins can change user roles
  - Only superadmins can delete users
  - Admins cannot demote themselves

## Backend API Endpoints

### Admin Dashboard

**GET `/api/v1x/admin/dashboard/stats`**
- Returns comprehensive platform statistics
- Requires: Admin role
- Response includes:
  - User metrics (total, active in 30 days)
  - Mentor stats (total, pending applications)
  - Session metrics (total, scheduled, completed)
  - Revenue data

### User Management

**GET `/api/v1x/admin/users`**
- List all users with filtering
- Query params: `role`, `search`, `limit`, `offset`
- Requires: Admin role

**PATCH `/api/v1x/admin/users/{user_id}/role`**
- Update user role
- Body: `{"role": "user|mentor|admin|superadmin"}`
- Requires: Superadmin role
- Prevents self-demotion

**DELETE `/api/v1x/admin/users/{user_id}`**
- Permanently delete a user
- Requires: Superadmin role
- Cannot delete self

### Mentor Management

**GET `/api/v1x/mentors/admin/mentors/applications`**
- List mentor applications
- Query param: `status` (pending, approved, rejected, suspended)
- Requires: Admin role

**PATCH `/api/v1x/mentors/admin/mentors/{mentor_id}/status`**
- Approve, reject, or suspend mentor
- Body: `{"status": "approved|rejected|suspended"}`
- Requires: Admin role
- Logged to audit trail

### Session Management

**GET `/api/v1x/mentors/admin/sessions`**
- List all mentoring sessions
- Query param: `status` (scheduled, completed, cancelled, no_show)
- Requires: Admin role

**PATCH `/api/v1x/admin/sessions/{session_id}/status`**
- Update session status
- Body: `{"status": "cancelled|no_show|completed", "reason": "optional"}`
- Requires: Admin role
- Logged to audit trail

### Audit Logs

**GET `/api/v1x/admin/logs`**
- Retrieve audit log entries
- Query params: `action`, `resource_type`, `limit`, `offset`
- Requires: Admin role
- Returns: Admin action history with timestamps, IPs, details

### Platform Settings (Placeholder)

**GET `/api/v1x/admin/settings`**
**POST `/api/v1x/admin/settings`**
- Get/update platform configuration
- Requires: Superadmin role (POST)
- TODO: Implement database storage

## Frontend Pages

### `/admin` - Dashboard
- Real-time statistics cards
- Quick action links
- Recent admin activity feed
- Pending approval badges

### `/admin/users` - User Management
- Search and filter users by role
- Inline role updates (dropdown)
- Delete user action
- Shows user count by role

### `/admin/mentors` - Mentor Applications
- Filter by application status
- Approve/reject workflow
- View mentor profiles and expertise
- Application statistics

### `/admin/sessions` - Session Moderation
- Filter by session status
- Cancel or mark sessions as no-show
- View session details
- Quick navigation to session page

### `/admin/courses` - Course Management
- Add course videos via admin key
- Select learning path
- Input YouTube ID and metadata

### `/admin/logs` - Audit Trail
- Filter by action type and resource
- View admin email, action details
- IP address and timestamp tracking
- Color-coded action types

## Setup & Migration

### 1. Run Database Migration

```bash
cd backend
python migrate_user_roles.py
```

This adds the `role` column to the users table and creates the `admin_logs` table.

### 2. Create Your First Admin

```powershell
# Create superadmin
python create_admin.py admin@yourdomain.com superadmin

# Or promote existing user to admin
python create_admin.py existing@user.com admin
```

### 3. Restart Backend

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

The new admin routes will be available at `/api/v1x/admin/*`

### 4. Login & Access

1. Go to `http://localhost:3000/login`
2. Login with your admin email/password (created above)
3. The app sets an HTTP-only `token` cookie upon login
4. Navigate to `http://localhost:3000/admin`
5. All admin pages require `admin` or `superadmin` role; non-admins see 401/403

Tip: If you change roles, log out and back in to refresh the session.

---

## End-to-End Flows

### Admin Flow (Current)
- Authenticate via `/login` (cookie-based JWT)
- Access `/admin` dashboard: see stats, quick links, recent activity
- Manage:
  - Users: view, search, change roles (superadmin), delete (superadmin)
  - Mentors: approve/reject/suspend applications
  - Sessions: cancel/mark no-show, view details
  - Courses: add course videos (JSON-backed)
  - Logs: audit trail with filters

### User Flow (Current)
- Sign up, log in, browse paths/courses
- Take quizzes, gain progress/credits
- Book mentor sessions (if available), attend via meeting URL

### Mentor Flow (Current)
- Apply with bio/expertise
- Admin reviews application
- If approved: set availability, receive bookings, conduct sessions
- Post-session: add notes; students can leave feedback/ratings

### Jobs & Applications (Planned)
- Employers post jobs (admin-approved)
- Users apply with resume/profile
- Admin dashboard for Jobs:
  - Approve/reject job postings
  - Moderate applications (flag spam, ensure quality)
  - Track pipeline (applied → shortlisted → interviewed → offer)
- Integrations: ATS parsing, LinkedIn import, resume analytics (parts exist under `modelsx` and `api/v1x`)

---

## What Exists vs. What’s Next

### Implemented (Now)
- RBAC with `user|mentor|admin|superadmin`
- Admin API: users, mentors, sessions, logs, dashboard stats, settings (placeholder)
- Frontend admin: dashboard, users, mentors, sessions, logs, courses
- Audit logs for all admin actions
- Migration and admin creation scripts

### Next Up (Roadmap)
- Admin Uniqueness & Branding
  - Dedicated admin theme + domain (e.g., `admin.skillforge.local`)
  - Admin-only sidebar, keyboard shortcuts, command palette
  - Saved views and custom filters per admin
- Security Hardening
  - 2FA for admins; device and IP verification
  - Session management: list/revoke active sessions
  - Rate limiting and anomaly detection on admin actions
- Jobs & Applications Module
  - Backend: `admin/jobs` and `admin/applications` endpoints
  - Frontend: `/admin/jobs`, `/admin/applications` with pipelines and bulk actions
  - Employer accounts + job posting workflow; approval queues
- Analytics & Reporting
  - Charts for cohort growth, mentor utilization, revenue trends
  - Export to CSV/Parquet; scheduled email reports
- Moderation & Quality
  - Dispute workflows for sessions
  - Content moderation (bios, reviews) with AI assist
- Settings
  - Persist platform settings in DB; feature flags; maintenance mode UI

---

## Admin API Quick Map (Unified)

- Dashboard: `GET /api/v1x/admin/dashboard/stats`
- Users:
  - `GET /api/v1x/admin/users`
  - `PATCH /api/v1x/admin/users/{id}/role` (superadmin)
  - `DELETE /api/v1x/admin/users/{id}` (superadmin)
- Mentors:
  - `GET /api/v1x/admin/mentors/applications`
  - `PATCH /api/v1x/admin/mentors/{id}/status`
- Sessions:
  - `GET /api/v1x/admin/sessions`
  - `PATCH /api/v1x/admin/sessions/{id}/status`
- Logs: `GET /api/v1x/admin/logs`
- Settings: `GET/POST /api/v1x/admin/settings`

---

## PowerShell Quick Start

```powershell
# Backend (first time)
cd backend
pip install -r requirements.txt
python migrate_user_roles.py
python create_admin.py admin@yourdomain.com superadmin

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Frontend
cd ..
npm install
$env:NEXT_PUBLIC_API_BASE = "http://localhost:8001"; npm run dev
```

## Audit Logging

All admin actions are automatically logged to the `admin_logs` table:

**Logged Actions:**
- `update_user_role` - Role changes
- `delete_user` - User deletions
- `update_mentor_status` - Mentor approvals/rejections
- `update_session_status` - Session modifications
- `update_platform_settings` - Configuration changes

**Logged Data:**
- Admin user ID and email
- Action type and resource
- Detailed change description
- IP address and user agent
- Timestamp

## Best Practices

### For Superadmins

1. **Create admin users sparingly** - Only trusted personnel
2. **Review audit logs regularly** - Monitor for suspicious activity
3. **Never share credentials** - Each admin should have their own account
4. **Use strong passwords** - 12+ characters recommended
5. **Keep backup superadmin** - Don't lock yourself out

### For Admins

1. **Document major actions** - Use meaningful status change reasons
2. **Check before deleting** - User deletion is permanent
3. **Review pending applications** - Process mentor applications promptly
4. **Monitor sessions** - Address disputes and issues quickly

### Security Considerations

1. **No self-demotion** - Superadmins cannot demote themselves
2. **Role-based guards** - Endpoints check permissions via dependencies
3. **Audit trail** - All actions are logged with attribution
4. **Cookie-based auth** - HTTP-only cookies prevent XSS
5. **CORS protection** - Only trusted origins allowed

## Future Enhancements

Planned features for production deployment:

- [ ] **Two-Factor Authentication (2FA)** for admin accounts
- [ ] **IP Whitelisting** - Restrict admin access by IP range
- [ ] **Session Management** - View and revoke active admin sessions
- [ ] **Email Notifications** - Alert on critical admin actions
- [ ] **Advanced Analytics** - Charts and trends on dashboard
- [ ] **Bulk Operations** - Multi-select for batch actions
- [ ] **Export Functionality** - Download audit logs, user lists
- [ ] **Rate Limiting** - Prevent abuse of admin endpoints
- [ ] **Settings Database** - Store platform config in DB
- [ ] **Webhook Integration** - Trigger external systems on actions
- [ ] **Mobile Admin App** - React Native admin interface

## Troubleshooting

### "Access denied. Admin privileges required"

- Ensure user has `admin` or `superadmin` role
- Check authentication cookie is present
- Verify role was set correctly: `python create_admin.py <email> admin`

### Role column missing error

- Run migration: `python migrate_user_roles.py`
- Restart backend after migration

### Cannot access /admin pages

- Login first at `/login`
- Check browser console for 401/403 errors
- Verify backend is running and accessible

### Audit logs not appearing

- Ensure `admin_logs` table exists (run migration)
- Check that admin actions use the new endpoints
- Verify AdminLog model imported in main.py

## API Response Examples

### Dashboard Stats
```json
{
  "total_users": 1234,
  "total_mentors": 56,
  "pending_mentor_applications": 8,
  "total_sessions": 432,
  "scheduled_sessions": 12,
  "completed_sessions": 389,
  "total_revenue": 15680.0,
  "active_users_30d": 234
}
```

### Audit Log Entry
```json
{
  "id": 1,
  "admin_user_id": 5,
  "admin_email": "admin@skillforge.com",
  "action": "update_mentor_status",
  "resource_type": "mentor",
  "resource_id": 12,
  "details": "Changed status from pending to approved",
  "ip_address": "192.168.1.100",
  "created_at": "2025-12-01T10:30:00Z"
}
```

## Support

For issues or questions about the admin system:
- Check this documentation first
- Review audit logs for action history
- Examine backend logs for errors
- Contact dev team if authentication issues persist

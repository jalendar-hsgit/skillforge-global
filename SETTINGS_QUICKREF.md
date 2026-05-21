# Platform Settings - Quick Reference Card

## Emergency Commands

```bash
# Disable site (maintenance mode)
cd backend && python manage_settings.py set maintenance_mode true

# Enable site
cd backend && python manage_settings.py set maintenance_mode false

# Close registration
cd backend && python manage_settings.py set allow_new_registrations false

# Open registration
cd backend && python manage_settings.py set allow_new_registrations true
```

## View Current Settings

```bash
# List all
cd backend && python manage_settings.py list

# Get specific
cd backend && python manage_settings.py get maintenance_mode
```

## Update Settings (Best Method)

**Use Admin UI**: http://localhost:3000/admin/settings (superadmin only)
- ✅ Clears cache immediately
- ✅ User-friendly interface
- ✅ Audit logging

**Or use CLI**:
```bash
cd backend
python manage_settings.py set <key> <value>
```

## Available Settings

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `platform_name` | string | "SkillForge Global" | Branding |
| `support_email` | string | "support@skillforge.com" | Contact |
| `allow_new_registrations` | boolean | true | Signup toggle |
| `mentor_approval_required` | boolean | true | Mentor workflow |
| `maintenance_mode` | boolean | false | Site lock |
| `featured_courses` | array | [] | Homepage display |

## Code Usage

```python
from app.services.settings_service import (
    is_maintenance_mode,
    allow_new_registrations,
    require_mentor_approval,
    get_platform_name,
    get_support_email,
    get_featured_courses
)

# Check settings
if is_maintenance_mode():
    # Site is in maintenance
    
if allow_new_registrations():
    # Signups are open
    
if require_mentor_approval():
    mentor.status = MentorStatus.PENDING
```

## Common Tasks

### Deploy New Feature
```bash
# Close site
python manage_settings.py set maintenance_mode true

# Deploy code
git pull && ./deploy.sh

# Open site
python manage_settings.py set maintenance_mode false
```

### Feature New Courses
```bash
# Set featured courses
python manage_settings.py set featured_courses '["ai-intro", "python-basics", "web-dev"]'
```

### Troubleshooting

**Settings not taking effect?**
- Wait 60 seconds (cache TTL) OR
- Update via admin UI (clears cache) OR
- Restart backend server

**Can't access site in maintenance mode?**
- Login as admin/superadmin (bypass) OR
- Disable: `python manage_settings.py set maintenance_mode false`

## API Reference

```bash
# Get settings (public)
GET /api/v1x/admin/settings/public

# Update settings (superadmin only)
POST /api/v1x/admin/settings
```

## Testing

```bash
cd backend && python test_settings.py
```

## Full Documentation

See `SETTINGS_GUIDE.md` for complete reference.

---

**Remember**: Always update via API/Admin UI for immediate effect. Direct DB changes require 60s cache expiry.

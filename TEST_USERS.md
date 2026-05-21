# Test Users for SkillForge Global

## Primary Demo User
```
Email: demo@skillforge.com
Password: Demo123!@#
```

## Standard Test Password
All test users created during testing use:
```
Password: Test123!@#
```

## Test User Categories

### 1. Video Progress Test Users
- `video_test_user_*@test.com` - Users created during video progress testing
- `dashboard_test_*@test.com` - Users for dashboard testing

### 2. System Test Users  
- `user@skillforge.com` - Regular user account
- `mentor@skillforge.com` - Mentor account
- Users with progress data (from seeding): Check database for non-admin, non-test emails

## Testing New Features

To test the video progress system:
1. Login with any test user (password: Test123!@#)
2. Visit `/watch/{video_id}` (video IDs 1-94 available)
3. Watch video and verify progress saves
4. Check dashboard at `/dashboard` to see stats

## Current System Stats
- **438 progress records** (includes test + seeded data)
- **47+ users** with video progress
- **93 videos** available for testing
- **6 courses** with multiple learning paths

## Notes
- All passwords are for development/testing only
- Production passwords should be changed
- Test users are clearly marked with 'test' or 'demo' in email

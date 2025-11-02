# Quick Start: Background Scheduler & DnD Enhancements

## Install New Backend Dependency

```powershell
# Navigate to backend directory
cd backend

# Install APScheduler
pip install APScheduler==3.10.4

# Or install all requirements
pip install -r requirements.txt
```

## Configure Email (Optional but Recommended)

Add to your `.env.local` or backend environment:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

**Note:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833).

## Start Backend with Scheduler

```powershell
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Expected console output:**
```
Scheduler lifecycle hooks registered
APScheduler started: follow-ups(30m), interviews(15m)
```

## Start Frontend

```powershell
# From repository root
npm run dev
```

## Test the Enhancements

### 1. Drag & Drop with Visual Feedback
1. Navigate to `http://localhost:3001/job-tracker`
2. Click "Kanban" view
3. Hover over a card's drag handle (⋮⋮ icon)
4. Drag a card to another column
5. Observe:
   - Blue highlight on target column while dragging
   - Success toast notification after drop
   - Smooth animations

### 2. Background Scheduler
The scheduler runs automatically:
- **Follow-up reminders:** Every 30 minutes
- **Interview reminders:** Every 15 minutes

To test manually without waiting:
```powershell
# Trigger follow-up reminders
curl -X POST http://localhost:8001/api/v1x/job-applications-notifications/send-follow-up-reminders `
  -H "Cookie: token=YOUR_AUTH_TOKEN"

# Trigger interview reminders (24h window)
curl -X POST "http://localhost:8001/api/v1x/job-applications-notifications/send-interview-reminders?hours_before=24" `
  -H "Cookie: token=YOUR_AUTH_TOKEN"
```

### 3. Toast Notifications
Toasts appear automatically:
- ✅ Success: Green toast when status update succeeds
- ❌ Error: Red toast when update fails (with auto-revert)
- Auto-dismiss after 3.5 seconds

### 4. E2E Tests
```powershell
# Install Playwright (if not already)
npx playwright install

# Run drag test
npx playwright test e2e/job-tracker-drag.spec.ts

# Run all job tracker tests
npx playwright test e2e/job-tracker*.spec.ts
```

## Troubleshooting

### Scheduler Not Starting
**Error:** `Import "apscheduler.schedulers.asyncio" could not be resolved`

**Solution:**
```powershell
pip install APScheduler==3.10.4
```

### Emails Not Sending
**Check:**
1. SMTP credentials set in environment
2. Console for message: `"Email not configured. Set SMTP_USER and SMTP_PASSWORD in environment."`
3. For Gmail: Use app password, not regular password
4. Check spam/junk folder

### DnD Not Working
**Check:**
1. Kanban view is selected (not List view)
2. At least one card exists in any column
3. Drag by the handle icon (⋮⋮), not the card body
4. Browser console for errors

### Toast Not Appearing
**Check:**
1. ToastProvider is wrapping the app (should be in `_app.tsx`)
2. Browser console for React errors
3. Try triggering manually: Use browser DevTools console:
   ```javascript
   // This won't work in production, just for debugging
   window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Test' }}))
   ```

## Verification Checklist

- [ ] Backend starts with scheduler messages
- [ ] Frontend shows Kanban view with drag handles
- [ ] Dragging card shows blue highlight on target
- [ ] Dropping card shows success toast
- [ ] SMTP credentials configured (if using email)
- [ ] Manual reminder endpoints work
- [ ] E2E tests pass

## Next Steps

1. **Add Test Data:**
   - Create a few job applications
   - Set follow-up dates in the past
   - Schedule interviews for tomorrow
   - Wait for scheduler to send reminders

2. **Monitor Logs:**
   - Check backend console for scheduler activity
   - Verify email delivery
   - Look for any error messages

3. **Production Deploy:**
   - Set SMTP credentials in production environment
   - Ensure APScheduler is in production requirements
   - Consider adding Redis for distributed scheduling

## What Was Added

✅ **Backend:**
- `backend/app/services/scheduler.py` - APScheduler jobs
- `backend/requirements.txt` - APScheduler dependency
- `backend/app/main.py` - Lifecycle hooks

✅ **Frontend:**
- `src/components/Toast.tsx` - Toast system
- `src/pages/_app.tsx` - ToastProvider
- `src/pages/job-tracker/index.tsx` - DnD polish
- `src/pages/job-tracker/add.tsx` - Mobile tweaks

✅ **Testing:**
- `e2e/job-tracker-drag.spec.ts` - Drag test

✅ **Docs:**
- `TRACKER_ENHANCEMENTS.md` - Full documentation
- `QUICKSTART_SCHEDULER.md` - This file

---
**Ready to go!** 🚀

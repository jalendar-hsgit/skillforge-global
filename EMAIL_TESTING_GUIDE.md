# 📧 Email Testing Guide

## Test Users Created

All test users have been created with the following credentials:

| Email | Password | Name | Coins | Purpose |
|-------|----------|------|-------|---------|
| `emailtest@skillforge.test` | Test123! | Email Test User | 100 | General email testing |
| `cointest@example.com` | Test123! | Coin Tester | 100 | Coin system testing |
| `admin@skillforge.test` | Test123! | Admin User | 100 | Admin features |
| `student@skillforge.test` | Test123! | Student User | 100 | Student workflows |
| `mentor@skillforge.test` | Test123! | Mentor User | 100 | Mentor features |

---

## Quick Test Script

### Create New Test User (PowerShell)
```powershell
# Run from project root
.\create_email_test_user.ps1

# Or with custom email
.\create_email_test_user.ps1 -Email "mytest@example.com" -Name "My Test User"
```

---

## Email Configuration Status

### Current Status: ⚠️ NOT CONFIGURED
Emails are **not being sent** because email provider credentials are not configured.

### What Happens Now:
- ✅ Welcome email **code runs** in background
- ✅ Email template **is generated**
- ⚠️ Email **is not sent** (logs: "SMTP credentials not configured, skipping email")
- ✅ User signup **still succeeds**
- ✅ 100 coins **are awarded**

---

## Configure Email Sending

### Option 1: SendGrid (Recommended for Testing)

**Steps:**
1. Sign up at [sendgrid.com](https://sendgrid.com) (free tier: 100 emails/day)
2. Create an API key (Settings → API Keys → Create API Key)
3. Edit `backend/.env`:
   ```env
   EMAIL_PROVIDER=sendgrid
   SENDGRID_API_KEY=SG.your_key_here
   EMAIL_FROM=noreply@skillforge.test
   EMAIL_FROM_NAME=SkillForge Global
   ```
4. Restart backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

**Test it:**
```powershell
# Create a new user (will send welcome email)
.\create_email_test_user.ps1 -Email "real@youremail.com" -Name "Real User"

# Check your email inbox for welcome message
```

---

### Option 2: Gmail SMTP (Easy for Personal Testing)

**Steps:**
1. Enable 2-Factor Authentication on your Gmail account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for "Mail"
4. Edit `backend/.env`:
   ```env
   EMAIL_PROVIDER=smtp
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your@gmail.com
   SMTP_PASSWORD=your_16_char_app_password
   EMAIL_FROM=your@gmail.com
   EMAIL_FROM_NAME=SkillForge Global
   ```
5. Restart backend

**Note:** Gmail has sending limits (500/day for free accounts)

---

### Option 3: Mailtrap (Development Testing)

**Perfect for testing without sending real emails!**

**Steps:**
1. Sign up at [mailtrap.io](https://mailtrap.io) (free account)
2. Create an inbox
3. Get SMTP credentials from dashboard
4. Edit `backend/.env`:
   ```env
   EMAIL_PROVIDER=smtp
   SMTP_HOST=sandbox.smtp.mailtrap.io
   SMTP_PORT=2525
   SMTP_USER=your_mailtrap_username
   SMTP_PASSWORD=your_mailtrap_password
   EMAIL_FROM=test@skillforge.test
   EMAIL_FROM_NAME=SkillForge Global
   ```
5. Restart backend

**Benefits:**
- ✅ No real emails sent
- ✅ View emails in web interface
- ✅ Test all email templates safely
- ✅ No spam concerns

---

## Email Templates Available

The following email templates are ready to use:

### 1. Welcome Email ✅
**Triggered:** On user signup  
**Recipient:** New user  
**Content:**
- Welcome message
- "Get Started in 3 Easy Steps"
- 100 coin bonus announcement
- Links to paths and dashboard

**Test:**
```powershell
.\create_email_test_user.ps1 -Email "test@example.com"
```

---

### 2. Password Reset Email ✅
**Triggered:** User requests password reset  
**Recipient:** User who forgot password  
**Content:**
- Reset link with secure token
- Security notice (expires in 1 hour)
- "Didn't request this?" warning

**API Endpoint:**
```http
POST /api/v1/auth/reset-password
{"email": "user@example.com"}
```

---

### 3. Job Application Reminder ✅
**Triggered:** X days after application  
**Recipient:** User with pending applications  
**Content:**
- Follow-up reminder
- Email template suggestion
- Link to application details

**Usage:**
Will be triggered by job tracker scheduler (see `backend/app/services/scheduler.py`)

---

### 4. Session Confirmation (Mentor) ✅
**Triggered:** Mentor session booked  
**Recipient:** Student and mentor  
**Content:**
- Session details (date, time, duration)
- Meeting link
- Preparation tips

**Existing feature** - already works

---

### 5. Payment Receipt ✅
**Triggered:** Successful payment  
**Recipient:** Student  
**Content:**
- Payment amount
- Session details
- Payment ID for records

**Existing feature** - already works

---

## Testing Checklist

### Without Email Configuration (Current State)
- [x] User signup succeeds
- [x] 100 coins awarded automatically
- [x] Welcome email code runs (background task)
- [x] Backend logs show: "SMTP credentials not configured, skipping email"
- [x] No actual email sent
- [x] No errors or crashes

### With Email Configuration (After Setup)
- [ ] Configure email provider (SendGrid/SMTP/Mailtrap)
- [ ] Restart backend
- [ ] Create new test user: `.\create_email_test_user.ps1`
- [ ] Check backend logs for: "Welcome email sent to [email]"
- [ ] Check email inbox (or Mailtrap) for welcome message
- [ ] Verify email formatting is correct
- [ ] Click links in email (should work)
- [ ] Verify 100 coins mentioned in email

---

## Troubleshooting

### Issue: "SMTP credentials not configured"
**Solution:** Email provider not set up. Follow configuration steps above.

### Issue: "Failed to send email"
**Possible causes:**
1. Wrong SMTP credentials
2. Gmail app password not used (regular password won't work)
3. SendGrid API key invalid
4. Network/firewall blocking SMTP port 587

**Debug:**
```powershell
# Check backend logs
cd backend
# Look for detailed error messages
```

### Issue: Email sent but not received
**Possible causes:**
1. Check spam folder
2. Email provider rate limit exceeded
3. Recipient email address invalid
4. SendGrid account not verified

**Test with Mailtrap:**
Use Mailtrap instead to verify emails are being generated correctly before sending real emails.

---

## Verify Email System Working

### Quick Verification Script
```powershell
# 1. Create test user
$email = "verify@test.com"
$user = @{email=$email; password="Test123!"; full_name="Verify User"} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/v1/auth/signup -ContentType 'application/json' -Body $user

# 2. Check backend terminal for:
# "Welcome email sent to verify@test.com" (success)
# OR
# "SMTP credentials not configured" (needs setup)

# 3. If configured, check email inbox or Mailtrap
```

---

## Backend Logs to Watch

After signup, look for these log messages:

**Success (Email Sent):**
```
INFO: Welcome email sent to test@example.com
INFO: Awarded 100 welcome coins to user 123
```

**Not Configured (Expected in Dev):**
```
WARNING: SMTP credentials not configured, skipping email
INFO: Awarded 100 welcome coins to user 123
```

**Error:**
```
ERROR: Failed to send welcome email to test@example.com: [error details]
INFO: Awarded 100 welcome coins to user 123
```

Note: User signup always succeeds even if email fails (non-blocking background task).

---

## Production Recommendations

### For Production Deployment:

1. **Use SendGrid** (recommended)
   - Reliable delivery
   - Good free tier
   - Easy tracking/analytics
   - Webhook support

2. **Configure SPF/DKIM/DMARC**
   - Prevents emails going to spam
   - Improves deliverability
   - Required for custom domain

3. **Monitor Sending**
   - Track email open rates
   - Monitor bounce rates
   - Set up bounce webhooks

4. **Rate Limiting**
   - Already implemented in code
   - 5 signups per hour per IP
   - Prevents email spam abuse

---

## Email Template Customization

Email templates are in: `backend/app/services/email_service.py`

To customize:
1. Edit HTML in template functions
2. Update branding/colors
3. Change button styles
4. Add/remove sections
5. Restart backend

Example:
```python
# In email_service.py, find:
async def send_welcome_email(...)
    html_content = f"""
    <html>
    <!-- Edit this HTML -->
    </html>
    """
```

---

## Summary

✅ **Test users created and ready**  
✅ **Email code implemented and tested**  
✅ **Multiple templates available**  
✅ **Background task integration working**  
⚠️ **Email provider needs configuration for actual sending**

**Next Step:** Choose an email provider (Mailtrap for dev, SendGrid for production) and configure credentials in `backend/.env`.

---

## Quick Commands Reference

```powershell
# Create test user with email
.\create_email_test_user.ps1 -Email "test@example.com" -Name "Test User"

# List all test users (from database)
cd backend
python -c "from app.core.db import SessionLocal; from app.models.user import User; db = SessionLocal(); users = db.query(User).all(); [print(f'{u.id}: {u.email}') for u in users]"

# Check if email provider is configured
python -c "from app.core.config import settings; print('Provider:', settings.EMAIL_PROVIDER); print('SMTP User:', settings.SMTP_USER or 'Not set'); print('SendGrid:', 'Set' if settings.SENDGRID_API_KEY else 'Not set')"
```

---

**Ready for Testing!** 🚀

Use `.\create_email_test_user.ps1` to create as many test users as needed.

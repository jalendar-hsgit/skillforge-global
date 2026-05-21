# 🔐 .env Configuration Template - Phase 2A

Copy this to `.env.local` and fill in your values.

---

## ✅ REQUIRED: Stripe Configuration

```bash
# Get these from: https://dashboard.stripe.com/apikeys

# Stripe API Keys (Test Mode)
STRIPE_PUBLIC_KEY=pk_test_51Iv6C...  # Starts with pk_test_
STRIPE_SECRET_KEY=sk_test_REPLACE_ME...  # Starts with sk_test_

# Stripe Webhook Secret (From Developers → Webhooks)
STRIPE_WEBHOOK_SECRET=whsec_test_... # Starts with whsec_test_
```

---

## 📧 REQUIRED: Email Configuration

Choose **ONE** of the following options:

### Option A: Gmail (Recommended for Production)

```bash
# Email Provider
EMAIL_PROVIDER=smtp

# Gmail SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password

# Email Sender Details
EMAIL_FROM=noreply@skillforge.com
EMAIL_FROM_NAME=SkillForge Global
```

**How to Get Gmail App Password**:
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Copy the 16-character password
4. Paste into SMTP_PASSWORD above

---

### Option B: SendGrid

```bash
# Email Provider
EMAIL_PROVIDER=sendgrid

# SendGrid API Key
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx...

# Email Sender Details
EMAIL_FROM=noreply@skillforge.com
EMAIL_FROM_NAME=SkillForge Global
```

**How to Get SendGrid API Key**:
1. Go to: https://app.sendgrid.com/settings/api_keys
2. Create new API key (Full Access)
3. Copy key
4. Paste into SENDGRID_API_KEY above

---

### Option C: AWS SES

```bash
# Email Provider
EMAIL_PROVIDER=ses

# AWS Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1

# Email Sender Details
EMAIL_FROM=noreply@skillforge.com
EMAIL_FROM_NAME=SkillForge Global
```

**How to Get AWS SES Credentials**:
1. Go to: https://console.aws.amazon.com/ses/
2. Verify your email address as sender
3. Create IAM user with SES permissions
4. Get access key and secret key
5. Configure region (us-east-1, eu-west-1, etc.)

---

### Option D: Mailhog (Local Development Only)

```bash
# Email Provider
EMAIL_PROVIDER=smtp

# Mailhog Settings (localhost)
SMTP_HOST=localhost
SMTP_PORT=1025

# Email Sender Details
EMAIL_FROM=noreply@skillforge.com
EMAIL_FROM_NAME=SkillForge Global

# Run Mailhog with:
# docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog
# 
# View emails at: http://localhost:8025
```

---

## 🔗 Optional: Frontend Configuration

```bash
# Frontend API Base URL
NEXT_PUBLIC_API_BASE=http://localhost:8001

# Frontend Origin (for email links)
FRONTEND_ORIGIN=http://localhost:3000
```

---

## 🚀 For Production Deployment

### Switch to Stripe Live Keys

```bash
# IMPORTANT: Only after testing!
# Get from: https://dashboard.stripe.com/apikeys (Switch to Live)

STRIPE_PUBLIC_KEY=pk_live_xxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_live_xxxxxxxxxxxxx
```

### Update Email Provider Credentials

```bash
# Use production credentials for your email provider
# Update SMTP_USER, SMTP_PASSWORD, or API keys
```

### Update Frontend Origin

```bash
NEXT_PUBLIC_API_BASE=https://api.skillforge.com
FRONTEND_ORIGIN=https://skillforge.com
```

---

## ✅ Complete Example (.env.local)

```bash
# ============================================
# SKILLFORGE GLOBAL - Environment Variables
# ============================================

# STRIPE CONFIGURATION
# Get from: https://dashboard.stripe.com/apikeys
STRIPE_PUBLIC_KEY=pk_test_51Iv6CAJKL1234567890abcdefghijklmnop
STRIPE_SECRET_KEY=sk_test_REPLACE_ME
STRIPE_WEBHOOK_SECRET=whsec_test_1234567890abcdefghijklmnop

# EMAIL CONFIGURATION - Choose ONE provider below:

# === OPTION A: Gmail (Recommended) ===
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=noreply@skillforge.com
EMAIL_FROM_NAME=SkillForge Global

# === OPTION B: SendGrid ===
# EMAIL_PROVIDER=sendgrid
# SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxx
# EMAIL_FROM=noreply@skillforge.com
# EMAIL_FROM_NAME=SkillForge Global

# === OPTION C: AWS SES ===
# EMAIL_PROVIDER=ses
# AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
# AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# AWS_REGION=us-east-1
# EMAIL_FROM=noreply@skillforge.com
# EMAIL_FROM_NAME=SkillForge Global

# === OPTION D: Mailhog (Local) ===
# EMAIL_PROVIDER=smtp
# SMTP_HOST=localhost
# SMTP_PORT=1025
# EMAIL_FROM=noreply@skillforge.com
# EMAIL_FROM_NAME=SkillForge Global

# FRONTEND CONFIGURATION
NEXT_PUBLIC_API_BASE=http://localhost:8001
FRONTEND_ORIGIN=http://localhost:3000

# JWT SECURITY
JWT_SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# DATABASE
DATABASE_URL=sqlite:///./app/data/skillforge.db

# ADMIN USER
ADMIN_EMAIL=admin@skillforge.com
ADMIN_PASSWORD=Admin@123456

# SERVER
HOST=0.0.0.0
PORT=8001

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8001"]

# DEMO MODE
DEMO_MODE=true
```

---

## 🔍 Verification Checklist

After setting up .env.local:

- [ ] STRIPE_PUBLIC_KEY is set
- [ ] STRIPE_SECRET_KEY is set
- [ ] STRIPE_WEBHOOK_SECRET is set
- [ ] Email provider is selected (one of A/B/C/D)
- [ ] Email credentials are correct
- [ ] EMAIL_FROM is set
- [ ] FRONTEND_ORIGIN is correct
- [ ] DATABASE_URL is correct
- [ ] File is named `.env.local` (not `.env`)
- [ ] File is in repository root directory

---

## 🧪 Test Your Configuration

### Test Stripe Keys

```bash
# In Python shell
import stripe
stripe.api_key = "sk_test_..."
print(stripe.Account.retrieve())  # Should return account info
```

### Test Email Configuration

```bash
# Using Python
from app.services.email_service import email_service
import asyncio

asyncio.run(email_service.send_email(
    to_email="test@example.com",
    subject="Test Email",
    html_content="<p>Test email from SkillForge</p>"
))
```

### Test Webhook Secret

```bash
# Check environment variable
echo $STRIPE_WEBHOOK_SECRET
# Should output: whsec_test_xxxxx
```

---

## ⚠️ Important Notes

### Security
- **NEVER** commit `.env.local` to git
- **NEVER** share STRIPE_SECRET_KEY or email credentials
- Keep SMTP_PASSWORD secret
- Use strong JWT_SECRET_KEY in production
- Rotate webhook secrets periodically

### Stripe Test Cards
For testing in development:

| Card Number | Description |
|-------------|-------------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Decline |
| 5555 5555 5555 4444 | Mastercard |
| 3782 822463 10005 | American Express |

Expiry: Any future date (12/25)
CVC: Any 3 digits (123)

### Email in Development

Use **Mailhog** for local development:

```bash
# Start Mailhog
docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog

# View emails at: http://localhost:8025
# No real emails are sent
# Perfect for testing
```

---

## 🚀 Getting Started

1. **Copy template above to `.env.local`**
2. **Fill in Stripe keys from https://dashboard.stripe.com/apikeys**
3. **Choose email provider and fill credentials**
4. **Test configuration** (see sections above)
5. **Start backend**: `uvicorn app.main:app --reload`
6. **Start webhook listener**: `stripe listen --forward-to http://localhost:8001/webhook/stripe`
7. **Test email sending**: (see test sections)
8. **Ready to go!** 🚀

---

## 📞 Troubleshooting

### Stripe Keys Invalid
- Go to: https://dashboard.stripe.com/apikeys
- Make sure you're in TEST mode (toggle at top)
- Copy keys exactly (including prefix pk_test_ / sk_test_)

### Email Not Sending
- Verify SMTP credentials in .env.local
- For Gmail: Enable "Less secure apps" or use App Password
- For SendGrid: Verify API key format (SG.xxxxx)
- For AWS SES: Verify access key, secret key, and region
- Check backend logs for error messages

### Webhook Secret Invalid
- Go to: https://dashboard.stripe.com/webhooks
- Copy signing secret exactly (include whsec_test_ prefix)
- Make sure backend is running when testing webhook

### Environment Variables Not Loading
- Make sure file is named `.env.local` (not `.env`)
- Make sure file is in repository root
- Backend must be restarted after changing .env.local
- Check for syntax errors (colons, quotes, etc.)

---

## 📚 Related Documentation

- **Configuration Guide**: `STRIPE_CONFIGURATION_GUIDE.md`
- **Quick Start**: `PHASE_2_QUICKSTART.md`
- **Email Setup**: `PHASE_2A_EMAIL_RECEIPTS_COMPLETE.md`
- **Testing**: `PHASE_2_TESTING_GUIDE.md`

---

## ✅ Final Checklist

- [ ] Created `.env.local` file
- [ ] Added Stripe API keys
- [ ] Added email provider credentials
- [ ] Verified all required fields present
- [ ] Backend starts without errors
- [ ] Email test passes
- [ ] Webhook test passes
- [ ] Ready to deploy

---

**Configuration Complete!** 🎉

Proceed to: `PHASE_2_QUICKSTART.md` for next steps.


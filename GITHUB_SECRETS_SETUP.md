# 🔐 GitHub Secrets Setup - Quick Reference

**Time Required**: 10 minutes  
**Required for**: CI/CD automation and deployments

---

## What Are GitHub Secrets?

Encrypted environment variables that are:
- ✅ Not visible in code or logs
- ✅ Accessible only in GitHub Actions
- ✅ Unique per repository
- ✅ Used for API keys, tokens, passwords

---

## Setup Instructions

### Step 1: Go to GitHub Settings

1. Your repo → Settings (top menu)
2. Secrets and Variables → Actions
3. Click "New repository secret"

### Step 2: Add Required Secrets

Copy-paste each pair into GitHub (name in code block, value after =)

#### Vercel Secrets

**Get these from**: https://vercel.com

1. **VERCEL_TOKEN**
   ```
   Value: Your Vercel API token
   Get from: Vercel → Settings → Tokens → Create token
   ```

2. **VERCEL_ORG_ID**
   ```
   Value: Your organization ID
   Get from: Vercel → Settings → Account → Team ID
   ```

3. **VERCEL_PROJECT_ID**
   ```
   Value: Your project ID
   Get from: Vercel → Project → Settings → Project ID
   ```

#### Railway Secrets

**Get these from**: https://railway.app

1. **RAILWAY_TOKEN**
   ```
   Value: Your Railway API token
   Get from: Railway → Settings → Tokens → Create
   ```

2. **RAILWAY_PROJECT_ID**
   ```
   Value: Your project ID
   Get from: Railway → Project → Settings → Project ID
   ```

3. **RAILWAY_DATABASE_URL**
   ```
   Value: PostgreSQL connection string
   Get from: Railway → PostgreSQL → Variables → DATABASE_URL
   ```

#### Security Secrets

**Generate these**:

1. **JWT_SECRET**
   ```bash
   # Generate random 32+ character string
   openssl rand -hex 32
   
   # Or use:
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **STRIPE_SECRET_KEY**
   ```
   Value: Your Stripe secret key
   Get from: Stripe Dashboard → Developers → API Keys → Secret Key
   ```

#### Optional Slack Notification

1. **SLACK_WEBHOOK**
   ```
   Value: Your Slack webhook URL
   Get from: https://api.slack.com/apps → Create app → Incoming Webhooks
   ```

---

## Complete Checklist

Create these secrets in GitHub (in this order):

```
GitHub → Settings → Secrets → Actions → New Repository Secret
```

**Required** (9 secrets):
- [ ] VERCEL_TOKEN
- [ ] VERCEL_ORG_ID
- [ ] VERCEL_PROJECT_ID
- [ ] RAILWAY_TOKEN
- [ ] RAILWAY_PROJECT_ID
- [ ] RAILWAY_DATABASE_URL
- [ ] JWT_SECRET
- [ ] STRIPE_SECRET_KEY
- [ ] SLACK_WEBHOOK (optional)

---

## How to Get Each Value

### Vercel Setup

```bash
# 1. Go to https://vercel.com/account/tokens
# 2. Click "Create token"
# 3. Name: "GitHub Actions"
# 4. Paste token as VERCEL_TOKEN

# 5. Go to https://vercel.com/settings
# 6. Find "Team ID" → Copy as VERCEL_ORG_ID

# 7. Go to your project
# 8. Settings → Copy "Project ID" as VERCEL_PROJECT_ID
```

### Railway Setup

```bash
# 1. Go to https://railway.app/settings
# 2. Find "API Token" section
# 3. Create new token → Copy as RAILWAY_TOKEN

# 4. Go to your project
# 5. Settings → Copy "Project ID" as RAILWAY_PROJECT_ID

# 6. Click "PostgreSQL" service
# 7. Variables tab → Copy DATABASE_URL
```

### Generate JWT_SECRET

```bash
# Linux/Mac:
openssl rand -hex 32

# Windows PowerShell:
[Convert]::ToHexString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))

# Or use Python:
python -c "import secrets; print(secrets.token_hex(32))"

# Result looks like:
# a1b2c3d4e5f6... (64 characters)
```

### Stripe Setup

```bash
# 1. Go to https://dashboard.stripe.com
# 2. Developers → API Keys
# 3. Copy "Secret key" (starts with sk_test_)
# 4. Paste as STRIPE_SECRET_KEY
```

### Slack Webhook (Optional)

```bash
# 1. Go to https://api.slack.com/apps
# 2. Click "Create New App"
# 3. From scratch → Name: "GitHub Alerts"
# 4. Features → Incoming Webhooks → Toggle ON
# 5. Click "Add New Webhook to Workspace"
# 6. Select channel #deployments
# 7. Copy webhook URL
# 8. Paste as SLACK_WEBHOOK
```

---

## Verify Secrets Are Set

### Via GitHub CLI

```bash
gh secret list
```

Should show:
```
VERCEL_TOKEN                 Configured
VERCEL_ORG_ID                Configured
VERCEL_PROJECT_ID            Configured
RAILWAY_TOKEN                Configured
RAILWAY_PROJECT_ID           Configured
RAILWAY_DATABASE_URL         Configured
JWT_SECRET                   Configured
STRIPE_SECRET_KEY            Configured
SLACK_WEBHOOK                Configured
```

### Via GitHub UI

Settings → Secrets → Actions → All 9 should be listed

---

## Troubleshooting

### Secret Not Working in Actions?

**Check**:
1. Spelling is EXACT (case-sensitive)
2. Secret is in correct repository (not organization)
3. Workflow file uses correct syntax: `${{ secrets.SECRET_NAME }}`
4. No extra spaces in value

**Debug**:
```yaml
# In workflow, check if secret exists:
- run: echo "Token length: ${#SECRET_VALUE}"
  env:
    SECRET_VALUE: ${{ secrets.VERCEL_TOKEN }}
```

### Secret Exposed in Logs?

**Prevent**:
- GitHub Actions automatically masks secrets in logs
- Don't print secrets: `echo ${{ secrets.TOKEN }}`
- Never commit secrets to code

**If Exposed**:
1. Rotate the token immediately
2. Create new token
3. Update GitHub secret
4. Delete old token

---

## Security Best Practices

✅ **Do**:
- Rotate tokens periodically (every 3-6 months)
- Use specific API keys (read-only when possible)
- Limit token scope to minimum needed
- Store original tokens safely (password manager)
- Use different tokens for different environments

❌ **Don't**:
- Share secret values
- Commit secrets to git
- Use same token everywhere
- Keep old unused tokens
- Log secret values

---

## Environment by Branch

**Option**: Different secrets per branch

```yaml
# .github/workflows/deploy.yml
env:
  DATABASE_URL: ${{ 
    github.ref == 'refs/heads/main' 
      ? secrets.PROD_DATABASE_URL 
      : secrets.DEV_DATABASE_URL 
  }}
```

**Add secrets**:
- PROD_DATABASE_URL (for main)
- DEV_DATABASE_URL (for develop)

---

## Next Steps

1. ✅ Generate JWT_SECRET (copy/paste above)
2. ✅ Get Vercel tokens (5 min)
3. ✅ Get Railway tokens (5 min)
4. ✅ Get Stripe key (2 min)
5. ✅ Create GitHub secrets (3 min)
6. ✅ Verify all 9 secrets set
7. ✅ Run first deployment!

**Total time**: ~15 minutes

---

## Testing Deployment

After secrets are set:

```bash
# Push to main branch
git push origin main

# Watch deployment:
# GitHub → Actions tab → Latest workflow

# Should see:
# ✅ Tests pass
# ✅ Frontend deployed
# ✅ Backend deployed
# ✅ Health checks pass
# ✅ Slack notification sent
```

---

## Quick Reference Table

| Secret | Length | Format | Source |
|--------|--------|--------|--------|
| VERCEL_TOKEN | 20-30 | Random string | Vercel |
| VERCEL_ORG_ID | 20-30 | Alphanumeric | Vercel |
| VERCEL_PROJECT_ID | 20-30 | Alphanumeric | Vercel |
| RAILWAY_TOKEN | 50+ | Long token | Railway |
| RAILWAY_PROJECT_ID | 20-30 | Alphanumeric | Railway |
| RAILWAY_DATABASE_URL | 100+ | PostgreSQL URL | Railway |
| JWT_SECRET | 64 | Hex string | Generate |
| STRIPE_SECRET_KEY | 50+ | sk_test_... | Stripe |
| SLACK_WEBHOOK | 100+ | https://... | Slack |

---

**Status**: ✅ Ready to deploy!

Need help? See DEPLOYMENT_GUIDE_COMPLETE.md for full instructions.

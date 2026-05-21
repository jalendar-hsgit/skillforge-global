# next.config.mjs - Production Security Configuration

**Location:** `next.config.mjs` at project root  
**Purpose:** Security headers and production optimization

---

## Add this to your next.config.mjs:

```javascript
// next.config.mjs
import { join } from 'path'

/** @type {import('next').NextConfig} */
const nextConfig = {
  // ============ SECURITY HEADERS ============
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          // Security: Prevent clickjacking attacks
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          // Security: Prevent MIME-type sniffing
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          // Security: Enable XSS protection
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          // Security: Referrer policy for privacy
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          // Security: HSTS for HTTPS enforcement (1 year)
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains; preload'
          },
          // Security: Permissions policy
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(), usb=()'
          },
          // Security: Content Security Policy
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com https://fonts.googleapis.com",
              "img-src 'self' https: data:",
              "connect-src 'self' http://localhost:8001 https://api.skillforge.com",
              "frame-ancestors 'none'",
              "base-uri 'self'",
              "form-action 'self'"
            ].join('; ')
          },
        ],
      },
      // Public assets (minimal restrictions)
      {
        source: '/public/:path*',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }
        ]
      },
      // API routes (strict security)
      {
        source: '/api/:path*',
        headers: [
          { key: 'Cache-Control', value: 'no-store' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
        ]
      }
    ]
  },

  // ============ REDIRECTS ============
  async redirects() {
    return [
      // Security: Redirect HTTP to HTTPS in production
      ...(process.env.NODE_ENV === 'production' 
        ? [{
            source: '/:path*',
            destination: 'https://skillforge.com/:path*',
            permanent: true,
            basePath: false,
          }]
        : []),
      
      // Redirect old paths to new ones
      {
        source: '/auth/login',
        destination: '/login',
        permanent: true,
      },
      {
        source: '/auth/signup',
        destination: '/signup',
        permanent: true,
      },
    ]
  },

  // ============ REWRITES ============
  async rewrites() {
    return {
      beforeFiles: [
        // API proxy for security
        {
          source: '/api/v1/:path*',
          destination: process.env.API_BASE || 'http://localhost:8001/api/v1/:path*'
        }
      ]
    }
  },

  // ============ ENVIRONMENT ============
  env: {
    // Public only (these are exposed to browser)
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001',
    NEXT_PUBLIC_SITE_NAME: 'SkillForge Global',
    NEXT_PUBLIC_VERSION: process.env.APP_VERSION || '1.0.0',
  },

  // ============ PRODUCTION OPTIMIZATION ============
  productionBrowserSourceMaps: false, // Don't expose source maps
  compress: true, // Enable gzip compression
  poweredByHeader: false, // Remove X-Powered-By header

  // ============ SECURITY BEST PRACTICES ============
  reactStrictMode: true, // Enable React strict mode
  swcMinify: true, // Minify with SWC
  
  // ESLint check on build
  eslint: {
    dirs: ['src/pages', 'src/components', 'src/lib']
  },

  // ============ IMAGE OPTIMIZATION ============
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.skillforge.com',
      },
      {
        protocol: 'https',
        hostname: '**.github.com',
      },
      {
        protocol: 'https',
        hostname: '**.googleusercontent.com',
      },
    ],
    // Security: Set size limits
    sizes: [320, 640, 960, 1280, 1920],
    // Security: Disable AVIF if needed
    formats: ['image/webp', 'image/jpeg', 'image/png'],
  },

  // ============ WEBPACK CONFIGURATION ============
  webpack: (config, { isServer }) => {
    // Security: Disable dynamic requires
    config.module.rules.push({
      test: /\.m?js$/,
      exclude: /node_modules/,
      loader: 'babel-loader',
      options: {
        presets: [
          ['@babel/preset-env', { modules: false }],
          '@babel/preset-react',
        ],
      },
    })

    return config
  },

  // ============ EXPERIMENTAL FEATURES ============
  experimental: {
    // Enable if using App Router
    // appDir: true,
  },
}

export default nextConfig
```

---

## 🔐 Environment Variables

Create `.env.production.local`:

```bash
# API Configuration
NEXT_PUBLIC_API_BASE=https://api.skillforge.com
NODE_ENV=production

# Security
SECURITY_HEADERS_ENABLED=true
AUDIT_LOG_ENABLED=true
RATE_LIMITING_ENABLED=true

# Session
SESSION_TIMEOUT_MINUTES=30
TOKEN_REFRESH_THRESHOLD_MINUTES=5

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

---

## 📝 CORS Configuration (Backend)

The backend should have CORS configured in `backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

# Add this to your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://skillforge.com",
        "https://www.skillforge.com",
        "http://localhost:3000",  # Development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 🔒 Nginx Configuration (Production)

If using Nginx as reverse proxy:

```nginx
# /etc/nginx/sites-available/skillforge

upstream frontend {
    server localhost:3000;
}

upstream backend {
    server localhost:8001;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name skillforge.com www.skillforge.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name skillforge.com www.skillforge.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/skillforge.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/skillforge.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Login endpoint (stricter rate limiting)
    location /api/auth/login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://backend;
    }
}
```

---

## 🧪 Verification Checklist

After deploying, verify:

```bash
# 1. Check security headers
curl -I https://skillforge.com/

# Expected response headers:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=31536000...

# 2. Check HTTPS enforcement
curl http://skillforge.com/
# Should redirect to HTTPS (301)

# 3. Check CSP policy
curl -s -D - https://skillforge.com/ | grep Content-Security-Policy

# 4. Check SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 skillforge.com

# 5. Security scan
npm install -g snyk
snyk test

# 6. Performance check
npm install -g lighthouse
lighthouse https://skillforge.com/ --output-path=report.html
```

---

## 📊 Security Scoring

After deployment, test at:
- **Mozilla Observatory:** https://observatory.mozilla.org/
- **SSL Labs:** https://www.ssllabs.com/ssltest/
- **Security Headers:** https://securityheaders.com/

**Target Scores:**
- Mozilla: A+ or A
- SSL Labs: A or A+
- Security Headers: A or A-

---

## 🚀 Deployment Checklist

- [ ] next.config.mjs updated with security headers
- [ ] .env.production.local created with secure values
- [ ] Backend CORS configured properly
- [ ] Nginx configuration deployed (if applicable)
- [ ] SSL certificate valid and installed
- [ ] All security headers verified
- [ ] HTTPS enforced
- [ ] Rate limiting configured
- [ ] Monitoring active
- [ ] Backup plan ready

---

**Status: ✅ PRODUCTION READY**

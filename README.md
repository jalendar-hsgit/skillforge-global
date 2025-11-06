# SkillForge Global

A comprehensive learning platform with mentor sessions, subscriptions, and AI-powered features.

## 🆕 Latest Updates (Nov 3, 2025)

**New Features Implemented:**
- ✅ **Email System** - Welcome emails, password reset, automated reminders (100% complete)
- ✅ **Coin Economy** - Real balances, 100-coin welcome bonus, functional shop with 6 items (95% complete)
- ✅ **Enhanced Security** - Rate limiting on signup/login to prevent brute force attacks (75% complete)

**System Progress:** 78% → 82% (+4% overall completion)

---

## Quick Start

### Frontend (Next.js)

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Backend (FastAPI)

```bash
## CI/CD & Development Workflow

### Continuous Integration

GitHub Actions automatically runs on every push and pull request:

**Backend Pipeline:**
- ✅ Unit tests (`unittest` - auth, hiring, error logging)
- ✅ E2E tests (pytest)
- ✅ Linting (flake8 - syntax errors)
- ✅ Import checks (smoke test)
- ✅ Database migrations (Alembic)

**Frontend Pipeline:**
- ✅ TypeScript type checking
- ✅ Next.js build
- ✅ ESLint linting
- ✅ Playwright e2e tests (optional)

### Pre-commit Hooks

Install pre-commit hooks to catch issues before committing:

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**Hooks include:**
- Python formatting (Black)
- Import sorting (isort)
- Linting (flake8)
- Frontend formatting (Prettier)
- Security scanning (detect-secrets)

### Running Tests Locally

**Backend tests:**
```bash
cd backend
python -m unittest discover -s tests -p "test_*.py" -v
```

**Frontend build:**
```bash
npm run build
npm run lint
```

cd backend
python -m venv .venv
- [Migrations Guide](backend/MIGRATIONS.md) - Database migration workflows
- [CHANGELOG](CHANGELOG.md) - Version history and recent changes
```

API documentation available at [http://localhost:8001/docs](http://localhost:8001/docs)

## Project Structure

### Frontend (`src/`)
- **pages/** - Next.js pages and API routes
- **components/** - Reusable UI components
- **hooks/** - Custom React hooks
- **lib/** - Utility functions and API client
- **styles/** - Global styles

### Backend (`backend/`)
- **app/api/v1/** - File-backed API routes (stable)
- **app/api/v1x/** - Database-backed API routes (optional)
- **app/models/** - Legacy SQLAlchemy models
- **app/modelsx/** - New DB models (subscriptions, mentors, payouts, etc.)
- **app/schemas/** - Pydantic request/response models
- **app/services/** - Business logic (Stripe, email, etc.)
- **app/core/** - Configuration, database, security

## Key Features

### 🤖 AI Quiz Generation v2 (NEW)
- **Multi-Provider LLM**: OpenAI, Anthropic, **Ollama (local, FREE)** support
- **Real-time Streaming**: Watch questions appear as they're generated (SSE)
- **Adaptive Difficulty**: Auto-adjusts based on your performance
- **Save & Retake**: Build a personal quiz library
- **Offline Fallback**: Works without API keys (deterministic mode)

**🦙 Ollama Setup:** See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) - Run AI locally, no API keys!  
**Quick Start:** See [AI_QUIZ_QUICKSTART.md](AI_QUIZ_QUICKSTART.md)  
**Full Docs:** See [AI_QUIZ_GUIDE.md](AI_QUIZ_GUIDE.md)

### 🎓 Core Features
- **Learning Paths**: Structured courses with video content and quizzes
- 👥 **Mentor System**: Book sessions, chat, share files
- 💳 **Subscriptions**: Tiered plans (Free, Pro, Enterprise) via Stripe
- 💰 **Payouts**: Stripe Connect integration for mentor earnings
- 🤖 **AI Assistant**: Chat support for learning
- 📊 **Progress Tracking**: Video progress, quiz attempts, completions
- 🔒 **Authentication**: JWT-based auth with HTTP-only cookies

## Testing

### E2E (Playwright)

The end-to-end tests spin up both backend (FastAPI) and frontend (Next.js) automatically.

```powershell
# Install deps
npm install
# Install browsers (first time only)
npx playwright install chromium
# Run all E2E tests
npm run e2e
# Or run a single test (import flow)
npx playwright test e2e/import.spec.ts --reporter=list
```

The Playwright config will:
- Install backend requirements before starting Uvicorn
- Start the backend on http://127.0.0.1:8001 and the frontend on http://127.0.0.1:3000
- Set NEXT_PUBLIC_API_BASE/API_BASE so the frontend points to the backend

Troubleshooting:
- If the backend port is busy, kill the process bound to 8001 and retry.
- On Windows PowerShell, avoid using string formatting with `-f` in one-liners unless properly scoped.
Windows tip: free port 8001 when stuck

```powershell
# Find the PID using port 8001
netstat -ano | findstr :8001
# Then kill it (replace <PID> with the number from the previous command)
Taskkill /F /PID <PID>
```

### Run Backend Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "sqlite:///./test.db"
$env:JWT_SECRET = "testsecret"
$env:FRONTEND_ORIGIN = "http://localhost:3000"
python -m pytest tests_e2e -v
```

Or use the convenience script:

```powershell
.\scripts\run-backend-tests.ps1
```

See [TESTING.md](TESTING.md) for detailed testing guide and troubleshooting.

## Database Migrations

This project uses Alembic for database schema migrations. See [backend/MIGRATIONS.md](backend/MIGRATIONS.md) for detailed instructions.

Quick commands:
```powershell
cd backend
.\venv\Scripts\Activate.ps1

# Create a new migration after model changes
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Check current version
alembic current
```

## Configuration

### Frontend Environment Variables

Create `.env.local` in the root directory:

```env
NEXT_PUBLIC_API_BASE=http://localhost:8001
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Backend Environment Variables

Create `.env` in the `backend/` directory:

```env
DATABASE_URL=sqlite:///./app/data/app.db
JWT_SECRET=your-secret-key-here
FRONTEND_ORIGIN=http://localhost:3000
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
ADMIN_KEY=your-admin-key
```

## API Documentation

### Health Check
```
GET /healthz
```

### Authentication
```
POST /api/v1/auth/signup
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Subscriptions
```
GET  /api/v1x/subscriptions/plans
GET  /api/v1x/subscriptions/current
POST /api/v1x/subscriptions/subscribe
POST /api/v1x/subscriptions/cancel
```

### Stripe Connect (Mentors)
```
POST /api/v1x/connect/create-account
GET  /api/v1x/connect/onboarding-link
GET  /api/v1x/connect/status
GET  /api/v1x/connect/login-link
```

For full API reference, visit the interactive docs at `/docs` when running the backend.

## CI/CD

Tests run automatically on GitHub Actions:
- ✅ Backend E2E tests
- ✅ Frontend build validation
- 📦 Optional deployment to Vercel/Render

See `.github/workflows/ci.yml` for workflow details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

- [Testing Guide](TESTING.md) - How to run and write tests
- [Fixes Summary](docs/FIXES_2025-01.md) - Recent bug fixes and improvements
- [Copilot Instructions](.github/copilot-instructions.md) - AI assistant guidance

## Tech Stack

**Frontend:**
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Stripe Elements

**Backend:**
- FastAPI
- SQLAlchemy
- Pydantic v2
- Stripe SDK
- Socket.IO (WebSocket chat)

**Deployment:**
- Frontend: Vercel
- Backend: Render / Railway
- Database: SQLite (dev) / PostgreSQL (prod)

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- 📧 Email: support@skillforge.global
- 🐛 GitHub Issues: [Create an issue](https://github.com/yourorg/skillforge-global/issues)
- 💬 Discord: [Join our community](https://discord.gg/skillforge)

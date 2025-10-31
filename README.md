# SkillForge Global

A comprehensive learning platform with mentor sessions, subscriptions, and AI-powered features.

## Quick Start

### Frontend (Next.js)

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
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

- 🎓 **Learning Paths**: Structured courses with video content and quizzes
- 👥 **Mentor System**: Book sessions, chat, share files
- 💳 **Subscriptions**: Tiered plans (Free, Pro, Enterprise) via Stripe
- 💰 **Payouts**: Stripe Connect integration for mentor earnings
- 🤖 **AI Assistant**: Chat support for learning
- 📊 **Progress Tracking**: Video progress, quiz attempts, completions
- 🔒 **Authentication**: JWT-based auth with HTTP-only cookies

## Testing

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

**Current Test Status**: ✅ All 6 E2E tests passing

See [TESTING.md](TESTING.md) for detailed testing guide and troubleshooting.

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

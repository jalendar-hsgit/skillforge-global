## Goal

Help AI contributors get productive quickly in this repository by summarizing the architecture, dev/run commands, project-specific patterns, and concrete file examples to inspect and modify.

## Quick start (what to run locally)

- **Backend (FastAPI)**:
  - Install: `pip install -r backend/requirements.txt`
  - Create tables: `python backend/init_db.py` or tables auto-create on startup via `Base.metadata.create_all(...)`
  - Seed demo data: `python backend/seed_all_demo_data.py` (creates 7 users, 4 mentors, 5 courses, 5 jobs, 3 marketplace products, 8 mentor sessions)
  - Run dev: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001` (from `backend/` dir)

- **Frontend (Next.js)**:
  - Run: `npm run dev` (from repo root) — uses `package.json` scripts
  - API base: reads `NEXT_PUBLIC_API_BASE` env var; defaults to `http://localhost:8001` in code (`src/lib/api.ts`)

## High-level architecture

- **Monorepo structure**:
  - Frontend: Next.js app under `src/` with pages, components, hooks, lib
  - Backend: FastAPI under `backend/app/` with routers, models, schemas
  - Database: SQLite at `backend/app/data/skillforge.db` (auto-created on startup)

- **Data models layer** (three-tier):
  1. **Base Users** (`backend/app/models/user.py`): Core User model with roles (USER, MENTOR, ADMIN, SUPERADMIN)
  2. **DB Models** (`backend/app/modelsx/*.py`): 40+ domain models including Mentor, Course, JobApplication, DigitalProduct, Order, etc.
  3. **SQLAlchemy ORM**: Uses declarative style with relationships; auto-creates tables on startup (no migrations)

- **Data flow**:
  - Frontend → HTTP calls → Backend REST endpoints
  - Backend queries SQLite via SQLAlchemy ORM
  - No file-based routing; all data is relational DB

## Key models (what to know immediately)

| Module | Purpose | Key Fields | Key Files |
|--------|---------|-----------|-----------|
| **User** | Platform accounts | email, role (enum: USER/MENTOR/ADMIN/SUPERADMIN), name, bio, skills | `models/user.py` |
| **Mentor** | Mentor profiles (1:1 with User) | user_id, bio, expertise (CSV), hourly_rate, status (PENDING/APPROVED/REJECTED/SUSPENDED), average_rating | `modelsx/mentor.py` |
| **MentorSession** | 1-on-1 sessions | mentor_id, student_id, topic, scheduled_at (DateTime), status (PENDING/CONFIRMED/COMPLETED/CANCELLED), price, duration_minutes | `modelsx/mentor.py` |
| **MentorAvailability** | Mentor hours | mentor_id, day_of_week, start_time, end_time | `modelsx/mentor.py` |
| **Course** | Courses/programs | path (slug, unique), title, description, difficulty, price, is_paid, is_premium | `modelsx/course.py` |
| **JobApplication** | Job tracking | user_id, company_name, position_title, status (APPLIED/SCREENING/INTERVIEW/OFFER/ACCEPTED/REJECTED), application_date, interviews (JSON), contacts (JSON) | `modelsx/job_application.py` |
| **DigitalProduct** | Marketplace items | seller_id, name, slug, product_type (enum), price, status (DRAFT/PUBLISHED/ARCHIVED), sales_count, average_rating | `modelsx/marketplace.py` |
| **Order** | Purchases | user_id, course_id, order_number, amount, status (pending/completed/failed/refunded), payment_method | `modelsx/order.py` |

## Demo data (what's in the DB by default)

Run `python backend/seed_all_demo_data.py` to populate:
- **2 Admin Users**: superadmin@skillforge.com (SUPERADMIN), admin@skillforge.com (ADMIN)
- **5 Regular Users**: john.doe@example.com, jane.smith@example.com, bob.wilson@example.com, alice.johnson@example.com, charlie.brown@example.com
- **4 Mentors**: Sarah Chen ($75/hr, python-ai), David Kumar ($65/hr, web-dev), Emily Rodriguez ($85/hr, ml), James Patterson ($70/hr, devops)
- **5 Courses**: Python Fundamentals ($49.99), Web Dev ($99.99), React ($149.99), ML ($199.99), DevOps ($129.99)
- **5 Job Applications**: Google, Microsoft, Amazon, Meta, Apple (users tracking applications with APPLIED status)
- **3 Marketplace Products**: Cheat sheets, templates, guides (sellers are mentors)
- **8 Mentor Sessions**: Scheduled for 7 days from now, PENDING confirmation
- **20 Availability Slots**: Each mentor available Mon-Fri 9am-5pm

## Important files & patterns

- **Backend entry**: `backend/app/main.py` — imports all models, creates DB tables, mounts routers
- **User roles**: `backend/app/models/user.py` defines `UserRole` enum (USER, MENTOR, ADMIN, SUPERADMIN)
- **Mentor workflows**: Check `backend/app/modelsx/mentor.py` for status flow: PENDING → APPROVED or REJECTED
- **Job application flow**: `backend/app/modelsx/job_application.py` tracks application_date, interviews (JSON array), and status transitions
- **Marketplace**: `backend/app/modelsx/marketplace.py` for DigitalProduct, `order.py` for Order model; seller_id links to User
- **Seeding**: `backend/seed_all_demo_data.py` is main seed script; individual scripts exist for specific domains

## Project-specific conventions / gotchas

1. **User Roles** are enum-based (USER, MENTOR, ADMIN, SUPERADMIN) — check role in endpoint guards
2. **Mentor creation requires two steps**: (1) Create User with role=MENTOR, (2) Create Mentor profile with status
3. **Mentor expertise field**: Stores comma-separated path slugs (e.g., "python-ai,web-dev"), not a list
4. **MentorSession.scheduled_at** is DateTime in UTC; use timezone-aware datetimes (not datetime.utcnow(), which is deprecated)
5. **JobApplication.interviews & .contacts**: Stored as JSON arrays; deserialize to dicts when reading
6. **DigitalProduct.slug** must be unique; generate from name by lowercasing and replacing spaces with hyphens
7. **Order.order_number**: Must be unique; pattern is "ORD-{user_id}-{course_id}" or similar
8. **No migrations**: Tables created on startup via `Base.metadata.create_all(engine)`; schema changes require code updates + DB reset
9. **SQLAlchemy relationships**: Watch for circular imports; many models use foreign_keys with viewonly=True to avoid circular references
10. **Seeding is idempotent**: Scripts check `.filter(...).first()` before creating; safe to run multiple times

## How to extend the backend safely

**Adding a new model**:
1. Create `backend/app/modelsx/feature_name.py` with SQLAlchemy Base class
2. Import in `backend/app/main.py` at top (before `create_all()`)
3. Add relationships to existing models (e.g., user_id FK, cascade rules)
4. Create corresponding Pydantic schemas in `backend/app/schemas/` if needed for APIs

**Adding a new endpoint**:
1. Create router in `backend/app/api/v1/feature_name.py` with `APIRouter(prefix="/feature")`
2. Include in `backend/app/main.py`: `app.include_router(feature_router.router)`
3. Use dependency injection for DB session: `def my_endpoint(db: Session = Depends(get_db))`
4. Test with: `pytest backend/tests/` or manual API calls

**Demo data for new features**:
1. Add seed function to `backend/seed_all_demo_data.py` following existing patterns
2. Call from main `DemoDataSeeder.run()` method
3. Test idempotency (run twice, ensure no errors)

## Example quick references

- **Seed demo data**: `python backend/seed_all_demo_data.py` (shows pending items report at end)
- **Check DB tables**: `sqlite3 backend/app/data/skillforge.db ".tables"`
- **User login**: POST `/api/v1/auth/login` with email/password
- **Create mentor**: POST `/api/v1/mentors` (requires User with role=MENTOR first)
- **List courses**: GET `/api/v1/courses` (all public courses)
- **Track job**: POST `/api/v1/job-applications` (user tracking their job search)
- **View pending mentor sessions**: Query DB: `SELECT * FROM mentor_sessions WHERE status='pending' ORDER BY scheduled_at`

## Testing & verification

- **Run backend tests**: `pytest backend/tests/` (if test suite exists)
- **Manual API testing**: Use Postman or `curl` against `http://localhost:8001/api/v1/*`
- **DB inspection**: `sqlite3 backend/app/data/skillforge.db` then `.schema` or `.tables`
- **Check model schema**: `python -c "from app.modelsx.mentor import Mentor; print(Mentor.__table__.columns.keys())"`

## What an AI should do first when changing code

1. Run the frontend dev server and the backend dev server locally to exercise the code paths you plan to change.
2. Inspect the corresponding router in `backend/app/api/v1/` and the matching schema in `backend/app/schemas/` before edits.
3. If you touch data files (e.g., `courses.json`), note concurrency caveats — v1 edits are file writes.
4. If adding persistent models, prefer `modelsx` + `api/v1x` pattern so the app can optionally enable DB-backed routes.

## Where to look for more context

- `backend/requirements.txt` — runtime deps for backend.
- `package.json` — frontend scripts (`dev`, `build`, `start`, `lint`).
- `backend/app/data/` — CSV/JSON fixtures used by v1 routers.

If any section above is unclear or you'd like the doc to include command snippets for Windows PowerShell, CI notes, or example PR message templates, tell me which part to expand and I'll update the file.
